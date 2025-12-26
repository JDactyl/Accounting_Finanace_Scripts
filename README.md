# Accounting_Finanace_Scripts
Python scripts for office related tasks

**---Receipt Reconciliation Tool---**

A Python-based automation script that reconciles bank or credit card statements against a directory of PDF receipts. It uses fuzzy date matching and optical-style text extraction to identify missing documentation for financial transactions.
Features:

    Dual Mode Support: Handles both Bank and Credit Card CSV exports (automatically handles sign reversal for credit transactions).

    PDF Intelligence: Extracts text from PDF receipts to find matching dollar amounts and transaction dates.

    Fuzzy Date Matching: Includes a configurable 3-day look-back window to account for processing delays between a purchase and the statement post date.

    Detailed Reporting: Generates a timestamped CSV report flagging matched transactions, partial matches, and missing receipts.

    Clean Data Handling: Automatically manages currency symbols ($), commas, and accounting-style negative numbers in parentheses ($5.00).

**Prerequisites:**
Before running the script, ensure you have the following installed:

    - Python 3.x
    Dependencies:
    - pip install pdfplumber python-dateutil

 **Project Structure**
        
        ├── receipt_reconciliation.py     # The main script
        ├── README.md                     # Project documentation
        └── [Output Files]                # YYYY-MM-DD_receipt_reconciliation.csv

**---Configuration---**
Before running the script, update the following variables in reconcile.py to match your local environment:

    1.) search_dir: The path to the folder where you store your PDF receipts. (script is operating-system agnostic)
    2.) csv_input_path: The path to your bank or credit card CSV statement.  You can pull this information by going to the folder the holds all of your receipts and look at the folders properties:  the filepath should be displayed for you.  Just copy and paste into this variable.
    3.) date_col, amount_col: If the date or amount column headers on the CSV are called something else that the default shortlist doesn't have, you can include it or adjust both variables to match the bank/credit cards you work with.

**---How It Works---**

    PDF Caching: The script scans your receipt directory, extracting all dollar amounts and dates into a temporary memory cache.

    User Input: You are prompted to specify if the file is a Bank or Credit Card statement.
        Credit Card mode flips negative values to positive to ensure purchases are matched correctly.

    Matching Logic:
        It looks for the exact dollar amount in the PDF text.
        If found, it checks if any date in that PDF falls within a 3-day window prior to the statement date.

    Reporting: The script writes results to a new CSV, detailing which PDF file matched which transaction and where that pdf is located in your file directory.

Example Output:

    Date	Amount	FileName	FilePath	Notes
    11/01/2025	45.50	receipt_123.pdf	/home/docs/receipt_123.pdf	Matched on 2025-10-31
    11/02/2025	1200.00	N/A	N/A	Transaction is payment or credit
    11/05/2025	12.99	N/A	N/A	No match found in 3-day window

