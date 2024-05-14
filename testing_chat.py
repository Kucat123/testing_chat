from pywebio.input import *
from pywebio.output import *
import pandas as pd
import gspread

df = pd.read_excel("pusatbantuan_lnsw_fix.xlsx")

x = select("pilih nomor: ", options=["08365", "071248", "9614982"])

put_text("penjelasan tentang table")
jawaban = "SSm Ekspor adalah sistem yang digunakan untuk proses pengajuan perizinan terkait ekspor barang melalui sistem tunggal yang mengintegrasikan proses penanganan dokumen terkait ekspor dan impor. Referensi: [1, 2, 33, 34, 17]"

referensi = [int(i) for i in jawaban.split('Referensi: ')[1].strip('[]').split(', ')[-5:]]
filtered_df = df[df['index'].isin(referensi)]

# Concatenate index and values into a single string
konten_values = filtered_df['konten'].tolist()
konten_text = '\n'.join(konten_values)
for index, value in zip(filtered_df.index, konten_values):
    konten_text += f"{index}: {value}\n"


#input saran to gsheet
aa = gspread.service_account(filename="sheet342.json")
sheet = aa.open("kritik saran")
wr_sheet = sheet.worksheet("isi")

saran = input("Masukkan kritik dan saran Anda:", type="text")
wr_sheet.append_row([saran])