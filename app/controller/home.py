from flask import render_template, abort, request, session, redirect, url_for, flash
from app.model.database import Database
from app.model.productmodel import Product
from app.controller.basecontroller import BaseController

# Mock Database Storehouse representing our verified Himalayan B2B ecosystem

PRODUCTS = [
    {
        "id": 1,
        "name": "Organic Himalayan Tea Leaves",
        "company": "Nepal Agro Export Co.",
        "category": "Agro",
        "category_display": "Himalayan Agro & Herbs",
        "price_range": "USD 8.50 - 12.00 / KG",
        "moq": "500 KG",
        "location": "Kathmandu",
        "rating": 4.9,
        "reviews_count": 42,
        "trader_id": 1,
        "description": "Our premium organic Himalayan black tea leaves are hand-plucked from the high-altitude hills of Ilam, Nepal. Naturally rich in antioxidants and processed using traditional orthodox methods, this tea offers a unique floral aroma and delicate, smooth finish prized by global tea connoisseurs.",
        "specs": {
            "packing": "25 KG Double-wall Kraft Sacks",
            "certification": "USDA Organic, EU Organic Standard",
            "freight": "Air Cargo to Tokyo, Frankfurt, NYC",
            "hscode": "0902.30.00 (Orthodox Tea)"
        }
    },
    {
        "id": 2,
        "name": "Handwoven Pashmina Shawls",
        "company": "Himalayan Crafts Co.",
        "category": "Crafts",
        "category_display": "Handmade Crafts",
        "price_range": "USD 35.00 - 45.00 / Unit",
        "moq": "100 Units",
        "location": "Pokhara",
        "rating": 4.8,
        "reviews_count": 28,
        "trader_id": 2,
        "description": "Genuine 100% Chyangra Pashmina shawls, hand-woven on traditional wooden looms by local weavers in Pokhara. Sourced from authentic mountain goat cashmere, these premium lightweight shawls are exceptionally warm, soft, and dyed using eco-friendly non-toxic agents, matching luxury B2B specifications.",
        "specs": {
            "packing": "Individual gift boxes, bulk cartons",
            "certification": "Chyangra Pashmina Trademark",
            "freight": "DHL, FedEx, UPS door-to-door express",
            "hscode": "6214.20.00 (Cashmere Shawls)"
        }
    },
    {
        "id": 3,
        "name": "Industrial Rice Mill Machine",
        "company": "TechMachinery Nepal",
        "category": "Industrial",
        "category_display": "Industrial Machinery",
        "price_range": "USD 1,500 - 1,950 / Unit",
        "moq": "2 Units",
        "location": "Biratnagar",
        "rating": 4.7,
        "reviews_count": 19,
        "trader_id": 3,
        "description": "Heavy-duty industrial grain processing mill, capable of multi-stage polishing, de-husking, and optical sorting at a rate of 1.5 Tons/hour. Manufactured with wear-resistant hardened steel components and low-noise electric motors, optimized for rural off-grid power grids.",
        "specs": {
            "packing": "Seaworthy steel cages / wooden crates",
            "certification": "CE Mark, ISO 9001:2015 Standards",
            "freight": "Border land freight, Sea freight via Kolkata",
            "hscode": "8437.80.00 (Grain Milling Machinery)"
        }
    }
]

TRADERS = [
    {
        "id": 1,
        "name": "Nepal Agro Export Co.",
        "type": "Exporter",
        "sector": "Organic Agriculture",
        "short_desc": "Leading global distributor of organic mountain herbs, Himalayan orthodox tea, wild ginger, and organic honey.",
        "about_desc": "Established in 2015, Nepal Agro Export Co. operates processing facilities in Ilam and Dhankuta, supporting over 2,000 micro-farmers. We specialize in supply-chain transparency, organic certification standards, and air freight logistics to Europe and Asia.",
        "location": "Kathmandu",
        "years_verified": 8,
        "response_time": "Fastest (< 1 hr)",
        "rating": 4.9,
        "reviews_count": 42
    },
    {
        "id": 2,
        "name": "Himalayan Crafts Co.",
        "type": "Manufacturer",
        "sector": "Handmade Luxury Crafts",
        "short_desc": "Artisanal workshop specializing in certified cashmere shawls, hand-spun wool carpets, and high-purity metal artifacts.",
        "about_desc": "Himalayan Crafts Co. is an award-winning social enterprise in Pokhara employing over 80 master weavers. Our products are exported to luxury boutiques in Tokyo, Paris, and London, guaranteeing authentic craftsmanship and premium quality controls.",
        "location": "Pokhara",
        "years_verified": 6,
        "response_time": "Very Fast (< 2 hrs)",
        "rating": 4.8,
        "reviews_count": 28
    },
    {
        "id": 3,
        "name": "TechMachinery Nepal",
        "type": "Broker",
        "sector": "Agro-Industrial Machinery",
        "short_desc": "Importer, assembler, and customs broker for high-efficiency farming machinery, milling units, and warehouse equipment.",
        "about_desc": "Operating since 2018 in Biratnagar's industrial corridor, TechMachinery Nepal engineers custom milling facilities and grain elevators. We also provide full freight clearance and custom transit support for imports across Nepal's land borders.",
        "location": "Biratnagar",
        "years_verified": 5,
        "response_time": "Fast (< 4 hrs)",
        "rating": 4.7,
        "reviews_count": 19
    }
]

