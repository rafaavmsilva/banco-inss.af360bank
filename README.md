# BMP Bank API Integration

This Flask application provides a REST API interface to interact with BMP Bank's APIs.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
   - Rename `.env.example` to `.env`
   - Add your BMP API key to the `.env` file

3. Run the application:
```bash
python app.py
```

## Available Endpoints

### Health Check
- GET `/health`
  - Check if the service is running

### Account Balance
- GET `/account/balance`
  - Retrieve account balance

### Transfer
- POST `/transfer`
  - Make a bank transfer
  - Required JSON body:
    ```json
    {
        "destination_account": "account_number",
        "amount": 100.00,
        "description": "Transfer description"
    }
    ```

### Statement
- GET `/statement`
  - Get account statement
  - Query parameters:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)

## Security
- API keys and sensitive information are stored in environment variables
- CORS is enabled for cross-origin requests
- All requests to BMP APIs are made with proper authentication
