RESTAURANT_NAME = "Jasmine"
CATEGORIES = ["Appetizer", "Main", "Dessert", "Drink"]

MAX_QTY = 10               # max quantity per dish in the cart
DISCOUNT_THRESHOLD = 500   # subtotal needed for a discount
DISCOUNT_RATE = 0.10       # 10% discount

# LIST of DICTIONARIES: each dish is one dictionary
menu_items = [
    {"id": 1, "name": "Tom Yum Goong", "category": "Appetizer", "price": 150.0, "stock": 15},
    {"id": 2, "name": "Spring Rolls", "category": "Appetizer", "price": 80.0, "stock": 20},
    {"id": 3, "name": "Pad Thai", "category": "Main", "price": 120.0, "stock": 25},
    {"id": 4, "name": "Green Curry", "category": "Main", "price": 140.0, "stock": 18},
    {"id": 5, "name": "Mango Sticky Rice", "category": "Dessert", "price": 90.0, "stock": 12},
    {"id": 6, "name": "Thai Iced Tea", "category": "Drink", "price": 50.0, "stock": 30},
    {"id": 7, "name": "Jasmine Tea", "category": "Drink", "price": 40.0, "stock": 30},
]

# Cart: list of {"id": item_id, "qty": quantity}
cart = []
