"""Local SQLite state. Short transactions; no shared connection across threads."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path, seed):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('INSERT OR IGNORE INTO settings VALUES (?,?)', ('profile', json.dumps(seed['candidate'])))
        if not self.jobs():
            job = dict(seed['job'])
            job.update({'seed_case': True, 'mode': 'Medical devices / product', 'status': 'Draft',
                        'description': job.get('description') or '\n'.join(x['text'] for x in job['requirements']) + '\n' + '\n'.join(job['duties']),
                        'notes': '', 'research': [], 'draft': None, 'revision': 0,
                        'review': None, 'applied_at': None, 'follow_up': '', 'created_at': now()})
            self.save_job(job)

    def connect(self):
        db = sqlite3.connect(self.path, timeout=20)
        db.execute('PRAGMA journal_mode=WAL')
        return db

    def profile(self):
        with self.connect() as db:
            return json.loads(db.execute('SELECT value FROM settings WHERE key=?', ('profile',)).fetchone()[0])

    def save_profile(self, profile):
        with self.connect() as db:
            db.execute('UPDATE settings SET value=? WHERE key=?', (json.dumps(profile), 'profile'))
            for key, data in db.execute('SELECT id,data FROM jobs').fetchall():
                job = json.loads(data)
                job['review'] = None
                job['seed_case'] = False
                job['revision'] = job.get('revision', 0) + 1
                if job['status'] == 'Reviewed':
                    job['status'] = 'Draft'
                db.execute('UPDATE jobs SET data=? WHERE id=?', (json.dumps(job), key))

    def jobs(self):
        with self.connect() as db:
            return [json.loads(r[0]) for r in db.execute('SELECT data FROM jobs ORDER BY rowid DESC')]

    def job(self, key):
        with self.connect() as db:
            row = db.execute('SELECT data FROM jobs WHERE id=?', (key,)).fetchone()
        if not row:
            raise ValueError('Job not found.')
        return json.loads(row[0])

    def save_job(self, job):
        job['updated_at'] = now()
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO jobs VALUES (?,?)', (job['id'], json.dumps(job)))

    def save_run(self, run):
        with self.connect() as db:
            db.execute('INSERT OR REPLACE INTO runs VALUES (?,?)', (run['id'], json.dumps(run)))

    def run(self, key):
        with self.connect() as db:
            row = db.execute('SELECT data FROM runs WHERE id=?', (key,)).fetchone()
        if not row:
            raise ValueError('Run not found.')
        return json.loads(row[0])

    def runs(self):
        with self.connect() as db:
            return [json.loads(r[0]) for r in db.execute('SELECT data FROM runs ORDER BY rowid DESC LIMIT 30')]
