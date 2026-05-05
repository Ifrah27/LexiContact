import fitz

def create_sample_pdf(filename="sample_contract.pdf"):
    doc = fitz.open()
    page = doc.new_page()
    
    text = """
EMPLOYMENT AGREEMENT

This Employment Agreement is made today between TechCorp ("Employer") and John Doe ("Employee").

1. Term
The employment shall commence on Jan 1, 2024 and continue at-will.

2. Confidentiality
Employee agrees not to disclose any information about the Employer, including publicly known information.

3. Non-Compete
Employee agrees not to work for any company in the world for 10 years after termination.

4. Indemnity
Employee will indemnify Employer for any and all losses regardless of fault.

5. Termination
Employer may terminate this agreement at any time without notice.
"""
    
    # Simple text insertion
    page.insert_text(fitz.Point(50, 50), text, fontsize=12)
    
    doc.save(filename)
    doc.close()
    print(f"Created {filename}")

if __name__ == "__main__":
    create_sample_pdf()
