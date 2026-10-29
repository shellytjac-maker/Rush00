"""gui.py - optional graphical interface (tkinter) for the Jasmine restaurant.
 
Run with:  python3 gui.py
The terminal version (python3 main.py) still works independently.
It re-uses the same data (data.py) and logic (menu.py, cart.py).
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkfont
 
from data import (RESTAURANT_NAME, CATEGORIES, MAX_QTY, DISCOUNT_THRESHOLD,
                  DISCOUNT_RATE,
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
 
 
def summary_stats():
    """Data processing for the summary: totals, average, best seller, ranking."""
    revenue = 0.0
    for order in orders:
        revenue += order["total"]
    count = len(orders)
    average = revenue / count if count else 0.0
    ranking = sorted(sales_count.items(), key=lambda p: p[1], reverse=True)
    best = ranking[0] if ranking else ("-", 0)
    return {"orders": count, "revenue": revenue, "average": average,
            "best": best, "ranking": ranking}
 
 
# ---------- look & feel ----------
BG = "#F7F3EA"        # warm cream background
CARD = "#FFFFFF"
BORDER = "#E3DCCB"
GREEN = "#2F7D5B"
DARK = "#1E4D3A"
GOLD = "#F2C14E"
TEXT = "#2B2B2B"
MUTED = "#7A7A72"
ROW_ALT = "#F1F7F3"
SOFT = "#DDEBE3"
RED = "#C0392B"
RED_DARK = "#962D22"
 
 
def setup_style(root):
    """Configure colours, fonts and widget styles. Returns the font family."""
    root.configure(bg=BG)
    base = tkfont.nametofont("TkDefaultFont")
    base.configure(size=11)
    family = base.actual("family")
    for name in ("TkTextFont", "TkMenuFont", "TkHeadingFont"):
        try:
            tkfont.nametofont(name).configure(size=11)
        except tk.TclError:
            pass
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=BG, foreground=TEXT, font=(family, 11))
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD)
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Card.TLabel", background=CARD)
    style.configure("CardHeader.TLabel", background=CARD, foreground=DARK,
                    font=(family, 13, "bold"))
    style.configure("CardTitle.TLabel", background=CARD, foreground=MUTED,
                    font=(family, 9, "bold"))
    style.configure("Stat.TLabel", background=CARD, foreground=DARK,
                    font=(family, 16, "bold"))
    style.configure("Total.TLabel", background=CARD, foreground=GREEN,
                    font=(family, 17, "bold"))
    style.configure("Hint.TLabel", background=CARD, foreground=MUTED,
                    font=(family, 9))
    style.configure("Status.TLabel", background=BG, foreground=MUTED)
 
    style.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(8, 8, 8, 0))
    style.configure("TNotebook.Tab", padding=(20, 9), background=SOFT,
                    foreground=DARK, font=(family, 11, "bold"), borderwidth=0)
    style.map("TNotebook.Tab", background=[("selected", GREEN)],
              foreground=[("selected", "white")])
 
    style.configure("Treeview", background="white", fieldbackground="white",
                    foreground=TEXT, rowheight=30, borderwidth=0, font=(family, 11))
    style.configure("Treeview.Heading", background=GREEN, foreground="white",
                    font=(family, 11, "bold"), relief="flat", padding=(6, 7))
    style.map("Treeview.Heading", background=[("active", DARK)])
    style.map("Treeview", background=[("selected", GOLD)],
              foreground=[("selected", TEXT)])
 
    for name, color, hover in (("Primary", GREEN, DARK),
                               ("Danger", RED, RED_DARK),
                               ("Soft", SOFT, "#C9DFD2")):
        text_color = DARK if name == "Soft" else "white"
        style.configure(f"{name}.TButton", background=color, foreground=text_color,
                        font=(family, 11, "bold"), padding=(14, 8), borderwidth=0,
                        focusthickness=0)
        style.map(f"{name}.TButton", background=[("pressed", hover), ("active", hover)],
                  foreground=[("active", text_color)])
    style.configure("TEntry", fieldbackground="white", padding=6)
    style.configure("TCombobox", fieldbackground="white", padding=5)
    style.configure("TSpinbox", fieldbackground="white", padding=5)
    style.configure("Vertical.TScrollbar", background=SOFT, troughcolor=BG,
                    borderwidth=0, arrowsize=14)
    return family
 
 
def make_card(parent, title):
    """A white rounded-looking panel with a title."""
    card = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    ttk.Label(card, text=title, style="CardHeader.TLabel").pack(
        anchor="w", padx=14, pady=(12, 6))
    return card
 
 
def make_tree(parent, columns, height):
    """columns: list of (key, heading, width, anchor). Returns (frame, tree)."""
    frame = ttk.Frame(parent, style="Card.TFrame")
    tree = ttk.Treeview(frame, columns=[c[0] for c in columns], show="headings",
                        height=height, selectmode="browse")
    for key, title, width, anchor in columns:
        tree.heading(key, text=title)
        tree.column(key, width=width, anchor=anchor, stretch=(key == "name"))
    bar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=bar.set)
    tree.pack(side="left", fill="both", expand=True)
    bar.pack(side="right", fill="y")
    tree.tag_configure("odd", background=ROW_ALT)
    tree.tag_configure("even", background="white")
    tree.tag_configure("soldout", foreground=MUTED)
    return frame, tree
 
 
def clear_tree(tree):
    for row in tree.get_children():
        tree.delete(row)
 
 
def stripe(index):
    return "odd" if index % 2 else "even"
 
 
# ---------- user interface ----------
class JasmineApp:
    def __init__(self, root):
        self.root = root
        root.title(f"{RESTAURANT_NAME} Restaurant")
        root.geometry("1100x700")
        root.minsize(980, 620)
        self.family = setup_style(root)
        self.build_header()
 
        bottom = ttk.Frame(root)
        bottom.pack(side="bottom", fill="x", padx=12, pady=(0, 10))
        self.status_var = tk.StringVar(value="Welcome! Select a dish to start an order.")
        ttk.Label(bottom, textvariable=self.status_var,
                  style="Status.TLabel").pack(side="left")
        ttk.Button(bottom, text="Exit", style="Danger.TButton",
                   command=self.on_exit).pack(side="right")
 
        tabs = ttk.Notebook(root)
        tabs.pack(fill="both", expand=True, padx=8, pady=4)
        self.order_tab = ttk.Frame(tabs)
        self.manage_tab = ttk.Frame(tabs)
        self.summary_tab = ttk.Frame(tabs)
        tabs.add(self.order_tab, text="  Order  ")
        tabs.add(self.manage_tab, text="  Manage Menu  ")
        tabs.add(self.summary_tab, text="  Sales Summary  ")
        tabs.bind("<<NotebookTabChanged>>", lambda e: self.refresh_all())
        self.build_order_tab()
        self.build_manage_tab()
        self.build_summary_tab()
        self.refresh_all()
 
    def build_header(self):
        header = tk.Frame(self.root, bg=DARK)
        header.pack(fill="x")
        tk.Label(header, text=RESTAURANT_NAME.upper(), bg=DARK, fg=GOLD,
                 font=(self.family, 24, "bold")).pack(side="left", padx=(22, 10), pady=14)
        tk.Label(header, text="Thai Restaurant  |  Order System", bg=DARK,
                 fg="#CFE5D8", font=(self.family, 12)).pack(side="left", pady=14)
        tk.Frame(self.root, bg=GOLD, height=3).pack(fill="x")
 
    def set_status(self, text):
        self.status_var.set(text)
 
    # ----- order tab -----
    def build_order_tab(self):
        self.order_tab.columnconfigure(0, weight=3)
        self.order_tab.columnconfigure(1, weight=2)
        self.order_tab.rowconfigure(0, weight=1)
 
        left = make_card(self.order_tab, "Menu")
        left.grid(row=0, column=0, sticky="nsew", padx=(8, 6), pady=8)
        right = make_card(self.order_tab, "Your Cart")
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 8), pady=8)
 
        bar = ttk.Frame(left, style="Card.TFrame")
        bar.pack(fill="x", padx=14, pady=(0, 8))
        self.cat_var = tk.StringVar(value="All")
        self.sort_var = tk.StringVar(value="ID")
        self.search_var = tk.StringVar()
        ttk.Combobox(bar, textvariable=self.cat_var, state="readonly", width=10,
                     values=["All"] + CATEGORIES).pack(side="left")
        ttk.Combobox(bar, textvariable=self.sort_var, state="readonly", width=14,
                     values=SORT_OPTIONS).pack(side="left", padx=6)
        search = ttk.Entry(bar, textvariable=self.search_var, width=14)
        search.pack(side="left")
        search.bind("<Return>", lambda e: self.refresh_menu())
        ttk.Button(bar, text="Search", style="Soft.TButton",
                   command=self.refresh_menu).pack(side="left", padx=6)
        self.cat_var.trace_add("write", lambda *a: self.refresh_menu())
        self.sort_var.trace_add("write", lambda *a: self.refresh_menu())
 
        frame, self.menu_tree = make_tree(left, [
            ("id", "ID", 45, "center"), ("name", "Dish", 170, "w"),
            ("category", "Category", 90, "w"), ("price", "Price", 75, "e"),
            ("stock", "Stock", 75, "center")], 14)
        frame.pack(fill="both", expand=True, padx=14)
        self.menu_tree.bind("<Double-1>", lambda e: self.on_add())
 
        row = ttk.Frame(left, style="Card.TFrame")
        row.pack(fill="x", padx=14, pady=12)
        ttk.Label(row, text="Quantity", style="Card.TLabel").pack(side="left")
        self.qty_var = tk.StringVar(value="1")
        ttk.Spinbox(row, from_=1, to=MAX_QTY, width=5,
                    textvariable=self.qty_var).pack(side="left", padx=8)
        ttk.Button(row, text="Add to Cart", style="Primary.TButton",
                   command=self.on_add).pack(side="left")
 
        frame, self.cart_tree = make_tree(right, [
            ("id", "ID", 40, "center"), ("name", "Dish", 140, "w"),
            ("qty", "Qty", 45, "center"), ("total", "Total", 80, "e")], 8)
        frame.pack(fill="both", expand=True, padx=14)
 
        btns = ttk.Frame(right, style="Card.TFrame")
        btns.pack(fill="x", padx=14, pady=(10, 0))
        ttk.Button(btns, text="Change Qty", style="Soft.TButton",
                   command=self.on_change_qty).pack(side="left")
        ttk.Button(btns, text="Remove", style="Soft.TButton",
                   command=self.on_remove).pack(side="left", padx=6)
        ttk.Button(btns, text="Clear", style="Soft.TButton",
                   command=self.on_clear).pack(side="left")
 
        totals = ttk.Frame(right, style="Card.TFrame")
        totals.pack(fill="x", padx=14, pady=(14, 0))
        totals.columnconfigure(1, weight=1)
        self.sub_var = tk.StringVar()
        self.disc_var = tk.StringVar()
        self.total_var = tk.StringVar()
        self.hint_var = tk.StringVar()
        ttk.Label(totals, text="Subtotal", style="Card.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(totals, textvariable=self.sub_var, style="Card.TLabel").grid(row=0, column=1, sticky="e")
        ttk.Label(totals, text="Discount", style="Card.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Label(totals, textvariable=self.disc_var, style="Card.TLabel").grid(row=1, column=1, sticky="e")
        ttk.Label(totals, text="Total", style="Total.TLabel").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Label(totals, textvariable=self.total_var, style="Total.TLabel").grid(row=2, column=1, sticky="e", pady=(6, 0))
        ttk.Label(totals, textvariable=self.hint_var, style="Hint.TLabel").grid(
            row=3, column=0, columnspan=2, sticky="w")
 
        pay = ttk.Frame(right, style="Card.TFrame")
        pay.pack(fill="x", padx=14, pady=(10, 14))
        ttk.Label(pay, text="Cash paid", style="Card.TLabel").pack(side="left")
        self.paid_var = tk.StringVar()
        entry = ttk.Entry(pay, textvariable=self.paid_var, width=10)
        entry.pack(side="left", padx=8)
        entry.bind("<Return>", lambda e: self.on_checkout())
        ttk.Button(pay, text="Checkout", style="Primary.TButton",
                   command=self.on_checkout).pack(side="left")
 
    def refresh_menu(self):
        clear_tree(self.menu_tree)
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
        for index, item in enumerate(items):
            sold_out = item["stock"] == 0
            stock = "SOLD OUT" if sold_out else item["stock"]
            tags = (stripe(index), "soldout") if sold_out else (stripe(index),)
            self.menu_tree.insert("", "end", iid=str(item["id"]), tags=tags, values=(
                item["id"], item["name"], item["category"],
                f"{item['price']:.2f}", stock))
 
    def refresh_cart(self):
        clear_tree(self.cart_tree)
        for index, line in enumerate(cart):
            item = find_item(line["id"])
            self.cart_tree.insert("", "end", iid=str(line["id"]), tags=(stripe(index),),
                                  values=(item["id"], item["name"], line["qty"],
                                          f"{item['price'] * line['qty']:.2f}"))
        subtotal = cart_subtotal()
        discount = calculate_discount(subtotal)
        self.sub_var.set(f"{subtotal:.2f}")
        self.disc_var.set(f"-{discount:.2f}")
        self.total_var.set(f"{subtotal - discount:.2f}")
        percent = int(DISCOUNT_RATE * 100)
        if discount > 0:
            self.hint_var.set(f"{percent}% discount applied!")
        else:
            self.hint_var.set(f"Spend {DISCOUNT_THRESHOLD}+ to get {percent}% off")
 
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
        else:
            self.set_status(f"Added {qty} x {find_item(item_id)['name']} to cart.")
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
        else:
            self.set_status("Quantity updated.")
        self.refresh_all()
 
    def on_remove(self):
        item_id = self.selected_id(self.cart_tree, "an item in the cart")
        if item_id is None:
            return
        line = cart_qty_of(item_id)
        if line:
            cart.remove(line)
            self.set_status("Item removed from cart.")
        self.refresh_all()
 
    def on_clear(self):
        cart.clear()
        self.set_status("Cart cleared.")
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
        self.set_status("Order completed. Thank you!")
        messagebox.showinfo("Receipt", receipt)
        self.refresh_all()
 
    def on_exit(self):
        if messagebox.askyesno("Exit", "Exit the program? Unsaved data will be lost."):
            self.root.destroy()
 
    # ----- manage tab -----
    def build_manage_tab(self):
        self.manage_tab.columnconfigure(1, weight=1)
        self.manage_tab.rowconfigure(0, weight=1)
        form = make_card(self.manage_tab, "Dish details")
        form.grid(row=0, column=0, sticky="ns", padx=(8, 6), pady=8)
        right = make_card(self.manage_tab, "All dishes (click a row to edit)")
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 8), pady=8)
 
        self.name_var = tk.StringVar()
        self.cat_form_var = tk.StringVar(value=CATEGORIES[0])
        self.price_var = tk.StringVar()
        self.stock_var = tk.StringVar()
        body = ttk.Frame(form, style="Card.TFrame")
        body.pack(fill="x", padx=14, pady=(0, 14))
        fields = [("Name", ttk.Entry(body, textvariable=self.name_var, width=24)),
                  ("Category", ttk.Combobox(body, textvariable=self.cat_form_var,
                                            state="readonly", values=CATEGORIES, width=21)),
                  ("Price", ttk.Entry(body, textvariable=self.price_var, width=24)),
                  ("Stock", ttk.Entry(body, textvariable=self.stock_var, width=24))]
        for number, (label, widget) in enumerate(fields):
            ttk.Label(body, text=label, style="Card.TLabel").grid(
                row=number * 2, column=0, sticky="w", pady=(8, 0))
            widget.grid(row=number * 2 + 1, column=0, sticky="ew")
        ttk.Button(body, text="Add Dish", style="Primary.TButton",
                   command=self.on_add_dish).grid(row=8, column=0, sticky="ew", pady=(18, 4))
        ttk.Button(body, text="Update Selected", style="Soft.TButton",
                   command=self.on_update_dish).grid(row=9, column=0, sticky="ew", pady=4)
        ttk.Button(body, text="Remove Selected", style="Danger.TButton",
                   command=self.on_remove_dish).grid(row=10, column=0, sticky="ew", pady=4)
        ttk.Button(body, text="Clear Form", style="Soft.TButton",
                   command=self.on_clear_form).grid(row=11, column=0, sticky="ew", pady=4)
 
        frame, self.manage_tree = make_tree(right, [
            ("id", "ID", 45, "center"), ("name", "Dish", 190, "w"),
            ("category", "Category", 95, "w"), ("price", "Price", 80, "e"),
            ("stock", "Stock", 70, "center")], 16)
        frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.manage_tree.bind("<<TreeviewSelect>>", self.on_select_dish)
 
    def refresh_manage(self):
        clear_tree(self.manage_tree)
        for index, item in enumerate(menu_items):
            self.manage_tree.insert("", "end", iid=str(item["id"]), tags=(stripe(index),),
                                    values=(item["id"], item["name"], item["category"],
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
 
    def on_clear_form(self):
        self.manage_tree.selection_remove(*self.manage_tree.selection())
        self.name_var.set("")
        self.cat_form_var.set(CATEGORIES[0])
        self.price_var.set("")
        self.stock_var.set("")
 
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
        self.set_status(f"Added dish '{name}'.")
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
        self.set_status(f"Updated dish '{name}'.")
        self.refresh_all()
 
    def on_remove_dish(self):
        item_id = self.selected_id(self.manage_tree, "a dish")
        if item_id is None:
            return
        item = find_item(item_id)
        if messagebox.askyesno("Remove", f"Remove '{item['name']}'?"):
            menu_items.remove(item)
            cart[:] = [line for line in cart if line["id"] != item_id]
            self.on_clear_form()
            self.set_status(f"Removed dish '{item['name']}'.")
            self.refresh_all()
 
    # ----- summary tab -----
    def build_summary_tab(self):
        cards = ttk.Frame(self.summary_tab)
        cards.pack(fill="x", padx=8, pady=(12, 4))
        self.stat_vars = {}
        stats = [("orders", "Orders"), ("revenue", "Revenue"),
                 ("average", "Average / order"), ("best", "Best seller")]
        for number, (key, title) in enumerate(stats):
            card = tk.Frame(cards, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=0, column=number, sticky="nsew", padx=6)
            cards.columnconfigure(number, weight=1, uniform="stat")
            ttk.Label(card, text=title.upper(), style="CardTitle.TLabel").pack(
                anchor="w", padx=14, pady=(12, 0))
            var = tk.StringVar()
            self.stat_vars[key] = var
            ttk.Label(card, textvariable=var, style="Stat.TLabel",
                      wraplength=190).pack(anchor="w", padx=14, pady=(2, 12))
 
        rank_card = make_card(self.summary_tab, "Sales ranking")
        rank_card.pack(fill="both", expand=True, padx=14, pady=8)
        frame, self.rank_tree = make_tree(rank_card, [
            ("rank", "Rank", 60, "center"), ("name", "Dish", 260, "w"),
            ("sold", "Sold", 90, "center")], 8)
        frame.pack(fill="both", expand=True, padx=14)
        bottom = ttk.Frame(rank_card, style="Card.TFrame")
        bottom.pack(fill="x", padx=14, pady=12)
        self.empty_var = tk.StringVar()
        ttk.Label(bottom, textvariable=self.empty_var, style="Hint.TLabel").pack(side="left")
        ttk.Button(bottom, text="Reset Sales History", style="Soft.TButton",
                   command=self.on_reset_sales).pack(side="right")
 
    def refresh_summary(self):
        stats = summary_stats()
        self.stat_vars["orders"].set(str(stats["orders"]))
        self.stat_vars["revenue"].set(f"{stats['revenue']:.2f}")
        self.stat_vars["average"].set(f"{stats['average']:.2f}")
        name, qty = stats["best"]
        self.stat_vars["best"].set("-" if qty == 0 else f"{name} ({qty})")
        clear_tree(self.rank_tree)
        for rank, (dish, sold) in enumerate(stats["ranking"], 1):
            self.rank_tree.insert("", "end", tags=(stripe(rank),),
                                  values=(rank, dish, sold))
        self.empty_var.set("" if stats["orders"] else
                           "No orders yet. Complete an order to see statistics.")
 
    def on_reset_sales(self):
        if len(orders) == 0:
            messagebox.showinfo("Reset", "There is no sales history to reset.")
            return
        if messagebox.askyesno("Reset", "Clear all orders and sales statistics?\n"
                                        "(Menu and stock are not changed.)"):
            orders.clear()
            sales_count.clear()
            next_ids["order"] = 1
            self.set_status("Sales history cleared.")
            self.refresh_all()
 
    def refresh_all(self):
        self.refresh_menu()
        self.refresh_cart()
        self.refresh_manage()
        self.refresh_summary()
 
 
def main():
    root = tk.Tk()
    JasmineApp(root)
    root.mainloop()
 
 
if __name__ == "__main__":
    main()
 
