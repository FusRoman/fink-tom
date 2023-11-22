import os
from slack import WebClient
from astropy.coordinates import SkyCoord
from astropy.time import Time
from django.conf import settings


def post_msg_on_slack(alert):

    link_fink = f"https://fink-portal.org/{alert['objectId']}"
    ra, dec = alert['candidate']['ra'], alert['candidate']['dec']

    equ_coord=f"EQU: ra={ra}, dec={dec}"
    coord = SkyCoord(ra=ra, dec=dec, unit="deg")
    gal_coord = f"GAL: l={coord.galactic.l.value}, b={coord.galactic.b.value}"
    ecl_coord = f"GAL: l={coord.transform_to('geocentricmeanecliptic').lon.value}, b={coord.transform_to('geocentricmeanecliptic').lat.value}"
    
    utc_time = f"UTC: {Time(alert['candidate']['jd'], format='jd').iso}"

    slack_msg = f"""
{link_fink}
{equ_coord}
{gal_coord}
{equ_coord}
{utc_time}
"""
    client = WebClient(token=settings.SLACK_BOT_TOKEN)
    client.chat_postMessage(
                channel='#gvom_targets',
                text=slack_msg,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": slack_msg
                        }
                    }
                ]
            )