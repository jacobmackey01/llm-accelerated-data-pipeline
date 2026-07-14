# LLM-Accelerated Data Pipeline

A small, portfolio-ready Python pipeline that extracts structured macro signals from unstructured central bank text using the OpenAI API, then loads the result into a Pandas DataFrame.

> **Current API model:** `gpt-5.6-luna` via the OpenAI Responses API.

The point is not to build a chatbot. The point is to automate the first stage of exploratory data analysis when quantitative workflows need facts buried in speeches, reports, minutes, or policy statements.

## What It Does

1. Reads a raw text file, such as a central bank report excerpt.
2. Sends the text to the OpenAI Responses API with a strict extraction prompt.
3. Uses Structured Outputs with a Pydantic schema so the response is machine-readable.
4. Uses a strict extraction prompt and evidence quotes to keep results focused and auditable.
5. Converts the parsed result into a Pandas DataFrame and writes it to CSV.

## Cobblestone Soundbite

> I noticed quantitative models frequently need data from unstructured text, like central bank reports. So, I built a Python pipeline using the OpenAI API. Instead of a chat interface, I pass the raw text to the API with a strict system prompt and Structured Outputs, requiring the LLM to extract only the entities I need and output them directly into a Pandas DataFrame. It basically automates the first stage of exploratory data analysis.

## Project Structure

```text
.
|-- sample_data/
|   `-- boe_monetary_policy_excerpt.txt
|-- src/
|   `-- llm_data_pipeline/
|       |-- __init__.py
|       |-- cli.py
|       |-- extractor.py
|       `-- schemas.py
|-- tests/
|   `-- test_dataframe.py
|-- .env.example
|-- .gitignore
|-- pyproject.toml
`-- README.md
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
```

Add your API key to `.env`:

```text
OPENAI_API_KEY=your_api_key_here
```

## Run The Pipeline

```bash
llm-data-pipeline sample_data/boe_monetary_policy_excerpt.txt --output outputs/boe_signals.csv
```

Or run it as a module:

```bash
python -m llm_data_pipeline.cli sample_data/boe_monetary_policy_excerpt.txt --output outputs/boe_signals.csv
```

The default model is `gpt-5.6-luna`. You can override it:

```bash
llm-data-pipeline sample_data/boe_monetary_policy_excerpt.txt --model gpt-5.4 --output outputs/boe_signals.csv
```

The pipeline explicitly uses `reasoning.effort="low"` for this bounded extraction task, avoiding GPT-5.6's default medium effort. It omits `temperature` by default because `gpt-5.6-luna` does not support that parameter. If you override the model with one that supports temperature, you can pass `--temperature` explicitly.

### Why Low Reasoning Effort?

The model is performing a bounded mapping task: it receives one supplied document and fills a predefined Pydantic schema. It is not browsing, calling tools, or planning across multiple steps. `low` therefore provides a better latency and reasoning-token tradeoff than GPT-5.6's default `medium` setting for this workload. It is not a determinism or accuracy guarantee: the schema controls output shape, the prompt and evidence quotes support auditability, and the existing tests cover request construction and tabular transformation. Extraction quality still needs to be measured on representative documents. If those evaluations show that ambiguous or deeply nested documents gain meaningful field accuracy from `medium`, the setting should be raised. This follows [OpenAI's guidance](https://developers.openai.com/api/docs/guides/latest-model) to use `low` for latency-sensitive workloads and choose higher effort only when it produces a measured quality gain.

## Platform Smoke Test

OpenAI's Platform sample uses `OpenAI(...)`, `client.responses.create(...)`, and `response.output_text`. This repo includes the same pattern, with the API key loaded from `.env` rather than pasted into source code:

```bash
python examples/platform_smoke_test.py
```

## Example Output Columns

The CSV contains one row per extracted signal:

```text
source_name,report_title,central_bank,report_date,metric,value,unit,period,direction,macro_category,implication,evidence_quote,confidence
```

Example rows might identify inflation, GDP growth, unemployment, or rate-path statements, with a quote from the source text attached as evidence.

## Why This Is Useful

Quantitative workflows often start with a messy ingestion problem:

- policy statements are prose-heavy;
- key macro signals are not always in tables;
- analysts need consistent columns before they can test factors or build dashboards;
- manual extraction does not scale.

This project demonstrates the handoff from unstructured text to structured research data:

```text
central bank text -> OpenAI structured extraction -> Pydantic object -> Pandas DataFrame -> CSV
```

## Notes On Reliability

- The default API call uses low reasoning effort and omits unsupported sampling parameters for `gpt-5.6-luna`.
- Structured Outputs forces the model to match the schema.
- The prompt tells the model not to infer facts absent from the text.
- Each extracted observation includes an `evidence_quote` for traceability.
- The included tests validate the DataFrame transformation without calling the API.

## Official OpenAI References

- [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs?api-mode=responses&lang=python)
- [Responses API reference](https://platform.openai.com/docs/api-reference/responses/object)
- [OpenAI model guide](https://developers.openai.com/api/docs/models)
