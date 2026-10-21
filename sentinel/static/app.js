"use strict";
const $ = id => document.getElementById(id);
const state = {csrf:"", actor:null, selected:null, detail:null, bundle:null, offset:0, replace:false, serial:0};
function node(tag,text,cls) {const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e;}
function button(text,action,cls) {const e=node("button",text,cls);e.type="button";e.onclick=()=>Promise.resolve(action()).catch(notice);return e;}
function notice(error) {$("notice").hidden=false;$("notice").textContent=error instanceof Error?error.message:String(error);}
async function api(path,options={}) {
  const headers={...options.headers};
  if(options.method&&options.method!=="GET")headers["X-CSRF-Token"]=state.csrf;
  if(options.body&&!(options.body instanceof FormData)){headers["Content-Type"]="application/json";options.body=JSON.stringify(options.body);}
  const r=await fetch(path,{...options,headers});
  if(r.status===401){location.assign("/login");throw Error("Session expired. Sign in again.");}
  const data=await r.json();if(!r.ok)throw Error(typeof data.detail==="string"?data.detail:JSON.stringify(data.detail));return data;
}
async function queue() {
  const query=new URLSearchParams({q:$("search").value,view:$("filter").value,offset:state.offset,limit:20});
  const data=await api("/api/claims?"+query);$("queue-count").textContent=`${data.total} assigned claims`;$("queue-list").replaceChildren();
  if(!data.items.length)$("queue-list").append(node("p","No matching claims. Import a sample bundle to start."));
  for(const item of data.items){const row=node("div",undefined,"queue-item"),select=button(item.reference,()=>openCase(item.id));select.setAttribute("aria-current",String(item.id===state.selected));row.append(select,node("small",`${item.patient_id} · ${item.state} · ${item.status||"No sources"}`));$("queue-list").append(row);}
  $("previous").disabled=state.offset===0;$("next").disabled=state.offset+20>=data.total;
}
async function openCase(id) {
  const serial=++state.serial,detail=await api(`/api/claims/${id}`);
  const version=(detail.bundles||[]).find(b=>b.bundle_id===detail.current_bundle_id);
  const bundle=version?await api(`/api/claims/${id}/bundles/${version.version}`):null;
  if(serial!==state.serial)return;
  state.selected=id;state.detail=detail;state.bundle=bundle;location.hash=`case=${id}`;renderCase();await queue();
  if(detail.latest&&["queued","running"].includes(detail.latest.status))setTimeout(()=>{if(state.selected===id)openCase(id).catch(notice);},750);
}
function renderCase() {
  const d=state.detail,b=state.bundle,root=$("detail");root.replaceChildren();root.append(node("h2",d.reference),node("p",`Patient ${d.patient_id} · Revision ${d.revision} · ${d.state}`,"case-meta"));
  root.append(button("Import corrected version",()=>showImport(true)));
  if(!b||!d.latest?.result){root.append(node("p",d.latest?.error||"Sources are queued for bounded local extraction. Refresh this claim if processing does not finish."));return;}
  const version=node("p",`Version ${b.version} · ${d.latest.result.rule_version}`,"case-meta");version.setAttribute("aria-label","Source version");root.append(version);
  const coverage=node("details");coverage.append(node("summary","Document coverage"));const list=node("ul",undefined,"coverage");
  for(const doc of b.documents)list.append(node("li",`${doc.type}: ${doc.status} · ${doc.filename} · ${doc.page_count} pages${doc.problems.length?" · "+doc.problems.join(", "):""}`));coverage.append(list);root.append(coverage);
  root.append(node("p",`AI review: ${d.latest.result.model_status}. Narrative comparison requires a named manual review and supervisor acknowledgement.`,"muted"));
  const bench=node("div",undefined,"workbench"),findings=node("section",undefined,"findings"),evidence=node("section",undefined,"evidence");findings.append(node("h3","Checks and findings"));evidence.id="evidence";evidence.setAttribute("aria-label","Finding detail");
  for(const check of d.latest.result.checks){const select=button(`${check.id} ${check.label}`,()=>selectCheck(check,evidence,findings),"finding");select.setAttribute("aria-label",`${check.id} ${check.label}`);select.dataset.check=check.id;select.append(node("small",check.status));findings.append(select);}
  evidence.append(node("h3","Select a check"),node("p","Inspect its source passages beside the finding."));bench.append(findings,evidence);root.append(bench);
  if(window.renderReview)window.renderReview(root);
  const history=node("details");history.append(node("summary","Source version history"));
  for(const old of d.bundles)history.append(button(`Open version ${old.version}`,async()=>{const original=await api(`/api/claims/${d.id}/bundles/${old.version}`);evidence.replaceChildren(node("h3",`Historical version ${old.version}`),node("p","Historical evidence; decisions apply to the current version only."));for(const doc of original.documents)evidence.append(button(`Open ${doc.type} original`,()=>window.open(`/api/documents/${doc.id}/content`,"_blank","noopener")));}));root.append(history);
}
function selectCheck(check,evidence,findings) {
  for(const b of findings.querySelectorAll("button"))b.setAttribute("aria-pressed",String(b.dataset.check===check.id));
  evidence.replaceChildren(node("h3",`${check.id} ${check.label}`),node("span",check.status,`status ${check.status}`));for(const reason of check.blocking_reasons||[])evidence.append(node("p",reason));
  const seen=new Set();for(const anchor of check.anchors||[]){const doc=state.bundle.documents.find(d=>d.id===anchor.document_id);if(!doc||anchor.bundle_id!==state.bundle.bundle_id)continue;const key=`${doc.id}:${anchor.page}`;if(seen.has(key))continue;seen.add(key);evidence.append(button(`View ${doc.type} page ${anchor.page}`,()=>viewSource(doc,anchor,evidence)));}
  if(window.renderDecision)window.renderDecision(check,evidence);
}
function viewSource(doc,anchor,evidence) {
  evidence.querySelector(".source-view")?.remove();const viewer=node("div",undefined,"source-view");viewer.append(node("h3",`${doc.filename} · page ${anchor.page}`));const original=node("a","Download original");original.href=`/api/documents/${doc.id}/content`;viewer.append(original);
  const text=doc.extraction.pages[anchor.page-1]||"No readable text. Inspect the original or replace it.",source=node("pre",undefined,"source-text");source.setAttribute("aria-label","Source text");source.tabIndex=0;const position=text.indexOf(anchor.value);
  if(position>=0)source.append(document.createTextNode(text.slice(0,position)),node("mark",anchor.value),document.createTextNode(text.slice(position+anchor.value.length)));else source.textContent=text;
  viewer.append(source);evidence.append(viewer);source.focus();
}
function showImport(replace=false){state.replace=replace;$("import-title").textContent=replace?`Import corrected version for ${state.detail.reference}`:"Import a versioned bundle";$("import-error").hidden=true;$("import-dialog").showModal();}
$("import-button").onclick=()=>showImport();$("cancel-import").onclick=()=>$("import-dialog").close();
$("manifest-file").onchange=async()=>{try{const m=JSON.parse(await $("manifest-file").files[0].text());$("import-preview").textContent=`${m.claim_ref} · ${m.documents.map(d=>d.type).join(", ")}`;}catch{$("import-preview").textContent="Select a valid JSON manifest.";}};
$("import-form").onsubmit=async e=>{e.preventDefault();const submit=e.submitter;submit.disabled=true;try{
  const manifest=JSON.parse(await $("manifest-file").files[0].text()),originals=[...$("original-files").files];
  if(!Array.isArray(manifest.documents)||originals.length!==manifest.documents.length||manifest.documents.some(d=>!originals.some(f=>f.name===d.filename)))throw Error("Select every original named in the manifest, with no extra files.");
  const current=state.replace?state.detail:await api("/api/cases",{method:"POST",body:manifest}),data=new FormData();data.append("manifest",JSON.stringify(manifest));data.append("expected_revision",current.revision);for(const member of manifest.documents)data.append("files",originals.find(f=>f.name===member.filename));
  await api(`/api/claims/${current.id}/bundles`,{method:"POST",body:data,headers:{"Idempotency-Key":crypto.randomUUID()}});$("import-dialog").close();await openCase(current.id);notice("Originals saved. Local checks are processing.");
}catch(error){$("import-error").hidden=false;$("import-error").textContent=error.message;$("import-error").focus();}finally{submit.disabled=false;}};
let searchTimer;$("search").oninput=()=>{clearTimeout(searchTimer);searchTimer=setTimeout(()=>{state.offset=0;queue().catch(notice);},150);};$("filter").onchange=()=>{state.offset=0;queue().catch(notice);};$("previous").onclick=()=>{state.offset=Math.max(0,state.offset-20);queue().catch(notice);};$("next").onclick=()=>{state.offset+=20;queue().catch(notice);};
$("logout").onclick=async()=>{try{await api("/api/session",{method:"DELETE"});location.assign("/login");}catch(e){notice(e);}};
async function start(){const session=await api("/api/session");if(!session.authenticated)return location.assign("/login");state.csrf=session.csrf_token;state.actor=session.actor;$("identity").textContent=session.actor.username;await queue();const id=new URLSearchParams(location.hash.slice(1)).get("case");if(id)await openCase(id);}
start().catch(notice);
