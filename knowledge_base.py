import chromadb
from chromadb.utils import embedding_functions

# Hardcoded standard "fair" clauses for common contract types
FAIR_CLAUSES = [
    {
        "id": "indemnity_1",
        "type": "indemnity",
        "text": "Each party shall indemnify, defend, and hold harmless the other party from and against any claims, losses, damages, liabilities, and expenses arising out of or related to the indemnifying party's gross negligence, willful misconduct, or breach of confidentiality obligations under this Agreement. Total liability under this section shall not exceed the total fees paid or payable under this Agreement in the twelve (12) months preceding the claim."
    },
    {
        "id": "termination_1",
        "type": "termination",
        "text": "Either party may terminate this Agreement for convenience by providing at least thirty (30) days prior written notice to the other party. In the event of a material breach, the non-breaching party may terminate this Agreement if the breaching party fails to cure such breach within fifteen (15) days of receiving written notice thereof."
    },
    {
        "id": "confidentiality_1",
        "type": "confidentiality",
        "text": "Confidential Information shall not include information that: (a) is or becomes publicly known through no fault of the receiving party; (b) was rightfully known to the receiving party prior to disclosure; (c) is independently developed by the receiving party without use of or reference to the disclosing party's Confidential Information; or (d) is rightfully received from a third party without restriction on disclosure."
    },
    {
        "id": "non_compete_1",
        "type": "non_compete",
        "text": "During the term of employment and for a period of six (6) months thereafter, Employee shall not directly or indirectly engage in or assist any business that directly competes with the specific products or services offered by Employer within a fifty (50) mile radius of Employee's primary work location."
    },
    {
        "id": "governing_law_1",
        "type": "governing_law",
        "text": "This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflict of law principles. Any legal action or proceeding arising under this Agreement will be brought exclusively in the federal or state courts located in Delaware, and the parties hereby irrevocably consent to the personal jurisdiction and venue therein."
    },
    {
        "id": "intellectual_property_1",
        "type": "intellectual_property",
        "text": "Employer acknowledges that Employee may use pre-existing intellectual property in the performance of services. Employee retains all rights to pre-existing IP. Upon full payment of all undisputed fees, Employee assigns to Employer all rights, title, and interest in and to the specific deliverables created solely for Employer under this Agreement."
    },
    {
        "id": "auto_renewal_1",
        "type": "auto_renewal",
        "text": "The initial term of this Agreement shall be one (1) year. Thereafter, this Agreement shall automatically renew for successive one (1) year terms unless either party provides written notice of its intent not to renew at least sixty (60) days prior to the expiration of the then-current term."
    },
    {
        "id": "data_privacy_1",
        "type": "data_privacy",
        "text": "Provider will use Customer Data solely to provide the Services under this Agreement. Provider shall not sell, rent, or lease Customer Data. Provider explicitly agrees not to use Customer Data to train, fine-tune, or improve any artificial intelligence or machine learning models without Customer's prior explicit written consent."
    },
    {
        "id": "limitation_of_liability_1",
        "type": "limitation_of_liability",
        "text": "Except for obligations regarding confidentiality, indemnification, gross negligence, or willful misconduct, neither party's total aggregate liability arising out of or related to this Agreement shall exceed the amounts paid by Customer to Provider in the twelve (12) months immediately preceding the event giving rise to the claim."
    },
    {
        "id": "payment_terms_1",
        "type": "payment_terms",
        "text": "Invoices are due and payable within thirty (30) days of receipt (Net 30). Late payments may accrue interest at a rate not to exceed 1.5% per month. Provider may suspend Services for non-payment only after providing Customer with at least fifteen (15) days written notice of past due amounts and an opportunity to cure."
    }
]

class KnowledgeBase:
    def __init__(self, persist_directory="./chroma_db"):
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection_name = "fair_clauses"
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )
        self._seed_database()

    def _seed_database(self):
        """Seeds the database if it's empty."""
        existing_count = self.collection.count()
        if existing_count == 0:
            print("Seeding Knowledge Base with standard fair clauses...")
            ids = [clause["id"] for clause in FAIR_CLAUSES]
            documents = [clause["text"] for clause in FAIR_CLAUSES]
            metadatas = [{"type": clause["type"]} for clause in FAIR_CLAUSES]
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Seeded {len(FAIR_CLAUSES)} clauses.")

    def query_fair_clause(self, clause_text: str, n_results: int = 1):
        """
        Queries the vector database for the most similar fair clause.
        Returns the text of the most similar clause.
        """
        results = self.collection.query(
            query_texts=[clause_text],
            n_results=n_results
        )
        
        if results and results['documents'] and len(results['documents'][0]) > 0:
            return results['documents'][0][0], results['metadatas'][0][0]
        return None, None

kb = None
def get_knowledge_base():
    global kb
    if kb is None:
        kb = KnowledgeBase()
    return kb
