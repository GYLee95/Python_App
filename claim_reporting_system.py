# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 23:25:38 2024

@author: gangylee

@GitHub

"""

from tkinter import *
from tkinter import filedialog, messagebox, simpledialog
from tkcalendar import *
from PIL import Image, ImageTk
from fpdf import FPDF
from datetime import date, datetime
from random import *
import re
import sqlite3

# -----------------------------------------------------------------------------
# Globals

TITLE = "Brosince Group Sdn Bhd | Claim Reporting System"
APP_ICON    = "icon/CPS.ico"
ROOT_BG_COLOR   = "#E6EBF6"
FONT_SIZE = 15
INPUT_WIDTH = 30

REPORT_ABBR = "CR"
REPORT_NUM = "%s%s_%s" %(REPORT_ABBR, datetime.now().strftime('%Y%m%d_%H%M%S'), randint(1, 1000))

DATABASE = 'claim_report.db'

# -----------------------------------------------------------------------------

class App_page:
    def __init__(self, root):
        self.root = root
        self.root.title("%s" %TITLE)
        self.root.iconbitmap(default=APP_ICON)
        
        # --- set bg color
        self.root.config(bg=ROOT_BG_COLOR)
        
        self.trans_amount = StringVar()
        self.trans_description = StringVar()
        self.receipt_path = None
        self.claims = []  # List to hold multiple claims
        
        # --- hide the main window
        self.root_hide()
        
        # --- ask for claimant name
        self.claimant = simpledialog.askstring(title="Claimant Name", prompt="Please key in your name:", parent=self.root)
        
        if self.claimant:
            # --- restore the main window
            self.root_show()
            
            # --- App layout
            # --- --- Data View
            self.main_frame = Frame(self.root, bg=ROOT_BG_COLOR)
            self.main_frame.grid(row=0, column=0, sticky=E+W+N+S)
            
            claimant_name = Label(self.main_frame, text="Claimant Name", font=("yu gothic ui",FONT_SIZE), bg=ROOT_BG_COLOR)
            claimant_name.grid(row=0, column=0, sticky=W, padx=5, pady=(10,0))
            claimant_name_input = Label(self.main_frame, text=f" : {self.claimant}", font=("yu gothic ui",FONT_SIZE), bg=ROOT_BG_COLOR)
            claimant_name_input.grid(row=0, column=1, sticky=W, pady=(10,0))
            
            submission_date = Label(self.main_frame, text="Submission Date", font=("yu gothic ui",15), bg=ROOT_BG_COLOR)
            submission_date.grid(row=1, column=0, sticky=W, padx=5)
            submission_date_input = Label(self.main_frame, text=" : %s" %date.today(), font=("yu gothic ui",FONT_SIZE), bg=ROOT_BG_COLOR)
            submission_date_input.grid(row=1, column=1, sticky=W)
            
            report_number = Label(self.main_frame, text="Report Number", font=("yu gothic ui",FONT_SIZE), bg=ROOT_BG_COLOR)
            report_number.grid(row=2, column=0, sticky=W, padx=5)
            report_number_input = Label(self.main_frame, text=" : %s" %(REPORT_NUM), font=("yu gothic ui",FONT_SIZE), bg=ROOT_BG_COLOR)
            report_number_input.grid(row=2, column=1, sticky=W)
            
            # team.grid(row=1, column=0, sticky=W+N, padx=20, pady=10, ipady=15)
            # self.team_select.grid(row=1, column=0, sticky=W+S, padx=20)
            
            claim_details = Label(self.main_frame, text="=========  Claim Details  =========", font=("yu gothic ui",FONT_SIZE,"bold"), bg=ROOT_BG_COLOR)
            claim_details.grid(row=3, column=0, columnspan=2, sticky=W, padx=5, pady=(30,10))
            
            transaction_date = Label(self.main_frame, text="Transaction Date", font=("yu gothic ui",FONT_SIZE), bg=ROOT_BG_COLOR)
            transaction_date.grid(row=4, column=0, sticky=W, padx=5, pady=(0,5))
            self.entry_transaction_date = DateEntry(self.main_frame, font=("yu gothic ui",FONT_SIZE), width=INPUT_WIDTH, background="darkblue", foreground="white", borderwidth=2, date_pattern='yyyy-mm-dd', maxdate=date.today())
            self.entry_transaction_date.grid(row=5, column=0, columnspan=2, sticky=W, padx=10, pady=(0,25))
            self.entry_transaction_date.set_date(datetime.today())  # Set default date to today
            
            amount = Label(self.main_frame, text="Amount (RM)", font=("yu gothic ui",FONT_SIZE), bg=ROOT_BG_COLOR)
            amount.grid(row=6, column=0, sticky=W, padx=5, pady=(0,5))
            amount_input = Entry(self.main_frame, textvariable=self.trans_amount, font=("yu gothic ui",FONT_SIZE), justify=LEFT, width=INPUT_WIDTH)
            amount_input.grid(row=7, column=0, columnspan=2, sticky=W, padx=10, pady=(0,25))
            
            description = Label(self.main_frame, text="Description", font=("yu gothic ui",FONT_SIZE), bg=ROOT_BG_COLOR)
            description.grid(row=8, column=0, sticky=W, padx=5, pady=(0,5))
            description_input = Entry(self.main_frame, textvariable=self.trans_description, font=("yu gothic ui",FONT_SIZE), justify=LEFT, width=INPUT_WIDTH)
            description_input.grid(row=9, column=0, columnspan=2, sticky=W, padx=10, pady=(0,25))
            
            receipt = Label(self.main_frame, text="Upload Receipt Image", font=("yu gothic ui",FONT_SIZE), bg=ROOT_BG_COLOR)
            receipt.grid(row=10, column=0, sticky=W, padx=5, pady=(0,5))
            self.img_label = Label(self.main_frame, bg=ROOT_BG_COLOR)
            self.img_label.grid(row=11, column=0, sticky=W, padx=20, pady=(0,10))
            receipt_btn = Button(self.main_frame, text="Upload Image", font=("yu gothic ui", 11,"bold"), command=self.upload_receipt)
            receipt_btn.grid(row=12, column=0, sticky=W, padx=20, pady=(0,25))
            
            add_btn = Button(self.main_frame, text="Add Claim", font=("yu gothic ui", 11,"bold"), command=self.add_claim)
            add_btn.grid(row=13, column=0, sticky=W, padx=20, pady=(0,25))
            
            # --- Claim Details
            view_frame = Frame(self.root, relief=RIDGE, bg=ROOT_BG_COLOR)
            view_frame.grid(row=0, column=1, sticky=E+W+N+S, padx=(200,0), pady=(10,0))
            
            # --- Create a scrollable listbox to show claims
            self.listbox = Listbox(view_frame, width=80, height=45, selectmode=SINGLE)
            self.listbox.grid(row=0, column=0, sticky=E+W+N+S)
            
            generate_btn = Button(view_frame, text="Generate Report", font=("yu gothic ui", 11,"bold"), command=self.generate_pdf)
            generate_btn.grid(row=1, column=0, sticky=W, padx=200, pady=(25,0))
            
            # --- Scale config
            # self.main_frame.rowconfigure(3, minsize=80)
            
        else:
            self.exits()
    
    # Function to upload the receipt image
    def upload_receipt(self):
        # global receipt_path
        self.receipt_path = filedialog.askopenfilename(
            title="Select Receipt Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        if self.receipt_path:
            # Load and display the image in the GUI
            img = Image.open(self.receipt_path)
            img.thumbnail((150, 150))  # Resize for display
            img = ImageTk.PhotoImage(img)
            self.img_label.config(image=img)
            self.img_label.image = img
        else:
            messagebox.showwarning("Warning", "No image selected.")
    
    # Function to add claim to list
    def add_claim(self):
        # --- Validate that all fields are filled
        if not (self.claimant and self.entry_transaction_date.get() and self.trans_amount.get() and self.trans_description.get() and self.receipt_path):
            messagebox.showerror("Error", "All fields and receipt image must be filled in.")
            return
        elif not self.is_positive_float(self.trans_amount.get()):
            messagebox.showerror("Error", "Amount must be Positive Numbers only.")
            return

        # Store the claim data in the list
        claim = {
            "name": self.claimant,
            "date": self.entry_transaction_date.get(),
            "amount": float(self.trans_amount.get()),
            "description": self.trans_description.get(),
            "receipt": self.receipt_path
        }
        self.claims.append(claim)
        
        # Clear the form for the next entry
        self.trans_amount.set("")
        self.trans_description.set("")
        self.img_label.image = None
        self.main_frame.grid_rowconfigure(11, weight=0)
        # self.main_frame.grid_columnconfigure(0, weight=0)
        self.img_label.grid(row=11, column=0, sticky=W, padx=20, pady=(0,10))
        self.receipt_path = None
        messagebox.showinfo("Success", "Claim added! You can add another claim or generate the report.")
        
        self.view_claims()
    
    # Function to show submitted claims
    def view_claims(self):
        # Populate the listbox with the claims
        for claim in self.claims:
            self.listbox.insert(END, f"Claim Number: {claim['date']} - {claim['name']}")

        def show_claim_details(event):
            selected_index = listbox.curselection()
            if selected_index:
                index = selected_index[0]
                claim = self.claims[index]
                details = f"Name: {claim['name']}\n" \
                          f"Date: {claim['date']}\n" \
                          f"Amount: {claim['amount']}\n" \
                          f"Description: {claim['description']}"
                messagebox.showinfo("Claim Details", details)

        # Bind double-click event to show claim details
        # self.listbox.bind("<Double-1>", show_claim_details)
    
    # Function to generate a consolidated PDF report with a table and total amount
    def generate_pdf(self):
        if not self.claims:
            messagebox.showerror("Error", "No claims to generate a report.")
            return

        # Create a new PDF document
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Claim Summary Report", ln=True, align="C")
        pdf.ln(10)

        # Add table header
        pdf.set_font("Arial", "B", 12)
        pdf.cell(40, 10, "Claimant Name", border=1, align="C")
        pdf.cell(40, 10, "Date", border=1, align="C")
        pdf.cell(30, 10, "Amount (RM)", border=1, align="C")
        pdf.cell(70, 10, "Description", border=1, align="C")
        pdf.ln(10)

        # Initialize total claim amount
        total_amount = 0.0

        # Iterate over each claim to add to table and report
        for claim in self.claims:
            pdf.set_font("Arial", "", 10)
            pdf.cell(40, 10, claim["name"], border=1)
            pdf.cell(40, 10, claim["date"], border=1)
            pdf.cell(30, 10, f"{claim['amount']:.2f}", border=1, align="R")
            pdf.cell(70, 10, claim["description"], border=1)
            pdf.ln(10)

            # Add claim amount to total
            total_amount += claim["amount"]

        # Add total claim amount to the PDF
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Total Claim Amount: RM{total_amount:.2f}", ln=True, align="L")
        pdf.ln(10)

        # Add each claim's receipt image below the table
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Receipts", ln=True, align="C")
        pdf.ln(5)

        for i, claim in enumerate(self.claims, start=1):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"Receipt for Claim #{i}", ln=True)
            pdf.image(claim['receipt'], x=10, y=pdf.get_y() + 5, w=100)
            pdf.ln(60)  # Adjust spacing between receipts

        # Save the PDF file
        filename = f"{REPORT_NUM}.pdf"
        pdf.output(filename)
        messagebox.showinfo("Success", f"PDF Report Generated: {filename}")

        # Clear claims after generating the report
        self.claims.clear()
    
    def is_float_regex(self, value):
        # --- Regular expression to match a float (positive or negative, with decimals)
        float_pattern = r'^-?\d+(\.\d+)?$'
        return bool(re.match(float_pattern, value))
    
    def is_positive_float(self, value):
        try:
            # --- Try converting the string to a float
            result = float(value)
            # --- Check if the float is positive
            return result > 0
        except ValueError:
            # --- If conversion fails, return False
            return False
    
    def root_show(self):
        self.root.deiconify()
        # --- fullscreen with title bar
        self.root.state('zoomed')
    
    def root_hide(self):
        self.root.withdraw()
    
    def exits(self):
        self.root.destroy()

def main_win():
    window = Tk()
    window.iconbitmap(APP_ICON)
    app = App_page(window)
    return window

def main():
    main = main_win()
    main.mainloop()

if __name__ == "__main__":
    main()




