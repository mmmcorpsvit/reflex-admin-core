"""
Seed demo data.

Usage:
    python -m demo.seed --sqlite
    python -m demo.seed --postgres "postgresql://user:pw@host/db"
"""
import argparse
import random
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from demo.models import Base, User, Post, Category
from datetime import datetime, timedelta

fake = Faker()

def seed(engine_url: str, total_users=200, posts_per_user=3):
    engine = create_engine(engine_url, future=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # categories
    categories = []
    for i in range(5):
        c = Category(name=fake.word().capitalize())
        session.add(c)
        categories.append(c)
    session.commit()

    users = []
    for i in range(total_users):
        u = User(
            email=f"user{i}@example.com",
            name=fake.name(),
            active=random.choice([True] * 8 + [False] * 2),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 200))
        )
        session.add(u)
        users.append(u)
    session.commit()

    for u in users:
        for j in range(posts_per_user):
            p = Post(
                title=fake.sentence(nb_words=6),
                body=fake.paragraph(nb_sentences=5),
                published=random.choice([True, False]),
                user_id=u.id,
                category_id=random.choice(categories).id
            )
            session.add(p)
    session.commit()
    print(f"Seeded {len(users)} users and approx {len(users)*posts_per_user} posts")
    session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", action="store_true", help="Use SQLite (demo.db)")
    parser.add_argument("--postgres", type=str, help="Postgres DSN")
    args = parser.parse_args()
    if args.sqlite:
        seed("sqlite:///demo.db")
    elif args.postgres:
        seed(args.postgres)
    else:
        print("Specify --sqlite or --postgres <dsn>")
