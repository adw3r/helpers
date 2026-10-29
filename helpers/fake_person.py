import httpx
import selectolax


class GenerateFakeNames:
    @classmethod
    async def get_full_name(cls) -> str:
        async with httpx.AsyncClient(verify=False) as client:
            response: httpx.Response = await client.get("https://generatefakename.com/ru/name/random/en/ng")
        response.raise_for_status()
        html_parser = selectolax.lexbor.LexborHTMLParser(response.text)
        serialized_response: str = html_parser.css_first("div.panel-body > h3").text()
        return serialized_response
