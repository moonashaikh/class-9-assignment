import sqlite3
import hashlib

# --- Database (Abstraction) ---
class Database:
    def __init__(self, db_name="store.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            username TEXT UNIQUE,
                            password TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS payments (
                            id INTEGER PRIMARY KEY,
                            username TEXT,
                            amount REAL,
                            method TEXT)''')
        self.conn.commit()

    def register_user(self, username, password):
        try:
            cursor = self.conn.cursor()
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def validate_user(self, username, password):
        cursor = self.conn.cursor()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
        return cursor.fetchone() is not None

    def log_payment(self, username, amount, method):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO payments (username, amount, method) VALUES (?, ?, ?)", (username, amount, method))
        self.conn.commit()

# --- User (Encapsulation) ---
class User:
    def __init__(self, db: Database):
        self.db = db
        self.username = None

    def signup(self, username, password):
        if self.db.register_user(username, password):
            print("User registered successfully.")
        else:
            print("Username already exists.")

    def login(self, username, password):
        if self.db.validate_user(username, password):
            self.username = username
            print(f"Welcome back, {username}!")
            return True
        else:
            print("Invalid credentials.")
            return False

# --- Payment (Polymorphism) ---
class Payment:
    def pay(self, amount):
        raise NotImplementedError("This method should be overridden.")

class CreditCardPayment(Payment):
    def pay(self, amount):
        print(f"Processing credit card payment of ${amount}...")
        return True

class PayPalPayment(Payment):
    def pay(self, amount):
        print(f"Processing PayPal payment of ${amount}...")
        return True

# --- Store App ---
class StoreApp:
    def __init__(self):
        self.db = Database()
        self.user = User(self.db)

    def run(self):
        print("Welcome to the E-Commerce App")
        while True:
            action = input("Choose action: [signup/login/quit]: ")
            if action == "signup":
                u = input("Username: ")
                p = input("Password: ")
                self.user.signup(u, p)
            elif action == "login":
                u = input("Username: ")
                p = input("Password: ")
                if self.user.login(u, p):
                    self.shop()
            elif action == "quit":
                break

    def shop(self):
        while True:
            amount = float(input("Enter amount to pay (or 0 to logout): "))
            if amount == 0:
                print("Logging out.")
                break
            method = input("Choose payment method (card/paypal): ")
            if method == "card":
                payment = CreditCardPayment()
            elif method == "paypal":
                payment = PayPalPayment()
            else:
                print("Invalid method.")
                continue

            if payment.pay(amount):
                self.db.log_payment(self.user.username, amount, method)
                print("Payment successful!")

# --- Run App ---
if __name__ == "__main__":
    app = StoreApp()
    app.run()
