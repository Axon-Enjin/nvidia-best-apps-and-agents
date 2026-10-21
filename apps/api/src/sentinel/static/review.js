"use strict";
function field(form,label,type="text") {const wrap=node("label",label),input=node(type==="textarea"?"textarea":"input");if(type!=="textarea")input.type=type;wrap.append(input);form.append(wrap);return input;}
function sourceChoices(form,documents=state.bundle.documents) {
  const group=node("fieldset"),legend=node("legend","Evidence from the current version");group.append(legend);const choices=[];
  for(const doc of documents){const name=doc.type==="attachment"?`attachment ${doc.filename}`:doc.type,label=node("label"),caption=node("span",`Evidence ${name} page 1`),input=node("input");input.type="checkbox";input.style.width="auto";input.style.display="inline";label.append(input,caption);group.append(label);const pages=field(group,`Evidence pages for ${name}`);pages.value="1";pages.placeholder="1, 2";pages.setAttribute("aria-description",`Comma-separated page numbers, from 1 to ${doc.page_count}.`);pages.oninput=()=>{caption.textContent=`Evidence ${name} ${pages.value.includes(",")?"pages":"page"} ${pages.value}`;};choices.push({input,pages,doc});}
  form.append(group);return ()=>choices.filter(c=>c.input.checked).flatMap(c=>{const value=c.pages.value.trim();if(!/^\d+(?:\s*,\s*\d+)*$/.test(value))throw Error("Enter evidence page numbers separated by commas.");const pages=[...new Set(value.split(",").map(Number))];if(pages.some(p=>p<1||p>c.doc.page_count))throw Error(`Evidence pages must be within ${c.doc.filename}.`);return pages.map(page=>({document_id:c.doc.id,page}));});
}
async function saveAction(action,payload={}) {
  await api(`/api/claims/${state.selected}/review-events`,{method:"POST",body:{expected_revision:state.detail.revision,bundle_id:state.bundle.bundle_id,rule_version:state.review.rule_version,action,...payload}});
  await openCase(state.selected);notice("Review action saved with named responsibility and source version.");
}
window.renderDecision=(check,evidence)=>{
  if(check.id==="P10")return;
  const form=node("form");form.append(node("h3","Record a review action"));const reason=field(form,"Review reason","textarea");reason.required=true;reason.maxLength=2000;
  const label=node("label","Review action"),select=node("select");
  const options=[["correction_created","Record discrepancy and request correction"]];
  if(check.id==="P07")options.push(["manual_p07","Record manual narrative comparison"],["dismissed","Dismiss a narrative question with evidence"]);
  if(check.id==="P08")options.push(["manual_p08","Record marks, signatory and date presence review"]);
  if(check.id==="P07"&&state.actor.roles.includes("supervisor"))options.push(["supervisor_ack","Acknowledge a different reviewer’s comparison"]);
  for(const [value,text]of options){const option=node("option",text);option.value=value;select.append(option);}label.append(select);form.append(label);
  const department=field(form,"Responsible department"),person=field(form,"Responsible person");department.maxLength=person.maxLength=200;
  const chosen=sourceChoices(form),save=node("button","Save review action","primary");save.type="submit";form.append(save);
  form.onsubmit=async e=>{e.preventDefault();save.disabled=true;try{await saveAction(select.value,{reason:reason.value,check_id:check.id,department:department.value,person:person.value,anchors:chosen()});}catch(error){notice(error);}finally{save.disabled=false;}};evidence.append(form);
};
window.renderReview=root=>{
  const review=state.review;if(!review)return;
  const section=node("section");section.setAttribute("aria-label","Correction tasks");section.append(node("h3","Correction tasks"));
  if(!review.tasks.length)section.append(node("p","No correction tasks recorded."));
  for(const task of review.tasks){const row=node("article",undefined,"task-row");row.append(node("h3",`${task.check_id} · ${task.department} · ${task.person}`),node("p",`${task.status} · ${task.reason}`));
    if(!["resolved","cancelled"].includes(task.status)){const reason=field(row,"Correction reason","textarea");reason.maxLength=2000;
      const transitions={open:["correction_handoff","Record handoff"],handed_off:["correction_acknowledged","Record acknowledgement"],acknowledged:["correction_resolved","Resolve after recheck"]};const next=transitions[task.status];
      if(next)row.append(button(next[1],()=>saveAction(next[0],{task_id:task.id,reason:reason.value})));
      row.append(button("Cancel correction with reason",()=>saveAction("correction_cancelled",{task_id:task.id,reason:reason.value})));}
    section.append(row);}
  root.append(section);
  const extras=node("details");extras.append(node("summary","Expected extra attachments"));const extraReason=field(extras,"Extra attachment reason","textarea");extras.append(button("Expect extra attachment",()=>saveAction("extra_expected",{reason:extraReason.value})));
  for(const expectation of review.expectations){const row=node("div",undefined,"task-row");row.append(node("p",`${expectation.reason} · ${expectation.withdrawn?"withdrawn":expectation.reviewed?"reviewed":"expected"}`));if(!expectation.withdrawn){const reason=field(row,"Attachment review reason","textarea"),chosen=sourceChoices(row,state.bundle.documents.filter(d=>d.type==="attachment"));row.append(button("Record extra attachment review",()=>saveAction("extra_reviewed",{expectation_id:expectation.id,reason:reason.value,anchors:chosen()})));if(state.actor.roles.includes("supervisor"))row.append(button("Withdraw mistaken extra requirement",()=>saveAction("extra_withdrawn",{expectation_id:expectation.id,reason:reason.value})));}extras.append(row);}root.append(extras);
  const recheck=node("details");recheck.append(node("summary","Rerun current sources"),node("p","Rerunning reopens manual review. Prior decisions remain in history."));const recheckReason=field(recheck,"Recheck reason","textarea");recheck.append(button("Recheck current version",()=>saveAction("recheck",{reason:recheckReason.value})));root.append(recheck);
  const history=node("details");history.setAttribute("aria-label","Review history");history.open=true;history.append(node("summary","Review history"));for(const event of review.events)history.append(node("p",`${event.actor} · ${event.action} · revision ${event.revision} · ${event.payload.reason}`,"event"));root.append(history);
  if(window.renderReports)window.renderReports(root);
};

