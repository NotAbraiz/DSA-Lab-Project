from tkinter import ttk
from tkinter import font as tkfont

def apply_styles():
    """Apply all styles to the application"""
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure default font
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=10)
    
    # Apply all style groups
    configure_base_styles(style)
    configure_login_styles(style)
    configure_sidebar_styles(style)
    configure_dashboard_styles(style)
    configure_inventory_styles(style)
    configure_cashier_styles(style)
    configure_dialog_styles(style)
    configure_treeview_styles(style)
    configure_scrollbar_styles(style)
    configure_receipt_styles(style)

# ======================
# BASE STYLES
# ======================
# In styles.py - Update label styles
def configure_base_styles(style):
    """Configure base styles with consistent backgrounds"""
    style.configure('TLabel', background='#f5f7fa', foreground='#263238')
    style.configure('TFrame', background='#f5f7fa')
    
    # Specific label styles
    style.configure('Header.TLabel',
                  font=('Segoe UI', 12, 'bold'),
                  background='#f5f7fa',
                  foreground='#263238')
    
    style.configure('Value.TLabel',
                  font=('Segoe UI', 14),
                  background='#f5f7fa',
                  foreground='#00bcd4')

# ======================
# LOGIN PAGE STYLES
# ======================
def configure_login_styles(style):
    """Configure login page styles"""
    # Login Panels
    style.configure('Login.LeftPanel.TFrame', background='#263238')
    style.configure('Login.RightPanel.TFrame', background='white')
    
    # Login Labels
    style.configure('Login.Title.TLabel', 
                  font=('Segoe UI', 22, 'bold'), 
                  foreground='white', 
                  background='#263238')
    
    style.configure('Login.Highlight.TLabel', 
                  font=('Segoe UI', 14, 'bold'), 
                  foreground='#00bcd4', 
                  background='#263238')
    
    style.configure('Login.Subheading.TLabel', 
                   font=('Segoe UI', 12, 'bold'), 
                   foreground='white', 
                   background='#263238')
    
    style.configure('Login.Body.TLabel', 
                   font=('Segoe UI', 10), 
                   foreground='white', 
                   background='#263238')
    
    style.configure('Login.Heading.TLabel', 
                   font=('Segoe UI', 14, 'bold'), 
                   foreground='#00bcd4', 
                   background='white')
    
    style.configure('Login.Note.TLabel', 
                   font=('Segoe UI', 9), 
                   foreground='gray', 
                   background='white')
    
    style.configure('Login.Label.TLabel', 
                   font=('Segoe UI', 10),
                   background='white')
    
    # Login Entry
    style.configure('Login.Entry.TEntry',
                   font=('Segoe UI', 10),
                   padding=8,
                   foreground='#212121',
                   fieldbackground='#f5f5f5',
                   borderwidth=1,
                   relief='flat')
    
    style.map('Login.Entry.TEntry',
             fieldbackground=[('focus', '#ffffff')],
             bordercolor=[('focus', '#00bcd4')],
             foreground=[('disabled', 'gray')])
    
    # Login Button
    style.configure('Login.Button.TButton',
                   font=('Segoe UI', 10, 'bold'),
                   padding=(10, 6),
                   borderwidth=0,
                   relief='flat',
                   background='#00bcd4',
                   foreground='white')
    
    style.map('Login.Button.TButton',
             background=[('active', '#0097a7'), ('disabled', '#b0bec5')],
             foreground=[('disabled', 'white')])

