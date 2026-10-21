"""The committed response samples behind the web client's types match what the API really returns.

Regenerate after an intended API change with UPDATE_WEB_CONTRACT=1, then fix any type errors
`pnpm --dir apps/web typecheck` reports.
"""
import json
import os

from e2e.web_contract import SAMPLES, capture_samples, shape, trim


def test_committed_samples_match_live_response_shapes(tmp_path):
    live = capture_samples(tmp_path)
    if os.getenv("UPDATE_WEB_CONTRACT") == "1":
        SAMPLES.mkdir(parents=True, exist_ok=True)
        for old in SAMPLES.glob("*.json"):
            old.unlink()
        for name, value in live.items():
            (SAMPLES / f"{name}.json").write_text(json.dumps(trim(value), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    committed = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in SAMPLES.glob("*.json")}
    assert sorted(committed) == sorted(live)
    for name, value in live.items():
        assert shape(committed[name]) == shape(value), f"{name} response shape changed"
