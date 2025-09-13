"""Schema definitions for book data validation."""
from marshmallow import Schema, fields, post_load
from typing import Dict, Any

class BookSchema(Schema):
    """Schema for validating book data."""
    
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Str(required=True)

    @post_load
    def make_book(self, data: Dict[str, Any], **kwargs) -> Dict[str, str]:
        """Process data after validation.
        
        Args:
            data (Dict[str, Any]): Validated data
            **kwargs: Additional keyword arguments
            
        Returns:
            Dict[str, str]: Processed data with string values
        """
        return {
            "title": str(data["title"]),
            "author": str(data["author"])
        }

# Create schema instances
book_schema = BookSchema()
books_schema = BookSchema(many=True)
