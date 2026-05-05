def verify_quote(clause_text: str, quoted_text: str) -> bool:
    """
    Checks if the quoted text returned by the LLM actually exists within the original clause.
    Uses simple substring matching after basic normalization (stripping whitespace/newlines).
    """
    if not quoted_text or quoted_text.lower() == "none" or quoted_text.lower() == "n/a":
        return True # Nothing to verify
        
    # Normalize texts: remove extra spaces and newlines for robust matching
    norm_clause = " ".join(clause_text.split())
    norm_quote = " ".join(quoted_text.split())
    
    # Check if the normalized quote is a substring of the normalized clause
    return norm_quote in norm_clause
