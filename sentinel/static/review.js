"use strict";
function field(form,label,type="text") {const wrap=node("label",label),input=node(type==="textarea"?"textarea":"input");if(type!=="textarea")input.type=type;wrap.append(input);form.append(wrap);return input;}
function sourceChoices(form) {
  const group=node("fieldset"),legend=node("legend","Evidence from the current version");group.append(legend);const choices=[];
  for(const doc of state.bundle.documents){const label=node("label",`Evidence ${doc.type} page 1`),input=node("input");input.type="checkbox";input.style.width="auto";input.style.display="inline";label.prepend(input);group.append(label);choices.push([input,{document_id:doc.id,page:1}]);}
  form.append(group);return ()=>choices.filter(([input])=>input.checked).map(([,anchor])=>anchor);
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
  for(const expectation of review.expectations){const row=node("div",undefined,"task-row");row.append(node("p",`${expectation.reason} · ${expectation.withdrawn?"withdrawn":expectation.reviewed?"reviewed":"expected"}`));if(!expectation.withdrawn){const reason=field(row,"Attachment review reason","textarea");row.append(button("Record extra attachment review",()=>saveAction("extra_reviewed",{expectation_id:expectation.id,reason:reason.value,anchors:state.bundle.documents.filter(d=>d.type==="attachment").map(d=>({document_id:d.id,page:1}))})));if(state.actor.roles.includes("supervisor"))row.append(button("Withdraw mistaken extra requirement",()=>saveAction("extra_withdrawn",{expectation_id:expectation.id,reason:reason.value})));}extras.append(row);}root.append(extras);
  const recheck=node("details");recheck.append(node("summary","Rerun current sources"),node("p","Rerunning reopens manual review. Prior decisions remain in history."));const recheckReason=field(recheck,"Recheck reason","textarea");recheck.append(button("Recheck current version",()=>saveAction("recheck",{reason:recheckReason.value})));root.append(recheck);
  const history=node("details");history.setAttribute("aria-label","Review history");history.open=true;history.append(node("summary","Review history"));for(const event of review.events)history.append(node("p",`${event.actor} · ${event.action} · revision ${event.revision} · ${event.payload.reason}`,"event"));root.append(history);
  if(window.renderReports)window.renderReports(root);
};
