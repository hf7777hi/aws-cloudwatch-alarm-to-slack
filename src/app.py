import boto3
import json
import logging
import os
import sys

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

LOGFMT="[%(levelname)s] %(asctime)s\t[%(pathname)s l.%(lineno)s %(funcName)s]\t%(message)s"
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
  logger.info('event: %s', event)
  
  slack_message = {'channel': os.getenv("SLACK_CHANNEL")}
  try:
    message = json.loads(event['Records'][0]['Sns']['Message'])
    
    alarm_name = message['AlarmName']
    reason = message['NewStateReason']
    # template.yamlの設定から直接拾う(OK, NG, INSUFFICIENT_DATA 以外はNewStateValueの値使う)
    state_emoji = os.getenv(message['NewStateValue'], message['NewStateValue'])

    slack_message['text'] = "%s *%s* %s\n```%s```" % (state_emoji, alarm_name, state_emoji, reason)
  except:
    import traceback
    t, v, tb = sys.exc_info()
    trace = traceback.format_exception(t,v,tb)
    logger.error(trace)
    # 例外時はslackにも内容を通知する。
    state_emoji = os.getenv('EXCEPTION')
    slack_message['text'] = "%s `%s` %s\n```%s```" % (state_emoji, trace, state_emoji, event)

  logger.info("slack_message: %s", slack_message)
  post(slack_message)

# Post massage to slack
def post(message):
  token = boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.getenv("ENCRYPTED_INCOMING_URL")))['Plaintext'].decode('utf-8')
  req = Request("https://" + token, json.dumps(message).encode('utf-8'))
  try:
    response = urlopen(req)
    response.read()
    logger.info("Message posted to %s", message['channel'])
  except HTTPError as e:
    logger.error("Request failed: %d %s", e.code, e.reason)
  except URLError as e:
    logger.error("Server connection failed: %s", e.reason)
