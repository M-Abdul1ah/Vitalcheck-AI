"""
Core symptom-checking chain.
Groq (fast LLM inference) + LangChain (prompt/output plumbing).
This is the heart of VitalCheck AI — everything else (Streamlit UI,
RAG, history) wraps around this chain.
"""
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from src.config import GROQ_API_KEY, GROQ_MODEL, TEMPERATURE
from src.prompts.prompts import symptom_prompt

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    temperature=TEMPERATURE,
)

# LCEL pipe: prompt -> llm -> plain string output
symptom_chain = symptom_prompt | llm | StrOutputParser()


def check_symptoms(symptoms: str) -> str:
    """Non-streaming call — good for testing or backend logging."""
    return symptom_chain.invoke({"symptoms": symptoms})


def check_symptoms_stream(symptoms: str):
    """Streaming generator — use this in Streamlit with st.write_stream()."""
    for chunk in symptom_chain.stream({"symptoms": symptoms}):
        yield chunk
