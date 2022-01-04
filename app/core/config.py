
import yaml

config_file = 'config.yml'
with open(config_file, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

PROJECT_NAME = config['project_name']
VERSION = config['version']
API_PREFIX = '/api'

scraper_config = config['scraper_info']
CONSUMER_KEY = scraper_config['consumer_key']
CONSUMER_SECRET = scraper_config['consumer_secret']
CALLBACK_URI = scraper_config['callback_uri']