Jasmine Restaurant

A terminal restaurant ordering app (Python, standard library only).

Purpose

Customers browse the menu, build a cart and pay; staff manage dishes and see sales.

Features
Browse menu: sort by price, filter by category, search by name, cheapest/priciest
Cart: add, change quantity, remove, clear
Checkout with discount, payment check, stock update
Manage menu: add / update / remove dishes
Sales summary: revenue, average order, best seller, ranking
Business rules
Sold-out dishes / quantity above stock are rejected
Max 10 per dish per order; duplicate dish names rejected
10% discount when subtotal >= 500; empty cart and insufficient payment rejected
Run
python3 main.py

Files: main.py (menu loop, summary), menu.py (menu data + input helpers), cart.py (cart + checkout), data.py (shared lists/dicts/settings).
