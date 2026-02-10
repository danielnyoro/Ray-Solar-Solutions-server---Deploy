"""
Provider routes - Profile, Products, Support
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models_sqlalchemy import db
from models_sqlalchemy.user import User
from models_sqlalchemy.models import ProviderProfile, Product, SupportTicket, TicketResponse
from middleware.auth import role_required

provider_bp = Blueprint('provider', __name__)

# ============== PROVIDER PROFILE ==============

@provider_bp.route('/profile', methods=['GET'])
@role_required('provider')
def get_profile():
    """Get provider profile"""
    try:
        user_id = get_jwt_identity()
        
        profile = ProviderProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return jsonify({'message': 'No profile found'}), 404
        
        return jsonify({'profile': profile.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@provider_bp.route('/profile', methods=['POST'])
@role_required('provider')
def create_profile():
    """Create provider profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check if profile already exists
        existing_profile = ProviderProfile.query.filter_by(user_id=user_id).first()
        if existing_profile:
            return jsonify({'error': 'Profile already exists'}), 400
        
        # Validate required fields
        required_fields = ['business_name', 'business_description', 'business_address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create profile
        profile = ProviderProfile(
            user_id=user_id,
            business_name=data['business_name'],
            business_description=data['business_description'],
            business_address=data['business_address'],
            tax_id=data.get('tax_id'),
            is_approved=False
        )
        
        db.session.add(profile)
        db.session.commit()
        
        return jsonify({
            'message': 'Profile created successfully',
            'profile': profile.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@provider_bp.route('/profile', methods=['PUT'])
@role_required('provider')
def update_profile():
    """Update provider profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        profile = ProviderProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Update fields
        if data.get('business_name'):
            profile.business_name = data['business_name']
        if data.get('business_description'):
            profile.business_description = data['business_description']
        if data.get('business_address'):
            profile.business_address = data['business_address']
        if data.get('tax_id'):
            profile.tax_id = data['tax_id']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': profile.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== PRODUCT MANAGEMENT ==============

@provider_bp.route('/products', methods=['GET'])
@role_required('provider')
def get_products():
    """Get provider's products"""
    try:
        user_id = get_jwt_identity()
        
        products = Product.query.filter_by(provider_id=user_id).all()
        
        return jsonify({
            'products': [p.to_dict() for p in products],
            'total': len(products)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@provider_bp.route('/products', methods=['POST'])
@role_required('provider')
def add_product():
    """Add new product"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Check if provider profile is approved
        profile = ProviderProfile.query.filter_by(user_id=user_id).first()
        if not profile or not profile.is_approved:
            return jsonify({'error': 'Provider profile must be approved first'}), 403
        
        # Validate required fields
        required_fields = ['name', 'description', 'price']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create product
        product = Product(
            provider_id=user_id,
            name=data['name'],
            description=data['description'],
            price=data['price'],
            wattage=data.get('wattage'),
            battery_capacity=data.get('battery_capacity'),
            solar_panel_type=data.get('solar_panel_type'),
            lighting_duration=data.get('lighting_duration'),
            warranty_period=data.get('warranty_period'),
            stock_quantity=data.get('stock_quantity', 0),
            image_url=data.get('image_url'),
            is_active=True,
            is_approved=False
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'message': 'Product added successfully',
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@provider_bp.route('/products/<int:product_id>', methods=['GET'])
@role_required('provider')
def get_product(product_id):
    """Get product details"""
    try:
        user_id = get_jwt_identity()
        
        product = Product.query.get(product_id)
        
        if not product or product.provider_id != user_id:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({'product': product.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@provider_bp.route('/products/<int:product_id>', methods=['PUT'])
@role_required('provider')
def update_product(product_id):
    """Update product"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        product = Product.query.get(product_id)
        
        if not product or product.provider_id != user_id:
            return jsonify({'error': 'Product not found'}), 404
        
        # Update fields
        updateable_fields = [
            'name', 'description', 'price', 'wattage', 'battery_capacity',
            'solar_panel_type', 'lighting_duration', 'warranty_period',
            'stock_quantity', 'image_url', 'is_active'
        ]
        
        for field in updateable_fields:
            if field in data:
                setattr(product, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@provider_bp.route('/products/<int:product_id>', methods=['DELETE'])
@role_required('provider')
def delete_product(product_id):
    """Delete product"""
    try:
        user_id = get_jwt_identity()
        
        product = Product.query.get(product_id)
        
        if not product or product.provider_id != user_id:
            return jsonify({'error': 'Product not found'}), 404
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== SUPPORT TICKETS ==============

@provider_bp.route('/tickets', methods=['GET'])
@role_required('provider')
def get_tickets():
    """Get all open support tickets"""
    try:
        tickets = SupportTicket.query.filter_by(status='open').all()
        
        tickets_data = []
        for ticket in tickets:
            ticket_dict = ticket.to_dict()
            ticket_dict['responses'] = [r.to_dict() for r in ticket.responses]
            tickets_data.append(ticket_dict)
        
        return jsonify({'tickets': tickets_data}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@provider_bp.route('/tickets/<int:ticket_id>/respond', methods=['POST'])
@role_required('provider')
def respond_to_ticket(ticket_id):
    """Respond to support ticket"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('message'):
            return jsonify({'error': 'Message is required'}), 400
        
        ticket = SupportTicket.query.get(ticket_id)
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Add response
        response = TicketResponse(
            ticket_id=ticket_id,
            responder_id=user_id,
            message=data['message']
        )
        
        db.session.add(response)
        
        # Mark as resolved if requested
        if data.get('resolve'):
            ticket.status = 'resolved'
        
        db.session.commit()
        
        return jsonify({'message': 'Response added successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== ANALYTICS ==============

@provider_bp.route('/analytics', methods=['GET'])
@role_required('provider')
def get_analytics():
    """Get provider analytics"""
    try:
        user_id = get_jwt_identity()
        
        total_products = Product.query.filter_by(provider_id=user_id).count()
        approved_products = Product.query.filter_by(
            provider_id=user_id,
            is_approved=True
        ).count()
        
        return jsonify({
            'analytics': {
                'total_products': total_products,
                'approved_products': approved_products,
                'pending_products': total_products - approved_products
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
