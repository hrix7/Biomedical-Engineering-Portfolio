"""Explicit local profile maintenance. Stop the dashboard before importing."""
import argparse
import json
from pathlib import Path
from app import Application, ROOT
from storage import now


def validate(profile):
    if not isinstance(profile,dict):
        raise ValueError('Profile must be a JSON object.')
    for key in ['name','location']:
        if not isinstance(profile.get(key),str) or not profile[key].strip():
            raise ValueError(f'{key} must contain text.')
    for key in ['email','phone']:
        if not isinstance(profile.get('contact',{}).get(key),str):
            raise ValueError(f'contact.{key} must contain text.')
    seen=set()
    for group in ['education','experience','projects']:
        if not isinstance(profile.get(group),list) or not profile[group]:
            raise ValueError(f'{group} must be a nonempty list.')
        for item in profile[group]:
            if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not item['id'] or item['id'] in seen:
                raise ValueError('All records need unique nonempty string IDs.')
            seen.add(item['id'])
            keys={'education':['institution','start','end'], 'experience':['role','organization','start','end'], 'projects':['title','period']}[group]
            for key in keys:
                if not isinstance(item.get(key),str):raise ValueError(f'{item["id"]}.{key} must contain text.')
            if group=='education' and not (item.get('degree') or item.get('program')):raise ValueError('Education needs degree or program.')
            if group!='education' and not item.get('excluded_from_drafts'):
                if not isinstance(item.get('facts'),list) or any(not isinstance(x,str) or not x.strip() for x in item['facts']):
                    raise ValueError(f'{item["id"]} needs a list of factual statements.')
    if not isinstance(profile.get('skills'),dict) or not isinstance(profile.get('preferences'),dict):
        raise ValueError('skills and preferences must be objects.')
    for key,value in profile['skills'].items():
        if key!='id' and (not isinstance(value,list) or any(not isinstance(s,str) for s in value)):
            raise ValueError('Each skill category must be a list of strings.')
    if profile['preferences'].get('api_budget_monthly_usd')!=0:
        raise ValueError('This project supports a zero paid-API budget only.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['export','import'])
    parser.add_argument('file',type=Path)
    parser.add_argument('--database',default=str(ROOT/'data/private/jobs.sqlite3'))
    args=parser.parse_args()
    app=Application(args.database)
    if args.action=='export':
        if args.file.exists():raise SystemExit('Output already exists. Choose a new filename.')
        args.file.write_text(json.dumps(app.store.profile(),indent=2,ensure_ascii=False)+'\n')
        print('Profile exported. Edit facts carefully before importing.')
    else:
        profile=json.loads(args.file.read_text())
        validate(profile)
        previous=app.store.profile()
        for group in ['experience','projects']:
            old={e['id']:e for e in previous[group]}
            for entry in profile[group]:
                if entry.get('facts')!=old.get(entry['id'],{}).get('facts'):
                    entry['source']='Candidate profile import, '+now()[:10]
        app.store.save_profile(profile)
        print('Profile imported. Applications retained; review approvals cleared.')


if __name__=='__main__':main()
