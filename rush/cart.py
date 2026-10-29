"""cart.py - view/edit cart, summary, and checkout."""
from data import cart, MAX_QTY, DISCOUNT_THRESHOLD, DISCOUNT_RATE
from menu import read_int, find_item, find_cart_line


def cart_subtotal():
    """Return the sum of price x qty for every cart line."""
    total = 0.0
    for line in cart:
        item = find_item(line["id"])
        total += item["price"] * line["qty"]
    return total


def calculate_discount(subtotal):
    """RULE: 10% discount when the subtotal reaches the threshold."""
    if subtotal >= DISCOUNT_THRESHOLD:
        return subtotal * DISCOUNT_RATE
    return 0.0


def show_cart():
    if len(cart) == 0:
        print("  Your cart is empty.")
        return
    print(f"  {'ID':<4}{'Name':<22}{'Qty':>5}{'Price':>9}{'Total':>10}")
    print("  " + "-" * 50)
    for line in cart:
        item = find_item(line["id"])
        print(f"  {item['id']:<4}{item['name']:<22}{line['qty']:>5}"
              f"{item['price']:>9.2f}{item['price'] * line['qty']:>10.2f}")
    subtotal = cart_subtotal()
    discount = calculate_discount(subtotal)
    print("  " + "-" * 50)
    print(f"  Subtotal: {subtotal:.2f}   Discount: -{discount:.2f}"
          f"   Total: {subtotal - discount:.2f}")


def view_edit_cart():
    show_cart()
    if len(cart) == 0:
        return

    print("\n1. Change quantity")
    print("2. Remove an item")
    print("3. Clear cart")
    print("4. Back")
    choice = read_int("Choose: ", 1, 4)
    if choice is None or choice == 4:
        return

    if choice == 3:
        cart.clear()
        print("  Cart cleared.")
        return

    item_id = read_int("Item id in cart: ", 1, 9999)
    if item_id is None:
        return
    line = find_cart_line(item_id)
    if line is None:
        print("  [!] That item is not in your cart.")
        return

    if choice == 2:
        cart.remove(line)
        print("  Item removed.")
    else:
        item = find_item(item_id)
        limit = min(MAX_QTY, item["stock"])
        qty = read_int(f"New quantity (1-{limit}): ", 1, limit)
        if qty is None:
            return
        line["qty"] = qty
        print("  Quantity updated.")

def checkout():
    if len(cart) == 0:                           # RULE: empty cart
        print("  [!] Cart is empty. Add dishes first.")
        return

    show_cart()
    subtotal = cart_subtotal()
    total = subtotal - calculate_discount(subtotal)

    for line in cart:                            # take dishes out of stock
        item = find_item(line["id"])
        item["stock"] -= line["qty"]

    print(f"\n  Final price to pay: {total:.2f} baht")
    print("  Thank you for dining at Jasmine!")
    cart.clear()