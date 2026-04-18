"""
Transaction categorizer using keyword matching on merchant names and descriptions.
"""

import re

# Keyword → category mapping (order matters: more specific first)
CATEGORY_RULES: list[tuple[list[str], str]] = [
    # Groceries
    (
        ["walmart", "kroger", "safeway", "whole foods", "trader joe", "aldi",
         "publix", "costco", "target grocery", "fresh market", "supermarket",
         "grocery", "market", "food mart", "7-eleven", "7eleven"],
        "Groceries",
    ),
    # Dining / Restaurants
    (
        ["mcdonald", "starbucks", "subway", "chipotle", "domino", "pizza",
         "burger", "kfc", "taco bell", "chick-fil", "doordash", "ubereats",
         "grubhub", "restaurant", "cafe", "diner", "sushi", "thai", "chinese",
         "indian food", "fast food", "food delivery"],
        "Dining",
    ),
    # Entertainment
    (
        ["netflix", "spotify", "hulu", "disney+", "disney plus", "hbo",
         "amazon prime", "apple tv", "youtube premium", "twitch", "steam",
         "playstation", "xbox", "nintendo", "cinema", "movie", "theater",
         "concert", "ticketmaster", "eventbrite", "amc"],
        "Entertainment",
    ),
    # Subscriptions (generic)
    (
        ["subscription", "monthly plan", "annual plan", "membership"],
        "Subscriptions",
    ),
    # Utilities
    (
        ["electric", "electricity", "water bill", "gas bill", "utility",
         "utilities", "internet", "broadband", "at&t", "verizon", "comcast",
         "xfinity", "spectrum", "phone bill", "mobile plan", "t-mobile",
         "sprint"],
        "Utilities",
    ),
    # Housing / Rent
    (
        ["rent", "mortgage", "property tax", "hoa", "landlord", "apartment",
         "lease"],
        "Housing",
    ),
    # Transportation
    (
        ["uber", "lyft", "taxi", "gas station", "shell", "exxon", "chevron",
         "bp fuel", "citgo", "parking", "toll", "transit", "metro", "bus pass",
         "train", "amtrak", "airline", "flight", "delta", "united airlines",
         "southwest", "american airlines"],
        "Transportation",
    ),
    # Healthcare
    (
        ["pharmacy", "cvs", "walgreens", "rite aid", "hospital", "clinic",
         "doctor", "dentist", "optometrist", "health", "medical", "insurance",
         "blue cross", "aetna", "cigna", "humana"],
        "Healthcare",
    ),
    # Shopping / Retail
    (
        ["amazon", "ebay", "etsy", "best buy", "apple store", "nike", "adidas",
         "h&m", "zara", "gap", "old navy", "macy", "nordstrom", "tj maxx",
         "ross", "marshalls", "online shopping", "retail"],
        "Shopping",
    ),
    # Education
    (
        ["tuition", "university", "college", "school", "udemy", "coursera",
         "edx", "skillshare", "linkedin learning", "books", "textbook"],
        "Education",
    ),
    # Savings / Investments
    (
        ["savings", "investment", "brokerage", "401k", "ira", "vanguard",
         "fidelity", "robinhood", "transfer to savings", "etf"],
        "Savings",
    ),
    # Income (credits)
    (
        ["payroll", "salary", "direct deposit", "income", "refund", "cashback",
         "tax refund", "interest earned"],
        "Income",
    ),
]


def categorize_transaction(description: str, amount: float) -> str:
    """
    Return a category string for the given transaction description and amount.
    A positive amount is treated as a debit (expense); negative as a credit.
    """
    desc_lower = description.lower()
    # Strip punctuation for cleaner matching
    desc_clean = re.sub(r"[^a-z0-9 ]", " ", desc_lower)

    for keywords, category in CATEGORY_RULES:
        for kw in keywords:
            if kw in desc_clean:
                return category

    # Fall back based on sign
    if amount < 0:
        return "Income"

    return "Other"
