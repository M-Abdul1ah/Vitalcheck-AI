"""
Core symptom-checking chain with RAG.
Flow: symptoms -> retrieve chunks (ChromaDB) -> prompt + context -> LLM -> text.
LLM is chosen in .env with LLM_PROVIDER=gemini or groq.
"""
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from src.prompts.prompts import symptom_prompt
from src.retriever import retrieve

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))


def _get_llm():
    if PROVIDER == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=TEMPERATURE,
        )
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        google_api_key=os.getenv("GEMINI_API_KEY"),
        model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        temperature=TEMPERATURE,
    )


llm = _get_llm()

# LCEL pipe: prompt -> llm -> plain string output
symptom_chain = symptom_prompt | llm | StrOutputParser()


def _build_inputs(symptoms: str) -> dict:
    """Fetch the closest knowledge chunks and pass them in as context."""
    context = "\n\n".join(retrieve(symptoms))
    return {"symptoms": symptoms, "context": context}


def check_symptoms(symptoms: str) -> str:
    """Non-streaming call, good for testing or backend logging."""
    return symptom_chain.invoke(_build_inputs(symptoms))


def check_symptoms_stream(symptoms: str):
    """Streaming generator, use this in Streamlit with st.write_stream()."""
    for chunk in symptom_chain.stream(_build_inputs(symptoms)):
        yield chunk