from types import SimpleNamespace

from llm_data_pipeline.extractor import DATAFRAME_COLUMNS, extract_report, extraction_to_dataframe
from llm_data_pipeline.schemas import PolicyObservation, ReportExtraction


def test_extraction_to_dataframe_returns_one_row_per_observation():
    extraction = ReportExtraction(
        report_title="Bank of England Monetary Policy Summary",
        central_bank="Bank of England",
        report_date="6 February 2025",
        policy_summary="The MPC cut rates while keeping restrictive guidance.",
        observations=[
            PolicyObservation(
                metric="Bank Rate",
                value="4.50%",
                unit="%",
                period="6 February 2025",
                direction="down",
                macro_category="policy_rate",
                implication="dovish",
                evidence_quote="reduce Bank Rate by 0.25 percentage points, to 4.50%",
                confidence=0.96,
            ),
            PolicyObservation(
                metric="CPI inflation",
                value="2.5",
                unit="percent",
                period="December 2024",
                direction="up",
                macro_category="inflation",
                implication="hawkish",
                evidence_quote="CPI inflation was 2.5% in December 2024, above the 2% target",
                confidence=0.94,
            ),
        ],
    )

    df = extraction_to_dataframe(extraction, source_name="sample.txt")

    assert list(df.columns) == DATAFRAME_COLUMNS
    assert len(df) == 2
    assert df.loc[0, "metric"] == "Bank Rate"
    assert df.loc[0, "value"] == "4.50"
    assert df.loc[0, "unit"] == "percent"
    assert df.loc[1, "macro_category"] == "inflation"
    assert df.loc[0, "central_bank"] == "Bank of England"


class RecordingResponses:
    def __init__(self, output_parsed):
        self.output_parsed = output_parsed
        self.requests = []

    def parse(self, **kwargs):
        self.requests.append(kwargs)
        return SimpleNamespace(output_parsed=self.output_parsed)


def test_extract_report_omits_temperature_by_default():
    extraction = ReportExtraction(
        report_title="",
        central_bank="",
        report_date="",
        policy_summary="",
        observations=[],
    )
    responses = RecordingResponses(extraction)
    client = SimpleNamespace(responses=responses)

    result = extract_report("Sample text", source_name="sample.txt", client=client)

    assert result is extraction
    assert "temperature" not in responses.requests[0]


def test_extract_report_passes_explicit_temperature():
    extraction = ReportExtraction(
        report_title="",
        central_bank="",
        report_date="",
        policy_summary="",
        observations=[],
    )
    responses = RecordingResponses(extraction)
    client = SimpleNamespace(responses=responses)

    extract_report(
        "Sample text",
        source_name="sample.txt",
        temperature=0.0,
        client=client,
    )

    assert responses.requests[0]["temperature"] == 0.0
