#a script that will take a bank or credit card statement csv file and check each transaction against a matching receipt located in a desktop file system. Outputs a csv reconciling transactions and flagging missing/partial matches
import csv, logging, pdfplumber, re
from datetime import datetime, date, timedelta
from dateutil import parser
from pathlib import Path                     

# to ask the user for input for Account Type
is_credit_card = input("Is this a credit card statement? (y/n): ").lower().strip() == 'y'

# to silence the P0 errors that were occuring during pdf text extraction
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# a function used to rip all text from a pdf
def extract_text_from_pdf(pdf_path):
    all_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:  #naming the current pdf file being reviewed as the local variable 'pdf'
            for page in pdf.pages:
                text = page.extract_text()
                if text:    #conditional that checks if there is actually any text to extract from the pdf
                    all_text += text + "\n" #appending the text from the current pdf and then including a newline
        return all_text
    except Exception as e:
        print(f"Could not read {pdf_path.name}: {e}")
        return ""

# regex for currency: 1,234.56, 12.00, etc.
DOLLAR_PATTERN = re.compile(r'\d{1,3}(?:,\d{3})*\.\d{2}')
# broad regex for dates: YYYY/MM/DD, MM/DD/YYYY, Month DD, YYYY, etc.
DATE_PATTERN = re.compile(r'(\d{1,4}[-/\.]\d{1,2}[-/\.]\d{1,4})|(\w+ \d{1,2},? \d{4})')

# building the pdf cache.  Providing an empty dictionary variable for the keywords pulled per pdf and a file directory from which the cache will be constructed
pdf_cache = {}
# --- Manual input to below variable required ---
search_dir = Path(r'ADD INPUT CSV FILEPATH HERE')

print("Building PDF cache - Extracting dates and amounts...")

# rglob makes it a recursive search in that it will handle searching through multiple files for pdf documents and then extract
for pdf_file in search_dir.rglob('*.pdf'):
    text = extract_text_from_pdf(pdf_file)
    if not text:
        continue

    # extract Dollars into a variable with a set data type
    found_dollars = set(DOLLAR_PATTERN.findall(text))

    # extract Full Dates (storing as actual datetime objects) into a variable with a set data type
    found_dates = set()

    # flatten the regex groups
    date_strings = [item for sublist in DATE_PATTERN.findall(text) for item in sublist if item]
    
    for ds in date_strings:
        try:
            # using the fuzzy=True parameter to catch dates inside text strings
            dt = parser.parse(ds, fuzzy=True).date() 
            found_dates.add(dt)
        except (ValueError, OverflowError):
            continue

# output variable from caching step that contains a dictionary made up of all pulled pdf's dollar and dates
    pdf_cache[pdf_file] = {
        'dollars': found_dollars,
        'dates': found_dates
    }

print(f"Cache complete. Indexed {len(pdf_cache)} PDFs.")

# the reconcilation logic of the script, used to match the opened csv keywords against what was pulled to create the cache
# --- Manual input to below variable required ---
csv_input_path = r'ADD INPUT FILEPATH HERE'

# output csv file name creation with yyyy-mm-dd format and output csv file creation
today_date = date.today()
date_string = today_date.strftime('%Y-%m-%d')
output_file_name = f'{date_string}_receipt_reconciliation.csv'

# assigning the input and output csv files local variables before beginning the loops
with open(csv_input_path, mode='r', encoding='utf-8') as csv_input, open(output_file_name, mode='w', newline='') as csv_output:

    # read the first line of the input csv to find the actual column names
    reader = csv.DictReader(csv_input)
    actual_headers = reader.fieldnames
    
    # a helper function to find the best matching column name
    def find_col(possible_names, headers):
        for name in possible_names:
            for header in headers:
                if name.lower() == header.lower().strip():
                    return header
        return None

    # to determine which columns to use for Date and Amount - adjust this if your date or amount column's are called something different than the below
    date_col = find_col(['Date', 'Transaction Date', 'Post Date', 'Trans Date', 'Posted Date'], actual_headers)
    amount_col = find_col(['Amount', 'Debit', 'Charge', 'Description Amount'], actual_headers)

    if not date_col or not amount_col:
        raise KeyError(f"Could not find Date or Amount columns. Found: {actual_headers}")

    writer = csv.DictWriter(csv_output, fieldnames=['Date', 'Amount', 'FileName', 'FilePath', 'Notes'])
    writer.writeheader()

    for row in reader:
        # use the dynamically found column names
        raw_date = row[date_col].strip()
        raw_dollar = row[amount_col].strip()
        
        try:
            clean_dollar = raw_dollar.replace('$', '').replace(',', '')
            if clean_dollar.startswith('(') and clean_dollar.endswith(')'):
                clean_dollar = '-' + clean_dollar.strip('()')
            
            dollar_float = float(clean_dollar)       
            
            if is_credit_card:
                dollar_float = dollar_float * -1
            
            if dollar_float < 0:
                writer.writerow({
                    'Date': raw_date,     
                    'Amount': raw_dollar,  
                    'FileName': 'N/A', 
                    'Notes': 'Transaction is either payment or vendor credit'
                })
                continue
            
            csv_dollar_formatted = "{:.2f}".format(dollar_float)

        except ValueError:
            continue
        
        try:
            target_date = parser.parse(raw_date).date()
        except:
            print(f"Could not parse date: {raw_date}")
            continue
        
        start_window = target_date - timedelta(days=3)        
        match_found = False
        
        for pdf_path, data in pdf_cache.items():
            if csv_dollar_formatted in data['dollars']:
                for pdf_dt in data['dates']:
                    if start_window <= pdf_dt <= target_date:
                        writer.writerow({
                            'Date': raw_date,     
                            'Amount': raw_dollar,  
                            'FileName': pdf_path.name, 
                            'FilePath': str(pdf_path), 
                            'Notes': f'Matched on {pdf_dt}'
                        })
                        match_found = True
                        break            
            if match_found: break
            
        if not match_found:
            writer.writerow({
                'Date': raw_date,      
                'Amount': raw_dollar,  
                'FileName': 'N/A', 
                'Notes': 'No match found in 3-day window'
            })

print('Exercise complete, script completed!')