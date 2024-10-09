import os
import pathlib

import json


ROOT_FOLDER = pathlib.Path(__file__).parent.absolute()
env_file = ROOT_FOLDER / 'config.json'
with open(env_file, 'r') as f:
    config = json.load(f)
os.environ.update(config)

ENVIRONMENT = dict(os.environ)

# Anti Captcha
ANTICAPTCHA_APIKEY = ENVIRONMENT['ANTICAPTCHA_APIKEY']
