import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.models import Role
from app.api.deps.db import engine
from sqlmodel import SQLModel, Session, text

def seed_roles():
    with Session(engine) as session:
        SQLModel.metadata.create_all(engine)

        session.exec(text("INSERT INTO roles (name, description) VALUES ('user', 'User');"))
        session.exec(text("INSERT INTO roles (name, description) VALUES ('admin', 'Admin');"))
        session.commit()
        print("Roles seeded successfully")

if __name__ == "__main__":
    seed_roles()
