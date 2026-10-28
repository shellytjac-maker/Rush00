"""gui.py - optional graphical interface (tkinter) for the Jasmine restaurant.
 
Run with:  python3 gui.py
The terminal version (python3 main.py) still works independently.
It re-uses the same data (data.py) and logic (menu.py, cart.py).
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
 
from data import (RESTAURANT_NAME, CATEGORIES, MAX_QTY, DISCOUNT_THRESHOLD,
                  menu_items, cart, orders, sales_count, next_ids)
from menu import find_item, name_exists
from cart import cart_subtotal, calculate_discount, cart_qty_of
 
SORT_OPTIONS = ["ID", "Name", "Price low->high", "Price high->low"]
 
 
# ---------- logic (return an error message, or None when OK) ----------
def gui_add_to_cart(item_id, qty):
    item = find_item(item_id)
    if item is None:
        return "Item not found."
    if item["stock"] == 0:                              # RULE: sold out
        return "Sorry, this dish is sold out."
    if qty < 1:
        return "Quantity must be at least 1."
    line = cart_qty_of(item_id)
    new_qty = qty + (line["qty"] if line else 0)
    if new_qty > MAX_QTY:                               # RULE: max per dish
        return f"Maximum {MAX_QTY} per dish per order."
    if new_qty > item["stock"]:                         # RULE: stock limit
        return f"Only {item['stock']} left in stock."
    if line:
        line["qty"] = new_qty
    else:
        cart.append({"id": item_id, "qty": qty})
    return None
 
 
def gui_change_qty(item_id, qty):
    item = find_item(item_id)
    line = cart_qty_of(item_id)
    if item is None or line is None:
        return "That item is not in your cart."
    if qty < 1 or qty > MAX_QTY:
        return f"Quantity must be between 1 and {MAX_QTY}."
    if qty > item["stock"]:
        return f"Only {item['stock']} left in stock."
    line["qty"] = qty
    return None
 
 
def gui_checkout(paid):
    """Return (error_message, receipt_text). One of them is None."""
    if len(cart) == 0:                                  # RULE: empty cart
        return "Cart is empty. Add dishes first.", None
    for line in cart:
        item = find_item(line["id"])
        if item is None or line["qty"] > item["stock"]:
            return "Stock changed. Please review your cart.", None
    subtotal = cart_subtotal()
    discount = calculate_discount(subtotal)
    total = subtotal - discount
    if paid < total:                                    # RULE: payment
        return f"Insufficient payment, short by {total - paid:.2f}.", None
    lines = []
    for line in cart:
        item = find_item(line["id"])
        item["stock"] -= line["qty"]
        sales_count[item["name"]] = sales_count.get(item["name"], 0) + line["qty"]
        lines.append({"name": item["name"], "qty": line["qty"],
                      "price": item["price"]})
    order_no = next_ids["order"]
    orders.append({"order_no": order_no, "lines": lines, "subtotal": subtotal,
                   "discount": discount, "total": total})
    next_ids["order"] += 1
    cart.clear()
    receipt = (f"Order #{order_no} complete!\n\nSubtotal: {subtotal:.2f}\n"
               f"Discount: -{discount:.2f}\nTotal: {total:.2f}\n"
               f"Paid: {paid:.2f}\nChange: {paid - total:.2f}\n\n"
               f"Thank you for dining at {RESTAURANT_NAME}!")
    return None, receipt
 
 
def validate_dish(name, price_text, stock_text, ignore_id=None):
    """Return (error, price, stock)."""
    if name == "":
        return "Dish name cannot be empty.", None, None
    if name_exists(name, ignore_id):                    # RULE: no duplicates
        return "A dish with this name already exists.", None, None
    try:
        price = float(price_text)
    except ValueError:
        return "Price must be a number.", None, None
    if price <= 0:
        return "Price must be greater than 0.", None, None
    try:
        stock = int(stock_text)
    except ValueError:
        return "Stock must be a whole number.", None, None
    if stock < 0:
        return "Stock cannot be negative.", None, None
    return None, price, stock
 
 
def summary_text():
    if len(orders) == 0:
        return "No orders yet."
    revenue = 0.0
    for order in orders:
        revenue += order["total"]
    best = max(sales_count, key=sales_count.get)
    text = (f"Orders: {len(orders)}\nRevenue: {revenue:.2f}\n"
            f"Average per order: {revenue / len(orders):.2f}\n"
            f"Best seller: {best} ({sales_count[best]} sold)\n\nRanking:\n")
    ranking = sorted(sales_count.items(), key=lambda p: p[1], reverse=True)
    for rank, (name, qty) in enumerate(ranking, 1):
        text += f"  {rank}. {name} - {qty}\n"
    return text
 
 
# ---------- user interface ----------
class JasmineApp:
    def __init__(self, root):
        self.root = root
        root.title(f"{RESTAURANT_NAME} Restaurant")
        root.geometry("980x560")
        tabs = ttk.Notebook(root)
        tabs.pack(fill="both", expand=True, padx=6, pady=6)
        self.order_tab = ttk.Frame(tabs)
        self.manage_tab = ttk.Frame(tabs)
        self.summary_tab = ttk.Frame(tabs)
        tabs.add(self.order_tab, text="Order")
        tabs.add(self.manage_tab, text="Manage Menu")
        tabs.add(self.summary_tab, text="Sales Summary")
        tabs.bind("<<NotebookTabChanged>>", lambda e: self.refresh_all())
        self.build_order_tab()
        self.build_manage_tab()
        self.build_summary_tab()
        self.refresh_all()
 
    # ----- order tab -----
    def build_order_tab(self):
        left = ttk.LabelFrame(self.order_tab, text="Menu")
        left.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        right = ttk.LabelFrame(self.order_tab, text="Your Cart")
        right.pack(side="right", fill="both", expand=True, padx=6, pady=6)
 
        bar = ttk.Frame(left)
        bar.pack(fill="x", padx=4, pady=4)
        self.cat_var = tk.StringVar(value="All")
        self.sort_var = tk.StringVar(value="ID")
        self.search_var = tk.StringVar()
        ttk.Combobox(bar, textvariable=self.cat_var, state="readonly", width=10,
                     values=["All"] + CATEGORIES).pack(side="left")
        ttk.Combobox(bar, textvariable=self.sort_var, state="readonly", width=14,
                     values=SORT_OPTIONS).pack(side="left", padx=4)
        ttk.Entry(bar, textvariable=self.search_var, width=14).pack(side="left")
        ttk.Button(bar, text="Search", command=self.refresh_menu).pack(side="left", padx=4)
        self.cat_var.trace_add("write", lambda *a: self.refresh_menu())
        self.sort_var.trace_add("write", lambda *a: self.refresh_menu())
 
        cols = ("id", "name", "category", "price", "stock")
        self.menu_tree = ttk.Treeview(left, columns=cols, show="headings", height=14)
        for col, width in zip(cols, (40, 150, 80, 70, 60)):
            self.menu_tree.heading(col, text=col.title())
            self.menu_tree.column(col, width=width, anchor="w")
        self.menu_tree.pack(fill="both", expand=True, padx=4)
 
        row = ttk.Frame(left)
        row.pack(fill="x", padx=4, pady=6)
        ttk.Label(row, text="Qty:").pack(side="left")
        self.qty_var = tk.StringVar(value="1")
        ttk.Spinbox(row, from_=1, to=MAX_QTY, width=5,
                    textvariable=self.qty_var).pack(side="left", padx=4)
        ttk.Button(row, text="Add to Cart", command=self.on_add).pack(side="left")
 
        ccols = ("id", "name", "qty", "total")
        self.cart_tree = ttk.Treeview(right, columns=ccols, show="headings", height=10)
        for col, width in zip(ccols, (40, 150, 50, 80)):
            self.cart_tree.heading(col, text=col.title())
            self.cart_tree.column(col, width=width, anchor="w")
        self.cart_tree.pack(fill="both", expand=True, padx=4, pady=4)
 
        btns = ttk.Frame(right)
        btns.pack(fill="x", padx=4)
        ttk.Button(btns, text="Change Qty", command=self.on_change_qty).pack(side="left")
        ttk.Button(btns, text="Remove", command=self.on_remove).pack(side="left", padx=4)
        ttk.Button(btns, text="Clear", command=self.on_clear).pack(side="left")
 
        self.totals_var = tk.StringVar()
        ttk.Label(right, textvariable=self.totals_var,
                  font=("TkDefaultFont", 11, "bold")).pack(anchor="w", padx=6, pady=8)
        pay = ttk.Frame(right)
        pay.pack(fill="x", padx=4, pady=4)
        ttk.Label(pay, text="Cash paid:").pack(side="left")
        self.paid_var = tk.StringVar()
        ttk.Entry(pay, textvariable=self.paid_var, width=10).pack(side="left", padx=4)
        ttk.Button(pay, text="Checkout", command=self.on_checkout).pack(side="left")
 
    def refresh_menu(self):
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)
        items = list(menu_items)
        if self.cat_var.get() != "All":
            items = [i for i in items if i["category"] == self.cat_var.get()]
        keyword = self.search_var.get().strip().lower()
        if keyword:
            items = [i for i in items if keyword in i["name"].lower()]
        sort = self.sort_var.get()
        if sort == "Name":
            items.sort(key=lambda i: i["name"].lower())
        elif sort == "Price low->high":
            items.sort(key=lambda i: i["price"])
        elif sort == "Price high->low":
            items.sort(key=lambda i: i["price"], reverse=True)
        for item in items:
            stock = "SOLD OUT" if item["stock"] == 0 else item["stock"]
            self.menu_tree.insert("", "end", iid=str(item["id"]), values=(
                item["id"], item["name"], item["category"],
                f"{item['price']:.2f}", stock))
 
    def refresh_cart(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        for line in cart:
            item = find_item(line["id"])
            self.cart_tree.insert("", "end", iid=str(line["id"]), values=(
                item["id"], item["name"], line["qty"],
                f"{item['price'] * line['qty']:.2f}"))
        subtotal = cart_subtotal()
        discount = calculate_discount(subtotal)
        hint = "" if discount > 0 else f"  (10% off at {DISCOUNT_THRESHOLD})"
        self.totals_var.set(f"Subtotal {subtotal:.2f} | Discount -{discount:.2f} | "
                            f"Total {subtotal - discount:.2f}{hint}")
 
    def selected_id(self, tree, what):
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Select", f"Please select {what} first.")
            return None
        return int(selection[0])
 
    def on_add(self):
        item_id = self.selected_id(self.menu_tree, "a dish from the menu")
        if item_id is None:
            return
        try:
            qty = int(self.qty_var.get())
        except ValueError:
            messagebox.showerror("Invalid", "Quantity must be a whole number.")
            return
        error = gui_add_to_cart(item_id, qty)
        if error:
            messagebox.showerror("Cannot add", error)
        self.refresh_all()
 
    def on_change_qty(self):
        item_id = self.selected_id(self.cart_tree, "an item in the cart")
        if item_id is None:
            return
        qty = simpledialog.askinteger("Change quantity", f"New quantity (1-{MAX_QTY}):",
                                      parent=self.root)
        if qty is None:
            return
        error = gui_change_qty(item_id, qty)
        if error:
            messagebox.showerror("Cannot change", error)
        self.refresh_all()
 
    def on_remove(self):
        item_id = self.selected_id(self.cart_tree, "an item in the cart")
        if item_id is None:
            return
        line = cart_qty_of(item_id)
        if line:
            cart.remove(line)
        self.refresh_all()
 
    def on_clear(self):
        cart.clear()
        self.refresh_all()
 
    def on_checkout(self):
        try:
            paid = float(self.paid_var.get())
        except ValueError:
            messagebox.showerror("Invalid", "Cash paid must be a number.")
            return
        if paid < 0:
            messagebox.showerror("Invalid", "Cash paid cannot be negative.")
            return
        error, receipt = gui_checkout(paid)
        if error:
            messagebox.showerror("Checkout failed", error)
            return
        self.paid_var.set("")
        messagebox.showinfo("Receipt", receipt)
        self.refresh_all()
 
    # ----- manage tab -----
    def build_manage_tab(self):
        form = ttk.LabelFrame(self.manage_tab, text="Dish details")
        form.pack(side="left", fill="y", padx=6, pady=6)
        self.name_var = tk.StringVar()
        self.cat_form_var = tk.StringVar(value=CATEGORIES[0])
        self.price_var = tk.StringVar()
        self.stock_var = tk.StringVar()
        fields = [("Name", ttk.Entry(form, textvariable=self.name_var, width=22)),
                  ("Category", ttk.Combobox(form, textvariable=self.cat_form_var,
                                            state="readonly", values=CATEGORIES, width=19)),
                  ("Price", ttk.Entry(form, textvariable=self.price_var, width=22)),
                  ("Stock", ttk.Entry(form, textvariable=self.stock_var, width=22))]
        for number, (label, widget) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=number, column=0, sticky="w", padx=6, pady=4)
            widget.grid(row=number, column=1, padx=6, pady=4)
        ttk.Button(form, text="Add Dish", command=self.on_add_dish).grid(
            row=4, column=0, columnspan=2, sticky="ew", padx=6, pady=(10, 2))
        ttk.Button(form, text="Update Selected", command=self.on_update_dish).grid(
            row=5, column=0, columnspan=2, sticky="ew", padx=6, pady=2)
        ttk.Button(form, text="Remove Selected", command=self.on_remove_dish).grid(
            row=6, column=0, columnspan=2, sticky="ew", padx=6, pady=2)
 
        cols = ("id", "name", "category", "price", "stock")
        self.manage_tree = ttk.Treeview(self.manage_tab, columns=cols,
                                        show="headings", height=16)
        for col, width in zip(cols, (40, 170, 90, 70, 60)):
            self.manage_tree.heading(col, text=col.title())
            self.manage_tree.column(col, width=width, anchor="w")
        self.manage_tree.pack(side="right", fill="both", expand=True, padx=6, pady=6)
        self.manage_tree.bind("<<TreeviewSelect>>", self.on_select_dish)
 
    def refresh_manage(self):
        for row in self.manage_tree.get_children():
            self.manage_tree.delete(row)
        for item in menu_items:
            self.manage_tree.insert("", "end", iid=str(item["id"]), values=(
                item["id"], item["name"], item["category"],
                f"{item['price']:.2f}", item["stock"]))
 
    def on_select_dish(self, event):
        selection = self.manage_tree.selection()
        if not selection:
            return
        item = find_item(int(selection[0]))
        if item is None:
            return
        self.name_var.set(item["name"])
        self.cat_form_var.set(item["category"])
        self.price_var.set(str(item["price"]))
        self.stock_var.set(str(item["stock"]))
 
    def on_add_dish(self):
        name = self.name_var.get().strip()
        error, price, stock = validate_dish(name, self.price_var.get(), self.stock_var.get())
        if error:
            messagebox.showerror("Cannot add", error)
            return
        menu_items.append({"id": next_ids["item"], "name": name,
                           "category": self.cat_form_var.get(),
                           "price": price, "stock": stock})
        next_ids["item"] += 1
        self.refresh_all()
 
    def on_update_dish(self):
        item_id = self.selected_id(self.manage_tree, "a dish")
        if item_id is None:
            return
        name = self.name_var.get().strip()
        error, price, stock = validate_dish(name, self.price_var.get(),
                                            self.stock_var.get(), item_id)
        if error:
            messagebox.showerror("Cannot update", error)
            return
        item = find_item(item_id)
        item["name"], item["category"] = name, self.cat_form_var.get()
        item["price"], item["stock"] = price, stock
        self.refresh_all()
 
    def on_remove_dish(self):
        item_id = self.selected_id(self.manage_tree, "a dish")
        if item_id is None:
            return
        item = find_item(item_id)
        if messagebox.askyesno("Remove", f"Remove '{item['name']}'?"):
            menu_items.remove(item)
            cart[:] = [line for line in cart if line["id"] != item_id]
            self.refresh_all()
 
    # ----- summary tab -----
    def build_summary_tab(self):
        self.summary_var = tk.StringVar()
        ttk.Label(self.summary_tab, textvariable=self.summary_var,
                  justify="left", font=("TkFixedFont", 12)).pack(anchor="nw", padx=16, pady=16)
 
    def refresh_all(self):
        self.refresh_menu()
        self.refresh_cart()
        self.refresh_manage()
        self.summary_var.set(summary_text())
 
 
def main():
    root = tk.Tk()
    JasmineApp(root)
    root.mainloop()
 
 
if __name__ == "__main__":
    main()
 
