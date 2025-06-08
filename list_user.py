from src.main import create_app, db
from src.models.user import User

def list_all_users():
    app = create_app()
    
    with app.app_context():
        users = User.query.all()
        print(f"Total users: {len(users)}")
        print("ID | Username | Email | Has Keys")
        print("--------------------------------")
        for user in users:
            has_keys = "Yes" if user.private_key_encrypted is not None else "No"
            print(f"{user.id} | {user.username} | {user.email} | {has_keys}")

if __name__ == "__main__":
    list_all_users()