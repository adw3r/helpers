import asyncio
import logging

import httpx

from . import config, errors

logger = logging.getLogger('src.api_interfaces')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class AntiCaptchaAPI:
    API_KEY = config.ANTICAPTCHA_APIKEY

    __headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    __user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'
    _client = httpx.AsyncClient(timeout=httpx.Timeout(10))

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(10))

    @staticmethod
    def check_solved(response):
        if 'Are you a human?' in response.text:
            raise errors.AreYouHumanError('Are you a human?')

    @classmethod
    async def get_balance(cls) -> httpx.Response:
        json_data = {
            'clientKey': cls.API_KEY,
        }

        response = httpx.post('https://api.anti-captcha.com/getBalance', headers=cls.__headers, json=json_data)
        logger.debug(f'balance response: {response}')
        return response

    @classmethod
    async def create_task(cls, url: str, sitekey: str) -> httpx.Response:
        json_data = {
            'clientKey': cls.API_KEY,
            'task': {
                'type': 'RecaptchaV2TaskProxyless',
                'websiteURL': url,
                'websiteKey': sitekey,
                'userAgent': cls.__user_agent,
            },
            'softId': 0,
        }

        response = await cls._client.post('https://api.anti-captcha.com/createTask', headers=cls.__headers,
                                          json=json_data)
        return response

    @classmethod
    async def get_task_result(cls, task_id: str | int) -> httpx.Response:
        json_data = {
            'clientKey': cls.API_KEY,
            'taskId': task_id,
        }

        response = await cls._client.post('https://api.anti-captcha.com/getTaskResult', headers=cls.__headers,
                                          json=json_data)
        return response

    @classmethod
    async def get_solution(cls, url: str, sitekey: str, attempts_count=10) -> str | None:
        response = await cls.create_task(url, sitekey)
        response.raise_for_status()
        task_id = response.json().get('taskId')
        logger.debug(f'task_id: {task_id}')
        if task_id is None:
            raise errors.TaskIdIsEmptyError('No task id')
        logger.debug(response.text)

        attempts_count = 10
        solution: str | None = None
        while solution is None and attempts_count > 0:
            attempts_count -= 1
            try:
                task_result: httpx.Response = await cls.get_task_result(task_id=task_id)
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
