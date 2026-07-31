from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_web_demo_has_required_static_assets_and_marketing_contract():
    html = (DOCS / "index.html").read_text(encoding="utf-8")

    assert (DOCS / ".nojekyll").is_file()
    assert (DOCS / "style.css").is_file()
    assert (DOCS / "demo.js").is_file()
    assert "Content-Security-Policy" in html
    assert "Zero live processes touched" in html
    assert "Star on GitHub" in html
    assert "https://github.com/bsmensah-ctrl/DLL-Injection-Lab" in html


def test_web_demo_models_the_same_classic_sequence_without_network_calls():
    script = (DOCS / "demo.js").read_text(encoding="utf-8")
    expected_actions = (
        "cross_process_handle_open",
        "remote_memory_allocation",
        "remote_memory_write",
        "remote_thread_start",
        "image_load",
    )

    positions = [script.index(f'"{action}"') for action in expected_actions]
    assert positions == sorted(positions)
    assert "actorPid: 4100" in script
    assert "targetPid: 4200" in script
    assert "synthetic: true" in script
    for prohibited in ("fetch(", "XMLHttpRequest", "WebSocket", "sendBeacon", "eval("):
        assert prohibited not in script
