"""Command line entry point for the extraction pipeline."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from llm_data_pipeline.extractor import DEFAULT_MODEL, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract central bank policy signals from text into a CSV-backed Pandas DataFrame."
    )
    parser.add_argument("input", type=Path, help="Path to the raw text file to extract.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/extractions.csv"),
        help="CSV output path.",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        help="OpenAI model ID.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help=(
            "Optional sampling temperature. Omit it for models such as "
            "gpt-5.6-luna that do not support this parameter."
        ),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    df = run_pipeline(
        args.input,
        output_path=args.output,
        model=args.model,
        temperature=args.temperature,
    )
    print(f"Wrote {len(df)} extracted observations to {args.output}")


if __name__ == "__main__":
    main()
