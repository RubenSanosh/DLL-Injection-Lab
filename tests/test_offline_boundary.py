import ast
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "crossview_lab"
FORBIDDEN_IMPORTS = {"ctypes", "psutil", "socket", "subprocess", "winreg"}
FORBIDDEN_TOKENS = {
    "CreateRemoteThread",
    "CreateToolhelp32Snapshot",
    "DeviceIoControl",
    "OpenProcess",
    "ReadProcessMemory",
    "VirtualAllocEx",
    "WriteProcessMemory",
}


def test_package_has_no_live_collection_imports_or_windows_api_calls():
    violations = []
    for path in PACKAGE.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }
        forbidden_imports = imports & FORBIDDEN_IMPORTS
        forbidden_tokens = {token for token in FORBIDDEN_TOKENS if token in source}
        if forbidden_imports or forbidden_tokens:
            violations.append((path.name, sorted(forbidden_imports), sorted(forbidden_tokens)))

    assert violations == []
