# **Receipt Reconciliation & Data Validation Tool**

## 📊 Business Case & Project Overview

In financial auditing, manually matching bank statements to physical receipts is a time-consuming, error-prone process. This project provides an automated ETL (Extract, Transform, Load) pipeline that reconciles CSV financial statements against a directory of PDF receipts. 
By leveraging Regular Expressions (Regex) and Fuzzy Logic, the script identifies missing documentation, accounts for banking "float" (transaction delays), and standardizes inconsistent data formats across different financial institutions.

---
## 🛠️ Key Data Science Competencies Demonstrated

**Data Cleaning & Normalization:** Standardizes inconsistent currency formats (e.g., converting ($5.00) strings to float -5.00) and handles sign-reversal logic between Asset (Bank) and Liability (Credit Card) accounts.  

**Automated Feature Mapping:** Implemented a robust header-detection algorithm that maps varying CSV schemas (e.g., "Post Date" vs. "Trans Date") to a unified data model.  

**Unstructured Data Extraction:** Utilizes pdfplumber and Regex to perform OCR-like data extraction from unstructured PDF documents.  

**Fuzzy Temporal Matching:** Accounts for real-world data variance by implementing a look-back window (default 3 days) to match transaction post-dates with receipt purchase dates.  

---
## 🚀 Features

**Dual-Mode Toggle:** Banks and credit card companies view your financial data differently and as such, they prepare it for customers to view in different ways.  This often means User-input driven logic to handle sign-reversal for Credit Card vs. Bank statements.  

**Smart Column Detection:** Automatically identifies date and amount columns using case-insensitive keyword mapping.  

**PDF Intelligence:** Extracts and caches dollar amounts and dates from receipt directories to optimize lookup speeds.  

**Comprehensive Reporting:** Generates a timestamped reconciliation report flagging matches, partial matches, and missing documentation.  

---
## ⚙️ Configuration & Installation

### Prerequisites

pip install pdfplumber python-dateutil

## Setup

    **search_dir**: Set this to your local directory containing PDF receipts.

    **csv_input_path**: Set this to the path of your bank/credit card CSV export.

    **date_col / amount_col**: The script includes a default shortlist of common headers. You can append unique headers from your specific bank to the find_col function.
    
---
## 📖 How It Works

    1.) Ingestion & Caching: The script performs a recursive search of the search_dir, parsing PDF text into a structured dictionary of dates and currency values.

    2.) Transformation: Based on the Bank/Credit Card toggle, the script normalizes transaction signs so that "purchases" always represent a positive search value.

    3.) Validation:

        Primary Key: Exact match on dollar amount.

        Secondary Validation: Date proximity (checks if receipt date ∈ [Statement Date - 3 days]).

    4.) Output: A reconciled CSV containing file paths for matched receipts and audit notes for unmatched rows.
    
---
## 📝 Example Output

    Date	Amount	FileName	FilePath	Notes
    11/01/2025	45.50	receipt_123.pdf	/home/docs/receipt_123.pdf	Matched on 2025-10-31
    11/02/2025	1200.00	N/A	N/A	Transaction is payment or credit
    11/05/2025	12.99	N/A	N/A	No match found in 3-day window
    
---
## ⚠️ Disclaimer

This tool is for educational and personal productivity purposes only. Financial data is sensitive. 
This script runs entirely locally, and no data is transmitted externally. 
Users should manually verify all outputs before making financial decisions or filing tax documentation. 
The author assumes no liability for financial discrepancies.

---
## 📜 License

Distributed under the MIT License. See LICENSE for more information.