# ======================
# SIDEBAR STYLES
# ======================
def configure_sidebar_styles(style):
    """Configure sidebar styles"""
    # Sidebar Frames
    style.configure('App.Sidebar.TFrame', 
                  background='#263238',
                  borderwidth=0)
    
    style.configure('App.Sidebar.Active.TFrame', 
                  background='white',
                  borderwidth=0)
    
    style.configure('App.Sidebar.Hover.TFrame',
                  background='#37474f',
                  borderwidth=0)

    # Sidebar Buttons
    sidebar_button_padding = (10, 6)
    style.configure('App.Sidebar.Button.TButton',
                  font=('Segoe UI', 10),
                  background='#263238',
                  foreground='white',
                  relief='flat',
                  padding=sidebar_button_padding,
                  anchor='w',
                  borderwidth=0)
    
    style.map('App.Sidebar.Button.TButton',
             background=[('active', '#37474f')],
             foreground=[('active', 'white')])
    
    style.configure('App.Sidebar.Button.Active.TButton',
                  font=('Segoe UI', 10),
                  background='white',
                  foreground='#00bcd4',
                  relief='flat',
                  padding=sidebar_button_padding,
                  anchor='w',
                  borderwidth=0)
    
    style.map('App.Sidebar.Button.Active.TButton',
             background=[('active', '#f0f0f0')],
             foreground=[('active', '#00bcd4')])

    # Sidebar Icons
    style.configure('App.Sidebar.Icon.TLabel',
                  background='#263238',
                  foreground='white',
                  borderwidth=0,
                  padding=0)
    
    style.configure('App.Sidebar.Icon.Hover.TLabel',
                  background='#37474f',
                  foreground='white',
                  borderwidth=0,
                  padding=0)
    
    style.configure('App.Sidebar.Icon.Active.TLabel',
                  background='white',
                  foreground='#00bcd4',
                  borderwidth=0,
                  padding=0)

# ======================
# DASHBOARD STYLES
# ======================

# ======================
# INVENTORY STYLES
# ======================
def configure_inventory_styles(style):
    """Configure inventory management styles"""
    # Inventory Main Frame
    style.configure('Inventory.Main.TFrame', background='#f8f9fa')
    
    # Inventory Labels
    style.configure('Inventory.Label.TLabel', 
                  background='#f8f9fa', 
                  font=('Segoe UI', 9))
    
    # Inventory Buttons
    style.configure('Inventory.Button.TButton', 
                  font=('Segoe UI', 9, 'bold'),
                  background='#00bcd4',
                  foreground='white',
                  borderwidth=0,
                  padding=6)
    
    style.map('Inventory.Button.TButton',
             background=[('active', '#2e59d9'), ('disabled', '#cccccc')],
             foreground=[('disabled', '#888888')])
    
    # Inventory Entry Fields
    style.configure('Inventory.Entry.TEntry',
                  fieldbackground='white',
                  bordercolor='#d1d3e2',
                  lightcolor='#d1d3e2',
                  darkcolor='#d1d3e2',
                  padding=5,
                  relief='flat')
    
    style.map('Inventory.Entry.TEntry',
             bordercolor=[('focus', '#4e73df')],
             lightcolor=[('focus', '#4e73df')],
             darkcolor=[('focus', '#4e73df')])
    
    # Inventory Combobox
    style.configure('Inventory.Combobox.TCombobox',
                  fieldbackground='white',
                  background='white',
                  arrowcolor='#4e73df',
                  padding=5)
    
    style.map('Inventory.Combobox.TCombobox',
             fieldbackground=[('readonly', 'white')],
             background=[('readonly', 'white')])
    
    # Inventory Status Bar
    style.configure('Inventory.StatusBar.TLabel',
                  background='#4e73df',
                  foreground='white',
                  font=('Segoe UI', 9),
                  padding=(5, 3))

