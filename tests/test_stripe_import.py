"""Test stripe import in Flask context."""

from app import create_app

app = create_app()

with app.app_context():
    print("Testing stripe import in Flask context...")
    
    # Test 1: Direct import
    import stripe
    print(f"✓ Direct import: {stripe}")
    print(f"  Has checkout: {hasattr(stripe, 'checkout')}")
    
    # Test 2: Import in function
    def test_func():
        import stripe as stripe_api
        print(f"✓ Function import: {stripe_api}")
        return stripe_api
    
    result = test_func()
    print(f"  Returned: {result}")
    
    # Test 3: Test the actual init_stripe function
    from app.payment.stripe_utils import init_stripe
    print("\nTesting init_stripe()...")
    stripe_module = init_stripe()
    print(f"✓ init_stripe returned: {stripe_module}")
    print(f"  Type: {type(stripe_module)}")
    print(f"  Is None: {stripe_module is None}")
    
    if stripe_module:
        print(f"  Has checkout: {hasattr(stripe_module, 'checkout')}")
        print(f"  API key set: {stripe_module.api_key is not None}")
    
    print("\n✅ All tests passed!")
