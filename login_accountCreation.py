##########
#   luis torres
#   login/ create an account
#   last updated:   10.30.23
##########

import sqlite3

def initialize_login_db():
    connection = sqlite3.connect("user_data.db")
    cursor = connection.cursor()

    #table creation
    cursor.execute('''CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, pass TEXT);''')
    connection.commit()
    return connection   #creates login DB

def show_users(connection): #hidden admin function, displays users in the DB, hit 3 on menu, FUNCTIONING
    cursor = connection.cursor()
    cursor.execute("SELECT name, pass, user_id FROM users")
    print("Current users in the database:")
    for row in cursor:
        print(f"Username: {row[0]} | Password: {row[1]} | UserID: {row[2]}")
        
def add_user(connection,username,password): #creates another user, username has to be unique FUNCTIONING
    try:
        script="INSERT INTO users(name,pass) VALUES (?,?);"
        connection.execute(script,(username,password))
        connection.commit()
    except sqlite3.IntegrityError:
        print("That Usename is taken. Please choose a different one.")

def check_login(connection,username,password): # returns user_id, FUNCTIONING
    cursor=connection.execute("SELECT user_id FROM users WHERE name = ? AND pass = ?", (username, password))
    row = cursor.fetchone()
    return row[0] if row else None   

def loginMenu(): # if there is no login DB, creates it. and/or runs login menu FUNCTIONING

    connection = initialize_login_db()
    user_id = None
    usersFirstName=None
    while True:
        answer = input("Welcome to the Expense Tracker Application! What would you like to do?\n1.)Log in \n2.)Create Account\n")

        if answer == "1":
            username = input("Please enter your username: ")
            password = input("Please enter your password: ")
            user_id = check_login(connection, username, password)
            usersFirstName=username
            if user_id:
                print(f"\nLogin success\nYour user ID is: {user_id}")
                # Perform actions for logged-in user
                break  # or continue in the loop depending on your application's flow
            else:
                print("\nLogin failed\n")

        elif answer == "2":
            username = input("Please enter a username: ")
            password = input("Please enter a password: ")
            add_user(connection, username, password)
            print(f"Account created for {username}")

        elif answer == '3':
            show_users(connection)
        else:
            print("Invalid option. Please enter 1 or 2.")

    connection.close()
    return user_id,usersFirstName     