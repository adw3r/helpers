import httpx
import selectolax


class GenerateFakeNames:
    __client = httpx.AsyncClient(verify=False)

    @classmethod
    async def get_full_name(cls) -> str:
        response: httpx.Response = await cls.__client.get("https://generatefakename.com/ru/name/random/en/ng")
        response.raise_for_status()
        html_parser = selectolax.lexbor.LexborHTMLParser(response.text)
        serialized_response: str = html_parser.css_first("div.panel-body > h3").text()
        return serialized_response
