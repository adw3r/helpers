import pytest

from helpers import anticaptchas


@pytest.mark.asyncio
async def test_anticaptcha():
    cap = anticaptchas.AntiCaptchaAPI('')
    balance_response = await cap.get_balance()
    assert balance_response.is_success
