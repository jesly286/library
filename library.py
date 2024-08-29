import re
import mysql.connector
from datetime import datetime, timedelta

# --- Database Connection ---
db = mysql.connector.connect(
         host='localhost',
         user='root',
         password='12345',
         database='library_db'
)
login = db.cursor()

# Creating Admin table
login.execute("""
CREATE TABLE IF NOT EXISTS Admin (
    ADMIN_ID INT AUTO_INCREMENT PRIMARY KEY,
    Firstname VARCHAR(300),
    Lastname VARCHAR(300),
    Password VARCHAR(300),
    Email VARCHAR(300)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Subscriptions (
    SUB_ID INT AUTO_INCREMENT PRIMARY KEY,
    PLANS VARCHAR(20),
    PRICE INT
)
""")

# Creating Customer table
login.execute("""
CREATE TABLE IF NOT EXISTS Customer (
    CUST_ID INT AUTO_INCREMENT PRIMARY KEY,
    First_Name VARCHAR(300),
    Last_Name VARCHAR(300),
    Password VARCHAR(300),
    Email VARCHAR(300),
    REG_Date DATE,
    SUB_ID INT,
    Last_Login DATE,
    FOREIGN KEY (SUB_ID) REFERENCES Subscriptions (SUB_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Authors (
    AUTHOR_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(300)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Category (
    CAT_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(300)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Genre (
    GEN_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(300)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Books (
    BOOK_ID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(300),
    Author_Name VARCHAR(300),
    Price VARCHAR(100),
    CAT_ID INT,
    GEN_ID INT,
    FOREIGN KEY (CAT_ID) REFERENCES Category(CAT_ID),
    FOREIGN KEY (GEN_ID) REFERENCES Genre(GEN_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Rentals (
    RENTAL_ID INT AUTO_INCREMENT PRIMARY KEY,
    CUST_ID INT,
    BOOK_ID INT,
    Rent_Date DATE,
    Return_Date DATE,
    FOREIGN KEY (CUST_ID) REFERENCES Customer(CUST_ID),
    FOREIGN KEY (BOOK_ID) REFERENCES Books(BOOK_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Reminders (
    REM_ID INT AUTO_INCREMENT PRIMARY KEY,
    ADMIN_ID INT,
    Rem_Date DATE,
    FOREIGN KEY (ADMIN_ID) REFERENCES Admin(ADMIN_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Sub_Reminders (
    SREM_ID INT AUTO_INCREMENT PRIMARY KEY,
    SUB_ID INT,
    Rem_Date DATE,
    Rem_Status VARCHAR(300),
    FOREIGN KEY (SUB_ID) REFERENCES Subscriptions(SUB_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Memberships (
    MEM_ID INT AUTO_INCREMENT PRIMARY KEY,
    CUST_ID INT,
    Start_Date DATE,
    Renewal_Status VARCHAR(300),
    FOREIGN KEY (CUST_ID) REFERENCES Customer(CUST_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Payments (
    PAYMENT_ID INT AUTO_INCREMENT PRIMARY KEY,
    SUB_ID INT,
    CUST_ID INT,
    MEM_ID INT,
    Amount VARCHAR(100),
    Payment_Date DATE,
    Payment_Method VARCHAR(300),
    FOREIGN KEY (SUB_ID) REFERENCES Subscriptions(SUB_ID),
    FOREIGN KEY (CUST_ID) REFERENCES Customer(CUST_ID),
    FOREIGN KEY (MEM_ID) REFERENCES Memberships(MEM_ID)
)
""")

login.execute("""
CREATE TABLE IF NOT EXISTS Reviews (
    REVIEW_ID INT AUTO_INCREMENT PRIMARY KEY,
    CUST_ID INT,
    BOOK_ID INT,
    Review_Text VARCHAR(500),
    Rating VARCHAR(300),
    Review_Date DATE,
    FOREIGN KEY (CUST_ID) REFERENCES Customer(CUST_ID),
    FOREIGN KEY (BOOK_ID) REFERENCES Books(BOOK_ID)
)
""")


