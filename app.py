from flask import Flask,jsonify,request
from functools import wraps

API_KEY = "podapati@1"

def require_api_key(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        key = request.headers.get("x-api-key")
        if key and key == API_KEY:
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401
    return decorated


app = Flask(__name__)

books = [
        {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
        {"id": 2, "title": "Deep Learning", "author": "Ian Goodfellow"},
    ]

@app.route("/")
def home():
    return "<h1>Library Management System API is running!</h1>"


@app.route("/books")
def get_books():
    return jsonify(books)

@app.route("/books/<int:book_id>")
def get_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return jsonify(book)
    return jsonify({"error" : "Book not found"}),404

@app.route("/search")
def search_books():
    author = request.args.get("author")
    title = request.args.get("title")

    results = books

    if author:
        results = [book for book in results if author.lower() in book["author"].lower()]
    if title:
        results = [book for book in results if title.lower() in book["title"].lower()]

    return jsonify(results)


@app.route("/add_book",methods=["POST"])
@require_api_key
def add_book():
    data = request.get_json()

    if not data or "title" not in data or "author" not in data:
        return jsonify({"error": "Both 'title' and 'author' are required"}), 400
    new_book ={
        "id":len(books) + 1,
        "title" : data["title"],
        "author" : data["author"]

    }
    books.append(new_book)
    return jsonify(new_book),201

@app.route("/books/<int:book_id>",methods=["PUT"])
@require_api_key
def update_book(book_id):
    data = request.get_json()
    for book in books:
        if book["id"] == book_id:
            book["title"] = data.get("title",book["title"])
            book["author"] = data.get("author",book["author"])
            return jsonify(book)
    return jsonify({"error":"Book not Found"}),404

@app.route("/books/<int:book_id>",methods=["DELETE"])
@require_api_key
def remove_book(book_id):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return jsonify({
                    "message": "Book deleted successfully",
                    "books" : books
                       })
    return jsonify({"Error":"book not found"}),404

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error":"Resource not found"}),404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug = True) 