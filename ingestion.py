import io
import re
import fitz  # PyMuPDF
import pymupdf4llm

def load_pdf(file_path_or_bytes):
    if isinstance(file_path_or_bytes, bytes):
        return file_path_or_bytes
    with open(file_path_or_bytes, "rb") as f:
        return f.read()

def pdf_to_markdown(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    md_text = pymupdf4llm.to_markdown(doc)
    return md_text

def clean_markdown(md_text: str) -> str:
    md_text = re.sub(r'(?im)^Page\s+\d+\s*(of\s*\d+)?\s*$', '', md_text)
    md_text = re.sub(r'(?im)^\s*\-\s*\d+\s*\-\s*$', '', md_text)
    md_text = re.sub(r'\n{3,}', '\n\n', md_text)
    return md_text.strip()

def split_into_clauses(md_text: str) -> list[str]:
    # Improved semantic chunking pattern
    pattern = r'^(?:\#{1,4}\s+|Article\s+[IVX]+|Section\s+\d+|\d+\.\d*\s+)'
    parts = re.split(f'({pattern})', md_text, flags=re.IGNORECASE | re.MULTILINE)
    
    clauses = []
    if parts[0].strip():
        clauses.append(parts[0].strip())
        
    for i in range(1, len(parts), 2):
        heading = parts[i]
        content = parts[i+1] if i+1 < len(parts) else ""
        clause_text = (heading + content).strip()
        if len(clause_text) > 30: # ignore very small empty fragments
            clauses.append(clause_text)
            
    if len(clauses) <= 1:
        clauses = [c.strip() for c in md_text.split('\n\n') if len(c.strip()) > 30]
    
    # Deduplicate while preserving order
    seen = set()
    unique_clauses = []
    for c in clauses:
        # Simple normalization for deduplication
        norm_c = " ".join(c.split()).lower()
        if norm_c not in seen:
            seen.add(norm_c)
            unique_clauses.append(c)
            
    return unique_clauses

def process_pdf(pdf_bytes: bytes) -> list[str]:
    md = pdf_to_markdown(pdf_bytes)
    cleaned_md = clean_markdown(md)
    clauses = split_into_clauses(cleaned_md)
    return clauses

if __name__ == "__main__":
    sample_text = """
## Section 1. Confidentiality
The parties agree to keep things secret.
    
2. Indemnification
You will pay for everything if it goes wrong.
    """
    print(split_into_clauses(sample_text))
