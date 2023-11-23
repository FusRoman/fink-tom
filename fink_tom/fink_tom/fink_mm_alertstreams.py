from tom_alertstreams.alertstreams.alertstream import AlertStream
import logging
from fink_client.consumer import AlertConsumer
from tom_targets.models import Target, TargetList
from psycopg2.errors import UniqueViolation
from django.db.utils import IntegrityError
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Group

from astropy.coordinates import SkyCoord
from astropy.time import Time

from astropy.coordinates import SkyCoord
from tom_common.hooks import run_hook

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FinkMMAlertStream(AlertStream):
    required_keys = [
        "FINK_STREAM_CLIENT_ID",
        "FINK_STREAM_SERVERS",
        "FINK_STREAM_GROUP_ID",
        "TOPIC_HANDLERS",
    ]
    allowed_keys = [
        "FINK_STREAM_CLIENT_ID",
        "FINK_STREAM_SERVERS",
        "FINK_STREAM_GROUP_ID",
        "TOPIC_HANDLERS",
        "NUMALERTS",
        "MAXTIMEOUT",
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.all_topics = list(self.topic_handlers.keys())

        self.target_list = {}
        public_group, _ = Group.objects.get_or_create(name="Public")
        for topic in self.all_topics:
            tl, is_created = TargetList.objects.get_or_create(name=topic)
            assign_perm("tom_targets.view_targetlist", public_group, tl)
            self.target_list[topic] = tl

    def listen(self):
        super().listen()

        logger.info("START TO LISTENING")

        fink_config = {
            "username": self.fink_stream_client_id,
            "bootstrap.servers": self.fink_stream_servers,
            "group_id": self.fink_stream_group_id,
        }

        logger.info(
            f"CREATE CONSUMER, \n\ttopics: {self.all_topics}\n\tfink_config: {fink_config}"
        )
        consumer = AlertConsumer(self.all_topics, fink_config)

        while True:
            logger.info("IS LISTENING ...")
            res_consume = consumer.consume(int(self.numalerts), int(self.maxtimeout))
            for topic, alert, key in res_consume:
                logger.info("MSG IS COMMING")
                logger.info(f"\n\ttopic : {topic}")
                try:
                    self.alert_handler[topic](self, topic, alert)

                except KeyError as err:
                    logger.error(
                        f"alert from topic {topic} received but no handler defined. err: {err}"
                    )
                except Exception:
                    logger.error(
                        f"exception raised during the handler call", exc_info=1
                    )

        consumer.close()


def ztf_alert_processor(finkmm_stream, topic, alert):
    """ZTF alert handler for ZTF alerts recover through the Fink Broker"""
    logger.info(
        f'fink_mm_alertstreams.ztf_alert_processor alert:\n\t{alert["objectId"]}\n\t{alert["candidate"]["jd"]}\n\t{alert["candidate"]["ra"]}\n\t{alert["candidate"]["dec"]}'
    )

    target_list = finkmm_stream.target_list[topic]
    t = Target(
        name=alert["objectId"],
        type="SIDEREAL",
        ra=alert["candidate"]["ra"],
        dec=alert["candidate"]["dec"],
        epoch=alert["candidate"]["jd"],
    )
    logger.info("SAVE TARGET")
    try:
        run_hook("gvom_start_cadence", target=t, target_list=target_list, alert=alert, topic=topic)
    except UniqueViolation:
        logger.error(f"Target {t} already in the database")
    except Exception:
        logger.error("error when trying to save new alerts in the db", exc_info=1)


def mm_alert_processor(finkmm_stream, topic, alert):
    """
    Multi-messenger alert handler for Fink
    """
    logger.info(
        f'fink_mm_alertstreams.mm_alert_processor alert:\n\t{alert["objectId"]}\n\t{alert["triggerId"]}'
    )

    public_group, _ = Group.objects.get_or_create(name="Public")
    target_list = finkmm_stream.target_list[topic]
    t = Target(
        name=alert["objectId"] + "_" + alert["triggerId"],
        type="SIDEREAL",
        ra=alert["ztf_ra"],
        dec=alert["ztf_dec"],
        epoch=alert["jd"],
    )

    logger.info("SAVE TARGET")
    try:
        gcn_sep = SkyCoord(alert["ztf_ra"], alert["ztf_dec"], unit="deg").separation(
            SkyCoord(alert["gcn_ra"], alert["gcn_dec"], unit="deg")
        )
        gcn_time_jd = Time(alert["triggerTimeUTC"]).jd
        t.save(
            extras={
                "triggerId": alert["triggerId"],
                "gcn_status": alert["gcn_status"],
                "gcn_ra": alert["gcn_ra"],
                "gcn_dec": alert["gcn_dec"],
                "distance to the gcn (degree)": gcn_sep.deg,
                "gcn_loc_error (in arcmin)": alert["gcn_loc_error"],
                "triggerTimeUTC": alert["triggerTimeUTC"],
                "delta_time (in day)": alert["jd"] - gcn_time_jd,
            }
        )

        target_list.targets.add(t)
        assign_perm("tom_targets.view_target", public_group, t)

        run_hook("gvom_start_cadence", target=t, target_list=target_list, alert=alert, topic=topic)
    except UniqueViolation:
        logger.error(f"Target {t} already in the database")
    except IntegrityError as ue:
        logger.error(f"Target {t} already in the database")
    except Exception:
        logger.error("error when trying to save new alerts in the db", exc_info=1)
