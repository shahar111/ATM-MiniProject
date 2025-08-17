import sqlite3

DB_NAME = "atm.db"


class Account:
    def __init__(self, account_number, balance=0):
        self.account_number = account_number
        self.balance = balance

    @staticmethod
    def initialize_db():
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_number TEXT PRIMARY KEY,
                balance REAL
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def get(account_number):
        conn = sqlite3.connect(DB_NAME)
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
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO accounts (account_number, balance) VALUES (?, ?)", (account_number, balance))
        conn.commit()
        conn.close()
        return Account(account_number, balance)

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
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE accounts SET balance = ? WHERE account_number = ?", (self.balance, self.account_number))
        conn.commit()
        conn.close()

    def get_balance(self):
        return self.balance
