import httpx


class SmsHub:
    api_key = ''  # 0.1911
    __url = 'https://smshub.org/stubs/handler_api.php'
    __session = httpx.AsyncClient()

    def __init__(self, apikey: str = ''):
        self.api_key = apikey

    async def __get_response(self, params):
        api_key_params = {
            'api_key': self.api_key,
        }
        api_key_params.update(params)
        response = await self.__session.get(self.__url, params=api_key_params)
        return response

    async def get_balance(self, currency='840'):
        """
        https://smshub.org/stubs/handler_api.php
        ?api_key=APIKEY&action=getBalance&currency=CURRENCY
        :return:
        """
        params = {
            'action': 'getBalance',
            'api_key': self.api_key,
            'currency': currency
        }
        response = await self.__get_response(params)
        return response

    async def get_number(self, service, maxprice: str | None = None, country: str | None = None,
                         operator: str | None = None, currency='840'):
        """
        https://smshub.org/stubs/handler_api.php
        ?api_key=APIKEY&action=getNumber
        &service=SERVICE&operator=OPERATOR&country=COUNTRY&maxPrice=MAXPRICE&currency=CURRENCY
        :param service:
        :param maxprice:
        :param country:
        :param operator:
        :return:
        """
        params = {
            'action': 'getNumber',
            'service': service,
            'operator': operator,
            'country': country,
            'maxPrice': maxprice,
            'currency': currency
        }
        response = await self.__get_response(params)
        return response

    async def set_status(self, status: str, _id: str | int):
        """https://smshub.org/stubs/handler_api.php
        ?api_key=APIKEY&action=setStatus
        &status=STATUS&id=ID"""
        params = {
            'action': 'setStatus',
            'status': status,
            'id': _id
        }
        response = await self.__get_response(params)
        return response

    async def get_status(self, _id: str | int):
        """https://smshub.org/stubs/handler_api.php
        ?api_key=APIKEY&action=getStatus&id=ID"""
        params = {
            'action': 'getStatus',
            'id': _id
        }
        response = await self.__get_response(params)
        return response

    async def get_prices(self, service=None, country=None, currency: str = '840'):
        """https://smshub.org/stubs/handler_api.php
        ?api_key=APIKEY&action=getPrices
        &service=SERVICE&country=COUNTRY&currency=CURRENCY"""
        params = {
            'action': 'getStatus',
            'service': service,
            'country': country,
            'currency': currency
        }
        response = await self.__get_response(params)
        return response

    async def update_api_currency(self, currency):
        """
        https://smshub.org/stubs/handler_api.php
        ?api_key=APIKEY&action=updateApiCurrency&&currency=CURRENCY
        :return:
        """
        params = {
            'action': 'updateApiCurrency',
            'currency': currency
        }
        response = await self.__get_response(params)
        return response
