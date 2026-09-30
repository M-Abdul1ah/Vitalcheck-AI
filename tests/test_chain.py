"""
Run this from the project root to sanity-check the chain BEFORE
touching the Streamlit UI:

    python test_chain.py
"""
from src.chains.symptom_chain import check_symptoms

if __name__ == "__main__":
    sample = "I have a headache and mild fever since yesterday"
    print("Testing with:", sample, "\n")
    result = check_symptoms(sample)
    print(result)
