# Jasmine Restaurant

A terminal food-ordering app written in Python (standard library only).

## Purpose
Customers browse the menu, add dishes to a cart, edit the cart and check out.

## Features
1. See menu: all items, by category, or lowest price to highest
2. Add to cart: choose a dish by id and a quantity
3. View/Edit cart: change a quantity, remove a dish, or clear the cart
4. Check out: shows the final price, updates stock, empties the cart
5. Exit

## Data structures
- `menu_items`: a list of dictionaries (one per dish)
- `cart`: a list of dictionaries (`id` and `qty`)

## Business rules
- The dish id must exist
- Sold-out dishes cannot be ordered
- Maximum 10 of one dish per order
- Quantity cannot be more than the stock
- A 10% discount applies when the subtotal is 500 or more
- Checkout is refused when the cart is empty

## Data processing
- Filtering the menu by category
- Sorting the menu by price
- Calculating the cart subtotal and discount

## Files
- `main.py`: main menu loop
- `menu.py`: input helper, menu viewing, adding to the cart
- `cart.py`: view/edit cart and checkout
- `data.py`: shared data and settings
