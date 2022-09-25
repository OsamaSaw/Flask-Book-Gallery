from functools import wraps
import datetime
import jwt
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session, make_response
from .models import Book, Author, Tags, association_table, User
from sqlalchemy import or_
from . import db
import json
from . import books
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from flask_login import login_user, login_required, logout_user, current_user

views = Blueprint('views', __name__)

books_list = []
search_list = []


def get_books():
    global books_list
    bookss = Book.query.all()  # pagination
    for book in bookss:
        title = book.title
        if len(title) > 50:
            title = title[:50] + '...'
        books_list.append([title, Author.query.get(book.author_id).name, book.cover])


def search_books(keywords):
    global search_list
    bookss = Book.query.all()
    search_list = []
    keywords = keywords.strip()
    for book in bookss:
        auther = Author.query.get(book.author_id).name
        if keywords in book.title or keywords in auther:
            # title = book.title
            search_list.append([book.title, auther, book.cover])


def validate_keywords(keywords):
    if not keywords:
        return False
    else:
        return True


def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            flash(f"Missing Token", 'error')
            return redirect(url_for('views.login'))
        try:
            print("checking token")
            from main import app
            # print(jwt.decode(token, "DfGnmvsGTDzzAwAJSEKjVLdtCqwNwvvXnjUVcHNGSmXHuDICMb", algorithms=["HS256"]))
            data = jwt.decode(token, "DfGnmvsGTDzzAwAJSEKjVLdtCqwNwvvXnjUVcHNGSmXHuDICMb", algorithms=["HS256"])
            print("Valid Token", data)
        except:
            flash(f"Invalid Token", 'error')
            return redirect(url_for('views.login'))
        return func(*args, **kwargs)
        # return redirect(url_for('views.home'))

    return wrapped


def check_user_token():
    user = User.query.get(current_user.id)
    try:
        data = jwt.decode(user.token, "DfGnmvsGTDzzAwAJSEKjVLdtCqwNwvvXnjUVcHNGSmXHuDICMb", algorithms=["HS256"])
        return True
    except:
        return False


@views.route('/', methods=['GET', 'POST'])
# @check_for_token
# @jwt_required()
# @check_user_token()
@login_required
def home():
    if check_user_token():
        global books_list, search_list
        # books.make_books()
        if request.method == 'POST':
            print("POST method")
            search_query = request.form.get('search')
            type_search = request.form.get('radio')
            if validate_keywords(search_query):
                print(search_query, type_search)
                page = request.args.get('page', 1, type=int)
                if type_search == 'Title':
                    pagination = db.session.query(Book, Author). \
                        filter(Book.title.contains(search_query)). \
                        join(Author, Book.author_id == Author.id). \
                        paginate(page, per_page=50)
                    return render_template("home.html", pagination=pagination, search=search_query, user=current_user)

                elif type_search == 'Author':
                    pagination = db.session.query(Book, Author). \
                        filter(Author.name.contains(search_query)). \
                        join(Author, Book.author_id == Author.id). \
                        paginate(page, per_page=50)
                    return render_template("home.html", pagination=pagination, search=search_query, user=current_user)
                else:
                    pagination = db.session.query(Book, Author, Tags, association_table). \
                        filter(Tags.tag.contains(search_query)).\
                        join(association_table, Book.id == association_table.c.book_id). \
                        join(Tags, Tags.id == association_table.c.tag_id). \
                        join(Author, Book.author_id == Author.id).\
                        paginate(page, per_page=50)
                    return render_template("home.html", pagination=pagination, search=search_query, user=current_user)

            else:
                flash("Invalid Search Keywords", "error")
                return redirect(url_for('views.home'))
        else:
            print("GET method")
            page = request.args.get('page', 1, type=int)

            p = db.session.query(Book, Author, Tags, association_table). \
                join(association_table, Book.id == association_table.c.book_id). \
                join(Tags, Tags.id == association_table.c.tag_id). \
                join(Author, Book.author_id == Author.id).\
                paginate(page, per_page=10)

            return render_template("home.html", pagination=p, user=current_user)
    else:
        flash("Token Expired, Login again", 'error')
        return redirect(url_for('auth.logout'))


