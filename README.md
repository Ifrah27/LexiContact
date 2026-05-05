# ⚖️ LexiContract — AI Legal Contract Analyzer

LexiContract is a high-performance AI tool designed to analyze legal contracts (NDA, Employment, SaaS ToS) and identify risky clauses using RAG (Retrieval-Augmented Generation) and Large Language Models.

## 🚀 Features

- **PDF Ingestion**: Parses PDFs into structured Markdown using PyMuPDF.
- **Semantic Chunking**: Intelligently splits documents into logical legal clauses.
- **Risk Heatmap**: Visual dashboard with High/Medium/Low risk scoring.
- **Knowledge Base**: Uses ChromaDB to store and compare clauses against industry-standard "fair" terms.
- **Hallucination Guard**: Cross-verifies LLM quotes against the original text to ensure 100% accuracy.
- **Modern UI**: Built with Streamlit for a clean, professional native experience.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: Groq (Llama 3.3 70B)
- **Vector DB**: ChromaDB
- **PDF Processing**: PyMuPDF (fitz)
- **Environment**: Python 3.10+

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Ifrah27/LexiContact.git
   cd LexiContact
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file in the root directory and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. Run the application:
   ```bash
   streamlit run app.py
   ```

## 📊 Evaluation

The project includes an `eval.py` script that uses the **RAGAS** framework to evaluate faithfulness and answer relevancy of the AI analysis.

---
Built with ❤️ for Legal-Tech Innovation.
