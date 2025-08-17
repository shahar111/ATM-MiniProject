from flask import Flask, jsonify
from flask import request
from account import Account

app = Flask(__name__)

# examples
accounts = {
    "123": Account("123", 100),
    "456": Account("456", 200)
}


@app.route('/accounts/<account_number>/balance')
def get_balance(account_number):
    account = accounts.get(account_number)
    if not account:
        account = Account(account_number, 0)
        accounts[account_number] = account
    return jsonify({"account_number": account_number, "balance": account.get_balance()})


@app.route('/accounts/<account_number>/deposit', methods=['POST'])
def deposit(account_number):
    account = accounts.get(account_number)
    if not account:
        account = Account(account_number, 0)
        accounts[account_number] = account

    data = request.get_json()
    amount = data.get("amount", 0)
    try:
        new_balance = account.deposit(amount)
        return jsonify({"account_number": account_number, "balance": new_balance})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
