from sqlalchemy import text
from database import engine

def run_migrations():
    with engine.connect() as connection:
        connection.execution_options(isolation_level="AUTOCOMMIT")
        
        print("Adding first_throw_id to users table...")
        try:
            connection.execute(text("ALTER TABLE users ADD COLUMN first_throw_id bigint"))
            print("Column added.")
        except Exception as e:
            print(f"Column might already exist: {e}")

        print("Adding index to throws.user_id...")
        try:
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_throws_user_id ON throws (user_id)"))
            print("Index created.")
        except Exception as e:
            print(f"Index creation failed: {e}")

if __name__ == "__main__":
    run_migrations()



