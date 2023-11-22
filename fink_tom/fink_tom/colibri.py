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
from django import forms
from crispy_forms.layout import Layout
import logging

logger = logging.getLogger("django.console")


class ColibriForm(BaseRoboticObservationForm):
    exposure_time = forms.IntegerField()
    exposure_count = forms.IntegerField()
    filter_choice = forms.MultipleChoiceField(
        choices=(
            ("g", "g"),
            ("r", "r"),
            ("i", "i"),
            ("z", "z"),
            ("y", "y"),
            ("J", "J"),
            ("H", "H")
        )
    )

    def layout(self):
        return Layout("exposure_time", "exposure_count", "filter_choice")


class ColibriFacility(BaseRoboticObservationFacility):
    name = "Colibri"
    observation_types = observation_forms = {"OBSERVATION": ColibriForm}

    SITES = {
        "(OAN) San PedroMártir": {
            "sitecode": "col",
            "latitude": 31.029166666666665,
            "longitude": -115.48694444444442,
            "elevation": 2829.9999999997976,
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
        return ColibriForm

    def get_observation_status(self, observation_id):
        return ["NOT CONNECTED"]

    def get_observation_url(self, observation_id):
        return ""

    def get_terminal_observing_states(self):
        return ["NOT CONNECTED", "IN PROGRESS", "COMPLETED"]

    def submit_observation(self, observation_payload):
        print("PAYLOAD:")
        logger.info(observation_payload)
        logger.info('This is an info message')
        print()
        return [1]

    def validate_observation(self, observation_payload):
        logger.info("VALIDATING ...")
        logger.info("-------------- TOTO -------------------")
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
                    "telescopes": [{"code": "colibri.oan@1.3m", "status": "Available"}],
                }
            ],
        }
