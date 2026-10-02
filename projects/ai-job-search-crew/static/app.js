'use strict';
let state, detail, selected, page = 'workspace', tab = 'match', dirty = false;
let generation = null, engine = 'template', model = '', installed = [], questionIndex = 0;
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeUrl = u => {try{const v=new URL(u);return ['http:','https:'].includes(v.protocol)?v.href:'#'}catch{return '#'}};
const fmtDate = d => d ? new Date(d).toLocaleDateString(undefined,{month:'short',day:'numeric',year:'numeric'}) : '—';
const badge = (s, color='') => `<span class="badge ${color}">${esc(s)}</span>`;
const statusColor = s => ['Reviewed','Offer'].includes(s)?'green':['Applied','Interview'].includes(s)?'blue':'';
const statusLabels = {clarification_required:'Needs clarification',supported_skill_listing:'Listed in CV',partial_evidence:'Partial evidence',relevant_evidence:'Relevant evidence',not_documented:'Not documented',candidate_confirmed:'Confirmed by you',related_evidence:'Related evidence',unknown:'Unknown'};

async function api(path, data) {
  const response = await fetch(path, data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json','X-App-Token':state.token},body:JSON.stringify(data)});
  const result = await response.json();
  if(!response.ok) throw new Error(result.error || 'The request failed.');
  return result;
}
function toast(msg) {$('#toast').textContent=msg;$('#toast').hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('#toast').hidden=true,7000);}
function leaveEditor() {if(dirty && !confirm('You have unsaved draft edits. Discard them and continue?'))return false;dirty=false;return true;}
async function refresh() {
  state = await api('/api/state');
  if(!selected || !state.jobs.some(j=>j.id===selected)) selected=state.jobs[0]?.id;
  if(selected) detail = await api('/api/jobs/'+selected);
  render();
}
function render() {
  document.querySelectorAll('[data-nav]').forEach(b=>b.classList.toggle('active',b.dataset.nav===page));
  $('#crumb').textContent=({workspace:'Applications',profile:'Your evidence',setup:'Local AI & setup'})[page];
  $('#content').innerHTML=page==='profile'?profileView():page==='setup'?setupView():workspaceView();
  $('#mode-options').innerHTML=state.modes.map(m=>`<option>${esc(m)}</option>`).join('');
}
function workspaceView() {
  const m=state.metrics;
  return `<section class="hero"><div><span class="eyebrow">YOUR NEXT CHAPTER</span><h1>Make each application count.</h1><p>A place to connect your experience with your next opportunity.</p></div><button class="button" data-action="new-job">+ Add opportunity</button></section>
    <div class="stats">${[
      ['Opportunities saved',m.saved,'A focused list, built by you'],['Applications sent',m.applied,'Recorded after you submit'],['Interviews',m.interviews,'Among submitted applications'],['Response rate',m.response_rate===null?'—':m.response_rate+'%',m.applied?'Any response, including rejections':'Available after your first application']
    ].map(([l,v,n])=>`<div class="stat"><div class="stat-label">${l}</div><div class="stat-value">${v}</div><div class="stat-note">${n}</div></div>`).join('')}</div>
    <div class="workspace-grid"><section class="card"><div class="list-heading">Your opportunities <span class="count">${state.jobs.length}</span></div><input class="search" id="job-search" placeholder="Filter company or role…" aria-label="Filter opportunities"><div class="job-list">${state.jobs.map(j=>`<button class="job-item ${j.id===selected?'active':''}" data-job="${esc(j.id)}" data-filter="${esc((j.company+' '+j.title).toLowerCase())}"><div class="company-label">${esc(j.company)}</div><span class="job-title">${esc(j.title)}</span>${badge(j.status,statusColor(j.status))}<div class="job-location">${esc(j.location||'Location not entered')}</div></button>`).join('')}</div></section>
    <section class="card">${detail?detailView():'<div class="empty">Add a job posting to start your application.</div>'}</section></div>
    <div class="footer-links"><a href="/api/tracker.csv" download>Download tracker CSV</a><a href="/api/backup" download>Back up all work</a></div>`;
}
function detailView() {
  const j=detail.job;
  return `<div class="detail-head"><div class="detail-meta"><span class="eyebrow" style="margin:0">${esc(j.company)}</span>${badge(j.status,statusColor(j.status))}</div><h2>${esc(j.title)}</h2><p class="subline">${esc(j.location)} &nbsp;·&nbsp; ${esc(j.mode)}${j.requisition?' &nbsp;·&nbsp; Req. '+esc(j.requisition):''}</p></div>
    <nav class="tabs" aria-label="Application sections">${[['match','Role match'],['drafts','Application drafts'],['review','Review'],['research','Company notes'],['interview','Interview'],['tracking','Track']].map(([key,label])=>`<button class="tab ${tab===key?'active':''}" data-tab="${key}">${label}</button>`).join('')}</nav>
    <div class="tab-body">${({match:matchView,drafts:draftsView,review:reviewView,research:researchView,interview:interviewView,tracking:trackingView})[tab]()}</div>`;
}
function matchView() {
  const a=detail.analysis;
  return `<div class="callout"><strong>Questions to resolve</strong>${a.flags.map(f=>`<div>• ${esc(f)}</div>`).join('')}</div>
    <div class="section-heading"><div><h3>What your experience supports</h3><p class="muted" style="margin:0">Evidence and open questions, side by side.</p></div><button class="button small secondary" data-tab="drafts">Build drafts →</button></div>
    <div class="table-wrap"><table><thead><tr><th>ROLE REQUIREMENT</th><th>YOUR EVIDENCE</th></tr></thead><tbody>${a.rows.map(r=>`<tr><td>${esc(r.text)}</td><td>${badge(statusLabels[r.status]||r.status,r.status==='candidate_confirmed'?'green':r.status==='clarification_required'?'amber':'blue')}<div class="row-note">${esc(r.explanation)}</div>${(r.evidence_ids||[]).map(e=>`<span class="evidence-ref">${esc(e)}</span>`).join('')}</td></tr>`).join('')}</tbody></table></div>
    <p class="method">${esc(a.method)}</p><details><summary>Adjust the requirements being compared</summary><form id="requirements-form"><label>One requirement per line<textarea name="requirements" rows="8" required maxlength="18000">${esc(detail.job.requirements.map(r=>r.text).join('\n'))}</textarea></label><button type="submit" class="button secondary">Save requirements</button></form><p class="method">Saving replaces this assessment with keyword mapping and clears review approval. The original posting stays saved below.</p></details><details><summary>Read the supporting evidence</summary>${detail.evidence.map(e=>`<div class="source-card"><span class="evidence-ref">${esc(e.id)}</span><b>${esc(e.label)}</b><p>${esc(e.text)}</p></div>`).join('')}</details>
    <details><summary>View saved posting text</summary><pre>${esc(detail.job.description)}</pre>${detail.job.posting_url?`<a href="${esc(safeUrl(detail.job.posting_url))}" target="_blank" rel="noreferrer">Open original posting ↗</a>`:''}</details>`;
}
function generatorView() {
  return `<div class="toolbar"><label>Writing mode<select id="engine"><option value="template" ${engine==='template'?'selected':''}>No-model · fact-based starter</option><option value="ollama" ${engine==='ollama'?'selected':''}>Local Ollama · writer + reviewer</option><option value="crewai" ${engine==='crewai'?'selected':''}>Local CrewAI · three agents</option></select></label><label id="model-label" ${engine==='template'?'hidden':''}>Installed local model<select id="model">${installed.length?installed.map(m=>`<option ${m===model?'selected':''}>${esc(m)}</option>`).join(''):'<option value="">No local model found</option>'}</select></label><button class="button" data-action="generate" ${generation?'disabled':''}>${detail.job.draft?'Create new version':'Create drafts'} →</button></div>`;
}
function draftsView() {
  const d=detail.job.draft;
  return `${generatorView()}${generation?'<div class="progress">Local AI is working. You can browse other sections; this may take several minutes. Your saved draft stays intact until the run succeeds.</div>':''}
    <div class="callout info">${engine==='template'?'No-model mode assembles your CV facts into a starter resume and letter. It does not generate AI prose.':'AI runs through a model installed on your computer. No paid provider or cloud fallback is configured.'}</div>
    ${d?`<p class="muted">${esc(d.writer_note)}</p><div class="two-col draft-editors"><label><span class="editor-label">Resume <span class="optional">editable</span></span><textarea id="resume-editor" class="editor">${esc(d.resume)}</textarea><span class="export-links"><a href="/api/jobs/${esc(selected)}/export?kind=resume" download>Text</a><a href="/api/jobs/${esc(selected)}/export?kind=resume&type=html" download>Print-ready HTML</a></span></label><label><span class="editor-label">Cover letter <span class="optional">editable</span></span><textarea id="cover-editor" class="editor">${esc(d.cover_letter)}</textarea><span class="export-links"><a href="/api/jobs/${esc(selected)}/export?kind=cover_letter" download>Text</a><a href="/api/jobs/${esc(selected)}/export?kind=cover_letter&type=html" download>Print-ready HTML</a></span></label></div>
    <div class="inline-actions"><button class="button" data-action="save-draft">Save edits</button><button class="button secondary" data-tab="review">Review checklist →</button><span id="dirty-note" class="muted">Saved version ${detail.job.revision}</span></div><p class="method">Downloads contain the last saved version. Open downloaded HTML in your browser and use Print → Save as PDF. Review the layout before submission.</p>
    ${d.reviewer_notes?.length?`<details><summary>Local AI reviewer notes</summary><pre>${esc(typeof d.reviewer_notes==='string'?d.reviewer_notes:JSON.stringify(d.reviewer_notes,null,2))}</pre></details>`:''}
    <details><summary>Evidence selected for this draft</summary>${(d.evidence_ids||[]).map(id=>`<span class="evidence-ref">${esc(id)}</span>`).join('')}</details>
    ${detail.job.history?.length?`<details><summary>Previous saved versions (${detail.job.history.length})</summary>${detail.job.history.slice().reverse().map(h=>`<details><summary>Version ${h.revision} · ${fmtDate(h.saved_at)}</summary><pre>${esc(h.draft.cover_letter)}</pre><pre>${esc(h.draft.resume)}</pre></details>`).join('')}</details>`:''}`:'<div class="empty">Your experience is ready. Create a first draft, then make it sound like you.</div>'}`;
}
function reviewView() {
  if(!detail.job.draft)return '<div class="empty">Create your application drafts first.<br><br><button class="button" data-tab="drafts">Go to drafts →</button></div>';
  const reviewed=detail.job.review?.revision===detail.job.revision;
  return `<div class="section-heading"><div><h3>Your final read-through</h3><p class="muted">Review the saved drafts. Editing them clears this approval.</p></div>${reviewed?badge('Reviewed','green'):badge('Awaiting your review','amber')}</div>
    ${detail.checks.map(c=>`<div class="quality-note ${c.severity==='block'?'block':''}"><b>${c.severity==='block'?'Resolve: ':'Check: '}</b>${esc(c.text)}</div>`).join('')}
    <form id="review-form"><div class="checklist">${[
      ['facts','The facts are accurate.','I can explain every skill, result and experience in an interview.'],
      ['company','The company and role are correct.','I checked names, contact details and any company-specific statements.'],
      ['relevance','The examples fit this role.','I checked the requirements and did not present gaps as experience.'],
      ['voice','It sounds like me.','I read the writing, removed generic phrasing and checked the exported layout.'],
      ['eligibility','I reviewed the eligibility questions.','I understand that approval here does not confirm employer eligibility or work authorization.']
    ].map(([key,label,sub])=>`<label><input type="checkbox" name="${key}" ${reviewed?'checked':''}><span><b>${label}</b><br><span class="muted">${sub}</span></span></label>`).join('')}</div><button class="button" type="submit">Mark current drafts reviewed</button></form>
    <p class="method">This records your review. It does not send an application or contact anyone.</p>`;
}
function researchView() {
  return `<h3>Company details worth remembering</h3><p class="muted">Save a useful detail with its source. Notes are reused for new jobs with the same company name. The app does not browse or verify the source.</p>
    ${(detail.job.research||[]).map(n=>`<div class="source-card"><p>${esc(n.note)}</p><a href="${esc(safeUrl(n.source_url))}" target="_blank" rel="noreferrer">Open source ↗</a><div class="source-meta">Saved ${fmtDate(n.saved_at)} · User-provided ${Date.now()-new Date(n.saved_at)>30*86400000?'· Recheck freshness':''}</div></div>`).join('')}
    <form id="research-form"><label>What did you learn?<textarea name="note" rows="4" required maxlength="4000" placeholder="A product, team priority, or specific reason the company interests you…"></textarea></label><label>Source link<input type="url" name="source_url" required placeholder="https://company.com/…"></label><button class="button secondary" type="submit">Save company note</button></form>
    <p class="method">Adding a note clears draft approval so you can check any new context before submission.</p>`;
}
function interviewView() {
  const q=detail.interview[questionIndex%detail.interview.length];
  return `<span class="eyebrow">PRACTICE · QUESTION ${questionIndex%detail.interview.length+1} OF ${detail.interview.length}</span><div class="question">${esc(q.question)}</div>
    ${q.evidence?`<div class="callout info"><strong>A possible experience to use</strong>${esc(q.evidence.text)} <span class="evidence-ref">${esc(q.evidence.id)}</span><br>Choose another example if this one does not answer the question.</div>`:''}
    <div class="star-grid">${Object.entries(q.framework).map(([k,v])=>`<div class="star"><strong>${k}</strong>${esc(v)}</div>`).join('')}</div>
    <form id="coach-form"><label>Practice your answer<textarea class="qa-answer" name="answer" required placeholder="Use your own words. Focus on what you did and what you learned."></textarea></label><div class="inline-actions"><button class="button" type="submit">Check structure</button><button class="button secondary" type="button" data-action="next-question">Next question →</button></div></form><div id="coach-feedback"></div><p class="method">This is a simple structure check, not AI feedback or a technical assessment. Practice answers are not saved.</p>`;
}
function trackingView() {
  const j=detail.job;
  return `<h3>Keep the story of this application</h3><p class="muted">Record what happened after you submitted it yourself.</p><form id="track-form"><div class="two-col"><label>Status<select name="status">${state.statuses.map(s=>`<option ${j.status===s?'selected':''}>${s}</option>`).join('')}</select></label><label>Follow-up date<input name="follow_up" type="date" value="${esc(j.follow_up)}"></label></div>
    <div class="checklist"><label><input type="checkbox" name="responded" ${j.responded?'checked':''}><span>I received a response, including a rejection.</span></label>${!j.applied_at?'<label><input type="checkbox" name="submitted_confirmation"><span>I have submitted this application myself.<br><span class="muted">Check this only when recording Applied, Interview or Offer for the first time.</span></span></label>':''}</div>
    <label>Notes<textarea name="notes" rows="5" maxlength="12000" placeholder="Follow-up, recruiter conversations, or next steps…">${esc(j.notes)}</textarea></label><button class="button" type="submit">Save tracking</button></form>
    <p class="method">Submission recorded: ${fmtDate(j.applied_at)}. Follow-up dates are reminders in this tracker only; no notifications or messages are sent.</p>
    ${j.applied_snapshot?`<details><summary>Application saved at submission</summary><pre>${esc(j.applied_snapshot.draft.cover_letter)}</pre><pre>${esc(j.applied_snapshot.draft.resume)}</pre></details>`:''}`;
}
function profileView() {
  const p=state.profile;
  return `<section class="hero"><div><span class="eyebrow">THE FACTS BEHIND YOUR APPLICATIONS</span><h1>Your experience, with evidence.</h1><p>Based on your CV and the corrections you confirmed.</p></div></section>
    <div class="callout info"><strong>Confirmed preferences</strong>Willing to relocate to Naples and work 40 hours per week on-site for the January–June 2027 Arthrex co-op. Other roles still need an availability check. Paid API budget: $0.</div>
    <div class="profile-grid"><div class="card card-pad"><h2>Education</h2>${p.education.map(e=>`<div class="profile-item"><h3>${esc(e.institution)}</h3><p>${esc(e.degree||e.program)}<br>${esc(e.start)} – ${esc(e.end)} ${e.gpa||e.cgpa?' · GPA '+esc(e.gpa||e.cgpa):''}</p><span class="evidence-ref">${esc(e.id)}</span></div>`).join('')}<div class="spacer"></div><h2>Technical skills</h2>${Object.values(p.skills).filter(Array.isArray).flat().map(s=>`<span class="skill-chip">${esc(s)}</span>`).join('')}</div>
    <div class="card card-pad"><h2>Experience</h2>${p.experience.map(e=>`<div class="profile-item"><h3>${esc(e.role)}</h3><p>${esc(e.organization)} · ${esc(e.start)} – ${esc(e.end)}</p><ul>${e.facts.map(f=>`<li>${esc(f)}</li>`).join('')}</ul><span class="evidence-ref">${esc(e.id)}</span></div>`).join('')}</div>
    <div class="card card-pad" style="grid-column:1/-1"><h2>Projects</h2>${p.projects.map(e=>`<div class="profile-item"><h3>${esc(e.title)} ${e.excluded_from_drafts?badge('Held out of drafts','amber'):badge('CV evidence','blue')}</h3><p>${esc(e.period)} · ${esc(e.advisor)}</p>${e.excluded_from_drafts?'<div class="callout">You confirmed sensor integration and physical testing were not completed. This project stays out of generated drafts until its completed design, fabrication and simulation work is clarified.</div>':`<ul>${(e.facts||[]).map(f=>`<li>${esc(f)}</li>`).join('')}</ul>`}</div>`).join('')}</div></div>
    <p class="method">CV evidence means you supplied it; it is not independent verification. The seed file is included in the project so it can be updated as your experience grows.</p>`;
}
function setupView() {
  return `<section class="hero"><div><span class="eyebrow">NO PAID APIS</span><h1>Start simple. Add local AI.</h1><p>Your first application workflow works without a model or API key.</p></div></section>
    <div class="profile-grid"><section class="card card-pad guide"><h2>Works now</h2><ul><li>Paste and save job descriptions.</li><li>Compare requirements with CV evidence.</li><li>Assemble and edit fact-based starter drafts.</li><li>Review, export, and track applications.</li><li>Practice interview answers with structure checks.</li></ul><div class="callout info">No-model mode is a practical fallback. It uses rules and templates, not AI agents.</div><h3>Keep a copy of your work</h3><p>Your saved jobs live in this project's <code>data/private</code> folder. Copy that folder while the app is stopped to back up the database.</p><a class="button secondary" href="/api/backup" download>Download data backup</a></section>
    <section class="card card-pad guide"><h2>Optional local generation</h2><ol><li>Install <a href="https://ollama.com/download/mac" target="_blank" rel="noreferrer">Ollama for Mac ↗</a> if your Mac meets its current requirements.</li><li>Download a local model suitable for your hardware. See the README for an example.</li><li>Start Ollama, then check the connection below.</li><li>In Application drafts, choose Local Ollama or Local CrewAI.</li></ol><button class="button secondary" data-action="check-models">Check local models</button><div id="model-status"></div><h3>Using CrewAI</h3><p>Install the optional dependency with the commands in <code>README.md</code>. The evidence analyst, writer and reviewer use the same local model. Cloud models are disabled.</p><div class="callout">The CrewAI integration is included, but a real local-model run still needs to be verified on your Mac. Model quality and speed depend on your hardware.</div></section></div>
    <section class="card card-pad guide" style="margin-top:20px"><h2>Recent local runs</h2>${state.runs.length?`<div class="table-wrap"><table><thead><tr><th>MODE / MODEL</th><th>STATUS</th><th>LOCAL USAGE</th></tr></thead><tbody>${state.runs.map(r=>`<tr><td>${esc(r.engine)} · ${esc(r.model)}</td><td>${esc(r.status)}${r.error?`<div class="row-note">${esc(r.error)}</div>`:''}</td><td>${r.usage?`${r.usage.calls} calls · ${r.usage.input_tokens+r.usage.output_tokens} tokens · ${r.usage.seconds}s`:'—'}<br>$0 API cost</td></tr>`).join('')}</tbody></table></div>`:'<p class="muted">No local AI runs yet.</p>'}</section>`;
}

