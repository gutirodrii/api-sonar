from sqlmodel import Session, create_engine, select
from models import User, Screen, Pulsera
from database import DATABASE_URL
import random

# Ensure we are using the postgres driver if the URL is for postgres
if "postgres://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

engine = create_engine(DATABASE_URL)

def create_dummy_users():
    with Session(engine) as session:
        print("Creating 10 dummy pulseras and users...")
        for i in range(10):
            pulsera_id = f"SEED{i:04d}"
            # Create pulsera if it doesn't exist
            if not session.get(Pulsera, pulsera_id):
                session.add(Pulsera(id=pulsera_id))
                session.commit()

            # Alternating group_id
            last_user = session.exec(select(User).order_by(User.id.desc())).first()
            if last_user is None or last_user.group_id == 2:
                next_group_id = 1
            else:
                next_group_id = 2

            user = User(
                pulsera_id=pulsera_id,
                state=random.choice([0, 1, 2]),
                group_id=next_group_id,
                thrower=random.choice([None, 1, 2, 3]),
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            # Create associated screen
            screen = Screen(user_id=user.id)
            session.add(screen)
            session.commit()

            print(f"Created user {user.id} (pulsera {pulsera_id}) group_id={user.group_id}")
            
if __name__ == "__main__":
    create_dummy_users()

