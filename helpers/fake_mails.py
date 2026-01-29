import datetime
import typing
import asyncio
import base64
import hashlib
import logging
import random
import re
import string
from abc import ABC, abstractmethod
from typing import Self

import httpx

from . import errors


def generate_username(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class InterFaceWithApiKey:
    apikey: str
    email: str | None = None

    def __init__(self, apikey, email=None):
        self.apikey = apikey
        self.email = email


class InterfaceMethods(ABC):
    email: str | None = None
    def __str__(self):
        return self.email

    @abstractmethod
    async def create_instance(self):
        pass

    @abstractmethod
    async def wait_for_html(self, attempts: int = 5, timeout: int = 10) -> str:
        pass


class InterfaceSession:
    session: httpx.AsyncClient = httpx.AsyncClient(verify=False)


class BasicInterface(InterFaceWithApiKey, InterfaceMethods, InterfaceSession, ABC):
    pass


class TempMailApi(BasicInterface):

    def __repr__(self):
        return f"<TempMailApi {self.email=}>"

    domains = [
        "@cevipsa.com",
        "@cpav3.com",
        "@nuclene.com",
        "@steveix.com",
        "@mocvn.com",
        "@tenvil.com",
        "@tgvis.com",
        "@amozix.com",
        "@anypsd.com",
        "@maxric.com",
    ]
    """
    https://rapidapi.com/Privatix/api/temp-mail
    """

    __base_url = "https://privatix-temp-mail-v1.p.rapidapi.com/request"

    def __init__(self, apikey: str, email: str = None):
        super().__init__(apikey, email)
        if self.email is not None:
            self.__email_id = self.__get_md5_hash(email)
        self.headers = {
            "x-rapidapi-host": "privatix-temp-mail-v1.p.rapidapi.com",
            "x-rapidapi-key": self.apikey,
        }

    async def create_instance(self) -> "TempMailApi":
        """
        :return: TempMailApi object instance
        """
        domain = random.choice(self.domains)
        self.email = generate_username() + domain
        self.__email_id = self.__get_md5_hash(self.email)
        return self

    async def __create_request(self, path: str):
        url_path = self.__base_url + path
        response = await self.session.get(url_path, headers=self.headers)
        logging.info(f"{response = }")
        return response

    @staticmethod
    def __get_md5_hash(email: str) -> str:
        md5_hash = hashlib.md5()
        md5_hash.update(email.encode("utf-8"))
        return md5_hash.hexdigest()

    async def get_domains(self) -> httpx.Response:
        url = "/domains/"
        return await self.__create_request(url)

    async def get_messages(self) -> httpx.Response:
        url = f"/mail/id/{self.__email_id}/"
        return await self.__create_request(url)

    async def get_message_attachments(self) -> httpx.Response:  # testme
        url = f"/atchmnts/id/{self.__email_id}/"
        return await self.__create_request(url)

    async def get_one_attachment(self, bat_id: str) -> httpx.Response:  # testme
        url = f"/one_attachment/id/{self.__email_id}/{bat_id}/"
        return await self.__create_request(url)

    async def get_one_message(self) -> httpx.Response:  # testme
        email_id = self.__get_md5_hash(self.email)
        return await self.__create_request(f"/one_mail/id/{email_id}/")

    async def get_source_message(self) -> httpx.Response:  # testme
        self.__email_id = self.__get_md5_hash(self.email)
        return await self.__create_request(f"/source/id/{self.__email_id}/")

    async def get_delete_message(self) -> httpx.Response:  # testme
        return await self.__create_request(
            f"/delete/id/{self.__get_md5_hash(self.email)}/"
        )

    async def wait_for_html(self, attempts: int = 5, timer: int = 10) -> str | None:
        messages = []
        while not messages and attempts > 0:
            attempts -= 1
            try:
                get_messages_response = await self.get_messages()
                messages = get_messages_response.json()
                if "error" in messages:
                    messages = []
            except Exception as error:
                logging.error(error)
            if not messages:
                logging.info("sleeping for 1 secs")
                await asyncio.sleep(timer)
        if not messages:
            return None
        message = messages[0]
        html = message["mail_html"]
        return html


class OneSecMail(BasicInterface):
    """
    https://www.1secmail.com/api/
    """

    login: str | None = None
    domain: str | None = None

    __client = httpx.AsyncClient(timeout=120, verify=False)
    __api_url = "https://www.1secmail.com/api/v1/"

    def __init__(self, login: str | None = None, domain: str | None = None):
        self.login = login
        self.domain = domain
        self.email = f"{login}@{domain}"
        super().__init__("", self.email)

    def __repr__(self):
        return f"<OneSecMail {self.email = }>"

    @classmethod
    async def create_instance(cls, username: str | None = None) -> "OneSecMail":
        if not username:
            username = generate_username(10).lower()
        resp = await cls.gen_random_mailboxes(1)
        domain = resp.json()[0].split("@")[1]
        return cls(login=username, domain=domain)

    @classmethod
    async def __get_response(cls, params: dict) -> httpx.Response:
        return await cls.__client.get(f"{cls.__api_url}", params=params)

    @classmethod
    async def gen_random_mailboxes(cls, count: int) -> httpx.Response:
        """https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=10"""
        params = {"action": "genRandomMailbox", "count": count}
        return await cls.__get_response(params)

    @classmethod
    async def domains_list(cls) -> httpx.Response:
        """https://www.1secmail.com/api/v1/?action=getDomainList"""
        params = {"action": "getDomainList"}
        return await cls.__get_response(params)

    def __check_login_domain(self):
        if not self.login:
            raise errors.EmptyLoginError("Login can`t be empty!")
        if not self.domain:
            raise errors.EmptyDomainError("Domain can`t be empty!")

    async def get_messages(self) -> httpx.Response:
        """https://www.1secmail.com/api/v1/?action=getMessages&login=demo&domain=1secmail.com"""
        self.__check_login_domain()
        params = {"action": "getMessages", "login": self.login, "domain": self.domain}
        return await self.__get_response(params)

    async def read_message(self, message_id: str | int) -> httpx.Response:
        """https://www.1secmail.com/api/v1/?action=readMessage&login=demo&domain=1secmail.com&id=639"""
        self.__check_login_domain()
        if not message_id:
            raise errors.MessageEmptyError("message id can`t be empty")
        params = {
            "action": "readMessage",
            "login": self.login,
            "domain": self.domain,
            "id": message_id,
        }
        return await self.__get_response(params)

    async def download(self, file_name: str) -> httpx.Response:
        """https://www.1secmail.com/api/v1/?action=download&login=demo&domain=1secmail.com&id=639&file=iometer.pdf"""
        if not file_name:
            raise errors.FileNameEmptyError("file_name id can`t be empty")
        params = {
            "action": "download",
            "login": self.login,
            "domain": self.domain,
            "file": file_name,
        }
        return await self.__get_response(params)

    async def wait_for_html(self, attempts: int = 5, timer: int = 10) -> str | None:
        return None


class RegMailSpace(BasicInterface):
    async def wait_for_html(self, attempts: int = 5, timer: int = 10) -> str | None:
        messages = []
        while not messages and attempts > 0:
            attempts -= 1
            try:
                messages = await self.get_messages()
                assert "error" not in messages.text, (
                    '"error" in mail_interface.get_messages()'
                )
                messages = messages.json()["messages"]
            except Exception as error:
                logging.error(error)
                messages = None
            if not messages:
                await asyncio.sleep(timer)
        if not messages:
            return None
        message = messages[-1]
        body_html = message["body"]["html"]
        if "DOCTYPE" in body_html:
            return body_html
        body_html = base64.b64decode(body_html + "=").decode("utf-8")
        return body_html

    def __init__(self, api_key, email=None):
        super().__init__(api_key, email)
        self.__headers = {
            "x-rapidapi-host": "temp-mail117.p.rapidapi.com",
            "x-rapidapi-key": self.apikey,
        }

    def __repr__(self):
        return f"RegMailSpace(api_key={self.apikey}, email={self.email})"

    async def create_instance(self):
        email = await self.get_email()
        if email.get("message"):
            raise Exception("Monthly limit exceeded")
        self.email = email.get("email")

        return self

    async def get_messages(self, email=None) -> httpx.Response:
        if email is not None:
            self.email = email

        if not self.email:
            raise Exception("email cannot be None")
        params = {
            "email": self.email,
        }
        response = await self.session.get(
            "https://temp-mail117.p.rapidapi.com/getmail.php",
            headers=self.__headers,
            params=params,
        )
        return response

    async def get_email(self) -> dict:
        response = await self.session.get(
            "https://temp-mail117.p.rapidapi.com/getaddress.php", headers=self.__headers
        )
        return response.json()


class RapidApi44(BasicInterface):
    email: str | None = None

    def __init__(self, api_key, email=None):
        super().__init__(api_key, email)
        self.__headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "temp-mail44.p.rapidapi.com",
            "Content-Type": "application/json",
        }

    async def create_instance(self) -> Self:
        resp = await self.create_email()
        email = resp.json()["email"]
        self.email = email
        return self

    async def create_email(self):
        url = "https://temp-mail44.p.rapidapi.com/api/v3/email/new"
        response = await self.session.post(url, headers=self.__headers)
        return response

    async def get_messages(self, email=None) -> httpx.Response:
        if email is not None:
            self.email = email
        url = f"https://temp-mail44.p.rapidapi.com/api/v3/email/{self.email}/messages"
        response = await self.session.get(url, headers=self.__headers)
        return response

    async def wait_for_html(self, attempts: int = 5, timer: int = 10) -> str | None:
        email_messages = []
        while not email_messages and attempts > 0:
            attempts -= 1
            try:
                email_messages = await self.get_messages()
                email_messages = email_messages.json()
                assert "error" not in email_messages, "Error in fake_mail.get_messages"
            except Exception as error:
                logging.error(error)
                email_messages = None
            if not email_messages:
                await asyncio.sleep(timer)
        if not email_messages:
            return None
        email_message = email_messages[0]
        body_html = email_message["body_html"]
        return body_html


