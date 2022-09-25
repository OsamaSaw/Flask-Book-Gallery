import random
import requests
from .models import Book, Author, Tags
from . import db
from flask_expects_json import expects_json
from jsonschema import validate

schema = {
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string',
            "minLength": 3,
            "uniqueItems": True
                 },
    },
    "required": ["name"]
}


tags = ["Classics",
        "Tragedy",
        "Sci-Fi",
        "Fantasy",
        "Action",
        "Mystery",
        "Romance"
        ]


def make_books():
    books_dic = []
    next_page = "http://gutendex.com/books"
    for i in range(7):
        print(next_page)
        r = requests.get(next_page)
        data = r.json()
        next_page = data['next']
        print(data)

        for bk in data['results']:
            book = []
            book.append(bk['title'])
            try:
                book.append(''.join(bk['authors'][0]['name']))
            except:
                book.append("Unknown")
            try:
                book.append(bk['formats']['image/jpeg'])
            except:
                book.append('https://i.pinimg.com/564x/55/b1/b5/55b1b5dbf1488a572f8aa37b0388d321.jpg')

            books_dic.append(book)

    for book in books_dic:
        title = book[0]
        auth = book[1]
        img = book[2]
        search = Book.query.filter_by(title=title).first()
        if search:
            continue
        search_auth = Author.query.filter_by(name=auth).first()
        if not search_auth:
            add_auther(auth)
            search_auth = Author.query.filter_by(name=auth).first()

        new_book = Book(title=title, cover=img, author_id=search_auth.id)
        new_tag = random.choice(tags)
        search_tag = Tags.query.filter_by(tag=new_tag).first()
        if not search_tag:
            search_tag = Tags(tag=new_tag)

        new_book.tags.append(search_tag)
        search_auth.books.append(new_book)
        # db.add(new_tag)
        # db.add(new_book)
        db.session.commit()
        print("Book added to DB")


@expects_json(schema)
def add_auther(auth):
    validate(instance={"name": auth}, schema=schema)
    new_auther = Author(name=auth)
    db.session.add(new_auther)
    db.session.commit()
    print("Auther added to DB")
