import sqlite3
from pywebio.input import select
from pywebio.output import put_text, put_table, put_buttons, clear
import pandas as pd
import gspread

appen_list = []
appen_dict ={
    "no": "",
    "id": ""
}
def initialize_gspread():
    gc = gspread.service_account(filename="sheet342.json")
    sheet = gc.open("kritik saran")
    return sheet.worksheet("isi")

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

def get_id(df_logs):
    return df_logs['id'].unique() if not df_logs.empty else []
###############

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

#get id
id_user = get_id(df_logs)

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

def initialize_gspread():
    gc = gspread.service_account(filename="sheet342.json")
    sheet = gc.open("kritik saran")
    return sheet.worksheet("isi")
shared_state = {'btn1': None, 'btn2': None, 'btn3':None}

def append_to_sheet(input):
    sheet = initialize_gspread()  
    # If both buttons have been clicked
    if shared_state['btn1'] and shared_state['btn2']:
        row_to_append = ['abc', shared_state['btn1'], shared_state['btn2'], 'ssm ekspor itu apa']
    elif shared_state['btn1']:  # If only button 1 has been clicked
        row_to_append = ['abc', shared_state['btn1'], '', 'ssm ekspor itu apa']
    elif shared_state['btn3']:  # If only button 2 has been clicked
        row_to_append = ['abc', '', shared_state['btn2'], 'ssm ekspor itu apa']
    
    # Append row to the Google Sheet
    sheet.append_row(row_to_append)

    # Reset shared state after appending
    shared_state['btn1'] = None
    shared_state['btn2'] = None
    shared_state['btn3'] = None


def show_page(page, filtered_logs):
    """Show a specific page of records."""
    if 0 <= page < total_pages:
        clear()  # Clear previous content
        start_index = page * records_per_page
        end_index = min(start_index + records_per_page, len(filtered_logs))
        page_data = filtered_logs.iloc[start_index:end_index]

        table_data = [['Id_User','No_Hp', 'Pertanyaan', 'Jawaban Sistem', 'Referensi', 'Apakah referensi sistem sudah up-to-date?', 'Apakah jawaban sudah sesuai referensi dari database?', 'Apakah referensi yang keluar relevan dengan pertanyaan yang ditanyakan?']]
        for i, row in page_data.iterrows():
            table_data.append([
                selected_phone_number, row['question'], row['answer'], ', '.join(row['references']),
                put_buttons(['A', 'B'], onclick=append_to_sheet),
                put_buttons(['A', 'B'], onclick=append_to_sheet),
                put_buttons(['A', 'B'], onclick=append_to_sheet)
            ])
        put_table(table_data)

        put_buttons(['Previous', 'Next'], onclick=[lambda: navigate_pages('previous'), lambda: navigate_pages('next')])
    else:
        put_text("No more records to display.")

def navigate_pages(direction):
    """Navigate between pages."""
    global current_page
    new_page = current_page + (1 if direction == 'next' else -1)
    if 0 <= new_page < total_pages:
        current_page = new_page
        show_page(new_page, filtered_logs)
    else:
        put_text("No more records to navigate.")

aa = gspread.service_account(filename="sheet342.json")
sheet = aa.open("kritik saran")
wr_sheet = sheet.worksheet("isi")
def next_available_row(worksheet, col):
    col_values = worksheet.col_values(col)
    return len(col_values) + 1
teks = input("Input your age: ")
next_row = next_available_row(wr_sheet, 5)
wr_sheet.update_acell(f'E{next_row}', teks)

# Display the initial page
show_page(current_page, filtered_logs)