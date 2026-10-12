"""Run the five ResumeLens stages on a résumé and save every result.

Usage:
    python run_pipeline.py examples/enid_sinclair.txt

Writes, inside visualizations/<résumé name>/:
    1_extraction.json      stage 1: regex extraction
    2_normalization.json   stage 2: FST-normalized tokens
    3_recognition.json     stage 3: verdict of each profile automaton
    4_profile.rlp          stage 4: candidate-profile DSL validated with textX
    5_visualization.html   stage 5: HTML page rendered from the validated model
"""

from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from textx.exceptions import TextXError  # noqa: E402

from resumelens.extraction import extract_resume  # noqa: E402
from resumelens.normalization import normalize_extraction  # noqa: E402
from resumelens.recognition import recognize_all  # noqa: E402
from resumelens.structuring import (  # noqa: E402
    build_candidate_profile,
    parse_candidate_profile,
)
from resumelens.visualization import render_html  # noqa: E402


def _save_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ResumeLens stages 1-5 on a résumé.")
    parser.add_argument("resume", type=Path, help="UTF-8 text file with the résumé")
    parser.add_argument(
        "--out", type=Path, default=ROOT / "visualizations",
        help="base output folder (default: visualizations/)",
    )
    parser.add_argument("--open", action="store_true", help="open the HTML in the browser")
    args = parser.parse_args()

    text = args.resume.read_text(encoding="utf-8")
    folder = args.out / args.resume.stem
    folder.mkdir(parents=True, exist_ok=True)

    extraction = extract_resume(text)
    _save_json(folder / "1_extraction.json", extraction.to_dict())
    print(f"[1] Extraction     -> {folder / '1_extraction.json'}")

    normalization = normalize_extraction(extraction)
    _save_json(folder / "2_normalization.json", normalization.to_dict())
    print(f"[2] Normalization  -> {normalization.tokens}")

    results = recognize_all(normalization.tokens)
    _save_json(folder / "3_recognition.json", [result.to_dict() for result in results])
    for result in results:
        print(f"[3] {result.profile:<28} {result.verdict}")

    try:
        dsl = build_candidate_profile(text)
        model = parse_candidate_profile(dsl)
    except TextXError as error:
        print(f"[4] Invalid candidate profile: {error}", file=sys.stderr)
        return 1
    (folder / "4_profile.rlp").write_text(dsl, encoding="utf-8")
    print(f"[4] Structuring    -> {folder / '4_profile.rlp'} (valid)")

    page = folder / "5_visualization.html"
    page.write_text(render_html(model), encoding="utf-8")
    print(f"[5] Visualization  -> {page}")

    if args.open:
        webbrowser.open(page.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
