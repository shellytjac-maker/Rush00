"""main.py - entry point for the Jasmine restaurant ordering app."""
from data import RESTAURANT_NAME, orders, sales_count
from menu import view_menu, manage_menu, read_int
from cart import add_to_cart, edit_cart, checkout, show_cart
 
 
def sales_summary():
    """Total revenue, average order, best seller, and ranking."""
    if len(orders) == 0:
        print("  No orders yet.")
        return
    revenue = 0.0
    for order in orders:
        revenue += order["total"]
    average = revenue / len(orders)
    best = max(sales_count, key=sales_count.get)
    print(f"  Orders: {len(orders)}")
    print(f"  Revenue: {revenue:.2f}")
    print(f"  Average per order: {average:.2f}")
    print(f"  Best seller: {best} ({sales_count[best]} sold)")
    print("  Ranking:")
    ranking = sorted(sales_count.items(), key=lambda pair: pair[1], reverse=True)
    for rank, (name, qty) in enumerate(ranking, 1):
        print(f"   {rank}. {name} - {qty}")
 
 
def print_main_menu():
    title = f" {RESTAURANT_NAME.upper()} RESTAURANT "
    print("\n" + title.center(34, "="))
    print("1. View Menu")
    print("2. Add Dish to Cart")
    print("3. View / Edit Cart")
    print("4. Checkout")
    print("5. Manage Menu (add/update/remove)")
    print("6. Sales Summary")
    print("7. Exit")
 
 
def main():
    running = True
    while running:
        print_main_menu()
        try:
            choice = read_int("Choose: ", 1, 7)
            if choice is None:
                continue
            if choice == 1:
                view_menu()
            elif choice == 2:
                add_to_cart()
            elif choice == 3:
                edit_cart()
            elif choice == 4:
                checkout()
            elif choice == 5:
                manage_menu()
            elif choice == 6:
                sales_summary()
            else:
                print("Goodbye! See you at Jasmine!")
                running = False
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            running = False
 
 
if __name__ == "__main__":
    main()
 
