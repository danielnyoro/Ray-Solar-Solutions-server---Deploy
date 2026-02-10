"""
M-PESA STK Push Integration Service
Handles M-PESA Lipa Na M-PESA Online payments
"""

import requests
import base64
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class MPesaService:
    """M-PESA Daraja API Integration"""
    
    def __init__(self):
        # M-PESA Credentials from environment
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY', '')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET', '')
        self.business_shortcode = os.getenv('MPESA_SHORTCODE', '174379')
        self.passkey = os.getenv('MPESA_PASSKEY', '')
        self.callback_url = os.getenv('MPESA_CALLBACK_URL', 'https://yourdomain.com/api/mpesa/callback')
        
        # API URLs (Sandbox - change to production URLs in production)
        self.environment = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
        
        if self.environment == 'production':
            self.auth_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
            self.stk_push_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            self.query_url = "https://api.safaricom.co.ke/mpesa/stkpushquery/v1/query"
        else:
            self.auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
            self.stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            self.query_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
    
    def get_access_token(self):
        """Get OAuth access token from Safaricom API"""
        try:
            auth_string = f"{self.consumer_key}:{self.consumer_secret}"
            encoded = base64.b64encode(auth_string.encode()).decode('utf-8')
            
            headers = {
                "Authorization": f"Basic {encoded}"
            }
            
            response = requests.get(self.auth_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            json_response = response.json()
            return json_response.get('access_token')
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
    
    def generate_password(self, timestamp):
        """Generate password for STK Push"""
        password_string = f"{self.business_shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode('utf-8')
        return password
    
    def initiate_stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """
        Initiate STK Push to customer's phone
        
        Args:
            phone_number: Customer phone number (format: 254XXXXXXXXX)
            amount: Amount to charge
            account_reference: Order number or reference
            transaction_desc: Description of transaction
            
        Returns:
            dict: Response from M-PESA API
        """
        try:
            # Get access token
            access_token = self.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'error': 'Failed to get access token'
                }
            
            # Format phone number
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif phone_number.startswith('+'):
                phone_number = phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self.generate_password(timestamp)
            
            # Prepare request headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Prepare request payload
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc
            }
            
            # Make request
            response = requests.post(
                self.stk_push_url, 
                json=payload, 
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            json_response = response.json()
            
            # Check response
            if json_response.get('ResponseCode') == '0':
                return {
                    'success': True,
                    'checkout_request_id': json_response.get('CheckoutRequestID'),
                    'merchant_request_id': json_response.get('MerchantRequestID'),
                    'response_code': json_response.get('ResponseCode'),
                    'response_description': json_response.get('ResponseDescription'),
                    'customer_message': json_response.get('CustomerMessage')
                }
            else:
                return {
                    'success': False,
                    'error': json_response.get('ResponseDescription', 'Unknown error'),
                    'response_code': json_response.get('ResponseCode')
                }
                
        except requests.exceptions.RequestException as e:
            print(f"Error initiating STK push: {e}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def query_transaction_status(self, checkout_request_id):
        """
        Query the status of a transaction
        
        Args:
            checkout_request_id: CheckoutRequestID from STK push response
            
        Returns:
            dict: Transaction status
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {
                    'success': False,
                    'error': 'Failed to get access token'
                }
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self.generate_password(timestamp)
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            response = requests.post(
                self.query_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Error querying transaction: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Singleton instance
mpesa_service = MPesaService()
