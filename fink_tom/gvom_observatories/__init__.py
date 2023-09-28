from astroplan import AltitudeConstraint, AirmassConstraint, MoonSeparationConstraint
import astropy.units as u

gvom_constraints = [
    AltitudeConstraint(30 * u.deg, 90 * u.deg),
    AirmassConstraint(2),
    MoonSeparationConstraint(min=20* u.deg)
]