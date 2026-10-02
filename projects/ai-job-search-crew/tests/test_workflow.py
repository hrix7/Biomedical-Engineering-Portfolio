import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from app import Application, CHECKS, make_handler
from engine import analyze, evidence_catalog, export_html, parse_requirements, template_draft, validate_draft
import local_ai


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = Application(Path(self.temp.name)/'test.sqlite3')
        self.id = 'arthrex-67794'
        self.profile = self.app.store.profile()

    def tearDown(self):
        self.temp.cleanup()

    def draft(self):
        self.app.generate(self.id, {'engine':'template'})
        return self.app.store.job(self.id)['draft']

    def review(self):
        self.app.review(self.id, dict.fromkeys(CHECKS,True))

    def test_corrections_override_cv_and_exclude_unfinished_project(self):
        self.assertEqual(self.profile['preferences']['api_budget_monthly_usd'],0)
        self.assertIsNone(self.profile['preferences']['available_hours_per_week'])
        self.assertFalse(any(e['parent']=='PROJ1' for e in evidence_catalog(self.profile)))
        d=self.draft()
        self.assertNotIn('pressure sore',d['resume'].lower())
        self.assertNotIn('thermal sensors',d['cover_letter'].lower())

    def test_demo_seed_keeps_eligibility_and_availability_unknown(self):
        result=self.app.details(self.id)['analysis']
        self.assertEqual(result['rows'][0]['status'],'clarification_required')
        self.assertEqual(result['rows'][-1]['status'],'clarification_required')
        self.assertIn('eight months',result['flags'][0])

    def test_keyword_mapping_does_not_invent_iso_or_testing(self):
        j={'description':'','requirements':parse_requirements('SolidWorks and ISO 13485 experience required.\nExperience with mechanical testing is required.'),'seed_case':False}
        rows=analyze(j,self.profile)['rows']
        self.assertIn('ISO 13485',rows[0]['explanation'])
        self.assertEqual(rows[1]['status'],'not_documented')
        self.assertNotEqual(rows[0]['status'],'fully_matched')

    def test_invalid_and_excluded_sources_block_review(self):
        d=self.draft();d['evidence_ids']=['PROJ1.1','INVENTED.99']
        self.assertEqual(sum(i['severity']=='block' for i in validate_draft(d,self.profile,self.app.store.job(self.id))),2)

    def test_claim_about_pressure_sore_testing_blocks(self):
        d=self.draft();d['resume']+='\nCompleted pressure-sore testing.'
        self.assertTrue(any(i['severity']=='block' for i in validate_draft(d,self.profile,self.app.store.job(self.id))))

    def test_review_required_before_first_submission(self):
        self.draft()
        with self.assertRaises(ValueError):
            self.app.track(self.id,{'status':'Applied','submitted_confirmation':True})
        self.review()
        with self.assertRaises(ValueError):
            self.app.track(self.id,{'status':'Applied'})
        self.app.track(self.id,{'status':'Applied','submitted_confirmation':True})
        self.assertIsNotNone(self.app.store.job(self.id)['applied_snapshot'])

    def test_edits_clear_review_keep_history_and_submission_snapshot(self):
        d=self.draft();self.review()
        self.app.track(self.id,{'status':'Applied','submitted_confirmation':True})
        before=self.app.store.job(self.id)['applied_snapshot']['draft']['cover_letter']
        self.app.edit_draft(self.id,{'resume':d['resume'],'cover_letter':d['cover_letter']+'\nExtra edited sentence.'})
        j=self.app.store.job(self.id)
        self.assertIsNone(j['review'])
        self.assertEqual(j['applied_snapshot']['draft']['cover_letter'],before)
        self.assertEqual(len(j['history']),1)

    def test_duplicate_job_and_company_notes_reuse(self):
        data={'company':'Example','title':'Design Engineer','description':'SolidWorks experience required.','mode':'Medical devices / product'}
        first=self.app.create_job(data)
        self.assertEqual(first['id'],self.app.create_job(data)['id'])
        self.app.research(first['id'],{'note':'A user-provided note.','source_url':'https://example.com/product'})
        second=self.app.create_job({**data,'title':'Research Engineer'})
        self.assertEqual(len(self.app.store.job(second['id'])['research']),1)

    def test_metrics_use_submitted_cohort(self):
        self.app.track(self.id,{'status':'Rejected','responded':True})
        self.assertIsNone(self.app.state()['metrics']['response_rate'])
        self.draft();self.review()
        self.app.track(self.id,{'status':'Interview','submitted_confirmation':True})
        m=self.app.state()['metrics']
        self.assertEqual((m['applied'],m['interviews'],m['response_rate']),(1,1,100))

    def test_reopening_database_preserves_changes(self):
        self.app.track(self.id,{'notes':'A saved note','status':'Draft'})
        again=Application(Path(self.temp.name)/'test.sqlite3')
        self.assertEqual(again.store.job(self.id)['notes'],'A saved note')

    def test_local_model_modes_reject_cloud(self):
        with self.assertRaises(ValueError):local_ai.LocalClient('example:cloud')
        with patch('local_ai.models',return_value={'models':['alias']}),patch('local_ai.request',return_value={'remote_host':'https://remote.example'}):
            with self.assertRaises(ValueError):local_ai.LocalClient('alias')

    def test_local_model_transport_assembly_with_fake_responses(self):
        response={'cover_letter':self.draft()['cover_letter'],'evidence_ids':['EXP3.1'],'reviewer_notes':['Check personal motivation.']}
        def fake_request(path,payload=None,timeout=5):
            if path=='/api/tags':return {'models':[{'name':'test:local'}]}
            if path=='/api/show':return {'details':{'parameter_size':'test'}}
            return {'message':{'content':json.dumps(response)},'prompt_eval_count':10,'eval_count':20}
        with patch('local_ai.request',side_effect=fake_request):
            d=local_ai.generate(self.app.store.job(self.id),self.profile,'test:local')
        self.assertEqual(d['usage']['calls'],2)
        self.assertEqual(d['usage']['api_cost_usd'],0)
        self.assertEqual(d['engine'],'ollama')

    def test_failed_generation_retains_draft(self):
        old=self.draft()
        with patch('local_ai.generate',side_effect=RuntimeError('Expected test failure')):
            run=self.app.generate(self.id,{'engine':'ollama','model':'missing'})
            deadline=time.monotonic()+3
            while self.app.store.run(run['run_id'])['status']=='running' and time.monotonic()<deadline:time.sleep(.02)
        self.assertEqual(self.app.store.run(run['run_id'])['status'],'failed')
        self.assertEqual(self.app.store.job(self.id)['draft'],old)

    def test_concurrent_edits_are_not_overwritten(self):
        old=self.draft();started=threading.Event();release=threading.Event()
        def fake(*args):started.set();release.wait(2);return old
        with patch('local_ai.generate',side_effect=fake):
            run=self.app.generate(self.id,{'engine':'ollama','model':'test'})
            self.assertTrue(started.wait(2))
            with self.app.lock:self.app.edit_draft(self.id,{'resume':old['resume'],'cover_letter':old['cover_letter']+'\nMy edit.'})
            release.set();deadline=time.monotonic()+3
            while self.app.store.run(run['run_id'])['status']=='running' and time.monotonic()<deadline:time.sleep(.02)
        self.assertEqual(self.app.store.run(run['run_id'])['status'],'failed')
        self.assertIn('My edit.',self.app.store.job(self.id)['draft']['cover_letter'])

    def test_print_export_escapes_html(self):
        output=export_html({'title':'<script>bad</script>'},{'resume':'<img src=x onerror=bad()>'},'resume')
        self.assertNotIn('<script>',output)
        self.assertNotIn('<img',output)
        self.assertIn('&lt;img',output)

    def test_stale_browser_save_is_rejected(self):
        old=self.draft();rev=self.app.store.job(self.id)['revision']
        self.app.generate(self.id,{'engine':'template'})
        with self.assertRaises(ValueError):
            self.app.edit_draft(self.id,{**old,'expected_revision':rev})

    def test_profile_import_preserves_jobs_and_resets_review(self):
        from profile_tool import validate
        self.draft();self.review()
        p=self.app.store.profile();p['experience'][0]['facts'].append('A candidate-confirmed additional fact.')
        validate(p);self.app.store.save_profile(p)
        self.assertEqual(len(self.app.store.jobs()),1)
        self.assertIsNone(self.app.store.job(self.id)['review'])
        self.assertEqual(self.app.store.job(self.id)['status'],'Draft')

    def test_http_workflow_and_cross_origin_protection(self):
        server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.app))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_address[1]}'
        try:
            with urllib.request.urlopen(base+'/api/state') as r:state=json.load(r)
            req=urllib.request.Request(base+'/api/jobs/'+self.id+'/generate',data=b'{"engine":"template"}',headers={'Content-Type':'application/json','X-App-Token':state['token']})
            with urllib.request.urlopen(req) as r:self.assertTrue(json.load(r)['completed'])
            req.add_header('Origin','https://untrusted.example')
            with self.assertRaises(urllib.error.HTTPError) as ctx:urllib.request.urlopen(req)
            self.assertEqual(ctx.exception.code,403)
        finally:server.shutdown();server.server_close();thread.join()


if __name__=='__main__':unittest.main()
