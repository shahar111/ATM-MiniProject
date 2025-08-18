import sqlite3


def is_int(item) -> bool:
    return isinstance(item, int) or str(item).lstrip('-+').isdigit()


class Account:
    DB_NAME = "atm.db"

    def __init__(self, account_number, balance=0):
        self.account_number = account_number
        self.balance = balance

    @staticmethod
    def is_valid_account_number(acc_num):
        return is_int(acc_num) and int(acc_num) > 0

    @staticmethod
    def initialize_db():
        with sqlite3.connect(Account.DB_NAME) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    account_number INT PRIMARY KEY,
                    balance REAL
                )
            ''')

    @staticmethod
    def get(account_number):
        if not Account.is_valid_account_number(account_number):
            raise ValueError("Account number must be a positive integer")

        row = None
        with sqlite3.connect(Account.DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT balance FROM accounts WHERE account_number = ?", (account_number,))
            row = c.fetchone()

        if row:
            return Account(account_number, row[0])
        else:
            return None

    @staticmethod
    def create(account_number, balance=0):
        if not Account.is_valid_account_number(account_number):
            raise ValueError("Account number must be a positive integer")
        if not isinstance(balance, (int, float)):
            raise ValueError("Amount must be numeric")
        if balance < 0:
            raise ValueError("Initial amount cannot be negative")
        try:
            with sqlite3.connect(Account.DB_NAME) as conn:
                conn.execute("INSERT INTO accounts VALUES (?, ?)", (int(account_number), float(balance)))
            return Account(account_number, balance)
        except sqlite3.IntegrityError:
            raise ValueError(f"Account {int(account_number)} already exists")

    def deposit(self, amount):
        if not isinstance(amount, (int, float)):
            raise ValueError("Amount must be numeric")
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.balance += amount
        self._update_db()
        return self.balance

    def withdraw(self, amount):
        if not isinstance(amount, (int, float)):
            raise ValueError("Amount must be numeric")
        if amount <= 0:
            raise ValueError("Withdraw must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self._update_db()
        return self.balance

    def _update_db(self):
        with sqlite3.connect(Account.DB_NAME) as conn:
            conn.execute("UPDATE accounts SET balance = ? WHERE account_number = ?",
                         (self.balance, self.account_number))

    def get_balance(self):
        return self.balance
