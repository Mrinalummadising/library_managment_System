import sqlite3
from tabulate import tabulate

# Initialize the database
def initialize_db():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    
    # Create tables if not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        is_available BOOLEAN DEFAULT 1
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS borrow_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        borrow_date TEXT NOT NULL,
        return_date TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(book_id) REFERENCES books(id)
    )
    """)
    
    conn.commit()
    conn.close()

# Add a new book
def add_book(title, author):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
    conn.commit()
    conn.close()
    print(f"Book '{title}' by {author} added to the library.")

# Register a new user
def register_user(name):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    print(f"User '{name}' registered successfully.")

# Borrow a book
def borrow_book(user_id, book_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    
    # Check if book is available
    cursor.execute("SELECT is_available FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    if not book:
        print("Book not found.")
        conn.close()
        return
    if not book[0]:
        print("Book is currently unavailable.")
        conn.close()
        return

    # Borrow the book
    cursor.execute("INSERT INTO borrow_records (user_id, book_id, borrow_date) VALUES (?, ?, DATE('now'))", (user_id, book_id))
    cursor.execute("UPDATE books SET is_available = 0 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    print(f"Book ID {book_id} borrowed by User ID {user_id}.")

# Return a book
def return_book(user_id, book_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # Check if the user borrowed this book
    cursor.execute("""
    SELECT id FROM borrow_records
    WHERE user_id = ? AND book_id = ? AND return_date IS NULL
    """, (user_id, book_id))
    record = cursor.fetchone()
    if not record:
        print("No active borrow record found for this user and book.")
        conn.close()
        return

    # Return the book
    cursor.execute("UPDATE borrow_records SET return_date = DATE('now') WHERE id = ?", (record[0],))
    cursor.execute("UPDATE books SET is_available = 1 WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    print(f"Book ID {book_id} returned by User ID {user_id}.")

# View available books
def view_books():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author FROM books WHERE is_available = 1")
    books = cursor.fetchall()
    conn.close()
    print(tabulate(books, headers=["ID", "Title", "Author"], tablefmt="pretty"))

# View user borrowing history
def view_user_history(user_id):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT b.title, br.borrow_date, br.return_date
    FROM borrow_records br
    JOIN books b ON br.book_id = b.id
    WHERE br.user_id = ?
    """, (user_id,))
    history = cursor.fetchall()
    conn.close()
    print(tabulate(history, headers=["Title", "Borrow Date", "Return Date"], tablefmt="pretty"))

# Main menu
def main():
    initialize_db()
    
    while True:
        print("\nLibrary Management System")
        print("1. Add Book")
        print("2. Register User")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. View Available Books")
        print("6. View User Borrowing History")
        print("7. Exit")
        
        choice = input("Enter your choice: ")
        if choice == "1":
            title = input("Enter book title: ")
            author = input("Enter book author: ")
            add_book(title, author)
        elif choice == "2":
            name = input("Enter user name: ")
            register_user(name)
        elif choice == "3":
            user_id = int(input("Enter user ID: "))
            book_id = int(input("Enter book ID: "))
            borrow_book(user_id, book_id)
        elif choice == "4":
            user_id = int(input("Enter user ID: "))
            book_id = int(input("Enter book ID: "))
            return_book(user_id, book_id)
        elif choice == "5":
            view_books()
        elif choice == "6":
            user_id = int(input("Enter user ID: "))
            view_user_history(user_id)
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
