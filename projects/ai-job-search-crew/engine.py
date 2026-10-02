"""Offline matching and evidence-grounded draft assembly. Python standard library only."""
import html
import json
import re
from datetime import date

MODES = {
    'Medical devices / product': ['cad', 'solidworks', 'implant', 'surgeon', 'prototyp', 'printing', 'device'],
    'Medical imaging / AI': ['python', 'pytorch', 'segmentation', 'imaging', 'deep', 'dice', 'localization'],
    'Biomaterials / research': ['biomaterials', 'research', 'ergonomic', 'risk', 'instruction'],
    'General biomedical': ['biomedical', 'device', 'research', 'design', 'clinical'],
}
ALIASES = {
    'SolidWorks': ['solidworks'], 'CAD': ['cad', 'computer aided design', 'computer-aided design'],
    'Python': ['python'], 'MATLAB': ['matlab'], 'PyTorch': ['pytorch'],
    'Microsoft Office': ['microsoft office', 'office suite'], 'FMEA': ['fmea'],
    'ISO 13485': ['iso 13485'], 'GD&T': ['gd&t', 'geometric dimensioning'],
    'Mechanical testing': ['mechanical testing', 'mechanical test equipment'],
    'Verification / validation': ['verification', 'validation'],
    'Surgical equipment': ['surgical equipment', 'surgical instrumentation'],
    '3D printing': ['3d printing', 'additive manufacturing', 'sla'],
    'Medical imaging': ['medical imaging', 'ct/mri', 'chest x-ray'],
    'Communication': ['communicat', 'collaborat', 'teamwork'],
    'Troubleshooting': ['troubleshoot', 'technical issues'],
    'Segmentation': ['segmentation'], 'Figma': ['figma'],
    'FDA pathways': ['510(k)', 'pma'], 'Faster R-CNN': ['faster r-cnn'],
}


def evidence_catalog(profile):
    """Atomic evidence IDs. Excluded projects never enter the writer's evidence pool."""
    rows = []
    for group in ['experience', 'projects']:
        for entry in profile[group]:
            if entry.get('excluded_from_drafts'):
                continue
            for i, fact in enumerate(entry.get('facts', [])):
                rows.append({'id': f"{entry['id']}.{i+1}", 'parent': entry['id'],
                             'label': entry.get('organization', entry.get('title')), 'text': fact,
                             'kind': group, 'source': entry.get('source', 'CV, page 1')})
    for group, skills in profile['skills'].items():
        if isinstance(skills, list):
            for i, skill in enumerate(skills):
                rows.append({'id': f'SK.{group}.{i+1}', 'parent': 'SKILLS1', 'label': 'Listed skill',
                             'text': skill, 'kind': 'skill', 'source': 'CV, page 1'})
    return rows


def has_term(text, term):
    # Stems deliberately limited to these known cases; short skills must match words.
    pattern = re.escape(term)
    if term in ['communicat', 'collaborat', 'troubleshoot']:
        return bool(re.search(r'\b' + pattern, text, re.I))
    return bool(re.search(r'(?<!\w)' + pattern + r'(?!\w)', text, re.I))


def classify_requirement(text):
    lower = text.lower()
    if re.search(r'sponsor|authoriz|visa|citizen|clearance', lower):
        return 'authorization'
    if re.search(r'enroll|graduat|degree|bachelor|master|phd|student|years? of experience|\d+\+? years?', lower):
        return 'eligibility'
    if re.search(r'hours? per week|on.site|hybrid|relocat|remote|availability', lower):
        return 'availability'
    return 'preferred' if re.search(r'preferred|nice.to.have|desirable', lower) else 'skill'


def parse_requirements(text):
    lines = [re.sub(r'^[\s•*#\-]+', '', x).strip() for x in text.splitlines()]
    rows = [x for x in lines if len(x) > 18]
    if len(rows) < 2:
        rows = re.split(r'(?<=[.;])\s+', text.strip())
    # Keep original wording and surface all extracted rows for editing in the UI.
    return [{'id': f'R{i+1}', 'text': x, 'type': classify_requirement(x)}
            for i, x in enumerate(rows[:60]) if x.strip()]


