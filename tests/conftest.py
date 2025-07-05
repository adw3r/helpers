import pathlib

import sys
import pytest


ROOT_DIR = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(scope="session", autouse=True)
def set_env():
    env_file = ROOT_DIR / ".env"
    if env_file.exists():
        from dotenv import load_dotenv

        load_dotenv(env_file)
