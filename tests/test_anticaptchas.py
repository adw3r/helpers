import os

import pytest

from helpers import anticaptchas
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.asyncio(loop_scope="session")
async def test_anticaptcha():
    cap = anticaptchas.AntiCaptchaAPI(os.getenv("ANTICAPTCHA_KEY"))
    balance_response = await cap.get_balance()
    print(balance_response.text)
    assert balance_response.is_success
