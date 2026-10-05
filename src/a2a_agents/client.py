import asyncio
import sys

import httpx
from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import new_text_message
from a2a.types import Role, SendMessageRequest

URL = "http://127.0.0.1:9101"


async def main(text: str):
    async with httpx.AsyncClient() as http:
        card = await A2ACardResolver(httpx_client=http, base_url=URL).get_agent_card()
    print("Agent:", card.name)
    client = await create_client(agent=card, client_config=ClientConfig(streaming=False))
    request = SendMessageRequest(message=new_text_message(text, role=Role.ROLE_USER))
    async for chunk in client.send_message(request):
        print(chunk)


asyncio.run(main(" ".join(sys.argv[1:]) or "my elbow is itchy, dry and red"))
