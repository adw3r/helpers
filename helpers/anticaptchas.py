import asyncio
import logging

import httpx

from . import errors

logger = logging.getLogger('src.api_interfaces')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class AntiCaptchaAPI:
    API_KEY = None

    __headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    __user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    _client = httpx.AsyncClient(timeout=httpx.Timeout(10))

    def __init__(self, api_key: str):
        self.API_KEY = api_key
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(10))

    @staticmethod
    def check_solved(response):
        if 'Are you a human?' in response.text:
            raise errors.AreYouHumanError('Are you a human?')

    async def get_balance(self) -> httpx.Response:
        json_data = {
            'clientKey': self.API_KEY,
        }

        response = httpx.post('https://api.anti-captcha.com/getBalance', headers=self.__headers, json=json_data)
        logger.debug(f'balance response: {response}')
        return response

    async def create_task(self, url: str, sitekey: str) -> httpx.Response:
        json_data = {
            'clientKey': self.API_KEY,
            'task': {
                'type': 'RecaptchaV2TaskProxyless',
                'websiteURL': url,
                'websiteKey': sitekey,
                'userAgent': self.__user_agent,
            },
            'softId': 0,
        }

        response = await self._client.post('https://api.anti-captcha.com/createTask', headers=self.__headers,
                                           json=json_data)
        return response

    async def get_task_result(self, task_id: str | int) -> httpx.Response:
        json_data = {
            'clientKey': self.API_KEY,
            'taskId': task_id,
        }

        response = await self._client.post('https://api.anti-captcha.com/getTaskResult', headers=self.__headers,
                                           json=json_data)
        return response

    async def get_solution(self, url: str, sitekey: str, attempts_count=10) -> str | None:
        response = await self.create_task(url, sitekey)
        response.raise_for_status()
        task_id = response.json().get('taskId')
        logger.debug(f'task_id: {task_id}')
        if task_id is None:
            raise errors.TaskIdIsEmptyError('No task id')
        logger.debug(response.text)

        attempts_count = attempts_count * 2
        solution: str | None = None
        while solution is None and attempts_count > 0:
            attempts_count -= 1
            try:
                task_result: httpx.Response = await self.get_task_result(task_id=task_id)
                logger.debug(f'task_result: {task_result.text}')
                task_result.raise_for_status()
                solution_dict = task_result.json().get('solution')
                if solution_dict is None:
                    continue
                solution = solution_dict.get('gRecaptchaResponse')
            except Exception as error:
                logger.error(error)
                await asyncio.sleep(0.5)
        return solution

    @classmethod
    async def check_balance(cls, response):
        balance_amount = response.json().get('balance', 0)
        logger.debug(f'anticaptcha balance : {balance_amount=}')
        if balance_amount <= 0:
            raise errors.AntiCaptchaLowBalanceError(f'{type(cls).__name__} Balance too low')
