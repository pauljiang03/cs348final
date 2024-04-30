from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import exc
from sqlalchemy.exc import OperationalError
from sqlalchemy import Index

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

basic_genres = [
    'Fiction',
    'Non-Fiction',
    'Mystery',
    'Fantasy',
    'Science Fiction',
    'Romance',
    'Thriller',
    'Biography',
    'History'
]

class User(db.Model):
    username = db.Column(db.String(50), unique=True, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    user_username = db.Column(db.String(50), db.ForeignKey('user.username'), nullable=False)  
    rating = db.Column(db.Integer)
    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.now)

    genre = db.relationship('Genre', backref=db.backref('books', lazy=True))

Index('ix_book_genre_id', Book.genre_id)

with app.app_context():
    db.drop_all()

    db.create_all()

    Genre.query.delete()

    for genre_name in basic_genres:
        genre = Genre(name=genre_name)
        db.session.add(genre)

    db.session.commit()

def create_db_session():
    with app.app_context():
        db_session = scoped_session(sessionmaker(bind=db.engine))
        return db_session

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data['username']
    email = data['email']
    db_session = create_db_session()

    stmt = db.text("INSERT INTO user (username, email) VALUES (:username, :email)")
    try:
        db_session.execute(stmt, {"username": username, "email": email})
        db_session.commit()
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()

    return jsonify({'message': 'User created successfully'})

@app.route('/users', methods=['GET'])
def get_users():
    db_session = create_db_session()

    stmt = db.text("SELECT username, email FROM user")
    users = db_session.execute(stmt).fetchall()

    user_list = []
    for user in users:
        user_data = {
            'username': user.username,
            'email': user.email
        }
        user_list.append(user_data)

    db_session.close()
    return jsonify(user_list)

@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    title = data['title']
    description = data.get('description')
    user_username = data['user_username']
    rating = data['rating']
    genre_id = data['genre_id']

    db_session = create_db_session()

    try:
        with db_session.begin():
            user = db_session.query(User).filter_by(username=user_username).with_for_update(nowait=True).one()
            db_session.connection(execution_options={'isolation_level': 'SERIALIZABLE'})

            book = Book(title=title, description=description, user_username=user_username, rating=rating, genre_id=genre_id)
            db_session.add(book)
    except exc.NoResultFound:
        return jsonify({'message': 'User not found'}), 404
    except OperationalError as e:
        if 'could not obtain lock' in str(e):
            return jsonify({'message': 'Unable to obtain lock, please try again later'}), 409
        else:
            raise
    except Exception as e:
        db_session.rollback()
        raise e

    return jsonify({'message': 'Book created successfully'})

