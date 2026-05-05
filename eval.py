import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from ingestion import process_pdf
from knowledge_base import get_knowledge_base
from analyzer import call_groq_llm, MODEL_NAME
import json

from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings

from dotenv import load_dotenv
load_dotenv()

def run_eval(pdf_path: str):
    """
    Runs a test contract through the pipeline and evaluates using RAGAS.
    Requires GROQ_API_KEY.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return
        
    print(f"--- Starting Evaluation on {pdf_path} ---")
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    clauses = process_pdf(pdf_bytes)
    print(f"Extracted {len(clauses)} clauses.")
    
    kb = get_knowledge_base()
    
    groq_llm = ChatGroq(model_name=MODEL_NAME, temperature=0)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    questions = []
    answers = []
    contexts = []
    
    print("Running analysis pipeline...")
    for i, clause in enumerate(clauses):
        fair_clause, metadata = kb.query_fair_clause(clause)
        if not fair_clause:
            fair_clause = "Standard reasonable commercial terms apply."
            
        clause_type = metadata["type"] if metadata else "general"
        
        prompt = f"""
        You are a legal contract analyst.
        UPLOADED CLAUSE: {clause}
        STANDARD FAIR CLAUSE: {fair_clause}
        Identify differences and assign a Risk Score (1-10). Provide recommendation.
        Respond in JSON with keys: type, differences, risk_score, risky_quote, recommendation.
        """
        
        response_text = call_groq_llm(prompt)
        
        try:
            result = json.loads(response_text)
            ans = result.get("recommendation", "")
        except:
            ans = "Failed to parse analysis."
            
        questions.append(f"What are the risks and recommendations for this {clause_type} clause?")
        answers.append(ans)
        contexts.append([clause, fair_clause])
        print(f"Processed clause {i+1}/{len(clauses)}")

    print("Pipeline complete. Running RAGAS evaluation...")
    
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts
    }
    dataset = Dataset.from_dict(data)
    
    result = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy
        ],
        llm=groq_llm,
        embeddings=embeddings
    )
    
    print("\\n--- Evaluation Results ---")
    print(result)
    
if __name__ == "__main__":
    test_pdf = "sample_contract.pdf"
    run_eval(test_pdf)
