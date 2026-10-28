"""cart.py - cart handling, discount rule, and checkout."""
from data import (cart, orders, sales_count, next_ids, menu_items,
                  MAX_QTY, DISCOUNT_THRESHOLD, DISCOUNT_RATE)
from menu import find_item, read_int, read_float, print_items
 
 
def cart_qty_of(item_id):
    for line in cart:
        if line["id"] == item_id:
            return line
    return None
 
 
def cart_subtotal():
    """Return the sum of price x qty for every cart line."""
    total = 0.0
    for line in cart:
        item = find_item(line["id"])
        if item is not None:
            total += item["price"] * line["qty"]
    return total
 
 
def calculate_discount(subtotal):
    """RULE: 10% discount when subtotal reaches the threshold."""
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
 
 
def add_to_cart():
    print_items(menu_items)
    item_id = read_int("Item id to order: ")
    if item_id is None:
        return
    item = find_item(item_id)
    if item is None:
        print("  [!] Item not found.")
        return
    if item["stock"] == 0:                       # RULE: unavailable item
        print("  [!] Sorry, this dish is sold out.")
        return
    qty = read_int("Quantity: ", 1)
    if qty is None:
        return
    line = cart_qty_of(item_id)
    new_qty = qty + (line["qty"] if line else 0)
    if new_qty > MAX_QTY:                        # RULE: max per item
        print(f"  [!] Maximum {MAX_QTY} per dish per order.")
        return
    if new_qty > item["stock"]:                  # RULE: not enough stock
        print(f"  [!] Only {item['stock']} left in stock.")
        return
    if line:
        line["qty"] = new_qty
    else:
        cart.append({"id": item_id, "qty": qty})
    print(f"  Added {qty} x {item['name']} to cart.")
 
 
def edit_cart():
    show_cart()
    if len(cart) == 0:
        return
    print("\n1. Change quantity  2. Remove item  3. Clear cart")
    choice = read_int("Choose: ", 1, 3)
    if choice is None:
        return
    if choice == 3:
        cart.clear()
        print("  Cart cleared.")
        return
    item_id = read_int("Item id in cart: ")
    if item_id is None:
        return
    line = cart_qty_of(item_id)
    if line is None:
        print("  [!] That item is not in your cart.")
        return
    if choice == 2:
        cart.remove(line)
        print("  Item removed from cart.")
        return
    item = find_item(item_id)
    qty = read_int(f"New quantity (1-{MAX_QTY}): ", 1, MAX_QTY)
    if qty is None:
        return
    if qty > item["stock"]:
        print(f"  [!] Only {item['stock']} left in stock.")
        return
    line["qty"] = qty
    print("  Quantity updated.")
 
 
def checkout():
    if len(cart) == 0:                           # RULE: empty cart
        print("  [!] Cart is empty. Add dishes first.")
        return
    for line in cart:                            # re-check stock
        item = find_item(line["id"])
        if item is None or line["qty"] > item["stock"]:
            print("  [!] Stock changed. Please review your cart.")
            return
    show_cart()
    subtotal = cart_subtotal()
    discount = calculate_discount(subtotal)
    total = subtotal - discount
 
    while True:                                  # RULE: enough payment
        paid = read_float(f"Cash paid (need {total:.2f}, 0 to cancel): ")
        if paid is None:
            continue
        if paid == 0:
            print("  Checkout cancelled.")
            return
        if paid < total:
            print(f"  [!] Insufficient payment, short by {total - paid:.2f}.")
        else:
            break
 
    order_lines = []
    for line in cart:
        item = find_item(line["id"])
        item["stock"] -= line["qty"]
        sales_count[item["name"]] = sales_count.get(item["name"], 0) + line["qty"]
        order_lines.append({"name": item["name"], "qty": line["qty"],
                            "price": item["price"]})
    orders.append({"order_no": next_ids["order"], "lines": order_lines,
                   "subtotal": subtotal, "discount": discount, "total": total})
    print(f"\n  Order #{next_ids['order']} complete! Change: {paid - total:.2f}")
    print("  Thank you for dining at Jasmine!")
    next_ids["order"] += 1
    cart.clear()
 
