"""menu.py - input helper, menu viewing, and adding to the cart."""
from data import menu_items, cart, CATEGORIES, MAX_QTY


def read_int(prompt, min_value, max_value):
    """Ask for a whole number in range. Return None if the input is bad."""
    text = input(prompt).strip()
    try:
        value = int(text)
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
    if len(items) == 0:
        print("  No items found.")
        return
    print(f"  {'ID':<4}{'Name':<22}{'Category':<12}{'Price':>8}{'Stock':>7}")
    print("  " + "-" * 53)
    for item in items:
        if item["stock"] == 0:
            stock = "SOLD OUT"
        else:
            stock = str(item["stock"])
        print(f"  {item['id']:<4}{item['name']:<22}{item['category']:<12}"
              f"{item['price']:>8.2f}{stock:>7}")


def view_menu():
    print("\n1. All items")
    print("2. Category")
    print("3. Lowest price to highest")
    choice = read_int("Choose: ", 1, 3)
    if choice is None:
        return

    if choice == 1:
        print_items(menu_items)
    elif choice == 2:
        for number, category in enumerate(CATEGORIES, 1):
            print(f"  {number}. {category}")
        pick = read_int("Category number: ", 1, len(CATEGORIES))
        if pick is None:
            return
        result = []
        for item in menu_items:
            if item["category"] == CATEGORIES[pick - 1]:
                result.append(item)
        print_items(result)
    else:
        print_items(sorted(menu_items, key=lambda item: item["price"]))


def add_to_cart():
    print_items(menu_items)
    item_id = read_int("Item id to order: ", 1, 9999)
    if item_id is None:
        return
    item = find_item(item_id)
    if item is None:                             # RULE: item must exist
        print("  [!] Item not found.")
        return
    if item["stock"] == 0:                       # RULE: sold out
        print("  [!] Sorry, this dish is sold out.")
        return

    qty = read_int("Quantity: ", 1, 9999)
    if qty is None:
        return

    line = find_cart_line(item_id)
    if line is None:
        new_qty = qty
    else:
        new_qty = line["qty"] + qty

    if new_qty > MAX_QTY:                        # RULE: max per dish
        print(f"  [!] Maximum {MAX_QTY} per dish per order.")
        return
    if new_qty > item["stock"]:                  # RULE: not enough stock
        print(f"  [!] Only {item['stock']} left in stock.")
        return

    if line is None:
        cart.append({"id": item_id, "qty": qty})
    else:
        line["qty"] = new_qty
    print(f"  Added {qty} x {item['name']} to cart.")