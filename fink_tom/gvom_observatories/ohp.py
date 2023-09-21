from tom_observations.facility import BaseRoboticObservationFacility, BaseRoboticObservationForm


class OHPForm(BaseRoboticObservationForm):
    pass


class OHPFacility(BaseRoboticObservationFacility):
    name = 'OHP'
    observation_types = observation_forms = {
        'OBSERVATION': OHPForm
    }

    SITES = {
        'OHP': {
            'latitude': 43.93083333333333,

            'longitude': 5.713333333333334,

            'elevation': 650.0000000000365
        }
    }

    def data_products(self, observation_id, product_id=None):
        return []

    def get_form(self, observation_type):
        return OHPForm

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