def validate_input(prompt, validation_func=None, error_message=None):
    while True:
        user_input = input(prompt).strip()
        if not validation_func or validation_func(user_input):
            return user_input
        if error_message:
            print(error_message)


def validate_name(name):
    return name.isalpha() and len(name) >= 2


def validate_password(password):
    return (len(password) >= 9 and
            re.search("[A-Z]", password) and
            re.search("[a-z]", password) and
            re.search("[0-9]", password) and
            re.search("[@#$%^&+=]", password))


def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def add_user(connection):
    cursor = connection.cursor()
    print("\n-----------------------------\n"
          "        Add New User\n"
          "------------------------------")

    firstname = validate_input("Enter first name: ", validate_name,
                               "Name should only contain alphabetic characters and be at least 2 characters long.")
    lastname = validate_input("Enter last name: ", validate_name,
                              "Name should only contain alphabetic characters and be at least 2 characters long.")
    email = validate_input("Enter email: ", validate_email, "Invalid email format.")
    password = validate_input("Enter the password: ", validate_password,
                              "Password must be at least 9 characters long, contain an uppercase letter,"
                              " a lowercase letter, a digit, and a special character (@#$%^&+=).")
    registration_date = datetime.now().date()

    while True:
        try:
            sub_id = int(input("Select a subscription plan\n(1001 - Weekly ($250) / 1002 - Monthly ($750)/ 1003 - Yearly ($2000)): "))
            if sub_id in [1001, 1002, 1003]:
                break
            else:
                print("Invalid subscription plan. Please select from the available options.")
        except ValueError:
            print("Please enter a valid number for the subscription plan.")

    try:
        cursor.execute(
            "INSERT INTO Customer (First_Name, Last_Name, Email, Password, SUB_ID, REG_Date) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (firstname, lastname, email, password, sub_id, registration_date)
        )
        connection.commit()
        print("User added successfully!")
        customer_login(db)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        print("Email might already be taken, please try again.")

