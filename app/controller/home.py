from flask import render_template, abort, request

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

class MainController:

    def home(self):
        # We can supply a list of products to showcase preview elements
        return render_template("landing_page.html", active_page='home')

    def products(self):
        # Read filter options if supplied
        search_query = request.args.get('search', '').strip().lower()
        selected_category = request.args.get('category', '').strip()
        selected_location = request.args.get('location', '').strip()
        
        filtered_products = PRODUCTS
        if search_query:
            filtered_products = [p for p in filtered_products if search_query in p['name'].lower() or search_query in p['company'].lower()]
        
        if selected_category:
            filtered_products = [p for p in filtered_products if p['category'] == selected_category]
            
        if selected_location:
            filtered_products = [p for p in filtered_products if p['location'] == selected_location]

        return render_template(
            "products.html", 
            products=filtered_products, 
            active_page='products',
            search_query=search_query,
            selected_category=selected_category,
            selected_location=selected_location
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
        return render_template("dashboard.html", active_page='dashboard')

    def chat(self):
        return render_template("chat.html", active_page='chat')