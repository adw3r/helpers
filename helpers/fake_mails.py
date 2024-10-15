import hashlib
import random
import string

import httpx

from . import errors


def generate_username(length: int = 8) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


class TempMailApi:
    def __str__(self):
        return self.email

    def __repr__(self):
        return f'<TempMailApi {self.email=}>'

    APIKEY = ''  # works
    domains = (
        '@cevipsa.com', '@cpav3.com', '@nuclene.com', '@steveix.com',
        '@mocvn.com', '@tenvil.com', '@tgvis.com', '@amozix.com', '@anypsd.com', '@maxric.com'
    )
    """
    https://rapidapi.com/Privatix/api/temp-mail
    """

    headers = {'x-rapidapi-host': 'privatix-temp-mail-v1.p.rapidapi.com', 'x-rapidapi-key': APIKEY}
    __base_url = 'https://privatix-temp-mail-v1.p.rapidapi.com/request'
    __client = httpx.AsyncClient(verify=False)
    email: str = None

    def __init__(self, email: str):
        self.email = email
        self.__email_id = self.__get_md5_hash(email)

    @classmethod
    async def create_email_instance(cls) -> 'TempMailApi':
        """
        :return: TempMailApi object instance
        """
        # domains = await cls.get_domains()
        # domain = random.choice(domains.json())
        if cls.email is None:
            domain = random.choice(cls.domains)
            return cls(email=generate_username() + domain)
        else:
            raise errors.CantUseThisMethod('Can`t create an email instance with already existing email')

    @classmethod
    async def __create_request(cls, path: str):
        response = await cls.__client.get(cls.__base_url + path, headers=cls.headers)
        return response

    @staticmethod
    def __get_md5_hash(email: str) -> str:
        md5_hash = hashlib.md5()
        md5_hash.update(email.encode('utf-8'))
        md5_result = md5_hash.hexdigest()
        return md5_result

    @classmethod
    async def get_domains(cls) -> httpx.Response:
        url = '/domains/'
        response = await cls.__create_request(url)
        return response

    async def get_messages(self) -> httpx.Response:
        url = f'/mail/id/{self.__email_id}/'
        response = await self.__create_request(url)
        return response

    async def get_message_attachments(self) -> httpx.Response:  # testme
        url = f'/atchmnts/id/{self.__email_id}/'
        response = await self.__create_request(url)
        return response

    async def get_one_attachment(self, bat_id: str) -> httpx.Response:  # testme
        url = f'/one_attachment/id/{self.__email_id}/{bat_id}/'
        response = await self.__create_request(url)
        return response

    async def get_one_message(self) -> httpx.Response:  # testme
        email_id = self.__get_md5_hash(self.email)
        response = await self.__create_request(f'/one_mail/id/{email_id}/')
        return response

    async def get_source_message(self) -> httpx.Response:  # testme
        self.__email_id = self.__get_md5_hash(self.email)
        response = await self.__create_request(f'/source/id/{self.__email_id}/')
        return response

    async def get_delete_message(self) -> httpx.Response:  # testme
        response = await self.__create_request(f'/delete/id/{self.__get_md5_hash(self.email)}/')
        return response


class OneSecMail:
    """
    https://www.1secmail.com/api/
    """
    __client = httpx.AsyncClient()
    __api_url = 'https://www.1secmail.com/api/v1/'
    login: str | None = None
    domain: str | None = None

    def __init__(self, login: str | None = None, domain: str | None = None):
        self.login = login
        self.domain = domain
        self.email = f'{login}@{domain}'

    @classmethod
    async def __get_response(cls, params: dict):
        response = await cls.__client.get(f'{cls.__api_url}', params=params)
        return response

    @classmethod
    async def gen_random_mailboxes(cls, count: int):
        'https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=10'
        params = {
            'action': 'genRandomMailbox',
            'count': count
        }
        response = await cls.__get_response(params)
        return response

    @classmethod
    async def domains_list(cls):
        'https://www.1secmail.com/api/v1/?action=getDomainList'
        params = {
            'action': 'getDomainList'
        }
        response = await cls.__get_response(params)
        return response

    def __check_login_domain(self):
        if not self.login:
            raise errors.EmptyLoginError('Login can`t be empty!')
        if not self.domain:
            raise errors.EmptyDomainError('Domain can`t be empty!')

    async def get_messages(self):
        'https://www.1secmail.com/api/v1/?action=getMessages&login=demo&domain=1secmail.com'
        self.__check_login_domain()
        params = {
            'action': 'getMessages',
            'login': self.login,
            'domain': self.domain
        }
        response = await self.__get_response(params)
        return response

    async def read_message(self, message_id: str | int):
        'https://www.1secmail.com/api/v1/?action=readMessage&login=demo&domain=1secmail.com&id=639'
        self.__check_login_domain()
        if not message_id:
            raise errors.MessageEmptyError('message id can`t be empty')
        params = {
            'action': 'readMessage',
            'login': self.login,
            'domain': self.domain,
            'id': message_id
        }
        response = await self.__get_response(params)
        return response

    async def download(self, file_name: str):
        'https://www.1secmail.com/api/v1/?action=download&login=demo&domain=1secmail.com&id=639&file=iometer.pdf'
        if not file_name:
            raise errors.FileNameEmptyError('file_name id can`t be empty')
        params = {
            'action': 'download',
            'login': self.login,
            'domain': self.domain,
            'file': file_name
        }
        response = await self.__get_response(params)
        return response
