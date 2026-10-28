
"""menu.py - input helpers and menu management (add/view/update/remove)."""
from data import menu_items, cart, CATEGORIES, MAX_QTY
 
 
# ---------- input helpers (return None on invalid input) ----------
def read_int(prompt, min_value=None, max_value=None):
    text = input(prompt).strip()
    try:
        value = int(text)
    except ValueError:
        print("  [!] Please enter a whole number.")
        return None
    if min_value is not None and value < min_value:
        print(f"  [!] Value must be at least {min_value}.")
        return None
    if max_value is not None and value > max_value:
        print(f"  [!] Value must be at most {max_value}.")
        return None
    return value
 
 
def read_float(prompt):
    text = input(prompt).strip()
    try:
        value = float(text)
    except ValueError:
        print("  [!] Please enter a number.")
        return None
    if value < 0:
        print("  [!] Value cannot be negative.")
        return None
    return value
 
 
def read_text(prompt):
    text = input(prompt).strip()
    if text == "":
        print("  [!] This field cannot be empty.")
        return None
    return text
 
 
# ---------- data functions ----------
def find_item(item_id):
    """Return the menu item dictionary with this id, or None."""
    for item in menu_items:
        if item["id"] == item_id:
            return item
    return None
 
 
def name_exists(name, ignore_id=None):
    for item in menu_items:
        if item["name"].lower() == name.lower() and item["id"] != ignore_id:
            return True
    return False
 
 
def print_items(items):
    if len(items) == 0:
        print("  No items found.")
        return
    print(f"  {'ID':<4}{'Name':<22}{'Category':<12}{'Price':>8}{'Stock':>7}")
    print("  " + "-" * 53)
    for item in items:
        stock = "SOLD OUT" if item["stock"] == 0 else str(item["stock"])
        print(f"  {item['id']:<4}{item['name']:<22}{item['category']:<12}"
              f"{item['price']:>8.2f}{stock:>7}")
 
 
# ---------- user actions ----------
def view_menu():
    """View menu with sorting / filtering (data-processing operations)."""
    print("\n1. All items  2. Price low->high  3. Price high->low")
    print("4. By category  5. Search by name  6. Cheapest & most expensive")
    choice = read_int("Choose view: ", 1, 6)
    if choice is None:
        return
    if choice == 1:
        print_items(menu_items)
    elif choice == 2:
        print_items(sorted(menu_items, key=lambda i: i["price"]))
    elif choice == 3:
        print_items(sorted(menu_items, key=lambda i: i["price"], reverse=True))
    elif choice == 4:
        for number, category in enumerate(CATEGORIES, 1):
            print(f"  {number}. {category}")
        pick = read_int("Category number: ", 1, len(CATEGORIES))
        if pick is None:
            return
        result = [i for i in menu_items if i["category"] == CATEGORIES[pick - 1]]
        print_items(result)
    elif choice == 5:
        keyword = read_text("Search keyword: ")
        if keyword is None:
            return
        result = [i for i in menu_items if keyword.lower() in i["name"].lower()]
        print_items(result)
    else:
        if len(menu_items) == 0:
            print("  Menu is empty.")
            return
        cheapest = min(menu_items, key=lambda i: i["price"])
        priciest = max(menu_items, key=lambda i: i["price"])
        print(f"  Cheapest : {cheapest['name']} ({cheapest['price']:.2f})")
        print(f"  Priciest : {priciest['name']} ({priciest['price']:.2f})")
 
 
def add_menu_item():
    name = read_text("New dish name: ")
    if name is None:
        return
    if name_exists(name):                       # RULE: no duplicate dishes
        print("  [!] A dish with this name already exists.")
        return
    for number, category in enumerate(CATEGORIES, 1):
        print(f"  {number}. {category}")
    pick = read_int("Category number: ", 1, len(CATEGORIES))
    if pick is None:
        return
    price = read_float("Price: ")
    if price is None:
        return
    if price == 0:
        print("  [!] Price must be greater than 0.")
        return
    stock = read_int("Stock quantity: ", 0)
    if stock is None:
        return
    from data import next_ids
    menu_items.append({"id": next_ids["item"], "name": name,
                       "category": CATEGORIES[pick - 1],
                       "price": price, "stock": stock})
    print(f"  Added '{name}' with id {next_ids['item']}.")
    next_ids["item"] += 1
 
 
def update_menu_item():
    print_items(menu_items)
    item_id = read_int("Item id to update: ")
    if item_id is None:
        return
    item = find_item(item_id)
    if item is None:
        print("  [!] Item not found.")
        return
    print("  1. Price  2. Stock  3. Name")
    field = read_int("Update which field: ", 1, 3)
    if field is None:
        return
    if field == 1:
        price = read_float("New price: ")
        if price is None:
            return
        if price == 0:
            print("  [!] Price must be greater than 0.")
            return
        item["price"] = price
    elif field == 2:
        stock = read_int("New stock: ", 0)
        if stock is None:
            return
        item["stock"] = stock
    else:
        name = read_text("New name: ")
        if name is None:
            return
        if name_exists(name, item_id):
            print("  [!] A dish with this name already exists.")
            return
        item["name"] = name
    print("  Item updated.")
 
 
def remove_menu_item():
    print_items(menu_items)
    item_id = read_int("Item id to remove: ")
    if item_id is None:
        return
    item = find_item(item_id)
    if item is None:
        print("  [!] Item not found.")
        return
    menu_items.remove(item)
    cart[:] = [line for line in cart if line["id"] != item_id]
    print(f"  Removed '{item['name']}' (also removed from cart).")
 
 
def manage_menu():
    print("\n--- Manage Menu ---")
    print("1. Add dish  2. Update dish  3. Remove dish")
    choice = read_int("Choose: ", 1, 3)
    if choice == 1:
        add_menu_item()
    elif choice == 2:
        update_menu_item()
    elif choice == 3:
        remove_menu_item()
 
