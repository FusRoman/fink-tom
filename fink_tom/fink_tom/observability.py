import plotly.express as px
import pandas as pd
import numpy as np
from astropy.time import Time
import astropy.units as u
from astroplan import Observer, FixedTarget, is_observable, observability_table, is_event_observable
from astroplan.utils import time_grid_from_range
from astropy.coordinates import SkyCoord
from tom_observations.facility import get_service_classes

from tom_targets.models import Target


gvom_network = [
    facility_class()
    for facility_class in get_service_classes().values()
]

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


def return_time_constraints(
    observatory: Observer,
    target: Target,
    constraints: list,
    time_range: Time,
    time_resolution: float,
):
    target = FixedTarget(coord=SkyCoord(ra=target.ra * u.deg, dec=target.dec * u.deg), name=target.name)
    observable = is_observable(constraints, observatory, target, time_range=time_range)
    if observable:
        obs_table = observability_table(
            constraints, observatory, [target], time_range=time_range
        )
        time_grid = time_grid_from_range(
            [time_range[0], time_range[1]], time_resolution=time_resolution
        )

        test_observability = is_event_observable(
            constraints,
            observatory,
            target,
            time_grid
        )[0]

        return (
            time_grid[test_observability],
            obs_table["fraction of time observable"].value[0],
        )
    else:
        return np.array([]), 0.0

def gvom_target_observability(target, start, end):
    if end is None:
        obs_res = [
            [
                obs.name,
                *return_time_constraints(
                    obs.observatory,
                    target,
                    obs.constraints,
                    simu_night_time_interval(obs.observatory, Time(start, format="jd")),
                    10 * u.minute,
                ),
            ]
            for obs in gvom_network
        ]
    else:
        obs_res = [
            [
                obs.name,
                *return_time_constraints(
                    obs.observatory,
                    target,
                    obs.constraints,
                    Time([start, end], format="datetime"),
                    10 * u.minute,
                ),
            ]
            for obs in gvom_network
        ]
    return np.array(obs_res, dtype="object")

def is_target_observable(target, start, end=None):
    observability = gvom_target_observability(target, start, end)

    res_pdf = pd.DataFrame(
        observability, columns=["observatory", "observable_time", "observable_fraction"]
    )
    res_pdf["objectId"] = target.name
    return res_pdf

def observability_figure(target, start, end):
    pdf_obs = is_target_observable(target, start, end)

    t = pd.concat(
        [
            pd.DataFrame(
                [
                    dict(
                        Observatory=obs.name,
                        Start=Time(time, format="jd").iso,
                        Finish=(Time(time, format="jd") + (10 * u.minute)).iso,
                    )
                    for time in pdf_obs[pdf_obs["observatory"] == obs.name][
                        "observable_time"
                    ].values[0]
                ]
            )
            for obs in gvom_network
        ]
    )
    fig = px.timeline(
        t,
        x_start="Start",
        x_end="Finish",
        y="Observatory",
        color="Observatory",
        title=f"{target.name} Observability by gvom network",
    )
    return fig


