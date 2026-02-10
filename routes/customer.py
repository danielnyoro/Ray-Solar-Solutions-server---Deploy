"""
Customer routes - Products, Cart, Checkout, Orders, Support
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models_sqlalchemy import db
from models_sqlalchemy.user import User
from models_sqlalchemy.models import (
    Product, CartItem, Order, OrderItem, SupportTicket
)
from services.mpesa_service import mpesa_service
from middleware.auth import role_required

customer_bp = Blueprint('customer', __name__)

# ============== PRODUCTS ==============

@customer_bp.route('/products', methods=['GET'])
@role_required('customer')
def browse_products():
    """Browse approved products with filters"""
    try:
        # Get query parameters
        search = request.args.get('search', '').strip()
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        min_wattage = request.args.get('min_wattage', type=int)
        max_wattage = request.args.get('max_wattage', type=int)
        
        # Base query - only approved and active products
        query = Product.query.filter_by(is_active=True, is_approved=True)
        
        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    Product.name.ilike(f'%{search}%'),
                    Product.description.ilike(f'%{search}%')
                )
            )
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        if min_wattage is not None:
            query = query.filter(Product.wattage >= min_wattage)
        
        if max_wattage is not None:
            query = query.filter(Product.wattage <= max_wattage)
        
        products = query.all()
        
        return jsonify({
            'products': [p.to_dict() for p in products],
            'total': len(products)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/products/<int:product_id>', methods=['GET'])
@role_required('customer')
def get_product(product_id):
    """Get product details"""
    try:
        product = Product.query.get(product_id)
        
        if not product or not product.is_active or not product.is_approved:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({'product': product.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== SHOPPING CART ==============

@customer_bp.route('/cart', methods=['GET'])
@role_required('customer')
def get_cart():
    """Get customer's cart"""
    try:
        user_id = get_jwt_identity()
        
        cart_items = CartItem.query.filter_by(customer_id=user_id).all()
        
        items = []
        subtotal = 0
        
        for item in cart_items:
            item_dict = item.to_dict()
            items.append(item_dict)
            if item.product:
                subtotal += item.product.price * item.quantity
        
        return jsonify({
            'items': items,
            'subtotal': subtotal,
            'item_count': len(items)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/cart/add', methods=['POST'])
@role_required('customer')
def add_to_cart():
    """Add product to cart"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('product_id'):
            return jsonify({'error': 'product_id is required'}), 400
        
        quantity = data.get('quantity', 1)
        
        # Validate product
        product = Product.query.get(data['product_id'])
        if not product or not product.is_active or not product.is_approved:
            return jsonify({'error': 'Product not available'}), 404
        
        # Check stock
        if product.stock_quantity < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        # Check if item already in cart
        cart_item = CartItem.query.filter_by(
            customer_id=user_id,
            product_id=data['product_id']
        ).first()
        
        if cart_item:
            # Update quantity
            cart_item.quantity += quantity
        else:
            # Add new item
            cart_item = CartItem(
                customer_id=user_id,
                product_id=data['product_id'],
                quantity=quantity
            )
            db.session.add(cart_item)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product added to cart',
            'cart_item': cart_item.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/cart/update/<int:item_id>', methods=['PUT'])
@role_required('customer')
def update_cart_item(item_id):
    """Update cart item quantity"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        cart_item = CartItem.query.get(item_id)
        
        if not cart_item or cart_item.customer_id != user_id:
            return jsonify({'error': 'Cart item not found'}), 404
        
        quantity = data.get('quantity', 1)
        
        # Validate stock
        if cart_item.product and cart_item.product.stock_quantity < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        cart_item.quantity = quantity
        db.session.commit()
        
        return jsonify({
            'message': 'Cart updated',
            'cart_item': cart_item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/cart/remove/<int:item_id>', methods=['DELETE'])
@role_required('customer')
def remove_from_cart(item_id):
    """Remove item from cart"""
    try:
        user_id = get_jwt_identity()
        
        cart_item = CartItem.query.get(item_id)
        
        if not cart_item or cart_item.customer_id != user_id:
            return jsonify({'error': 'Cart item not found'}), 404
        
        db.session.delete(cart_item)
        db.session.commit()
        
        return jsonify({'message': 'Item removed from cart'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/cart/clear', methods=['DELETE'])
@role_required('customer')
def clear_cart():
    """Clear entire cart"""
    try:
        user_id = get_jwt_identity()
        
        CartItem.query.filter_by(customer_id=user_id).delete()
        db.session.commit()
        
        return jsonify({'message': 'Cart cleared'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== CHECKOUT & ORDERS ==============

@customer_bp.route('/checkout', methods=['POST'])
@role_required('customer')
def checkout():
    """Process checkout with M-PESA integration"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['payment_method', 'shipping_address', 'phone_number']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Get cart items
        cart_items = CartItem.query.filter_by(customer_id=user_id).all()
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Validate stock
        for item in cart_items:
            if not item.product or not item.product.is_active:
                return jsonify({'error': f'Product unavailable'}), 400
            
            if item.product.stock_quantity < item.quantity:
                return jsonify({'error': f'Insufficient stock for {item.product.name}'}), 400
        
        # Calculate total
        subtotal = sum(item.product.price * item.quantity for item in cart_items)
        shipping = 1000
        tax = subtotal * 0.01
        total = subtotal + shipping + tax
        
        # Create order
        order = Order(
            customer_id=user_id,
            order_number=Order.generate_order_number(),
            total_amount=total,
            payment_method=data['payment_method'],
            shipping_address=data['shipping_address'],
            phone_number=data['phone_number'],
            payment_status='pending',
            order_status='pending'
        )
        
        db.session.add(order)
        db.session.flush()
        
        # Add order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        # Process M-PESA payment
        if data['payment_method'] == 'mpesa':
            mpesa_result = mpesa_service.initiate_stk_push(
                phone_number=data['phone_number'],
                amount=total,
                account_reference=order.order_number,
                transaction_desc=f"Payment for Order {order.order_number}"
            )
            
            if mpesa_result['success']:
                order.mpesa_checkout_request_id = mpesa_result.get('checkout_request_id')
                order.mpesa_merchant_request_id = mpesa_result.get('merchant_request_id')
                db.session.commit()
                
                # Clear cart
                CartItem.query.filter_by(customer_id=user_id).delete()
                db.session.commit()
                
                return jsonify({
                    'message': 'M-PESA payment initiated. Check your phone.',
                    'order': order.to_dict(),
                    'mpesa': {
                        'checkout_request_id': mpesa_result.get('checkout_request_id'),
                        'customer_message': mpesa_result.get('customer_message')
                    }
                }), 201
            else:
                order.payment_status = 'failed'
                db.session.commit()
                
                return jsonify({
                    'error': 'M-PESA payment failed',
                    'details': mpesa_result.get('error')
                }), 400
        
        else:
            # Other payment methods
            order.payment_status = 'completed'
            order.order_status = 'processing'
            db.session.commit()
            
            # Clear cart
            CartItem.query.filter_by(customer_id=user_id).delete()
            db.session.commit()
            
            return jsonify({
                'message': 'Order placed successfully',
                'order': order.to_dict()
            }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/orders', methods=['GET'])
@role_required('customer')
def get_orders():
    """Get customer's order history"""
    try:
        user_id = get_jwt_identity()
        
        orders = Order.query.filter_by(customer_id=user_id)\
            .order_by(Order.created_at.desc()).all()
        
        orders_data = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['items'] = [item.to_dict() for item in order.order_items]
            orders_data.append(order_dict)
        
        return jsonify({'orders': orders_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/orders/<int:order_id>', methods=['GET'])
@role_required('customer')
def get_order(order_id):
    """Get order details"""
    try:
        user_id = get_jwt_identity()
        
        order = Order.query.get(order_id)
        
        if not order or order.customer_id != user_id:
            return jsonify({'error': 'Order not found'}), 404
        
        order_dict = order.to_dict()
        order_dict['items'] = [item.to_dict() for item in order.order_items]
        
        return jsonify({'order': order_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============== SUPPORT TICKETS ==============

@customer_bp.route('/tickets', methods=['GET'])
@role_required('customer')
def get_tickets():
    """Get customer's support tickets"""
    try:
        user_id = get_jwt_identity()
        
        tickets = SupportTicket.query.filter_by(customer_id=user_id)\
            .order_by(SupportTicket.created_at.desc()).all()
        
        tickets_data = []
        for ticket in tickets:
            ticket_dict = ticket.to_dict()
            ticket_dict['responses'] = [r.to_dict() for r in ticket.responses]
            tickets_data.append(ticket_dict)
        
        return jsonify({'tickets': tickets_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/tickets', methods=['POST'])
@role_required('customer')
def create_ticket():
    """Create support ticket"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('subject') or not data.get('message'):
            return jsonify({'error': 'Subject and message are required'}), 400
        
        order_id = data.get('order_id')
        if order_id:
            order = Order.query.get(order_id)
            if not order or order.customer_id != user_id:
                return jsonify({'error': 'Invalid order'}), 400
        
        ticket = SupportTicket(
            customer_id=user_id,
            order_id=order_id,
            ticket_number=SupportTicket.generate_ticket_number(),
            subject=data['subject'],
            message=data['message'],
            status='open'
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify({
            'message': 'Support ticket created',
            'ticket': ticket.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
@role_required('customer')
def get_ticket(ticket_id):
    """Get ticket details with responses"""
    try:
        user_id = get_jwt_identity()
        
        ticket = SupportTicket.query.get(ticket_id)
        
        if not ticket or ticket.customer_id != user_id:
            return jsonify({'error': 'Ticket not found'}), 404
        
        ticket_dict = ticket.to_dict()
        ticket_dict['responses'] = [r.to_dict() for r in ticket.responses]
        
        return jsonify({'ticket': ticket_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
