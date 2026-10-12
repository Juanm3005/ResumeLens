"""Command-line interface for ResumeLens (stages 1, 2, 4 and 5)."""

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
    parser.add_argument(
        "resume",
        type=Path,
        help="UTF-8 text file containing a résumé (or a DSL file with --validate)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="write the result to this file instead of standard output",
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="print the stage-2 normalized qualifications instead of stage-1 matches",
    )
    parser.add_argument(
        "--profile",
        choices=("full_stack", "ml_engineer", "devops", "data_engineer"),
        help="with --normalize, sort tokens in the canonical order of this profile",
    )
    parser.add_argument(
        "--dsl",
        action="store_true",
        help="print the stage-4 candidate-profile DSL document (validated with textX)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="treat the input as a candidate-profile DSL file and validate it",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="print the stage-5 HTML visualization (of the résumé, or of the "
        "DSL file when combined with --validate)",
    )
    args = parser.parse_args(argv)
    if args.profile and not args.normalize:
        parser.error("--profile requires --normalize")
    if sum((args.normalize, args.dsl, args.validate)) > 1:
        parser.error("--normalize, --dsl and --validate are mutually exclusive")
    if args.html and (args.normalize or args.dsl):
        parser.error("--html can only be combined with --validate")

    try:
        text = args.resume.read_text(encoding="utf-8")
    except OSError as error:
        parser.error(f"could not read {args.resume}: {error}")

    if args.validate or args.dsl or args.html:
        # Imported lazily so stages 1-2 keep working without textX.
        from textx.exceptions import TextXError

        from .structuring.builder import build_candidate_profile
        from .structuring.dsl import parse_candidate_profile_file
        from .visualization import render_html, render_html_from_resume

        try:
            if args.validate:
                model = parse_candidate_profile_file(args.resume)
                result = (
                    render_html(model) if args.html
                    else f"{args.resume}: valid candidate profile\n"
                )
            elif args.html:
                result = render_html_from_resume(text)
            else:
                result = build_candidate_profile(text)
        except TextXError as error:
            sys.stderr.write(f"{args.resume}: invalid candidate profile: {error}\n")
            return 1
    elif args.normalize:
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