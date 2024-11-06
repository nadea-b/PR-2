from sqlalchemy import create_engine, Column, Integer, String, Float, inspect
from sqlalchemy.orm import declarative_base

# Create the base class for declarative models
Base = declarative_base()


# Define the Book model
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    link = Column(String, nullable=False)

    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}', price={self.price}, link='{self.link}')>"


# Create database and tables
def setup_database():
    # Create SQLite database file
    engine = create_engine('sqlite:///bookstore.db')

    # Check for existing tables
    inspector = inspect(engine)
    if "books" in inspector.get_table_names():
        Book.__table__.drop(engine)  # Drop the table if it exists

    # Create all tables
    Base.metadata.create_all(engine)

    print("Tables in database:", inspector.get_table_names())
    return engine


# Example usage to initialize the database
if __name__ == "__main__":
    setup_database()
