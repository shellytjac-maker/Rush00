"""main.py - entry point for the Jasmine restaurant app."""
from menu import view_menu, add_to_cart, read_int
from cart import view_edit_cart, checkout


def print_main_menu():
    print("\n===== JASMINE RESTAURANT =====")
    print("1. See menu")
    print("2. Add to cart")
    print("3. View/Edit cart")
    print("4. Check out")
    print("5. Exit")


def main():
    while True:
        print_main_menu()
        choice = read_int("Choose: ", 1, 5)
        if choice is None:
            continue

        if choice == 1:
            view_menu()
        elif choice == 2:
            add_to_cart()
        elif choice == 3:
            view_edit_cart()
        elif choice == 4:
            checkout()
        else:
            print("Goodbye! See you at Jasmine!")
            break


main()