class NiceMailApi(InterfaceMethods, InterfaceSession):
    domains = [
        "oeralb.com",
        "sisood.com",
        "disefl.com",
        "suarj.com",
        "mfxis.com",
        "anogz.com",
    ]
    token: str
    token_pattern = re.compile('(?<=")eyJhbGciOiJIUzI1NiJ9\..+(?="]</script>)')

    def __serialize_bearer_token(self, resp: httpx.Response) -> str:
        return self.token_pattern.search(resp.text).group(0)

    async def get_bearer_token(self) -> httpx.Response:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML"
            ", like Gecko) Chrome/138.0.0.0 Safari/537.36",
        }

        resp = await self.session.get("https://mailporary.com/en", headers=headers)

        return resp

    async def get_emails(self) -> httpx.Response:
        headers = {
            "Authorization": f"Bearer {self.token}",
        }
        headers['x-request-id'] = ''.join([random.choice(string.digits + string.ascii_lowercase) for _ in range(32)])
        headers['x-timestamp'] = str(round(datetime.datetime.now().timestamp()))
        resp = await self.session.get(f"https://web.mailporary.com/api/v1/mailbox/{self.email}", headers=headers)
        return resp

    async def get_message(self, message_id: str) -> httpx.Response:
        """
        https://web.mailporary.com/api/v1/mailbox/bvb2kakh%40sisood.com/20260106T235659-2047
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
        }
        headers['x-request-id'] = ''.join([random.choice(string.digits + string.ascii_lowercase) for _ in range(32)])
        headers['x-timestamp'] = str(round(datetime.datetime.now().timestamp()))
        resp = await self.session.get(f"https://web.mailporary.com/api/v1/mailbox/{self.email}/{message_id}", headers=headers)
        return resp


    async def wait_for_html(self, attempts: int = 5, timer: float = 10) -> str | None:
        """
        https://web.mailporary.com/api/v1/mailbox/rouwod33pg%40disefl.com
        """
        if not self.email:
            raise Exception("email cannot be None")
        email_messages = []
        while not email_messages and attempts > 0:
            attempts -= 1
            resp = await self.get_emails()
            email_messages = resp.json()
            if "error" in email_messages:
                email_messages = []
            if not email_messages:
                await asyncio.sleep(timer)
        if not email_messages:
            return None
        last_letter = await self.get_message(message_id=email_messages[0]['id'])
        last_letter = last_letter.json()
        html = last_letter['body']['html']
        return html


    async def create_instance(self) -> Self:
        if not self.email:
            domain = random.choice(self.domains)
            self.email = f'{generate_username()}@{domain}'
        self.token = self.__serialize_bearer_token(await self.get_bearer_token())
        return self

    def __init__(self, email=None):
        self.email = email
