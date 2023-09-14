from tom_alertstreams.alertstreams.alertstream import AlertStream
import logging
from fink_client.consumer import AlertConsumer


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FinkMMAlertStream(AlertStream):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def listen(self):
        super().listen()

        required_keys = ['FINK_STREAM_CLIENT_ID', 'FINK_STREAM_SERVERS', 'FINK_STREAM_GROUP_ID', 'TOPIC_HANDLERS']
        allowed_keys = ['FINK_STREAM_CLIENT_ID', 'FINK_STREAM_SERVERS', 'FINK_STREAM_GROUP_ID', 'TOPIC_HANDLERS', 'NUMALERTS', 'MAXTIMEOUT']

        fink_config = {
            'username': self.fink_stream_client_id,
            'bootstrap.servers': self.fink_stream_servers,
            'group_id': self.fink_stream_group_id
        }

        topics = list(self.topic_handlers.keys())

        consumer = AlertConsumer(topics, fink_config)

        while True:
            res_consume = consumer.consume(self.numalerts, self.maxtimeout)
            for topic, alert, key in res_consume:
                try:
                    self.alert_handler[topic](alert)
                except KeyError as err:
                    logger.error(f'alert from topic {topic} received but no handler defined. err: {err}')
                except Exception:
                    logger.error(f"exception raised during the handler call", exc_info=1)

        consumer.close()


def alert_logger(alert):
    """Example alert handler for GCN Classic over Kafka

    This alert handler simply logs the topic and value of the cimpl.Message instance.

    See https://docs.confluent.io/4.1.1/clients/confluent-kafka-python/index.html#message
    for cimpl.Message details.
    """
    logger.info(f'gcn.alert_logger alert.value(): {alert}')