# ======================
# CASHIER POS STYLES
# ======================
def configure_cashier_styles(style):
    """Configure cashier POS styles"""
    # Cashier Main Frame
    style.configure("Cashier.Value.TLabel", 
                font=('Segoe UI', 9), 
                background="#ffffff",
                foreground="#000000")
    style.configure('Cashier.Detail.Notebook.TNotebook',
                background='white',
                borderwidth=0)

    style.configure('Cashier.Detail.Notebook.Tab',
                    font=('Segoe UI', 10, 'bold'),
                    background='#e0f7fa',  # light cyan-blue
                    padding=(10, 6))

    style.map('Cashier.Detail.Notebook.Tab',
            background=[('selected', '#00bcd4'), ('active', '#b2ebf2')],
            foreground=[('selected', 'white'), ('!selected', '#263238')])
    style.configure('Cashier.Main.TFrame', background='white')
    
    # Cashier Labels
    style.configure('Cashier.Label.TLabel', 
                  background='white', 
                  font=('Segoe UI', 10))
    
    style.configure("Cashier.SectionHeader.TLabel", 
                font=('Segoe UI', 11, 'bold'), 
                background="#f0f0f0",
                foreground="#333333")
    # Cashier Buttons
    style.configure('Cashier.Button.TButton', 
                  font=('Segoe UI', 9, 'bold'),
                  background='#00bcd4',
                  foreground='white',
                  borderwidth=0,
                  padding=6)
    
    style.map('Cashier.Button.TButton',
             background=[('active', '#2e59d9'), ('disabled', '#cccccc')],
             foreground=[('disabled', '#888888')])
    
    # Cashier Entry Fields
    style.configure('Cashier.Entry.TEntry',
                  fieldbackground='white',
                  bordercolor='#d1d3e2',
                  lightcolor='#d1d3e2',
                  darkcolor='#d1d3e2',
                  padding=5,
                  relief='flat')
    
    style.map('Cashier.Entry.TEntry',
             bordercolor=[('focus', '#4e73df')],
             lightcolor=[('focus', '#4e73df')],
             darkcolor=[('focus', '#4e73df')])
    
    # Cashier Total Label
    style.configure('Cashier.Total.TLabel',
                  font=('Segoe UI', 12, 'bold'),
                  foreground='#00bcd4',
                  background='white')
    
    # Cashier Notebook
    style.configure('Cashier.Notebook.TNotebook', 
                  background='#f5f7fa',  # Light background
                  borderwidth=0)
    
    style.configure('Cashier.Notebook.Tab',
                  font=('Segoe UI', 10, 'bold'),
                  background='#1e88e5',  # Sidebar blue for inactive tabs
                  foreground='#1e88e5',   # White text for contrast
                  padding=[10, 6],     # Comfortable padding
                  borderwidth=0,
                  focuscolor='#f5f7fa') # No focus color
    
    style.map('Cashier.Notebook.Tab',
             background=[('selected', '#0d47a1')],  # Darker blue for active tab
             foreground=[('selected', 'white')],    # Keep white text
             relief=[('selected', 'flat'), ('!selected', 'flat')])

    style.configure("Cashier.Details.TFrame", background="#ffffff")
    
    # Cashier Dashboard Styles
    style.configure('Cashier.Dashboard.Title.TLabel',
                  font=('Segoe UI', 14, 'bold'),
                  foreground='#263238',
                  background='#f8f9fa')
    
    style.configure('Cashier.Dashboard.Stats.TFrame',
                  background='#f8f9fa')
    
    style.configure('Cashier.Dashboard.Card.TFrame',
                  background='white',
                  borderwidth=1,
                  relief='solid')
    
    style.configure('Cashier.Dashboard.Card.Title.TLabel',
                  font=('Segoe UI', 11, 'bold'),
                  foreground='#263238',
                  background='white')
    
    style.configure('Cashier.Dashboard.Card.Value.TLabel',
                  font=('Segoe UI', 18, 'bold'),
                  foreground='#00bcd4',
                  background='white')
    
    style.configure('Cashier.Dashboard.Section.TLabel',
                  font=('Segoe UI', 12, 'bold'),
                  foreground='#263238',
                  background='#f8f9fa')

