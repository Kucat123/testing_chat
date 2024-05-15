import sqlite3
from pywebio.input import select
from pywebio.output import put_text, put_table, put_buttons
import pandas as pd
import gspread

# Load the Excel file into a DataFrame
df = pd.read_excel("pusatbantuan_lnsw_fix.xlsx")

# Connect to SQLite database
# Use a raw string for the file path or double backslashes to avoid escape sequence errors
conn = sqlite3.connect(r'D:\Projects\LNSW\new_wa_api\logging_db\logs.db')
cursor = conn.cursor()

# Retrieve data from SQLite database
try:
    cursor.execute("SELECT * FROM logs")  # Replace 'tablename' with your actual table name

    rows = cursor.fetchall()
    
except sqlite3.Error as e:
    put_text(f"An error occurred while connecting to the database: {e}")
    rows = []  # Ensure rows is an empty list if there's an error

# The pd.read_sql_table function is not appropriate here as it expects a table name and a SQLAlchemy engine, not the result of a fetchall() call.
# Instead, we should use pd.DataFrame to convert the rows fetched from the database into a DataFrame.
# Additionally, we should handle the case where rows is an empty list due to a database error.
if rows:
    df_logs = pd.DataFrame(rows, columns=[column[0] for column in cursor.description])
else:
    df_logs = pd.DataFrame()
# print(df_logs)

# Get unique phone numbers from the DataFrame
unique_phone_numbers = df_logs['phone_number'].unique()

# Let the user select a phone number
selected_phone_number = select("Pilih nomor: ", options=unique_phone_numbers)

# Filter the DataFrame based on the selected phone number
filtered_logs = df_logs[df_logs['phone_number'] == selected_phone_number]

put_text("penjelasan tentang table")

jawaban = filtered_logs['answer']


references = filtered_logs['reference_index'][1].split(", ")
print(references)

# filtered_df = df[df['index'].isin(filtered_logs['reference_index'])]

# print(filtered_df)



# # Concatenate index and values into a single string
# konten_values = filtered_df['konten'].tolist()
# konten_text = '\n'.join(konten_values)
# for index, value in zip(filtered_df.index, konten_values):
#     konten_text += f"{index}: {value}\n"

# # print(filtered_logs)

# i=0
# for index, row in filtered_logs.iterrows():
#     put_table([
#         ['No', 'Pertanyaan', 'Jawaban Sistem', 'Referensi' ,'Apakah referensi sistem sudah up-to-date?', 'Apakah jawaban sudah sesuai referensi dari database?', 'Apakah referensi yang keluar relevan dengan pertanyaan yang ditanyakan?'],
#         [i+1, row['question'], row['answer'], filtered_df[i],put_buttons(['NO', 'YES'], onclick=...), put_buttons(['NO', 'YES'], onclick=...), put_buttons(['NO', 'YES'], onclick=...)]
#     ])
#     i+=1

# # #input saran to gsheet
# # aa = gspread.service_account(filename="sheet342.json")
# # sheet = aa.open("kritik saran")
# # wr_sheet = sheet.worksheet("isi")

# # saran = input("Masukkan kritik dan saran Anda:", type="text")
# # wr_sheet.append_row([saran])
# # #comment