def analyze(job, profile, seed_analysis=None):
    catalog = evidence_catalog(profile)
    if seed_analysis and job.get('seed_case'):
        mapped = []
        for req, mapping in zip(job['requirements'], seed_analysis['mappings']):
            mapped.append({'id': req['id'], 'text': req['text'], 'type': req['type'], **mapping})
        return {'rows': mapped, 'flags': [
            'Recent-graduate window: May 2026 to January 2027 is approximately eight months. Ask Arthrex whether its six-month rule is measured at application or start, and whether a recent MS graduate qualifies.',
            'Work authorization and sponsorship are not stated in the posting; no eligibility conclusion is made.',
            'Formal verification/validation and specific mechanical test equipment are not established by this CV.'
        ], 'method': 'Curated, source-linked assessment of the supplied Arthrex posting; no overall match score.'}
    rows, flags = [], []
    for req in job['requirements']:
        text = req['text']
        kind = classify_requirement(text)
        if kind in ['authorization', 'eligibility', 'availability']:
            explanation = 'Review the exact requirement against your circumstances; the tool does not decide eligibility.'
            if kind == 'availability':
                explanation = 'Confirm hours, location, and availability for this job; the public demo does not establish availability.'
            if re.search(r'recent graduate|within.*months|enrolled', text, re.I):
                explanation += ' Your MS graduation month is May 2026. Check the reference date and enrollment rules.'
            rows.append({'id': req['id'], 'text': text, 'type': kind, 'status': 'clarification_required',
                         'evidence_ids': [], 'explanation': explanation})
            flags.append(text)
            continue
        matched, missing, evidence = [], [], []
        for label, aliases in ALIASES.items():
            if not any(has_term(text, a) for a in aliases):
                continue
            relevant = [e for e in catalog if any(has_term(e['text'], a) for a in aliases)]
            if label == 'CAD':
                relevant += [e for e in catalog if e['kind'] == 'skill' and e['text'] in ['SolidWorks', 'Fusion 360', 'PTC Creo']]
            if label == 'Communication':
                relevant += [e for e in catalog if e['parent'] in ['EXP1']]
            if label == 'Troubleshooting':
                relevant += [e for e in catalog if e['parent'] == 'EXP4']
            if relevant:
                matched.append(label)
                evidence.extend(e['id'] for e in relevant)
            else:
                missing.append(label)
        status = 'related_evidence' if matched else 'not_documented'
        note = 'Related terms: ' + ', '.join(matched) + '. ' if matched else ''
        note += 'Not documented: ' + ', '.join(missing) + '. ' if missing else ''
        note += 'Keyword evidence is not proof that the whole requirement is met; check proficiency, scope and qualifiers.' if matched else 'No evidence found by the limited keyword dictionary. Review manually; this is not proof of missing ability.'
        rows.append({'id': req['id'], 'text': text, 'type': kind, 'status': status,
                     'evidence_ids': list(dict.fromkeys(evidence))[:8], 'explanation': note})
    if not any(classify_requirement(r['text']) == 'authorization' for r in job['requirements']):
        flags.append('Work authorization requirements were not identified by the parser. Check the full posting.')
    return {'rows': rows, 'flags': flags, 'method': 'Conservative keyword mapping of the requirements you saved. It does not infer overall fit or eligibility.'}


def selected_evidence(job, profile):
    terms = MODES.get(job.get('mode'), MODES['Medical devices / product'])
    posting = job.get('description', '').lower()
    rows = evidence_catalog(profile)
    def score(row):
        text = row['text'].lower()
        overlap = sum(1 for token in set(re.findall(r'\b[a-z]{5,}\b', text)) if token in posting)
        generic = {'device', 'research', 'biomedical', 'risk', 'design', 'clinical'}
        return sum((1 if term in generic else 5) for term in terms if term in text) + min(5, overlap)
    return sorted((e for e in rows if e['kind'] != 'skill'), key=score, reverse=True)[:8]


def template_draft(job, profile, chosen_ids=None):
    evidence = selected_evidence(job, profile)
    if chosen_ids:
        by_id = {e['id']: e for e in evidence_catalog(profile)}
        evidence = [by_id[k] for k in chosen_ids if k in by_id and by_id[k]['kind'] != 'skill'] or evidence
    skill_rows = [e for e in evidence_catalog(profile) if e['kind'] == 'skill']
    terms = MODES.get(job.get('mode'), [])
    preferred_categories = {'Medical devices / product': ['cad_and_design','medical_devices_and_regulatory'],
                            'Medical imaging / AI': ['programming_and_data','medical_imaging_and_ai'],
                            'Biomaterials / research': ['medical_devices_and_regulatory','programming_and_data']}.get(job.get('mode'),[])
    skill_rows.sort(key=lambda e: -(sum(4 for t in terms if t in e['text'].lower()) + sum(6 for c in preferred_categories if c in e['id'])))
    skills = [e['text'] for e in skill_rows]
    contact = profile['contact']
    resume = [profile['name'], f"{profile['location']} | {contact['email']} | {contact['phone']}", '', 'EDUCATION']
    for entry in profile['education']:
        resume.append(f"{entry['institution']} — {entry.get('degree') or entry['program']} | {entry['start']}–{entry['end']}")
        if entry.get('gpa') or entry.get('cgpa'):
            resume.append('GPA: ' + (entry.get('gpa') or entry['cgpa']))
    resume += ['', 'TECHNICAL SKILLS', ', '.join(skills[:18]), '', 'EXPERIENCE']
    parent_order = list(dict.fromkeys(e['parent'] for e in evidence))
    for entry in sorted(profile['experience'], key=lambda e: parent_order.index(e['id']) if e['id'] in parent_order else 99):
        resume += [f"{entry['role']} | {entry['organization']} | {entry['start']}–{entry['end']}"]
        resume += ['• ' + x for x in entry['facts']]
        resume += ['']
    resume.append('SELECTED PROJECTS')
    parents = list(dict.fromkeys(e['parent'] for e in evidence if e['kind'] == 'projects'))[:2]
    for project in profile['projects']:
        if project['id'] in parents:
            resume += [f"{project['title']} | {project['period']}"]
            resume += ['• ' + x for x in project['facts']]
            resume += ['']
    # Extractive evidence paragraphs avoid adding unsupported outcomes or role history.
    examples = evidence[:3]
    body = '\n\n'.join(f"In my work with {e['label']}, I {e['text'][0].lower() + e['text'][1:]}." for e in examples)
    degree = profile['education'][0]
    cover = f"Dear Hiring Team,\n\nI am applying for the {job['title']} position at {job['company']}. My education includes a {degree.get('degree') or degree.get('program')} from {degree['institution']}.\n\n{body}\n\nI would welcome the opportunity to discuss how this experience relates to your team's work. Thank you for considering my application.\n\n{profile['name']}"
    return {'resume': '\n'.join(resume), 'cover_letter': cover,
            'evidence_ids': [e['id'] for e in evidence], 'engine': 'template',
            'writer_note': 'Extractive starter draft, not AI-generated. Add your specific motivation and edit the letter before review.'}


