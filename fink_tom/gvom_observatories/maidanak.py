from tom_observations.facility import BaseRoboticObservationFacility, BaseRoboticObservationForm


class MaidanakForm(BaseRoboticObservationForm):
    pass


class MaidanakFacility(BaseRoboticObservationFacility):
    name = 'Maidanak'
    observation_types = observation_forms = {
        'OBSERVATION': MaidanakForm
    }


    SITES = {
        'Maidanak': {
            'latitude': 38.6733975,

            'longitude': 66.8956051,

            'elevation': 2593
        }
    }

    def data_products(self, observation_id, product_id=None):
        return []

    def get_form(self, observation_type):
        return MaidanakForm

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
