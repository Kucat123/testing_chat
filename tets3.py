from pywebio.input import *
from pywebio.output import *
from pywebio import start_server
import gspread

appen_list = []
appen_dict = {
    "no": "",
    "id": ""
}

def initialize_gspread():
    gc = gspread.service_account(filename="sheet342.json")
    sheet = gc.open("kritik saran")
    return sheet.worksheet("isi")

def button1_click(btn_val):
    global appen_dict
    appen_dict["no"] = btn_val
    with use_scope("btn_scope"):
        clear()
        put_text(f"Clicked: {btn_val}")

def button2_click(btn_val):
    global appen_dict
    appen_dict["id"] = btn_val
    with use_scope("btn_scope1"):
        clear()
        put_text(f"Clicked: {btn_val}")

def append_to_sheet():
    global appen_list
    global appen_dict
    # Collect the current state of appen_dict into appen_list
    appen_list.append([appen_dict["no"], appen_dict["id"]])
    
    # Display the collected data for confirmation
    with use_scope("btn_scope2"):
        clear()
        put_text(f"Collected Data: {appen_list}")

    # Initialize Google Sheets and append the collected data
    sheet = initialize_gspread()
    for record in appen_list:
        sheet.append_row(record)

    # Clear the appen_list and appen_dict for the next set of inputs
    appen_list.clear()
    appen_dict.clear()

def main():
    put_table([
        ['Type', 'btn1', 'btn2', 'konten'],
        ['abc',
         put_scope("btn_scope", put_buttons([('A', 'ref'), ('B', 'jawaban')], onclick=lambda btn_val: button1_click(btn_val))),
         put_scope("btn_scope1", put_buttons([('A', 'val A'), ('B', 'val b')], onclick=lambda btn_val: button2_click(btn_val))),
         'ssm ekspor itu apa',
         put_scope("btn_scope2", put_button("submit", onclick=append_to_sheet))
        ]
    ])

start_server(main, port=8082, debug=True)
