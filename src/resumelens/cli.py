"""Command-line interface for ResumeLens (stage 1 extraction, stage 2 normalization)."""

from __future__ import annotations

import argparse
import json
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
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="print the stage-2 normalized qualifications instead of stage-1 matches",
    )
    parser.add_argument(
        "--profile",
        choices=("full_stack", "ml_engineer"),
        help="with --normalize, sort tokens in the canonical order of this profile",
    )
    args = parser.parse_args(argv)
    if args.profile and not args.normalize:
        parser.error("--profile requires --normalize")

    try:
        text = args.resume.read_text(encoding="utf-8")
    except OSError as error:
        parser.error(f"could not read {args.resume}: {error}")

    if args.normalize:
        # Imported lazily so stage 1 keeps working without pyformlang.
        from .normalization import normalize_text

        payload = normalize_text(text, args.profile).to_dict()
        result = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    else:
        result = extract_resume(text).to_json() + "\n"

    if args.output is None:
        sys.stdout.write(result)
    else:
        try:
            args.output.write_text(result, encoding="utf-8")
        except OSError as error:
            parser.error(f"could not write {args.output}: {error}")
    return 0