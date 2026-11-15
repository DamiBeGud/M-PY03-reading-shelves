import os
import hashlib
from pathlib import Path
import psycopg

def main():
    with psycopg.connect(os.environ['DATABASE_URL'],connect_timeout=2) as conn:
        conn.execute('SELECT pg_advisory_xact_lock(73192)')
        conn.execute('CREATE TABLE IF NOT EXISTS app_migrations(version text PRIMARY KEY,checksum text NOT NULL)')
        for path in sorted(Path(__file__).with_name('migrations').glob('*.sql')):
            sql=path.read_text();checksum=hashlib.sha256(sql.encode()).hexdigest()
            old=conn.execute('SELECT checksum FROM app_migrations WHERE version=%s',(path.name,)).fetchone()
            if old:
                if old[0]!=checksum: raise ValueError('migration_checksum_changed')
                continue
            conn.execute(sql)
            conn.execute('INSERT INTO app_migrations(version,checksum) VALUES(%s,%s)',(path.name,checksum))

if __name__=='__main__': main()
