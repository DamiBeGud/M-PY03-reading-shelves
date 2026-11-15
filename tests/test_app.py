from uuid import uuid4
from fastapi.testclient import TestClient
from reading_shelves.app import create_app
from reading_shelves.repository import Conflict,InvalidTag
class Fake:
    def __init__(self):self.tags={};self.books={}
    def ready(self):pass
    def tag(self,name):
        if name in self.tags.values():raise Conflict()
        id=uuid4();self.tags[id]=name;return {'id':id,'name':name}
    def book(self,reference,title,tags):
        if any(t not in self.tags for t in tags):raise InvalidTag()
        if any(b['reference']==reference for b in self.books.values()):raise Conflict()
        id=uuid4();row={'id':id,'reference':reference,'title':title,'tag_ids':tags};self.books[id]=row;return row
    def get(self,id):return self.books.get(id)
    def list(self,names):return [b for b in self.books.values() if set(names)<={self.tags[t] for t in b['tag_ids']}]
def test_relationship_filter_and_uniqueness_with_fake_repository():
    client=TestClient(create_app(Fake()))
    a=client.post('/tags',json={'name':'a'}).json()['id'];b=client.post('/tags',json={'name':'b'}).json()['id']
    response=client.post('/books',json={'reference':'one','title':'First','tag_ids':[a,b]});assert response.status_code==201
    id=response.json()['id'];assert client.get('/books/'+id).json()['reference']=='one'
    client.post('/books',json={'reference':'two','title':'Second','tag_ids':[a]})
    assert len(client.get('/books?tags=a,b').json()['books'])==1
    assert client.post('/books',json={'reference':'one','title':'Other','tag_ids':[]}).status_code==409
    assert client.post('/books',json={'reference':'three','title':'Other','tag_ids':[str(uuid4())]}).status_code==400
