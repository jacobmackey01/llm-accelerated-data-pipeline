# Cobblestone Pitch Notes

## 30-Second Version

I built a Python pipeline that turns unstructured central bank text into structured research data. It uses the OpenAI API directly, not ChatGPT, with a strict extraction schema and `temperature=0`. The output is parsed into a Pydantic object, flattened into a Pandas DataFrame, and exported to CSV for downstream analysis.

## Why It Fits The Role

Cobblestone cares about AI-accelerated workflows. This project shows that I can apply an LLM to a real data bottleneck rather than treating it as a generic chat tool. The workflow is useful anywhere a quantitative model needs clean features from messy prose: central bank reports, earnings calls, macro commentary, policy minutes, or broker notes.

## Technical Details To Mention

- The pipeline calls the OpenAI API from Python scripts.
- The system prompt constrains the model to extract only facts present in the source text.
- Structured Outputs force the response into a typed Pydantic schema.
- `temperature=0` keeps extraction focused and repeatable.
- Pandas turns the parsed objects into rows for analysis.
- Evidence quotes are stored beside each observation for auditability.

## Interview Walkthrough

1. Show the sample input text in `sample_data/`.
2. Show the extraction schema in `src/llm_data_pipeline/schemas.py`.
3. Show the API call in `src/llm_data_pipeline/extractor.py`.
4. Run the CLI and open the resulting CSV.
5. Explain how this could scale to batch extraction across many reports.

## Natural Follow-Up Ideas

- Add batch processing for a folder of reports.
- Store outputs in SQLite or DuckDB.
- Add validation checks against known macro series.
- Compare extracted sentiment against rate moves or bond yields.
