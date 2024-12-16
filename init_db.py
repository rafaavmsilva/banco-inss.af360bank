from app import create_app, db, User

app = create_app()

with app.app_context():
    db.create_all()
    
    # Create a test user if it doesn't exist
    test_user = User.query.filter_by(username='admin').first()
    if not test_user:
        test_user = User(
            username='admin',
            password='admin123'  # In production, use proper password hashing
        )
        db.session.add(test_user)
        db.session.commit()
        print("Test user created successfully!")
    
    print("Database tables created successfully!")
