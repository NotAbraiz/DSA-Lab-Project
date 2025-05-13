import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry  # Added for date filtering
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Cursor
import numpy as np
from datetime import datetime, timedelta

class DashboardSection:
    def __init__(self, app):
        self.app = app
        self.frame = None
        self.graph_frame = None
        self.current_graph = None
        self.graph_canvas = None
        self.toolbar = None
        self.graph_options = []
        self.date_range = {
            'start': (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
            'end': datetime.now().strftime("%Y-%m-%d")
        }
        self.setup_graph_options()

    def setup_graph_options(self):
        """Initialize available graph options based on user role"""
        if self.app.current_user_role == "admin":
            self.graph_options = [
                ("Sales Trend", self.create_sales_trend_graph),
                ("Counter Performance", self.create_counter_performance_graph),
                ("Inventory Status", self.create_inventory_status_graph),
                ("Daily Comparison", self.create_daily_comparison_graph)
            ]
        else:
            self.graph_options = [
                ("Your Performance", self.create_cashier_performance_graph),
                ("Hourly Sales", self.create_hourly_sales_graph),
                ("Product Popularity", self.create_product_popularity_graph)
            ]

    def show(self, parent):
        """Show the modern dashboard interface"""
        self.frame = ttk.Frame(parent, style='Modern.Dashboard.TFrame')
        self.frame.pack(expand=True, fill='both', padx=15, pady=15)
        
        # Header with date
        self.create_header()
        
        # Stats cards with modern design
        self.create_stats_cards()
        
        # Interactive graph selector and container
        self.create_graph_selector()
        
        # Recent activity section
        self.create_activity_section()

    def create_header(self):
        """Create modern header with date"""
        header = ttk.Frame(self.frame, style='Modern.Header.TFrame')
        header.pack(fill='x', pady=(0, 15))
        
        # Dashboard title with icon
        title_frame = ttk.Frame(header, style='Modern.Header.TFrame')
        title_frame.pack(side='left')
        
        ttk.Label(title_frame, 
                text="📊 Dashboard", 
                style='Modern.Header.Title.TLabel').pack(side='left', padx=5)
        
        # Right side with date
        current_date = datetime.now().strftime("%A, %d %B %Y")
        ttk.Label(header, 
                text=f"🗓️ {current_date}", 
                style='Modern.Header.Date.TLabel').pack(side='right', padx=10)

    def create_stats_cards(self):
        """Create modern stats cards with hover effects"""
        cards_frame = ttk.Frame(self.frame, style='Modern.Cards.TFrame')
        cards_frame.pack(fill='x', pady=(0, 20))
        
        if self.app.current_user_role == "admin":
            stats = self.get_admin_stats()
        else:
            stats = self.get_cashier_stats()
        
        for i, (title, value, color) in enumerate(stats):
            card = ttk.Frame(cards_frame, style='Modern.Card.TFrame')
            card.grid(row=0, column=i, padx=8, sticky='nsew')
            cards_frame.columnconfigure(i, weight=1)
            
            # Card content
            ttk.Label(card, 
                    text=title, 
                    style='Modern.Card.Title.TLabel').pack(pady=(12, 0), padx=12, anchor='w')
            
            ttk.Label(card, 
                    text=value, 
                    style='Modern.Card.Value.TLabel').pack(pady=(2, 0), padx=12, anchor='w')

    def get_admin_stats(self):
        """Get statistics for admin dashboard"""
        stats = []
        
        # Total Products
        products = self.app.db.get_products()
        total_products = len(products)
        stats.append(("Total Products", f"{total_products}", "#4e73df"))
        
        # Total Sales Today
        today = datetime.now().strftime("%Y-%m-%d")
        today_sales = self.app.counter_db.get_sales_by_date(today)
        today_total = sum(sale['total_amount'] for sale in today_sales) if today_sales else 0
        stats.append(("Today's Sales", f"PKR {today_total:,.2f}", "#1cc88a"))
        
        # Active Counters
        counters = self.app.counter_db.get_counters(active_only=True)
        stats.append(("Active Counters", f"{len(counters)}", "#36b9cc"))
        
        # Inventory Status
        low_stock = sum(1 for p in products if p['status'] == "Low Stock")
        out_of_stock = sum(1 for p in products if p['status'] == "Out of Stock")
        stats.append(("Inventory Alerts", f"{low_stock} Low, {out_of_stock} Out", "#f6c23e"))
        
        return stats

    def get_cashier_stats(self):
        """Get statistics for cashier dashboard"""
        stats = []
        
        # Today's Sales
        today = datetime.now().strftime("%Y-%m-%d")
        sales = self.app.counter_db.get_sales_by_date_and_cashier(today, self.app.current_user)
        today_total = sum(sale['total_amount'] for sale in sales) if sales else 0
        stats.append(("Today's Sales", f"PKR {today_total:,.2f}", "#4e73df"))
        
        # Transactions Count
        stats.append(("Transactions", f"{len(sales)}", "#1cc88a"))
        
        # Average Sale
        avg_sale = today_total / len(sales) if sales else 0
        stats.append(("Avg. Sale", f"PKR {avg_sale:,.2f}", "#36b9cc"))
        
        # Popular Product
        if sales:
            product_counts = {}
            for sale in sales:
                details = self.app.counter_db.get_sale_details(sale['id'])
                if details:
                    for item in details['items']:
                        product_counts[item['product_name']] = product_counts.get(item['product_name'], 0) + item['quantity']
            if product_counts:
                top_product = max(product_counts.items(), key=lambda x: x[1])
                stats.append(("Top Product", f"{top_product[0]} ({top_product[1]})", "#f6c23e"))
            else:
                stats.append(("Top Product", "N/A", "#f6c23e"))
        else:
            stats.append(("Top Product", "N/A", "#f6c23e"))
        
        return stats
    def create_graph_selector(self):
        """Create graph selector and container with date filtering"""
        graph_container = ttk.Frame(self.frame, style='Modern.Graph.Container.TFrame')
        graph_container.pack(fill='both', expand=True, pady=(0, 20))
        
        # Graph selector and filter controls
        selector_frame = ttk.Frame(graph_container, style='Modern.Graph.Selector.TFrame')
        selector_frame.pack(fill='x', padx=10, pady=10)
        
        # Visualization label and dropdown
        ttk.Label(selector_frame,
                text="📈 Select Visualization:",
                style='Modern.Graph.Selector.Label.TLabel').pack(side='left')
        
        self.graph_var = tk.StringVar()
        self.graph_var.set(self.graph_options[0][0])  # Set default
                
        # Create styles with the specified blue colors
        style = ttk.Style()
        main_blue = '#00bcd4'  # Main cyan-blue color
        hover_blue = '#0097a7' # Darker cyan-blue for hover
        
        # Style for dropdown menu (matches inventory.py comboboxes)
        style.configure('Modern.Dropdown.TMenubutton', 
                    background=main_blue,
                    foreground='white',
                    font=('Segoe UI', 10),
                    relief='flat',
                    padding=5)
        style.map('Modern.Dropdown.TMenubutton',
                background=[('active', hover_blue), ('pressed', main_blue)])
        
        # Create dropdown with automatic update binding
        graph_menu = ttk.OptionMenu(
            selector_frame,
            self.graph_var,
            self.graph_options[0][0],
            *[opt[0] for opt in self.graph_options],
            style='Modern.Dropdown.TMenubutton'
        )
        graph_menu.pack(side='left', padx=10)
        self.graph_var.trace_add('write', lambda *args: self.update_graph())
        
        # Date range filter frame
        date_filter_frame = ttk.Frame(selector_frame, style='Modern.Filter.TFrame')
        date_filter_frame.pack(side='right', padx=10)
        
        # Configure styles for date filter components
        style.configure('Modern.Filter.TLabel', 
                    foreground=main_blue,
                    font=('Segoe UI', 9, 'bold'),
                    padding=2)
        
        # From date
        ttk.Label(date_filter_frame, 
                text="From:", 
                style='Modern.Filter.TLabel').pack(side='left')
        
        self.start_date_entry = DateEntry(
            date_filter_frame,
            date_pattern='yyyy-mm-dd',
            mindate=datetime.now() - timedelta(days=365),
            maxdate=datetime.now(),
            background=main_blue,
            foreground='white',
            selectbackground=hover_blue,
            selectforeground='white',
            normalbackground='white',
            normalforeground='#333333',
            weekendbackground='white',
            weekendforeground='#333333',
            headersbackground=main_blue,
            headersforeground='white',
            bordercolor=main_blue,
            othermonthforeground='#aaaaaa',
            othermonthbackground='white',
            othermonthweforeground='#aaaaaa',
            othermonthwebackground='white',
            arrowcolor='white',
            selectmode='day',
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )
        self.start_date_entry.set_date(self.date_range['start'])
        self.start_date_entry.pack(side='left', padx=5)
        self.start_date_entry.bind('<<DateEntrySelected>>', lambda e: self.update_graph())
        
        # To date
        ttk.Label(date_filter_frame, 
                text="To:", 
                style='Modern.Filter.TLabel').pack(side='left', padx=(10, 0))
        
        self.end_date_entry = DateEntry(
            date_filter_frame,
            date_pattern='yyyy-mm-dd',
            mindate=datetime.now() - timedelta(days=365),
            maxdate=datetime.now(),
            background=main_blue,
            foreground='white',
            selectbackground=hover_blue,
            selectforeground='white',
            normalbackground='white',
            normalforeground='#333333',
            weekendbackground='white',
            weekendforeground='#333333',
            headersbackground=main_blue,
            headersforeground='white',
            bordercolor=main_blue,
            othermonthforeground='#aaaaaa',
            othermonthbackground='white',
            othermonthweforeground='#aaaaaa',
            othermonthwebackground='white',
            arrowcolor='white',
            selectmode='day',
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )
        self.end_date_entry.set_date(self.date_range['end'])
        self.end_date_entry.pack(side='left', padx=5)
        self.end_date_entry.bind('<<DateEntrySelected>>', lambda e: self.update_graph())
        
        # Graph frame with toolbar
        self.graph_frame = ttk.Frame(graph_container, style='Modern.Graph.TFrame')
        self.graph_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Show default graph
        self.update_graph()
        
    def apply_date_filter(self):
        """Apply the selected date range filter"""
        self.date_range = {
            'start': self.start_date_entry.get_date().strftime("%Y-%m-%d"),
            'end': self.end_date_entry.get_date().strftime("%Y-%m-%d")
        }
        self.update_graph()

    def update_graph(self, *args):
        """Update the displayed graph based on selection"""
        # Clear previous graph
        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()
        if self.toolbar:
            self.toolbar.destroy()
        
        # Find and create selected graph
        selected = self.graph_var.get()
        for name, func in self.graph_options:
            if name == selected:
                self.current_graph = func()
                break
        
        # Embed new graph
        if self.current_graph:
            self.graph_canvas = FigureCanvasTkAgg(self.current_graph, master=self.graph_frame)
            self.graph_canvas.draw()
            self.graph_canvas.get_tk_widget().pack(fill='both', expand=True)
            
            # Add interactive toolbar
            self.toolbar = NavigationToolbar2Tk(self.graph_canvas, self.graph_frame)
            self.toolbar.update()
            
            # Add hover effect for data points
            self.add_graph_interactivity()

    def add_graph_interactivity(self):
        """Add interactive elements to the graph"""
        if not self.current_graph:
            return
            
        # Enable cursor tracking
        cursor = Cursor(self.current_graph.axes[0], useblit=True, color='red', linewidth=1)
        
        # Connect click event for detailed view
        def on_click(event):
            if event.inaxes:
                print(f"Clicked at: {event.xdata}, {event.ydata}")
                # Could show detailed popup here
        
        self.current_graph.canvas.mpl_connect('button_press_event', on_click)

    def create_sales_trend_graph(self):
        """Create interactive sales trend graph with date filtering"""
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#f8f9fa')
        
        # Get sales data for selected date range
        start_date = datetime.strptime(self.date_range['start'], "%Y-%m-%d")
        end_date = datetime.strptime(self.date_range['end'], "%Y-%m-%d")
        delta = end_date - start_date
        dates = []
        sales = []
        
        for i in range(delta.days + 1):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            daily_sales = self.app.counter_db.get_sales_by_date(date)
            total = sum(sale['total_amount'] for sale in daily_sales) if daily_sales else 0
            dates.append(datetime.strptime(date, "%Y-%m-%d"))
            sales.append(total)
        
        # Create line plot with markers
        line, = ax.plot(dates, sales, 
                       marker='o', 
                       color='#4e73df', 
                       linewidth=2.5,
                       markersize=8,
                       markerfacecolor='white',
                       markeredgewidth=2)
        
        # Style the plot
        ax.set_title(f'Sales Trend ({self.date_range["start"]} to {self.date_range["end"]})', 
                    pad=20, fontsize=14, fontweight='bold')
        ax.set_ylabel('Sales (PKR)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Format x-axis dates
        fig.autofmt_xdate()
        
        return fig

    def create_counter_performance_graph(self):
        """Create interactive counter performance comparison with date filtering"""
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#f8f9fa')
        
        counters = self.app.counter_db.get_counters(active_only=True)
        counter_names = [c['cashier_name'] for c in counters]
        counter_sales = []
        
        for counter in counters:
            # Get sales for the selected date range
            sales = self.app.counter_db.get_sales_history({
                'start_date': self.date_range['start'],
                'end_date': self.date_range['end'],
                'counter_id': counter['id']
            })
            total = sum(s['total_amount'] for s in sales) if sales else 0
            counter_sales.append(total)
        
        # Create colorful bars
        colors = plt.cm.viridis(np.linspace(0, 1, len(counter_names)))
        bars = ax.bar(counter_names, counter_sales, color=colors)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'PKR {height:,.0f}',
                   ha='center', va='bottom',
                   fontsize=10, fontweight='bold')
        
        # Style the plot
        ax.set_title(f'Counter Performance ({self.date_range["start"]} to {self.date_range["end"]})', 
                    pad=20, fontsize=14, fontweight='bold')
        ax.set_ylabel('Total Sales (PKR)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.3, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Rotate x-labels for better fit
        plt.xticks(rotation=45, ha='right')
        
        return fig

    def create_inventory_status_graph(self):
        """Create inventory status pie chart"""
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#f8f9fa')
        
        # Get inventory status counts from database
        inventory_status = {
            "In Stock": len(self.app.db.get_products({'status': 'In Stock'})),
            "Low Stock": len(self.app.db.get_products({'status': 'Low Stock'})),
            "Out of Stock": len(self.app.db.get_products({'status': 'Out of Stock'}))
        }
        
        # Create pie chart
        labels = [f"{k} ({v})" for k, v in inventory_status.items()]
        sizes = inventory_status.values()
        colors = ['#4e73df', '#f6c23e', '#e74a3b']
        
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            colors=colors, 
            autopct='%1.1f%%',
            startangle=90, 
            wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
        )
        
        # Improve label appearance
        for text in texts + autotexts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        
        ax.set_title('Current Inventory Status', pad=20, fontsize=14, fontweight='bold')
        ax.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle
        
        return fig

    def create_daily_comparison_graph(self):
        """Create comparison of selected date range vs previous period"""
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#f8f9fa')
        
        # Calculate previous period dates
        start_date = datetime.strptime(self.date_range['start'], "%Y-%m-%d")
        end_date = datetime.strptime(self.date_range['end'], "%Y-%m-%d")
        delta = end_date - start_date
        
        prev_start = start_date - delta - timedelta(days=1)
        prev_end = start_date - timedelta(days=1)
        
        # Get current period sales
        current_sales = 0
        for i in range(delta.days + 1):
            date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            daily_sales = self.app.counter_db.get_sales_by_date(date)
            current_sales += sum(sale['total_amount'] for sale in daily_sales) if daily_sales else 0
        
        # Get previous period sales
        prev_sales = 0
        for i in range(delta.days + 1):
            date = (prev_start + timedelta(days=i)).strftime("%Y-%m-%d")
            daily_sales = self.app.counter_db.get_sales_by_date(date)
            prev_sales += sum(sale['total_amount'] for sale in daily_sales) if daily_sales else 0
        
        # Create bar chart
        periods = [
            f"Previous\n{prev_start.strftime('%d %b')} to {prev_end.strftime('%d %b')}",
            f"Current\n{start_date.strftime('%d %b')} to {end_date.strftime('%d %b')}"
        ]
        values = [prev_sales, current_sales]
        colors = ['#858796', '#4e73df']
        
        bars = ax.bar(periods, values, color=colors)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'PKR {height:,.2f}',
                   ha='center', va='bottom',
                   fontsize=10, fontweight='bold')
        
        # Calculate and display percentage change
        if prev_sales > 0:
            change_percent = ((current_sales - prev_sales) / prev_sales) * 100
            change_text = f"{'↑' if change_percent >=0 else '↓'} {abs(change_percent):.1f}%"
            ax.text(1, max(values)*0.9, change_text, 
                   fontsize=12, fontweight='bold',
                   color='green' if change_percent >=0 else 'red',
                   ha='center')
        
        # Style the plot
        ax.set_title('Sales Period Comparison', pad=20, fontsize=14, fontweight='bold')
        ax.set_ylabel('Total Sales (PKR)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.3, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        return fig

    def create_cashier_performance_graph(self):
        """Create performance graph for current cashier with date filtering"""
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#f8f9fa')
        
        # Get sales data for current cashier in date range
        sales = self.app.counter_db.get_sales_history({
            'start_date': self.date_range['start'],
            'end_date': self.date_range['end'],
            'cashier_name': self.app.current_user  # Changed from current_user_id to current_user
        })
        
        
        # Group by day
        daily_sales = {}
        for sale in sales:
            date = datetime.strptime(sale['sale_time'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            daily_sales[date] = daily_sales.get(date, 0) + sale['total_amount']
        
        # Prepare data for plotting
        dates = [datetime.strptime(date, "%Y-%m-%d") for date in sorted(daily_sales.keys())]
        amounts = [daily_sales[date.strftime("%Y-%m-%d")] for date in dates]
        
        # Create line plot
        line, = ax.plot(dates, amounts, 
                       marker='o', 
                       color='#4e73df', 
                       linewidth=2.5,
                       markersize=8,
                       markerfacecolor='white',
                       markeredgewidth=2)
        
        # Style the plot
        ax.set_title(f'Your Performance ({self.date_range["start"]} to {self.date_range["end"]})', 
                    pad=20, fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Sales (PKR)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Format x-axis dates
        fig.autofmt_xdate()
        
        return fig

    def create_hourly_sales_graph(self):
        """Create hourly sales breakdown for current cashier with date filtering"""
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#f8f9fa')
        
        # Get sales data for current cashier in date range
        sales = self.app.counter_db.get_sales_history({
            'start_date': self.date_range['start'],
            'end_date': self.date_range['end'],
            'cashier_name': self.app.current_user  # Changed from current_user_id to current_user
        })
            
        # Group by hour across all days
        hourly_sales = {}
        for sale in sales:
            hour = datetime.strptime(sale['sale_time'], "%Y-%m-%d %H:%M:%S").hour
            hourly_sales[hour] = hourly_sales.get(hour, 0) + sale['total_amount']
        
        # Fill in missing hours with 0
        for hour in range(24):
            if hour not in hourly_sales:
                hourly_sales[hour] = 0
        
        # Sort by hour
        hours = sorted(hourly_sales.keys())
        amounts = [hourly_sales[hour] for hour in hours]
        
        # Create bar chart
        bars = ax.bar(hours, amounts, color='#4e73df')
        
        # Style the plot
        ax.set_title(f"Hourly Sales ({self.date_range['start']} to {self.date_range['end']})", 
                    pad=20, fontsize=14, fontweight='bold')
        ax.set_xlabel('Hour of Day', fontsize=12)
        ax.set_ylabel('Sales (PKR)', fontsize=12)
        ax.set_xticks(range(24))
        ax.grid(True, linestyle='--', alpha=0.3, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        return fig

    def create_product_popularity_graph(self):
        """Create graph of most popular products for current cashier with date filtering"""
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#f8f9fa')
        ax.set_facecolor('#f8f9fa')
        
        # Get sales data for current cashier in date range
        sales = self.app.counter_db.get_sales_history({
            'start_date': self.date_range['start'],
            'end_date': self.date_range['end'],
            'cashier_name': self.app.current_user  # Changed from current_user_id to current_user
        })
        
        # Count product sales
        product_counts = {}
        for sale in sales:
            sale_details = self.app.counter_db.get_sale_details(sale['id'])
            if sale_details:
                for item in sale_details['items']:
                    product_counts[item['product_name']] = product_counts.get(item['product_name'], 0) + item['quantity']
        
        # Sort by quantity and take top 10
        sorted_products = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        products = [p[0] for p in sorted_products]
        quantities = [p[1] for p in sorted_products]
        
        # Create horizontal bar chart
        y_pos = range(len(products))
        bars = ax.barh(y_pos, quantities, color='#4e73df')
        
        # Style the plot
        ax.set_title(f'Top Selling Products ({self.date_range["start"]} to {self.date_range["end"]})', 
                    pad=20, fontsize=14, fontweight='bold')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(products)
        ax.set_xlabel('Quantity Sold', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.3, axis='x')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        return fig

    def create_activity_section(self):
        """Create modern activity section with filtering"""
        activity_container = ttk.Frame(self.frame, style='Modern.Activity.TFrame')
        activity_container.pack(fill='both', expand=True)
        
        # Activity header with filter
        header = ttk.Frame(activity_container, style='Modern.Activity.Header.TFrame')
        header.pack(fill='x', pady=(0, 10))
        
        ttk.Label(header,
                 text="🔄 Recent Activity",
                 style='Modern.Activity.Title.TLabel').pack(side='left', padx=5)
        
        # Filter options
        filter_frame = ttk.Frame(header, style='Modern.Activity.Header.TFrame')
        filter_frame.pack(side='right')
        
        ttk.Label(filter_frame,
                 text="Filter:",
                 style='Modern.Activity.Filter.TLabel').pack(side='left', padx=5)
        
        self.activity_filter = ttk.Combobox(filter_frame,
                                          values=["All", "Sales", "Inventory", "System"],
                                          style='Modern.Activity.Filter.TCombobox')
        self.activity_filter.set("All")
        self.activity_filter.pack(side='left')
        self.activity_filter.bind("<<ComboboxSelected>>", self.filter_activity)
        
        # Activity table with modern styling
        self.activity_tree = ttk.Treeview(activity_container,
                                        columns=('Time', 'Type', 'User', 'Details', 'Amount'),
                                        show='headings',
                                        style='Modern.Treeview',
                                        height=8)
        
        # Configure columns
        self.activity_tree.column('Time', width=120, anchor='center')
        self.activity_tree.column('Type', width=120, anchor='center')
        self.activity_tree.column('User', width=120, anchor='center')
        self.activity_tree.column('Details', width=200, anchor='w')
        self.activity_tree.column('Amount', width=120, anchor='e')
        
        # Add headings
        self.activity_tree.heading('Time', text='⏱️ Time')
        self.activity_tree.heading('Type', text='📝 Type')
        self.activity_tree.heading('User', text='👤 User')
        self.activity_tree.heading('Details', text='📋 Details')
        self.activity_tree.heading('Amount', text='💰 Amount')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(activity_container,
                                orient="vertical",
                                command=self.activity_tree.yview,
                                style='Modern.Scrollbar.Vertical.TScrollbar')
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        
        self.activity_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Load activity data
        self.load_activity_data()

    def filter_activity(self, event=None):
        """Filter activity based on selected filter option"""
        selected_filter = self.activity_filter.get()
        
        # Clear current selection
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        # Get all activities
        if self.app.current_user_role == "admin":
            activities = self.get_admin_activities()
        else:
            activities = self.get_cashier_activities()
        
        # Filter activities if needed
        if selected_filter != "All":
            activities = [act for act in activities if act[1] == selected_filter]
        
        # Add filtered activities to treeview
        for i, activity in enumerate(activities):
            tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            self.activity_tree.insert('', 'end', values=activity, tags=tags)

    def load_activity_data(self):
        """Load activity data into the treeview"""
        # Clear existing data
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        # Get appropriate data based on user role
        if self.app.current_user_role == "admin":
            activities = self.get_admin_activities()
        else:
            activities = self.get_cashier_activities()
        
        # Add to treeview with alternating row colors
        for i, activity in enumerate(activities):
            tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            self.activity_tree.insert('', 'end', values=activity, tags=tags)

    def get_admin_activities(self):
        """Generate sample activity data for admin"""
        # This would come from your database in a real application
        activities = []
        for i in range(10):
            time = (datetime.now() - timedelta(minutes=i*30)).strftime("%H:%M")
            activities.append((
                time,
                "Sale" if i % 3 else "Inventory",
                f"Cashier {i%3+1}",
                f"Completed transaction #{1000+i}",
                f"PKR {1500+i*200:,.2f}"
            ))
        return activities

    def get_cashier_activities(self):
        """Generate sample activity data for cashier"""
        activities = []
        for i in range(10):
            time = (datetime.now() - timedelta(minutes=i*15)).strftime("%H:%M")
            activities.append((
                time,
                "Sale",
                "You",
                f"Completed transaction #{2000+i}",
                f"PKR {800+i*150:,.2f}"
            ))
        return activities

    def refresh_dashboard(self):
        """Refresh all dashboard components"""
        if self.frame:
            self.hide()
            self.show(self.frame.master)

    def hide(self):
        """Clean up when hiding the dashboard"""
        if self.frame:
            if hasattr(self, 'graph_canvas') and self.graph_canvas:
                self.graph_canvas.get_tk_widget().destroy()
            if hasattr(self, 'toolbar') and self.toolbar:
                self.toolbar.destroy()
            self.frame.pack_forget()