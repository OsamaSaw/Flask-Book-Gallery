# Flask Book Gallery
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/powered-by-electricity.svg)](https://forthebadge.com)

a simple book gallery using Flask, with APi to get the books, SQLAlchemy for database manipulation, and jwt and login for authentication

![](https://i.imgur.com/pzTkcqj.png)

this project purpose was only to get familiar with Flask, before anyone says anything, the Api for the books
did not provide any Categories for the books, so the types you are seeing are random.

the database models are a bit complicated, because the relationship Between Auther --> book (One-to-Many)
and Between the books and the category <--> tags (Many-to-Many)

but in reality each book has more than one category and more than one auther, but for simplicity I only used one each 

and used the build in login for Flask to handle the users, and added the Jwt for the user sessions, not the best use
and not what I had in mind, but it will do for now