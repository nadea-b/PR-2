from sqlalchemy import create_engine, Column, Integer, String, Float, inspect
from sqlalchemy.orm import declarative_base  # Updated import path

# Create the base class for declarative models
Base = declarative_base()

# Define the Book model
class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    link = Column(String, nullable=False)  # Added column for the book's link

    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}', price={self.price}, link='{self.link}')>"

# Create database and tables
def setup_database():
    # Create SQLite database file
    engine = create_engine('sqlite:///bookstore.db')

    inspector = inspect(engine)
    print("Tables in database:", inspector.get_table_names())

    # Create all tables
    Base.metadata.create_all(engine)

    return engine

# Example usage to initialize the database
if __name__ == "__main__":
    setup_database()
