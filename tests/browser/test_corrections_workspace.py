from playwright.sync_api import expect

from tests.browser.test_review_workspace import FIXTURE, login


def test_saved_correction_controls_survive_browser_reload(live_workspace):
    base, browser, _, _ = live_workspace
    page = browser.new_page()
    login(page, base)
    page.get_by_role('button', name='Import bundle', exact=True).click()
    page.get_by_label('Bundle manifest').set_input_files(str(FIXTURE / 'manifest.json'))
    page.get_by_label('Original documents').set_input_files([str(p) for p in FIXTURE.iterdir() if p.name != 'manifest.json'])
    page.get_by_role('button', name='Import and check').click()
    page.get_by_role('button', name='P05 Dates and disposition').wait_for(timeout=20000)
    page.get_by_role('button', name='P05 Dates and disposition').click()
    page.get_by_label('Review reason').fill('Discharge date differs; request corrected source')
    page.get_by_label('Responsible department').fill('Records')
    page.get_by_label('Responsible person').fill('Sample Clerk')
    page.get_by_label('Evidence discharge page 1', exact=True).check()
    page.get_by_role('button', name='Save review action').click()
    expect(page.get_by_label('Correction tasks')).to_contain_text('Sample Clerk')
    page.get_by_label('Correction reason').fill('Handed over locally to records desk')
    page.get_by_role('button', name='Record handoff').click()
    expect(page.get_by_label('Correction tasks')).to_contain_text('handed_off')
    page.reload()
    expect(page.get_by_label('Correction tasks')).to_contain_text('handed_off')
    expect(page.get_by_label('Review history')).to_contain_text('Handed over locally')
    page.close()
