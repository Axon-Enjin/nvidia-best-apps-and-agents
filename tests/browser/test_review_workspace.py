from pathlib import Path

from playwright.sync_api import expect

from tests.account_helpers import PASSWORD

FIXTURE = Path(__file__).parents[1] / 'fixtures' / 'development' / 'discrepant'


def login(page, base):
    page.goto(base)
    page.get_by_label('Username').fill('reviewer')
    page.get_by_label('Password').fill(PASSWORD)
    page.get_by_role('button', name='Sign in', exact=True).press("Enter")
    page.wait_for_url(base + '/')


def test_import_queue_findings_and_current_source_are_local_responsive_and_keyboard_operable(live_workspace, tmp_path):
    base, browser, _, _ = live_workspace
    for width, scale in [(1366, 1), (375, 1), (1366, 2)]:
        context = browser.new_context(viewport={'width': int(width/scale), 'height': int(768/scale)},device_scale_factor=scale)
        page = context.new_page()
        external, errors, assets = [], [], []
        page.on('request', lambda r, external=external: external.append(r.url) if not r.url.startswith(base + '/') else None)
        page.on('pageerror', lambda e, errors=errors: errors.append(str(e)))
        page.on('response', lambda r, assets=assets: assets.append((r.url, r.status)) if '/static/' in r.url else None)
        login(page, base)
        expect(page.get_by_role('heading', name='Review queue')).to_be_visible()
        if width == 1366 and scale == 1:
            page.get_by_role('button', name='Import bundle', exact=True).press("Enter")
            page.get_by_label('Bundle manifest').set_input_files(str(FIXTURE / 'manifest.json'))
            page.get_by_label('Original documents').set_input_files([str(p) for p in FIXTURE.iterdir() if p.name != 'manifest.json'])
            page.get_by_role('button', name='Import and check', exact=True).press("Enter")
        page.get_by_label('Search claims').fill('SYN-CLAIM')
        page.get_by_role('button', name='SYN-CLAIM-1', exact=True).first.press("Enter")
        expect(page.get_by_role('button', name='P05 Dates and disposition')).to_be_visible(timeout=20000)
        page.get_by_role('button', name='P05 Dates and disposition').press("Enter")
        expect(page.get_by_label('Finding detail')).to_contain_text('Conflicting discharge_date')
        page.get_by_role('button', name='View discharge page 1').first.press("Enter")
        expect(page.get_by_label('Source text')).to_contain_text('2026-10-15')
        assert page.get_by_label('Source text').bounding_box()['y'] < page.get_by_label('Review reason').bounding_box()['y']
        expect(page.get_by_label('Source version')).to_contain_text('Version 1')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.get_by_label('Search claims').focus()
        page.keyboard.press('Tab')
        assert page.evaluate("document.activeElement.tagName") in {'BUTTON', 'SELECT', 'INPUT'}
        screenshot = Path('test-results') / f'workbench-{width}-{scale}.png'
        screenshot.parent.mkdir(exist_ok=True)
        page.screenshot(path=str(screenshot), full_page=True)
        assert not external and not errors
        assert assets and all(status == 200 for _, status in assets)
        context.close()
