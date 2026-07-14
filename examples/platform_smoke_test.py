"""Minimal OpenAI Platform-style smoke test.

This mirrors the Python sample shown on platform.openai.com, but keeps the
API key in `.env` instead of hard-coding it into source code.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to .env first.")

    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            input="write a haiku about ai",
            reasoning={"effort": "low"},
            store=True,
        )
    except Exception as exc:
        if "insufficient_quota" in str(exc):
            raise RuntimeError(
                "OpenAI returned insufficient_quota. The SDK call matches the Platform sample, "
                "but this API project needs billing or credits enabled."
            ) from exc
        raise

    print(response.output_text)


if __name__ == "__main__":
    main()
