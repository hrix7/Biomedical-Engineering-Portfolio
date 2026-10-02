#!/usr/bin/env python3
"""Run with python3 app.py. The dashboard binds to your computer only."""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from engine import MODES, analyze, coach_answer, evidence_catalog, export_html, interview_pack, parse_requirements, template_draft, validate_draft
from storage import Store, now
import local_ai

ROOT = Path(__file__).resolve().parent
CHECKS = ['facts', 'company', 'relevance', 'voice', 'eligibility']
STATUSES = ['Draft', 'Reviewed', 'Applied', 'Interview', 'Offer', 'Rejected', 'Archived']


def require_text(data, key, limit=30000):
    val = data.get(key, '')
    if not isinstance(val, str) or not val.strip() or len(val) > limit:
        raise ValueError(f'{key.replace("_", " ").capitalize()} is required and must be at most {limit} characters.')
    return val.strip()


def invalidate(job):
    job['review'] = None
    job['revision'] = job.get('revision', 0) + 1
    if job['status'] == 'Reviewed':
        job['status'] = 'Draft'


def keep_history(job):
    if job.get('draft'):
        job.setdefault('history', []).append({'saved_at': now(), 'revision': job['revision'], 'draft': job['draft'], 'review': job.get('review')})
        job['history'] = job['history'][-20:]


