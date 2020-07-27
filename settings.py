import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

slack_webhook_url = os.environ.get('slack_webhook_url')
slack_user_id = os.environ.get('slack_user_id')
api_token = os.environ.get('api_token')
doc_data_dir = os.environ.get('doc_data_dir')
sentences_data_dir = os.environ.get('sentences_data_dir')
sentences_data_name = os.environ.get('sentences_data_name')
