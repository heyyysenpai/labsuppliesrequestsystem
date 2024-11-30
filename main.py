from tkinter import *
from tkinter import ttk, messagebox
import tkinter
import random
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from datetime import datetime
import pandas as pd
from pathlib import Path
import csv
from tkcalendar import DateEntry

last_request_number = 0 # To keep track of last request number
saved_requests = [] # List of saved requests
current_user_role = None  # Will store 'admin' or 'staff'
selected_record_id = None

# Initialize CSV database
def initialize_csv():
    csv_file = Path("labsuppreqsys-data.csv")
    headers = [
        'id', 'request_no', 'status', 'request_date', 'item', 
        'quantity', 'unit', 'catalog_no', 'brand', 'product_link', 
        'iob_allocation', 'ppmp_allocation'
    ]
    
    if not csv_file.exists():
        # Create empty DataFrame with the correct columns
        df = pd.DataFrame(columns=headers)
        # Save it as CSV with empty strings instead of NaN
        df.to_csv(csv_file, index=False, na_rep='')
        print("Created new CSV file")
    
    return csv_file

csv_file = initialize_csv()

def create_main_window():
    # Initialize the main window
    window = Tk()
    window.title("Lab Supplies Request System")
    window.geometry("1350x700")
    window.resizable(False, False)

    # Create header frame with user info and logout button
    header_frame = Frame(window)
    header_frame.pack(fill=X, padx=10, pady=5)

    # Create right-aligned container frame
    right_container = Frame(header_frame)
    right_container.pack(side=RIGHT)

    # Add logout button (first, so it appears on the right)
    def logout():
        response = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if response:
            window.destroy()  # Close the main window
            login_window = create_login_window()  # Create new login window
            login_window.mainloop()

    logout_button = Button(
        right_container, 
        text="Logout", 
        command=logout,
        bg="#ff4d4d",  # Red background
        fg="white",    # White text
        font=("Arial", 10, "bold"),
        padx=10,
        pady=2,
        relief=RAISED,
        cursor="hand2"  # Hand cursor on hover
    )
    logout_button.pack(side=RIGHT, padx=(5, 0))  # Small padding between label and button

    # Add user info label (to the left of logout button)
    user_label = Label(right_container, text=f"Hello, {current_user_role}", font=("Arial", 10))
    user_label.pack(side=RIGHT)

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
            # Read CSV and handle NaN values properly
            df = pd.read_csv(csv_file).astype(str).replace('nan', '')
            
            if not df.empty:
                for _, row in df.iterrows():
                    values = [
                        row['request_no'],
                        row['status'],
                        row['request_date'],
                        row['item'],
                        row['quantity'],
                        row['unit'],
                        row['catalog_no'],
                        row['brand'],
                        row['product_link'],
                        row['iob_allocation'],
                        row['ppmp_allocation']
                    ]
                    # Replace any remaining 'nan' with empty string
                    values = ['' if v == 'nan' else v for v in values]
                    my_tree.insert(parent='', index='end', values=values, tag="orow")
                
                my_tree.tag_configure('orow', background="#EEEEEE")
            
        except Exception as e:
            print(f"Error in refresh_table: {str(e)}")
            messagebox.showerror("Database Error", f"Failed to fetch data: {str(e)}")

    # Generate code
    def generate_code():
        global last_request_number
        last_request_number += 1
        request_code = f"Request-{last_request_number:03d}"
        placeholderArray[0].set(request_code)

    # Save function
    def save():
        global selected_record_id
        request_data = [var.get() for var in placeholderArray]
        
        # For staff users, we only need to check if any field other than request_no is filled
        if current_user_role == "staff":
            # Exclude request_no (index 0) from the check
            other_fields = request_data[1:]
            if not any(other_fields):
                messagebox.showwarning("Input Error", "Please select a row to update or fill in the form for a new entry.")
                return
            
            # Check if all required fields except request_no are filled
            if not all(other_fields):
                messagebox.showwarning("Input Error", "Please fill in all fields except Request No.")
                return
        else:
            # For non-staff users, keep original validation
            if not any(request_data):
                messagebox.showwarning("Input Error", "Please select a row to update or fill in the form for a new entry.")
                return
            
            if not all(request_data):
                messagebox.showwarning("Input Error", "Please fill in all fields.")
                return
        
        data = {
            'request_no': request_data[0],
            'status': request_data[1],
            'request_date': request_data[2],
            'item': request_data[3],
            'quantity': request_data[4],
            'unit': request_data[5],
            'catalog_no': request_data[6],
            'brand': request_data[7],
            'product_link': request_data[8],
            'iob_allocation': request_data[9],
            'ppmp_allocation': request_data[10]
        }
        
        try:
            df = pd.read_csv(csv_file)
            
            # Check if we're updating an existing record
            if selected_record_id is not None:
                # Update existing record using the ID
                df.loc[df['id'] == selected_record_id, list(data.keys())] = list(data.values())
            else:
                # Add new record (this part shouldn't be reached when updating)
                new_id = len(df) + 1 if not df.empty else 1
                new_row = pd.DataFrame([{'id': new_id, **data}])
                df = pd.concat([df, new_row], ignore_index=True)
            
            # Save changes
            df.to_csv(csv_file, index=False)
            messagebox.showinfo("Success", "Record saved successfully")
            
            # Reset selection and refresh table
            selected_record_id = None
            refresh_table()
            
            # Clear fields after saving based on user role
            if current_user_role == 'admin':
                # Clear all fields for admin
                for placeholder in placeholderArray:
                    placeholder.set("")
            else:
                # For staff:
                # Clear all fields including Request No.
                for i in range(len(placeholderArray)):
                    placeholderArray[i].set("")
                
                # Re-enable Request Date field for staff
                entry_widgets[2].config(state='normal')
                
                # Reset field states
                for i, widget in enumerate(entry_widgets):
                    if i in [0, 1]:  # REQUEST NO. and STATUS
                        widget.config(state='readonly')
                    else:
                        widget.config(state='normal')
            
            # Reset buttons
            select_button.config(text="SELECT")
            save_button.config(state='disabled')
            clear_button.config(state='disabled')
            
        except Exception as e:
            print(f"Save error: {str(e)}")
            messagebox.showerror("Error", f"Failed to save: {str(e)}")

    # Delete function
    def delete():
        selected_items = my_tree.selection()
        
        if not selected_items:
            messagebox.showwarning("Selection Error", "Please select at least one item to delete.")
            return
        
        if current_user_role == 'staff':
            # Ask for confirmation
            confirm = messagebox.askyesno("Confirm", "Do you want to request deletion for the selected items?")
            
            if confirm:
                try:
                    # Read CSV
                    df = pd.read_csv(csv_file)
                    
                    # Update status for selected items
                    for item in selected_items:
                        values = my_tree.item(item)['values']
                        request_no = str(values[0])
                        item_name = str(values[3])
                        
                        # Create a more specific mask for matching
                        if request_no == '' or request_no == 'nan':
                            # If no request number, match both item name and ensure request_no is empty
                            mask = (df['item'] == item_name) & (df['request_no'].isna() | (df['request_no'] == ''))
                        else:
                            # If there's a request number, use that for exact matching
                            mask = df['request_no'] == request_no
                        
                        # Update status only for the exact matching row
                        if mask.any():
                            df.loc[mask, 'status'] = 'To be Deleted'
                    
                    # Save changes
                    df.to_csv(csv_file, index=False)
                    
                    # Clear selection and form
                    my_tree.selection_remove(selected_items)
                    for placeholder in placeholderArray:
                        placeholder.set("")
                    
                    # Reset all Manage buttons
                    select_button.config(text="SELECT")
                    save_button.config(state='disabled')
                    clear_button.config(state='disabled')
                    delete_button.config(state='normal')
                    
                    # Re-enable appropriate fields for staff
                    for i, widget in enumerate(entry_widgets):
                        if i in [0, 1]:  # REQUEST NO. and STATUS
                            widget.config(state='readonly')
                        else:
                            widget.config(state='normal')
                    
                    # Re-enable ADD+ button
                    for btn in manage_frame.winfo_children():
                        if btn['text'] == 'ADD+':
                            btn.config(state='normal')
                    
                    # Refresh table
                    refresh_table()
                    
                    # Show success message
                    window.after(100, lambda: messagebox.showinfo("Success", 
                        "Your deletion request has been submitted successfully!"))
                    
                except Exception as e:
                    print(f"Error in delete: {str(e)}")
                    messagebox.showerror("Error", "Could not process deletion request.")
    
        else:  # Admin user
            # Admin delete code remains the same
            response = messagebox.askyesno("Delete", "Are you sure you want to delete the selected items?")
            if response:
                df = pd.read_csv(csv_file)
                df = df.fillna('')
                
                for item in selected_items:
                    values = my_tree.item(item)['values']
                    request_no = str(values[0])
                    item_name = str(values[3])
                    
                    if request_no == '' or request_no == 'nan':
                        df = df[df['item'] != item_name]
                    else:
                        df = df[df['request_no'] != request_no]
                
                df.to_csv(csv_file, index=False)
                refresh_table()
                my_tree.selection_remove(selected_items)
                for placeholder in placeholderArray:
                    placeholder.set("")
                messagebox.showinfo("Success", "Selected items deleted successfully.")

    # Select function
    def select():
        global placeholderArray, selected_record_id
        selected_item = my_tree.selection()
        
        if select_button['text'] == "UNSELECT":
            my_tree.selection_remove(my_tree.selection())
            select_button.config(text="SELECT")
            save_button.config(state='disabled')
            clear_button.config(state='disabled')
            selected_record_id = None
            
            # Re-enable delete button when unselecting
            if current_user_role == 'staff':
                delete_button.config(state='normal')
            
            # Empty out all fields in the form
            for placeholder in placeholderArray:
                placeholder.set("")
            
            # Reset Status to empty as well
            placeholderArray[1].set("")
            
            # Re-enable all appropriate fields for staff
            if current_user_role == 'staff':
                # Enable all fields except REQUEST NO. and STATUS
                for i, widget in enumerate(entry_widgets):
                    if i in [0, 1]:  # REQUEST NO. and STATUS
                        widget.config(state='readonly')
                    else:
                        widget.config(state='normal')
                
                # Re-enable buttons
                for btn in manage_frame.winfo_children():
                    if btn['text'] in ['ADD+']:
                        btn.config(state='normal')
            else:
                # For admin, keep Request Date disabled
                entry_widgets[2].config(state='disabled')
            
            return
        
        if selected_item:
            save_button.config(state='normal')
            clear_button.config(state='normal')
            values = my_tree.item(selected_item[0])['values']
            
            try:
                df = pd.read_csv(csv_file)
                request_no = values[0] if values[0] != 'nan' else ''
                
                if request_no == '':
                    record = df[df['request_no'].isna() | (df['request_no'] == '')].iloc[0]
                else:
                    record = df[df['request_no'] == request_no].iloc[0]
                
                selected_record_id = record['id']
                
                # Check status for staff user
                if current_user_role == 'staff':
                    status = values[1]  # Status is the second column
                    if status == 'To be Deleted':
                        delete_button.config(state='disabled')
                    else:
                        delete_button.config(state='normal')
                
                # Rest of the existing select code...
                for i, value in enumerate(values):
                    if value is not None:
                        value_str = '' if pd.isna(value) or str(value).lower() == 'nan' else str(value)
                        placeholderArray[i].set(value_str)
                
                select_button.config(text="UNSELECT")
                
                # Always disable Request Date when an item is selected
                entry_widgets[2].config(state='disabled')
                
                if current_user_role == 'staff':
                    # Get current status
                    status = placeholderArray[1].get()
                    
                    # If status is 'Done' or 'To be Deleted', disable everything
                    if status in ['Done', 'To be Deleted']:
                        # Disable all entry fields
                        for widget in entry_widgets:
                            widget.config(state='readonly')
                        # Disable buttons except SELECT
                        for btn in manage_frame.winfo_children():
                            if btn['text'] in ['ADD+', 'SAVE', 'CLEAR']:
                                btn.config(state='disabled')
                    else:
                        # Enable appropriate fields for staff
                        for i, widget in enumerate(entry_widgets):
                            if i in [0, 1]:  # REQUEST NO. and STATUS
                                widget.config(state='readonly')
                            elif i == 2:  # REQUEST DATE
                                widget.config(state='disabled')
                            else:
                                widget.config(state='normal')
                        # Enable buttons
                        for btn in manage_frame.winfo_children():
                            if btn['text'] in ['ADD+', 'SAVE', 'CLEAR']:
                                btn.config(state='normal')

            except Exception as e:
                print(f"Select error: {str(e)}")
                messagebox.showerror("Error", "Failed to get record details")
        else:
            messagebox.showwarning("Selection Error", "Please select an item first.")

    # Clear function
    def clear():
        if current_user_role == 'admin':
            # Admin can only clear REQUEST NO. and STATUS
            placeholderArray[0].set("")  # Clear REQUEST NO.
            placeholderArray[1].set("")  # Clear STATUS
        else:
            # Staff can clear everything except REQUEST NO., STATUS, and REQUEST DATE
            # Save the current request date
            current_date = placeholderArray[2].get()
            
            # Clear fields from index 3 onwards (skipping REQUEST NO., STATUS, and REQUEST DATE)
            for i in range(3, len(placeholderArray)):
                placeholderArray[i].set("")
            
            # Restore the request date
            placeholderArray[2].set(current_date)
        
        # Disable clear button after clearing
        clear_button.config(state='disabled')

    # Export function
    def export():
        selected_items = my_tree.selection()
        if not selected_items:
            messagebox.showinfo("Export", "No data selected for export.")
            return
        
        try:
            # Prepare a list to hold the values of selected rows
            all_values = []
            columns = ["Request No.", "Status", "Request Date", "Item", "Quantity", "Unit", 
                       "Catalog No.", "Brand", "Product Link", "IOB Allocation", "PPMP Allocation"]
            
            # Collect values from all selected items
            for item in selected_items:
                values = list(my_tree.item(item)['values'])  # Convert tuple to list
                all_values.append(values)
            
            # Create DataFrame with the selected rows
            df = pd.DataFrame(all_values, columns=columns)
            
            # Generate Excel filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"request_export_{timestamp}.xlsx"
            
            # Export to Excel with error handling
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Request Details')
                
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    # Add new function
    def add_new():
        if current_user_role != 'staff':
            messagebox.showwarning("Access Denied", "Only staff members can add new records.")
            return

        request_data = [var.get() for var in placeholderArray]
        
        if request_data[0]:  # REQUEST NO. is at index 0
            messagebox.showwarning("Input Error", "REQUEST NO. must be empty for new records.")
            return
        
        if not all(request_data[2:]):  # Skip REQUEST NO. and STATUS
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        
        placeholderArray[1].set("Pending")  # Set STATUS to Pending
        
        try:
            df = pd.read_csv(csv_file)
            
            new_id = len(df) + 1 if not df.empty else 1
            data = {
                'id': new_id,
                'request_no': '',  # Explicitly set as empty string
                'status': 'Pending',
                'request_date': request_data[2],
                'item': request_data[3],
                'quantity': request_data[4],
                'unit': request_data[5],
                'catalog_no': request_data[6],
                'brand': request_data[7],
                'product_link': request_data[8],
                'iob_allocation': request_data[9],
                'ppmp_allocation': request_data[10]
            }
            
            # Create new DataFrame row and ensure no NaN values
            new_row = pd.DataFrame([data])
            new_row = new_row.fillna('')  # Replace any NaN values with empty strings
            
            # Concatenate and ensure no NaN values in entire DataFrame
            df = pd.concat([df, new_row], ignore_index=True)
            df = df.fillna('')  # Replace any NaN values with empty strings
            
            # Save to CSV with empty strings instead of NaN
            df.to_csv(csv_file, index=False, na_rep='')
            
            messagebox.showinfo("Success", "Record added successfully")
            clear()
            refresh_table()
            
        except Exception as e:
            print(f"Add error: {str(e)}")
            messagebox.showerror("Error", f"Failed to add record: {str(e)}")

    # Create the main frame
    frame = Frame(window, bg="#4169e1")
    frame.pack(fill=BOTH, expand=True)

    # Button color
    btnColor = "#36454F"

    # Create the manage frame
    def create_manage_frame():
        global manage_frame
        manage_frame = LabelFrame(frame, text="Manage", borderwidth=5)
        manage_frame.grid(row=0, column=0, sticky="w", padx=10, pady=20)

        buttons = [
            ("ADD+", add_new),
            ("SAVE", save),
            ("DELETE", delete),
            ("SELECT", select),
            ("CLEAR", clear),
            ("EXPORT", export)
        ]

        # Store button references globally
        global select_button, save_button, clear_button, delete_button
        
        for col, (text, command) in enumerate(buttons):
            btn = Button(manage_frame, text=text, width=10, borderwidth=3, 
                        bg=btnColor, fg='white', command=command)
            
            # Store references to buttons
            if text == "SELECT":
                select_button = btn
            elif text == "SAVE":
                save_button = btn
                save_button.config(state='disabled')
            elif text == "CLEAR":
                clear_button = btn
                clear_button.config(state='disabled')
            elif text == "DELETE":
                delete_button = btn
            
            # Disable certain buttons for staff
            if current_user_role == 'staff' and text in ['EXPORT']:
                btn['state'] = 'disabled'
            
            btn.grid(row=0, column=col, padx=5, pady=5)

    create_manage_frame()
        
    # Create the entries frame
    def create_entries_frame():
        global entry_widgets
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
                elif i == 2:  # REQUEST DATE - Always readonly for admin
                    widget = DateEntry(entries_frame, width=47, textvariable=placeholderArray[i], 
                                     date_pattern='yyyy-mm-dd', state='disabled')  # Changed to disabled
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
                elif i == 2:  # REQUEST DATE
                    widget = DateEntry(entries_frame, width=47, textvariable=placeholderArray[i], 
                                     date_pattern='yyyy-mm-dd')
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
                df = pd.read_csv("labsuppreqsys-data.csv")
                data_to_display = df.values.tolist()
                
                if not search_text:
                    # Display all data when search is empty
                    for row in data_to_display:
                        values = [
                            row[0],
                            row[1],
                            row[2],
                            row[3],
                            row[4],
                            row[5],
                            row[6],
                            row[7],
                            row[8],
                            row[9],
                            row[10]
                        ]
                        my_tree.insert('', 'end', values=values, tag="orow")
                else:
                    # Filter and display matching rows
                    for row in data_to_display:
                        row_values = [str(value).lower() for value in row]
                        if any(search_text in value for value in row_values):
                            values = [
                                row[0],
                                row[1],
                                row[2],
                                row[3],
                                row[4],
                                row[5],
                                row[6],
                                row[7],
                                row[8],
                                row[9],
                                row[10]
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

