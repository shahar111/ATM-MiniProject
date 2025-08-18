import unittest
import os
import json
from account import Account
from app import app

# Use a separate DB for testing
TEST_DB = os.path.abspath("test_atm.db")

# --- Test account definitions ---
VALID_ACCOUNTS = {
    1111: 100,
    1112: 100.5,
    2222: 200,
    3333: 0
}

INVALID_ACCOUNTS = {
    "abc": 100,  # non-numeric account number
    "100abc": 100,  # non-numeric account number

    -123: 50,  # negative account number
    111.1: 100,
}

INVALID_AMOUNTS = {

    444: -10,  # negative initial balance
    456: -0.5,  # negative initial balance

    555: "fifty",  # non-numeric balance
    556: "50fifty",  # non-numeric balance

    111: "10.10.10",

    100: "100",
}

ADDITIONAL_ACCOUNTS = {
    "9999": 50,
    8888: 0,
    "4444": 1234567.89,
    5555: 0.987654321
}

# BASE_URL = "http://127.0.0.1:5000"
BASE_URL = ""


# --- Base Test Case ---
class BaseTestCase(unittest.TestCase):
    """Base class for all tests: sets up DB and common accounts."""

    def setUp(self):
        # Remove test DB if exists
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

        Account.DB_NAME = TEST_DB
        Account.initialize_db()

        # Initialize valid accounts
        self.accounts = {}
        for acc_num, balance in VALID_ACCOUNTS.items():
            self.accounts[acc_num] = Account.create(acc_num, balance)

    def tearDown(self):
        # Remove DB after each test
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)


# --- Helper function for API error checks ---
def assert_api_error(client, endpoint, payload=None, method="post"):
    if method.lower() == "post":
        res = client.post(endpoint, json=payload)
    elif method.lower() == "get":
        res = client.get(endpoint)
    else:
        raise ValueError(f"Unsupported method {method}")
    assert res.status_code == 400
    data = json.loads(res.data)
    assert "error" in data


# --- Account Tests ---
class TestAccount(BaseTestCase):

    def test_get_balance(self):
        for acc_num, acc in self.accounts.items():
            fetched = Account.get(acc_num)
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.get_balance(), acc.get_balance())

    def test_create_additional_accounts(self):
        for acc_num, balance in ADDITIONAL_ACCOUNTS.items():
            acc = Account.create(acc_num, balance)
            self.assertAlmostEqual(acc.get_balance(), balance)
            fetched = Account.get(acc_num)
            self.assertIsNotNone(fetched)

    def test_create_invalid_accounts(self):
        for acc_num, balance in INVALID_ACCOUNTS.items():
            with self.assertRaises(ValueError):
                Account.create(acc_num, balance)

    def test_create_invalid_amounts(self):
        for acc_num, balance in INVALID_AMOUNTS.items():
            with self.assertRaises(ValueError):
                Account.create(acc_num, balance)

    def test_get_invalid_accounts(self):
        for acc_num in INVALID_AMOUNTS.keys():
            self.assertIsNone(Account.get(acc_num))

    def test_deposit_valid(self):
        for acc_num, acc in self.accounts.items():
            new_balance = acc.deposit(50)
            self.assertAlmostEqual(new_balance, VALID_ACCOUNTS[acc_num] + 50)

    def test_deposit_invalid_amounts(self):
        for acc in self.accounts.values():
            for val in INVALID_AMOUNTS.values():
                with self.assertRaises(ValueError):
                    acc.deposit(val)

    def test_withdraw_valid(self):
        for acc_num, acc in self.accounts.items():
            if acc.get_balance() > 0:
                amount = acc.get_balance() // 2
                new_balance = acc.withdraw(amount)
                self.assertEqual(new_balance, VALID_ACCOUNTS[acc_num] - amount)

    def test_withdraw_invalid_amounts(self):
        for acc in self.accounts.values():
            # more than balance
            with self.assertRaises(ValueError):
                acc.withdraw(acc.get_balance() + 0.01)
            # invalid types or negative
            for val in INVALID_AMOUNTS.values():
                with self.assertRaises(ValueError):
                    acc.withdraw(val)

    def test_boundary_zero_amounts(self):
        for acc in self.accounts.values():
            with self.assertRaises(ValueError):
                acc.deposit(0)
            with self.assertRaises(ValueError):
                acc.withdraw(0)


# --- App / API Tests ---
class TestApp(BaseTestCase):
    def setUp(self):
        super().setUp()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_get_balance_existing(self):
        for acc_num, balance in VALID_ACCOUNTS.items():
            res = self.client.get(f"/accounts/{acc_num}/balance")
            data = json.loads(res.data)
            self.assertAlmostEqual(data["balance"], balance)

    def test_get_balance_new_account(self):
        for acc_num in ADDITIONAL_ACCOUNTS.keys():
            res = self.client.get(f"/accounts/{acc_num}/balance")
            data = json.loads(res.data)
            self.assertEqual(data["balance"], 0)

    def test_get_balance_invalid_account(self):
        for acc_num in INVALID_ACCOUNTS.keys():
            assert_api_error(self.client, f"/accounts/{str(acc_num)}/balance", {}, "get")


    def test_deposit_valid(self):
        for acc_num, balance in VALID_ACCOUNTS.items():
            res = self.client.post(f"/accounts/{acc_num}/deposit", json={"amount": 50})
            data = json.loads(res.data)
            self.assertAlmostEqual(data["balance"], balance + 50)

    def test_deposit_missing_amount(self):
        for acc_num in VALID_ACCOUNTS.keys():
            assert_api_error(self.client, f"/accounts/{acc_num}/deposit", {})

    def test_deposit_invalid_amount(self):
        for acc_num in VALID_ACCOUNTS.keys():
            for val in INVALID_AMOUNTS.values():
                assert_api_error(self.client, f"/accounts/{acc_num}/deposit", {"amount": val})

    def test_withdraw(self):
        for acc_num, balance in VALID_ACCOUNTS.items():
            if balance > 0:
                amount = balance // 2
                res = self.client.post(f"/accounts/{acc_num}/withdraw", json={"amount": amount})
                data = json.loads(res.data)
                self.assertAlmostEqual(data["balance"], balance - amount)

    def test_withdraw_insufficient(self):
        for acc_num, balance in VALID_ACCOUNTS.items():
            assert_api_error(self.client, f"/accounts/{acc_num}/withdraw", {"amount": balance + 0.01})

    def test_withdraw_missing_amount(self):
        for acc_num in VALID_ACCOUNTS.keys():
            assert_api_error(self.client, f"/accounts/{acc_num}/withdraw", {})

    def test_withdraw_invalid_amount(self):
        for acc_num in VALID_ACCOUNTS.keys():
            for val in INVALID_AMOUNTS.values():
                assert_api_error(self.client, f"/accounts/{acc_num}/withdraw", {"amount": val})


if __name__ == "__main__":
    unittest.main()
