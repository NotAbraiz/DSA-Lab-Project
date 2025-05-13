import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from cashier_employee import CashierEmployee

class CashierAdmin:
    """Admin interface for managing cashiers and counters"""
    
    def __init__(self, app, db, counter_db):
        self.app = app
        self.db = db
        self.counter_db = counter_db
        self.frame = None
        self.counters_table = None
        self.current_time_label = None
        self.transactions_table = None
        self.form_entries = {}

    def show(self, parent):
        """Show the admin interface"""
        self.create_main_frame(parent)
        self.create_admin_interface()

    def hide(self):
        """Hide the admin interface"""
        if self.frame:
            self.frame.pack_forget()

    def create_main_frame(self, parent):
        """Create the main container frame"""
        self.frame = ttk.Frame(parent, style="Cashier.Main.TFrame")
        self.frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.frame.grid_rowconfigure(0, weight=0)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

    def create_admin_interface(self):
        """Create admin view for managing counters"""
        self.create_header()
        self.create_counters_table()
        self.create_admin_buttons()
        self.update_time()
        self.load_counters()

    def create_header(self):
        """Create header with title and time"""
        header_frame = ttk.Frame(self.frame, style="Cashier.Main.TFrame")
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(header_frame, 
                 text="CASHIER COUNTER MANAGEMENT", 
                 style="Cashier.Label.TLabel",
                 font=('Segoe UI', 12, 'bold')).pack(side='left', padx=(0, 20))

        self.current_time_label = ttk.Label(header_frame, 
                                          style="Cashier.Label.TLabel")
        self.current_time_label.pack(side='right')

    def update_time(self):
        """Update the current time display"""
        now = datetime.now()
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        self.current_time_label.config(text=time_str)
        self.frame.after(1000, self.update_time)

    def create_counters_table(self):
        """Create table to display counters information"""
        table_frame = ttk.Frame(self.frame, style="Cashier.Main.TFrame")
        table_frame.grid(row=1, column=0, sticky='nsew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Define columns with relative widths that will adjust
        self.counters_table = ttk.Treeview(
            table_frame,
            columns=("ID", "Cashier Name", "Cashier ID", "Password", "Device ID", "Status", "Created At"),
            show='headings',
            selectmode='browse',
            style="Custom.Treeview"
        )
        
        # Configure columns with relative weights
        columns = {
            "ID": {"text": "ID", "width": 50, "anchor": 'center', "stretch": False},
            "Cashier Name": {"text": "Cashier Name", "width": 150, "anchor": 'w', "stretch": True},
            "Cashier ID": {"text": "Cashier ID", "width": 80, "anchor": 'center', "stretch": False},
            "Password": {"text": "Password", "width": 100, "anchor": 'center', "stretch": False},
            "Device ID": {"text": "Device ID", "width": 120, "anchor": 'center', "stretch": False},
            "Status": {"text": "Status", "width": 100, "anchor": 'center', "stretch": False},
            "Created At": {"text": "Created At", "width": 150, "anchor": 'center', "stretch": False}
        }
        
        for col, config in columns.items():
            self.counters_table.heading(col, text=config["text"], anchor=config.get("anchor", 'w'))
            self.counters_table.column(col, width=config["width"], anchor=config.get("anchor", 'w'),
                                     stretch=config.get("stretch", False))
        
        # Add vertical scrollbar only
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.counters_table.yview)
        self.counters_table.configure(yscrollcommand=vsb.set)
        
        # Grid layout
        self.counters_table.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        # Make the table expand with the window
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Bind double click to view counter details
        self.counters_table.bind("<Double-1>", self.show_counter_details)

    def create_admin_buttons(self):
        """Create action buttons for admin"""
        button_frame = ttk.Frame(self.frame, style="Cashier.Main.TFrame")
        button_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        
        ttk.Button(button_frame, 
                text="➕ Add New Counter", 
                style="Cashier.Button.TButton",
                command=self.show_add_counter_dialog).pack(side='left', padx=5)
        
        ttk.Button(button_frame, 
                text="🗑️ Delete Counter", 
                style="Cashier.Button.TButton",
                command=self.delete_counter).pack(side='left', padx=5)
        
        # Removed the View Reports button completely

    def load_counters(self):
        """Load counters from database"""
        # Clear existing data
        for item in self.counters_table.get_children():
            self.counters_table.delete(item)
        
        counters = self.counter_db.get_counters(active_only=False)
        
        # Add to table with masked password
        for counter in counters:
            self.counters_table.insert("", 'end', values=(
                counter['id'],
                counter['cashier_name'],
                counter['cashier_id'],
                "********",  # Mask the password in table view
                counter.get('device_id', 'N/A'),
                counter['status'].capitalize(),
                counter['created_at']
            ))
        
        # Auto-size columns after loading data
        self.auto_size_columns()

    def auto_size_columns(self):
        """Automatically adjust column widths based on content"""
        for col in self.counters_table["columns"]:
            self.counters_table.column(col, width=tk.font.Font().measure(col) + 20)  # Header width
            
            for item in self.counters_table.get_children():
                cell_value = self.counters_table.set(item, col)
                self.counters_table.column(col, width=max(
                    self.counters_table.column(col, "width"),
                    tk.font.Font().measure(cell_value) + 20
                ))

    def show_add_counter_dialog(self):
        """Show dialog to add a new counter"""
        dialog, container = self.create_dialog("Add New Counter", 450, 400)
        
        ttk.Label(container, 
                 text="Add New Counter", 
                 style="Cashier.Dialog.Title.TLabel").pack(pady=(0, 15))
        
        fields = [
            ("Cashier Name", "entry"),
            ("Cashier ID", "entry"),
            ("Password", "entry"),
            ("Device ID", "entry", ""),
            ("Status", "combobox", ["active", "inactive", "maintenance"], "active"),
        ]
        
        self.add_form_fields(container, fields)
        
        # Configure password entry to show asterisks
        self.form_entries["Password"].config(show="*")
        
        btn_frame = ttk.Frame(container, style="Cashier.Dialog.ButtonFrame.TFrame")
        btn_frame.pack(side='bottom', pady=(15, 0))
        
        ttk.Button(btn_frame, 
                  text="Cancel", 
                  style="Cashier.Dialog.Neutral.TButton",
                  command=dialog.destroy).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, 
                  text="Add Counter", 
                  style="Cashier.Dialog.Button.TButton",
                  command=lambda: self.add_counter_action(
                      dialog,
                      self.form_entries["Cashier Name"].get(),
                      self.form_entries["Cashier ID"].get(),
                      self.form_entries["Password"].get(),
                      self.form_entries["Device ID"].get(),
                      self.form_entries["Status"].get()
                  )).pack(side='right', padx=5)

    def add_counter_action(self, dialog, cashier_name, cashier_id, password, device_id, status):
        """Handle adding a new counter"""
        try:
            if not cashier_name or not cashier_id or not password:
                raise ValueError("Cashier name, ID and password are required")
            
            # Validate cashier ID is numeric
            try:
                cashier_id = int(cashier_id)
            except ValueError:
                raise ValueError("Cashier ID must be a number")
            
            # Add to database with plain text password
            counter_id = self.counter_db.add_counter(
                cashier_name=cashier_name,
                cashier_id=cashier_id,
                device_id=device_id if device_id else None,
                password=password,
                status=status
            )
            
            if counter_id:
                # Refresh table
                self.load_counters()
                messagebox.showinfo(
                    "Success", 
                    f"Counter for {cashier_name} added successfully"
                )
                dialog.destroy()
            else:
                raise ValueError("Failed to add counter")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_counter_details(self, event):
        """Show details for selected counter including transaction history"""
        selected = self.counters_table.selection()
        if not selected:
            return
        
        item = self.counters_table.item(selected)
        counter_id = item['values'][0]
        cashier_name = item['values'][1]
        
        # Get counter details from database
        counters = self.counter_db.get_counters(active_only=False)
        counter = next((c for c in counters if c['id'] == counter_id), None)
        
        if not counter:
            messagebox.showerror("Error", "Counter not found")
            return

        # Create dialog window
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"Counter {counter_id} - {cashier_name}")
        dialog.geometry("900x600")
        dialog.resizable(True, True)
        
        # Make dialog modal and stay on top
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Position dialog
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - 450
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - 300
        dialog.geometry(f"+{x}+{y}")
        
        # Create notebook with styling that matches inventory buttons
        style = ttk.Style()
        
        # Configure notebook style
        style.configure("Cashier.TNotebook", 
                    background="#f5f7fa",  # Light background matching inventory
                    borderwidth=0)
        
        # Configure tab style to match inventory buttons
        style.configure("Cashier.TNotebook.Tab",
                    font=('Segoe UI', 10, 'bold'),
                    background="#00bcd4",  # Blue color matching inventory buttons
                    foreground="white",    # White text
                    padding=[10, 6],      # Slightly larger padding
                    borderwidth=0,
                    focuscolor="#f5f7fa")  # No focus color
        
        # Configure tab states to match button hover effects
        style.map("Cashier.TNotebook.Tab",
                background=[("selected", "#0097a7"),  # Darker blue when selected (active)
                            ("active", "#00bcd4")],    # Regular blue when hovered
                foreground=[("selected", "white"),     # Keep white text
                            ("active", "white")],
                relief=[("selected", "flat"),          # Flat appearance
                        ("!selected", "flat")])
        
        notebook = ttk.Notebook(dialog, style="Cashier.TNotebook")
        notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Counter Info Tab
        info_tab = ttk.Frame(notebook, style="Cashier.Main.TFrame")
        notebook.add(info_tab, text="Counter Information")
        self.create_counter_info_tab(info_tab, counter)
        
        # Transactions Tab
        transactions_tab = ttk.Frame(notebook, style="Cashier.Main.TFrame")
        notebook.add(transactions_tab, text="Transaction History")
        self.create_transactions_tab(transactions_tab, counter_id)
        
        # Button frame at bottom
        btn_frame = ttk.Frame(dialog, style="Cashier.Main.TFrame")
        btn_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(btn_frame, 
                text="Close", 
                style="Cashier.Button.TButton",
                command=dialog.destroy).pack(side='right', padx=5)
    
    def create_counter_info_tab(self, parent, counter):
        """Create the counter information tab"""
        # Info frame
        info_frame = ttk.Frame(parent, style="Cashier.Main.TFrame")
        info_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Display counter info
        ttk.Label(info_frame, 
                text=f"Counter ID: {counter['id']}", 
                style="Cashier.Dialog.Info.TLabel",
                font=('Segoe UI', 12)).pack(anchor='w', pady=5)
        
        ttk.Label(info_frame, 
                text=f"Cashier Name: {counter['cashier_name']}", 
                style="Cashier.Dialog.Info.TLabel").pack(anchor='w', pady=5)
        
        ttk.Label(info_frame, 
                text=f"Cashier ID: {counter['cashier_id']}", 
                style="Cashier.Dialog.Info.TLabel").pack(anchor='w', pady=5)
        
        ttk.Label(info_frame, 
                text=f"Password: {counter['password']}", 
                style="Cashier.Dialog.Info.TLabel").pack(anchor='w', pady=5)
        
        ttk.Label(info_frame, 
                text=f"Device ID: {counter.get('device_id', 'N/A')}", 
                style="Cashier.Dialog.Info.TLabel").pack(anchor='w', pady=5)
        
        ttk.Label(info_frame, 
                text=f"Status: {counter['status'].capitalize()}", 
                style="Cashier.Dialog.Info.TLabel").pack(anchor='w', pady=5)
        
        ttk.Label(info_frame, 
                text=f"Created At: {counter['created_at']}", 
                style="Cashier.Dialog.Info.TLabel").pack(anchor='w', pady=5)
        
        # Action buttons
        btn_frame = ttk.Frame(info_frame, style="Cashier.Main.TFrame")
        btn_frame.pack(side='bottom', pady=(20, 0))
        
        ttk.Button(btn_frame, 
                text="Edit Counter", 
                style="Cashier.Button.TButton",
                command=lambda: self.edit_counter_action(counter)).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, 
                text="Reset Password", 
                style="Cashier.Button.TButton",
                command=lambda: self.reset_password_action(counter['id'])).pack(side='left', padx=5)

    def reset_password_action(self, counter_id):
        """Handle password reset for a counter"""
        # Create dialog to get new password
        dialog, container = self.create_dialog("Reset Password", 350, 200)
        
        ttk.Label(container, 
                 text="Enter New Password:", 
                 style="Cashier.Dialog.Label.TLabel").pack(pady=10)
        
        password_entry = ttk.Entry(container, 
                                 style="Cashier.Dialog.Entry.TEntry",
                                 show="")
        password_entry.pack(fill='x', padx=20, pady=5)
        
        btn_frame = ttk.Frame(container, style="Cashier.Dialog.ButtonFrame.TFrame")
        btn_frame.pack(side='bottom', pady=(15, 0))
        
        ttk.Button(btn_frame, 
                  text="Cancel", 
                  style="Cashier.Dialog.Neutral.TButton",
                  command=dialog.destroy).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, 
                  text="Set Password", 
                  style="Cashier.Dialog.Button.TButton",
                  command=lambda: self.save_new_password(
                      dialog,
                      counter_id,
                      password_entry.get()
                  )).pack(side='right', padx=5)

    def save_new_password(self, dialog, counter_id, new_password):
        """Save the new password to database"""
        if not new_password:
            messagebox.showerror("Error", "Password cannot be empty")
            return
            
        # Update in database with plain text password
        success = self.counter_db.update_counter(counter_id, {"password": new_password})
        
        if success:
            # Refresh tables
            self.load_counters()
            messagebox.showinfo("Success", "Password updated successfully")
            dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to update password")

    def edit_counter_action(self, counter):
        """Handle editing counter details"""
        # Create edit dialog
        dialog, container = self.create_dialog(f"Edit Counter {counter['id']}", 450, 300)
        
        ttk.Label(container, 
                 text=f"Edit Counter {counter['id']}", 
                 style="Cashier.Dialog.Title.TLabel").pack(pady=(0, 15))
        
        fields = [
            ("Cashier Name", "entry", counter['cashier_name']),
            ("Cashier ID", "entry", counter['cashier_id']),
            ("Device ID", "entry", counter.get('device_id', '')),
            ("Status", "combobox", ["active", "inactive", "maintenance"], counter['status'])
        ]
        
        self.add_form_fields(container, fields)
        
        btn_frame = ttk.Frame(container, style="Cashier.Dialog.ButtonFrame.TFrame")
        btn_frame.pack(side='bottom', pady=(15, 0))
        
        ttk.Button(btn_frame, 
                  text="Cancel", 
                  style="Cashier.Dialog.Neutral.TButton",
                  command=dialog.destroy).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, 
                  text="Save Changes", 
                  style="Cashier.Dialog.Button.TButton",
                  command=lambda: self.save_counter_changes(
                      dialog,
                      counter['id'],
                      self.form_entries["Cashier Name"].get(),
                      self.form_entries["Cashier ID"].get(),
                      self.form_entries["Device ID"].get(),
                      self.form_entries["Status"].get()
                  )).pack(side='right', padx=5)

    def save_counter_changes(self, dialog, counter_id, cashier_name, cashier_id, device_id, status):
        """Save changes to counter details"""
        try:
            if not cashier_name or not cashier_id:
                raise ValueError("Cashier name and ID are required")
            
            # Validate cashier ID is numeric
            try:
                cashier_id = int(cashier_id)
            except ValueError:
                raise ValueError("Cashier ID must be a number")
            
            updates = {
                "cashier_name": cashier_name,
                "cashier_id": cashier_id,
                "device_id": device_id if device_id else None,
                "status": status
            }
            
            # Update in database
            success = self.counter_db.update_counter(counter_id, updates)
            
            if success:
                # Refresh tables
                self.load_counters()
                messagebox.showinfo("Success", "Counter updated successfully")
                dialog.destroy()
            else:
                raise ValueError("Failed to update counter")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_transactions_tab(self, parent, counter_id):
        """Create the transaction history tab for a counter"""
        # Create frame for transactions
        transactions_frame = ttk.Frame(parent, style="Cashier.Main.TFrame")
        transactions_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create transactions table
        self.transactions_table = ttk.Treeview(
            transactions_frame,
            columns=("ID", "Receipt ID", "Customer", "Amount", "Payment Method", "Time"),
            show='headings',
            style="Custom.Treeview"
        )
        
        # Configure columns
        columns = {
            "ID": {"text": "ID", "width": 50, "anchor": 'center'},
            "Receipt ID": {"text": "Receipt ID", "width": 120, "anchor": 'center'},
            "Customer": {"text": "Customer", "width": 150, "anchor": 'w'},
            "Amount": {"text": "Amount", "width": 100, "anchor": 'e'},
            "Payment Method": {"text": "Payment", "width": 100, "anchor": 'center'},
            "Time": {"text": "Time", "width": 150, "anchor": 'center'}
        }
        
        for col, config in columns.items():
            self.transactions_table.heading(col, text=config["text"], anchor=config.get("anchor", 'w'))
            self.transactions_table.column(col, width=config["width"], anchor=config.get("anchor", 'w'))
        
        # Add vertical scrollbar only (removed horizontal scrollbar)
        vsb = ttk.Scrollbar(transactions_frame, orient="vertical", command=self.transactions_table.yview)
        self.transactions_table.configure(yscrollcommand=vsb.set)
        
        # Grid layout (removed hsb grid)
        self.transactions_table.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        # Make the table expand
        transactions_frame.grid_rowconfigure(0, weight=1)
        transactions_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click event to show receipt
        self.transactions_table.bind("<Double-1>", self.show_transaction_receipt)
        
        # Load transactions
        self.load_transactions(counter_id)

    def show_transaction_receipt(self, event):
        """Show receipt for selected transaction using CashierEmployee's method"""
        selected = self.transactions_table.selection()
        if not selected:
            return
            
        # Get transaction data
        item = self.transactions_table.item(selected[0])
        transaction_id = item['values'][0]  # First column is ID
        
        try:
            # Get complete transaction details
            transaction_data = self.counter_db.get_sale_details(transaction_id)
            if not transaction_data:
                raise Exception("Transaction not found")
            
            # Prepare receipt data
            receipt_data = {
                'receipt_id': transaction_data['receipt_id'],
                'date_time': transaction_data['sale_time'],
                'cashier': transaction_data['cashier_name'],
                'customer': transaction_data['customer_name'] or "Walk-in Customer",
                'items': [
                    {
                        'name': item['product_name'],
                        'quantity': item['quantity'],
                        'price': item['unit_price'],
                        'total': item['total_price']
                    }
                    for item in transaction_data['items']
                ],
                'total': transaction_data['total_amount'],
                'payment_method': transaction_data['payment_method'] or 'cash'
            }
            
            # Create a temporary CashierEmployee instance to use its show_receipt method
            temp_cashier = CashierEmployee(self.app, self.db, self.counter_db)
            temp_cashier.show_receipt(receipt_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load receipt: {str(e)}")

    def load_transactions(self, counter_id):
        """Load transactions for a specific counter"""
        # Clear existing data
        for item in self.transactions_table.get_children():
            self.transactions_table.delete(item)
        
        # Get transactions from database
        transactions = self.counter_db.get_transactions_for_counter(counter_id)
        
        # Add to table
        for trans in transactions:
            self.transactions_table.insert("", 'end', values=(
                trans['id'],
                trans['receipt_id'],
                trans.get('customer_name', 'N/A'),
                f"PKR {trans['total_amount']:,.2f}",
                trans.get('payment_method', 'cash').title(),
                trans['sale_time']
            ))

    def delete_counter(self):
        """Delete the selected counter"""
        selected = self.counters_table.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a counter to delete")
            return
        
        item = self.counters_table.item(selected)
        counter_id = item['values'][0]
        cashier_name = item['values'][1]
        
        # Confirm deletion
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete counter for {cashier_name}?\n"
            "This will also delete all associated transactions!"
        ):
            return
        
        try:
            # First delete associated sales and items
            cursor = self.counter_db.conn.cursor()
            
            # Get all sale IDs for this counter
            cursor.execute("SELECT id FROM sales WHERE counter_id = ?", (counter_id,))
            sale_ids = [row[0] for row in cursor.fetchall()]
            
            # Delete sale items
            for sale_id in sale_ids:
                cursor.execute("DELETE FROM sale_items WHERE sale_id = ?", (sale_id,))
            
            # Delete sales
            cursor.execute("DELETE FROM sales WHERE counter_id = ?", (counter_id,))
            
            # Finally delete the counter
            cursor.execute("DELETE FROM counters WHERE id = ?", (counter_id,))
            
            self.counter_db.conn.commit()
            
            # Refresh the table
            self.load_counters()
            messagebox.showinfo("Success", "Counter deleted successfully")
            
        except Exception as e:
            self.counter_db.conn.rollback()
            messagebox.showerror("Error", f"Failed to delete counter: {str(e)}")


    def add_form_fields(self, parent, fields):
        """Add form fields to a dialog"""
        self.form_entries = {}  # Reset form entries dictionary
        form_frame = ttk.Frame(parent, style='Cashier.Dialog.TFrame')
        form_frame.pack(fill='both', expand=True)
        
        for field in fields:
            row = ttk.Frame(form_frame, style='Cashier.Dialog.TFrame')
            row.pack(fill='x', pady=5)
            
            ttk.Label(row, 
                     text=f"{field[0]}:", 
                     style="Cashier.Dialog.Label.TLabel").pack(side='left')
            
            if field[1] == "entry":
                entry = ttk.Entry(row, style="Cashier.Dialog.Entry.TEntry")
                entry.pack(side='left', fill='x', expand=True)
                if len(field) > 2:
                    entry.insert(0, field[2])
                self.form_entries[field[0]] = entry
            elif field[1] == "combobox":
                combo = ttk.Combobox(row,   
                                   values=field[2], 
                                   style="Cashier.Dialog.Combobox.TCombobox")
                combo.pack(side='left', fill='x', expand=True)
                if len(field) > 3:
                    combo.set(field[3])
                self.form_entries[field[0]] = combo

    def create_dialog(self, title, width=400, height=300):
        """Create a base dialog window"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.resizable(False, False)
        
        # Make dialog modal and stay on top
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(background='#ffffff')
        
        # Center dialog
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - (width // 2)
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")
        
        container = ttk.Frame(dialog, style='Cashier.Dialog.TFrame')
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        return dialog, container