def validate_draft(draft, profile, job):
    """Deterministic flags only; this is not a semantic truth verifier."""
    issues = []
    text = draft.get('resume', '') + '\n' + draft.get('cover_letter', '')
    if not draft.get('resume', '').strip() or not draft.get('cover_letter', '').strip():
        issues.append({'severity': 'block', 'text': 'Both resume and cover letter must contain text.'})
    for label in [job['company'], job['title']]:
        if label.casefold() not in draft.get('cover_letter', '').casefold():
            issues.append({'severity': 'block', 'text': f'Cover letter is missing the exact company or role: {label}'})
    valid_ids = {e['id'] for e in evidence_catalog(profile)}
    for ref in draft.get('evidence_ids', []):
        if ref not in valid_ids:
            issues.append({'severity': 'block', 'text': f'Unknown or excluded evidence ID: {ref}'})
    if re.search(r'\[(?:insert|your name|company|job title)|\bTODO\b|\bTBD\b', text, re.I):
        issues.append({'severity': 'block', 'text': 'Unfinished placeholder text found.'})
    held_out = any(p['id'] == 'PROJ1' and p.get('excluded_from_drafts') for p in profile['projects'])
    if held_out and re.search(r'pressure.sore|ulcer.risk|skin tissue|thermal sensors', text, re.I):
        issues.append({'severity': 'block', 'text': 'Pressure-sore project is held out until completed activities are confirmed. Remove it from this draft or update the profile with confirmed details first.'})
    if re.search(r'\b(expert|extensive expertise|certified|led clinical trials)\b', text, re.I):
        issues.append({'severity': 'review', 'text': 'Check claims of expertise or certification against your evidence.'})
    source = json.dumps(profile, ensure_ascii=False)
    for number in sorted(set(re.findall(r'\b\d+(?:\.\d+)?%', text))):
        if number not in source:
            issues.append({'severity': 'review', 'text': f'Check unsupported percentage: {number}'})
    issues.append({'severity': 'review', 'text': 'Read every claim against the evidence. Automated checks cannot establish factual accuracy or catch all unsupported statements.'})
    return issues


def interview_pack(job, profile):
    evidence = selected_evidence(job, profile)[:4]
    return [{'question': q, 'evidence': evidence[i % len(evidence)] if evidence else None,
             'framework': {'Situation': 'Describe the real context and constraints.',
                           'Task': 'State your own responsibility.',
                           'Action': 'Explain what you personally did and why.',
                           'Result': 'Use a confirmed outcome; do not invent numbers.'}}
            for i, q in enumerate([
                f"Why are you interested in {job['title']} at {job['company']}?",
                'Tell me about a design or technical problem you worked through.',
                'Describe a time you collaborated with someone from another discipline.',
                'How did you check the quality of your work? What were its limitations?',
                'Which requirement in this role would require the most learning from you?'])]


def coach_answer(answer):
    words = len(answer.split())
    notes = []
    if words < 40:
        notes.append('Add the context, your specific action and the outcome.')
    elif words > 250:
        notes.append('Shorten the setup and focus on your action and result.')
    if not re.search(r'\bI\b', answer):
        notes.append('Clarify your personal contribution using “I” where appropriate.')
    if not re.search(r'result|achiev|improv|learn|led to|outcome', answer, re.I):
        notes.append('Make the result or lesson explicit.')
    return {'word_count': words, 'notes': notes or ['The length and basic structure look usable. Check accuracy and relevance yourself.'],
            'method': 'Simple writing checks, not AI or technical evaluation.'}


def export_html(job, draft, kind):
    text = draft[kind]
    return '<!doctype html><html><head><meta charset="utf-8"><title>' + html.escape(job['title']) + '</title><style>body{font:11pt/1.5 Arial,sans-serif;max-width:760px;margin:42px auto;color:#111}pre{font:inherit;white-space:pre-wrap;overflow-wrap:anywhere}@media print{body{margin:0}button{display:none}}@page{margin:18mm}</style></head><body><pre>' + html.escape(text) + '</pre></body></html>'
