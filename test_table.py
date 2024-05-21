import pandas as pd
from pywebio.output import put_table, put_buttons, put_text, put_row

data = {
    'index': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'Referensi': [
        'Referensi 1', 'Referensi 2', 'Referensi 3', 'Referensi 4', 'Referensi 5',
        'Referensi 6', 'Referensi 7', 'Referensi 8', 'Referensi 9', 'Referensi 10'
    ],
    'Score': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
}

df = pd.DataFrame(data)
jawaban = "Referensi: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"

referensi = [int(i) for i in jawaban.split('Referensi: ')[1].strip('[]').split(', ')]

filtered_df = df[df['index'].isin(referensi)]

def handle_click(btn_value):
    put_text(f"You clicked: {btn_value}")

#tabel PyWebIO
table_content = [['Referensi', 'Score']]
for _, row in filtered_df.iterrows():
    table_content.append([
        row['Referensi'],
        put_buttons([row['Score']], onclick=handle_click)
    ])
put_table(table_content)