@views.route('/add/category/<tag>', methods=['POST'])
# @login_required
def add_category(tag):
    search_tag = Tags.query.filter_by(tag=tag).first()
    if not search_tag:
        search_tag = Tags(tag=tag)
        db.session.add(search_tag)
        db.session.commit()
        return json.dumps({"Status": "Success", "msg": "Category Added"})
    else:
        return json.dumps({"Status": "Error", "msg": "Already Exist"})


@views.route('/update/category/<old>/<new>', methods=['PUT'])
# @login_required
def update_category(old, new):
    search_tag = Tags.query.filter_by(tag=old).first()
    if not search_tag:
        return json.dumps({"Status": "Error", "msg": "Does Not Exist"})
    else:
        search_tag.tag = new
        db.session.commit()
        return json.dumps({"Status": "Success", "msg": "Category Updated "})


@views.route('/get/category', methods=['GET'])
# @login_required
def get_category():
    search_tag = Tags.query.all()
    tags = []
    for tag in search_tag:
        tags.append(tag.tag)
        print(tag.tag)
    if not search_tag:
        return json.dumps({"Status": "Error", "msg": "Does Not Exist"})
    else:

        return json.dumps({"Status": "Success", "msg": tags})


@views.route('/delete/category/<tag>', methods=['DELETE'])
# @login_required
def delete_category(tag):
    search_tag = Tags.query.filter_by(tag=tag).first()
    if not search_tag:
        return json.dumps({"Status": "Error", "msg": "Does Not Exist"})
    else:
        db.session.delete(search_tag)
        db.session.commit()
        return json.dumps({"Status": "Success", "msg": "Category Deleted "})

# -----------------------------------------------------------------------------

@views.route('/get/books-by-category/', methods=['GET'])
# @login_required
def get_category_books_count():
    search_tag = Tags.query.all()
    if not search_tag:
        return json.dumps({"Status": "Error", "msg": "Does Not Exist"})
    else:
        books = []
        for tag in search_tag:
            # count = association_table.query.filter(association_table.tag_id == Tags.tag == tag.tag).count()
            count = db.session.query(Tags, association_table). \
                filter(Tags.tag.contains(tag.tag)). \
                join(Tags, Tags.id == association_table.c.tag_id).count()
            # print(count, tag.tag)
            books.append([tag.tag, count])

        return json.dumps({"Status": "Success", "msg": books})


@views.route('/get/books-by-category/<cate>', methods=['GET'])
# @login_required
def get_category_books_cate(cate):
    search_tag = Tags.query.filter_by(tag=cate).first()
    if not search_tag:
        return json.dumps({"Status": "Error", "msg": "Does Not Exist"})
    else:
        books = []
        count = 0
        pagination = db.session.query(Book, Tags, association_table). \
            filter(Tags.tag.contains(cate)). \
            join(association_table, Book.id == association_table.c.book_id). \
            join(Tags, Tags.id == association_table.c.tag_id)

        for item in pagination:
            print(item.Book.title)
            books.append([item.Book.id, item.Book.title])
            count += 1
        print(count)

        return json.dumps({"Status": "Success", "size": count, "msg": books})


@views.route('/get/count-by-category/<cate>', methods=['GET'])
# @login_required
def get_category_books_by_cate_count(cate):
    search_tag = Tags.query.filter_by(tag=cate).first()
    if not search_tag:
        return json.dumps({"Status": "Error", "msg": "Does Not Exist"})
    else:
        count = db.session.query(Tags, association_table).\
            filter(Tags.tag.contains(cate)).\
            join(Tags, Tags.id == association_table.c.tag_id).count()

        # for item in pagination:
        #     print(item.Book.title)
        #     books.append([item.Book.id, item.Book.title])
        #     count += 1
        print(count)

        return json.dumps({"Status": "Success", "msg": count})

