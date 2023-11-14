from datetime import *

categories = ["Food", "Bills", "Rent", "Entertainment", "Others"]
expenses = {category: [] for category in categories}
descriptions = []
groups = {}
shared_expenses = {}
payments = {}  # Dictionary to store payments between group members
budgets = {}  # Dictionary to store budgets for expense categories

def quick_record_expense(user_id,conn): #records expense quickly with todays date as current date, DOES NOT SUPPORT GROUP EXPENSE FUNCTIONING
    # Record an expense with a description
    print("\nExpense Categories:")
    today = datetime.today()
    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category}")

    try:
        choice = int(input("Select a category (1-5): "))
        if choice < 1 or choice > 5:
            print("Invalid choice. Please select a valid category.")
            return

        category = categories[choice - 1]
        amount = float(input("Enter the expense amount: "))
        description = input("Enter a description for the expense: ")

        # Get date
        current_date = datetime.today()

        # Add the expense and description to the chosen category
        expenses[category].append((current_date, amount, description))
        descriptions.append((current_date, description))
        print(f"Expense of ${amount} recorded for {category} on {current_date} with description: {description}")

        script = """INSERT INTO expenses(user_id, category, price, isSharedExpense, description, date) 
                    VALUES (?, ?, ?, ?, ?, ?);
                 """

        conn.execute(script, (user_id, category, amount, 0, description,current_date))
        conn.commit()

    except ValueError:
        print("Invalid input. Please enter a valid number for the category and a valid expense amount.")
def list_all_expenses(user_id, conn): #list all expenses for specific userID FUNCTIONING
    # Create a cursor object using the cursor() method
    cursor = conn.cursor()
    
    # Prepare SQL query to select all records from the expenses table
    try:
        # Executing the SQL command
        cursor.execute("SELECT date, category, price, description,id FROM expenses WHERE user_id = ?", (user_id,))

        # Fetch all rows from the database
        expenses = cursor.fetchall()

        # Check if there are any expenses
        if expenses:
            print("\nAll Expenses:")
            for expense in expenses:
                date, category, price, description, id = expense
                print(f"Expense ID: {id} Date: {date}, Category: {category}, Amount: ${price:.2f}, Description: {description},")
        else:
            print("No expenses found for this user.")

    except Exception as e:
        # Print any error messages to stdout
        print("There was an error fetching the expenses:", e)
    finally:
        # Ensure that the cursor object is closed after operation
        cursor.close()
def filter_by_category(user_id,conn):# lists all expenses for category type FUNCTIONING
    cursor = conn.cursor()
    categories = ["Food", "Bills", "Rent", "Entertainment", "Others"]

    print("\nFilter Expenses by Category:")
    for i, category in enumerate(categories, start=1):
        print(f"{i}. {category}")

    try:
        choice = int(input("Select a category (1-5): "))

        if choice < 1 or choice > 5:
            print("Invalid choice. Please select a valid category.")
            return

        category = categories[choice - 1]
        # Executing the SQL command
        cursor.execute("SELECT date, category, price, description, id FROM expenses WHERE user_id = ? AND category = ?", (user_id, category))

        # Fetch all rows from the database
        expenses = cursor.fetchall()

        if expenses:
            print(f"\nAll Expenses of Category: {category}")
            for expense in expenses:
                date, category, price, description, id = expense
                print(f"Expense ID: {id} Date: {date}, Category: {category}, Amount: ${price:.2f}, Description: {description},")
        else:
            print("No expenses found for this user.")

    except Exception as e:
        # Print any error messages to stdout
        print("There was an error fetching the expenses:", e)
    finally:
        # Ensure that the cursor object is closed after operation
        cursor.close()
