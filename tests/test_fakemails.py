import os

import pytest

import helpers
from dotenv import load_dotenv

load_dotenv()

class TestRapidApi44:
    @pytest.mark.asyncio(loop_scope="session")
    async def test_create_email(self):
        cli = helpers.fake_mails.RapidApi44(os.environ["RAPIDAPI_KEY"])

        resp = await cli.create_email()
        assert resp.status_code == 200
        assert resp.json()["email"] != ""

    @pytest.mark.asyncio(loop_scope="session")
    async def test_create_instance(self):
        cli = helpers.fake_mails.RapidApi44(os.environ["RAPIDAPI_KEY"])

        cli = await cli.create_instance()
        assert cli.email is not None

    @pytest.mark.asyncio(loop_scope="session")
    async def test_get_message_response(self):
        cli = helpers.fake_mails.RapidApi44(os.environ["RAPIDAPI_KEY"])
        cli = await cli.create_instance()
        resp = await cli.get_messages()
        print(resp.text)
        assert resp.status_code == 200


class TestRegMailSpace:

    @pytest.mark.asyncio(loop_scope="session")
    async def test_create_instance(self):
        cli = helpers.fake_mails.RapidApi44(os.environ["REG_MAIL_API_KEY"])

        cli = await cli.create_instance()
        assert cli.email is not None

class TestOneSecMail:

    @pytest.mark.asyncio(loop_scope="session")
    async def test_create_instance(self):
        pytest.skip("OneSecMail is not working")
        cli = helpers.fake_mails.OneSecMail()

        cli = await cli.create_email_instance()
        assert cli.email is not None

class TestTempMailApi:

    @pytest.mark.asyncio(loop_scope="session")
    async def test_create_instance(self):
        cli = helpers.fake_mails.TempMailApi(os.getenv("TEMP_MAIL_API_KEY"))

        cli = cli.create_email_instance()
        print(cli.email)
        assert cli.email is not None
        messages = await cli.get_messages()
        print(messages.text)