import tkinter as tk
from tkinter import messagebox, ttk
import os

# Import database
from database import InventoryDB, CounterDB
# Import style configuration and application sections
from styles import apply_styles
from dashboard import DashboardSection
from inventory import InventorySection
from cashier_employee import CashierEmployee    
from cashier_admin import CashierAdmin 

# Constants
ICON_NAMES = ["dashboard", "inventory", "cashier",  "logout"]
ICON_STATES = ["default", "active", "hover"]
EMOJI_FALLBACKS = {
    "dashboard": "📊",
    "inventory": "📦",
    "cashier": "💰",
    "logout": "🚪"
}

class InventoryApp:
    """Main application class for Inventory Management System"""
    
    def __init__(self, root):
        """Initialize the application"""
        self.root = root
        self.db = InventoryDB()
        self.counter_db = CounterDB()
        self.setup_main_window()
        self.create_assets_directory()
        self.current_user = None  
        self.current_user_role = None
        apply_styles()

        # Initialize application state
        self.current_section = None
        self.active_button = None
        self.section_widgets = {}
        self.icons = {state: {} for state in ICON_STATES}
        self.sections = {}  # Will be initialized after login

        # Start with login UI
        self.create_login_ui()

    def setup_main_window(self):
        """Configure the main application window"""
        self.root.title("Inventory Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#f5f7fa')
        self.root.minsize(1000, 600)  # Set minimum window size

    def create_assets_directory(self):
        """Create assets directory if it doesn't exist"""
        if not os.path.exists('assets'):
            os.makedirs('assets')

    # ======================
    # ICON MANAGEMENT
    # ======================
    def load_icons(self):
        """Load all icon images with different states"""
        for name in ICON_NAMES:
            try:
                # Load default white icon
                default_img = tk.PhotoImage(file=f"assets/{name}.png")
                self.icons["default"][name] = self.resize_icon(default_img)
                
                # Load blue icon for active state
                active_img = tk.PhotoImage(file=f"assets/{name}_blue.png")
                self.icons["active"][name] = self.resize_icon(active_img)
                
                # Hover uses same as default (white on dark)
                self.icons["hover"][name] = self.icons["default"][name]
                
            except Exception as e:
                # Fallback to emoji if icon not found
                print(f"Error loading icon {name}: {e}")
                self.set_emoji_fallback(name)

    def resize_icon(self, image):
        """Resize icon to appropriate dimensions"""
        return image.subsample(
            max(1, image.width() // 20), 
            max(1, image.height() // 20)
        )

    def set_emoji_fallback(self, name):
        """Set emoji fallback for missing icons"""
        for state in ICON_STATES:
            self.icons[state][name] = EMOJI_FALLBACKS[name]

    # ======================
    # LOGIN UI
    # ======================
    def create_login_ui(self):
        """Create the login interface"""
        self.clear_window()
        self.setup_login_container()
        self.root.bind('<Return>', lambda event: self.login())

    def setup_login_container(self):
        """Create the centered login container"""
        container = ttk.Frame(self.root, style='Main.Container.TFrame', width=800, height=400)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        container.pack_propagate(False)

        left_frame = ttk.Frame(container, style='Login.LeftPanel.TFrame', width=300, height=400)
        left_frame.pack(side='left', fill='y')
        left_frame.pack_propagate(False)

        right_frame = ttk.Frame(container, style='Login.RightPanel.TFrame', width=500, height=400)
        right_frame.pack(side='right', fill='y')
        right_frame.pack_propagate(False)

        self.setup_left_panel_content(left_frame)
        self.setup_right_panel_content(right_frame)

    def setup_left_panel_content(self, parent):
        """Setup content for left login panel"""
        content_frame = ttk.Frame(parent, style='Login.LeftPanel.TFrame')
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(content_frame, text="Inventory \nManagement APP", 
                 style='Login.Title.TLabel', justify='center').pack(pady=(0, 15), fill="x")
        ttk.Label(content_frame, text="DSA Lab Project", style='Login.Highlight.TLabel').pack()
        ttk.Label(content_frame, text="Submitted by:", style='Login.Subheading.TLabel').pack(pady=(20, 5))
        ttk.Label(content_frame, text="Abraiz Abdur Rehman\n2023-EE-351", 
                 style='Login.Body.TLabel', justify='center').pack()
        ttk.Label(content_frame, text="Musa Piracha\n2023-EE-421", 
                 style='Login.Body.TLabel').pack(pady=5)
        ttk.Label(content_frame, text="Submitted to:\nMr. Azeem Iqbal", 
                 style='Login.Highlight.TLabel', justify='center').pack(pady=(20, 0))

    def setup_right_panel_content(self, parent):
        """Setup content for right login panel"""
        ttk.Label(parent, text="Welcome to Your Inventory Hub", 
                 style='Login.Heading.TLabel').pack(pady=(50, 5))
        ttk.Label(parent, text="Secure login to manage and track your products.", 
                 style='Login.Note.TLabel').pack(pady=(0, 30))

        ttk.Label(parent, text="Username", style='Login.Label.TLabel').pack(anchor='w', padx=50)
        self.username_entry = ttk.Entry(parent, style='Login.Entry.TEntry')
        self.username_entry.pack(padx=50, fill='x', pady=(0, 10))

        ttk.Label(parent, text="Password", style='Login.Label.TLabel').pack(anchor='w', padx=50)
        self.password_entry = ttk.Entry(parent, show="*", style='Login.Entry.TEntry')
        self.password_entry.pack(padx=50, fill='x', pady=(0, 20))

        ttk.Button(parent, text="Login", command=self.login, 
                  style='Login.Button.TButton').pack(pady=(10, 0))

    # Modify the login method:
    def login(self):
        """Handle login authentication"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Login Failed", "Please enter both username and password")
            return
        
        # Check for admin login (fixed credentials)
        if username == "admin" and password == "123":
            self.current_user = username
            self.current_user_role = "admin"
            self.initialize_sections()
            self.create_dashboard_ui(username)
            return
        
        # Check for cashier login in database - now using cashier_name instead of cashier_id
        cashiers = self.counter_db.get_counters(active_only=True)
        for cashier in cashiers:
            if cashier['cashier_name'].lower() == username.lower() and cashier['password'] == password:
                self.current_user = cashier['cashier_name']  # Use name instead of ID
                self.current_user_role = "cashier"
                self.initialize_sections()
                self.create_dashboard_ui(cashier['cashier_name'])
                return
        
        # If no match found
        messagebox.showerror("Login Failed", "Incorrect username or password")

    def initialize_sections(self):
        """Initialize application sections based on user role"""
        self.sections = {
            "dashboard": DashboardSection(self),
            "inventory": InventorySection(self, self.db),
            "cashier": CashierAdmin(self, self.db, self.counter_db) if self.current_user_role == "admin" else CashierEmployee(self, self.db, self.counter_db),
        }

    # ======================
    # DASHBOARD UI
    # ======================
    def create_dashboard_ui(self, username):
        """Create the main dashboard interface"""
        self.clear_window()
        self.root.unbind('<Return>')
        self.load_icons()
        
        self.setup_main_container()
        self.setup_sidebar(username)
        self.setup_navigation_buttons()
        self.create_logout_button()
        
        # Show dashboard by default
        self.show_section("dashboard")
        
        # Ensure sidebar is visible
        if hasattr(self, 'sidebar'):
            self.sidebar.pack(side='left', fill='y')

    def setup_main_container(self):
        """Create the main container for dashboard"""
        main_container = ttk.Frame(self.root, style='Main.Container.TFrame')
        main_container.pack(fill='both', expand=True)
        
        # Sidebar with fixed width
        self.sidebar = ttk.Frame(main_container, 
                            style='App.Sidebar.TFrame', 
                            width=220)  # Fixed width
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)  # Prevent width changes
        
        # Main content area
        self.main_content = ttk.Frame(main_container, style='App.Main.TFrame')
        self.main_content.pack(side='right', expand=True, fill='both')
    def setup_sidebar(self, username):
        """Configure the sidebar header"""
        sidebar_header = ttk.Frame(self.sidebar, style='App.Sidebar.TFrame')
        sidebar_header.pack(pady=(20, 30), padx=10, fill='x')
        
        ttk.Label(sidebar_header, text="Inventory Pro", style='Login.Title.TLabel').pack()
        ttk.Label(sidebar_header, text=f"Welcome, {username}", style='Login.Body.TLabel').pack()

    def setup_navigation_buttons(self):
        """Create navigation buttons in sidebar"""
        nav_buttons = [
            ("Dashboard", "dashboard", "dashboard"),
            ("Inventory", "inventory", "inventory"),
            ("Cashier", "cashier", "cashier")
        ]

        for text, section, icon_name in nav_buttons:
            # Only show sections that are available for the user's role
            if section in self.sections:
                self.create_nav_button(text, section, icon_name)

    def create_nav_button(self, text, section, icon_name):
        """Create a single navigation button"""
        btn_frame = ttk.Frame(self.sidebar, style='App.Sidebar.TFrame')
        self.section_widgets[section] = {
            'frame': btn_frame,
            'icon_name': icon_name
        }
        btn_frame.pack(fill='x', padx=10, pady=1)
        btn_frame.section = section
        btn_frame.icon_name = icon_name
        
        # Create icon label
        icon_label = ttk.Label(
            btn_frame,
            image=self.icons["default"][icon_name],
            style='App.Sidebar.Icon.TLabel'
        )
        icon_label.is_icon = True
        icon_label.grid(row=0, column=0, padx=(5, 5), sticky='w')
        
        # Create button
        btn = ttk.Button(
            btn_frame, 
            text=text, 
            command=lambda s=section: self.show_section(s),
            style='App.Sidebar.Button.TButton',
            cursor='hand2',
            takefocus=0
        )
        btn.grid(row=0, column=1, sticky='ew')
        btn.section = section
        
        # Configure hover effects
        for widget in [btn_frame, icon_label, btn]:
            widget.bind("<Enter>", lambda e, f=btn_frame, i=icon_name: self.on_sidebar_hover(f, i, True))
            widget.bind("<Leave>", lambda e, f=btn_frame, i=icon_name: self.on_sidebar_hover(f, i, False))
        
        btn_frame.columnconfigure(1, weight=1)

    def create_logout_button(self):
        """Create logout button at bottom of sidebar"""
        logout_frame = ttk.Frame(self.sidebar, style='App.Sidebar.TFrame')
        logout_frame.pack(side='bottom', fill='x', padx=10, pady=20)
        logout_frame.section = "logout"
        logout_frame.icon_name = "logout"
        
        # Create icon label
        icon_label = ttk.Label(
            logout_frame,
            image=self.icons["default"]["logout"],
            style='App.Sidebar.Icon.TLabel'
        )
        icon_label.is_icon = True
        icon_label.grid(row=0, column=0, padx=(5, 10))
        
        # Create button
        btn = ttk.Button(
            logout_frame, 
            text="Logout", 
            command=self.create_login_ui,
            style='App.Sidebar.Button.TButton',
            takefocus=0
        )
        btn.grid(row=0, column=1, sticky='ew')
        
        # Configure hover effects
        for widget in [logout_frame, icon_label, btn]:
            widget.bind("<Enter>", lambda e, f=logout_frame: self.on_sidebar_hover(f, "logout", True))
            widget.bind("<Leave>", lambda e, f=logout_frame: self.on_sidebar_hover(f, "logout", False))
        
        logout_frame.columnconfigure(1, weight=1)

    def on_sidebar_hover(self, frame, icon_name, is_hover):
        """Handle hover effects for sidebar buttons"""
        if self.active_button and frame.section == self.active_button.section:
            return  # Don't change active button
        
        for widget in frame.winfo_children():
            if isinstance(widget, ttk.Label) and hasattr(widget, 'is_icon'):
                if is_hover:
                    widget.configure(
                        image=self.icons["hover"][icon_name],
                        style='App.Sidebar.Icon.Hover.TLabel'
                    )
                else:
                    widget.configure(
                        image=self.icons["default"][icon_name],
                        style='App.Sidebar.Icon.TLabel'
                    )
        
        frame.configure(style='App.Sidebar.Hover.TFrame' if is_hover else 'App.Sidebar.TFrame')

    # ======================
    # SECTION MANAGEMENT
    # ======================
    def show_section(self, section_name):
        """Show the specified application section"""
        if section_name not in self.sections:
            return
            
        self.update_active_button(section_name)
        self.update_section_content(section_name)

    def update_active_button(self, section_name):
        """Update the active button styling"""
        # Reset previous active button
        if self.active_button:
            current_section = None
            for sec, data in self.section_widgets.items():
                if data['frame'] == self.active_button:
                    current_section = sec
                    break
            
            if current_section:
                self.reset_button_style(current_section)

        # Activate new section
        if section_name in self.section_widgets:
            widget_data = self.section_widgets[section_name]
            self.active_button = widget_data['frame']
            self.set_active_button_style(widget_data)

    def reset_button_style(self, section_name):
        """Reset the style of a button to default"""
        widget_data = self.section_widgets[section_name]
        widget_data['frame'].configure(style='App.Sidebar.TFrame')
        
        for child_widget in self.active_button.winfo_children():
            if isinstance(child_widget, ttk.Label) and hasattr(child_widget, 'is_icon'):
                child_widget.configure(
                    image=self.icons["default"][widget_data['icon_name']],
                    style='App.Sidebar.Icon.TLabel'
                )
            elif isinstance(child_widget, ttk.Button):
                child_widget.configure(style='App.Sidebar.Button.TButton')

    def set_active_button_style(self, widget_data):
        """Set the active button styling"""
        widget_data['frame'].configure(style='App.Sidebar.Active.TFrame')
        
        for child_widget in widget_data['frame'].winfo_children():
            if isinstance(child_widget, ttk.Button):
                child_widget.configure(style='App.Sidebar.Button.Active.TButton')
            elif isinstance(child_widget, ttk.Label) and hasattr(child_widget, 'is_icon'):
                child_widget.configure(
                    image=self.icons["active"][widget_data['icon_name']],
                    style='App.Sidebar.Icon.Active.TLabel'
                )

    def update_section_content(self, section_name):
        """Update the content area with the selected section"""
        if self.current_section:
            self.current_section.hide()
        
        self.current_section = self.sections[section_name]
        self.current_section.show(self.main_content)

    # ======================
    # UTILITY METHODS
    # ======================
    def clear_window(self):
        """Clear all widgets from the window"""
        for widget in self.root.winfo_children():
            widget.destroy()

# ======================
# APPLICATION ENTRY POINT
# ======================
if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
