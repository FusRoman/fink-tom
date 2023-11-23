from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from astropy.coordinates import SkyCoord
from astropy.time import Time
from django.conf import settings
import logging
import io
from datetime import datetime, timedelta
from PIL import Image
import time
import matplotlib.pyplot as plt
from fink_science.image_classification.utils import unzip_cutout, img_normalizer
from fink_tom.observability import observability_figure

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def unzip_img(stamp, title_name):
    min_img = 0
    max_img = 255
    img = img_normalizer(unzip_cutout(stamp), min_img, max_img)
    img = Image.fromarray(img).convert("L")

    _ = plt.figure(figsize=(15, 6))
    plt.imshow(img, cmap='gray', vmin=min_img, vmax=max_img)
    plt.title(title_name)
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return buf



def post_msg_on_slack(alert, target):

    client = WebClient(token=settings.SLACK_BOT_TOKEN)
    link_fink = f"https://fink-portal.org/{alert['objectId']}"
    link_tom = f"http://157.136.249.112:1337/targets/{target.id}/"

    ra, dec = alert['candidate']['ra'], alert['candidate']['dec']

    equ_coord=f"EQU: ra={ra:.6f}, dec={dec:.6f}"
    coord = SkyCoord(ra=ra, dec=dec, unit="deg")
    gal_coord = f"GAL: l={coord.galactic.l.value:.6f}, b={coord.galactic.b.value:.6f}"
    ecl_coord = f"ECL: l={coord.transform_to('geocentricmeanecliptic').lon.value:.6f}, b={coord.transform_to('geocentricmeanecliptic').lat.value:.6f}"
    
    utc_time = f"UTC: {Time(alert['candidate']['jd'], format='jd').iso}"

    science_img = unzip_img(alert['cutoutScience']['stampData'], "Science")
    science_temp = unzip_img(alert['cutoutTemplate']['stampData'], "Template")
    science_diff = unzip_img(alert['cutoutDifference']['stampData'], "Difference")

    fig = observability_figure(target, datetime.utcnow(), datetime.utcnow() + timedelta(days=1))
    bytes_fig = io.BytesIO(fig.to_image(format="png"))
    bytes_fig.seek(0)


    result = client.files_upload_v2(
            file_uploads=[
                {
                    "file": science_img,
                    "title": "science"
                },
                {
                    "file": science_temp,
                    "title": "template"
                },
                {
                    "file": science_diff,
                    "title": "difference"
                },
                {
                    "file": bytes_fig,
                    "title": "observability"
                }
            ]
        )
    time.sleep(3)
    
    science_perml = f"<{result['files'][0]['permalink']}|{' '}>"
    template_perml = f"<{result['files'][1]['permalink']}|{' '}>"
    difference_perml = f"<{result['files'][2]['permalink']}|{' '}>"
    obs_perml = f"<{result['files'][3]['permalink']}|{' '}>"

    slack_msg = f"""

===========================================
GVOM Network : New target to follow
{link_fink}
{link_tom}

--- Coordinates
{equ_coord}
{gal_coord}
{ecl_coord}
--- Time
{utc_time}

--- Brightness
magpsf: {alert['candidate']['magpsf']:.6f} ± {alert['candidate']['sigmapsf']:.6f}

--- Cutout
{science_perml}{template_perml}{difference_perml}
{obs_perml}
"""
    try:
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
        time.sleep(3)
        logging.info("Post msg on slack successfull")
    except SlackApiError as e:
        if e.response["ok"] is False:
            logging.error("Post slack msg error", exc_info=1)
