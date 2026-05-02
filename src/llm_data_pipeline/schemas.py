"""Typed schemas used for strict LLM extraction."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Direction = Literal["up", "down", "flat", "mixed", "unclear"]
MacroCategory = Literal[
    "inflation",
    "growth",
    "labor_market",
    "policy_rate",
    "financial_conditions",
    "exchange_rate",
    "other",
]
PolicyImplication = Literal["hawkish", "dovish", "neutral", "mixed", "unclear"]


class PolicyObservation(BaseModel):
    """One research-ready signal extracted from a source document."""

    model_config = ConfigDict(extra="forbid")

    metric: str = Field(description="The macro metric, entity, or policy variable mentioned.")
    value: str = Field(description="The reported value without unit symbols, or an empty string if no explicit value is present.")
    unit: str = Field(description="The unit attached to the value, such as percent or percentage points, or an empty string if absent.")
    period: str = Field(description="The date or period the observation refers to, or an empty string if absent.")
    direction: Direction = Field(description="Whether the text says this metric moved up, down, flat, mixed, or unclear.")
    macro_category: MacroCategory = Field(description="The broad macro category for the observation.")
    implication: PolicyImplication = Field(description="Likely policy implication, based only on the source wording.")
    evidence_quote: str = Field(description="A short direct quote from the source text supporting the observation.")
    confidence: float = Field(description="Model confidence from 0 to 1.")


class ReportExtraction(BaseModel):
    """Structured extraction output for one document."""

    model_config = ConfigDict(extra="forbid")

    report_title: str = Field(description="Title or inferred source name from the provided text.")
    central_bank: str = Field(description="The central bank or institution named in the text.")
    report_date: str = Field(description="The publication or decision date, or an empty string if absent.")
    policy_summary: str = Field(description="One concise sentence summarizing the policy signal in the text.")
    observations: list[PolicyObservation] = Field(description="Extracted macro and policy observations.")
