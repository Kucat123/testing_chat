import pandas as pd
from pywebio.input import *
from pywebio.output import *
import sqlite3
import ast

conn = sqlite3.connect(r'logs.db')
cursor = conn.cursor()
df = pd.read_excel("pusatbantuan_lnsw_fix.xlsx")
try:
    cursor.execute("SELECT * FROM logs")  # Replace 'tablename' with your actual table name

    rows = cursor.fetchall()
    
except sqlite3.Error as e:
    put_text(f"An error occurred while connecting to the database: {e}")
    rows = []  # Ensure rows is an empty list if there's an error
if rows:
    df_logs = pd.DataFrame(rows, columns=[column[0] for column in cursor.description])
else:
    df_logs = pd.DataFrame()

unique_phone_numbers = df_logs['phone_number'].unique()
# Let the user select a phone number
selected_phone_number = select("Pilih nomor: ", options=unique_phone_numbers)
# Filter the DataFrame based on the selected phone number
filtered_logs = df_logs[df_logs['phone_number'] == selected_phone_number]

def filter_logs_by_phone(df_logs, phone_number):
    """Filter logs DataFrame by phone number."""
    return df_logs[df_logs['phone_number'] == phone_number] if not df_logs.empty else pd.DataFrame()

# Ambil nilai unik dari kolom reference_index
ref_idx = df_logs['reference_index'].unique()

# Bersihkan dan konversi nilai indeks ke dalam daftar (jika diperlukan)
def safe_eval(value):
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return []

# Bersihkan dan konversi nilai indeks ke dalam daftar
ref_idx_list = []
for idx in ref_idx:
    if idx and isinstance(idx, str) and idx.strip() != '':
        idx_list = safe_eval(idx)  # Mengubah string list menjadi list asli secara aman
        ref_idx_list.extend(idx_list)

# Filter dataframe berdasarkan nilai index yang ditemukan
filtered_df = df[df['index'].isin(ref_idx_list)]

# Buat tabel konten berdasarkan index
table_data = [["Index", "Konten"]]
for _, row in filtered_df.iterrows():
    table_data.append([row['index'], row['konten']])

def main():
    # Tampilkan tabel menggunakan PyWebIO
    put_table(table_data)
