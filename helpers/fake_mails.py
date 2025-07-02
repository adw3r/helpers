import hashlib
import logging
import random
import string

import httpx

from . import errors


def generate_username(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class TempMailApi:
    def __str__(self):
        return self.email

    def __repr__(self):
        return f"<TempMailApi {self.email=}>"

    APIKEY = None  # works
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
    __client = httpx.AsyncClient(verify=False)
    email: str = None

    def __get_headers(self):
        return {"x-rapidapi-host": "privatix-temp-mail-v1.p.rapidapi.com", "x-rapidapi-key": self.APIKEY}

    def __init__(self, apikey: str, email: str = None):
        self.APIKEY = apikey
        self.email = email
        if self.email is not None:
            self.__email_id = self.__get_md5_hash(email)

    def create_email_instance(self) -> "TempMailApi":
        """
        :return: TempMailApi object instance
        """
        if self.email is None:
            domain = random.choice(self.domains)
            self.email = generate_username() + domain
            self.__email_id = self.__get_md5_hash(self.email)
            return self
        raise errors.CantUseThisMethod("Can`t create an email instance with already existing email")

    async def __create_request(self, path: str):
        headers = self.__get_headers()
        url_path = self.__base_url + path
        response = await self.__client.get(url_path, headers=headers)
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
        return await self.__create_request(f"/delete/id/{self.__get_md5_hash(self.email)}/")


class OneSecMail:
    """
    https://www.1secmail.com/api/
    """

    email: str = None
    login: str | None = None
    domain: str | None = None

    __client = httpx.AsyncClient(timeout=120, verify=False)
    __api_url = "https://www.1secmail.com/api/v1/"

    def __init__(self, login: str | None = None, domain: str | None = None):
        self.login = login
        self.domain = domain
        self.email = f"{login}@{domain}"

    def __repr__(self):
        return f"<OneSecMail {self.email = }>"

    @classmethod
    async def create_email_instance(cls, username: str | None = None) -> "OneSecMail":
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
        "https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=10"
        params = {"action": "genRandomMailbox", "count": count}
        return await cls.__get_response(params)

    @classmethod
    async def domains_list(cls) -> httpx.Response:
        "https://www.1secmail.com/api/v1/?action=getDomainList"
        params = {"action": "getDomainList"}
        return await cls.__get_response(params)

    def __check_login_domain(self):
        if not self.login:
            raise errors.EmptyLoginError("Login can`t be empty!")
        if not self.domain:
            raise errors.EmptyDomainError("Domain can`t be empty!")

    async def get_messages(self) -> httpx.Response:
        "https://www.1secmail.com/api/v1/?action=getMessages&login=demo&domain=1secmail.com"
        self.__check_login_domain()
        params = {"action": "getMessages", "login": self.login, "domain": self.domain}
        return await self.__get_response(params)

    async def read_message(self, message_id: str | int) -> httpx.Response:
        "https://www.1secmail.com/api/v1/?action=readMessage&login=demo&domain=1secmail.com&id=639"
        self.__check_login_domain()
        if not message_id:
            raise errors.MessageEmptyError("message id can`t be empty")
        params = {"action": "readMessage", "login": self.login, "domain": self.domain, "id": message_id}
        return await self.__get_response(params)

    async def download(self, file_name: str) -> httpx.Response:
        "https://www.1secmail.com/api/v1/?action=download&login=demo&domain=1secmail.com&id=639&file=iometer.pdf"
        if not file_name:
            raise errors.FileNameEmptyError("file_name id can`t be empty")
        params = {"action": "download", "login": self.login, "domain": self.domain, "file": file_name}
        return await self.__get_response(params)


class RegMailSpace:
    __client = httpx.AsyncClient()

    def __init__(self, api_key, email=None):
        self.__api_key = api_key
        self.email = email
        self.__headers = {
            "x-rapidapi-host": "temp-mail117.p.rapidapi.com",
            "x-rapidapi-key": self.__api_key,
        }

    def __repr__(self):
        return f"RegMailSpace(api_key={self.__api_key}, email={self.email})"

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
        response = await self.__client.get(
            "https://temp-mail117.p.rapidapi.com/getmail.php",
            headers=self.__headers,
            params=params,
        )
        return response

    async def get_email(self) -> dict:
        response = await self.__client.get(
            "https://temp-mail117.p.rapidapi.com/getaddress.php", headers=self.__headers
        )
        return response.json()
