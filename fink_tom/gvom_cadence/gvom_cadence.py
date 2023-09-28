from tom_observations.cadence import CadenceStrategy
from tom_observations.models import ObservationRecord
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GVOMCadence(CadenceStrategy):

    def run(self):
        
        logger.info("run the cadence ...")
        obs_record = ObservationRecord.objects.get_or_create(
        )