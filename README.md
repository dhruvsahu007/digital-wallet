# FastAPI Wallet API

This is a simple FastAPI application for managing user wallets and transactions.

## Installation

1. Clone the repository
2. Create a virtual environment
3. Install the dependencies

```bash
pip install -r requirements.txt
```
## Running the application

```bash
uvicorn main:app --reload
```

## Endpoints

### User Management

- `POST /users/`: Create a new user
- `GET /users/{user_id}`: Get user details
- `PUT /users/{user_id}`: Update user details

### Wallet Management

- `GET /wallet/{user_id}/balance`: Get wallet balance
- `POST /wallet/{user_id}/add-money`: Add money to wallet
- `POST /wallet/{user_id}/withdraw`: Withdraw money from wallet

### Transaction History

- `GET /transactions/{user_id}?page=1&limit=10`: Get transaction history
- `GET /transactions/detail/{transaction_id}`: Get transaction details
- `POST /transactions`: Create a new transaction

### Fund Transfer

- `GET /transfer/{transfer_id}`: Get transfer details

