import logging
import datetime
from tom_observations.cadence import get_cadence_strategy
from tom_observations.models import DynamicCadence
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Group

from tom_targets.models import Target
from astropy.time import Time

# import facilities
from fink_tom.colibri import ColibriFacility
from fink_tom.jilin import JilinFacility
from fink_tom.xinglong import XinglongFacility
from fink_tom.slack_bot import post_msg_on_slack
from fink_tom.observability import is_target_observable

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def start(target: Target, target_list, alert, topic):
    logger.info("start the cadence for the target: {}".format(target))
    pdf_obs = is_target_observable(target, target.epoch)

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

    logger.info(f"is observable: {is_observable_in_gvom}")
    if is_observable_in_gvom:
        logger.info("target {} observable by gvom network".format(target))
        public_group, _ = Group.objects.get_or_create(name="Public")
        target.save(extras={
            "triggerTimeUTC": Time(target.epoch, format="jd").iso
        })
        target_list.targets.add(target)
        assign_perm("tom_targets.view_target", public_group, target)
        post_msg_on_slack(alert, target)

        dynamic_cadence = DynamicCadence(
            cadence_strategy="GVOMCadence", created=datetime.datetime.now(), active=True
        )
        cadence = get_cadence_strategy("GVOMCadence")(dynamic_cadence)
        cadence.run()
