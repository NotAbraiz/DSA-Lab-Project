import tkinter as tk
from tkinter import ttk, messagebox

class InventorySection:
    """Inventory management section of the application"""
    
    def __init__(self, app, db):
        """Initialize the inventory section"""
        self.app = app
        self.db = db 
        self.frame = None
        self.tree = None
        self.search_entry = None
        self.filter_category = None
        self.filter_company = None
        self.filter_status = None
        self.summary_label = None
        self.form_entries = {}  # To store references to form entry widgets

    # ======================
    # MAIN UI COMPONENTS
    # ======================
    def show(self, parent):
        """Show the inventory section"""
        self.create_main_frame(parent)
        self.create_header()
        self.create_search_filter_card()
        self.create_action_buttons()
        self.create_inventory_table()
        
        # Bind search entry to automatically filter table
        self.search_entry.bind('<KeyRelease>', self.search_items)
        
        # Bind click event to the main frame for deselection
        self.frame.bind("<Button-1>", self.deselect_all)

    def hide(self):
        """Hide the inventory section"""
        if self.frame:
            self.frame.pack_forget()

    def deselect_all(self, event):
        """Deselect all items when clicking outside widgets"""
        widget = event.widget
        # Only deselect if clicking on the frame itself, not its children
        if widget == self.frame:
            if self.tree:
                self.tree.selection_remove(self.tree.selection())

    # ======================
    # UI CREATION METHODS
    # ======================
    def create_main_frame(self, parent):
        """Create the main container frame"""
        self.frame = ttk.Frame(parent, style="Inventory.Main.TFrame")
        self.frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.frame.grid_rowconfigure(0, weight=0)
        self.frame.grid_rowconfigure(1, weight=0)
        self.frame.grid_rowconfigure(2, weight=0)
        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

    def create_header(self):
        """Create the header section with proper padding"""
        header_frame = ttk.Frame(self.frame, style="Inventory.Main.TFrame")
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        ttk.Label(header_frame, 
                 text="INVENTORY MANAGEMENT", 
                 style="Inventory.Label.TLabel",
                 font=('Segoe UI', 12, 'bold')).pack(side='left', padx=(0, 20))

        self.summary_label = ttk.Label(header_frame, 
                                     style="Inventory.Label.TLabel")
        self.summary_label.pack(side='right')
        self.update_summary()

    def update_summary(self):
        """Update the inventory summary label with real data"""
        products = self.db.get_products()
        total_items = len(products)
        total_value = sum(p['worth'] for p in products)
        low_stock = sum(1 for p in products if p['status'] == "Low Stock")
        out_of_stock = sum(1 for p in products if p['status'] == "Out of Stock")
        
        self.summary_label.config(
            text=f"Total: {total_items} items | Value: {total_value:,.2f} PKR | "
                 f"Low Stock: {low_stock} | Out of Stock: {out_of_stock}"
        )

    def create_search_filter_card(self):
        """Create search and filter card"""
        card_frame = ttk.Frame(self.frame, style="Inventory.Main.TFrame")
        card_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        
        card = ttk.Frame(card_frame, style="Inventory.Main.TFrame", padding=5)
        card.pack(fill='x')
        
        self.create_search_row(card)
        self.create_filter_row(card)

    def create_search_row(self, parent):
        """Create search components"""
        search_frame = ttk.Frame(parent, style="Inventory.Main.TFrame")
        search_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(search_frame, 
                 text="Search Inventory:", 
                 style="Inventory.Label.TLabel").pack(side='left', padx=(0, 5))
        
        self.search_entry = ttk.Entry(search_frame, style="Inventory.Entry.TEntry")
        self.search_entry.pack(side='left', fill='x', expand=True)

    def create_filter_row(self, parent):
        """Create filter components"""
        filter_frame = ttk.Frame(parent, style="Inventory.Main.TFrame")
        filter_frame.pack(fill='x')
        
        ttk.Label(filter_frame, 
                text="Filters:", 
                style="Inventory.Label.TLabel").pack(side='left', padx=(0, 5))
        
        # Get categories and companies from database
        categories = ["All Categories"] + self.db.get_all_categories()
        companies = ["All Companies"] + self.db.get_all_companies()
        
        # Category filter
        self.filter_category = ttk.Combobox(filter_frame, 
                                        values=categories,
                                        style="Inventory.Combobox.TCombobox",
                                        width=18)
        self.filter_category.pack(side='left', padx=(0, 5))
        self.filter_category.set("All Categories")
        
        # Company filter
        self.filter_company = ttk.Combobox(filter_frame, 
                                        values=companies,
                                        style="Inventory.Combobox.TCombobox",
                                        width=18)
        self.filter_company.pack(side='left', padx=(0, 5))
        self.filter_company.set("All Companies")
        
        # Status filter
        self.filter_status = ttk.Combobox(filter_frame, 
                                        values=["All Status", "In Stock", "Low Stock", "Out of Stock"], 
                                        style="Inventory.Combobox.TCombobox",
                                        width=18)
        self.filter_status.pack(side='left', padx=(0, 5))
        self.filter_status.set("All Status")
        
        # Range filter components
        self.range_type = ttk.Combobox(filter_frame,
                                    values=["No Range", "Price Range", "Quantity Range"],
                                    style="Inventory.Combobox.TCombobox",
                                    width=15)
        self.range_type.pack(side='left', padx=(0, 5))
        self.range_type.set("No Range")
        self.range_type.bind("<<ComboboxSelected>>", self.toggle_range_fields)
        
        # Range fields (initially hidden)
        self.range_frame = ttk.Frame(filter_frame, style="Inventory.Main.TFrame")
        
        self.min_label = ttk.Label(self.range_frame, text="Min:", style="Inventory.Label.TLabel")
        self.min_entry = ttk.Entry(self.range_frame, style="Inventory.Entry.TEntry", width=8)
        self.max_label = ttk.Label(self.range_frame, text="Max:", style="Inventory.Label.TLabel")
        self.max_entry = ttk.Entry(self.range_frame, style="Inventory.Entry.TEntry", width=8)
        
        self.min_label.pack(side='left')
        self.min_entry.pack(side='left', padx=(0, 5))
        self.max_label.pack(side='left')
        self.max_entry.pack(side='left')
        
        # Bind events
        self.min_entry.bind("<KeyRelease>", self.apply_filters)
        self.max_entry.bind("<KeyRelease>", self.apply_filters)
        self.filter_category.bind("<<ComboboxSelected>>", self.apply_filters)
        self.filter_company.bind("<<ComboboxSelected>>", self.apply_filters)
        self.filter_status.bind("<<ComboboxSelected>>", self.apply_filters)

    def refresh_filters(self):
        """Refresh the filter dropdowns with current database values"""
        # Get updated lists from database
        categories = self.db.get_all_categories()
        companies = self.db.get_all_companies()
        
        # Update the combobox values
        current_category = self.filter_category.get()
        current_company = self.filter_company.get()
        
        self.filter_category['values'] = categories
        self.filter_company['values'] = companies
        
        # Restore previous selections if they still exist
        if current_category in categories:
            self.filter_category.set(current_category)
        else:
            self.filter_category.set("All Categories")
        
        if current_company in companies:
            self.filter_company.set(current_company)
        else:
            self.filter_company.set("All Companies")

    def toggle_range_fields(self, event=None):
        """Show or hide range fields based on selection"""
        self.range_frame.pack_forget()
        selected = self.range_type.get()
        
        if selected == "No Range":
            self.min_entry.delete(0, tk.END)
            self.max_entry.delete(0, tk.END)
        else:
            self.range_frame.pack(side='left')
        self.apply_filters()
    
    def apply_filters(self, event=None):
        """Apply all filters by reloading data from database with filters"""
        self.populate_sample_data()

    def create_action_buttons(self):
        """Create action buttons"""
        action_frame = ttk.Frame(self.frame, style="Inventory.Main.TFrame")
        action_frame.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        
        action_card = ttk.Frame(action_frame, style="Inventory.Main.TFrame", padding=5)
        action_card.pack(fill='x')
        
        self.create_primary_buttons(action_card)

    # Update create_primary_buttons method
    def create_primary_buttons(self, parent):
        """Create primary action buttons without export/claims"""
        btn_frame = ttk.Frame(parent, style="Inventory.Main.TFrame")
        btn_frame.pack(side='left', fill='x', expand=True)
        
        buttons = [
            ("➕ Add New Item", self.show_add_item_dialog),
            ("✏️ Edit Item", self.show_edit_item_dialog),
            ("🗑️ Delete Item", self.show_delete_item_dialog),
            ("📦 Restock", self.show_restock_dialog)
        ]
        
        for text, command in buttons:
            ttk.Button(btn_frame, 
                    text=text, 
                    style="Inventory.Button.TButton",  
                    command=command).pack(side='left', padx=2)


    def create_inventory_table(self):
        """Create the inventory table"""
        table_frame = ttk.Frame(self.frame, style="Inventory.Main.TFrame")
        table_frame.grid(row=3, column=0, sticky='nsew')
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Name", "Category", "Company", "Code", "TradePrice", "MfgPrice", "Quantity", "Status", "Worth"),
            show='headings',
            selectmode='browse',
            style="Custom.Treeview"
        )
        
        self.configure_table_columns()
        
        vsb = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        self.tree.bind("<Configure>", self.adjust_column_widths)
        self.populate_sample_data()

    def configure_table_columns(self):
        """Configure table columns and headings"""
        columns = {
            "ID": {"text": "ID", "width": 60, "anchor": 'center', "stretch": False},
            "Name": {"text": "Item Name", "width": 150, "anchor": 'w', "stretch": True},
            "Category": {"text": "Category", "width": 120, "anchor": 'w', "stretch": False},
            "Company": {"text": "Company", "width": 120, "anchor": 'w', "stretch": False},
            "Code": {"text": "Item Code", "width": 100, "anchor": 'center', "stretch": False},
            "TradePrice": {"text": "Trade Price (PKR)", "width": 100, "anchor": 'e', "stretch": False},
            "MfgPrice": {"text": "Mfg Price (PKR)", "width": 100, "anchor": 'e', "stretch": False},
            "Quantity": {"text": "Qty", "width": 60, "anchor": 'center', "stretch": False},
            "Status": {"text": "Status", "width": 100, "anchor": 'center', "stretch": False},
            "Worth": {"text": "Worth (PKR)", "width": 100, "anchor": 'e', "stretch": False}
        }
        
        for col, config in columns.items():
            self.tree.heading(col, text=config["text"], anchor=config.get("anchor", 'w'))
            self.tree.column(col, width=config["width"], anchor=config.get("anchor", 'w'),
                            stretch=config.get("stretch", False))

    def adjust_column_widths(self, event):
        """Automatically adjust column widths"""
        fixed_width = sum(
            int(self.tree.column(col)['width']) 
            for col in self.tree['columns'] 
            if not self.tree.column(col)['stretch']
        )
        
        available_width = event.width - 20
        
        if available_width > fixed_width:
            stretch_cols = [col for col in self.tree['columns'] if self.tree.column(col)['stretch']]
            if stretch_cols:
                extra_space = available_width - fixed_width
                per_col = extra_space // len(stretch_cols)
                for col in stretch_cols:
                    self.tree.column(col, width=per_col)

    def populate_sample_data(self):
        """Populate the table with data from database"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # First ensure all statuses are up to date
        self.db.cursor.execute("""
            UPDATE products 
            SET status = CASE 
                WHEN quantity <= 0 THEN 'Out of Stock'
                WHEN quantity <= 10 THEN 'Low Stock'
                ELSE 'In Stock'
            END
        """)
        self.db.conn.commit()
        
        # Get products from database with current filters
        filters = self.get_current_filters()
        products = self.db.get_products(filters)
        
        for product in products:
            # Determine status emoji
            if product['status'] == "Out of Stock":
                status_emoji = "🔴"
                status_tag = "out_of_stock"
            elif product['status'] == "Low Stock":
                status_emoji = "🟡"
                status_tag = "low_stock"
            else:
                status_emoji = "🟢"
                status_tag = "in_stock"
            
            self.tree.insert("", 'end', values=(
                product['id'],
                product['name'],
                product['category'],
                product['company'],
                product['code'],
                f"{product['trade_price']:,.2f}",
                f"{product['mfg_price']:,.2f}",
                product['quantity'],
                f"{status_emoji} {product['status']}",
                f"{product['worth']:,.2f}"
            ), tags=(status_tag,))
        
        self.update_summary()
    
    def get_current_filters(self):
        """Get current filter values from UI"""
        filters = {}
        
        # Category filter
        category = self.filter_category.get()
        if category != "All Categories":
            filters['category'] = category
            
        # Company filter
        company = self.filter_company.get()
        if company != "All Companies":
            filters['company'] = company
            
        # Status filter
        status = self.filter_status.get()
        if status != "All Status":
            filters['status'] = status
            
        # Search query
        search_query = self.search_entry.get().strip()
        if search_query:
            filters['search_query'] = search_query
            
        # Range filters
        range_type = self.range_type.get()
        if range_type == "Price Range":
            try:
                min_price = float(self.min_entry.get()) if self.min_entry.get() else 0
                max_price = float(self.max_entry.get()) if self.max_entry.get() else float('inf')
                filters['range_type'] = "Price Range"
                filters['min_price'] = min_price
                filters['max_price'] = max_price
            except ValueError:
                pass
                
        elif range_type == "Quantity Range":
            try:
                min_qty = float(self.min_entry.get()) if self.min_entry.get() else 0
                max_qty = float(self.max_entry.get()) if self.max_entry.get() else float('inf')
                filters['range_type'] = "Quantity Range"
                filters['min_qty'] = min_qty
                filters['max_qty'] = max_qty
            except ValueError:
                pass
                
        return filters

    def create_dialog(self, title, width=400, height=300):
        """Create a base dialog window"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        dialog.configure(background='#ffffff')
        
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - (width // 2)
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")
        
        container = ttk.Frame(dialog, style='Inventory.Dialog.TFrame')
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        return dialog, container
    
    def show_add_item_dialog(self):
        """Show dialog for adding new item"""
        dialog, container = self.create_dialog("Add New Item", 500, 450)
        
        ttk.Label(container, 
                text="Add New Inventory Item", 
                style="Inventory.Dialog.Title.TLabel").pack(pady=(0, 15))
        
        # Get categories and companies from database
        categories = list(self.db.get_all_categories())
        categories.sort()  # Sort alphabetically

        companies = list(self.db.get_all_companies())
        companies.sort()  # Sort alphabetically
        
        fields = [
            ("Item Name", "entry"),
            ("Category", "combobox", categories),  # Use database categories
            ("Company", "combobox", companies),
            ("Item Code", "entry"),
            ("Trade Price (PKR)", "entry"),
            ("Mfg Price (PKR)", "entry"),
            ("Initial Quantity", "entry"),
        ]
        
        self.add_form_fields(container, fields)
        
        btn_frame = ttk.Frame(container, style="Inventory.Dialog.ButtonFrame.TFrame")
        btn_frame.pack(side='bottom', pady=(15, 0))
        
        ttk.Button(btn_frame, 
                text="Cancel", 
                style="Inventory.Dialog.Neutral.TButton",
                command=dialog.destroy).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, 
                text="Add Item", 
                style="Inventory.Dialog.Button.TButton",
                command=lambda: self.add_item_action(dialog)).pack(side='right', padx=5)

    def show_edit_item_dialog(self):
        """Show dialog for editing item"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item_data = self.tree.item(selected)['values']
        dialog, container = self.create_dialog("Edit Item", 500, 450)
        
        ttk.Label(container, 
                text=f"Edit Item (ID: {item_data[0]})", 
                style="Inventory.Dialog.Title.TLabel").pack(pady=(0, 15))
        
        # Get categories and companies from database
        categories = list(self.db.get_all_categories())
        categories.sort()  # Sort alphabetically

        companies = list(self.db.get_all_companies())
        companies.sort()  # Sort alphabetically
        
        fields = [
            ("Item Name", "entry", item_data[1]),
            ("Category", "combobox", categories, item_data[2]),  # Use database categories
            ("Company", "combobox",companies, item_data[3]),
            ("Item Code", "entry", item_data[4]),
            ("Trade Price (PKR)", "entry", item_data[5].replace(',', '')),
            ("Mfg Price (PKR)", "entry", item_data[6].replace(',', '')),
        ]
        
        self.add_form_fields(container, fields)
        
        btn_frame = ttk.Frame(container, style="Inventory.Dialog.ButtonFrame.TFrame")
        btn_frame.pack(side='bottom', pady=(15, 0))
        
        ttk.Button(btn_frame, 
                text="Cancel", 
                style="Inventory.Dialog.Neutral.TButton",
                command=dialog.destroy).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, 
                text="Save Changes", 
                style="Inventory.Dialog.Button.TButton",
                command=lambda: self.edit_item_action(dialog, item_data[0])).pack(side='right', padx=5)

    def show_delete_item_dialog(self):
        """Show confirmation dialog for deleting item"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        item_data = self.tree.item(selected)['values']
        dialog, container = self.create_dialog("Confirm Deletion", 400, 200)
        
        ttk.Label(container, 
                text=f"Delete this item permanently?", 
                style="Inventory.Dialog.Title.TLabel").pack(pady=(10, 5))
        
        ttk.Label(container, 
                text=f"ID: {item_data[0]} | {item_data[1]}", 
                style="Inventory.Dialog.Info.TLabel").pack()
        
        btn_frame = ttk.Frame(container, style="Inventory.Dialog.ButtonFrame.TFrame")
        btn_frame.pack(side='bottom', pady=(15, 0))
        
        ttk.Button(btn_frame, 
                text="Cancel", 
                style="Inventory.Dialog.Neutral.TButton",
                command=dialog.destroy).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, 
                text="Delete Permanently", 
                style="Inventory.Dialog.Danger.TButton",
                command=lambda: self.delete_item_action(dialog, item_data[0])).pack(side='right', padx=5)

    def show_restock_dialog(self):
        """Show dialog for restocking item"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an item to restock")
            return
        
        item_data = self.tree.item(selected)['values']
        dialog, container = self.create_dialog("Restock Item", 400, 250)
        
        ttk.Label(container, 
                text=f"Restock Item", 
                style="Inventory.Dialog.Title.TLabel").pack(pady=(0, 15))
        
        ttk.Label(container, 
                text=f"{item_data[1]} (Current: {item_data[7]})", 
                style="Inventory.Dialog.Info.TLabel").pack()
        
        amount_frame = ttk.Frame(container, style="Inventory.Dialog.TFrame")
        amount_frame.pack(pady=10)
        
        ttk.Label(amount_frame, 
                text="Restock Amount:", 
                style="Inventory.Dialog.Label.TLabel").pack(side='left', padx=(0, 10))
        
        self.restock_amount = ttk.Entry(amount_frame, style="Inventory.Dialog.Entry.TEntry", width=10)
        self.restock_amount.pack(side='left')
        
        btn_frame = ttk.Frame(container, style="Inventory.Dialog.ButtonFrame.TFrame")
        btn_frame.pack(side='bottom', pady=(15, 0))
        
        ttk.Button(btn_frame, 
                text="Cancel", 
                style="Inventory.Dialog.Neutral.TButton",
                command=dialog.destroy).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, 
                text="Confirm Restock", 
                style="Inventory.Dialog.Button.TButton",
                command=lambda: self.restock_item_action(dialog, item_data[0])).pack(side='right', padx=5)

    # ======================
    # ACTION METHODS
    # ======================
    def search_items(self, event=None):
        """Handle search functionality"""
        query = self.search_entry.get().lower()
        
        if not query:
            self.apply_filters()
            return
        
        visible_items = 0
        for item in self.tree.get_children():
            values = [str(v).lower() for v in self.tree.item(item, 'values')]
            if any(query in value for value in values):
                self.tree.item(item, tags=(self.tree.item(item, 'tags')[0],))
                self.tree.detach(item)
                self.tree.reattach(item, '', 'end')
                visible_items += 1
            else:
                self.tree.detach(item)

    def add_form_fields(self, parent, fields):
        """Add form fields to a dialog"""
        self.form_entries = {}  # Reset form entries dictionary
        form_frame = ttk.Frame(parent, style='Inventory.Dialog.TFrame')
        form_frame.pack(fill='both', expand=True)
        
        for field in fields:
            row = ttk.Frame(form_frame, style='Inventory.Dialog.TFrame')
            row.pack(fill='x', pady=5)
            
            ttk.Label(row, 
                    text=f"{field[0]}:", 
                    style="Inventory.Dialog.Label.TLabel").pack(side='left')
            
            if field[1] == "entry":
                entry = ttk.Entry(row, style="Inventory.Dialog.Entry.TEntry")
                entry.pack(side='left', fill='x', expand=True)
                if len(field) > 2:
                    entry.insert(0, field[2])
                self.form_entries[field[0]] = entry
            elif field[1] == "combobox":
                combo = ttk.Combobox(row, 
                                values=field[2], 
                                style="Inventory.Dialog.Combobox.TCombobox")
                combo.pack(side='left', fill='x', expand=True)
                if len(field) > 3:
                    combo.set(field[3])
                self.form_entries[field[0]] = combo


    def update_product_status(self, product_id):
        """Force update product status based on current quantity"""
        query = """
        UPDATE products 
        SET status = CASE 
            WHEN quantity <= 0 THEN 'Out of Stock'
            WHEN quantity <= 10 THEN 'Low Stock'
            ELSE 'In Stock'
        END
        WHERE id = ?
        """
        self.db.cursor.execute(query, (product_id,))
        self.db.conn.commit()

    def add_item_action(self, dialog):
        """Handle add item action with database"""
        try:
            # Get data from form fields
            quantity = int(self.form_entries["Initial Quantity"].get())
            
            # Determine status based on quantity
            if quantity <= 0:
                status = "Out of Stock"
            elif quantity <= 10:
                status = "Low Stock"
            else:
                status = "In Stock"
                
            product_data = {
                'name': self.form_entries["Item Name"].get().strip(),
                'category': self.form_entries["Category"].get().strip(),
                'company': self.form_entries["Company"].get().strip(),
                'code': self.form_entries["Item Code"].get().strip(),
                'trade_price': float(self.form_entries["Trade Price (PKR)"].get()),
                'mfg_price': float(self.form_entries["Mfg Price (PKR)"].get()),
                'quantity': quantity,
                'status': status,
                'worth': float(self.form_entries["Trade Price (PKR)"].get()) * quantity
            }
            
            # Validate required fields
            if not all(product_data.values()):
                raise ValueError("All fields are required")
            
            if product_data['quantity'] < 0:
                raise ValueError("Quantity cannot be negative")
                
            if product_data['trade_price'] <= 0 or product_data['mfg_price'] <= 0:
                raise ValueError("Prices must be positive values")
            
            # Add to database
            product_id = self.db.add_product(product_data)
            self.populate_sample_data()
            self.refresh_filters() 
            dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add item: {str(e)}")

    def edit_item_action(self, dialog, item_id):
        """Handle edit item action with database"""
        try:
            # Get updated data from form
            updates = {
                'name': self.form_entries["Item Name"].get().strip(),
                'category': self.form_entries["Category"].get().strip(),
                'company': self.form_entries["Company"].get().strip(),
                'code': self.form_entries["Item Code"].get().strip(),
                'trade_price': float(self.form_entries["Trade Price (PKR)"].get()),
                'mfg_price': float(self.form_entries["Mfg Price (PKR)"].get()),
            }
            
            # Validate required fields
            if not all(updates.values()):
                raise ValueError("All fields are required")
                
            if updates['trade_price'] <= 0 or updates['mfg_price'] <= 0:
                raise ValueError("Prices must be positive values")
            
            # Update in database
            success = self.db.update_product(item_id, updates)
            if success:
                # Force status update based on current quantity
                self.db.cursor.execute("""
                    UPDATE products 
                    SET status = CASE 
                        WHEN quantity <= 0 THEN 'Out of Stock'
                        WHEN quantity <= 10 THEN 'Low Stock'
                        ELSE 'In Stock'
                    END
                    WHERE id = ?
                """, (item_id,))
                self.db.conn.commit()
                
                self.populate_sample_data()
                self.refresh_filters() 
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to update item")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update item: {str(e)}")

    def delete_item_action(self, dialog, item_id):
        """Handle delete item action with database"""
        try:
            success = self.db.delete_product(item_id)
            if success:
                self.populate_sample_data()
                self.refresh_filters() 
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to delete item")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete item: {str(e)}")

    def restock_item_action(self, dialog, item_id):
        """Handle restock item action with database"""
        try:
            amount = int(self.restock_amount.get())
            if amount <= 0:
                raise ValueError("Restock amount must be positive")
            
            success = self.db.restock_product(item_id, amount)
            if success:
                self.update_product_status(item_id)
                self.populate_sample_data()
                self.refresh_filters() 
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to restock item")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid amount: {str(e)}")
            self.restock_amount.focus()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restock: {str(e)}")
        
    def export_data(self):
        """Handle export data action"""
        messagebox.showinfo("Export", "Export data functionality")

    def show_claims(self):
        """Handle claims action"""
        messagebox.showinfo("Claims", "Claims management panel")