"""
Admin routes - Provider approval, Product approval, User management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models_sqlalchemy import db
from models_sqlalchemy.user import User
from models_sqlalchemy.models import ProviderProfile, Product, Order
from middleware.auth import role_required

admin_bp = Blueprint('admin', __name__)

# ============== PROVIDER MANAGEMENT ==============

@admin_bp.route('/providers/pending', methods=['GET'])
@role_required('admin')
def get_pending_providers():
    """Get all pending provider profiles"""
    try:
        providers = ProviderProfile.query.filter_by(is_approved=False).all()
        
        providers_data = []
        for provider in providers:
            provider_dict = provider.to_dict()
            user = User.query.get(provider.user_id)
            if user:
                provider_dict['user_email'] = user.email
                provider_dict['user_name'] = user.full_name
            providers_data.append(provider_dict)
        
        return jsonify({'providers': providers_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/providers/approved', methods=['GET'])
@role_required('admin')
def get_approved_providers():
    """Get all approved provider profiles"""
    try:
        providers = ProviderProfile.query.filter_by(is_approved=True).all()
        
        providers_data = []
        for provider in providers:
            provider_dict = provider.to_dict()
            user = User.query.get(provider.user_id)
            if user:
                provider_dict['user_email'] = user.email
                provider_dict['user_name'] = user.full_name
            providers_data.append(provider_dict)
        
        return jsonify({'providers': providers_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/providers/<int:provider_id>/approve', methods=['PUT'])
@role_required('admin')
def approve_provider(provider_id):
    """Approve a provider profile"""
    try:
        provider = ProviderProfile.query.get(provider_id)
        
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404
        
        provider.is_approved = True
        db.session.commit()
        
        return jsonify({
            'message': 'Provider approved successfully',
            'provider': provider.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/providers/<int:provider_id>/reject', methods=['PUT'])
@role_required('admin')
def reject_provider(provider_id):
    """Reject a provider profile"""
    try:
        provider = ProviderProfile.query.get(provider_id)
        
        if not provider:
            return jsonify({'error': 'Provider not found'}), 404
        
        provider.is_approved = False
        db.session.commit()
        
        return jsonify({
            'message': 'Provider rejected',
            'provider': provider.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== PRODUCT MANAGEMENT ==============

@admin_bp.route('/products/pending', methods=['GET'])
@role_required('admin')
def get_pending_products():
    """Get all pending products"""
    try:
        products = Product.query.filter_by(is_approved=False).all()
        
        products_data = []
        for product in products:
            product_dict = product.to_dict()
            user = User.query.get(product.provider_id)
            if user:
                product_dict['provider_name'] = user.full_name
            products_data.append(product_dict)
        
        return jsonify({'products': products_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/all', methods=['GET'])
@role_required('admin')
def get_all_products():
    """Get all products"""
    try:
        products = Product.query.all()
        
        products_data = []
        for product in products:
            product_dict = product.to_dict()
            user = User.query.get(product.provider_id)
            if user:
                product_dict['provider_name'] = user.full_name
            products_data.append(product_dict)
        
        return jsonify({'products': products_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:product_id>/approve', methods=['PUT'])
@role_required('admin')
def approve_product(product_id):
    """Approve a product"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        product.is_approved = True
        db.session.commit()
        
        return jsonify({
            'message': 'Product approved successfully',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/products/<int:product_id>/reject', methods=['PUT'])
@role_required('admin')
def reject_product(product_id):
    """Reject a product"""
    try:
        product = Product.query.get(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        product.is_approved = False
        db.session.commit()
        
        return jsonify({
            'message': 'Product rejected',
            'product': product.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== USER MANAGEMENT ==============

@admin_bp.route('/users', methods=['GET'])
@role_required('admin')
def get_users():
    """Get all users"""
    try:
        role_filter = request.args.get('role')
        
        if role_filter:
            users = User.query.filter_by(role=role_filter).all()
        else:
            users = User.query.all()
        
        return jsonify({
            'users': [user.to_dict() for user in users],
            'total': len(users)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/activate', methods=['PUT'])
@role_required('admin')
def activate_user(user_id):
    """Activate a user"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_active = True
        db.session.commit()
        
        return jsonify({
            'message': 'User activated',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/deactivate', methods=['PUT'])
@role_required('admin')
def deactivate_user(user_id):
    """Deactivate a user"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.role == 'admin':
            return jsonify({'error': 'Cannot deactivate admin users'}), 403
        
        user.is_active = False
        db.session.commit()
        
        return jsonify({
            'message': 'User deactivated',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============== ANALYTICS ==============

@admin_bp.route('/analytics', methods=['GET'])
@role_required('admin')
def get_analytics():
    """Get platform analytics"""
    try:
        total_users = User.query.count()
        total_customers = User.query.filter_by(role='customer').count()
        total_providers = User.query.filter_by(role='provider').count()
        total_products = Product.query.count()
        approved_products = Product.query.filter_by(is_approved=True).count()
        total_orders = Order.query.count()
        
        # Calculate total revenue
        orders = Order.query.filter_by(payment_status='completed').all()
        total_revenue = sum(order.total_amount for order in orders)
        
        return jsonify({
            'analytics': {
                'total_users': total_users,
                'total_customers': total_customers,
                'total_providers': total_providers,
                'total_products': total_products,
                'approved_products': approved_products,
                'pending_products': total_products - approved_products,
                'total_orders': total_orders,
                'total_revenue': float(total_revenue)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
