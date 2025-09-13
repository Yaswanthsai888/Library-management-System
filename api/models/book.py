"""Book model for the Library Management System."""
from typing import Dict, Any

class Book:
    """Book class representing a book in the library."""
    
    def __init__(self, id: int, title: str, author: str):
        """Initialize a new book.
        
        Args:
            id (int): Unique identifier for the book
            title (str): Title of the book
            author (str): Author of the book
        """
        self.id = id
        self.title = title
        self.author = author

    def to_dict(self) -> Dict[str, Any]:
        """Convert book object to dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary containing book data
        """
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Book':
        """Create a Book instance from dictionary data.
        
        Args:
            data (Dict[str, Any]): Dictionary containing book data
            
        Returns:
            Book: New Book instance
        """
        return Book(
            id=data.get("id", 0),
            title=data["title"],
            author=data["author"]
        )
