from tom_observations.facility import (
    BaseRoboticObservationFacility,
    BaseRoboticObservationForm,
)
from astroplan import Observer
import astropy.units as u
from astroplan import (
    AltitudeConstraint,
    AirmassConstraint,
    MoonSeparationConstraint,
    AtNightConstraint,
)


class JilinForm(BaseRoboticObservationForm):
    pass


class JilinFacility(BaseRoboticObservationFacility):
    name = "Jilin"
    observation_types = observation_forms = {"OBSERVATION": JilinForm}

    SITES = {
        "Jilin": {
            "sitecode": "jil",
            "latitude": 43.824377777777784,
            "longitude": 126.3304611111111,
            "elevation": 900,
        }
    }

    observatory = Observer(
        longitude=SITES[list(SITES.keys())[0]]["longitude"] * u.deg,
        latitude=SITES[list(SITES.keys())[0]]["latitude"] * u.deg,
        elevation=SITES[list(SITES.keys())[0]]["elevation"] * u.m,
        name=list(SITES.keys())[0],
    )

    constraints = [
        AltitudeConstraint(30 * u.deg, 90 * u.deg),
        AirmassConstraint(2),
        MoonSeparationConstraint(min=20 * u.deg),
        AtNightConstraint.twilight_astronomical(),
    ]

    def data_products(self, observation_id, product_id=None):
        return []

    def get_form(self, observation_type):
        return JilinForm

    def get_observation_status(self, observation_id):
        return ["NOT CONNECTED"]

    def get_observation_url(self, observation_id):
        return ""

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
        return self.SITES

    def get_facility_weather_urls(self):
        """
        Returns a dictionary containing a URL for weather information
        for each site in the Facility SITES. This is intended to be useful
        in observation planning.

        `facility_weather = {'code': 'XYZ', 'sites': [ site_dict, ... ]}`
        where
        `site_dict = {'code': 'XYZ', 'weather_url': 'http://path/to/weather'}`

        """
        return {
            "code": self.name,
            "sites": [
                {
                    "code": list(self.SITES.keys())[0],
                    "weather_url": "https://www.colibri-obs.org/?page_id=790",
                }
            ],
        }

    def get_facility_status(self):
        """
        Returns a dictionary describing the current availability of the Facility
        telescopes. This is intended to be useful in observation planning.
        The top-level (Facility) dictionary has a list of sites. Each site
        is represented by a site dictionary which has a list of telescopes.
        Each telescope has an identifier (code) and an status string.

        The dictionary hierarchy is of the form:

        `facility_dict = {'code': 'XYZ', 'sites': [ site_dict, ... ]}`
        where
        `site_dict = {'code': 'XYZ', 'telescopes': [ telescope_dict, ... ]}`
        where
        `telescope_dict = {'code': 'XYZ', 'status': 'AVAILABILITY'}`

        See lco.py for a concrete implementation example.
        """
        return {
            "code": self.name,
            "sites": [
                {
                    "code": list(self.SITES.keys())[0],
                    "telescopes": [{"code": "jilin.telescope", "status": "Available"}],
                }
            ],
        }
