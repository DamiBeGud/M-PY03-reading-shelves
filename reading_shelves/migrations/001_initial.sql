CREATE TABLE books(id uuid PRIMARY KEY,reference text NOT NULL UNIQUE,title text NOT NULL);
CREATE TABLE tags(id uuid PRIMARY KEY,name text NOT NULL UNIQUE);
CREATE TABLE book_tags(book_id uuid NOT NULL REFERENCES books(id),tag_id uuid NOT NULL REFERENCES tags(id),PRIMARY KEY(book_id,tag_id));