# ======================
# RECEIPT STYLES
# ======================
# ======================
# RECEIPT STYLES (UPDATED)
# ======================
# ======================
# RECEIPT STYLES (UPDATED)
# ======================
def configure_receipt_styles(style):
    """Configure receipt styles with improved formatting and visual hierarchy"""
    # Main receipt frame - remove grey background
    style.configure("Receipt.Frame.TFrame", 
                background='white',
                borderwidth=0,
                relief='flat',
                padding=10)
    
    # Header section - remove grey background
    style.configure("Receipt.Header.TFrame", 
                background='white',
                borderwidth=0,
                padding=(0, 0, 10, 0))
    
    # Company name - more prominent
    style.configure('Receipt.Title.TLabel',
                font=('Helvetica', 16, 'bold'),
                foreground='#263238',
                background='white',  # Explicit white background
                padding=(0, 0, 5, 0))
    
    # Receipt type - slightly smaller than title
    style.configure('Receipt.Subtitle.TLabel',
                font=('Helvetica', 13, 'bold'),
                foreground='#00bcd4',
                background='white',
                padding=(0, 0, 15, 0))
    
    # Details section - clean layout
    style.configure("Receipt.Details.TFrame", 
                background='white',
                borderwidth=0,
                padding=(0, 0, 15, 0))
    
    style.configure("Receipt.DetailLabel.TLabel", 
                font=('Helvetica', 10),
                foreground='#5a5c69',  # Softer gray
                background='white',
                anchor='w')  # Left aligned
    
    style.configure("Receipt.DetailValue.TLabel", 
                font=('Helvetica', 10),
                foreground='#263238',  # Darker for values
                background='white',
                anchor='w')  # Left aligned
    
    # Items section - clean table-like layout
    style.configure("Receipt.Items.TFrame", 
                background='white',
                borderwidth=0,
                padding=(0, 0, 10, 0))
    
    # Column headers - subtle but clear
    style.configure('Receipt.ColumnHeader.TLabel',
                  font=('Segoe UI', 9, 'bold'),
                  foreground='#5a5c69',
                  background='white',
                  padding=(0, 0, 0, 2)) 
    
    # Item rows - clean and readable
    style.configure("Receipt.ItemName.TLabel", 
                font=('Helvetica', 9),
                foreground='#263238',  # Dark for readability
                background='white',
                anchor='w')  # Left aligned
    
    style.configure("Receipt.ItemQty.TLabel", 
                font=('Helvetica', 9),
                foreground='#263238',
                background='white',
                anchor='center')  # Centered for quantities
    
    style.configure("Receipt.ItemPrice.TLabel", 
                font=('Helvetica', 9),
                foreground='#263238',
                background='white',
                anchor='e')  # Right aligned for prices
    
    style.configure("Receipt.ItemTotal.TLabel", 
                font=('Helvetica', 9),
                foreground='#263238',
                background='white',
                anchor='e')  # Right aligned for totals
    
    # Totals section - more prominent
    style.configure("Receipt.Totals.TFrame", 
                background='white',
                borderwidth=0,
                padding=(10, 10, 0, 10))
    
    # Total labels - bold and clear
    style.configure("Receipt.TotalLabel.TLabel", 
                font=('Helvetica', 11, 'bold'),
                foreground='#263238',
                background='white',
                anchor='w')  # Left aligned
    
    # Total values - bold and prominent
    style.configure("Receipt.TotalValue.TLabel", 
                font=('Helvetica', 11, 'bold'),
                foreground='#00bcd4',  # Accent color for totals
                background='white',
                anchor='e')  # Right aligned
    
    # Payment method - subtle
    style.configure("Receipt.Payment.TLabel", 
                font=('Helvetica', 9),
                foreground='#5a5c69',
                background='white',
                anchor='w')  # Left aligned
    
    # Footer - subtle thank you message
    style.configure("Receipt.Footer.TLabel", 
                font=('Helvetica', 9, 'italic'),
                foreground='#5a5c69',
                background='white',
                anchor='center')  # Centered
    
    # Divider lines - subtle
    style.configure('Receipt.Divider.TLabel',
                font=('Helvetica', 1),
                foreground='#e0e0e0',
                background='white')
    
    # Action buttons frame
    style.configure("Receipt.Buttons.TFrame", 
                background='white',
                borderwidth=0,
                padding=(10, 0, 0, 0))
    
    # Standard button
    style.configure("Receipt.Button.TButton", 
                font=('Helvetica', 9, 'bold'),
                foreground='white',
                background='#00bcd4',  # Accent color
                borderwidth=0,
                padding=6,
                width=10)
    
    style.map("Receipt.Button.TButton",
            background=[('active', '#0097a7')])  # Darker when pressed
    
    # Close button - less prominent
    style.configure("Receipt.CloseButton.TButton", 
                font=('Helvetica', 9),
                foreground='#5a5c69',
                background='#f5f5f5',
                borderwidth=1,
                relief='flat',
                padding=6,
                width=10)
    
    style.map("Receipt.CloseButton.TButton",
            background=[('active', '#e0e0e0')])
    
    # Receipt Styles
    style.configure('Cashier.Receipt.Frame.TFrame', background='white')
    style.configure('Cashier.Receipt.Header.TLabel',
                font=('Helvetica', 16, 'bold'),
                foreground='#263238',
                background='white')
    style.configure('Cashier.Receipt.Subtitle.TLabel',
                font=('Helvetica', 13, 'bold'),
                foreground='#00bcd4',
                background='white')
    style.configure('Receipt.Detail.TLabel',
                font=('Helvetica', 10),
                foreground='#5a5c69',
                background='white',
                anchor='w')
    style.configure('Cashier.Receipt.Divider.TLabel',
                font=('Helvetica', 1),
                foreground='#e0e0e0',
                background='white')
    style.configure('Receipt.ColumnHeader.TLabel',
                font=('Helvetica', 9, 'bold'),
                foreground='#5a5c69',
                background='white',
                anchor='w')
    # For numeric columns
    style.configure('Receipt.Number.TLabel',
                  font=('Consolas', 9),  # Monospace is crucial
                  foreground='#263238',
                  background='white')
    style.configure('Receipt.Item.TLabel',
                  font=('Segoe UI', 9),
                  foreground='#263238',
                  background='white')
    style.configure('Receipt.Total.TLabel',
                font=('Helvetica', 11, 'bold'),
                foreground='#00bcd4',
                background='white',
                anchor='w')
    style.configure('Receipt.Payment.TLabel',
                font=('Helvetica', 9),
                foreground='#5a5c69',
                background='white',
                anchor='w')
    style.configure('Receipt.Footer.TLabel',
                font=('Helvetica', 9, 'italic'),
                foreground='#5a5c69',
                background='white',
                anchor='center')

