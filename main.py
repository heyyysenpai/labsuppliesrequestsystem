from tkinter import *
from tkinter import ttk, messagebox
import tkinter
import random
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

import os

from supabase import create_client, Client


# After load_dotenv()
print("Supabase URL:", os.environ.get("SUPABASE_URL"))
print("Supabase Key:", os.environ.get("SUPABASE_KEY"))

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise Exception("Supabase credentials not found in environment variables")

supabase: Client = create_client(url, key)

try:
    # Test the connection
    print("Attempting to connect to Supabase...")
    print(f"Table name: labsuppliesrequestsystem")
    response = supabase.table('labsuppliesrequestsystem').select("*").execute()
    print("Raw response:", response)
    print("Response data:", response.data)
    print("Supabase connection successful!")
    print(f"Number of records: {len(response.data)}")
    if response.data:
        print("First record:", response.data[0])
    else:
        print("No records found in the response")
except Exception as e:
    print(f"Supabase connection error: {str(e)}")
    print(f"Error type: {type(e)}")

last_request_number = 0 # To keep track of last request number
saved_requests = [] # List of saved requests
current_user_role = None  # Will store 'admin' or 'staff'


def create_main_window():
# Initialize the main window
    window = tkinter.Tk()
    window.title("Lab Supplies Request System")
    window.geometry("720x640")

    # Create a Treeview with a scrollbar
    def create_treeview():
        tree_frame = Frame(window)
        tree_frame.pack(fill=BOTH, expand=True)

        scrollbar = Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        my_tree = ttk.Treeview(tree_frame, show='headings', height=20, yscrollcommand=scrollbar.set)
        my_tree.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar.config(command=my_tree.yview)

        return my_tree

    # Refresh the Treeview with dummy data
    def refresh_table():
        for data in my_tree.get_children():
            my_tree.delete(data)
        
        try:
            print("\nRefresh Table Debug:")
            print("1. Attempting to fetch data...")
            response = supabase.table('labsuppliesrequestsystem').select(
                'request_no, status, request_date, item, quantity, unit, catalog_no, brand, product_link, iob_allocation, ppmp_allocation'
            ).execute()
            print("2. Response received:", response)
            supabase_data = response.data
            print("3. Data extracted:", supabase_data)
            print(f"4. Number of records: {len(supabase_data)}")
            
            if not supabase_data:
                print("5. No data returned from Supabase")
                return
            
            for row in supabase_data:
                print("6. Processing row:", row)
                values = [
                    row.get('request_no', ''),
                    row.get('status', ''),
                    row.get('request_date', ''),
                    row.get('item', ''),
                    row.get('quantity', ''),
                    row.get('unit', ''),
                    row.get('catalog_no', ''),
                    row.get('brand', ''),
                    row.get('product_link', ''),
                    row.get('iob_allocation', ''),
                    row.get('ppmp_allocation', '')
                ]
                my_tree.insert(parent='', index='end', values=values, tag="orow")
            
            my_tree.tag_configure('orow', background="#EEEEEE")
        except Exception as e:
            print(f"Error in refresh_table: {str(e)}")
            print(f"Error type: {type(e)}")
            messagebox.showerror("Database Error", f"Failed to fetch data: {str(e)}")

    # Generate code
    def generate_code():
        global last_request_number
        last_request_number += 1
        request_code = f"Request-{last_request_number:03d}"
        placeholderArray[0].set(request_code)

    # Save function
    def save(): 
        # Both admin and staff can save
        request_data = [var.get() for var in placeholderArray]
        
        if all(request_data):
            # Set initial status to 'Pending' for staff
            if current_user_role == 'staff':
                request_data[1] = 'Pending'  # Status field
            
            saved_requests.append(request_data)
            refresh_table()
            clear()
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")

    # Delete function
    def delete():
        selected_item = my_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item to delete.")
            return
        
        request_no = my_tree.item(selected_item[0])['values'][0]
        
        if current_user_role == 'staff':
            messagebox.showwarning("Permission Denied", "Staff cannot delete records.")
            return
        
        # Admin workflow - delete directly
        response = messagebox.askyesno("Delete", "Are you sure you want to delete this item?")
        if response:
            try:
                print(f"Attempting to delete request_no: {request_no}")
                
                # Get all records to find the one we want to delete
                get_records = supabase.table('labsuppliesrequestsystem')\
                    .select('*')\
                    .execute()
                
                # Find the record with matching request_no
                record_to_delete = None
                for record in get_records.data:
                    if record['request_no'] == request_no:
                        record_to_delete = record
                        break
                
                if record_to_delete:
                    # Delete using the record's ID
                    result = supabase.table('labsuppliesrequestsystem')\
                        .delete()\
                        .eq('id', record_to_delete['id'])\
                        .execute()
                    
                    print(f"Delete response: {result}")
                    
                    # Remove from treeview and clear form
                    my_tree.delete(selected_item)
                    clear()
                    
                    # Refresh the table to ensure sync with database
                    refresh_table()
                    messagebox.showinfo("Success", "Item deleted successfully")
                else:
                    messagebox.showerror("Error", "Record not found in database")
                    
            except Exception as e:
                print(f"Delete error: {str(e)}")
                print(f"Error type: {type(e)}")
                messagebox.showerror("Error", f"Failed to delete: {str(e)}")

    # Select function
    def select():
        global placeholderArray
        # Get the selected item from the tree
        selected_item = my_tree.selection()
        
        if selected_item:
            # Get all values from the selected row
            values = my_tree.item(selected_item[0])['values']  # Add [0] to get first selected item
            # Fill entry fields with selected values
            for i, value in enumerate(values):
                if value is not None:  # Check if value exists
                    placeholderArray[i].set(str(value))  # Convert to string
        else:
            messagebox.showwarning("Selection Error", "Please select an item first.")

    # Clear function
    def clear():
        if current_user_role == 'admin':
            # Admin can only clear REQUEST NO. and STATUS
            placeholderArray[0].set("")  # Clear REQUEST NO.
            placeholderArray[1].set("")  # Clear STATUS
        else:
            # Staff can clear everything except REQUEST NO. and STATUS
            for i in range(2, len(placeholderArray)):
                placeholderArray[i].set("")

    # Export function
    def export():
        selected_item = my_tree.selection()
        if not selected_item:
            messagebox.showinfo("Export", "No data")
            return
        
        try:
            # Get selected values and columns
            values = list(my_tree.item(selected_item[0])['values'])  # Convert tuple to list
            columns = ["Request No.", "Status", "Request Date", "Item", "Quantity", "Unit", 
                      "Catalog No.", "Brand", "Product Link", "IOB Allocation", "PPMP Allocation"]
            
            # Create DataFrame with the selected row
            df = pd.DataFrame([values], columns=columns)
            
            # Generate Excel filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"request_export_{timestamp}.xlsx"
            
            # Export to Excel with error handling
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Request Details')
                
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    # Create the main frame
    frame = Frame(window, bg="#4169e1")
    frame.pack(fill=BOTH, expand=True)

    # Button color
    btnColor = "#36454F"

    # Create the manage frame
    def create_manage_frame():
        manage_frame = LabelFrame(frame, text="Manage", borderwidth=5)
        manage_frame.grid(row=0, column=0, sticky="w", padx=10, pady=20)

        buttons = [
            ("SAVE", save),
            ("DELETE", delete),
            ("SELECT", select),
            ("CLEAR", clear),
            ("EXPORT", export)
        ]

        for col, (text, command) in enumerate(buttons):
            btn = Button(manage_frame, text=text, width=10, borderwidth=3, 
                        bg=btnColor, fg='white', command=command)
            
            # Disable certain buttons for staff
            if current_user_role == 'staff' and text in ['EXPORT']:
                btn['state'] = 'disabled'
            
            btn.grid(row=0, column=col, padx=5, pady=5)

    create_manage_frame()
        
    # Create the entries frame
    def create_entries_frame():
        entries_frame = LabelFrame(frame, text="Form", borderwidth=5)
        entries_frame.grid(row=1, column=0, sticky="w", padx=10, pady=20)

        labels = [
            "REQUEST NO.", "STATUS", "REQUEST DATE", "ITEM", "QUANTITY",
            "UNIT", "CATALOG NO.", "BRAND", "PRODUCT LINK", "IOB ALLOCATION", "PPMP ALLOCATION"
        ]

        for i, label in enumerate(labels):
            Label(entries_frame, text=label, anchor="e", width=15).grid(row=i, column=0, padx=10)

        # Entry fields
        global placeholderArray
        placeholderArray = [StringVar() for _ in range(11)]
        statusArray = ['Pending', 'Done']

        if current_user_role == 'admin':
            # Admin: Only REQUEST NO. and STATUS are editable
            entry_widgets = []
            for i in range(11):
                if i == 0:  # REQUEST NO.
                    widget = Entry(entries_frame, width=50, textvariable=placeholderArray[i])
                elif i == 1:  # STATUS
                    widget = ttk.Combobox(entries_frame, width=50, textvariable=placeholderArray[i], values=statusArray)
                else:  # All other fields
                    widget = Entry(entries_frame, width=50, textvariable=placeholderArray[i], state='readonly')
                entry_widgets.append(widget)
        else:
            # Staff: Everything except REQUEST NO. and STATUS is editable
            entry_widgets = []
            for i in range(11):
                if i == 0:  # REQUEST NO.
                    widget = Entry(entries_frame, width=50, textvariable=placeholderArray[i], state='readonly')
                elif i == 1:  # STATUS
                    widget = ttk.Combobox(entries_frame, width=50, textvariable=placeholderArray[i], state='readonly')
                else:  # All other fields
                    widget = Entry(entries_frame, width=50, textvariable=placeholderArray[i])
                entry_widgets.append(widget)

        for i, entry in enumerate(entry_widgets):
            entry.grid(row=i, column=1, padx=5, pady=5)

        # Only show generate code button for admin
        if current_user_role == 'admin':
            Button(entries_frame, text="GENERATE CODE", command=generate_code, 
                   borderwidth=3, bg=btnColor, fg='white').grid(row=0, column=2, padx=5, pady=5)

    create_entries_frame()

    # Create search frame
    def create_search_frame():
        search_frame = Frame(frame)
        search_frame.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        Label(search_frame, text="Search:", font=("Arial", 10)).pack(side=LEFT, padx=5)
        
        search_var = StringVar()
        search_entry = Entry(search_frame, textvariable=search_var, width=30, font=("Arial", 10))
        search_entry.pack(side=LEFT, padx=5)
        
        def on_search_change(*args):
            search_text = search_var.get().lower().strip()
            
            # Clear the tree
            for item in my_tree.get_children():
                my_tree.delete(item)
            
            try:
                # Fetch fresh data from Supabase
                response = supabase.table('labsuppliesrequestsystem').select(
                    'request_no, status, request_date, item, quantity, unit, catalog_no, brand, product_link, iob_allocation, ppmp_allocation'
                ).execute()
                data_to_display = response.data
                
                if not search_text:
                    # Display all data when search is empty
                    for row in data_to_display:
                        values = [
                            row.get('request_no', ''),
                            row.get('status', ''),
                            row.get('request_date', ''),
                            row.get('item', ''),
                            row.get('quantity', ''),
                            row.get('unit', ''),
                            row.get('catalog_no', ''),
                            row.get('brand', ''),
                            row.get('product_link', ''),
                            row.get('iob_allocation', ''),
                            row.get('ppmp_allocation', '')
                        ]
                        my_tree.insert('', 'end', values=values, tag="orow")
                else:
                    # Filter and display matching rows
                    for row in data_to_display:
                        row_values = [str(value).lower() for value in row.values()]
                        if any(search_text in value for value in row_values):
                            values = [
                                row.get('request_no', ''),
                                row.get('status', ''),
                                row.get('request_date', ''),
                                row.get('item', ''),
                                row.get('quantity', ''),
                                row.get('unit', ''),
                                row.get('catalog_no', ''),
                                row.get('brand', ''),
                                row.get('product_link', ''),
                                row.get('iob_allocation', ''),
                                row.get('ppmp_allocation', '')
                            ]
                            my_tree.insert('', 'end', values=values, tag="orow")
            
                # Maintain row styling
                my_tree.tag_configure('orow', background="#EEEEEE")
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to fetch data: {str(e)}")
        
        search_var.trace('w', on_search_change)

    create_search_frame()

    # Create the Treeview
    my_tree = create_treeview()

    # Set up the columns for the Treeview
    my_tree['columns'] = ("Request No.", "Status", "Request Date", "Item", "Quantity", "Unit", "Catalog No.",
                        "Brand", "Product Link", "IOB Allocation", "PPMP Allocation")
    for col in my_tree['columns']:
        my_tree.heading(col, text=col, anchor=W)
        my_tree.column(col, anchor=W, width=100)

    # Refresh the table to display initial data
    refresh_table()

    # Make the window resizable
    window.resizable(True, True)

    # Start the main loop
    window.mainloop()

    # Function to validate login credentials
