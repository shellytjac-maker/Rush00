"""gui.py - very simple GUI (tkinter): pick dishes, fill a cart, checkout.
 
Run with:  python3 gui.py
Uses the same data and logic as the terminal version (python3 main.py).
"""
import tkinter as tk
from tkinter import messagebox
 
from data import (RESTAURANT_NAME, MAX_QTY, menu_items, cart, orders,
                  sales_count, next_ids)
from menu import find_item
from cart import cart_subtotal, calculate_discount, cart_qty_of
 
 
def add_dish(item_id, qty):
    """Add a dish to the cart. Return an error message, or None if OK."""
    item = find_item(item_id)
    if item["stock"] == 0:                       # RULE: sold out
        return "Sorry, this dish is sold out."
    if qty < 1:
        return "Quantity must be at least 1."
    line = cart_qty_of(item_id)
    new_qty = qty + (line["qty"] if line else 0)
    if new_qty > MAX_QTY:                        # RULE: max per dish
        return f"Maximum {MAX_QTY} per dish."
    if new_qty > item["stock"]:                  # RULE: not enough stock
        return f"Only {item['stock']} left in stock."
    if line:
        line["qty"] = new_qty
    else:
        cart.append({"id": item_id, "qty": qty})
    return None
 
 
def pay(paid):
    """Pay for the cart. Return (error, message)."""
    if len(cart) == 0:                           # RULE: empty cart
        return "Cart is empty.", None
    subtotal = cart_subtotal()
    total = subtotal - calculate_discount(subtotal)
    if paid < total:                             # RULE: payment too low
        return f"Not enough money, short by {total - paid:.2f}.", None
    lines = []
    for line in cart:
        item = find_item(line["id"])
        item["stock"] -= line["qty"]
        sales_count[item["name"]] = sales_count.get(item["name"], 0) + line["qty"]
        lines.append({"name": item["name"], "qty": line["qty"], "price": item["price"]})
    orders.append({"order_no": next_ids["order"], "lines": lines, "total": total})
    next_ids["order"] += 1
    cart.clear()
    return None, f"Paid! Change: {paid - total:.2f}\nThank you!"
 
 
root = tk.Tk()
root.title(f"{RESTAURANT_NAME} Restaurant")
menu_box = tk.Listbox(root, width=40, height=10, exportselection=False)
cart_box = tk.Listbox(root, width=40, height=10, exportselection=False)
qty_var, cash_var, total_var = tk.StringVar(value="1"), tk.StringVar(), tk.StringVar()
 
 
def refresh():
    menu_box.delete(0, tk.END)
    for item in menu_items:
        stock = "SOLD OUT" if item["stock"] == 0 else f"({item['stock']} left)"
        menu_box.insert(tk.END, f"{item['name']}  {item['price']:.2f}  {stock}")
    cart_box.delete(0, tk.END)
    for line in cart:
        item = find_item(line["id"])
        cart_box.insert(tk.END, f"{item['name']} x{line['qty']}")
    subtotal = cart_subtotal()
    total_var.set(f"Total: {subtotal - calculate_discount(subtotal):.2f}")
 
 
def on_add():
    selected = menu_box.curselection()
    if not selected:
        messagebox.showwarning("Select", "Please select a dish.")
        return
    try:
        qty = int(qty_var.get())
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a whole number.")
        return
    error = add_dish(menu_items[selected[0]]["id"], qty)
    if error:
        messagebox.showerror("Error", error)
    refresh()
 
 
def on_clear():
    cart.clear()
    refresh()
 
 
def on_pay():
    try:
        paid = float(cash_var.get())
    except ValueError:
        messagebox.showerror("Error", "Cash must be a number.")
        return
    error, message = pay(paid)
    if error:
        messagebox.showerror("Error", error)
        return
    cash_var.set("")
    messagebox.showinfo("Receipt", message)
    refresh()
 
 
tk.Label(root, text="Menu").grid(row=0, column=0)
tk.Label(root, text="Cart").grid(row=0, column=1)
menu_box.grid(row=1, column=0, padx=8)
cart_box.grid(row=1, column=1, padx=8)
tk.Label(root, text="Qty:").grid(row=2, column=0, sticky="w", padx=8)
tk.Entry(root, textvariable=qty_var, width=5).grid(row=2, column=0)
tk.Button(root, text="Add to Cart", command=on_add).grid(row=2, column=0, sticky="e", padx=8)
tk.Label(root, textvariable=total_var).grid(row=2, column=1)
tk.Label(root, text="Cash:").grid(row=3, column=1, sticky="w", padx=8)
tk.Entry(root, textvariable=cash_var, width=8).grid(row=3, column=1)
tk.Button(root, text="Pay", command=on_pay).grid(row=3, column=1, sticky="e", padx=8)
tk.Button(root, text="Clear Cart", command=on_clear).grid(row=3, column=0)
tk.Button(root, text="Exit", command=root.destroy).grid(row=4, column=0, columnspan=2, pady=8)
 
refresh()
root.mainloop()
 
