"""Command-line access to the shared renderer and installed resources."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from . import __version__
from .resources import package_digest, resource_root, verify_lock


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"kgupc-toolkit {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build", help="Build combined/individual problems or an editorial")
    build_parser.add_argument("source", type=Path)
    build_parser.add_argument("--lock", type=Path)
    commands.add_parser("resources", help="Print the installed resource directory")
    commands.add_parser("fingerprint", help="Print the version and reproducible package-content lock")
    verify_parser = commands.add_parser("verify-lock")
    verify_parser.add_argument("lock", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            from .build import build, find_main
            build(find_main(args.source), lock=args.lock)
        elif args.command == "resources":
            print(resource_root())
        elif args.command == "fingerprint":
            print(json.dumps({"schema": 1, "version": __version__, "package_sha256": package_digest(),
                              "repository": "https://github.com/SOLUTIO-NEST/kgupc-toolkit"}, indent=2))
        elif args.command == "verify-lock":
            verify_lock(args.lock)
            print(f"Verified kgupc-toolkit {__version__}")
    except (ValueError, OSError) as error:
        print(f"Toolkit error: {error}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(f"LaTeX build failed (exit {error.returncode}). See the log above.", file=sys.stderr)
        return error.returncode
    return 0
