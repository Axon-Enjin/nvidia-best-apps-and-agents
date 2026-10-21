import hashlib
import json

from playwright.sync_api import expect

from sentinel.samples import development_bundle
from tests.browser.test_offline_acceptance import import_ui
from tests.browser.test_review_workspace import login


def test_manual_review_records_actual_multipage_source_anchor(live_workspace,tmp_path):
    base,browser,_,_=live_workspace
    files,manifest=development_bundle()
    filename,content=files[1]
    content+=b"\fSupplement: Fictional second-page course continuation.\n"
    files[1]=(filename,content)
    manifest["documents"][1]["sha256"]=hashlib.sha256(content).hexdigest()
    for name,data in files:
        (tmp_path/name).write_bytes(data)
    (tmp_path/"manifest.json").write_text(json.dumps(manifest))
    page=browser.new_page()
    login(page,base)
    import_ui(page,tmp_path)
    page.get_by_role("button",name="P07 Narrative agreement").click()
    page.get_by_label("Review action").select_option("manual_p07")
    page.get_by_label("Review reason").fill("Compared narratives including the second-page continuation")
    for kind in ("cf2","cf4","cf5","discharge"):
        page.get_by_label(f"Evidence {kind} page 1",exact=True).check()
    page.get_by_label("Evidence pages for cf4",exact=True).fill("2")
    page.get_by_role("button",name="Save review action").click()
    expect(page.get_by_label("Review history")).to_contain_text("second-page continuation")
    case_id=page.url.split("case=")[1]
    result=page.request.get(base+f"/api/claims/{case_id}/review-state").json()
    event=result["events"][-1]
    assert any(a["page"] == 2 for a in event["payload"]["anchors"])
    page.close()