class MainController(BaseController):

    def home(self):
        # We can supply a list of products to showcase preview elements
        return render_template("landing_page.html", active_page='home')

    def products(self):
        db = Database()

        # 1. Get query parameters
        search = request.args.get("search", "").strip()
        category = request.args.get("category", "").strip()
        location = request.args.get("location", "").strip()
        sort = request.args.get("sort", "").strip()

        # 2. Build Query with JOIN to get the Vendor Name (Company)
        query = """
            SELECT p.*, u.username AS vendor_name 
            FROM products p
            LEFT JOIN user_products up ON p.id = up.product_id
            LEFT JOIN users u ON up.user_id = u.id
            WHERE 1=1
        """
        params = []

        if search:
            query += " AND p.product_name LIKE %s"
            params.append(f"%{search}%")

        # Sorting
        if sort == "low":
            query += " ORDER BY p.product_price ASC"
        elif sort == "high":
            query += " ORDER BY p.product_price DESC"
        else:
            query += " ORDER BY p.id DESC"

        # 3. Fetch Data
        products_data = db.fetch_all(query, tuple(params))
        db.close()

        # 4. Convert to Product objects
        products = [Product.from_db(item) for item in products_data]

        return render_template(
            "products.html", 
            products=products, 
            active_page='products',
            search_query=search,
            selected_category=category,
            selected_location=location,
            sort=sort
        )

    def product_detail(self, product_id):
        product = next((p for p in PRODUCTS if p['id'] == product_id), None)
        if not product:
            abort(404)
        return render_template("product_detail.html", product=product, active_page='products')

    def traders(self):
        search_query = request.args.get('search', '').strip().lower()
        selected_business_type = request.args.get('business_type', '').strip()
        
        filtered_traders = TRADERS
        if search_query:
            filtered_traders = [t for t in filtered_traders if search_query in t['name'].lower() or search_query in t['sector'].lower()]
            
        if selected_business_type:
            filtered_traders = [t for t in filtered_traders if t['type'] == selected_business_type]

        return render_template(
            "traders.html", 
            traders=filtered_traders, 
            active_page='traders',
            search_query=search_query,
            selected_business_type=selected_business_type
        )

    def trader_profile(self, trader_id):
        trader = next((t for t in TRADERS if t['id'] == trader_id), None)
        if not trader:
            abort(404)
            
        # Extract items owned by this specific trader
        listed_products = [p for p in PRODUCTS if p['trader_id'] == trader_id]
        
        return render_template(
            "trader_profile.html", 
            trader=trader, 
            listed_products=listed_products,
            active_page='traders'
        )

    def dashboard(self):
        user_id = self.get_current_user_id()
        if not user_id:
            return redirect(url_for('auth.login'))

        db = Database()
        
        # 1. Fetch real orders with product details
        orders = db.fetch_all("""
            SELECT o.id AS order_id, o.total_amount AS amount, o.status, p.product_name AS product 
            FROM orders o
            LEFT JOIN products p ON o.product_id = p.id
            WHERE o.user_id = %s 
            ORDER BY o.created_at DESC 
            LIMIT 5
        """, (user_id,))

        # 2. Fetch Wishlist (including product ID for navigation)
        wishlist = db.fetch_all("""
            SELECT p.id, p.product_name AS name, p.category, p.product_price AS price, p.product_image AS image
            FROM wishlist w
            JOIN products p ON w.product_id = p.id
            WHERE w.user_id = %s
        """, (user_id,))

        # 3. Fetch Shopping Cart
        cart_items = db.fetch_all("""
            SELECT p.id, p.product_name AS name, p.product_price AS price, p.product_image AS image, sc.quantity, p.category
            FROM shopping_cart sc
            JOIN products p ON sc.product_id = p.id
            WHERE sc.user_id = %s
        """, (user_id,))

        # 4. Fetch statistics
        stats = db.fetch_one("""
            SELECT 
                COUNT(*) AS total_orders, 
                IFNULL(SUM(total_amount), 0) AS total_spending 
            FROM orders 
            WHERE user_id = %s
        """, (user_id,))
        
        db.close()

        return render_template(
            "customer.html", 
            active_page='dashboard',
            total_orders=stats['total_orders'],
            wishlist_count=len(wishlist),
            saved_vendors=0,
            total_spending=f"{stats['total_spending']:.2f}",
            orders=orders,
            wishlist=wishlist,
            cart_items=cart_items
        )

    def checkout(self):
        user_id = self.get_current_user_id()
        if not user_id:
            return redirect(url_for('auth.login'))

        if request.method == 'POST':
            address, phone = self.get_form_data('address', 'phone')

            if not address or not phone:
                flash("Shipping address and phone number are required.", "danger")
                return redirect(url_for('main.dashboard'))

            db = Database()
            try:
                # 1. Fetch items currently in the user's cart
                cart_items = db.fetch_all("""
                    SELECT sc.product_id, sc.quantity, p.product_price
                    FROM shopping_cart sc
                    JOIN products p ON sc.product_id = p.id
                    WHERE sc.user_id = %s
                """, (user_id,))

                if cart_items:
                    # 2. Transfer cart items to the orders table
                    for item in cart_items:
                        total = item['product_price'] * item['quantity']
                        db.execute("""
                            INSERT INTO orders (user_id, product_id, total_amount, status, shipping_address, phone_number)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (user_id, item['product_id'], total, 'pending', address, phone))
                    
                    # 3. Clear the shopping cart
                    db.execute("DELETE FROM shopping_cart WHERE user_id = %s", (user_id,))
                    flash("Order placed successfully! Payment method: Cash on Delivery.", "success")
                else:
                    flash("Your cart is empty.", "warning")
            except Exception as e:
                flash(f"Checkout failed: {str(e)}", "danger")
            finally:
                db.close()

        return redirect(url_for('main.dashboard'))

    def chat(self):
        return render_template("chat.html", active_page='chat')