import sqlite3


class Account:
    DB_NAME = "atm.db"

    def __init__(self, account_number, balance=0):
        self.account_number = account_number
        self.balance = balance

    @staticmethod
    def initialize_db():
        conn = sqlite3.connect(Account.DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_number INT PRIMARY KEY,
                balance REAL
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def get(account_number):
        conn = sqlite3.connect(Account.DB_NAME)
        c = conn.cursor()
        c.execute("SELECT balance FROM accounts WHERE account_number = ?", (account_number,))
        row = c.fetchone()
        conn.close()
        if row:
            return Account(account_number, row[0])
        else:
            return None

    @staticmethod
    def create(account_number, balance=0):
        if not isinstance(account_number, int) or account_number <= 0:
            raise ValueError("Account number must be a positive integer")
        if not isinstance(balance, (int, float)):
            raise ValueError("Amount must be numeric")
        if balance < 0:
            raise ValueError("Initial amount cannot be negative")

        try:
            with sqlite3.connect(Account.DB_NAME) as conn:
                conn.execute("INSERT INTO accounts VALUES (?, ?)", (account_number, balance))
            return Account(account_number, balance)
        except sqlite3.IntegrityError:
            raise ValueError(f"Account {account_number} already exists")

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.balance += amount
        self._update_db()
        return self.balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdraw must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self._update_db()
        return self.balance

    def _update_db(self):
        conn = sqlite3.connect(Account.DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE accounts SET balance = ? WHERE account_number = ?", (self.balance, self.account_number))
        conn.commit()
        conn.close()

    def get_balance(self):
        return self.balance