# ======================
# DIALOG STYLES
# ======================
def configure_dialog_styles(style):
    """Configure dialog box styles"""
    # Dialog Container
    style.configure('Dialog.TFrame', 
                  background='#ffffff',
                  borderwidth=0,
                  relief='flat')
    
    # Dialog Title
    style.configure('Dialog.Title.TLabel',
                  font=('Segoe UI', 14, 'bold'),
                  foreground='#263238',
                  background='#ffffff',
                  padding=(0, 0, 10, 0))
    
    # Dialog Subtitle/Info
    style.configure('Dialog.Info.TLabel',
                  font=('Segoe UI', 10),
                  foreground='#5a5c69',
                  background='#ffffff',
                  padding=(0, 0, 5, 0))
    
    # Dialog Form Labels
    style.configure('Dialog.Label.TLabel',
                  font=('Segoe UI', 9),
                  foreground='#5a5c69',
                  background='#ffffff',
                  padding=(0, 5, 5, 5),
                  anchor='e')
    
    # Dialog Form Entries
    style.configure('Dialog.Entry.TEntry',
                  font=('Segoe UI', 9),
                  foreground='#212121',
                  fieldbackground='#ffffff',
                  borderwidth=1,
                  relief='solid',
                  padding=5)
    
    style.map('Dialog.Entry.TEntry',
             fieldbackground=[('focus', '#ffffff')],
             bordercolor=[('focus', '#00bcd4')])
    
    # Dialog Form Comboboxes
    style.configure('Dialog.Combobox.TCombobox',
                  font=('Segoe UI', 9),
                  foreground='#212121',
                  fieldbackground='#ffffff',
                  background='#ffffff',
                  arrowcolor='#00bcd4',
                  padding=5)
    
    style.map('Dialog.Combobox.TCombobox',
             fieldbackground=[('readonly', 'white')],
             background=[('readonly', 'white')])
    
    # Dialog Button Frame
    style.configure('Dialog.ButtonFrame.TFrame',
                  background='#ffffff',
                  borderwidth=0,
                  padding=(0, 10, 0, 0))
    
    # Dialog Buttons
    style.configure('Dialog.Button.TButton',
                  font=('Segoe UI', 9, 'bold'),
                  background='#00bcd4',
                  foreground='white',
                  borderwidth=0,
                  padding=(10, 5))
    
    style.map('Dialog.Button.TButton',
             background=[('active', '#0097a7'), ('disabled', '#b0bec5')],
             foreground=[('disabled', 'white')])
    
    # Dialog Danger Button (for delete actions)
    style.configure('Dialog.Danger.TButton',
                  font=('Segoe UI', 9, 'bold'),
                  background='#f44336',
                  foreground='white',
                  borderwidth=0,
                  padding=(10, 5))
    
    style.map('Dialog.Danger.TButton',
             background=[('active', '#d32f2f'), ('disabled', '#ef9a9a')],
             foreground=[('disabled', 'white')])
    
    # Dialog Neutral Button (for cancel actions)
    style.configure('Dialog.Neutral.TButton',
                  font=('Segoe UI', 9, 'bold'),
                  background='#9e9e9e',
                  foreground='white',
                  borderwidth=0,
                  padding=(10, 5))
    
    style.map('Dialog.Neutral.TButton',
             background=[('active', '#757575'), ('disabled', '#e0e0e0')],
             foreground=[('disabled', 'white')])

    # Quantity Dialog Styles
    style.configure('QuantityDialog.TFrame',
                  background='#ffffff',
                  borderwidth=0,
                  relief='flat')
    
    style.configure('QuantityDialog.Title.TLabel',
                  font=('Segoe UI', 14, 'bold'),
                  foreground='#263238',
                  background='#ffffff',
                  padding=(0, 0, 5, 10))
    
    style.configure('QuantityDialog.Content.TFrame',
                  background='#ffffff',
                  borderwidth=0,
                  padding=(10, 5))
    
    style.configure('QuantityDialog.Label.TLabel',
                  font=('Segoe UI', 10),
                  foreground='#5a5c69',
                  background='#ffffff')
    
    style.configure('QuantityDialog.Entry.TEntry',
                  font=('Segoe UI', 10),
                  foreground='#212121',
                  fieldbackground='#f8f9fa',
                  borderwidth=1,
                  relief='solid',
                  padding=8,
                  bordercolor='#e0e0e0',
                  lightcolor='#e0e0e0',
                  darkcolor='#e0e0e0')
    
    style.map('QuantityDialog.Entry.TEntry',
             fieldbackground=[('focus', '#ffffff')],
             bordercolor=[('focus', '#00bcd4')],
             lightcolor=[('focus', '#00bcd4')],
             darkcolor=[('focus', '#00bcd4')])
    
    style.configure('QuantityDialog.ButtonFrame.TFrame',
                  background='#ffffff',
                  borderwidth=0,
                  padding=(0, 10, 0, 0))
    
    style.configure('QuantityDialog.Button.TButton',
                  font=('Segoe UI', 10, 'bold'),
                  background='#00bcd4',
                  foreground='white',
                  borderwidth=0,
                  padding=(12, 8),
                  focuscolor='#00bcd4')
    
    style.map('QuantityDialog.Button.TButton',
             background=[('active', '#0097a7'), ('disabled', '#e0e0e0')],
             foreground=[('disabled', '#9e9e9e')])
    
    style.configure('QuantityDialog.CancelButton.TButton',
                  font=('Segoe UI', 10),
                  background='#f5f5f5',
                  foreground='#5a5c69',
                  borderwidth=0,
                  padding=(12, 8))
    
    style.map('QuantityDialog.CancelButton.TButton',
             background=[('active', '#e0e0e0')])
    
    # Dialog Card Styles
    style.configure('Dialog.Card.TFrame',
               background='white',
               borderwidth=1,
               relief='solid',
               bordercolor='#e0e0e0')

    # Plus Button Style
    style.configure("Cashier.Plus.TButton", 
               background="#e6f2ff", 
               foreground="black",
               padding=0)
    style.map("Cashier.Plus.TButton",
         background=[('active', '#0078d7')])

