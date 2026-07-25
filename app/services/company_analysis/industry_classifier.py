"""
app/services/company_analysis/industry_classifier.py
----------------------------------------------------
Helper logic to classify and normalize industry names.
"""

from typing import Optional

def normalize_industry(industry_name: Optional[str]) -> str:
    """
    Normalizes an industry name returned by AI into a standardized category.
    """
    if not industry_name:
        return "Unknown"
        
    lower = industry_name.lower()
    
    if "hotel" in lower or "hospitality" in lower or "resort" in lower:
        return "Hospitality & Hotels"
    elif "software" in lower or "saas" in lower or "tech" in lower:
        return "Technology & Software"
    elif "retail" in lower or "ecommerce" in lower:
        return "Retail & E-commerce"
    elif "finance" in lower or "bank" in lower or "fintech" in lower:
        return "Finance & Banking"
        
    return industry_name.title()
