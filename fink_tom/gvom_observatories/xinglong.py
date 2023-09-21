from tom_observations.facility import BaseRoboticObservationFacility, BaseRoboticObservationForm


class XinglongForm(BaseRoboticObservationForm):
    pass


class XinglongFacility(BaseRoboticObservationFacility):
    name = 'Xinglong'
    observation_types = observation_forms = {
        'OBSERVATION': XinglongForm
    }

    SITES = {
        'Xinglong': {
            'latitude': 40.393333333333324,

            'longitude': 117.57500000000002,

            'elevation': 949.9999999991034
        }
    }

    def data_products(self, observation_id, product_id=None):
        return []

    def get_form(self, observation_type):
        return XinglongForm

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