# ======================
# TREEVIEW STYLES
# ======================
def configure_treeview_styles(style):
    """Configure treeview widget styles"""
    # Modern Treeview styles with sidebar blue color (#00bcd4)
    style.configure('Treeview', 
               rowheight=28,
               background='white',
               fieldbackground='white',
               borderwidth=0)

    style.map('Treeview',
         background=[('selected', '#e0e0e0')],
         foreground=[('selected', 'black')])
    
    style.configure('Custom.Treeview',
                  font=('Segoe UI', 9),
                  rowheight=28,
                  background='white',
                  fieldbackground='white',
                  bordercolor='#d1d3e2',
                  borderwidth=0,
                  relief='flat')

    style.configure('Custom.Treeview.Heading',
                  font=('Segoe UI', 9, 'bold'),
                  background='#00bcd4',  # Using sidebar blue color
                  foreground='white',
                  relief='flat',
                  padding=5)

    style.map('Custom.Treeview.Heading',
             background=[('active', '#0097a7')])  # Slightly darker blue on active

    style.configure('Custom.Treeview',
                  highlightthickness=0,
                  bd=0)

    style.configure('Custom.Treeview.Item',
                  padding=(5, 5))

    style.map('Custom.Treeview',
             background=[('selected', '#e0e0e0')],  # Light grey for selection
             foreground=[('selected', 'black')])  # Keep text black when selected

    # Status-based row colors
    style.configure('in_stock.Treeview',
                  background='#e8f5e9')  # Light green

    style.configure('low_stock.Treeview',
                  background='#fff8e1')  # Light yellow

    style.configure('out_of_stock.Treeview',
                  background='#ffebee')  # Light red