def validate_login(username, password):
    # Simple dictionary of users and their roles
    users = {
        "admin": {"password": "admin", "role": "admin"},
        "staff": {"password": "staff", "role": "staff"}
    }
    
    if username in users and users[username]["password"] == password:
        global current_user_role
        current_user_role = users[username]["role"]
        return True
    return False

# Function to create the login window
def create_login_window():
    global current_user_role
    
    def login(event=None):  # Add event parameter with default None
        username = username_entry.get()
        password = password_entry.get()
        
        if validate_login(username, password):
            login_window.destroy()
            create_main_window()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    login_window = Tk()
    login_window.title("Login")
    login_window.geometry("500x300")

    title_label = Label(login_window, text="Lab Supplies Request System",
                       font=("Arial", 12, "bold"))
    title_label.pack(pady=10)

    Label(login_window, text="Username",
          font=("Arial", 10)).pack(pady=5)
    username_entry = Entry(login_window, font=("Arial", 10),
                         width=25)
    username_entry.pack(pady=5)

    Label(login_window, text="Password",
          font=("Arial", 10)).pack(pady=5)
    password_entry = Entry(login_window, show="*", font=("Arial", 10),
                         width=25)
    password_entry.pack(pady=5)

    login_btn = Button(login_window, text="Login",
                      command=login,
                      font=("Arial", 10, "bold"),
                      width=15)
    login_btn.pack(pady=15)

    # Bind Enter key to login function
    login_window.bind('<Return>', login)  # Bind to window
    username_entry.bind('<Return>', login)  # Bind to username entry
    password_entry.bind('<Return>', login)  # Bind to password entry

    # Center the login window
    login_window.update_idletasks()
    width = login_window.winfo_width()
    height = login_window.winfo_height()
    x = (login_window.winfo_screenwidth() // 2) - (width // 2)
    y = (login_window.winfo_screenheight() // 2) - (height // 2)
    login_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    login_window.mainloop()

# Start the application with the login window
create_login_window()

