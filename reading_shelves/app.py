from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict, StrictInt

from uuid import UUID
from .repository import PostgresShelf,Conflict,InvalidTag
class Tag(BaseModel):name:str=Field(min_length=1,max_length=40,pattern=r'.*\S.*')
class Book(BaseModel):
    reference:str=Field(min_length=1,max_length=64,pattern=r'^[A-Za-z0-9-]+$')
    title:str=Field(min_length=1,max_length=120,pattern=r'.*\S.*')
    tag_ids:list[UUID]=Field(max_length=10)
def create_app(repository=None):
    repository=repository if repository is not None else PostgresShelf()
    app=FastAPI(title='Reading shelves')
    def call(fn,*args):
        try:return fn(*args)
        except Conflict:raise HTTPException(409,'duplicate') from None
        except InvalidTag:raise HTTPException(400,'unknown_tag') from None
        except Exception:raise HTTPException(503,'database_unavailable') from None
    @app.get('/health/live')
    def live():return {'status':'ok'}
    @app.get('/health/ready')
    def ready():call(repository.ready);return {'status':'ready'}
    @app.post('/tags',status_code=201)
    def tag(p:Tag):return call(repository.tag,p.name.strip())
    @app.post('/books',status_code=201)
    def book(p:Book):
        if len(set(p.tag_ids))!=len(p.tag_ids):raise HTTPException(400,'duplicate_tag')
        return call(repository.book,p.reference,p.title.strip(),p.tag_ids)
    @app.get('/books/{book_id}')
    def get(book_id:UUID):
        row=call(repository.get,book_id)
        if row is None:raise HTTPException(404,'not_found')
        return row
    @app.get('/books')
    def listing(tags:str=''):
        names=list(dict.fromkeys(t.strip() for t in tags.split(',') if t.strip()))
        if len(names)>10 or any(len(t)>40 for t in names):raise HTTPException(400,'invalid_tags')
        return {'books':call(repository.list,names)}
    return app
app=create_app()
