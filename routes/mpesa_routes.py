"""
M-PESA integration routes
Handles M-PESA STK Push and callbacks
"""
from flask import Blueprint, request, jsonify
from models_sqlalchemy import db
from models_sqlalchemy.models import Order
from services.mpesa_service import mpesa_service
from datetime import datetime

mpesa_bp = Blueprint('mpesa', __name__)

@mpesa_bp.route('/callback', methods=['POST'])
def mpesa_callback():
    """
    M-PESA callback endpoint
    Safaricom calls this endpoint after payment is processed
    """
    try:
        data = request.get_json()
        print("=" * 60)
        print("M-PESA CALLBACK RECEIVED:")
        print(data)
        print("=" * 60)
        
        # Extract callback data
        callback_body = data.get('Body', {}).get('stkCallback', {})
        
        result_code = callback_body.get('ResultCode')
        result_desc = callback_body.get('ResultDesc')
        merchant_request_id = callback_body.get('MerchantRequestID')
        checkout_request_id = callback_body.get('CheckoutRequestID')
        
        # Find order by checkout_request_id
        order = Order.query.filter_by(mpesa_checkout_request_id=checkout_request_id).first()
        
        if not order:
            print(f"Order not found for CheckoutRequestID: {checkout_request_id}")
            return jsonify({
                'ResultCode': 0,
                'ResultDesc': 'Success'
            }), 200
        
        # Payment successful
        if result_code == 0:
            # Extract callback metadata
            callback_metadata = callback_body.get('CallbackMetadata', {}).get('Item', [])
            
            # Parse metadata
            amount = None
            receipt_number = None
            transaction_date = None
            phone_number = None
            
            for item in callback_metadata:
                name = item.get('Name')
                value = item.get('Value')
                
                if name == 'Amount':
                    amount = value
                elif name == 'MpesaReceiptNumber':
                    receipt_number = value
                elif name == 'TransactionDate':
                    # Format: 20231215143022
                    transaction_date = datetime.strptime(str(value), '%Y%m%d%H%M%S')
                elif name == 'PhoneNumber':
                    phone_number = value
            
            # Update order
            order.payment_status = 'completed'
            order.order_status = 'processing'
            order.mpesa_receipt_number = receipt_number
            order.mpesa_transaction_date = transaction_date
            order.mpesa_phone_number = phone_number
            
            db.session.commit()
            
            print(f"✅ Payment successful for order {order.order_number}")
            print(f"   Receipt: {receipt_number}")
            print(f"   Amount: {amount}")
            
        else:
            # Payment failed
            order.payment_status = 'failed'
            order.order_status = 'cancelled'
            db.session.commit()
            
            print(f"❌ Payment failed for order {order.order_number}")
            print(f"   Reason: {result_desc}")
        
        # Always return success to M-PESA
        return jsonify({
            'ResultCode': 0,
            'ResultDesc': 'Success'
        }), 200
        
    except Exception as e:
        print(f"Error processing M-PESA callback: {e}")
        # Still return success to M-PESA to avoid retries
        return jsonify({
            'ResultCode': 0,
            'ResultDesc': 'Success'
        }), 200

@mpesa_bp.route('/query/<checkout_request_id>', methods=['GET'])
def query_payment(checkout_request_id):
    """
    Query M-PESA payment status
    """
    try:
        result = mpesa_service.query_transaction_status(checkout_request_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
