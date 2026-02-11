"""
Initialize database with Flask-Migrate and seed with sample data
Run this after: flask db init, flask db migrate, flask db upgrade
"""
from app import create_app
from models_sqlalchemy import db
from models_sqlalchemy.user import User
from models_sqlalchemy.models import (
    ProviderProfile, Product, Order, OrderItem, CartItem, SupportTicket, TicketResponse
)
from datetime import datetime, timedelta
import random

app = create_app()

def seed_database():
    """Seed database with sample data"""
    
    with app.app_context():
        print(" Starting database seeding...")
        print("=" * 60)
        
        # Clear existing data (optional - comment out if you want to keep data)
        print("Clearing existing data...")
        db.session.query(TicketResponse).delete()
        db.session.query(SupportTicket).delete()
        db.session.query(OrderItem).delete()
        db.session.query(Order).delete()
        db.session.query(CartItem).delete()
        db.session.query(Product).delete()
        db.session.query(ProviderProfile).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        # 1. Create Admin Users (2 admins with @gmail.com)
        print("\n Creating admin users...")
        
        admin1 = User(
            email='admin@gmail.com',
            role='admin',
            full_name='System Administrator',
            phone='+254700000001',
            is_active=True
        )
        admin1.set_password('Admin@2026')
        db.session.add(admin1)
        
        admin2 = User(
            email='blaire.admin@gmail.com',
            role='admin',
            full_name='Blaire Mwangi',
            phone='+254700000002',
            is_active=True
        )
        admin2.set_password('Admin@2026')
        db.session.add(admin2)
        
        db.session.commit()
        print(f" Created 2 admin users")
        
        # 2. Create Customer Users
        print("\n Creating customer users...")
        
        customers_data = [
            ('John Kamau', 'john.kamau@gmail.com', '+254712345678'),
            ('Mary Wanjiku', 'mary.wanjiku@gmail.com', '+254722345678'),
            ('David Omondi', 'david.omondi@gmail.com', '+254732345678'),
            ('Grace Achieng', 'grace.achieng@gmail.com', '+254742345678'),
            ('Peter Mwangi', 'peter.mwangi@gmail.com', '+254752345678'),
        ]
        
        customers = []
        for full_name, email, phone in customers_data:
            customer = User(
                email=email,
                role='customer',
                full_name=full_name,
                phone=phone,
                is_active=True
            )
            customer.set_password('Customer123')
            db.session.add(customer)
            customers.append(customer)
        
        db.session.commit()
        print(f" Created {len(customers_data)} customers")
        
        # 3. Create Provider Users
        print("\n Creating provider users...")
        
        providers_data = [
            ('Solar Energy Ltd', 'solar.energy@gmail.com', '+254762345678',
             'Leading provider of quality solar solutions in East Africa',
             '123 Kenyatta Avenue, Nairobi', 'PIN1234567890'),
            
            ('Bright Light Co', 'bright.light@gmail.com', '+254772345678',
             'Affordable and reliable solar lighting for every home',
             '456 Moi Avenue, Mombasa', 'PIN2234567890'),
            
            ('EcoPower Solutions', 'ecopower@gmail.com', '+254782345678',
             'Sustainable energy solutions for a brighter tomorrow',
             '789 Uhuru Street, Kisumu', 'PIN3234567890'),
            
            ('SunTech Kenya', 'suntech.kenya@gmail.com', '+254792345678',
             'Advanced solar technology at competitive prices',
             '321 Haile Selassie Ave, Nakuru', 'PIN4234567890'),
        ]
        
        providers = []
        for business_name, email, phone, description, address, tax_id in providers_data:
            provider = User(
                email=email,
                role='provider',
                full_name=business_name,
                phone=phone,
                is_active=True
            )
            provider.set_password('Provider123')
            db.session.add(provider)
            db.session.flush()  # Get provider ID
            
            # Create provider profile
            profile = ProviderProfile(
                user_id=provider.id,
                business_name=business_name,
                business_description=description,
                business_address=address,
                tax_id=tax_id,
                is_approved=True
            )
            db.session.add(profile)
            providers.append(provider)
        
        db.session.commit()
        print(f" Created {len(providers_data)} providers with profiles")
        
        # 4. Create Products
        print("\n Creating products...")
        
        products_data = [
            # Solar Energy Ltd products
            (providers[0].id, 'Solar LED Lantern 20W',
             'Bright and efficient 20W LED lantern with built-in solar panel. Perfect for outdoor camping or home use.',
             1500.00, 20, '6000mAh', 'Monocrystalline', '8-10 hours', '2 years', 50,
             'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400'),
            
            (providers[0].id, 'Solar Street Light 50W',
             'High-power 50W street light with motion sensor. Ideal for outdoor lighting and pathways.',
             4500.00, 50, '12000mAh', 'Polycrystalline', '12-14 hours', '3 years', 30,
             'https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400'),
            
            (providers[0].id, 'Portable Solar Charger 30W',
             'Compact solar charger for phones and tablets. Features dual USB ports.',
             2800.00, 30, '15000mAh', 'Monocrystalline', 'N/A', '1 year', 40,
             'https://images.unsplash.com/photo-1593642532400-2682810df593?w=400'),
            
            # Bright Light Co products
            (providers[1].id, 'Solar Table Lamp 10W',
             'Elegant solar table lamp perfect for reading. Adjustable brightness levels.',
             800.00, 10, '4000mAh', 'Monocrystalline', '6-8 hours', '1 year', 60,
             'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=400'),
            
            (providers[1].id, 'Solar Garden Light Set 5W',
             'Set of 4 decorative garden lights. Waterproof and weather-resistant.',
             1200.00, 5, '2000mAh', 'Amorphous', '8 hours', '1 year', 80,
             'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400'),
            
            (providers[1].id, 'Solar Camping Light 15W',
             'Versatile camping light with hook and magnet. Waterproof IPX6 rated.',
             1800.00, 15, '5000mAh', 'Polycrystalline', '10-12 hours', '2 years', 45,
             'https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400'),
            
            # EcoPower Solutions products
            (providers[2].id, 'Solar Home System 100W',
             'Complete home lighting system with 4 LED bulbs and mobile charging.',
             18500.00, 100, '40000mAh', 'Monocrystalline', '24+ hours', '5 years', 15,
             'https://images.unsplash.com/photo-1593642532400-2682810df593?w=400'),
            
            (providers[2].id, 'Solar Security Light 40W',
             'Motion-activated security light with wide-angle coverage.',
             3500.00, 40, '10000mAh', 'Monocrystalline', '10-12 hours', '2 years', 25,
             'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=400'),
            
            (providers[2].id, 'Solar Panel Kit 200W',
             'Professional-grade solar panel kit for off-grid applications.',
             25000.00, 200, None, 'Monocrystalline', 'N/A', '10 years', 10,
             'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400'),
            
            # SunTech Kenya products
            (providers[3].id, 'Solar Fan with Light 25W',
             'Multi-functional solar fan with LED light. Includes remote control.',
             3200.00, 25, '8000mAh', 'Polycrystalline', '8 hours', '2 years', 35,
             'https://images.unsplash.com/photo-1509391366360-2e959784a276?w=400'),
            
            (providers[3].id, 'Solar Floodlight 60W',
             'High-intensity floodlight for large outdoor areas. Waterproof construction.',
             5500.00, 60, '15000mAh', 'Monocrystalline', '12-15 hours', '3 years', 20,
             'https://images.unsplash.com/photo-1593642532400-2682810df593?w=400'),
            
            (providers[3].id, 'Solar Emergency Light 12W',
             'Compact emergency light with phone charging capability.',
             950.00, 12, '3500mAh', 'Monocrystalline', '6-8 hours', '1 year', 70,
             'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=400'),
        ]
        
        products = []
        for data in products_data:
            product = Product(
                provider_id=data[0],
                name=data[1],
                description=data[2],
                price=data[3],
                wattage=data[4],
                battery_capacity=data[5],
                solar_panel_type=data[6],
                lighting_duration=data[7],
                warranty_period=data[8],
                stock_quantity=data[9],
                image_url=data[10],
                is_active=True,
                is_approved=True
            )
            db.session.add(product)
            products.append(product)
        
        db.session.commit()
        print(f" Created {len(products_data)} products")
        
        # 5. Create Sample Orders
        print("\n Creating sample orders...")
        
        order_count = 0
        for customer in customers[:3]:  # First 3 customers
            for i in range(random.randint(2, 3)):
                order = Order(
                    customer_id=customer.id,
                    order_number=Order.generate_order_number(),
                    total_amount=random.randint(2000, 50000),
                    payment_method=random.choice(['mpesa', 'card', 'paypal']),
                    payment_status=random.choice(['completed', 'pending']),
                    order_status=random.choice(['pending', 'processing', 'completed']),
                    shipping_address='123 Main Street, Nairobi, Kenya',
                    phone_number=customer.phone,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(order)
                db.session.flush()
                
                # Add 1-3 items to order
                for _ in range(random.randint(1, 3)):
                    product = random.choice(products)
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=random.randint(1, 3),
                        price=product.price
                    )
                    db.session.add(order_item)
                
                order_count += 1
        
        db.session.commit()
        print(f" Created {order_count} orders")
        
        # 6. Create Sample Support Tickets
        print("\n Creating support tickets...")
        
        ticket_subjects = [
            'Product not working as expected',
            'Delivery delay inquiry',
            'Request for product installation guide',
            'Battery not charging properly',
            'Question about warranty coverage'
        ]
        
        ticket_count = 0
        orders = Order.query.limit(5).all()
        for order in orders:
            if random.random() > 0.5:
                ticket = SupportTicket(
                    customer_id=order.customer_id,
                    order_id=order.id,
                    ticket_number=SupportTicket.generate_ticket_number(),
                    subject=random.choice(ticket_subjects),
                    message=f"Hello, I have an issue with my order {order.order_number}. Please help.",
                    status='open'
                )
                db.session.add(ticket)
                ticket_count += 1
        
        db.session.commit()
        print(f" Created {ticket_count} support tickets")
        
        print("\n" + "=" * 60)
        print(" Database seeding completed successfully!")
        print("\n Summary:")
        print(f"   - 2 Admin users (with @gmail.com)")
        print(f"   - {len(customers)} Customers")
        print(f"   - {len(providers)} Providers")
        print(f"   - {len(products)} Products")
        print(f"   - {order_count} Orders")
        print(f"   - {ticket_count} Support Tickets")
        
        print("\n Test Accounts:")
        print("   Admin 1:  admin@gmail.com / Admin@2026")
        print("   Admin 2:  blaire.admin@gmail.com / Admin@2026")
        print("   Customer: john.kamau@gmail.com / Customer123")
        print("   Provider: solar.energy@gmail.com / Provider123")
        print("\n All users use @gmail.com addresses")

if __name__ == '__main__':
    seed_database()
