from flask import Flask, jsonify
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


if __name__ == "__main__":
    app.run(debug=True)