# ======================
# SCROLLBAR STYLES
# ======================
def configure_scrollbar_styles(style):
    """Configure scrollbar styles"""
    # Modern Scrollbar style
    style.configure('Vertical.TScrollbar',
                  gripcount=0,
                  background='#d1d3e2',
                  darkcolor='#d1d3e2',
                  lightcolor='#d1d3e2',
                  troughcolor='#f8f9fa',
                  bordercolor='#f8f9fa',
                  arrowcolor='#00bcd4',
                  relief='flat',
                  width=12,
                  arrowsize=12)
    
    style.map('Vertical.TScrollbar',
             background=[('active', '#b0b5c0')])
    
    # Add to configure_dashboard_styles function:
# In styles.py - Update dashboard styles

def configure_dashboard_styles(style):
    """Configure modern dashboard styles with sidebar blue theme"""
    # Main colors
    primary_color = '#00bcd4'  # Sidebar blue
    primary_dark = '#0097a7'   # Darker blue for hover
    text_color = '#263238'     # Dark gray for text
    bg_color = '#f5f7fa'       # Light background
    

    style.configure('Modern.Dropdown.TMenubutton', 
                background='#00bcd4',
                foreground='white',
                font=('Segoe UI', 10),
                relief='flat',
                padding=5)
    style.map('Modern.Dropdown.TMenubutton',
            background=[('active', '#0097a7'), ('pressed', '#00bcd4')])

    style.configure('Modern.Filter.TLabel', 
                foreground='#00bcd4',
                font=('Segoe UI', 9, 'bold'),
                padding=2)
    # Dashboard frame styles
    style.configure('Modern.Dashboard.TFrame', background=bg_color)
    style.configure('Modern.Header.TFrame', background=bg_color)
    style.configure('Modern.Header.Title.TLabel',
                  font=('Segoe UI', 14, 'bold'),
                  foreground=text_color,
                  background=bg_color)
    style.configure('Modern.Header.Date.TLabel',
                  font=('Segoe UI', 10),
                  foreground='#5a5c69',
                  background=bg_color)
    
    # Card styles
    style.configure('Modern.Cards.TFrame', background=bg_color)
    style.configure('Modern.Card.TFrame',
                  background='white',
                  borderwidth=1,
                  relief='solid',
                  bordercolor='#e0e0e0',
                  padding=10)
    style.configure('Modern.Card.Hover.TFrame',
                  background='#f0f5ff',
                  borderwidth=1,
                  relief='solid',
                  bordercolor='#e0e0e0',
                  padding=10)
    style.configure('Modern.Card.Title.TLabel',
                  font=('Segoe UI', 10, 'bold'),
                  foreground=text_color,
                  background='white')
    style.configure('Modern.Card.Value.TLabel',
                  font=('Segoe UI', 18, 'bold'),
                  foreground=primary_color,
                  background='white')
    style.configure('Modern.Card.Change.TLabel',
                  font=('Segoe UI', 9),
                  foreground='#1cc88a',  # Green for positive change
                  background='white')
    
    # Graph selector dropdown
    style.configure('Modern.Graph.Selector.Menu.TMenubutton',
                  font=('Segoe UI', 10),
                  foreground='white',
                  background=primary_color,
                  relief='flat',
                  padding=8)
    style.map('Modern.Graph.Selector.Menu.TMenubutton',
             background=[('active', primary_dark)],
             foreground=[('active', 'white')])
    
    # Other dashboard styles...
    # (Keep your existing dashboard styles here)
    
    # Graph selector dropdown
    # Dashboard Dropdown Button
    style.configure('Dashboard.Dropdown.TMenubutton',
                    font=('Segoe UI', 10),
                    foreground='white',
                    background='#00bcd4',
                    relief='flat',
                    padding=8)

    style.map('Dashboard.Dropdown.TMenubutton',
            background=[('active', '#0097a7'), ('!disabled', '#00bcd4')],
            foreground=[('active', 'white'), ('!disabled', 'white')])

    
    # Cards styling
    style.configure('Dashboard.Card.TFrame',
                  background='white',
                  borderwidth=1,
                  relief='solid',
                  bordercolor='#e0e0e0')
    
    style.configure('Dashboard.Card.Title.TLabel',
                  font=('Segoe UI', 10, 'bold'),
                  foreground=text_color,
                  background='white')
    
    style.configure('Dashboard.Card.Value.TLabel',
                  font=('Segoe UI', 18, 'bold'),
                  foreground=primary_color,
                  background='white')
    
    
    # Graph styles
    style.configure('Modern.Graph.Container.TFrame', background='#f8f9fa')
    style.configure('Modern.Graph.Selector.TFrame', background='white')
    style.configure('Modern.Graph.Selector.Label.TLabel',
                  font=('Segoe UI', 10),
                  foreground='#5a5c69',
                  background='white')
    style.map('Modern.Graph.Selector.Menu.TMenubutton',
             fieldbackground=[('readonly', 'white')],
             background=[('readonly', 'white')],
             foreground=[('readonly', '#2e59d9')])
    style.configure('Modern.Graph.TFrame', background='white')
    
    # Activity styles
    style.configure('Modern.Activity.TFrame', background='#f8f9fa')
    style.configure('Modern.Activity.Header.TFrame', background='white')
    style.configure('Modern.Activity.Title.TLabel',
                  font=('Segoe UI', 12, 'bold'),
                  foreground='#2e59d9',
                  background='white')
    style.configure('Modern.Activity.Filter.TLabel',
                  font=('Segoe UI', 9),
                  foreground='#5a5c69',
                  background='white')
    style.map('Modern.Activity.Filter.TCombobox',
             fieldbackground=[('readonly', 'white')],
             background=[('readonly', 'white')])
    
    # Treeview styles
    style.configure('Modern.Treeview',
                  font=('Segoe UI', 9),
                  rowheight=28,
                  background='white',
                  fieldbackground='white',
                  bordercolor='#d1d3e2',
                  borderwidth=0)
    style.configure('Modern.Treeview.Heading',
                  font=('Segoe UI', 9, 'bold'),
                  background='#2e59d9',
                  foreground='white',
                  relief='flat',
                  padding=5)
    style.map('Modern.Treeview.Heading',
             background=[('active', '#1c3ca3')])
    style.map('Modern.Treeview',
             background=[('selected', '#e0e0e0')],
             foreground=[('selected', 'black')])
    
    # Custom row colors
    style.configure('evenrow.Treeview', background='white')
    style.configure('oddrow.Treeview', background='#f8f9fa')
    
    # Button style
    style.configure('Modern.Button.TButton',
                  font=('Segoe UI', 9, 'bold'),
                  background='#2e59d9',
                  foreground='white',
                  borderwidth=0,
                  padding=6)
    style.map('Modern.Button.TButton',
             background=[('active', '#1c3ca3'), ('disabled', '#cccccc')],
             foreground=[('disabled', '#888888')])
    
    # Scrollbar style
    style.configure('Modern.Scrollbar.Vertical.TScrollbar',
                  gripcount=0,
                  background='#d1d3e2',
                  darkcolor='#d1d3e2',
                  lightcolor='#d1d3e2',
                  troughcolor='#f8f9fa',
                  bordercolor='#f8f9fa',
                  arrowcolor='#2e59d9',
                  relief='flat',
                  width=12)
    style.map('Modern.Scrollbar.Vertical.TScrollbar',
             background=[('active', '#b0b5c0')])
    