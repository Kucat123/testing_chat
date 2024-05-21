import sqlite3
from pywebio.input import *
from pywebio.output import *
import pandas as pd
import gspread

# Global list and dictionary to store user inputs
appen_list = []
appen_dict = {
    "referensi": "",
    "ref_relevan": "",
    "ref_up_to_date": "",
    "jawaban_sesuai": ""
}

def initialize_gspread():
    gc = gspread.service_account(filename="sheet342.json")
    sheet = gc.open("kritik saran")
    return sheet.worksheet("isi")

def button1_click(btn_val, row_idx, ref_idx):
    global appen_dict
    put_text("tetsss")
    appen_dict[f"ref_relevan_{row_idx}_{ref_idx}"] = btn_val
    put_text(appen_dict)
    with use_scope(f"btn_scope_{row_idx}_{ref_idx}_1", clear=True):
        put_text(f"clicked: {btn_val}")

def button2_click(btn_val, row_idx, ref_idx):
    global appen_dict
    appen_dict[f"ref_up_to_date_{row_idx}_{ref_idx}"] = btn_val
    with use_scope(f"btn_scope_{row_idx}_{ref_idx}_2", clear=True):
        put_text(f"clicked: {btn_val}")

def button3_click(btn_val, row_idx):
    global appen_dict
    appen_dict[f"jawaban_sesuai_{row_idx}"] = btn_val
    with use_scope(f"btn_scope_{row_idx}_3", clear=True):
        put_text(f"clicked: {btn_val}")

def append_to_sheet():
    global appen_list
    global appen_dict
    put_text("tets list")
    put_text(selected_phone_number)
    appen_list.append(selected_phone_number)
    put_text(appen_list)
    sheet = initialize_gspread()
    sheet.append_row(appen_list)
    appen_list = []
    appen_dict = {}
    put_text("Data appended to Google Sheets.")

def load_data_from_excel(file_path):
    """Load data from an Excel file into a DataFrame."""
    return pd.read_excel(file_path)

def connect_to_database(db_path):
    """Connect to the SQLite database and return logs DataFrame."""
    try:
        with sqlite3.connect(db_path) as conn:
            return pd.read_sql_query("SELECT * FROM logs", conn), None
    except sqlite3.Error as e:
        return pd.DataFrame(), e

def get_unique_phone_numbers(df_logs):
    """Get unique phone numbers from the logs DataFrame."""
    return df_logs['phone_number'].unique() if not df_logs.empty else []

def filter_logs_by_phone(df_logs, phone_number):
    """Filter logs DataFrame by phone number."""
    return df_logs[df_logs['phone_number'] == phone_number] if not df_logs.empty else pd.DataFrame()

def process_references(df, filtered_logs):
    """Process reference indices and retrieve corresponding 'konten' values."""
    if not filtered_logs.empty:
        filtered_logs['references'] = filtered_logs['reference_index'].str.strip("[]").str.split(", ")
        filtered_logs.drop('reference_index', axis='columns', inplace=True)

        # Limit to 5 references and ensure they are valid integers
        filtered_logs['references'] = filtered_logs['references'].apply(
            lambda refs: [df.at[int(idx), 'konten'] for idx in refs if idx.isdigit()][:5] if refs else []
        )

# Load the Excel file into a DataFrame
df = load_data_from_excel("pusatbantuan_lnsw_fix.xlsx")

# Connect to SQLite database and retrieve data
df_logs, error = connect_to_database(r'logs.db')
if error:
    put_text(f"An error occurred while connecting to the database: {error}")

# Get unique phone numbers from the DataFrame
unique_phone_numbers = get_unique_phone_numbers(df_logs)
# Let the user select a phone number
selected_phone_number = select("Pilih nomor: ", options=list(unique_phone_numbers))

# Filter the DataFrame based on the selected phone number
filtered_logs = filter_logs_by_phone(df_logs, selected_phone_number)

put_text("penjelasan tentang table")

# Process reference indices and retrieve corresponding 'konten' values
process_references(df, filtered_logs)

# Pagination setup
records_per_page = 1
total_pages = (len(filtered_logs) + records_per_page - 1) // records_per_page
current_page = 0  # Use a global variable to track the current page
def show_page(page, filtered_logs):
    """Show a specific page of records."""
    if 0 <= page < total_pages:
        clear()  # Clear previous content
        start_index = page * records_per_page
        end_index = min(start_index + records_per_page, len(filtered_logs))
        page_data = filtered_logs.iloc[start_index:end_index]

        table_data = [['No', 'No Hp', 'Pertanyaan', 'Jawaban Sistem', 'Penilaian Referensi', 'Apakah jawaban sudah sesuai?']]
        for idx, row in page_data.iterrows():
            i = start_index + idx  # Absolute index
            references_table = [['Referensi', 'apakah ref relevan', 'apakah ref up to date']]
            for ref_idx, ref in enumerate(row['references']):
                references_table.append([
                    ref,
                    put_scope(f"btn_scope_{i}_{ref_idx}_1", put_buttons(['yes', 'no', 'tdk tau'], onclick=lambda btn_val, row_idx=i, ref_idx=ref_idx: button1_click(btn_val, row_idx, ref_idx))),
                    put_scope(f"btn_scope_{i}_{ref_idx}_2", put_buttons(['yes', 'no', 'tdk tau'], onclick=lambda btn_val, row_idx=i, ref_idx=ref_idx: button2_click(btn_val, row_idx, ref_idx)))
                ])
            
            table_data.append([
                i + 1, selected_phone_number, row['question'], row['answer'],
                put_table(references_table),
                put_scope(f"btn_scope_{i}_3", put_buttons(['NO', 'YES'], onclick=lambda btn_val, row_idx=i: button3_click(btn_val, row_idx)))
            ])
        
        put_table(table_data)

        # Submit button
        put_button(['Submit'], onclick=collect_and_append_data)

        put_buttons(['Previous', 'Next'], onclick=[lambda: navigate_pages('previous'), lambda: navigate_pages('next')])
    else:
        put_text("No more records to display.")  

def collect_and_append_data():
    global appen_list
    global appen_dict
    for idx in range(len(filtered_logs)):
        row_idx = current_page * records_per_page + idx
        appen_list.append([
            row_idx + 1,  # No
            selected_phone_number,  # No Hp
            filtered_logs.iloc[row_idx]['question'],  # Pertanyaan
            filtered_logs.iloc[row_idx]['answer'],  # Jawaban Sistem
            # Penilaian Referensi
            [[
                filtered_logs.iloc[row_idx]['references'][ref_idx], 
                appen_dict.get(f"ref_relevan_{row_idx}_{ref_idx}", ""), 
                appen_dict.get(f"ref_up_to_date_{row_idx}_{ref_idx}", "")
            ] for ref_idx in range(len(filtered_logs.iloc[row_idx]['references']))],
            appen_dict.get(f"jawaban_sesuai_{row_idx}", "")  # Apakah jawaban sudah sesuai?
        ])

    append_to_sheet()

def navigate_pages(direction):
    """Navigate between pages."""
    global current_page
    new_page = current_page + (1 if direction == 'next' else -1)
    if 0 <= new_page < total_pages:
        current_page = new_page
        show_page(new_page, filtered_logs)
    else:
        put_text("No more records to navigate.")

# Display the initial page
show_page(current_page, filtered_logs)
