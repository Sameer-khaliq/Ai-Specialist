# create_sample_docs.py — run this once to make test files
import os

os.makedirs("documents", exist_ok=True)

docs = {
    "company_policy.txt": """
    COMPANY POLICY DOCUMENT
    
    Leave Policy:
    Employees get 20 annual leaves per year.
    Sick leave is 10 days per year.
    Maternity leave is 90 days.
    All leave requests must be submitted 2 weeks in advance.
    
    Remote Work Policy:
    Employees can work remotely 3 days per week.
    Core hours are 10am to 4pm.
    VPN must be used for all remote work.
    """,
    
    "product_manual.docx": """
    PRODUCT MANUAL — AI Assistant Pro v2.0
    
    Installation:
    Run pip install ai-assistant-pro to install.
    Requires Python 3.9 or higher.
    Minimum 8GB RAM required.
    
    Features:
    - Natural language processing
    - Multi-document search
    - Real-time response generation
    - API integration support
    
    Troubleshooting:
    If the product crashes, restart the service.
    For API errors, check your API key in settings.
    Contact support@aiassistant.com for help.
    """,
    
    "financial_report.pdf": """
    FINANCIAL REPORT Q3 2024
    
    Revenue: $2.4 million (up 23% from Q2)
    Expenses: $1.8 million
    Net Profit: $600,000
    
    Top performing products:
    1. AI Assistant Pro — $1.2M revenue
    2. Data Analytics Suite — $800K revenue
    3. Cloud Storage Plan — $400K revenue
    
    Forecast Q4:
    Expected revenue: $3.1 million
    New product launches: 2 planned
    Hiring plan: 15 new engineers
    """
}

for filename, content in docs.items():
    with open(f"documents/{filename}", "w") as f:
        f.write(content)

print("sample documents created in /documents folder")