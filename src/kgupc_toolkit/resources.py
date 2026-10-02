"""Locate installed assets and reject changes under an archived version name."""

import hashlib
import json
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent


def resource_root() -> Path:
    return PACKAGE_ROOT / "resources"


def package_digest() -> str:
    digest = hashlib.sha256()
    files = list(PACKAGE_ROOT.glob("*.py"))
    files.extend(path for path in resource_root().rglob("*") if path.is_file())
    for path in sorted(files, key=lambda item: item.relative_to(PACKAGE_ROOT).as_posix()):
        name = path.relative_to(PACKAGE_ROOT).as_posix().encode("utf-8")
        content = path.read_bytes()
        # Source checkout line endings must not change release identity.
        if path.suffix in (".py", ".tex", ".md", ".txt", ".json"):
            content = content.replace(b"\r\n", b"\n")
        digest.update(name + b"\0" + len(content).to_bytes(8, "big") + content)
    return digest.hexdigest()


def verify_lock(lock: Path) -> dict:
    from . import __version__

    data = json.loads(Path(lock).read_text(encoding="utf-8"))
    if data.get("schema") != 1:
        raise ValueError(f"Unsupported toolkit lock schema: {lock}")
    if data.get("version") != __version__:
        raise ValueError(f"Toolkit version mismatch: need {data.get('version')}, installed {__version__}")
    if data.get("package_sha256") != package_digest():
        raise ValueError("Toolkit contents differ from the contest lock. Install the original release; "
                         "use a new version and lock for a changed template.")
    return data


def find_lock(source: Path) -> Path | None:
    source = Path(source).resolve()
    directory = source if source.is_dir() else source.parent
    for parent in (directory, *directory.parents):
        lock = parent / "toolkit.lock.json"
        if lock.is_file():
            return lock
    return None