window.renderReports=root=>{
  const section=node("section");section.setAttribute("aria-label","Completion and reports");section.append(node("h3","Complete internal review"));
  for(const blocker of state.review.blockers)section.append(node("p",`${blocker.id}: ${blocker.reasons.join(" ")}`));
  const finalize=button("Complete current review",async()=>{await api(`/api/claims/${state.selected}/finalize`,{method:"POST",body:{expected_revision:state.detail.revision,bundle_id:state.bundle.bundle_id,rule_version:state.review.rule_version}});await openCase(state.selected);notice("Internal review record saved. Ready for final submission review.");},"primary");
  finalize.disabled=!state.review.can_finalize||state.detail.state==="Ready for final submission review";section.append(finalize);root.append(section);
  api(`/api/claims/${state.selected}/reports`).then(data=>{if(!section.isConnected)return;for(const report of data.items){const row=node("div",undefined,"task-row");row.append(node("p",`Review record · revision ${report.revision} · ${report.stale?"Stale after later changes":"Current"}`));if(!report.stale){for(const [format,label]of [["csv","Download CSV"],["html","Open printable record"]]){const link=node("a",label);link.href=`/api/reports/${report.id}/export?format=${format}`;link.target="_blank";link.rel="noopener";row.append(link,document.createTextNode(" · "));}}else row.append(button("Inspect historical review record",async()=>{const data=await api(`/api/reports/${report.id}`);row.append(node("pre",JSON.stringify(data.snapshot,null,2),"source-text"));}));section.append(row);}}).catch(notice);
};

window.renderConfirmations=root=>{
  const details=node("details");details.append(node("summary","Confirm extraction against source"),node("p","Inspect a legible printed original. Confirm each candidate or correct its extraction. Handwritten or unreadable content requires replacement. Confirmations reopen manual review."));
  const form=node("form"),docLabel=node("label","Source document"),docSelect=node("select"),fieldLabel=node("label","Source field"),fieldSelect=node("select");
  for(const doc of state.bundle.documents){const option=node("option",`${doc.type} · ${doc.filename}`);option.value=doc.id;docSelect.append(option);}docLabel.append(docSelect);fieldLabel.append(fieldSelect);form.append(docLabel,fieldLabel);
  const page=field(form,"Source page","number");page.value="1";page.min="1";
  const candidate=node("p"),value=field(form,"Confirmed source value"),reason=field(form,"Source confirmation reason","textarea");value.required=reason.required=true;reason.maxLength=2000;value.maxLength=10000;
  const printed=field(form,"I can read this printed source","checkbox");printed.required=true;printed.style.width="auto";form.append(candidate);
  const preview=node("div");
  const updateValue=()=>{const doc=state.bundle.documents.find(d=>d.id===docSelect.value),confirmation=state.review.confirmations.find(d=>d.document_id===doc.id)?.confirmed[fieldSelect.value];const raw=doc.extraction.fields?.[fieldSelect.value]||"";value.value=confirmation?.value||raw;candidate.textContent=`Extracted candidate: ${raw||"not extracted"}. Saved confirmation: ${confirmation?.value||"none"}.`;};
  const updateDocument=()=>{const doc=state.bundle.documents.find(d=>d.id===docSelect.value),requirements=state.review.confirmations.find(d=>d.document_id===doc.id);fieldSelect.replaceChildren();for(const key of requirements.fields){const option=node("option",key);option.value=key;fieldSelect.append(option);}page.max=doc.page_count;page.value="1";preview.replaceChildren();if(doc.content_type.startsWith("image/")){const image=node("img");image.src=`/api/documents/${doc.id}/preview`;image.alt=`Original ${doc.type}`;image.style.maxWidth="100%";preview.append(image);}const link=node("a","Open original source");link.href=`/api/documents/${doc.id}/${doc.content_type==="application/pdf"?"preview":"content"}`;link.target="_blank";link.rel="noopener";preview.append(link);updateValue();};
  docSelect.onchange=updateDocument;fieldSelect.onchange=updateValue;const submit=node("button","Confirm source value","primary");submit.type="submit";form.append(submit);
  form.onsubmit=async e=>{e.preventDefault();submit.disabled=true;try{await api(`/api/documents/${docSelect.value}/confirm`,{method:"POST",body:{expected_revision:state.detail.revision,anchor:{page:Number(page.value),field:fieldSelect.value},value:value.value,reason:reason.value,source_kind:"printed"}});await openCase(state.selected);notice("Source confirmation saved; original and extracted values retained.");}catch(error){notice(error);}finally{submit.disabled=false;}};
  details.append(form,preview);root.append(details);updateDocument();
};
