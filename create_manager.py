from app import create_app
from app.services.auth_service import create_user
from getpass import getpass
import sqlite3

app = create_app()

with app.app_context():

    name = input("Enter manager name: ")
    email = input("Enter manager email: ")
    password = getpass("Enter manager password: ")
    confirm_password = getpass("Confirm password: ")

    if password != confirm_password:
        print("Passwords do not match!")

    else:
        try:
            create_user(name, email, password, "manager")
            print("Manager account created successfully!")

        except sqlite3.IntegrityError:
            print("This email is already registered.")