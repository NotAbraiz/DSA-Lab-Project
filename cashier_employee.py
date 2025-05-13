import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkinter import simpledialog, filedialog
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import win32print
import win32api
import os


class CashierEmployee:
    """Cashier POS interface for employees"""
    
    def __init__(self, app, db, counter_db):
        """Initialize cashier interface"""
        # Core attributes
        self.app = app
        self.db = db
        self.counter_db = counter_db
        self.frame = None
        self.current_customer = None
        self.current_cart = []
        self.sales_history = []
        self.pos_mode = False
        self.current_hover_item = None
        
        # UI Components
        self.search_entry = None
        self.products_table = None
        self.cart_table = None
        self.sales_history_table = None  # Initialize as None
        self.total_label = None
        self.customer_label = None
        self.time_label = None
        
        # Auto-refresh settings (but don't start yet)
        self.auto_refresh_interval = 30000  # 30 seconds

    # ======================
    # MAIN WINDOW MANAGEMENT
    # ======================
    
    def show(self, parent):
        """Show the cashier interface"""
        self.create_main_frame(parent)
        self.show_start_screen()

    def hide(self):
        """Hide the cashier interface"""
        if self.frame:
            self.frame.pack_forget()
        self.pos_mode = False
        self.show_sidebar()

    def create_main_frame(self, parent):
        """Create the main container frame"""
        self.frame = ttk.Frame(parent, style="Cashier.Main.TFrame")
        self.frame.pack(expand=True, fill='both')

    def clear_frame(self):
        """Clear all widgets from the frame"""
        for widget in self.frame.winfo_children():
            widget.destroy()

    # ======================
    # START SCREEN & MODE MANAGEMENT
    # ======================
    
    def show_start_screen(self):
        """Show the initial start counter screen"""
        self.clear_frame()
        self.pos_mode = False
        self.show_sidebar()
        
        container = ttk.Frame(self.frame, style="Main.Container.TFrame")
        container.place(relx=0.5, rely=0.5, anchor='center')
        
        ttk.Label(container, 
                 text="Cashier POS System", 
                 style="Cashier.Dashboard.Title.TLabel").pack(pady=20)
        
        ttk.Button(container,
                  text="START COUNTER",
                  style="Cashier.Button.TButton",
                  command=self.start_counter).pack(pady=20, ipadx=20, ipady=10)

    def start_counter(self):
        """Transition to the full POS interface"""
        self.pos_mode = True
        self.clear_frame()
        self.create_pos_interface()
        self.load_all_products()
        
        # Hide sidebar without destroying it
        if hasattr(self.app, 'sidebar'):
            self.app.sidebar.pack_forget()
    def return_to_start(self):
        """Return to the start screen"""
        self.pos_mode = False
        self.clear_frame()
        self.show_start_screen()
        
        # Show sidebar again
        if hasattr(self.app, 'sidebar'):
            self.app.sidebar.pack(side='left', fill='y')
    def hide_sidebar(self):
        """Hide the application sidebar"""
        if hasattr(self.app, 'sidebar'):
            self.app.sidebar.pack_forget()

    def show_sidebar(self):
        """Show the application sidebar"""
        if hasattr(self.app, 'sidebar') and not self.pos_mode:
            self.app.sidebar.pack(side='left', fill='y')

    # ======================
    # POS INTERFACE CREATION
    # ======================
    
    def create_pos_interface(self):
        """Create the main POS interface"""
        self.create_header()
        self.create_main_content_area()
        self.update_time()
        # Start auto-refresh AFTER UI is created
        self.schedule_auto_refresh()  # Moved here from __init__

    def create_header(self):
        """Create header with time and cashier info"""
        header_frame = ttk.Frame(self.frame, style="Cashier.Main.TFrame")
        header_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(header_frame,
                text="Back",
                style="Cashier.Button.TButton",
                command=self.return_to_start).pack(side='left', padx=10)
        
        ttk.Label(header_frame,
                text=f"Cashier: {self.app.current_user}",
                style="Cashier.Label.TLabel").pack(side='left')
        
        # New clock styling
        self.time_label = ttk.Label(header_frame, 
                                style="Cashier.Label.TLabel",
                                font=('Segoe UI', 14, 'bold'),
                                foreground='#263238')
        self.time_label.pack(side='right', padx=20)

    def create_main_content_area(self):
        """Create the main content area with left and right panels"""
        main_content = ttk.Frame(self.frame, style="Cashier.Main.TFrame")
        main_content.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Left panel (Products and Sales History)
        left_panel = ttk.Frame(main_content, style="Cashier.Main.TFrame")
        left_panel.pack(side='left', fill='both', expand=True)
        
        self.create_search_section(left_panel)
        products_frame = ttk.Frame(left_panel, style="Cashier.Main.TFrame")
        products_frame.pack(fill='both', expand=True)
        self.create_products_section(products_frame)
        self.create_sales_history_section(left_panel)
        
        # Right panel (Cart and Customer Info) - Increased width from 400 to 450
        right_panel = ttk.Frame(main_content, style="Cashier.Main.TFrame", width=450)
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)
        
        self.create_customer_section(right_panel)
        self.create_cart_section(right_panel)
        self.create_payment_section(right_panel)

    # ======================
    # PRODUCTS SECTION
    # ======================
    
    def create_search_section(self, parent):
        """Create product search section"""
        search_frame = ttk.Frame(parent, style="Cashier.Main.TFrame")
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame,
                text="Search Products:",
                style="Cashier.Label.TLabel").pack(side='left', padx=(0, 5))
        
        self.search_entry = ttk.Entry(search_frame, style="Cashier.Entry.TEntry")
        self.search_entry.pack(side='left', expand=True, fill='x')
        self.search_entry.bind('<KeyRelease>', self.search_products)

    def create_products_section(self, parent):
        """Create products display section"""
        container = ttk.Frame(parent, style="Cashier.Main.TFrame")
        container.pack(fill='both', expand=True)
        
        # Treeview setup
        self.products_table = ttk.Treeview(
            container,
            columns=("ID", "Name", "Company", "Price", "Stock", "Add"),
            show='headings',
            selectmode='browse',
            style="Custom.Treeview"
        )
        
        # Configure columns
        columns = {
            "ID": {"text": "ID", "width": 50, "anchor": 'center'},
            "Name": {"text": "Product", "width": 150, "anchor": 'w'},
            "Company": {"text": "Company", "width": 120, "anchor": 'w'},
            "Price": {"text": "Price", "width": 80, "anchor": 'e'},
            "Stock": {"text": "In Stock", "width": 80, "anchor": 'center'},
            "Add": {"text": "", "width": 40, "anchor": 'center'}
        }
        
        for col, config in columns.items():
            self.products_table.heading(col, text=config["text"], anchor=config["anchor"])
            self.products_table.column(col, width=config["width"], anchor=config["anchor"])
        
        # Scrollbar
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.products_table.yview)
        self.products_table.configure(yscrollcommand=vsb.set)
        
        self.products_table.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Initialize hover tracking
        self.current_hover_item = None
        
        # Configure tags for hover effects
        self.products_table.tag_configure('hover', background='#f0f0f0')
        self.products_table.tag_configure('plus_visible', foreground='black')
        self.products_table.tag_configure('plus_hover', background='#e6f2ff')
        
        # Bind events
        self.products_table.bind("<Button-1>", self.on_table_click)
        self.products_table.bind("<Motion>", self.on_product_hover)
        self.products_table.bind("<Leave>", self.on_product_hover_leave)

    def load_all_products(self):
        """Load all products with visual stock indicators"""
        for item in self.products_table.get_children():
            self.products_table.delete(item)
        
        results = self.db.get_products({})
        
        for product in results:
            stock = product['quantity']
            stock_status = "Out of Stock" if stock <= 0 else f"In Stock ({stock})"
            tags = ('out_of_stock',) if stock <= 0 else ()
            
            self.products_table.insert("", 'end', values=(
                product['id'],
                product['name'],
                product['company'],
                f"PKR {product['trade_price']:,.2f}",
                stock_status,
                ""  # Add button column
            ), tags=tags)

    def refresh_products(self, product_ids=None):
        """Refresh specific products or all products"""
        if product_ids:
            # Refresh only specified products
            for item in self.products_table.get_children():
                values = self.products_table.item(item)['values']
                if int(values[0]) in product_ids:
                    stock = self.db.get_product_stock(int(values[0]))
                    stock_status = "Out of Stock" if stock <= 0 else f"In Stock ({stock})"
                    new_values = list(values)
                    new_values[4] = stock_status
                    self.products_table.item(item, values=new_values, 
                                        tags=('out_of_stock',) if stock <= 0 else ())
        else:
            # Full refresh
            self.load_all_products()

    def search_products(self, event=None):
        """Filter products based on search query"""
        query = self.search_entry.get().lower().strip()
        
        if not query:
            self.load_all_products()
            return
        
        for item in self.products_table.get_children():
            self.products_table.delete(item)
        
        results = self.db.get_products({"search_query": query})
        
        for product in results:
            self.products_table.insert("", 'end', values=(
                product['id'],
                product['name'],
                product['company'],
                f"PKR {product['trade_price']:,.2f}",
                product['quantity'],
                ""
            ), tags=('plus_hidden',))

    # ======================
    # PRODUCTS TABLE INTERACTIONS
    # ======================
    
    def on_product_hover(self, event):
        """Handle hover effect on products"""
        item = self.products_table.identify_row(event.y)
        column = self.products_table.identify_column(event.x)
        
        # Clear all hover effects
        for i in self.products_table.get_children():
            current_tags = list(self.products_table.item(i, 'tags'))
            if 'hover' in current_tags:
                current_tags.remove('hover')
            if 'plus_hover' in current_tags:
                current_tags.remove('plus_hover')
            values = list(self.products_table.item(i, 'values'))
            if len(values) >= 6:
                values[5] = ""
            self.products_table.item(i, values=values, tags=current_tags)
        
        if item:
            values = list(self.products_table.item(item, 'values'))
            if len(values) >= 6:
                values[5] = "+"
                tags = ['plus_visible', 'hover']
                
                if column == "#6":
                    tags.append('plus_hover')
                    self.current_hover_item = item
                
                self.products_table.item(item, values=values, tags=tags)

    def on_product_hover_leave(self, event):
        """Remove hover effects when mouse leaves"""
        for item in self.products_table.get_children():
            current_tags = list(self.products_table.item(item, 'tags'))
            if 'hover' in current_tags:
                current_tags.remove('hover')
            if 'plus_hover' in current_tags:
                current_tags.remove('plus_hover')
            values = list(self.products_table.item(item, 'values'))
            if len(values) >= 6:
                values[5] = ""
            self.products_table.item(item, values=values, tags=current_tags)
        self.current_hover_item = None

    def on_table_click(self, event):
        """Handle clicks on the products table"""
        column = self.products_table.identify_column(event.x)
        item = self.products_table.identify_row(event.y)
        
        if column == "#6" and item == self.current_hover_item:
            if not self.current_customer:
                messagebox.showwarning("No Customer", "Please select a customer before adding items")
                return
            self.show_quantity_dialog_for_item(item)

    def show_quantity_dialog_for_item(self, item):
        """Show quantity dialog only if item is in stock"""
        item_data = self.products_table.item(item)
        values = item_data['values']
        product_id = values[0]
        product_name = values[1]
        price = float(values[3].replace('PKR ', '').replace(',', ''))
        
        # Check stock before showing dialog
        stock = self.db.get_product_stock(product_id)
        if stock is None:
            messagebox.showerror("Error", "Product not found in inventory")
            return
            
        if stock <= 0:
            messagebox.showwarning("Out of Stock", 
                                f"{product_name} is currently out of stock")
            return
            
        self.show_quantity_dialog(product_id, product_name, price, stock)

    # ======================
    # QUANTITY DIALOG
    # ======================
        
    def show_quantity_dialog(self, product_id, product_name, price, max_quantity):
        """Show the original style quantity dialog with stock validation"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Add to Cart")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        # Center dialog on screen
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - 200
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - 125
        dialog.geometry(f"+{x}+{y}")
        
        container = ttk.Frame(dialog, style='Inventory.Dialog.TFrame')
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        ttk.Label(container, 
                text="Add to Cart", 
                style="Inventory.Dialog.Title.TLabel").pack(pady=(0, 15))
        
        # Product info
        stock_text = f" (Available: {max_quantity})" if max_quantity > 0 else " (Out of Stock)"
        ttk.Label(container, 
                text=f"{product_name}{stock_text}", 
                style="Inventory.Dialog.Info.TLabel").pack()
        
        ttk.Label(container, 
                text=f"Price: PKR {price:,.2f}", 
                style="Inventory.Dialog.Info.TLabel").pack()
        
        # Quantity controls
        quantity_frame = ttk.Frame(container, style="Inventory.Dialog.TFrame")
        quantity_frame.pack(pady=10)
        
        ttk.Label(quantity_frame, 
                text="Quantity:", 
                style="Inventory.Dialog.Label.TLabel").pack(side='left', padx=(0, 10))
        
        # Minus button
        minus_btn = ttk.Button(quantity_frame, 
                            text="-", 
                            width=2,
                            style="Inventory.Dialog.Button.TButton")
        minus_btn.pack(side='left')
        
        # Quantity entry
        quantity_var = tk.StringVar(value="1")
        quantity_entry = ttk.Entry(quantity_frame, 
                            textvariable=quantity_var,
                            style="Inventory.Dialog.Entry.TEntry", 
                            width=8,
                            justify='center')
        quantity_entry.pack(side='left', padx=5)
        quantity_entry.focus()
        quantity_entry.select_range(0, tk.END)
        
        # Plus button
        plus_btn = ttk.Button(quantity_frame, 
                            text="+", 
                            width=2,
                            style="Inventory.Dialog.Button.TButton")
        plus_btn.pack(side='left')
        
        # Button commands
        minus_btn.configure(command=lambda: self.adjust_quantity(quantity_var, quantity_entry, -1, max_quantity))
        plus_btn.configure(command=lambda: self.adjust_quantity(quantity_var, quantity_entry, 1, max_quantity))
        
        # Action buttons
        btn_frame = ttk.Frame(container, style="Inventory.Dialog.ButtonFrame.TFrame")
        btn_frame.pack(side='bottom', pady=(15, 0))
        
        ttk.Button(btn_frame, 
                text="Cancel", 
                style="Inventory.Dialog.Neutral.TButton",
                command=dialog.destroy).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, 
                text="Add to Cart", 
                style="Inventory.Dialog.Button.TButton",
                command=lambda: self.validate_and_add_to_cart(
                    product_id, product_name, price, quantity_var.get(), max_quantity, dialog)
                ).pack(side='right', padx=5)
        
        # Keyboard bindings
        dialog.bind("<Return>", lambda e: self.validate_and_add_to_cart(
            product_id, product_name, price, quantity_var.get(), max_quantity, dialog))
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def adjust_quantity(self, quantity_var, quantity_entry, change, max_quantity):
        """Adjust quantity value with stock limit"""
        try:
            current = int(quantity_var.get())
            new_val = max(1, min(current + change, max_quantity))
            quantity_var.set(str(new_val))
            quantity_entry.icursor(tk.END)
        except ValueError:
            quantity_var.set("1")
            quantity_entry.icursor(tk.END)
    def validate_and_add_to_cart(self, product_id, product_name, price, quantity, max_quantity, dialog):
        """Validate quantity before adding to cart"""
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            if quantity > max_quantity:
                raise ValueError(f"Cannot add more than {max_quantity} items")
                
            self.add_to_cart_with_quantity(product_id, product_name, price, quantity, dialog)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    # ======================
    # CART MANAGEMENT
    # ======================
    
    def create_cart_section(self, parent):
        """Create shopping cart section"""
        frame = ttk.Frame(parent, style="Cashier.Main.TFrame")
        frame.pack(fill='both', expand=True, pady=(0, 10))
        
        ttk.Label(frame,
                text="Current Cart",
                style="Cashier.Dashboard.Section.TLabel").pack(anchor='w')
        
        self.cart_table = ttk.Treeview(frame,
                                    columns=("Item", "Price", "quantity", "Total"),
                                    show='headings',
                                    style="Custom.Treeview")
        
        # Configure columns (slightly wider)
        self.cart_table.heading("Item", text="Item", anchor='w')
        self.cart_table.heading("Price", text="Price", anchor='e')
        self.cart_table.heading("quantity", text="quantity", anchor='center')
        self.cart_table.heading("Total", text="Total", anchor='e')
        
        self.cart_table.column("Item", width=180, anchor='w')  # Increased from 150
        self.cart_table.column("Price", width=90, anchor='e')  # Increased from 80
        self.cart_table.column("quantity", width=70, anchor='center')  # Increased from 60
        self.cart_table.column("Total", width=90, anchor='e')  # Increased from 80
        
        # Scrollbar
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.cart_table.yview)
        self.cart_table.configure(yscrollcommand=vsb.set)
        
        self.cart_table.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

    def add_to_cart_with_quantity(self, product_id, product_name, price, quantity, dialog):
        """Add item to cart with final validation"""
        try:
            # Final stock check (in case something changed)
            stock = self.db.get_product_stock(product_id)
            if stock is None:
                raise Exception("Product not found in inventory")
            if stock < quantity:
                raise Exception(f"Only {stock} items available now")
                return
                
            # Check if already in cart
            for item in self.current_cart:
                if item['id'] == product_id:
                    # Check if combined quantity exceeds stock
                    if (item['quantity'] + quantity) > stock:
                        messagebox.showwarning("Stock Limit", 
                                            f"Cannot add more than {stock} items total")
                        return
                    item['quantity'] += quantity
                    item['total'] = item['price'] * item['quantity']
                    self.update_cart_display()
                    dialog.destroy()
                    return
            
            # Add new item
            self.current_cart.append({
                'id': product_id,
                'name': product_name,
                'price': price,
                'quantity': quantity,
                'total': price * quantity
            })
            
            self.update_cart_display()
            dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid quantity: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_cart_display(self):
        """Update the cart display"""
        for item in self.cart_table.get_children():
            self.cart_table.delete(item)
        
        total = 0
        for item in self.current_cart:
            self.cart_table.insert("", 'end', values=(
                item['name'],
                f"PKR {item['price']:,.2f}",
                item['quantity'],
                f"PKR {item['total']:,.2f}"
            ))
            total += item['total']
        
        self.total_label.config(text=f"PKR {total:,.2f}")

    def show_cart_menu(self, event):
        """Show context menu for cart items"""
        selected = self.cart_table.identify_row(event.y)
        if selected:
            self.cart_table.selection_set(selected)
            self.cart_menu.post(event.x_root, event.y_root)

    def increase_quantity(self):
        """Increase quantity of selected item"""
        selected = self.cart_table.selection()
        if not selected:
            return
            
        item_id = self.cart_table.index(selected[0])
        self.current_cart[item_id]['quantity'] += 1
        self.current_cart[item_id]['total'] = self.current_cart[item_id]['price'] * self.current_cart[item_id]['quantity']
        self.update_cart_display()

    def decrease_quantity(self):
        """Decrease quantity of selected item"""
        selected = self.cart_table.selection()
        if not selected:
            return
            
        item_id = self.cart_table.index(selected[0])
        if self.current_cart[item_id]['quantity'] > 1:
            self.current_cart[item_id]['quantity'] -= 1
            self.current_cart[item_id]['total'] = self.current_cart[item_id]['price'] * self.current_cart[item_id]['quantity']
            self.update_cart_display()

    def remove_item(self):
        """Remove selected item from cart"""
        selected = self.cart_table.selection()
        if not selected:
            return
            
        item_id = self.cart_table.index(selected[0])
        del self.current_cart[item_id]
        self.update_cart_display()

    # ======================
    # CUSTOMER MANAGEMENT
    # ======================
    
    def create_customer_section(self, parent):
        """Create customer information section"""
        frame = ttk.Frame(parent, style="Cashier.Main.TFrame")
        frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(frame,
                text="Customer Information",
                style="Cashier.Dashboard.Section.TLabel").pack(anchor='w')
        
        self.customer_label = ttk.Label(frame,
                                    text="No customer selected",
                                    style="Cashier.Label.TLabel")
        self.customer_label.pack(anchor='w', pady=5)
        
        btn_frame = ttk.Frame(frame, style="Cashier.Main.TFrame")
        btn_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(btn_frame,
                text="Select Customer",
                style="Cashier.Button.TButton",
                command=self.select_customer).pack()
        
    def select_customer(self):
        """Simplified customer selection dialog with just name field"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Select Customer")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Center dialog on screen
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - 200
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - 100
        dialog.geometry(f"+{x}+{y}")
        
        container = ttk.Frame(dialog, style="Cashier.Dialog.TFrame")
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Simple instruction label
        ttk.Label(container,
                text="Enter customer name:",
                style="Cashier.Dialog.Label.TLabel").pack(pady=(10, 5))
        
        # Single text entry field
        name_entry = ttk.Entry(container,
                            style="Cashier.Dialog.Entry.TEntry")
        name_entry.pack(fill='x', pady=10)
        name_entry.focus()
        
        # Button frame
        btn_frame = ttk.Frame(container, style="Cashier.Dialog.TFrame")
        btn_frame.pack(fill='x', pady=(10, 0))
        
        # Confirm button
        ttk.Button(btn_frame,
                text="Confirm",
                style="Cashier.Dialog.Button.TButton",
                command=lambda: self.set_customer(name_entry.get(), dialog)
                ).pack(side='right', padx=5)
        
        # Cancel button
        ttk.Button(btn_frame,
                text="Cancel",
                style="Cashier.Dialog.Neutral.TButton",
                command=dialog.destroy
                ).pack(side='right', padx=5)
        
        # Bind Enter key to confirm
        dialog.bind("<Return>", lambda e: self.set_customer(name_entry.get(), dialog))

    def set_customer(self, name, dialog):
        """Set the selected customer and close dialog"""
        if name.strip():  # Only proceed if name is not empty
            self.current_customer = {
                'name': name.strip(),
                'phone': '',
                'email': ''
            }
            self.update_customer_display()
            dialog.destroy()
        else:
            messagebox.showwarning("Invalid Input", "Please enter a customer name")

    def new_customer(self):
        """Create a new customer record"""
        name = simpledialog.askstring("New Customer", "Enter customer name:")
        if name:
            self.current_customer = {
                'name': name,
                'phone': '',
                'email': ''
            }
            self.update_customer_display()

    def existing_customer(self):
        """Select an existing customer"""
        name = simpledialog.askstring("Existing Customer", "Enter customer name:")
        if name:
            self.current_customer = {
                'name': name,
                'phone': '0300-1234567',
                'email': f"{name.lower().replace(' ', '_')}@example.com"
            }
            self.update_customer_display()

    def update_customer_display(self):
        """Update the customer information display"""
        if self.current_customer:
            info = f"Customer: {self.current_customer['name']}"
            if self.current_customer['phone']:
                info += f"\nPhone: {self.current_customer['phone']}"
            if self.current_customer['email']:
                info += f"\nEmail: {self.current_customer['email']}"
            self.customer_label.config(text=info)
        else:
            self.customer_label.config(text="No customer selected")

    # ======================
    # PAYMENT & SALES HISTORY
    # ======================
    
    def create_payment_section(self, parent):
        """Create payment section"""
        frame = ttk.Frame(parent, style="Cashier.Main.TFrame")
        frame.pack(fill='x', pady=(0, 10))
        
        total_frame = ttk.Frame(frame, style="Cashier.Main.TFrame")
        total_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(total_frame,
                text="Total:",
                style="Cashier.Label.TLabel").pack(side='left')
        
        self.total_label = ttk.Label(total_frame,
                                text="PKR 0.00",
                                style="Cashier.Total.TLabel")
        self.total_label.pack(side='right')
        
        btn_frame = ttk.Frame(frame, style="Cashier.Main.TFrame")
        btn_frame.pack(fill='x')
        
        # Action buttons frame (for grouped buttons)
        action_btn_frame = ttk.Frame(btn_frame, style="Cashier.Main.TFrame")
        action_btn_frame.pack(side='left')
        
        # Complete Sale button
        ttk.Button(action_btn_frame,
                text="Complete Sale",
                style="Cashier.Button.TButton",
                command=self.complete_sale).pack(side='left', padx=5)
        
        # Edit Item button
        ttk.Button(action_btn_frame,
                text="Edit Item",
                style="Cashier.Button.TButton",
                command=self.edit_selected_item).pack(side='left', padx=5)
        
        # Delete Item button
        ttk.Button(action_btn_frame,
                text="Delete Item",
                style="Cashier.Button.TButton",
                command=self.delete_selected_item).pack(side='left', padx=5)
        
        # Cancel Sale button (far right)
        ttk.Button(btn_frame,
                text="Cancel Sale",
                style="Cashier.Dialog.Neutral.TButton",
                command=self.cancel_sale).pack(side='right')

    def create_sales_history_section(self, parent):
        """Create sales history section with proper sizing"""
        container = ttk.Frame(parent, style="Cashier.Main.TFrame")
        container.pack(fill='both', expand=True, pady=(10, 0))  # Added some padding

        # Header
        ttk.Label(container,
                text="Today's Sales", 
                style="Cashier.Dashboard.Section.TLabel").pack(anchor='w', pady=(0, 5))

        # Table frame with fixed height
        table_frame = ttk.Frame(container, style="Cashier.Main.TFrame")
        table_frame.pack(fill='both', expand=True)
        
        # Calculate appropriate height (shows ~5 rows with header)
        style = ttk.Style()
        row_height = style.lookup('Treeview', 'rowheight', default=20)
        table_height = 6  # 5 rows + header

        # Table with fixed height
        self.sales_history_table = ttk.Treeview(
            table_frame,
            columns=("ID", "Receipt ID", "Customer", "Amount", "Payment", "Date", "Time"),
            show='headings',
            height=6,
            style="Custom.Treeview"
        )
        
        # Add double-click binding
        self.sales_history_table.bind("<Double-1>", self.show_selected_receipt)
        

        # Column configuration (slightly adjusted widths)
        columns = {
            "ID": {"width": 40, "anchor": "center"},
            "Receipt ID": {"width": 130, "anchor": "center"},
            "Customer": {"width": 120, "anchor": "w"},
            "Amount": {"width": 80, "anchor": "e"},
            "Payment": {"width": 80, "anchor": "center"},
            "Date": {"width": 80, "anchor": "center"},
            "Time": {"width": 60, "anchor": "center"}
        }

        for col, config in columns.items():
            self.sales_history_table.heading(col, text=col, anchor=config["anchor"])
            self.sales_history_table.column(col, **config)

        # Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.sales_history_table.yview)
        self.sales_history_table.configure(yscrollcommand=vsb.set)

        # Layout
        self.sales_history_table.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Button at bottom (now properly spaced)
        btn_frame = ttk.Frame(container, style="Cashier.Main.TFrame")
        btn_frame.pack(fill='x', pady=(5, 0))  # Reduced padding
        
        ttk.Button(btn_frame,
                text="View Full History",
                style="Cashier.Button.TButton",
                command=self.view_full_history).pack(side='left')

        # Load initial data
        self.load_todays_sales()

    def load_todays_sales(self):
        """Load today's sales for current cashier"""
        if not hasattr(self, 'sales_history_table') or not self.sales_history_table.winfo_exists():
            return

        # Clear existing data
        for item in self.sales_history_table.get_children():
            self.sales_history_table.delete(item)

        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            # Get sales data for today and current cashier
            sales_data = self.counter_db.get_sales_by_date_and_cashier(
                today, 
                self.app.current_user
            )
            
            if not sales_data:
                self.sales_history_table.insert("", 'end', values=("No sales today", "", "", "", "", "", ""))
                return

            for sale in sales_data:
                sale_time = datetime.strptime(sale['sale_time'], "%Y-%m-%d %H:%M:%S")
                date = sale_time.strftime("%Y-%m-%d")
                time = sale_time.strftime("%H:%M:%S")

                self.sales_history_table.insert("", 'end', values=(
                    sale['id'],
                    sale['receipt_id'],
                    sale['customer_name'],
                    f"PKR {sale['total_amount']:,.2f}",
                    date,
                    time
                ))
        except Exception as e:
            print(f"Error loading today's sales: {e}")
            self.sales_history_table.insert("", 'end', values=("Error loading data", "", "", "", "", "", ""))

    def view_full_history(self):
        """Show full sales history with real-time search"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title(f"Sales History - {self.app.current_user}")
        dialog.geometry("900x650")
        dialog.minsize(700, 450)

        # Make this window stay on top of main window
        dialog.transient(self.app.root)
        dialog.attributes('-topmost', True)  # This is key for keeping it on top
        
        # Center dialog
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - 450
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - 325
        dialog.geometry(f"+{x}+{y}")

        # Force focus to this window
        dialog.focus_force()
        
        # Store reference to this dialog as an instance variable
        self.history_window = dialog

        # Rest of your view_full_history implementation...
        container = ttk.Frame(dialog, style="Cashier.Main.TFrame")
        container.pack(fill='both', expand=True, padx=10, pady=10)

        # Title with cashier name
        ttk.Label(container,
                text=f"Sales History for {self.app.current_user}",
                style="Cashier.Dashboard.Title.TLabel").pack(anchor='w', pady=(0, 10))

        # Search frame
        search_frame = ttk.Frame(container, style="Cashier.Main.TFrame")
        search_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(search_frame,
                text="Search (Receipt ID or Customer):",
                style="Cashier.Label.TLabel").pack(side='left', padx=(0, 5))

        self.history_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame,
                            textvariable=self.history_search_var,
                            style="Cashier.Entry.TEntry",
                            width=30)
        search_entry.pack(side='left', padx=5)
        search_entry.focus()

        # Bind KeyRelease to trigger search
        self.history_search_var.trace_add("write", lambda *args: self.filter_history_table(history_table))

        # Table frame
        table_frame = ttk.Frame(container, style="Cashier.Main.TFrame")
        table_frame.pack(fill='both', expand=True)

        # Create history table
        history_table = ttk.Treeview(
            table_frame,
            columns=("ID", "Receipt ID", "Customer", "Amount", "Payment", "Date", "Time"),
            show='headings',
            style="Custom.Treeview"
        )

        # Configure columns
        columns = {
            "ID": {"width": 50, "anchor": "center"},
            "Receipt ID": {"width": 120, "anchor": "center"},
            "Customer": {"width": 150, "anchor": "w"},
            "Amount": {"width": 100, "anchor": "e"},
            "Payment": {"width": 100, "anchor": "center"},
            "Date": {"width": 100, "anchor": "center"},
            "Time": {"width": 80, "anchor": "center"}
        }

        for col, config in columns.items():
            history_table.heading(col, text=col)
            history_table.column(col, **config)

        # Store all sales data for filtering
        self.all_sales_data = self.counter_db.get_sales_by_cashier(self.app.current_user)

        # Add data to table
        self.filter_history_table(history_table)

        # Add double-click binding
        # In your view_full_history method, modify the binding:
        history_table.bind("<Double-1>", lambda e: self.show_selected_receipt(e, history_table, dialog))

        # Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=history_table.yview)
        history_table.configure(yscrollcommand=vsb.set)

        # Grid layout
        history_table.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Close button
        btn_frame = ttk.Frame(container, style="Cashier.Main.TFrame")
        btn_frame.pack(fill='x', pady=(10, 0))

        ttk.Button(btn_frame,
                text="Close",
                style="Cashier.Button.TButton",
                command=dialog.destroy).pack(side='right')
        
    def filter_history_table(self, table):
        """Filter the history table based on current search text"""
        # Get current search text
        search_text = self.history_search_var.get().lower()
        
        # Clear existing data
        for item in table.get_children():
            table.delete(item)

        if not search_text:
            # Show all data if search is empty
            sales_data = self.all_sales_data
        else:
            # Filter data
            sales_data = [
                sale for sale in self.all_sales_data
                if (search_text in sale['receipt_id'].lower() or 
                    (sale['customer_name'] and search_text in sale['customer_name'].lower()))
            ]

        # Add filtered data to table
        for sale in sales_data:
            sale_time = datetime.strptime(sale['sale_time'], "%Y-%m-%d %H:%M:%S")
            date = sale_time.strftime("%Y-%m-%d")
            time = sale_time.strftime("%H:%M:%S")

            table.insert("", 'end', values=(
                sale['id'],
                sale['receipt_id'],
                sale['customer_name'],
                f"PKR {sale['total_amount']:,.2f}",
                date,
                time
            ))

        # Show message if no results found
        if not sales_data:
            table.insert("", 'end', values=("No matching sales found", "", "", "", "", "", ""))

    def show_selected_receipt(self, event, table=None, parent_window=None):
        """Show receipt for selected sale entry"""
        # Determine which table was clicked
        table = table if table else self.sales_history_table
        
        # Get selected item
        selected = table.selection()
        if not selected:
            return
            
        # Get sale data
        item = table.item(selected[0])
        sale_id = item['values'][0]  # First column is ID
        
        try:
            # Get complete sale details
            sale_data = self.counter_db.get_sale_details(sale_id)
            if not sale_data:
                raise Exception("Sale not found")
            
            # Prepare receipt data
            receipt_data = {
                'receipt_id': sale_data['receipt_id'],
                'date_time': sale_data['sale_time'],
                'cashier': sale_data['cashier_name'],
                'customer': sale_data['customer_name'] or "Walk-in Customer",
                'items': [
                    {
                        'name': item['product_name'],
                        'quantity': item['quantity'],
                        'price': item['unit_price'],
                        'total': item['total_price']
                    }
                    for item in sale_data['items']
                ],
                'total': sale_data['total_amount'],
            }
            
            # Show receipt with the parent_window parameter
            self.show_receipt(receipt_data, parent_window)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load receipt: {str(e)}")

    def complete_sale(self):
        """Complete the current sale and generate receipt"""
        if not self.current_cart:
            messagebox.showwarning("Warning", "Cart is empty")
            return
            
        if not self.current_customer:
            messagebox.showwarning("Warning", "Please select a customer")
            return

        try:
            # Get current counter info - THIS IS CRUCIAL
            counters = self.counter_db.get_counters()
            if not counters:
                raise Exception("No counters available in the system")
                
            # Use the first active counter if available
            active_counters = [c for c in counters if c.get('status', '').lower() == 'active']
            if not active_counters:
                raise Exception("No active counters available")
                
            counter = active_counters[0]  # Use first active counter
            counter_id = counter['id']
            cashier_id = counter['cashier_id']  # Get from counter data

            # Generate receipt data
            receipt_id = f"RCPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            total_amount = sum(item['total'] for item in self.current_cart)
            sale_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Prepare sale data with valid counter_id
            sale_data = {
                'receipt_id': receipt_id,
                'counter_id': counter_id,  # Use valid counter_id
                'cashier_id': cashier_id,  # Use from counter data
                'cashier_name': self.app.current_user,
                'customer_name': self.current_customer['name'],
                'total_amount': total_amount,
                'items': [
                    {
                        'product_id': item['id'],
                        'product_name': item['name'],
                        'quantity': item['quantity'],
                        'unit_price': item['price'],
                        'total_price': item['total']
                    }
                    for item in self.current_cart
                ]
            }
            
            # Record sale
            result = self.counter_db.record_sale(sale_data)
            if not result['success']:
                raise Exception(result['error'])
                
            # Update inventory and refresh product display
            updated_products = []
            for item in self.current_cart:
                update_success = self.db.update_product_quantity(
                    item['id'],
                    -item['quantity']
                )
                if not update_success:
                    raise Exception(f"Failed to update inventory for product {item['id']}")
                updated_products.append(item['id'])
            
            # Refresh the products that were updated
            self.refresh_products(updated_products)
            
            # Generate and show receipt
            receipt_data = {
                'receipt_id': receipt_id,
                'date_time': sale_time,
                'cashier': self.app.current_user,
                'customer': self.current_customer['name'],
                'items': self.current_cart,
                'total': total_amount,
            }
            self.show_receipt(receipt_data)
            
            # Clear cart and refresh sales
            self.current_cart = []
            self.current_customer = None
            self.update_cart_display()
            self.update_customer_display()
            self.load_todays_sales()  # Refresh the sales table
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete sale: {str(e)}")
            messagebox.showerror("Error", f"Failed to complete sale: {str(e)}")
                
    def refresh_products(self, product_ids=None):
        """Refresh specific products or all products if None"""
        current_search = self.search_entry.get()
        if current_search:
            self.search_products()  # Refresh with current search
        else:
            self.load_all_products()  # Full refresh

    def delete_selected_item(self):
        """Delete the selected item from cart"""
        selected = self.cart_table.selection()
        if not selected:
            messagebox.showwarning("Warning", "No item selected")
            return
            
        item_id = self.cart_table.index(selected[0])
        del self.current_cart[item_id]
        self.update_cart_display()

    def edit_selected_item(self):
        """Edit the selected item's quantity"""
        selected = self.cart_table.selection()
        if not selected:
            messagebox.showwarning("Warning", "No item selected")
            return
        
        item_id = self.cart_table.index(selected[0])
        item = self.current_cart[item_id]
        
        # Create edit dialog
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Edit Item Quantity")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - 150
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - 100
        dialog.geometry(f"+{x}+{y}")
        
        container = ttk.Frame(dialog, style="Cashier.Main.TFrame")
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(container,
                text=f"Editing: {item['name']}",
                style="Cashier.Label.TLabel").pack(pady=5)
        
        ttk.Label(container,
                text=f"Current Price: PKR {item['price']:,.2f}",
                style="Cashier.Label.TLabel").pack(pady=5)
        
        # Quantity controls
        quantity_frame = ttk.Frame(container, style="Cashier.Main.TFrame")
        quantity_frame.pack(pady=10)
        
        ttk.Label(quantity_frame,
                text="New Quantity:",
                style="Cashier.Label.TLabel").pack(side='left', padx=(0, 10))
        
        quantity_var = tk.StringVar(value=str(item['quantity']))
        quantity_entry = ttk.Entry(quantity_frame,
                            textvariable=quantity_var,
                            style="Cashier.Entry.TEntry",
                            width=8,
                            justify='center')
        quantity_entry.pack(side='left')
        quantity_entry.focus()
        quantity_entry.select_range(0, tk.END)
        
        # Action buttons
        btn_frame = ttk.Frame(container, style="Cashier.Main.TFrame")
        btn_frame.pack(side='bottom', pady=(15, 0))
        
        ttk.Button(btn_frame,
                text="Cancel",
                style="Cashier.Dialog.Neutral.TButton",
                command=dialog.destroy).pack(side='left', padx=5)
        
        ttk.Button(btn_frame,
                text="Update",
                style="Cashier.Button.TButton",
                command=lambda: self.update_item_quantity(
                    item_id, quantity_var.get(), dialog)
                ).pack(side='right', padx=5)
        
        dialog.bind("<Return>", lambda e: self.update_item_quantity(
            item_id, quantity_var.get(), dialog))
        dialog.bind("<Escape>", lambda e: dialog.destroy())

    def update_item_quantity(self, item_id, new_quantity, dialog):
        """Update the quantity of an item in the cart"""
        try:
            quantity = int(new_quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
                
            self.current_cart[item_id]['quantity'] = quantity
            self.current_cart[item_id]['total'] = self.current_cart[item_id]['price'] * quantity
            self.update_cart_display()
            dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid quantity: {str(e)}")
    def cancel_sale(self):
        """Cancel the current sale or clear customer if cart is empty"""
        if not self.current_cart and not self.current_customer:
            return
            
        if not self.current_cart:
            # If cart is empty but customer is selected, just clear customer
            self.current_customer = None
            self.update_customer_display()
            return
            
        if messagebox.askyesno("Cancel Sale", "Are you sure you want to cancel this sale?"):
            self.current_cart = []
            self.current_customer = None
            self.update_cart_display()
            self.update_customer_display()

    def print_receipt(self):
        """Print the current receipt"""
        if not self.current_cart:
            messagebox.showwarning("Warning", "Cart is empty")
            return
            
        total = sum(item['total'] for item in self.current_cart)
        transaction = {
            'time': datetime.now().strftime("%H:%M:%S"),
            'customer': self.current_customer['name'] if self.current_customer else "Walk-in",
            'items': len(self.current_cart),
            'total': total,
            'details': self.current_cart.copy()
        }
        
        self.show_receipt(transaction)

    def update_sales_history(self):
        """Update the sales history display"""
        for item in self.sales_history_table.get_children():
            self.sales_history_table.delete(item)
        
        for sale in self.sales_history:
            self.sales_history_table.insert("", 'end', values=(
                sale['time'],
                sale['customer'],
                sale['items'],
                f"PKR {sale['total']:,.2f}"
            ))

    def load_sample_sales_history(self):
        """Load sample sales history data"""
        sample_sales = [
            {'time': '10:15:22', 'customer': 'Ali Khan', 'items': 3, 'total': 4500.00},
            {'time': '11:30:45', 'customer': 'Walk-in', 'items': 5, 'total': 6250.75},
            {'time': '12:45:10', 'customer': 'Sara Ahmed', 'items': 2, 'total': 3200.50},
        ]
        
        self.sales_history = sample_sales
        self.update_sales_history()

    # ======================
    # RECEIPT MANAGEMENT
    # ======================
        
    def show_receipt(self, receipt_data, parent_window=None):
        """Display receipt while keeping parent window on top"""
        dialog = tk.Toplevel(parent_window if parent_window else self.app.root)
        dialog.title(f"Receipt #{receipt_data['receipt_id']}")
        dialog.geometry("380x680")
        dialog.resizable(False, True)
        
        # Configure window hierarchy
        if parent_window:
            dialog.transient(parent_window)
            # Keep parent window on top of main window
            parent_window.lift()
            parent_window.focus_force()
        
        # Configure the receipt window
        dialog.attributes('-topmost', True)  # Temporarily force on top
        dialog.grab_set()  # Make it modal
        
        # Center the dialog
        if parent_window:
            x = parent_window.winfo_x() + (parent_window.winfo_width() // 2) - 190
            y = parent_window.winfo_y() + (parent_window.winfo_height() // 2) - 340
        else:
            x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - 190
            y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - 340
        dialog.geometry(f"+{x}+{y}")
        
        # After showing, adjust attributes to maintain proper stacking
        def adjust_stack():
            dialog.attributes('-topmost', False)
            if parent_window:
                parent_window.lift()
                dialog.lift(parent_window)
        
        dialog.after(100, adjust_stack) # Make it modal

        # Center dialog relative to parent
        if parent_window:
            x = parent_window.winfo_x() + (parent_window.winfo_width() // 2) - 190
            y = parent_window.winfo_y() + (parent_window.winfo_height() // 2) - 340
        else:
            x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - 190
            y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - 340
        dialog.geometry(f"+{x}+{y}")
        dialog.focus_set()
        
        # Make the dialog stay on top and modal
        dialog.transient(self.app.root)  # Set as child of main window
        dialog.grab_set()  # Make it modal

        # Center dialog
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - 190
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - 340
        dialog.geometry(f"+{x}+{y}")
        dialog.focus_set()

        # Main container
        main_frame = ttk.Frame(dialog, style='Receipt.Frame.TFrame')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Header
        header_frame = ttk.Frame(main_frame, style='Receipt.Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(header_frame,
                text="INVENTORY PRO",
                style='Receipt.Title.TLabel',
                background='white').pack()  # Explicit white background
        ttk.Label(header_frame,
                text="SALES RECEIPT",
                style='Receipt.Subtitle.TLabel',
                background='white').pack()

        # Receipt details
        details_frame = ttk.Frame(main_frame, style='Receipt.Details.TFrame')
        details_frame.pack(fill='x', pady=(0, 15))

        ttk.Label(details_frame,
                text=f"Receipt #: {receipt_data['receipt_id']}",
                style='Receipt.Detail.TLabel',
                background='white').pack(anchor='w')
        ttk.Label(details_frame,
                text=f"Date: {receipt_data['date_time'].split()[0]}",
                style='Receipt.Detail.TLabel',
                background='white').pack(anchor='w')
        ttk.Label(details_frame,
                text=f"Time: {receipt_data['date_time'].split()[1]}",
                style='Receipt.Detail.TLabel',
                background='white').pack(anchor='w')
        ttk.Label(details_frame,
                text=f"Cashier: {receipt_data['cashier']}",
                style='Receipt.Detail.TLabel',
                background='white').pack(anchor='w')
        ttk.Label(details_frame,
                text=f"Customer: {receipt_data['customer']}",
                style='Receipt.Detail.TLabel',
                background='white').pack(anchor='w')

        # Divider
        ttk.Label(main_frame,
                text="-"*50,
                style='Receipt.Divider.TLabel',
                background='white').pack(fill='x', pady=5)

        # Define column widths and alignments
        COLUMN_SPECS = {
            'item': {'width': 25, 'anchor': 'w', 'padx': 0},
            'qty': {'width': 7, 'anchor': 'center', 'padx': 2},
            'price': {'width': 12, 'anchor': 'e', 'padx': 2},
            'total': {'width': 12, 'anchor': 'e', 'padx': 0}
        }

        # Items header frame - using grid for precise control
        items_header = ttk.Frame(main_frame, style='Receipt.Items.TFrame')
        items_header.pack(fill='x', pady=(0, 3))  # Reduced pady for tighter spacing
        
        # Column headings using grid layout
        ttk.Label(items_header, text="ITEM",
                style='Receipt.ColumnHeader.TLabel',
                width=COLUMN_SPECS['item']['width'],
                anchor=COLUMN_SPECS['item']['anchor']).grid(
                    row=0, column=0, 
                    padx=COLUMN_SPECS['item']['padx'],
                    sticky='ew')
        
        ttk.Label(items_header, text="QTY",
                style='Receipt.ColumnHeader.TLabel',
                width=COLUMN_SPECS['qty']['width'],
                anchor=COLUMN_SPECS['qty']['anchor']).grid(
                    row=0, column=1,
                    padx=COLUMN_SPECS['qty']['padx'],
                    sticky='ew')
        
        ttk.Label(items_header, text="PRICE",
                style='Receipt.ColumnHeader.TLabel',
                width=COLUMN_SPECS['price']['width'],
                anchor=COLUMN_SPECS['price']['anchor']).grid(
                    row=0, column=2,
                    padx=COLUMN_SPECS['price']['padx'],
                    sticky='ew')
        
        ttk.Label(items_header, text="TOTAL",
                style='Receipt.ColumnHeader.TLabel',
                width=COLUMN_SPECS['total']['width'],
                anchor=COLUMN_SPECS['total']['anchor']).grid(
                    row=0, column=3,
                    padx=COLUMN_SPECS['total']['padx'],
                    sticky='e')

        # Configure column weights for the header
        items_header.grid_columnconfigure(0, weight=1)
        items_header.grid_columnconfigure(1, weight=0)
        items_header.grid_columnconfigure(2, weight=0)
        items_header.grid_columnconfigure(3, weight=0)

        # Items list - using same grid layout for perfect alignment
        for item in receipt_data['items']:
            item_frame = ttk.Frame(main_frame, style='Receipt.Items.TFrame')
            item_frame.pack(fill='x', pady=1)
            
            name = (item['name'][:22] + '...') if len(item['name']) > 25 else item['name']
            
            # Item name
            ttk.Label(item_frame, text=name,
                    style='Receipt.Item.TLabel',
                    width=COLUMN_SPECS['item']['width'],
                    anchor=COLUMN_SPECS['item']['anchor']).grid(
                        row=0, column=0,
                        padx=COLUMN_SPECS['item']['padx'],
                        sticky='w')
            
            # Quantity
            ttk.Label(item_frame, text=f"{item['quantity']:2d}",
                    style='Receipt.Number.TLabel',
                    width=COLUMN_SPECS['qty']['width'],
                    anchor=COLUMN_SPECS['qty']['anchor']).grid(
                        row=0, column=1,
                        padx=COLUMN_SPECS['qty']['padx'],
                        sticky='ew')
            
            # Price
            ttk.Label(item_frame, text=f"{item['price']:>{COLUMN_SPECS['price']['width']-3},.2f}",
                    style='Receipt.Number.TLabel',
                    width=COLUMN_SPECS['price']['width'],
                    anchor=COLUMN_SPECS['price']['anchor']).grid(
                        row=0, column=2,
                        padx=COLUMN_SPECS['price']['padx'],
                        sticky='e')
            
            # Total
            ttk.Label(item_frame, text=f"{item['total']:>{COLUMN_SPECS['total']['width']-3},.2f}",
                    style='Receipt.Number.TLabel',
                    width=COLUMN_SPECS['total']['width'],
                    anchor=COLUMN_SPECS['total']['anchor']).grid(
                        row=0, column=3,
                        padx=COLUMN_SPECS['total']['padx'],
                        sticky='e')

            # Configure column weights for item row
            item_frame.grid_columnconfigure(0, weight=1)
            item_frame.grid_columnconfigure(1, weight=0)
            item_frame.grid_columnconfigure(2, weight=0)
            item_frame.grid_columnconfigure(3, weight=0)

        # Divider
        ttk.Label(main_frame,
                text="-"*50,
                style='Receipt.Divider.TLabel',
                background='white').pack(fill='x', pady=5)

        # Totals
        totals_frame = ttk.Frame(main_frame, style='Receipt.Totals.TFrame')
        totals_frame.pack(fill='x', pady=(5, 10))
        
        ttk.Label(totals_frame, text="TOTAL:",
                style='Receipt.Total.TLabel',
                background='white').pack(side='left')
        ttk.Label(totals_frame, text=f"PKR {receipt_data['total']:,.2f}",
                style='Receipt.Total.TLabel',
                background='white').pack(side='right')

        # Footer
        ttk.Label(main_frame,
                text="Thank you for your business!",
                style='Receipt.Footer.TLabel',
                background='white').pack(pady=(10, 0))

        # Buttons
        btn_frame = ttk.Frame(main_frame, style='Receipt.Buttons.TFrame')
        btn_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Button(btn_frame, text="Print",
                style='Receipt.Button.TButton',
                command=lambda: self.print_receipt(receipt_data)).pack(side='left', padx=5)

        ttk.Button(btn_frame, text="Save PDF",
                style='Receipt.Button.TButton',
                command=lambda: self.save_receipt_pdf(receipt_data)).pack(side='left', padx=5)

        ttk.Button(btn_frame, text="Close",
                style='Receipt.CloseButton.TButton',
                command=dialog.destroy).pack(side='right', padx=5)
        
    def print_receipt(self, receipt_data):
        """Print the receipt using system printer"""
        try:
            # Create a temporary PDF
            pdf_path = os.path.join(os.getcwd(), "temp_receipt.pdf")
            self.generate_pdf_receipt(receipt_data, pdf_path)
            
            # Print the PDF
            printer_name = win32print.GetDefaultPrinter()
            win32api.ShellExecute(
                0,
                "print",
                pdf_path,
                f'/d:"{printer_name}"',
                ".",
                0
            )
            messagebox.showinfo("Print", "Receipt sent to printer")
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print receipt: {str(e)}")

    def save_receipt_pdf(self, receipt_data):
        """Save receipt as PDF file using a file dialog"""
        try:
            # Ask user where to save the PDF
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                initialfile=f"receipt_{receipt_data['receipt_id']}.pdf"
            )
            
            if file_path:  # If user didn't cancel
                self.generate_pdf_receipt(receipt_data, file_path)
                messagebox.showinfo("Save", f"Receipt saved successfully at:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save receipt: {str(e)}")

    def generate_pdf_receipt(self, receipt_data, file_path):
        """Generate properly sized PDF receipt with perfect column alignment"""
        # Page dimensions (80mm width)
        width = 226.8  # 80mm in points (1mm = 2.835 points)
        height = 500   # Initial height
        
        c = canvas.Canvas(file_path, pagesize=(width, height))
        current_y = height - 40  # Start position
        
        # Header
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width/2, current_y, "INVENTORY PRO")
        current_y -= 20
        
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width/2, current_y, "SALES RECEIPT")
        current_y -= 25
        
        # Receipt details
        c.setFont("Helvetica", 8)
        # Split date_time into date and time if it's a string
        if isinstance(receipt_data['date_time'], str):
            date_part = receipt_data['date_time'].split()[0] if ' ' in receipt_data['date_time'] else receipt_data['date_time']
            time_part = receipt_data['date_time'].split()[1] if ' ' in receipt_data['date_time'] else ''
        else:
            date_part = receipt_data['date_time'].strftime("%Y-%m-%d")
            time_part = receipt_data['date_time'].strftime("%H:%M:%S")
        
        details = [
            f"Receipt #: {receipt_data['receipt_id']}",
            f"Date: {date_part}",
            f"Time: {time_part}",
            f"Cashier: {receipt_data['cashier']}",
            f"Customer: {receipt_data['customer'] or 'Walk-in Customer'}"
        ]
        
        for detail in details:
            c.drawString(20, current_y, detail)
            current_y -= 15
        
        current_y -= 10  # Extra space
        
        # Divider line
        c.line(10, current_y, width-10, current_y)
        current_y -= 15
        
        # Define column positions (aligned with data below)
        col_positions = {
            'item': 15,       # Left-aligned
            'qty': 120,       # Right edge of quantity
            'price': 150,     # Right edge of price
            'total': width-15 # Right edge of page
        }
        
        # Column headers - aligned exactly with data columns
        c.setFont("Helvetica-Bold", 8)
        c.drawString(col_positions['item'], current_y, "ITEM")
        c.drawRightString(col_positions['qty'], current_y, "QTY")  # Right-aligned
        c.drawRightString(col_positions['price'], current_y, "PRICE")  # Right-aligned
        c.drawRightString(col_positions['total'], current_y, "TOTAL")  # Right-aligned
        current_y -= 15
        
        # Items list - perfectly aligned with headers
        c.setFont("Helvetica", 8)
        for item in receipt_data['items']:
            # Item name (truncate if too long)
            name = (item['name'][:18] + '...') if len(item['name']) > 21 else item['name']
            c.drawString(col_positions['item'], current_y, name)
            
            # Quantity - right-aligned to header
            c.drawRightString(col_positions['qty'], current_y, str(item['quantity']))
            
            # Price - right-aligned to header with 2 decimal places
            c.drawRightString(col_positions['price'], current_y, f"{item['price']:,.2f}")
            
            # Total - right-aligned to header with 2 decimal places
            c.drawRightString(col_positions['total'], current_y, f"{item['total']:,.2f}")
            
            current_y -= 12
        
        current_y -= 8  # Space before total
        
        # Divider line
        c.line(10, current_y, width-10, current_y)
        current_y -= 15
        
        # Total - aligned with item columns
        c.setFont("Helvetica-Bold", 9)
        c.drawString(col_positions['item'], current_y, "TOTAL:")
        c.drawRightString(col_positions['total'], current_y, f"PKR {receipt_data['total']:,.2f}")
        current_y -= 15
        
        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(width/2, current_y, "Thank you for your business!")
        
        c.showPage()
        c.save()

    # ======================
    # UTILITY METHODS
    # ======================
    
    def create_dialog(self, title, width=400, height=300):
        """Create a base dialog window"""
        dialog = tk.Toplevel(self.app.root)
        dialog.title(title)
        dialog.geometry(f"{width}x{height}")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.focus_set()
        dialog.grab_set()
        dialog.configure(background='#ffffff')
        
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - (width // 2)
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - (height // 2)
        dialog.geometry(f"+{x}+{y}")
        
        container = ttk.Frame(dialog, style='Inventory.Dialog.TFrame')
        container.pack(fill='both', expand=True, padx=10, pady=10)
        
        return dialog, container
    
    def schedule_auto_refresh(self):
        """Schedule automatic refresh of sales data"""
        if hasattr(self, 'sales_history_table') and self.sales_history_table.winfo_exists():
            try:
                self.load_todays_sales()
            except Exception as e:
                print(f"Error in auto-refresh: {e}")
        
        # Only schedule next refresh if the window still exists
        if hasattr(self, 'frame') and self.frame.winfo_exists():
            self.frame.after(self.auto_refresh_interval, self.schedule_auto_refresh)

    def update_time(self):
        """Update the current time display"""
        if hasattr(self, 'time_label') and self.time_label.winfo_exists():
            now = datetime.now()
            time_str = now.strftime("%a %d %b %Y\n%I:%M:%S %p")  # New format
            self.time_label.config(text=time_str)
            self.frame.after(1000, self.update_time)