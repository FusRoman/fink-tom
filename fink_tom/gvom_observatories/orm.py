from tom_observations.facility import BaseRoboticObservationFacility, BaseRoboticObservationForm


class ORMForm(BaseRoboticObservationForm):
    pass


class ORMFacility(BaseRoboticObservationFacility):
    name = 'ORM'
    observation_types = observation_forms = {
        'OBSERVATION': ORMForm
    }

    SITES = {
        'ORM': {
            'latitude': 28.758333333333336,

            'longitude': -17.879999999999995,

            'elevation': 2326.999999998442
        }
    }

    def data_products(self, observation_id, product_id=None):
        return []

    def get_form(self, observation_type):
        return ORMForm

    def get_observation_status(self, observation_id):
        return ["NOT CONNECTED"]
    
    def get_observation_url(self, observation_id):
        return ''
    
    def get_terminal_observing_states(self):
        return ["NOT CONNECTED", "IN PROGRESS", "COMPLETED"]
    
    def submit_observation(self, observation_payload):
        print("PAYLOAD:")
        print(observation_payload)
        print()
        return [1]
    
    def validate_observation(self, observation_payload):
        print("VALIDATING ...")
        pass
    
    def get_observing_sites(self):
        return {}
