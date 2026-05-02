"""OpenAI extraction and Pandas conversion utilities."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv() -> bool:
        return False

from llm_data_pipeline.schemas import ReportExtraction

load_dotenv()

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

SYSTEM_PROMPT = """You extract macroeconomic and monetary-policy signals for quantitative research.

Rules:
- Use only facts stated in the supplied text.
- Do not infer missing numbers, dates, or institutions.
- If a value, unit, period, date, or title is missing, use an empty string.
- Keep numeric values clean: use value "4.50" with unit "percent", not value "4.50%" with unit "%".
- Classify policy implications conservatively as hawkish, dovish, neutral, mixed, or unclear.
- Each observation must include a short evidence quote copied from the source text.
- Return only the structured extraction requested by the schema.
"""

DATAFRAME_COLUMNS = [
    "source_name",
    "report_title",
    "central_bank",
    "report_date",
    "policy_summary",
    "metric",
    "value",
    "unit",
    "period",
    "direction",
    "macro_category",
    "implication",
    "evidence_quote",
    "confidence",
]

PERCENT_PATTERN = re.compile(r"^([+-]?\d+(?:\.\d+)?)\s*%$")
PERCENT_WORD_PATTERN = re.compile(r"^([+-]?\d+(?:\.\d+)?)\s*(percent|percentage points?)$", re.IGNORECASE)


def normalize_value_unit(value: str, unit: str) -> tuple[str, str]:
    """Normalize common numeric/unit duplication before writing tabular output."""

    clean_value = value.strip()
    clean_unit = unit.strip()

    if clean_unit == "%":
        clean_unit = "percent"

    percent_match = PERCENT_PATTERN.match(clean_value)
    if percent_match:
        return percent_match.group(1), clean_unit or "percent"

    percent_word_match = PERCENT_WORD_PATTERN.match(clean_value)
    if percent_word_match:
        normalized_unit = percent_word_match.group(2).lower()
        return percent_word_match.group(1), clean_unit or normalized_unit

    return clean_value, clean_unit


def read_text(path: str | Path) -> str:
    """Read a UTF-8 text file."""

    return Path(path).read_text(encoding="utf-8")


def extract_report(
    raw_text: str,
    *,
    source_name: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
    client: Any | None = None,
) -> ReportExtraction:
    """Extract structured policy observations from raw text using the OpenAI API."""

    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set. Add it to .env or your shell environment.")

        from openai import OpenAI

        client = OpenAI(api_key=api_key)

    try:
        response = client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Source name: {source_name}\n\n"
                        "Extract the macroeconomic and monetary-policy signals from this text:\n\n"
                        f"{raw_text}"
                    ),
                },
            ],
            text_format=ReportExtraction,
            temperature=temperature,
            store=True,
        )
    except Exception as exc:
        message = str(exc)
        if "insufficient_quota" in message:
            raise RuntimeError(
                "OpenAI returned insufficient_quota. Your API key is being read, but the API "
                "account needs billing or credits enabled on platform.openai.com."
            ) from exc
        raise

    extraction = response.output_parsed
    if extraction is None:
        raise RuntimeError("The OpenAI response did not contain parsed structured output.")

    return extraction


def extraction_to_dataframe(
    extraction: ReportExtraction,
    *,
    source_name: str,
) -> pd.DataFrame:
    """Convert a structured extraction into one row per observation."""

    rows: list[dict[str, Any]] = []
    for observation in extraction.observations:
        row = observation.model_dump()
        row["value"], row["unit"] = normalize_value_unit(row["value"], row["unit"])
        row.update(
            {
                "source_name": source_name,
                "report_title": extraction.report_title,
                "central_bank": extraction.central_bank,
                "report_date": extraction.report_date,
                "policy_summary": extraction.policy_summary,
            }
        )
        rows.append(row)

    return pd.DataFrame(rows, columns=DATAFRAME_COLUMNS)


def write_dataframe(df: pd.DataFrame, output_path: str | Path) -> Path:
    """Write the DataFrame to CSV."""

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False)
    return destination


def run_pipeline(
    input_path: str | Path,
    *,
    output_path: str | Path,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
) -> pd.DataFrame:
    """Run the full text-to-DataFrame pipeline."""

    source = Path(input_path)
    raw_text = read_text(source)
    extraction = extract_report(
        raw_text,
        source_name=source.name,
        model=model,
        temperature=temperature,
    )
    df = extraction_to_dataframe(extraction, source_name=source.name)
    write_dataframe(df, output_path)
    return df
