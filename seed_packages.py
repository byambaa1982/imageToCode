"""
Seed packages table with default pricing packages.
Run this script after database migrations to populate the packages table.
"""

from app import create_app
from app.extensions import db
from app.models import Package
from datetime import datetime


def seed_packages():
    """Seed the packages table with default packages."""
    app = create_app()
    
    with app.app_context():
        # Check if packages already exist
        existing_packages = Package.query.count()
        if existing_packages > 0:
            print(f"⚠️  Packages table already has {existing_packages} records.")
            response = input("Do you want to delete existing packages and reseed? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Seeding cancelled.")
                return
            
            # Delete existing packages
            Package.query.delete()
            db.session.commit()
            print("✅ Deleted existing packages.")
        
        # Define default packages
        packages = [
            {
                'name': 'Starter Pack',
                'code': 'starter_pack',
                'description': '2 additional conversions',
                'price': 1.99,
                'credits': 2.00,
                'is_active': True,
                'is_featured': False,
                'display_order': 1,
                'badge': None
            },
            {
                'name': 'Pro Pack',
                'code': 'pro_pack',
                'description': '3 conversions - Best Value!',
                'price': 2.49,
                'credits': 3.00,
                'is_active': True,
                'is_featured': True,
                'display_order': 2,
                'badge': 'Most Popular'
            },
            {
                'name': 'Bulk Pack',
                'code': 'bulk_pack',
                'description': '10 conversions for power users',
                'price': 7.99,
                'credits': 10.00,
                'is_active': True,
                'is_featured': False,
                'display_order': 3,
                'badge': 'Best Value'
            }
        ]
        
        # Create and add packages
        for pkg_data in packages:
            package = Package(**pkg_data)
            db.session.add(package)
            print(f"➕ Adding package: {pkg_data['name']} (${pkg_data['price']} for {pkg_data['credits']} credits)")
        
        # Commit all packages
        db.session.commit()
        
        print("\n✅ Successfully seeded packages table!")
        print(f"📦 Total packages created: {len(packages)}")
        
        # Display summary
        print("\n📋 Package Summary:")
        print("-" * 80)
        all_packages = Package.query.order_by(Package.display_order).all()
        for pkg in all_packages:
            per_credit = float(pkg.price) / float(pkg.credits)
            featured = " [FEATURED]" if pkg.is_featured else ""
            badge = f" [{pkg.badge}]" if pkg.badge else ""
            print(f"  • {pkg.name}{featured}{badge}")
            print(f"    Code: {pkg.code}")
            print(f"    Price: ${pkg.price:.2f} for {int(pkg.credits)} credits")
            print(f"    Per Credit: ${per_credit:.2f}")
            print(f"    Status: {'Active' if pkg.is_active else 'Inactive'}")
            print()


if __name__ == '__main__':
    try:
        seed_packages()
    except Exception as e:
        print(f"❌ Error seeding packages: {str(e)}")
        import traceback
        traceback.print_exc()
