from sqlmodel import Session, create_engine, select
from models import User, Screen
from database import DATABASE_URL
import random

# Ensure we are using the postgres driver if the URL is for postgres
if "postgres://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

engine = create_engine(DATABASE_URL)

def create_dummy_users():
    with Session(engine) as session:
        print("Creating 10 dummy users...")
        for i in range(10):
            user = User(
                state=random.choice([0, 1, 2]),
                group_id=random.randint(1, 5),
                thrower=random.choice([None, 1, 2, 3])
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            
            # Create associated screen
            screen = Screen(user_id=user.id)
            session.add(screen)
            session.commit()
            
            print(f"Created user {user.id} with state {user.state}")
            
if __name__ == "__main__":
    create_dummy_users()

