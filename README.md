# ATM-MiniProject

## Overview
This project is a simple ATM system with a server-side implementation.  
It provides REST API endpoints for basic ATM operations:

- Get account balance
- Deposit money
- Withdraw money

The backend is implemented in Python using Flask and SQLite for data storage.  
Each account is uniquely identified by an account number.

---

## My Approach

### Design Decisions
1. **Flask Framework**: Chosen for simplicity and rapid API development.
2. **SQLite Database**: Lightweight, file-based storage suitable for this mini-project.
3. **Account Class**: Encapsulates account operations (create, deposit, withdraw) and database interaction.
4. **Separate Test Database**: Ensures tests do not affect production data.
5. **API Endpoints**:
   - `GET /accounts/<account_number>/balance` — retrieves account balance.
   - `POST /accounts/<account_number>/deposit` — deposits a specified amount.
   - `POST /accounts/<account_number>/withdraw` — withdraws a specified amount.


### Challenges I Faced
- I struggled with the deployment, as the options written in the home assignment instructions all cost money and experience I do not have, and therefore, after researching options with ChatGPT, I have decided to host my server on Render.
- I didn't know how to test the application.

### Assumptions
- If the call withdraw or deposit has a negative amount, return an error.
- If the user attempts to deposit/get-balance on an unexisting account, the databse create the new account ith initial balance of 0.
- If the user attempts to withdraw on an unexisting account, return error.
  
---

## Installation

1. Clone the repository:

```bash
git clone <YOUR_REPO_URL>
cd ATM-MiniProject
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the server locally:

```bash
python app.py
```

## API Usage
1. Deposit
```bash
POST /accounts/<account_number>/deposit
Content-Type: application/json

{
  "amount": 50
}
```
2. Withdraw
```bash
POST /accounts/<account_number>/withdraw
Content-Type: application/json

{
  "amount": 30
}
```
3. Balance
```bash
GET /accounts/<account_number>/balance
```

## Deployment
The server is hosted on Render at:
https://atm-miniproject.onrender.com/

Notes
Flask runs with host="0.0.0.0" and port 5000.

The root URL (/) currently shows "Not Found"; the API is intended for programmatic access via endpoints.
