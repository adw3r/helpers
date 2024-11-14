import asyncio
import logging

import httpx

from . import errors

logger = logging.getLogger("src.api_interfaces")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


class AntiCaptchaAPI:
    API_KEY = None
    url_to_api = "https://api.anti-captcha.com"

    __headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    __user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    _client = httpx.AsyncClient(timeout=httpx.Timeout(10))

    def __init__(self, api_key: str):
        self.API_KEY = api_key
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(10))

    @staticmethod
    def check_solved(response):
        if "Are you a human?" in response.text:
            raise errors.AreYouHumanError("Are you a human?")

    async def get_balance(self) -> httpx.Response:
        json_data = {
            "clientKey": self.API_KEY,
        }

        response = httpx.post(f"{self.url_to_api}/getBalance", headers=self.__headers, json=json_data)
        logger.debug(f"balance response: {response}")
        return response

    async def create_task(self, task_block) -> httpx.Response:
        json_data = {
            "clientKey": self.API_KEY,
            "task": task_block,
            "softId": 0,
        }

        return await self._client.post(f"{self.url_to_api}/createTask", headers=self.__headers, json=json_data)

    async def get_task_result(self, task_id: str | int) -> httpx.Response:
        json_data = {
            "clientKey": self.API_KEY,
            "taskId": task_id,
        }

        return await self._client.post(f"{self.url_to_api}/getTaskResult", headers=self.__headers, json=json_data)

    async def get_solution(
        self,
        url: str,
        sitekey: str,
        attempts_count=10,
        task_type="RecaptchaV2TaskProxyless",
        min_score="0.9",
        action: str = "submit",
        is_invisible=False,
        cookie=None,
        user_agent=None,
    ) -> str | None:
        match task_type:
            # case 'RecaptchaV2Task':
            #     task_block = {
            #         "type": "RecaptchaV2Task",
            #         "websiteURL": url,
            #         "websiteKey": sitekey,
            #         "proxyType": "http",
            #         "proxyAddress": "8.8.8.8",
            #         "proxyPort": 8080,
            #         "proxyLogin": "proxyLoginHere",
            #         "proxyPassword": "proxyPasswordHere",
            #         "userAgent": "MODERN_USER_AGENT_HERE",
            #         "cookie": cookie
            #     }
            case "RecaptchaV2TaskProxyless":
                task_block = {
                    "type": task_type,
                    "websiteURL": url,
                    "websiteKey": sitekey,
                    # 'userAgent': self.__user_agent,
                    "isInvisible": is_invisible,
                    "userAgent": user_agent,
                    "cookie": cookie,
                }
            case "RecaptchaV3TaskProxyless":
                task_block = {
                    "type": "RecaptchaV3TaskProxyless",
                    "websiteURL": url,
                    "websiteKey": sitekey,
                    "minScore": min_score,
                    "pageAction": action,
                    "isEnterprise": False,
                }

        response = await self.create_task(task_block)
        response.raise_for_status()
        task_id = response.json().get("taskId")
        logger.debug(f"task_id: {task_id}")
        if task_id is None:
            raise errors.TaskIdIsEmptyError("No task id")
        logger.debug(response.text)

        attempts_count = attempts_count * 2
        solution: str | None = None
        while solution is None and attempts_count > 0:
            attempts_count -= 1
            try:
                task_result: httpx.Response = await self.get_task_result(task_id=task_id)
                logger.debug(f"task_result: {task_result.text}")
                task_result.raise_for_status()
                solution_dict = task_result.json().get("solution")
                if solution_dict is None:
                    continue
                solution = solution_dict.get("gRecaptchaResponse")
            except Exception as error:
                logger.error(error)
                await asyncio.sleep(0.5)
        return solution

    @classmethod
    async def check_balance(cls, response):
        balance_amount = response.json().get("balance", 0)
        logger.debug(f"anticaptcha balance : {balance_amount=}")
        if balance_amount <= 0:
            raise errors.AntiCaptchaLowBalanceError(f"{type(cls).__name__} Balance too low")


