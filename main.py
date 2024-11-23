from tkinter import *
from tkinter import ttk, messagebox
import tkinter
import random

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
        for array in dummydata:
            my_tree.insert(parent='', index='end', iid=array, text="", values=array, tag="orow")
        my_tree.tag_configure('orow', background="#EEEEEE")

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

    # Update function
    def update():
        selected_item = my_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item to update.")
            return
        
        request_data = [var.get() for var in placeholderArray]
        
        if current_user_role == 'staff':
            # Staff can't modify status or request number
            old_values = my_tree.item(selected_item)['values']
            request_data[0] = old_values[0]  # Keep original request number
            request_data[1] = old_values[1]  # Keep original status
        
        if all(request_data):
            for i, item in enumerate(saved_requests):
                if item[0] == my_tree.item(selected_item)['values'][0]:
                    saved_requests[i] = request_data
                    refresh_table()
                    clear()
                    return
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields.")

    # Delete function
    def delete():
        selected_item = my_tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select an item to delete.")
            return
        
        request_no = my_tree.item(selected_item)['values'][0]
        
        if current_user_role == 'staff':
            # Staff deletion requests need admin approval
            response = messagebox.askyesno("Delete Request", 
                "This will mark the item for deletion and require admin approval. Continue?")
            if response:
                # Mark the status as "Pending Deletion"
                for i, item in enumerate(saved_requests):
                    if item[0] == request_no:
                        saved_requests[i][1] = "Pending Deletion"
                        refresh_table()
                        messagebox.showinfo("Success", "Delete request sent to admin")
                        return
        else:
            # Admin can delete directly
            for i, item in enumerate(saved_requests):
                if item[0] == request_no:
                    del saved_requests[i]
                    refresh_table()
                    return

    # Select function
    def select():
        # Get the selected item from the tree
        selected_item = my_tree.selection()
        
        if selected_item:
            # Get all values from the selected row
            values = my_tree.item(selected_item)['values']
            # Fill entry fields with selected values
            for i, var in enumerate(placeholderArray):
                var.set(values[i])
        else:
            messagebox.showwarning("Selection Error", "Please select an item first.")

    # Clear function
    def clear():
        # Clear all entry fields
        for var in placeholderArray:
            var.set("")

    # Export function (placeholder for actual export logic)
    def export():
        messagebox.showinfo("Export", "Export functionality is not implemented yet.")
                        
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
            ("UPDATE", update),
            ("DELETE", delete),
            ("SELECT", select),
            ("FIND", None),  # Placeholder for find functionality
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

        entry_widgets = [
            Entry(entries_frame, width=50, textvariable=placeholderArray[0]),
            ttk.Combobox(entries_frame, width=50, textvariable=placeholderArray[1], values=statusArray),
            Entry(entries_frame, width=50, textvariable=placeholderArray[2]),
            Entry(entries_frame, width=50, textvariable=placeholderArray[3]),
            Entry(entries_frame, width=50, textvariable=placeholderArray[4]),
            Entry(entries_frame, width=50, textvariable=placeholderArray[5]),
            Entry(entries_frame, width=50, textvariable=placeholderArray[6]),
            Entry(entries_frame, width=50, textvariable=placeholderArray[7]),
            Entry(entries_frame, width=50, textvariable=placeholderArray[8]),
            Entry(entries_frame, width=50, textvariable=placeholderArray[9]),
            Entry(entries_frame, width=50, textvariable=placeholderArray[10]),
        ]

        for i, entry in enumerate(entry_widgets):
            entry.grid(row=i, column=1, padx=5, pady=5)
            
            # Disable status and request number fields for staff
            if current_user_role == 'staff' and i in [0, 1]:  # Request No. and Status fields
                entry['state'] = 'disabled'

        # Only show generate code button for admin
        if current_user_role == 'admin':
            Button(entries_frame, text="GENERATE CODE", command=generate_code, 
                   borderwidth=3, bg=btnColor, fg='white').grid(row=0, column=2, padx=5, pady=5)

    create_entries_frame()

    # Create the Treeview
    my_tree = create_treeview()

    # Dummy data for testing
    dummydata = [
        ['Request1', 'Pending', '2023-10-01', 'Item1', '10', ' pcs', 'CAT001', 'BrandA', 'http://example.com', 'IOB1', 'PPMP1'],
        ['Request2', 'Done', '2023-10-02', 'Item2', '5', 'pcs', 'CAT002', 'BrandB', 'http://example.com', 'IOB2', 'PPMP2']
    ]

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
    login_window = Tk()
    login_window.title("Login")
    login_window.geometry("300x200")

    Label(login_window, text="Username").pack(pady=10)
    username_entry = Entry(login_window)
    username_entry.pack(pady=5)

    Label(login_window, text="Password").pack(pady=10)
    password_entry = Entry(login_window, show="*")
    password_entry.pack(pady=5)

    def login():
        username = username_entry.get()
        password = password_entry.get()
        if validate_login(username, password):
            login_window.destroy()  # Close the login window
            create_main_window()  # Open the main application
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    Button(login_window, text="Login", command=login).pack(pady=20)

    login_window.mainloop()

# Start the application with the login window
create_login_window()

