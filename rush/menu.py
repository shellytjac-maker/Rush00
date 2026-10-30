"""menu.py - input helper, menu viewing, and adding to the cart."""
from data import menu_items, cart, CATEGORIES, MAX_QTY
 
 
def read_int(prompt, min_value, max_value):
    """Ask for a whole number in range. Return None if the input is bad."""
    try:
        value = int(input(prompt))
    except ValueError:
        print("  [!] Please enter a whole number.")
        return None
    if value < min_value or value > max_value:
        print(f"  [!] Please enter a number between {min_value} and {max_value}.")
        return None
    return value
 
 
def find_item(item_id):
    """Return the menu dictionary with this id, or None."""
    for item in menu_items:
        if item["id"] == item_id:
            return item
    return None
 
 
def find_cart_line(item_id):
    """Return the cart line with this id, or None."""
    for line in cart:
        if line["id"] == item_id:
            return line
    return None
 
 
def print_items(items):
    for item in items:
        print(f"  {item['id']}. {item['name']} ({item['category']}) - "
              f"{item['price']:.2f} - stock {item['stock']}")
 
 
def view_menu():
    print("1. All items  2. By category  3. Price low to high")
    choice = read_int("Choose: ", 1, 3)
    if choice == 1:
        print_items(menu_items)
    elif choice == 2:                            # search by condition
        for number, category in enumerate(CATEGORIES, 1):
            print(f"  {number}. {category}")
        pick = read_int("Category number: ", 1, len(CATEGORIES))
        if pick is not None:
            for item in menu_items:
                if item["category"] == CATEGORIES[pick - 1]:
                    print_items([item])
    elif choice == 3:                            # sorting
        print_items(sorted(menu_items, key=lambda item: item["price"]))
 
 
def add_to_cart():
    print_items(menu_items)
    item_id = read_int("Item id to order: ", 1, 9999)
    qty = read_int("Quantity: ", 1, 9999)
    if item_id is None or qty is None:
        return
    item = find_item(item_id)
    line = find_cart_line(item_id)
    total_qty = qty
    if line is not None:
        total_qty = qty + line["qty"]
 
    if item is None:                             # RULE 1: item must exist
        print("  [!] Item not found.")
    elif item["stock"] == 0:                     # RULE 2: sold out
        print("  [!] Sorry, this dish is sold out.")
    elif total_qty > MAX_QTY:                    # RULE 3: max per dish
        print(f"  [!] Maximum {MAX_QTY} per dish per order.")
    elif total_qty > item["stock"]:              # RULE 4: not enough stock
        print(f"  [!] Only {item['stock']} left in stock.")
    elif line is None:
        cart.append({"id": item_id, "qty": qty})
        print(f"  Added {qty} x {item['name']} to cart.")
    else:
        line["qty"] = total_qty
        print(f"  Added {qty} x {item['name']} to cart.")
 
