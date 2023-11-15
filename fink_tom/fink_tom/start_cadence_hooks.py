import logging
import datetime
import numpy as np
import pandas as pd
from tom_observations.cadence import get_cadence_strategy
from tom_observations.models import DynamicCadence, ObservationGroup
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Group

import astropy.units as u
from astroplan import Observer, FixedTarget, is_observable, observability_table
from astroplan.utils import time_grid_from_range
from tom_targets.models import Target
from astropy.coordinates import SkyCoord
from astropy.time import Time

# import facilities
from fink_tom.colibri import ColibriFacility
from fink_tom.jilin import JilinFacility
from fink_tom.maidanak import MaidanakFacility
from fink_tom.ohp import OHPFacility
from fink_tom.orm import ORMFacility
from fink_tom.xinglong import XinglongFacility

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def simu_night_time_interval(ref_obs, ref_date: str):
    """
    Compute the list of the date interval during which the observable skies
    will be crossmatched (TB updated)

    Parameters
    ----------
    ref_obs : astroplan.observer.Observer
        astroplan.observer.Observer object for the Observatory chosen as the
        reference observatory.
    ref_date : str
        Date of reference to start the simulation.
    n_days : int
        Number of simulated days.
    day_bin : int
        Day interval between two simulated nights.

    Returns
    -------
    None.

    """
    # compute the start time of the nearest (compared to the detection time)
    # night
    date_start_night = ref_obs.twilight_evening_astronomical(ref_date, which="nearest")

    # compute the morning time of the nearest (compared to the detection time)
    # day
    date_end_night = ref_obs.twilight_morning_astronomical(ref_date, which="nearest")

    # If the detection time is within the current night, use the detection
    # time as a starting date and the end of the night as an ending date
    if date_start_night < ref_date and date_end_night > ref_date:
        if date_end_night.jd - date_start_night.jd > 0.5:
            time_ranges = Time([date_start_night, date_end_night])
        else:
            time_ranges = Time([ref_date, date_end_night])
    elif date_start_night < ref_date and date_end_night < ref_date:
        # If the detection time is after the nearest night, use the next
        # night  starting date as a starting date and the end of the night
        # as an ending date
        date_start_night = ref_obs.twilight_evening_astronomical(ref_date, which="next")
        date_end_night = ref_obs.twilight_morning_astronomical(
            date_start_night, which="next"
        )
        time_ranges = Time([date_start_night, date_end_night])
    # If the detection time is during day time, use the night starting date
    # as a starting date and the end of the night as an ending date
    elif date_start_night > ref_date and date_end_night > ref_date:
        date_start_night = ref_obs.twilight_evening_astronomical(ref_date, which="next")
        date_end_night = ref_obs.twilight_morning_astronomical(
            date_start_night, which="next"
        )
        time_ranges = Time([date_start_night, date_end_night])
    elif date_start_night > ref_date and date_end_night < ref_date:
        date_end_night = ref_obs.twilight_morning_astronomical(ref_date, which="next")
        time_ranges = Time([date_start_night, date_end_night])
    return time_ranges


def target_observability(target: Target) -> bool:
    """
    Return true of the target are observable at the observatory

    Parameters
    ----------
    observatory : Observer
        the observatory to test
    target : Target
        the target to test

    Returns
    -------
    bool
        if True, the target is observable to the observatory
    """
    targets = FixedTarget(coord=SkyCoord(ra=target.ra * u.deg, dec=target.dec * u.deg))

    def observability_test(observatory):
        time_range = simu_night_time_interval(
            observatory, Time(target.epoch, format="jd")
        )
        return is_observable(
            observatory.gvom_constraints,
            observatory,
            targets,
            time_range=time_range,
            time_grid_resolution=1 * u.hour,
        )

    is_observable_colibri = observability_test(ColibriFacility.observatory)
    return is_observable_colibri


def return_time_constraints(
    observatory: Observer,
    target: FixedTarget,
    constraints: list,
    target_trig_time: float,
    time_resolution: float,
):
    target_trigger_time = Time(target_trig_time, format="jd")
    time_range = simu_night_time_interval(observatory, target_trigger_time)
    observable = is_observable(constraints, observatory, target, time_range=time_range)
    if observable:
        obs_table = observability_table(
            constraints, observatory, [target], time_range=time_range
        )
        time_grid = time_grid_from_range(
            [time_range[0], time_range[1]], time_resolution=time_resolution
        )

        observability_grid = np.zeros((len(constraints), len(time_grid)))

        for i, constraint in enumerate(constraints):
            # Evaluate each constraint
            observability_grid[i, :] = constraint(observatory, target, times=time_grid)

        all_cons_true = np.array(observability_grid).all(axis=0)
        return (
            time_grid[all_cons_true],
            obs_table["fraction of time observable"].value[0],
        )
    else:
        return np.array([]), 0.0


def gvom_target_observability(target, target_trig_time):
    gvom_network = [
        ColibriFacility(),
        XinglongFacility(),
        JilinFacility(),
        OHPFacility(),
        ORMFacility(),
        MaidanakFacility(),
    ]

    obs_res = [
        [
            obs.name,
            *return_time_constraints(
                obs.observatory,
                target,
                obs.constraints,
                target_trig_time,
                10 * u.minute,
            ),
        ]
        for obs in gvom_network
    ]
    return np.array(obs_res, dtype="object")


def is_target_observable(tom_target):
    astroplan_target = FixedTarget(
        coord=SkyCoord(tom_target.ra, tom_target.dec, unit="deg"), name=tom_target.name
    )

    observability = gvom_target_observability(astroplan_target, tom_target.epoch)

    res_pdf = pd.DataFrame(
        observability, columns=["observatory", "observable_time", "observable_fraction"]
    )
    res_pdf["objectId"] = tom_target.name
    return res_pdf


def start(target, target_list):
    logger.info("start the cadence for the target: {}".format(target))
    pdf_obs = is_target_observable(target)

    # list of observatory where the target must be observable
    required_obs_pdf = pdf_obs[
        pdf_obs["observatory"].isin(
            [
                ColibriFacility().name,
                XinglongFacility().name,
                JilinFacility().name,
                # ORMFacility().name
            ]
        )
    ]
    is_observable_in_gvom = (required_obs_pdf["observable_fraction"] != 0.0).all()

    if is_observable_in_gvom:
        public_group, _ = Group.objects.get_or_create(name="Public")
        target.save()
        target_list.targets.add(target)
        assign_perm("tom_targets.view_target", public_group, target)

        dynamic_cadence = DynamicCadence(
            cadence_strategy="GVOMCadence", created=datetime.datetime.now(), active=True
        )
        cadence = get_cadence_strategy("GVOMCadence")(dynamic_cadence)
        cadence.run()
