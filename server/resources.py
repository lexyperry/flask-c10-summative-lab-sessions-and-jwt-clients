# Import necessary modules
from flask_restful import Api, Resource 
from flask import request, session, jsonify
from models import db, User, Book 

# Initialize Flask-RESTful API object
api= Api()

# Helper function to get current logged-in user from session
def current_user():
    user_id = session.get("user_id")
    if user_id:
        return User.query.get(user_id)
    return None

# ---- AUTH ROUTES ----

# Handles user registration
class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "Missing username or password"}, 400 
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {"error": "Username already exists"}, 400

        new_user = User(username=username)
        new_user.password_hash = password 

        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.id
    
        return {"message": "User created", "username": new_user.username}, 201

# Handles user login
class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session["user_id"] = user.id
            return {"message": "Login successful"}, 200
            
        return {"error": "Invalid credentials"}, 401
        
# Handles user logout
class Logout(Resource):
        def delete(self):
            session["user_id"] = None
            return {"message": "Logged out"}, 204
            
# ---- BOOK ROUTES ----

# Handles GET and POST for books
class Books(Resource):
    def get(self):
        user = current_user()
        if not user:
            return {"error": "Unauthorized"}, 401
            
        page = request.args.get("page", 1, type=int)
        per_page = 5 
        books = Book.query.filter_by(user_id=user.id).paginate(page=page, per_page=per_page, error_out=False)

        return [
            {"id": b.id, "title": b.title, "author": b.author, "rating": b.rating}
            for b in books.items
            ]
        
    def post(self):
        user = current_user()
        if not user:
            return {"error": "Unauthorized"}, 401
            
        data = request.get_json()
        title = data.get("title")
        author = data.get("author")
        rating = data.get("rating", None)

        book = Book(title=title, author=author, rating=rating, user_id=user.id)
        db.session.add(book)
        db.session.commit()

        return {"message": "Book created", "id": book.id}, 201

# Handles PATCH and DELETE for individual books
class BookById(Resource):
    def patch(self, book_id):
        user = current_user()
        book = Book.query.get(book_id)

        if not user or not book or book.user_id != user.id:
            return {"error": "Unauthorized"}, 401
            
        data = request.get_json()
        book.title = data.get("title", book.title)
        book.author = data.get("author", book.author)
        book.rating = data.get("rating", book.rating)

        db.session.commit()
        return {"message": "Book updated"}
        
    def delete(self, book_id):
        user = current_user()
        book = Book.query.get(book_id)

        if not user or not book or book.user_id != user.id:
            return {"error": "Unauthorized"}, 401
            
        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted"}
    
class CheckSession(Resource):
    def get(self):
        user = current_user()
        if user:
            return {"id": user.id, "username": user.username}, 200
        return {"error": "Unauthorized"}, 401

api.add_resource(CheckSession, "/check_session")

        
# ---- REGISTER ROUTES ----

api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(Books, "/books")
api.add_resource(BookById, "/books/<int:book_id>")