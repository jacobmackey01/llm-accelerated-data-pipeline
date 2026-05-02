from llm_data_pipeline.extractor import DATAFRAME_COLUMNS, extraction_to_dataframe
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
