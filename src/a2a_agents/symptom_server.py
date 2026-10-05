"""Symptom agent exposed over A2A (port 9101)."""
import asyncio

import uvicorn
from starlette.applications import Starlette

from a2a.helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill

from src.chains.symptom_chain import check_symptoms

PORT = 9101


class SymptomExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        text = context.get_user_input()
        answer = await asyncio.to_thread(check_symptoms, text)
        await event_queue.enqueue_event(new_text_message(answer))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("cancel not supported")


skill = AgentSkill(
    id="symptom_check",
    name="Skin symptom check",
    description="General guidance for skin symptoms (Urdu/English). Not a diagnosis.",
    tags=["dermatology", "symptoms"],
    examples=["my elbow is itchy and red"],
)

card = AgentCard(
    name="Vital Check Symptom Agent",
    description="RAG-based skin symptom guidance. Not a doctor.",
    version="0.1.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(streaming=False),
    supported_interfaces=[
        AgentInterface(
            protocol_binding="JSONRPC",
            url=f"http://127.0.0.1:{PORT}",
            protocol_version="1.0",
        )
    ],
    skills=[skill],
)

handler = DefaultRequestHandler(
    agent_executor=SymptomExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=card,
)

routes = []
routes.extend(create_agent_card_routes(card))
routes.extend(create_jsonrpc_routes(handler, "/"))
app = Starlette(routes=routes)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