document.addEventListener('click', async event => {
  const button = event.target.closest('button');
  if(!button)return;
  try {
    if(button.dataset.nav){if(!leaveEditor())return;page=button.dataset.nav;render();return;}
    if(button.dataset.job){if(!leaveEditor())return;selected=button.dataset.job;questionIndex=0;detail=await api('/api/jobs/'+selected);render();return;}
    if(button.dataset.tab){if(!leaveEditor())return;tab=button.dataset.tab;render();return;}
    const action=button.dataset.action;
    if(action==='new-job'){$('#new-job').showModal();return;}
    if(action==='close-modal'){$('#new-job').close();return;}
    if(action==='generate'){
      if(!leaveEditor())return;
      const result=await api('/api/jobs/'+selected+'/generate',{engine,model});
      if(result.completed){await refresh();toast('Starter drafts created. Edit them before review.');}
      else{generation=result.run_id;render();pollRun(result.run_id);}
    }
    if(action==='save-draft'){
      await api('/api/jobs/'+selected+'/draft',{resume:$('#resume-editor').value,cover_letter:$('#cover-editor').value,expected_revision:detail.job.revision});
      dirty=false;await refresh();toast('Edits saved. The review checklist has been reset.');
    }
    if(action==='check-models'){
      button.disabled=true;
      const r=await api('/api/models');installed=r.models;model=installed.includes(model)?model:installed[0]||'';
      $('#model-status').innerHTML=`<p class="muted">${esc(r.message)} ${installed.length?'Installed: '+esc(installed.join(', ')):''}</p>`;
      button.disabled=false;
    }
    if(action==='next-question'){questionIndex++;render();}
  } catch(error){toast(error.message);button.disabled=false;}
});
document.addEventListener('input', event => {
  if(['resume-editor','cover-editor'].includes(event.target.id)){dirty=true;$('#dirty-note').textContent='Unsaved edits';$('#dirty-note').className='warn-inline';}
  if(event.target.id==='job-search'){
    const q=event.target.value.toLowerCase();document.querySelectorAll('.job-item').forEach(b=>b.hidden=!b.dataset.filter.includes(q));
  }
});
document.addEventListener('change',async event=>{
  if(event.target.id==='model')model=event.target.value;
  if(event.target.id==='engine'){
    engine=event.target.value;$('#model-label').hidden=engine==='template';
    if(engine!=='template'){
      try{const r=await api('/api/models');installed=r.models;model=installed.includes(model)?model:installed[0]||'';const field=$('#model');if(field)field.innerHTML=installed.length?installed.map(m=>`<option ${m===model?'selected':''}>${esc(m)}</option>`).join(''):'<option value="">No local model found</option>';if(!r.available)toast(r.message);}catch(e){toast(e.message);}
    }
  }
});
document.addEventListener('submit',async event=>{
  event.preventDefault();const form=event.target;const values=Object.fromEntries(new FormData(form));const submit=form.querySelector('[type="submit"]');submit.disabled=true;
  try{
    if(form.id==='job-form'){
      if(!leaveEditor())return;
      const r=await api('/api/jobs',values);selected=r.id;tab='match';page='workspace';$('#new-job').close();form.reset();await refresh();toast(r.duplicate?'This opportunity is already saved.':'Opportunity saved. Review the extracted requirements.');
    }
    if(form.id==='review-form'){
      ['facts','company','relevance','voice','eligibility'].forEach(k=>values[k]=form.elements[k].checked);
      await api('/api/jobs/'+selected+'/review',values);await refresh();toast('Your review is recorded. Nothing has been submitted.');
    }
    if(form.id==='research-form'){await api('/api/jobs/'+selected+'/research',values);await refresh();toast('Company note saved.');}
    if(form.id==='requirements-form'){await api('/api/jobs/'+selected+'/requirements',values);await refresh();toast('Requirements updated. Review the new mapping.');}
    if(form.id==='track-form'){
      values.responded=form.elements.responded.checked;values.submitted_confirmation=form.elements.submitted_confirmation?.checked||false;
      await api('/api/jobs/'+selected+'/track',values);await refresh();toast('Tracking updated.');
    }
    if(form.id==='coach-form'){
      const r=await api('/api/coach',values);$('#coach-feedback').innerHTML=`<div class="callout info" style="margin-top:20px"><strong>${r.word_count} words · Structure feedback</strong>${r.notes.map(n=>`<div>• ${esc(n)}</div>`).join('')}</div>`;
    }
  }catch(e){toast(e.message);}finally{submit.disabled=false;}
});
async function pollRun(id){
  try{
    const r=await api('/api/runs/'+id);
    if(r.status==='running'||r.status==='queued'){setTimeout(()=>pollRun(id),2500);return;}
    generation=null;
    // Never re-render over an open unsaved editor when another run finishes.
    if(!dirty)await refresh();
    toast(r.status==='completed'?'Local drafts are ready for review.':r.error||'Local generation failed.');
  }catch(e){generation=null;toast(e.message);}
}
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue='';}});
refresh().then(()=>{const active=state.runs.find(r=>r.status==='running');if(active){generation=active.id;pollRun(active.id);}}).catch(e=>{$('#content').textContent='Could not open the workspace: '+e.message;});