class Application:
    def __init__(self, database):
        self.seed = json.loads((ROOT / 'data/seed.json').read_text())
        self.store = Store(database, self.seed)
        self.lock = threading.RLock()
        self.generation_lock = threading.Lock()
        self.token = secrets.token_urlsafe(32)
        for run in self.store.runs():
            if run['status'] in ['running', 'queued']:
                run.update(status='failed', error='The application restarted before this run finished.')
                self.store.save_run(run)

    def details(self, job_id):
        job = self.store.job(job_id)
        profile = self.store.profile()
        return {'job': job, 'analysis': analyze(job, profile, self.seed['initial_analysis']),
                'checks': validate_draft(job['draft'], profile, job) if job.get('draft') else [],
                'interview': interview_pack(job, profile), 'evidence': evidence_catalog(profile)}

    def state(self):
        jobs = self.store.jobs()
        submitted = [j for j in jobs if j.get('applied_at')]
        interviews = sum(bool(j.get('interview_at')) for j in submitted)
        responses = sum(bool(j.get('responded')) for j in submitted)
        return {'token': self.token, 'profile': self.store.profile(), 'modes': list(MODES), 'statuses': STATUSES,
                'jobs': [{k: j.get(k) for k in ['id','company','title','location','status','mode','updated_at','applied_at','follow_up','responded']} for j in jobs],
                'metrics': {'saved': len(jobs), 'applied': len(submitted), 'interviews': interviews,
                            'response_rate': round(100*responses/len(submitted)) if submitted else None,
                            'interview_rate': round(100*interviews/len(submitted)) if submitted else None,
                            'api_cost_usd': 0}, 'runs': self.store.runs()}

    def create_job(self, data):
        company = require_text(data, 'company', 200)
        title = require_text(data, 'title', 300)
        description = require_text(data, 'description', 30000)
        for job in self.store.jobs():
            if (job['company'].casefold(), job['title'].casefold(), job['description'].strip()) == (company.casefold(), title.casefold(), description):
                return {'id': job['id'], 'duplicate': True}
        mode = data.get('mode')
        if mode not in MODES:
            raise ValueError('Choose a supported job direction.')
        requirements = parse_requirements(data.get('requirements') or description)
        if not requirements:
            raise ValueError('Add at least one requirement.')
        url = data.get('posting_url', '').strip()
        if url and urlparse(url).scheme not in ['https', 'http']:
            raise ValueError('Posting URL must use http or https.')
        cached = next((j.get('research', []) for j in self.store.jobs() if j['company'].casefold() == company.casefold() and j.get('research')), [])
        job = {'id': str(uuid4()), 'company': company, 'title': title, 'location': str(data.get('location',''))[:300],
               'mode': mode, 'description': description, 'posting_url': url, 'requirements': requirements,
               'seed_case': False, 'status': 'Draft', 'notes': '', 'research': cached,
               'draft': None, 'review': None, 'revision': 0, 'applied_at': None, 'follow_up': '', 'created_at': now()}
        self.store.save_job(job)
        return {'id': job['id'], 'duplicate': False}

    def generate(self, job_id, data):
        engine = data.get('engine', 'template')
        if engine not in ['template','ollama','crewai']:
            raise ValueError('Only no-model and local-model modes are available.')
        job = self.store.job(job_id)
        if engine == 'template':
            draft = template_draft(job, self.store.profile())
            keep_history(job)
            job['draft'] = draft
            invalidate(job)
            self.store.save_job(job)
            return {'completed': True}
        if not self.generation_lock.acquire(blocking=False):
            raise ValueError('A local AI run is already in progress. Please wait for it to finish.')
        run = {'id': str(uuid4()), 'job_id': job_id, 'status': 'running', 'engine': engine,
               'model': str(data.get('model','')), 'started_at': now(), 'api_cost_usd': 0}
        self.store.save_run(run)
        snapshot_revision = job['revision']
        profile = self.store.profile()
        def worker():
            try:
                draft = local_ai.generate(job, profile, run['model'], engine)
                with self.lock:
                    current = self.store.job(job_id)
                    if current['revision'] != snapshot_revision:
                        raise ValueError('Job or draft changed during generation. New output was not applied; your edits were preserved.')
                    keep_history(current)
                    current['draft'] = draft
                    invalidate(current)
                    self.store.save_job(current)
                run.update(status='completed', usage=draft.get('usage',{}))
            except Exception as exc:
                run.update(status='failed', error=str(exc)[:1200])
            finally:
                run['finished_at'] = now()
                self.store.save_run(run)
                self.generation_lock.release()
        threading.Thread(target=worker, daemon=True).start()
        return {'run_id': run['id'], 'completed': False}

    def edit_draft(self, job_id, data):
        job = self.store.job(job_id)
        if data.get('expected_revision', job['revision']) != job['revision']:
            raise ValueError('A newer draft was saved while you were editing. Copy your edits before refreshing, then merge them into the new version.')
        if not job.get('draft'):
            raise ValueError('Create a draft first.')
        keep_history(job)
        for key in ['resume', 'cover_letter']:
            job['draft'][key] = require_text(data, key, 60000)
        job['draft']['human_edited'] = True
        invalidate(job)
        self.store.save_job(job)
        return {'saved': True}

    def review(self, job_id, data):
        job = self.store.job(job_id)
        if not job.get('draft'):
            raise ValueError('Create a draft first.')
        issues = validate_draft(job['draft'], self.store.profile(), job)
        if any(x['severity'] == 'block' for x in issues):
            raise ValueError('Resolve the blocking draft issues before marking it reviewed.')
        if not all(data.get(key) is True for key in CHECKS):
            raise ValueError('Complete all five review checks, including unresolved eligibility questions.')
        job['review'] = {'revision': job['revision'], 'checked_at': now(), 'checks': {k: True for k in CHECKS}}
        if job['status'] in ['Draft', 'Reviewed']:
            job['status'] = 'Reviewed'
        self.store.save_job(job)
        return {'reviewed': True}

    def track(self, job_id, data):
        job = self.store.job(job_id)
        status = data.get('status', job['status'])
        if status not in STATUSES:
            raise ValueError('Unknown application status.')
        if status == 'Reviewed' and (not job.get('review') or job['review']['revision'] != job['revision']):
            raise ValueError('Use the review checklist before choosing Reviewed.')
        if status in ['Applied','Interview','Offer'] and not job.get('applied_at'):
            if not job.get('review') or job['review']['revision'] != job['revision']:
                raise ValueError('Review the current draft before recording the first submission.')
            if data.get('submitted_confirmation') is not True:
                raise ValueError('Confirm that you submitted the application yourself.')
            job['applied_at'] = now()
            job['applied_snapshot'] = {'draft': job['draft'], 'review': job['review'], 'recorded_at': now()}
        if status in ['Interview','Offer']:
            job['interview_at'] = job.get('interview_at') or now()
            job['responded'] = True
        elif 'responded' in data:
            job['responded'] = data['responded'] is True
        follow_up = str(data.get('follow_up', ''))
        if follow_up:
            from datetime import date
            date.fromisoformat(follow_up)
        job.update(status=status, notes=str(data.get('notes',''))[:12000], follow_up=follow_up)
        self.store.save_job(job)
        return {'saved': True}

    def research(self, job_id, data):
        job = self.store.job(job_id)
        note = require_text(data, 'note', 4000)
        url = require_text(data, 'source_url', 2000)
        if urlparse(url).scheme not in ['http','https'] or not urlparse(url).netloc:
            raise ValueError('Add the source webpage URL using http or https.')
        if len(job.get('research',[])) >= 12:
            raise ValueError('This job already has 12 research notes. Keep the research focused.')
        job.setdefault('research',[]).append({'note': note, 'source_url': url, 'saved_at': now(), 'verification': 'User-provided; not fetched by the app'})
        invalidate(job)
        self.store.save_job(job)
        return {'saved': True}

    def requirements(self, job_id, data):
        job = self.store.job(job_id)
        text = require_text(data, 'requirements', 18000)
        rows = parse_requirements(text)
        if not rows:
            raise ValueError('Add at least one complete requirement.')
        job['requirements'] = rows
        job['seed_case'] = False
        invalidate(job)
        self.store.save_job(job)
        return {'saved': True}


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # Do not log pasted text or personal data.

        def send(self, body, code=200, mime='application/json', filename=None):
            if mime == 'application/json':
                body = json.dumps(body, ensure_ascii=False)
            if isinstance(body, str):
                body = body.encode('utf-8')
            self.send_response(code)
            self.send_header('Content-Type', mime + ('; charset=utf-8' if mime.startswith('text/') else ''))
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
            if filename:
                self.send_header('Content-Disposition', 'attachment; filename="' + filename + '"')
            self.end_headers()
            self.wfile.write(body)

        def valid_origin(self):
            port = self.server.server_address[1]
            host = self.headers.get('Host', '')
            if host not in [f'127.0.0.1:{port}', f'localhost:{port}']:
                return False
            origin = self.headers.get('Origin')
            return not origin or origin in [f'http://127.0.0.1:{port}', f'http://localhost:{port}']

        def do_GET(self):
            if not self.valid_origin():
                return self.send({'error':'Only local requests are accepted.'},403)
            parsed = urlparse(self.path)
            path = parsed.path
            try:
                if path == '/api/state':
                    return self.send(app.state())
                if path == '/api/models':
                    return self.send(local_ai.models())
                if path.startswith('/api/runs/'):
                    return self.send(app.store.run(path.rsplit('/',1)[1]))
                if path == '/api/backup':
                    return self.send({'profile':app.store.profile(), 'jobs':app.store.jobs(), 'runs':app.store.runs()}, filename='job-search-backup.json')
                if path == '/api/tracker.csv':
                    out = io.StringIO()
                    writer = csv.writer(out)
                    writer.writerow(['Company','Role','Location','Status','Applied','Follow up','Responded','Notes'])
                    for j in app.store.jobs():
                        vals = [j.get(k,'') for k in ['company','title','location','status','applied_at','follow_up','responded','notes']]
                        writer.writerow([("'"+str(v)) if str(v).startswith(('=','+','-','@')) else v for v in vals])
                    return self.send(out.getvalue(), mime='text/csv', filename='application-tracker.csv')
                parts = path.strip('/').split('/')
                if len(parts) >= 3 and parts[:2] == ['api','jobs']:
                    details = app.details(parts[2])
                    if len(parts) == 3:
                        return self.send(details)
                    if len(parts) == 4 and parts[3] == 'export':
                        qs = parse_qs(parsed.query)
                        kind = qs.get('kind',['resume'])[0]
                        kind = kind if kind in ['resume','cover_letter'] else 'resume'
                        draft = details['job'].get('draft')
                        if not draft:
                            raise ValueError('Create a draft first.')
                        if qs.get('type',['txt'])[0] == 'html':
                            return self.send(export_html(details['job'], draft, kind), mime='text/html', filename=kind+'.html')
                        return self.send(draft[kind], mime='text/plain', filename=kind+'.txt')
                files = {'/':('index.html','text/html'),'/app.js':('app.js','text/javascript'),'/styles.css':('styles.css','text/css')}
                if path in files:
                    name, mime = files[path]
                    return self.send((ROOT/'static'/name).read_bytes(), mime=mime)
                return self.send({'error':'Not found.'},404)
            except (ValueError, KeyError) as exc:
                self.send({'error':str(exc)},400)

        def do_POST(self):
            if not self.valid_origin() or not secrets.compare_digest(self.headers.get('X-App-Token',''),app.token):
                return self.send({'error':'Refresh the local dashboard and try again.'},403)
            try:
                length = int(self.headers.get('Content-Length',0))
                if length <= 0 or length > 250000:
                    raise ValueError('Request is empty or too large.')
                data = json.loads(self.rfile.read(length))
                if not isinstance(data,dict):
                    raise ValueError('Expected a JSON object.')
                path = urlparse(self.path).path
                with app.lock:
                    if path == '/api/jobs':
                        return self.send(app.create_job(data))
                    if path == '/api/coach':
                        return self.send(coach_answer(require_text(data,'answer',10000)))
                    parts = path.strip('/').split('/')
                    if len(parts) == 4 and parts[:2] == ['api','jobs']:
                        methods = {'generate':app.generate, 'draft':app.edit_draft,'review':app.review,'track':app.track,'research':app.research,'requirements':app.requirements}
                        if parts[3] in methods:
                            return self.send(methods[parts[3]](parts[2], data))
                return self.send({'error':'Not found.'},404)
            except (ValueError, KeyError, TypeError) as exc:
                self.send({'error':str(exc)},400)
            except Exception:
                self.send({'error':'The operation failed. Your last saved data is retained; check the terminal or restart.'},500)
    return Handler


def main():
    parser = argparse.ArgumentParser(description='Hritika’s local job-search workspace')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--database',default=str(ROOT/'data/private/jobs.sqlite3'))
    args = parser.parse_args()
    app = Application(args.database)
    try:
        server = ThreadingHTTPServer(('127.0.0.1',args.port),make_handler(app))
    except OSError:
        raise SystemExit('Port is in use. Try: python3 app.py --port 8766')
    print(f'Open http://127.0.0.1:{args.port} in your browser. Press Ctrl+C to stop.',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()


if __name__ == '__main__':
    main()
