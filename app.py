from flask import Flask, jsonify
from flask import request
from account import Account

app = Flask(__name__)
Account.initialize_db()


@app.route("/")
def home():
    return {
        "project": "ATM Mini Project",
        "version": "1.0",
        "endpoints": [
            "/accounts/<account_number>/balance",
            "/accounts/<account_number>/deposit",
            "/accounts/<account_number>/withdraw"
        ]
    }


# --- GET BALANCE ---
@app.route('/accounts/<account_number>/balance')
def get_balance(account_number):
    if not Account.is_valid_account_number(account_number):
        return jsonify({"error": "Account number must be a positive integer"}), 400
    account = Account.get(account_number)
    if not account:
        account = Account.create(account_number, 0)
    return jsonify({"account_number": account_number, "balance": account.get_balance()})


# --- DEPOSIT ---
@app.route('/accounts/<account_number>/deposit', methods=['POST'])
def deposit(account_number):
    account = Account.get(account_number)
    if not account:
        account = Account.create(account_number, 0)

    data = request.get_json()
    if not data or "amount" not in data:
        return jsonify({"error": "Missing 'amount' in request"}), 400

    amount = data.get("amount", 0)
    try:
        new_balance = account.deposit(amount)
        return jsonify({"account_number": account_number, "balance": new_balance})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# --- WITHDRAW ---
@app.route('/accounts/<account_number>/withdraw', methods=['POST'])
def withdraw(account_number):
    account = Account.get(account_number)
    if not account:
        return jsonify({"error": "Account not found"}), 404

    data = request.get_json()
    if not data or "amount" not in data:
        return jsonify({"error": "Missing 'amount' in request"}), 400

    amount = data.get("amount", 0)
    try:
        new_balance = account.withdraw(amount)
        return jsonify({"account_number": account_number, "balance": new_balance})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.errorhandler(404)
def not_found(e):
    return {"error": "Endpoint not found"}, 404


@app.errorhandler(500)
def server_error(e):
    return {"error": "Internal server error"}, 500


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)
