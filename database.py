import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

class InventoryDB:
    def __init__(self, db_name: str = 'inventory.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        """Create the products table if it doesn't exist"""
        query = """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            company TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            trade_price REAL NOT NULL,
            mfg_price REAL NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT NOT NULL,
            worth REAL GENERATED ALWAYS AS (trade_price * quantity) STORED
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_product(self, product: Dict) -> int:
        """Add a new product to the database"""
        query = """
        INSERT INTO products (name, category, company, code, trade_price, mfg_price, quantity, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (
            product['name'],
            product['category'],
            product['company'],
            product['code'],
            product['trade_price'],
            product['mfg_price'],
            product['quantity'],
            product['status']
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_products(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get products with optional filters"""
        base_query = "SELECT * FROM products"
        params = []
        
        if filters:
            where_clauses = []
            
            # Category filter
            if filters.get('category') and filters['category'] != "All Categories":
                where_clauses.append("category = ?")
                params.append(filters['category'])
                
            # Company filter
            if filters.get('company') and filters['company'] != "All Companies":
                where_clauses.append("company = ?")
                params.append(filters['company'])
                
            # Status filter
            if filters.get('status') and filters['status'] != "All Status":
                status_map = {
                    "In Stock": "In Stock",
                    "Low Stock": "Low Stock", 
                    "Out of Stock": "Out of Stock"
                }
                if filters['status'] in status_map:
                    where_clauses.append("status = ?")
                    params.append(status_map[filters['status']])
                    
            # Price range filter
            if filters.get('range_type') == "Price Range":
                min_price = filters.get('min_price', 0)
                max_price = filters.get('max_price', float('inf'))
                where_clauses.append("trade_price BETWEEN ? AND ?")
                params.extend([min_price, max_price])
                
            # Quantity range filter
            elif filters.get('range_type') == "Quantity Range":
                min_qty = filters.get('min_qty', 0)
                max_qty = filters.get('max_qty', float('inf'))
                where_clauses.append("quantity BETWEEN ? AND ?")
                params.extend([min_qty, max_qty])
                
            # Search query
            if filters.get('search_query'):
                search = f"%{filters['search_query']}%"
                where_clauses.append("""
                    (name LIKE ? OR 
                    category LIKE ? OR 
                    company LIKE ? OR 
                    code LIKE ?)
                """)
                params.extend([search, search, search, search])
                
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
        
        cursor = self.conn.cursor()
        cursor.execute(base_query, params)
        
        products = []
        for row in cursor.fetchall():
            products.append({
                'id': row[0],
                'name': row[1],
                'category': row[2],
                'company': row[3],
                'code': row[4],
                'trade_price': row[5],
                'mfg_price': row[6],
                'quantity': row[7],
                'status': row[8],
                'worth': row[9]
            })
            
        return products

    def update_product(self, product_id: int, updates: Dict) -> bool:
        """Update a product's information"""
        set_clauses = []
        params = []
        
        for field, value in updates.items():
            set_clauses.append(f"{field} = ?")
            params.append(value)
            
        if not set_clauses:
            return False
            
        query = f"UPDATE products SET {', '.join(set_clauses)} WHERE id = ?"
        params.append(product_id)
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        
        return cursor.rowcount > 0

    def delete_product(self, product_id: int) -> bool:
        """Delete a product from the database"""
        query = "DELETE FROM products WHERE id = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (product_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def restock_product(self, product_id: int, amount: int) -> bool:
        """Increase a product's quantity by specified amount and update status"""
        if amount <= 0:
            return False
            
        query = """
        UPDATE products 
        SET quantity = quantity + ?,
            status = CASE 
                WHEN quantity + ? <= 0 THEN 'Out of Stock'
                WHEN quantity + ? <= 10 THEN 'Low Stock'
                ELSE 'In Stock'
            END
        WHERE id = ?
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (amount, amount, amount, product_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_all_categories(self) -> List[str]:
        """Get all unique product categories from the database"""
        query = "SELECT DISTINCT category FROM products ORDER BY category"
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]

    def get_all_companies(self) -> List[str]:
        """Get all unique companies from the database"""
        query = "SELECT DISTINCT company FROM products ORDER BY company"
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]
    
    def get_product_stock(self, product_id):
        """Get current stock quantity for a product"""
        self.cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None
        
    def update_product_quantity(self, product_id, quantity_change):
        """Update product quantity in inventory"""
        try:
            self.cursor.execute("""
                UPDATE products 
                SET quantity = quantity + ? 
                WHERE id = ?
            """, (quantity_change, product_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating product quantity: {e}")
            self.conn.rollback()
            return False
    
    def close(self):
        """Close the database connection"""
        self.conn.close()

class CounterDB:
    def __init__(self, db_name: str = 'Counter.db'):
        """Initialize the counters database"""
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        """Create all necessary tables for counters and sales"""
        try:
            # Counters table
            counters_query = """
            CREATE TABLE IF NOT EXISTS counters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cashier_name TEXT NOT NULL UNIQUE,
                cashier_id INTEGER NOT NULL,
                device_id TEXT,
                status TEXT DEFAULT 'active',
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            self.conn.execute(counters_query)
            
            # Sales table
            sales_query = """
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id TEXT NOT NULL UNIQUE,
                counter_id INTEGER NOT NULL,
                cashier_id INTEGER NOT NULL,
                cashier_name TEXT NOT NULL,
                customer_name TEXT,
                total_amount REAL NOT NULL,
                payment_method TEXT DEFAULT 'cash',
                sale_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (counter_id) REFERENCES counters(id)
            )
            """
            self.conn.execute(sales_query)
            
            # Sale items table
            sale_items_query = """
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id)
            );
            """
            self.conn.execute(sale_items_query)
            
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
            raise

    def add_counter(self, cashier_name: str, cashier_id: int, device_id: str, password: str, status: str = 'active') -> int:
        """Add a new counter to the database"""
        query = """
        INSERT INTO counters (cashier_name, cashier_id, device_id, password, status) 
        VALUES (?, ?, ?, ?, ?)
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (cashier_name, cashier_id, device_id, password, status))
        self.conn.commit()
        return cursor.lastrowid

    def get_counters(self, active_only: bool = True) -> List[Dict]:
        """Get all counters, optionally filtered by active status"""
        query = "SELECT id, cashier_name, cashier_id, device_id, status, password, created_at FROM counters"
        params = []

        if active_only:
            query += " WHERE status = 'active'"
        
        query += " ORDER BY id"
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def update_counter(self, counter_id: int, updates: Dict) -> bool:
        """Update counter information"""
        allowed_fields = {"cashier_name", "cashier_id", "device_id", "status", "password"}
        set_clauses = []
        params = []

        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = ?")
                params.append(value)

        if not set_clauses:
            return False  # No valid fields to update

        query = f"UPDATE counters SET {', '.join(set_clauses)} WHERE id = ?"
        params.append(counter_id)

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount > 0

    def record_sale(self, sale_data: Dict) -> Dict:
        """Record a new sale in the database with proper error handling"""
        cursor = self.conn.cursor()
        
        try:
            # Insert sale record
            sale_query = """
            INSERT INTO sales (
                receipt_id, counter_id, cashier_id, cashier_name,
                customer_name, total_amount, payment_method, sale_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sale_query, (
                sale_data['receipt_id'],
                sale_data['counter_id'],
                sale_data['cashier_id'],
                sale_data['cashier_name'],
                sale_data.get('customer_name', ''),
                sale_data['total_amount'],
                sale_data.get('payment_method', 'cash'),
                sale_data.get('sale_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            ))
            sale_id = cursor.lastrowid
            
            # Insert sale items
            items_query = """
            INSERT INTO sale_items (
                sale_id, product_id, product_name, 
                quantity, unit_price, total_price
            ) VALUES (?, ?, ?, ?, ?, ?)
            """
            
            for item in sale_data['items']:
                if not all(key in item for key in ['product_id', 'product_name', 'quantity', 'unit_price', 'total_price']):
                    raise ValueError("Invalid item data structure")
                    
                cursor.execute(items_query, (
                    sale_id,
                    item['product_id'],
                    item['product_name'],
                    item['quantity'],
                    item['unit_price'],
                    item['total_price']
                ))
            
            self.conn.commit()
            return {'success': True, 'sale_id': sale_id}
            
        except sqlite3.Error as e:
            self.conn.rollback()
            return {'success': False, 'error': f"Database error: {str(e)}"}
        except Exception as e:
            self.conn.rollback()
            return {'success': False, 'error': f"System error: {str(e)}"}
    
    def get_sales_history(self, filters: Dict = None) -> List[Dict]:
        """Get sales history with optional filters"""
        base_query = """
        SELECT 
            s.id, 
            s.receipt_id, 
            s.counter_id,
            s.cashier_id, 
            s.cashier_name, 
            s.customer_name, 
            s.total_amount, 
            s.payment_method,
            s.sale_time
        FROM sales s
        """
        params = []
        
        if filters:
            where_clauses = []
            
            # Date range filter
            if filters.get('start_date'):
                where_clauses.append("DATE(s.sale_time) >= ?")
                params.append(filters['start_date'])
            if filters.get('end_date'):
                where_clauses.append("DATE(s.sale_time) <= ?")
                params.append(filters['end_date'])
                
            # Counter filter
            if filters.get('counter_id'):
                where_clauses.append("s.counter_id = ?")
                params.append(filters['counter_id'])
                
            # Cashier filter
            if filters.get('cashier_id'):
                where_clauses.append("s.cashier_id = ?")
                params.append(filters['cashier_id'])
                
            if where_clauses:
                base_query += " WHERE " + " AND ".join(where_clauses)
        
        base_query += " ORDER BY s.sale_time DESC"
        
        cursor = self.conn.cursor()
        cursor.execute(base_query, params)
        
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
    def get_sale_details(self, sale_id):
        """Get detailed information about a specific sale"""
        try:
            # Get sale header
            header_query = """
            SELECT 
                id, receipt_id, cashier_name, customer_name,
                total_amount, payment_method, sale_time
            FROM sales
            WHERE id = ?
            """
            self.cursor.execute(header_query, (sale_id,))
            header = self.cursor.fetchone()
            
            if not header:
                return None
                
            # Get sale items
            items_query = """
            SELECT 
                product_id, product_name, quantity, 
                unit_price, total_price
            FROM sale_items
            WHERE sale_id = ?
            """
            self.cursor.execute(items_query, (sale_id,))
            items = self.cursor.fetchall()
            
            return {
                'id': header[0],
                'receipt_id': header[1],
                'cashier_name': header[2],
                'customer_name': header[3],
                'total_amount': header[4],
                'payment_method': header[5],
                'sale_time': header[6],
                'items': [{
                    'product_id': item[0],
                    'product_name': item[1],
                    'quantity': item[2],
                    'unit_price': item[3],
                    'total_price': item[4]
                } for item in items]
            }
            
        except Exception as e:
            print(f"Error getting sale details: {e}")
            return None
    
    def get_transactions_for_counter(self, counter_id):
        """Get all transactions for a specific counter"""
        query = """
        SELECT id, receipt_id, customer_name, total_amount, sale_time
        FROM sales
        WHERE counter_id = ?
        ORDER BY sale_time DESC
        """
        cursor = self.conn.cursor()
        cursor.execute(query, (counter_id,))
        
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_sales_by_date(self, date):
        """Get all sales for a specific date (YYYY-MM-DD format)"""
        try:
            query = """
                SELECT 
                    id, 
                    receipt_id, 
                    customer_name, 
                    total_amount, 
                    sale_time, 
                    cashier_name
                FROM sales
                WHERE DATE(sale_time) = ?
                ORDER BY sale_time DESC
            """
            self.cursor.execute(query, (date,))
            
            columns = [col[0] for col in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting sales by date: {e}")
            return []

    def get_all_sales(self):
        """Get all sales records with consistent return format"""
        try:
            query = """
                SELECT 
                    id,
                    receipt_id,
                    customer_name,
                    total_amount,
                    sale_time,
                    cashier_name
                FROM sales
                ORDER BY sale_time DESC
            """
            self.cursor.execute(query)
            
            columns = [col[0] for col in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting all sales: {e}")
            return []
    
    def get_sales_by_cashier(self, cashier_name):
        """Get all sales records for a specific cashier with all needed fields"""
        try:
            self.cursor.execute("""
                SELECT 
                    id, receipt_id, customer_name, total_amount, sale_time
                FROM sales
                WHERE cashier_name = ?
                ORDER BY sale_time DESC
            """, (cashier_name,))
            
            columns = [col[0] for col in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting sales by cashier: {e}")
            return []
        
    def get_sales_by_date_and_cashier(self, date, cashier_name):
        """Get sales for specific date and cashier"""
        try:
            self.cursor.execute("""
                SELECT 
                    id, receipt_id, customer_name, total_amount, sale_time
                FROM sales
                WHERE DATE(sale_time) = ? AND cashier_name = ?
                ORDER BY sale_time DESC
            """, (date, cashier_name))
            
            columns = [col[0] for col in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting sales by date and cashier: {e}")
            return []

    def close(self):
        """Close the database connection"""
        self.conn.close()