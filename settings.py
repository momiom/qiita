import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

slack_webhook_url = os.environ.get("slack_webhook_url")
api_token = os.environ.get("api_token")
