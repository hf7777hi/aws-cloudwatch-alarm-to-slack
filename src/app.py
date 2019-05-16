import boto3
import json
import logging
import os
import sys

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

LOGFMT="[%(levelname)s]\t%(asctime)s.%(msecs)03d\t[%(pathname)s l.%(lineno)s %(funcName)s]\t%(message)s"
DATEFMT="%Y%m%d %H:%M:%S" 
logger = logging.getLogger()
for h in logger.handlers:
    logger.removeHandler(h)
h = logging.StreamHandler(sys.stdout)
h.setFormatter(logging.Formatter(LOGFMT, datefmt=DATEFMT))
logger.addHandler(h)
logger.setLevel(logging.INFO)
if os.getenv("STAGE") != "PROD":
    logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    logger.info("-----> start. %s", event)
    logger.info(event['Records'][0]['Sns']['Message'])
    message = json.loads(event['Records'][0]['Sns']['Message'])
    logger.info("Message: " + str(message))

    alarm_name = message['AlarmName']
    #old_state = message['OldStateValue']
    new_state = message['NewStateValue']
    reason = message['NewStateReason']

    slack_message = {
        'channel': os.getenv("SLACK_CHANNEL"),
        'text': "%s state is now %s: %s" % (alarm_name, new_state, reason)
    }
    post(slack_message)

# Post massage to slack
def post(message):
    token = boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.getenv("ENCRYPTED_INCOMING_TOKEN")))['Plaintext'].decode('utf-8')
    req = Request(os.getenv("WEBHOOK_URL") + token, json.dumps(message).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
