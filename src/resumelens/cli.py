"""Command-line interface for résumé extraction."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .extraction import extract_resume


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract résumé information with the ResumeLens stage-one regexes."
    )
    parser.add_argument("resume", type=Path, help="UTF-8 text file containing a résumé")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="write JSON to this file instead of standard output",
    )
    args = parser.parse_args(argv)

    try:
        text = args.resume.read_text(encoding="utf-8")
    except OSError as error:
        parser.error(f"could not read {args.resume}: {error}")

    result = extract_resume(text).to_json() + "\n"
    if args.output is None:
        sys.stdout.write(result)
    else:
        try:
            args.output.write_text(result, encoding="utf-8")
        except OSError as error:
            parser.error(f"could not write {args.output}: {error}")
    return 0