def monthToDateExpenses(user_id,conn):#calculates total expenses for month, RETURNS total as INT, FUNCTIONING
    cursor = conn.cursor()
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    # Format the dates in the correct string format for SQL
    first_day_str = first_day_this_month.strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    
    query = """
        SELECT SUM(price) FROM expenses
        WHERE user_id = ? AND date >= ? AND date <= ?
    """
    cursor.execute(query, (user_id, first_day_str, today_str))
    
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else 0
def filter_by_month(user_id,conn):
    # Filter expenses by date range
    try:
        cursor=conn.cursor()
        start_date_str = input("Enter month and year to look up expenses: YYYY-MM\n")
        year, month = map(int, start_date_str.split('-'))
        datepattern=f"{start_date_str}%"
        cursor.execute("SELECT date, category, price, description, id FROM expenses WHERE user_id = ? AND date LIKE ?", (user_id,datepattern))
        expenses=cursor.fetchall()
        total_amount = 0

        if expenses:
            month_name = datetime(year, month, 1).strftime("%B")
            print(f"Expenses for the month of {month_name}, {year}:")
            for expense in expenses:
                date, category, price, description, id = expense
                print(f"Expense ID: {id} Date: {date}, Category: {category}, Amount: ${price:.2f}, Description: {description},")
                total_amount+=price
            print(f"Total amount spent for the month: ${total_amount}")
        else:
            print("No expenses found for the specified month.")

        cursor.close()
       
    except ValueError:
        print("Invalid date format. Please use the YYYY-MM format for dates.")
def add_split_expense(user_id, conn):
    try:
        total_amount = float(input("Enter the total amount of the expense: "))
        num_people = int(input("Enter the number of people to split the expense with: "))

        split_details = {}
        for i in range(num_people):
            person_name = input(f"Enter the name for person {i+1}: ")
            amount = float(input(f"Enter the amount person {i+1} owes: "))
            split_details[person_name] = amount

        # Add the main expense
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (user_id, price, isSharedExpense) VALUES (?, ?, ?)", (user_id, total_amount, 1))
        expense_id = cursor.lastrowid  # Get the ID of the newly added expense

        # Add split details
        for person_name, amount in split_details.items():
            cursor.execute("INSERT INTO split_expenses (expense_id, owed_by_person, amount, is_paid) VALUES (?, ?, ?, ?)", (expense_id, person_name, amount, 0))

        conn.commit()
        print("Split expense added successfully.")

    except ValueError:
        print("Invalid input. Please enter valid numeric values.")

def display_split_expenses(conn, expense_id):
    cursor = conn.cursor()
    cursor.execute("SELECT owed_by_person, amount, is_paid FROM split_expenses WHERE expense_id = ?", (expense_id,))
    splits = cursor.fetchall()

    if splits:
        print("\nSplit Expense Details:")
        for split in splits:
            owed_by_person, amount, is_paid = split
            status = "Paid" if is_paid else "Unpaid"
            print(f"{owed_by_person} owes ${amount:.2f} - Status: {status}")
    else:
        print("No split details found for this expense.")
def update_repayment_status(conn, expense_id, person_name):
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE split_expenses SET is_paid = 1 WHERE expense_id = ? AND owed_by_person = ?", (expense_id, person_name))
        conn.commit()
        print("Repayment status updated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

def summarize_expenses():#Not yet implemented
    # Summarize expenses for a given time period
    print("\nExpense Summaries:")
    print("1. Monthly")
    print("2. Quarterly")
    print("3. Yearly")

    try:
        choice = int(input("Select a summary period (1-3): "))
        if choice < 1 or choice > 3:
            print("Invalid choice. Please select a valid summary period.")
            return

        if choice == 1:
            period = "Month"
        elif choice == 2:
            period = "Quarter"
        else:
            period = "Year"

        # Calculate and display the summary
        today = datetime.date.today()
        total_expense = 0
        for category, category_expenses in expenses.items():
            category_total = sum(amount for date, amount, _ in category_expenses if date >= today - datetime.timedelta(days=30 * choice))
            total_expense += category_total
            print(f"{category} Expenses in the Last {period}: ${category_total:.2f}")

        print(f"Total Expenses in the Last {period}: ${total_expense:.2f}")

    except ValueError:
        print("Invalid input. Please enter a valid number for the summary period.")
def show_menu():#Not used
    while True:
        print("\nExpense Tracking System:")
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
                record_expense()
            elif choice == 2:
                list_expenses()
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
def create_budget():
    while True:
        try:
          
            budget_input = input("Please enter your budget for the month: ")

           
            budget = float(budget_input)

           
            if budget < 0:
                print("Please enter a positive number.")
                continue

            return budget

        except ValueError:
            # Handle cases where the conversion to float fails (invalid input)
            print("Invalid input. Please enter a numeric value.")