def update_user(connection, user_id):
    cursor = connection.cursor()
    print("\n----------------------------------\n "
                   "     Update User Details\n"
          " -----------------------------------"
          "")
    firstname = input("Enter new first name: ").strip()
    lastname = input("Enter new last name: ").strip()
    email = validate_input("Enter new email: ", validate_email, "Invalid email format.")
    password = validate_input("Enter new password: ", validate_password,
                              "Password must be at least 9 characters long, contain an uppercase letter, "
                              "a lowercase letter, a digit, and a special character (@#$%^&+=).")
    registration_date = validate_input("Enter new registration date (YYYY-MM-DD): ", validate_date,
                                       "Invalid date format. Please use YYYY-MM-DD.")
    new_sub_id = int(input("Enter new subscription ID : "))

    try:
        cursor.execute(
            """
            UPDATE Customer 
            SET First_Name = %s, Last_Name = %s, Email = %s, Password = %s, REG_Date = %s, SUB_ID = %s 
            WHERE CUST_ID = %s
            """,
            (firstname, lastname, email, password, registration_date, new_sub_id, user_id)
        )
        connection.commit()
        print("User details updated successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def remove_user(connection,userid):
    cursor = connection.cursor()
    print("\n--------------------------------\n "
                        "      Remove User\n "
          "-----------------------------------"
          "")

    try:
        cursor.execute("""
            SELECT CUST_ID FROM Customer
            WHERE CUST_ID = %s
        """, (int(userid),))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
            cursor.execute("DELETE FROM Customer WHERE CUST_ID = %s", (user_id,))
            connection.commit()
            print("User removed successfully!")
        else:
            print("No user found with the provided details.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def add_books(connection):
    cursor = connection.cursor()
    print("\n---------------------------\n"
             "          Add New Book\n "
          "-----------------------------"
          "")
    title = input("Enter the book title: ").strip()
    author_name = input("Enter the author's name: ").strip()
    price = validate_input("Enter the book price: ", lambda p: p.replace('.', '', 1).isdigit(),
                           "Price must be a valid number.")
    category_id = validate_input("Enter the category ID: ", lambda c: c.isdigit(), "Category ID must be a number.")
    genre_id = validate_input("Enter the genre ID: ", lambda g: g.isdigit(), "Genre ID must be a number.")

    try:
        cursor.execute(
            "INSERT INTO Books (Title, Author_Name, Price, CAT_ID, GEN_ID) "
            "VALUES (%s, %s, %s, %s, %s)",
            (title, author_name, float(price), int(category_id), int(genre_id))
        )
        connection.commit()
        print("Book added successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def update_books(connection):
    cursor = connection.cursor()
    print("\n-----------------------------\n "
             "       Update Book Details\n "
          "--------------------------------"
          "")
    book_id = validate_input("Enter the book ID to update: ", lambda b: b.isdigit(), "Book ID must be a number.")
    title = input("Enter new book title: ").strip()
    author_name = input("Enter new author name: ").strip()
    price = validate_input("Enter new book price: ", lambda p: p.replace('.', '', 1).isdigit(),
                           "Price must be a valid number.")
    category_id = validate_input("Enter new category ID: ", lambda c: c.isdigit(), "Category ID must be a number.")
    genre_id = validate_input("Enter new genre ID: ", lambda g: g.isdigit(), "Genre ID must be a number.")

    try:
        cursor.execute(
            """
            UPDATE Books 
            SET Title = %s, Author_Name = %s, Price = %s, CAT_ID = %s, GEN_ID = %s 
            WHERE BOOK_ID = %s
            """,
            (title, author_name, float(price), int(category_id), int(genre_id), int(book_id))
        )
        connection.commit()
        print("Book details updated successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def remove_books(connection):
    cursor = connection.cursor()
    print("\n------------------------------\n "
                       "     Remove Book\n"
          "--------------------------------"
         "")
    book_id = validate_input("Enter the book ID to remove: ", lambda b: b.isdigit(), "Book ID must be a number.")

    try:
        cursor.execute("DELETE FROM Books WHERE BOOK_ID = %s", (int(book_id),))
        connection.commit()
        print("Book removed successfully!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def view_rental_history(connection):
    cursor = connection.cursor()
    print("\n--------------------------------\n"
                 "     View Rental History\n"
          "--------------------------------"
          "")
    customer_id = validate_input("Enter customer ID to view rental history: ", lambda c: c.isdigit(),
                                 "Customer ID must be a number.")

    try:
        cursor.execute("""
            SELECT Rent_Date, Return_Date, Title
            FROM Rentals
            JOIN Books ON Rentals.BOOK_ID = Books.BOOK_ID
            WHERE CUST_ID = %s
        """, (int(customer_id),))

        rentals = cursor.fetchall()

        if rentals:
            for rental in rentals:
                print(f"Rent Date: {rental[0]}, Return Date: {rental[1]}, Book Title: {rental[2]}")
        else:
            print("No rental history found for this customer.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def send_subscription_reminders(connection, admin_id):
    cursor = connection.cursor()
    print("\n------------------------------------------------------------\n"
                           "       Send Subscription Renewal Reminders\n "
          "-------------------------------------------------------------"
          "")
    today = datetime.now().date()

    try:
        cursor.execute("""
            SELECT CUST_ID, Start_Date, Renewal_Status
            FROM Subscriptions
            WHERE Renewal_Status = 'Active'
        """)

        subscriptions = cursor.fetchall()

        for subscription in subscriptions:
            cust_id, start_date, renewal_status = subscription
            next_renewal_date = start_date + timedelta(days=365)  # Assuming annual renewal

            if next_renewal_date <= today + timedelta(days=7):   # Remind 7 days before renewal
                cursor.execute("""
                    INSERT INTO Sub_Reminders (SUB_ID, Rem_Date, Rem_Status)
                    VALUES (%s, %s, %s)
                """, (cust_id, today, 'Pending'))

                connection.commit()
                print(f"Reminder sent for subscription ID {cust_id}.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def view_rented_books(connection):
    cursor = connection.cursor()
    print("\n----------------------------\n "
                 "    View Rented Books\n "
          "------------------------------"
          "")

    query = """
    SELECT Rentals.RENTAL_ID, Customer.CUST_ID, Customer.First_Name, Customer.Last_Name, 
           Books.BOOK_ID, Books.Title, Rentals.Rent_Date, Rentals.Return_Date
    FROM Rentals
    JOIN Customer ON Rentals.CUST_ID = Customer.CUST_ID
    JOIN Books ON Rentals.BOOK_ID = Books.BOOK_ID
    ORDER BY Rentals.Rent_Date DESC
    """

    cursor.execute(query)
    rented_books = cursor.fetchall()

    if rented_books:
        print(f"{'Rental ID':<10} {'Customer ID':<12} {'Customer Name':<25} {'Book ID':<8} {'Book Title':<30} "
              f"{'Rent Date':<12} {'Return Date':<12}")
        print("=" * 100)
        for rental in rented_books:
            rental_id, cust_id, first_name, last_name, book_id, title, rent_date, return_date = rental
            print(f"{rental_id:<10} {cust_id:<12} {first_name + ' ' + last_name:<25} {book_id:<8} {title:<30} "
                  f"{rent_date:<12} {return_date if return_date else 'Not Returned':<12}")
    else:
        print("No rented books found.")
    cursor.close()


def rent_book_for_customer(connection):
    cursor = connection.cursor()
    print("\n--------------------------------\n "
            "      Rent Book for Customer\n"
          "----------------------------------"
          "")

    cust_id = input("Enter Customer ID: ").strip()
    cursor.execute("SELECT CUST_ID FROM Customer WHERE CUST_ID = %s", (cust_id,))
    if not cursor.fetchone():
        print("Invalid Customer ID.")
        cursor.close()
        return

    book_id = input("Enter Book ID: ").strip()
    cursor.execute("SELECT BOOK_ID FROM Books WHERE BOOK_ID = %s", (book_id,))
    if not cursor.fetchone():
        print("Invalid Book ID.")
        cursor.close()
        return

    cursor.execute("SELECT RENTAL_ID FROM Rentals WHERE BOOK_ID = %s AND Return_Date IS NULL", (book_id,))
    if cursor.fetchone():
        print("This book is already rented and not yet returned.")
        cursor.close()
        return

    try:
        rent_date = datetime.now().date()  # Use datetime.now().date() to get the current date
        cursor.execute("INSERT INTO Rentals (CUST_ID, BOOK_ID, Rent_Date) VALUES (%s, %s, %s)",
                       (cust_id, book_id, rent_date))
        connection.commit()
        print("Book rented successfully!")
    except mysql.connector.Error as e:
        connection.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()


def search_books(connection):
    cursor = connection.cursor()
    print("\n-----------------------\n "
          "       Search Books\n"
          "--------------------------"
          "")
    title = input("Enter book title : ").strip()
    author_name = input("Enter author name : ").strip()

    min_price = input("Enter minimum price : ").strip()
    max_price = input("Enter maximum price : ").strip()

    cat_id = input("Enter category ID : ").strip()
    gen_id = input("Enter genre ID : ").strip()

    query = "SELECT Title, Author_Name, Price, CAT_ID, GEN_ID FROM Books WHERE 1=1"
    params = []

    if title:
        query += " AND Title LIKE %s"
        params.append(f"%{title}%")

    if author_name:
        query += " AND Author_Name LIKE %s"
        params.append(f"%{author_name}%")

    if min_price:
        query += " AND Price >= %s"
        params.append(float(min_price))

    if max_price:
        query += " AND Price <= %s"
        params.append(float(max_price))

    if cat_id:
        query += " AND CAT_ID = %s"
        params.append(int(cat_id))

    if gen_id:
        query += " AND GEN_ID = %s"
        params.append(int(gen_id))

    try:
        cursor.execute(query, tuple(params))
        books = cursor.fetchall()  # Fetch all results to clear the cursor

        if books:
            print("\nSearch Results:")
            for book in books:
                print(f"Title: {book[0]}, Author: {book[1]}, Price: ${book[2]}, "
                      f"Category ID: {book[3]}, Genre ID: {book[4]}")
        else:
            print("No books found matching the criteria.")
    except mysql.connector.Error as e:
        print(f"Error fetching books: {e}")
    finally:
        cursor.close()

def borrow_books(connection):
    cursor = connection.cursor()
    print("\n----------------------------\n"
                "        Borrow a Book\n "
          "-----------------------------"
          "")
    bookid = input("Enter the book id:")

    query = "SELECT  r.BOOK_ID,b.Title, b.Author_Name, b.Price FROM rentals r join books b on r.BOOK_ID=b.BOOK_ID WHERE r.BOOK_ID = %s"
    cursor.execute(query, (int(bookid),))
    book = cursor.fetchone()

    if book:
        print(f"\nBook Found: Title: {book[1]}, AuthorName: {book[2]}, Price: ${book[3]}")
        if input("Do you want to borrow this book? (yes/no): ").strip().lower() == 'yes':
            try:
                rent_date = datetime.now()  # Use datetime.now() to get the current date and time
                return_date = rent_date + timedelta(days=14)
                cust_id = input("Enter your customer ID: ").strip()  # Ask for customer ID to be used in Rentals table
                cursor.execute("INSERT INTO Rentals (CUST_ID, BOOK_ID, Rent_Date, Return_Date) VALUES (%s, %s, %s, %s)",
                               (cust_id, book[0], rent_date, return_date))
                connection.commit()
                print("Book borrowed successfully. Return Date:", return_date.strftime('%Y-%m-%d'))
            except mysql.connector.Error as e:
                connection.rollback()
                print(f"Failed to borrow the book: {e}")
    else:
        print("Book not found or details do not match.")
    cursor.close()


def add_review(connection, cust_id):
    cursor = connection.cursor()

    while True:
        try:
            book_id = int(input("Enter the Book ID you want to review: ").strip())
            cursor.execute("SELECT BOOK_ID FROM Books WHERE BOOK_ID = %s", (book_id,))
            if cursor.fetchone():
                break
            else:
                print("Invalid Book ID.")
        except ValueError:
            print("Book ID must be an integer. Please try again.")

    while True:
        review_text = input("Enter your review (max 500 characters): ").strip()
        if len(review_text) <= 500:
            break
        else:
            print("Review text is too long. Please limit it to 500 characters.")

    while True:
        rating = input("Enter your rating (e.g., 1-5): ").strip()
        if rating in ["1", "2", "3", "4", "5"]:
            break
        else:
            print("Invalid rating. Please enter a number between 1 and 5.")

    review_date = datetime.now().date()  # Use datetime.now().date() for the current date

    try:
        cursor.execute("INSERT INTO Reviews (CUST_ID, BOOK_ID, Review_Text, Rating, Review_Date) "
                       "VALUES (%s, %s, %s, %s, %s)",
                       (cust_id, book_id, review_text, rating, review_date))
        connection.commit()
        print("Review added successfully!")
    except mysql.connector.Error as e:
        connection.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()


def validate_admin_id(admin_id, db):
    try:
        admin_id = int(admin_id)
        if admin_id <= 0:
            return False

        cursor = db.cursor()
        cursor.execute("SELECT ADMIN_ID FROM Admin WHERE ADMIN_ID = %s", (admin_id,))
        result = cursor.fetchone()
        cursor.close()

        return result is not None

    except ValueError:
        return False


def validate_admin_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def validate_admin_password(password):
    if len(password) < 9:
        print("Password must be at least 9 characters long.")
        return False
    if not re.search("[A-Z]", password):
        print("Password must contain at least one uppercase letter.")
        return False
    if not re.search("[a-z]", password):
        print("Password must contain at least one lowercase letter.")
        return False
    if not re.search("[0-9]", password):
        print("Password must contain at least one digit.")
        return False
    if not re.search("[@#$%^&+=]", password):
        print("Password must contain at least one special character (@#$%^&+=).")
        return False
    return True


def admin_login(connection):
    cursor = connection.cursor()

    print("\n--------------------------\n "
                    "     Admin Login\n "
          "----------------------------"
          "")
    admin_id = input("Enter admin_id: ").strip()
    password = input("Enter admin password: ").strip()

    if not validate_admin_id(admin_id, db):
        print("Invalid ID format.")
        cursor.close()
        return None

    if not validate_admin_password(password):
        print("Invalid password format.")
        cursor.close()
        return None

    try:
        cursor.execute(
            "SELECT ADMIN_ID, Firstname, Lastname FROM Admin WHERE ADMIN_ID = %s AND Password = %s",
            (admin_id, password)
        )
        admin = cursor.fetchone()

        if admin:
            print(f"Welcome {admin[1]} {admin[2]}!")
            admin_page(db)
        else:
            print("Login failed! Incorrect email or password.")
            return None
    except mysql.connector.Error as e:
        print(f"Error during login: {e}")
        return None
    finally:
        cursor.close()


def customer_login(connection):
    cursor = connection.cursor()
    print("\n-----------------------------\n"
          "        Customer Login\n"
          "-------------------------------")

    email = input("Enter your email: ").strip()
    password = input("Enter your password: ").strip()

    try:
        cursor.execute("SELECT CUST_ID, First_Name, Last_Name FROM Customer WHERE Email = %s AND Password = %s",
                       (email, password))
        customer = cursor.fetchone()

        if customer:
            cust_id, first_name, last_name = customer
            customer_page(connection, cust_id)
            print(f"Welcome, {first_name} {last_name}!")
        else:
            print("Invalid email or password. Please try again.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()




def customer_page(connection, customer_id):
    while True:
        print("\n---------------------------\n"
              "       Customer Page\n"
              "---------------------------")
        print("1. View List of Rented Books")
        print("2. Rent a Book")
        print("3. Search for Books")
        print("4. Borrow a Book")
        print("5. Add Reviews")
        print("6. Logout")

        choice = input("Select an option: ").strip()

        if choice == '1':
            view_rented_books(connection)
        elif choice == '2':
            rent_book_for_customer(connection)
        elif choice == '3':
            search_books(connection)
        elif choice == '4':
            borrow_books(connection)
        elif choice == '5':
            add_review(connection, customer_id)
        elif choice == '6':
            print("Logging out...")
            break
        else:
            print("Invalid option. Please try again.")


def view_popular_books(connection):
    cursor = connection.cursor()
    try:
        print("\n---------------------------\n"
                    "        Popular Books\n "
              "-----------------------------"
              "")
        query = """
        SELECT title, author_name, Price
        FROM Books
        ORDER BY Price DESC LIMIT 10
        """
        cursor.execute(query)
        books = cursor.fetchall()

        if books:
            for book in books:
                print(f"Title: {book[0]}, Author: {book[1]}, Price: ${book[2]:}")
        else:
            print("No popular books found.")
    except mysql.connector.Error as e:
        print(f"Error fetching popular books: {e}")
    finally:
        cursor.close()


def view_book_details(connection):
    cursor = connection.cursor()
    try:
        book_title = input("Enter the book title to view details: ").strip()

        query = """
        SELECT Books.title, Books.author_name, Books.Price, Category.category_name, Genre.genre_name
        FROM Books
        JOIN Category ON Books.CAT_ID = Category.CAT_ID
        JOIN Genre ON Books.GEN_ID = Genre.GEN_ID
        WHERE Books.title = %s
        """
        cursor.execute(query, (book_title,))
        book = cursor.fetchone()

        if book:
            print(f"\nTitle: {book[0]}")
            print(f"Author: {book[1]}")
            print(f"Price: ${book[2]:.2f}")
            print(f"Category: {book[3]}")
            print(f"Genre: {book[4]}")
        else:
            print("Book not found.")
    except mysql.connector.Error as e:
        print(f"Error fetching book details: {e}")
    finally:
        cursor.close()

def view_users_list(db):
    cursor = db.cursor()
    query = "SELECT CUST_ID, First_Name, Last_name, Password, Email,REG_Date,SUB_ID,Last_Login FROM customer"
    cursor.execute(query)
    users = cursor.fetchall()

    if not users:
        print("\nNo users found.")
    else:
        print("\nUsers List:")
        print("{:<10} {:<20} {:<20} {:<30}".format("User ID", "First Name", "Last Name", "Email"))
        print("-" * 80)
        for user in users:
            print("{:<10} {:<20} {:<20} {:<30}".format(user[0], user[1], user[2], user[3]))
    cursor.close()
def admin_page(db):
    while True:
        print("\n---------------------------\n"
                        "       Admin Page\n "
              "------------------------------"
              "")
        print("1. Add New User")
        print("2. Update Existing User")
        print("3. Remove a User")
        print("4. Add New Book")
        print("5. Update Existing Book")
        print("6. Remove a Book")
        print("7. View Rental History")
        print("8. Send Subscription Renewal Reminders")
        print("9. Logout")
        print("10. View Users List")

        choice = input("Select an option (1-10): ").strip()

        if choice == '1':
            add_user(db)
        elif choice == '2':
            user_id = input("Enter the user ID to update: ").strip()
            update_user(db, user_id)
        elif choice == '3':
            user_id = input("Enter the user ID to remove: ").strip()
            remove_user(db,user_id)
        elif choice == '4':
            add_books(db)
        elif choice == '5':
            book_id = input("Enter the book ID to update: ").strip()
            update_books(db)
        elif choice == '6':
            book_id = input("Enter the book ID to remove: ").strip()
            remove_books(db)
        elif choice == '7':
            view_rental_history(db)
        elif choice == '8':
            send_subscription_reminders(db)
        elif choice == '9':
            main_menu(db)
            break
        elif choice == '10':
            view_users_list(db)
        else:
            print("Invalid option. Please try again.")

def guest_user_page(connection):
    while True:
        print("\n-----------------------------\n"
                    "       Guest User Page\n"
              "-----------------------------"
              "")
        print("1. View List of Popular Books")
        print("2. View Book Details")
        print("3. Register for an Account")
        print("4. Back to Main Menu")

        choice = input("Select an option: ").strip()

        if choice == '1':
            view_popular_books(connection)
        elif choice == '2':
            view_book_details(connection)
        elif choice == '3':
            add_user(connection)
        elif choice == '4':
            break
        else:
            print("Invalid option. Please try again.")


def main_menu(db):
    while True:
        print("\n-----------------------------\n "
                         "        Main Menu\n"
              "-----------------------------"
              "")
        print("1. Admin Login")
        print("2. Customer Login")
        print("3. User Registration")
        print("4. Guest User")
        print("5. Exit")
        choice = input("Select an option (1-4): ")

        if choice == '1':
            admin_login(db)
        elif choice == '2':
            customer_login(db)
        elif choice == '3':
            add_user(db)
        elif choice == '4':
            guest_user_page(db)
        elif choice == '5':
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main_menu(db)
