# NepMart Global E‑commerce System

## Project Overview

_NepMart_ is a Python Flask‑based B2B e‑commerce platform that showcases a catalog of Himalayan products. The application demonstrates a clean **object‑oriented architecture**, a MySQL backend, and a **machine‑learning recommendation engine** that suggests similar products based on product descriptions.

## Key Features

- **Product Catalog** – Static catalogue (with a plan to migrate to DB) displaying product details, images, and pricing.
- **User‑friendly UI** – Jinja2 templates with a modern, responsive design.
- **ML Recommendations** – TF‑IDF + cosine similarity powered engine that returns the top‑3 related products on each product page.
- **REST‑like routing** – Blueprint‑based Flask routes for clean separation of concerns.
- **Extensible Architecture** – Abstract `BaseModel` and `Database` utilities for easy addition of new models.

## Architecture Overview

```
app/
├─ controller/
│   └─ home.py          # route handlers & static PRODUCT list
├─ model/
│   ├─ base.py          # BaseModel abstract class
│   ├─ product.py       # Product ORM wrapper
│   ├─ recommendation.py# RecommendationEngine (TF‑IDF)
│   └─ database.py      # MySQL connection helper
├─ templates/
│   ├─ index.html
│   ├─ product_detail.html
│   └─ ...
└─ static/               # CSS/JS assets
```

- `run.py` boots the Flask app.
- `app/controller/home.py` loads the product list and injects recommendations.
- `app/model/recommendation.py` builds the TF‑IDF matrix on startup and exposes `get_recommendations(product_id, top_n=3)`.

## Tech Stack

- **Python 3.13**
- **Flask** – lightweight web framework
- **MySQL** – relational data store (configured in `app/model/database.py`)
- **scikit‑learn** – TF‑IDF vectorizer & cosine similarity
- **Jinja2** – HTML templating
- **Bootstrap 5** – UI styling

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd NepMart-Global-E-commerce-System
   ```
2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure the database**
   - Edit `app/model/database.py` with your MySQL credentials.
   - Run the provided schema script (found in `db/schema.sql`).
5. **Run the application**
   ```bash
   python run.py
   ```
   The site will be available at `http://localhost:5000`.

## Using the Recommendation Engine

The engine is initialised at import time:
```python
from app.model.recommendation import RecommendationEngine
engine = RecommendationEngine()
```
When a product page is rendered, `home.py` calls:
```python
recommendations = engine.get_recommendations(product.id)
```
The resulting list of product dictionaries is passed to `product_detail.html` and displayed as "You may also like" cards.

## Adding New Products

Current implementation stores products in the `PRODUCTS` list inside `app/controller/home.py`. To add more items, edit that list with the following schema:
```python
{
    "id": <int>,
    "name": "<Product Name>",
    "price": <float>,
    "description": "<Short description>",
    "image": "<static/image.jpg>"
}
```
After adding items, the recommendation matrix will automatically include them on the next server restart.

## Contributing

1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/awesome`).
3. Ensure code follows the existing OOP patterns.
4. Run tests (`pytest tests/`).
5. Submit a Pull Request.

## License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.

---
*Generated on 2026‑06‑08*
