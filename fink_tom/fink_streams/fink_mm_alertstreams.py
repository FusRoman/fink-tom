from tom_alertstreams.alertstreams.alertstream import AlertStream
import logging
from fink_client.consumer import AlertConsumer
from tom_targets.models import Target, TargetMatchManager, TargetList
from psycopg2.errors import UniqueViolation

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FinkMMAlertStream(AlertStream):
    required_keys = ['FINK_STREAM_CLIENT_ID', 'FINK_STREAM_SERVERS', 'FINK_STREAM_GROUP_ID', 'TOPIC_HANDLERS']
    allowed_keys = ['FINK_STREAM_CLIENT_ID', 'FINK_STREAM_SERVERS', 'FINK_STREAM_GROUP_ID', 'TOPIC_HANDLERS', 'NUMALERTS', 'MAXTIMEOUT']

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.all_topics = list(self.topic_handlers.keys())
        self.target_list = {topic : TargetList(name=topic) for topic in self.all_topics}
        for tl in self.target_list.values():
            tl.save()

    def listen(self):
        super().listen()

        logger.info("START TO LISTENING")

        fink_config = {
            'username': self.fink_stream_client_id,
            'bootstrap.servers': self.fink_stream_servers,
            'group_id': self.fink_stream_group_id
        }

        logger.info(f"CREATE CONSUMER, \n\ttopics: {self.all_topics}\n\tfink_config: {fink_config}")
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
                    logger.error(f'alert from topic {topic} received but no handler defined. err: {err}')
                except Exception:
                    logger.error(f"exception raised during the handler call", exc_info=1)

        consumer.close()


def alert_logger(finkmm_stream, topic, alert):
    """Example alert handler for GCN Classic over Kafka

    This alert handler simply logs the topic and value of the cimpl.Message instance.

    See https://docs.confluent.io/4.1.1/clients/confluent-kafka-python/index.html#message
    for cimpl.Message details.
    """
    logger.info(f'gcn.alert_logger alert:\n\t{alert["objectId"]}\n\t{alert["candidate"]["jd"]}\n\t{alert["candidate"]["ra"]}\n\t{alert["candidate"]["dec"]}')
    
    t_search_manager = TargetMatchManager()
    r_search = t_search_manager.check_for_fuzzy_match(alert["objectId"])
    print(r_search)

    target_list = finkmm_stream.target_list[topic]
    t = Target(
        name=alert["objectId"],
        type='SIDEREAL',
        ra=alert["candidate"]["ra"],
        dec=alert["candidate"]["dec"],
        epoch=alert["candidate"]["jd"]
    )

    logger.info("SAVE TARGET")
    try:
        t.save()
        target_list.targets.add(t)
    except UniqueViolation:
        logger.error(f"Target {t} already in the database")
    except Exception:
        logger.error("error when trying to save new alerts in the db", exc_info=1)