@app.route('/books', methods=['GET'])
def get_books():
    genre_id = request.args.get('genre_id', default=None, type=int)
    if genre_id:
        books = Book.query.filter_by(genre_id=genre_id).all()
    else:
        books = Book.query.all()
    book_list = []
    for book in books:
        book_data = {
            'id': book.id,
            'title': book.title,
            'description': book.description,
            'user_username': book.user_username,
            'rating': book.rating,
            'genre': {
                'id': book.genre.id,
                'name': book.genre.name
            },
            'created_at': book.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        book_list.append(book_data)
    return jsonify(book_list)

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    db_session = create_db_session()
    try:
        with db_session.begin():
            book = db_session.query(Book).filter_by(id=book_id).with_for_update(nowait=True).one()
            data = request.get_json()
            book.title = data['title']
            book.description = data.get('description')
            book.user_username = data['user_username']
            book.rating = data['rating']
            book.genre_id = data['genre_id']
    except exc.NoResultFound:
        return jsonify({'message': 'Book not found'}), 404
    except OperationalError as e:
        if 'could not obtain lock' in str(e):
            return jsonify({'message': 'Unable to obtain lock, please try again later'}), 409
        else:
            raise
    except Exception as e:
        db_session.rollback()
        raise e

    return jsonify({'message': 'Book updated successfully'})

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    db_session = create_db_session()
    try:
        with db_session.begin():
            book = db_session.query(Book).filter_by(id=book_id).with_for_update(nowait=True).one()
            db_session.delete(book)
    except exc.NoResultFound:
        return jsonify({'message': 'Book not found'}), 404
    except OperationalError as e:
        if 'could not obtain lock' in str(e):
            return jsonify({'message': 'Unable to obtain lock, please try again later'}), 409
        else:
            raise
    except Exception as e:
        db_session.rollback()
        raise e

    return jsonify({'message': 'Book deleted successfully'})

@app.route('/genres', methods=['GET'])
def get_genres():
    db_session = create_db_session()

    stmt = db.text("SELECT id, name FROM genre")
    genres = db_session.execute(stmt).fetchall()

    genre_list = []
    for genre in genres:
        genre_data = {
            'id': genre.id,
            'name': genre.name
        }
        genre_list.append(genre_data)

    db_session.close()
    return jsonify(genre_list)

@app.route('/genres', methods=['POST'])
def create_genre():
    data = request.get_json()
    name = data['name']
    db_session = create_db_session()

    stmt = db.text("INSERT INTO genre (name) VALUES (:name)")

    try:
        db_session.execute(stmt, {"name": name})
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    finally:
        db_session.close()

    return jsonify({'message': 'Genre created successfully'})

@app.route('/books/report', methods=['GET'])
def get_book_report():
    genre_id = request.args.get('genre_id', default=None, type=int)
    db_session = create_db_session()

    if genre_id:
        query = db_session.query(
            Genre.name,
            db.func.avg(Book.rating).label('avg_rating'),
            db.func.count(Book.id).label('num_ratings'),
            db.func.count(db.distinct(Book.user_username)).label('num_users'),
            db.func.count(Book.id).label('num_books'),
            Book.title.label('book_title')
        ).join(Book).filter(Book.genre_id == genre_id).group_by(Genre.id, Book.title)

        subquery = query.subquery()
        result = db_session.query(
            subquery.c.name,
            db.func.avg(subquery.c.avg_rating).label('avg_rating'),
            db.func.sum(subquery.c.num_ratings).label('num_ratings'),
            db.func.count(db.distinct(subquery.c.num_users)).label('num_users'),
            db.func.sum(subquery.c.num_books).label('num_books'),
            db.func.max(subquery.c.avg_rating).label('highest_avg_rating'),
            subquery.c.book_title.label('highest_rated_book')
        ).group_by(subquery.c.name).first()

        if result:
            genre_name, avg_rating, num_ratings, num_users, num_books, highest_avg_rating, highest_rated_book = result

            report_data = {
                'genre_name': genre_name,
                'avg_rating': float(avg_rating) if avg_rating else None,
                'num_ratings': num_ratings,
                'num_users': num_users,
                'num_books': num_books,
                'highest_rated_book': f"{highest_rated_book} ({highest_avg_rating:.2f})" if highest_rated_book else None
            }
        else:
            report_data = {}
    else:
        query = db_session.query(
            db.func.avg(Book.rating).label('avg_rating'),
            db.func.count(Book.id).label('num_ratings'),
            db.func.count(db.distinct(Book.user_username)).label('num_users'),
            db.func.count(Book.id).label('num_books'),
            db.func.max(Book.rating).label('highest_avg_rating'),
            Book.title.label('highest_rated_book')
        )

        result = query.first()

        if result:
            avg_rating, num_ratings, num_users, num_books, highest_avg_rating, highest_rated_book = result

            report_data = {
                'avg_rating': float(avg_rating) if avg_rating else None,
                'num_ratings': num_ratings,
                'num_users': num_users,
                'num_books': num_books,
                'highest_rated_book': f"{highest_rated_book} ({highest_avg_rating:.2f})" if highest_rated_book and highest_avg_rating else None
            }
        else:
            report_data = {}

    return jsonify(report_data)

if __name__ == '__main__':
    app.run()