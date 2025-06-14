from app import db, User
from werkzeug.security import generate_password_hash

# Seed data
test_users = [
    {'username': 'testuser1', 'password': 'password123'},
    {'username': 'admin', 'password': 'adminpass'},
    {'username': 'shellcoach', 'password': 'linuxrocks'},
]

for user_data in test_users:
    existing = User.query.filter_by(username=user_data['username']).first()
    if not existing:
        new_user = User(
            username=user_data['username'],
            password=generate_password_hash(user_data['password'], method='sha256')
        )
        db.session.add(new_user)

db.session.commit()
print("✅ Seeded test users.")
