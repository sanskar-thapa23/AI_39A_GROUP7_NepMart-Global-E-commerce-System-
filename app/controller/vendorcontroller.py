from flask import render_template, session, redirect, url_for, flash, request
from app.controller.basecontroller import BaseController
from app.model.database import Database
from app.model.productmodel import Product

class VendorController(BaseController):

    def dashboard(self):
        # 1. Get the logged-in user's ID from the session
        user_id = self.get_current_user_id()

        # Get period filter (default 30 days)
        period = request.args.get('period', '30')
        try:
            days = int(period)
        except ValueError:
            days = 30

        db = Database()

        # Calculate dashboard statistics
        # 1. Total Products count for this vendor
        prod_count_row = db.fetch_one("SELECT COUNT(*) as count FROM user_products WHERE user_id = %s", (user_id,))
        total_products = prod_count_row['count'] if prod_count_row else 0

        # 2. Orders, Unique Customers, and Revenue (Filtered by period)
        # Logic: Join orders with user_products to filter by current vendor's product ownership
        stats_query = """
            SELECT 
                COUNT(o.id) as total_orders,
                COUNT(DISTINCT o.user_id) as total_customers,
                IFNULL(SUM(o.total_amount), 0) as total_revenue
            FROM orders o
            JOIN user_products up ON o.product_id = up.product_id
            WHERE up.user_id = %s AND o.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        stats = db.fetch_one(stats_query, (user_id, days))

        # 3. Fetch Sales Trend for Chart
        trend_query = """
            SELECT DATE(o.created_at) as date, SUM(o.total_amount) as revenue
            FROM orders o
            JOIN user_products up ON o.product_id = up.product_id
            WHERE up.user_id = %s AND o.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY DATE(o.created_at)
            ORDER BY date ASC
        """
        sales_trend = db.fetch_all(trend_query, (user_id, days))
        
        # Calculate max revenue for chart scaling
        max_rev = max([day['revenue'] for day in sales_trend]) if sales_trend else 0

        # 3. Fetch only products associated with this vendor via the pivot table
        products_query = """
            SELECT p.* FROM products p
            JOIN user_products up ON p.id = up.product_id
            WHERE up.user_id = %s
            ORDER BY p.id DESC
        """
        products_data = db.fetch_all(products_query, (user_id,))
        db.close()

        # 4. Convert data to Product objects and pass everything to template
        products = [Product.from_db(item) for item in products_data]

        return render_template(
            "vendor.html",
            products=products,
            total_products=total_products,
            total_orders=stats['total_orders'] if stats else 0,
            total_customers=stats['total_customers'] if stats else 0,
            total_revenue=stats['total_revenue'] if stats else 0,
            sales_trend=sales_trend,
            max_rev=max_rev,
            period=period,
            messages=[]  # Providing empty list to avoid errors if messages table isn't ready
        )

    def products(self):
        return render_template("vendor/products.html")

    def orders(self):
        # 1. Get the logged-in vendor's ID from the session
        vendor_id = self.get_current_user_id()

        db = Database()
        # 2. Fetch orders with product details and customer name, specifically for this vendor
        query = """
            SELECT 
                o.id AS order_id, 
                o.total_amount, 
                o.status, 
                o.shipping_address, 
                o.phone_number, 
                o.created_at,
                p.product_name, 
                p.product_image,
                u.username AS customer_name
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN users u ON o.user_id = u.id
            JOIN user_products up ON p.id = up.product_id
            WHERE up.user_id = %s
            ORDER BY o.created_at DESC
        """
        orders = db.fetch_all(query, (vendor_id,))
        db.close()

        return render_template("vendor/orders.html", orders=orders)

    def analytics(self):
        user_id = self.get_current_user_id()
        
        # Get period filter (default 30 days)
        period = request.args.get('period', '30')
        try:
            days = int(period)
        except ValueError:
            days = 30

        db = Database()
        # 1. Fetch Sales Stats for the selected period
        stats_query = """
            SELECT 
                COUNT(o.id) as total_orders,
                COUNT(DISTINCT o.user_id) as total_customers,
                IFNULL(SUM(o.total_amount), 0) as total_revenue
            FROM orders o
            JOIN user_products up ON o.product_id = up.product_id
            WHERE up.user_id = %s AND o.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """
        stats = db.fetch_one(stats_query, (user_id, days))

        # 2. Fetch Sales Trend for Chart
        trend_query = """
            SELECT DATE(o.created_at) as date, SUM(o.total_amount) as revenue
            FROM orders o
            JOIN user_products up ON o.product_id = up.product_id
            WHERE up.user_id = %s AND o.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY DATE(o.created_at)
            ORDER BY date ASC
        """
        sales_trend = db.fetch_all(trend_query, (user_id, days))
        
        # Ensure revenue values are floats for Jinja calculation and safety
        processed_trend = []
        for day in sales_trend:
            processed_trend.append({
                'date': day['date'], 
                'revenue': float(day['revenue'] or 0)
            })
            
        max_rev = max([day['revenue'] for day in processed_trend]) if processed_trend else 0
        db.close()

        return render_template(
            "vendor/analytics.html",
            total_orders=stats['total_orders'] if stats else 0,
            total_customers=stats['total_customers'] if stats else 0,
            total_revenue=stats['total_revenue'] if stats else 0,
            sales_trend=processed_trend,
            max_rev=max_rev,
            period=period
        )

    def messages(self):
        return render_template("vendor/messages.html")

    def process_order(self, order_id):
        vendor_id = self.get_current_user_id()
        db = Database()
        
        # Security: Verify this order contains a product owned by this vendor
        check_query = """
            SELECT o.id FROM orders o
            JOIN user_products up ON o.product_id = up.product_id
            WHERE o.id = %s AND up.user_id = %s
        """
        if db.fetch_one(check_query, (order_id, vendor_id)):
            db.execute("UPDATE orders SET status = 'completed' WHERE id = %s", (order_id,))
            flash(f"Order #ORD-{order_id} has been marked as completed.", "success")
        else:
            flash("Unauthorized access or order not found.", "danger")
            
        db.close()
        return redirect(url_for('vendor.orders'))

    def order_details(self, order_id):
        vendor_id = self.get_current_user_id()
        db = Database()
        query = """
            SELECT 
                o.id AS order_id, o.total_amount, o.status, o.shipping_address, o.phone_number, o.created_at,
                p.product_name, p.product_image, p.product_description,
                u.username AS customer_name, u.email AS customer_email
            FROM orders o
            JOIN products p ON o.product_id = p.id
            JOIN users u ON o.user_id = u.id
            JOIN user_products up ON p.id = up.product_id
            WHERE o.id = %s AND up.user_id = %s
        """
        order = db.fetch_one(query, (order_id, vendor_id))
        db.close()
        
        if not order:
            flash("Order not found or access denied.", "danger")
            return redirect(url_for('vendor.orders'))
            
        return render_template("vendor/order_detail.html", order=order)