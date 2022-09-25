import sqlitis

sqll = '''select book.id, book.cover, book.title, a2.name as auther, t.tag  from book
inner join association a on book.id = a.book_id
inner join tags t on a.tag_id = t.id
inner join author a2 on book.author_id = a2.id'''


