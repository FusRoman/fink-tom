from tom_observations.facility import BaseRoboticObservationFacility, BaseRoboticObservationForm
from astroplan import Observer
import astropy.units as u


class ColibriForm(BaseRoboticObservationForm):
    pass


class ColibriFacility(BaseRoboticObservationFacility):
    name = 'Colibri'
    observation_types = observation_forms = {
        'OBSERVATION': ColibriForm
    }

    SITES = {
        '(OAN) San PedroMártir': {
            'latitude': 31.029166666666665,
            'longitude': -115.48694444444442,
            'elevation': 2829.9999999997976
        }
    }

    observatory = Observer(
        longitude=SITES['(OAN) San PedroMártir']['longitude'] * u.deg,
        latitude=SITES['(OAN) San PedroMártir']['latitude'] * u.deg,
        elevation=SITES['(OAN) San PedroMártir']['elevation'] * u.m,
        name=list(SITES.keys())[0],
    )

    def data_products(self, observation_id, product_id=None):
        return []

    def get_form(self, observation_type):
        return ColibriForm

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

