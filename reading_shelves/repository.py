import os
from uuid import uuid4
import psycopg
from psycopg.rows import dict_row

class Conflict(Exception): pass
class InvalidTag(Exception): pass

class PostgresShelf:
    def __init__(self): self.url=os.environ['DATABASE_URL']
    def connection(self): return psycopg.connect(self.url,connect_timeout=2,row_factory=dict_row)
    def ready(self):
        with self.connection() as conn:
            conn.execute('SELECT id FROM books LIMIT 1');conn.execute('SELECT id FROM tags LIMIT 1')
    def tag(self,name):
        try:
            with self.connection() as conn:
                return conn.execute('INSERT INTO tags(id,name) VALUES(%s,%s) RETURNING id,name',(uuid4(),name)).fetchone()
        except psycopg.errors.UniqueViolation: raise Conflict() from None
    def book(self,reference,title,tags):
        try:
            with self.connection() as conn:
                row=conn.execute('INSERT INTO books(id,reference,title) VALUES(%s,%s,%s) RETURNING id,reference,title',(uuid4(),reference,title)).fetchone()
                for tag in tags: conn.execute('INSERT INTO book_tags(book_id,tag_id) VALUES(%s,%s)',(row['id'],tag))
                return {**row,'tag_ids':tags}
        except psycopg.errors.UniqueViolation: raise Conflict() from None
        except psycopg.errors.ForeignKeyViolation: raise InvalidTag() from None
    def get(self,book_id):
        with self.connection() as conn:
            row=conn.execute('SELECT id,reference,title FROM books WHERE id=%s',(book_id,)).fetchone()
            if not row: return None
            ids=[r['tag_id'] for r in conn.execute('SELECT tag_id FROM book_tags WHERE book_id=%s ORDER BY tag_id',(book_id,))]
            return {**row,'tag_ids':ids}
    def list(self,names):
        with self.connection() as conn:
            if not names:return conn.execute('SELECT id,reference,title FROM books ORDER BY reference LIMIT 100').fetchall()
            return conn.execute('SELECT b.id,b.reference,b.title FROM books b JOIN book_tags bt ON bt.book_id=b.id JOIN tags t ON t.id=bt.tag_id WHERE t.name=ANY(%s) GROUP BY b.id,b.reference,b.title HAVING COUNT(DISTINCT t.name)=%s ORDER BY b.reference LIMIT 100',(names,len(names))).fetchall()
