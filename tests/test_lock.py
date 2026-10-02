import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from kgupc_toolkit import __version__, resources


class VersionLockTests(unittest.TestCase):
    def test_same_version_with_changed_template_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "resources").mkdir()
            template = root / "resources" / "problem.tex"
            template.write_text("original template", encoding="utf-8")
            with patch.object(resources, "PACKAGE_ROOT", root):
                lock = root / "toolkit.lock.json"
                lock.write_text(json.dumps({"schema": 1, "version": __version__,
                                            "package_sha256": resources.package_digest()}), encoding="utf-8")
                resources.verify_lock(lock)
                template.write_text("modified template", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "contents differ"):
                    resources.verify_lock(lock)

    def test_different_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            lock = Path(temporary) / "toolkit.lock.json"
            lock.write_text(json.dumps({"schema": 1, "version": "0.0.0", "package_sha256": ""}),
                            encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "version mismatch"):
                resources.verify_lock(lock)
