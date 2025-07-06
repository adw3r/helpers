import os

import pytest

import helpers
from dotenv import load_dotenv

load_dotenv()


class TestRapidApi44:
    cli = helpers.fake_mails.RapidApi44(os.environ["RAPIDAPI_KEY"])

    async def test_create_email(self):
        resp = await self.cli.create_email()
        assert self.cli.apikey is not None
        assert resp.status_code == 200
        assert resp.json()["email"] != ""

    async def test_create_instance(self):
        cli = await self.cli.create_instance()
        assert cli.apikey is not None
        assert cli.email is not None

    async def test_get_message_response(self):
        cli = await self.cli.create_instance()
        assert cli.apikey is not None
        resp = await cli.get_messages()
        print(resp.text)
        assert resp.status_code == 200

    async def test_wait_for_html(self):
        cli = await self.cli.create_instance()
        html = await cli.wait_for_html(attempts=2, timer=0)
        assert html is None


class TestRegMailSpace:
    cli = helpers.fake_mails.RapidApi44(os.environ["REG_MAIL_API_KEY"])

    async def test_create_instance(self):
        cli = await self.cli.create_instance()
        assert cli.apikey is not None
        assert cli.email is not None

    async def test_wait_for_html(self):
        cli = await self.cli.create_instance()
        html = await cli.wait_for_html(attempts=2, timer=0)
        assert html is None


class TestOneSecMail:
    cli = helpers.fake_mails.OneSecMail()
    async def test_create_instance(self):
        pytest.skip("OneSecMail is not working")
        cli = await self.cli.create_instance()
        assert cli.email is not None

    async def test_wait_for_html(self):
        pytest.skip("OneSecMail is not working")
        cli = await self.cli.create_instance()
        html = await cli.wait_for_html(attempts=2, timer=0)
        assert html is None


class TestTempMailApi:
    cli = helpers.fake_mails.TempMailApi(os.getenv("TEMP_MAIL_API_KEY"))

    async def test_create_instance(self):
        cli = await self.cli.create_instance()
        assert cli.email is not None
        assert cli.apikey is not None
        messages = await cli.get_messages()
        assert messages.text == '{"error":"There are no emails yet"}'

    async def test_wait_for_html(self):
        cli = await self.cli.create_instance()
        html = await cli.wait_for_html(attempts=2, timer=0)
        assert html is None