class TwoCaptchaApi:
    API_KEY = None

    __headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    __user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    _client = httpx.AsyncClient(timeout=httpx.Timeout(10))

    def __init__(self, api_key: str):
        self.API_KEY = api_key
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(10))

    @staticmethod
    def check_solved(response):
        if "Are you a human?" in response.text:
            raise errors.AreYouHumanError("Are you a human?")

    async def get_balance(self) -> httpx.Response:
        json_data = {
            "clientKey": self.API_KEY,
        }

        response = httpx.post("https://api.2captcha.com/getBalance", headers=self.__headers, json=json_data)
        logger.debug(f"balance response: {response}")
        return response

    async def create_task(self, task_block) -> httpx.Response:
        json_data = {
            "clientKey": self.API_KEY,
            "task": task_block,
            "softId": 0,
        }

        return await self._client.post("https://api.2captcha.com/createTask", headers=self.__headers, json=json_data)

    async def get_task_result(self, task_id: str | int) -> httpx.Response:
        json_data = {
            "clientKey": self.API_KEY,
            "taskId": task_id,
        }

        return await self._client.post("https://api.2captcha.com/getTaskResult", headers=self.__headers, json=json_data)

    async def get_solution(
        self,
        url: str,
        sitekey: str,
        attempts_count=10,
        task_type="RecaptchaV2TaskProxyless",
        min_score="0.9",
        action: str = "submit",
        is_invisible=False,
        cookie=None,
        user_agent=None,
    ) -> str | None:
        match task_type:
            # case 'RecaptchaV2Task':
            #     task_block = {
            #         "type": "RecaptchaV2Task",
            #         "websiteURL": url,
            #         "websiteKey": sitekey,
            #         "proxyType": "http",
            #         "proxyAddress": "8.8.8.8",
            #         "proxyPort": 8080,
            #         "proxyLogin": "proxyLoginHere",
            #         "proxyPassword": "proxyPasswordHere",
            #         "userAgent": "MODERN_USER_AGENT_HERE",
            #         "cookie": cookie
            #     }
            case "RecaptchaV2TaskProxyless":
                task_block = {
                    "type": task_type,
                    "websiteURL": url,
                    "websiteKey": sitekey,
                    # 'userAgent': self.__user_agent,
                    "isInvisible": is_invisible,
                    "userAgent": user_agent,
                    "cookie": cookie,
                }
            case "RecaptchaV3TaskProxyless":
                task_block = {
                    "type": "RecaptchaV3TaskProxyless",
                    "websiteURL": url,
                    "websiteKey": sitekey,
                    "minScore": min_score,
                    "pageAction": action,
                    "isEnterprise": False,
                }

        response = await self.create_task(task_block)
        response.raise_for_status()
        task_id = response.json().get("taskId")
        logger.debug(f"task_id: {task_id}")
        if task_id is None:
            raise errors.TaskIdIsEmptyError("No task id")
        logger.debug(response.text)

        attempts_count = attempts_count * 2
        solution: str | None = None
        while solution is None and attempts_count > 0:
            attempts_count -= 1
            try:
                task_result: httpx.Response = await self.get_task_result(task_id=task_id)
                logger.debug(f"task_result: {task_result.text}")
                task_result.raise_for_status()
                solution_dict = task_result.json().get("solution")
                solution = solution_dict.get("gRecaptchaResponse")
            except AttributeError as error:
                logger.error(error)
                await asyncio.sleep(0.5)
            except Exception as error:
                logger.exception(error)
                await asyncio.sleep(0.5)
        return solution

    @classmethod
    async def check_balance(cls, response):
        balance_amount = response.json().get("balance", 0)
        logger.debug(f"anticaptcha balance : {balance_amount=}")
        if balance_amount <= 0:
            raise errors.AntiCaptchaLowBalanceError(f"{type(cls).__name__} Balance too low")


class TwoCaptchaExtended(AntiCaptchaAPI):
    url_to_api = "https://api.2captcha.com"
