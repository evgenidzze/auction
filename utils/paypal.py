import requests

from utils.config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET



async def get_access_token():
    url = "https://api-m.paypal.com/v1/oauth2/token"  # Ось тут додано '/v1/oauth2/token'
    data = {
        "grant_type": "client_credentials"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET), headers=headers, data=data)
    access_token = response.json()["access_token"]
    return access_token


async def create_payment_token():
    access_token = await get_access_token()
    url = "https://api-m.paypal.com/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": "5.00"
                }
            }
        ],
        "application_context": {
            "brand_name": "Your Brand Name",
            "landing_page": "BILLING",
            "user_action": "PAY_NOW",
            "return_url": "https://paypal.com"
        }
    }

    response = requests.post(url, headers=headers, json=data)

    token = response.json().get('id')
    return token


#
async def capture(order_id):
    access_token = await get_access_token()
    capture_url = f"https://api-m.paypal.com/v2/checkout/orders/{order_id}/capture"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    requests.post(capture_url, headers=headers)


async def get_status(order_id):
    access_token = await get_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"https://api-m.paypal.com/v2/checkout/orders/{order_id}", headers=headers)
    order_status = response.json().get('status')
    return order_status

