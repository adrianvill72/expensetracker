from login_accountCreation import loginMenu
from functions import *
import sqlite3

def create_expenses_table():
    # Connect to the SQLite database
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Create the expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            price REAL,
            isSharedExpense BOOLEAN,
            date TEXT,
            description TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        );
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()



def main():
    current_userID,usersFirstName=loginMenu()
    create_expenses_table()
    conn = conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    monthExpenses=monthToDateExpenses(current_userID,conn)
    while True:
        print(f"\nWelcome {usersFirstName},")
        print("\nExpense Tracking System:")
        if(monthExpenses!=None):
            print(f"This month you have spent a total of: ${monthExpenses} ")
        print("1. Record an Expense")
        print("2. List Expenses")
        print("3. Edit Expense")
        print("4. Summarize Expenses")
        print("5. Shared Expense Tracking")
        print("6. Create a Budget")
        print("7. Exit")

        try:
            choice = int(input("Enter your choice (1-7): "))
            if choice == 1:
                quick_record_expense(current_userID,conn)
            elif choice == 2:
                print("\nExpense Viewer: ")
                print("\n 1.) List all Expenses.")
                print("\n 2.) View this months expenses.")
                print("\n 3.) View Expense by Category.")

                choice2=(input("\nMake a selection:"))

                match choice2:
                    case "1":
                        list_all_expenses(current_userID,conn)
                        
                    case "2":
                        return 
                    case "3":
                        filter_by_category(current_userID,conn)
                        
            elif choice == 3:
                edit_expense()
            elif choice == 4:
                summarize_expenses()
            elif choice == 5:
                shared_expense_tracking()
            elif choice == 6:
                create_budget()  # New option to create a budget
            elif choice == 7:
                print("Exiting the Expense Tracking System. Goodbye!")
                break
            else:
                print("Invalid choice. Please select a valid option (1-7).")
        except ValueError:
            print("Invalid input. Please enter a valid number for your choice.")

    
if __name__ == "__main__":
    main()
