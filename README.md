# Mortgage Document Assistant

A FastAPI service that reads mortgage application documents (pay stubs, employment letters) and extracts structured, validated data using LLM structured outputs.

**Core principle:** missing data is marked as missing, never guessed. In lending, a guessed value is worse than a missing one.

## What it does today

`POST /extract` takes a plain-text document and returns:

```json
{
  "data": {
    "applicant_name": "Priya Raman",
    "employer": "Northwind Logistics Inc.",
    "gross_annual_income": null,
    "pay_frequency": "biweekly",
    "employment_start_date": null
  },
  "missing_fields": ["gross_annual_income", "employment_start_date"]
}
```

## Design decisions

- **Schema-constrained output:** uses Claude structured outputs (`client.messages.parse()`) with a Pydantic model, so responses always match the schema.
- **Strict validation:** `pay_frequency` is limited to fixed values, and dates must be real dates.
- **No guessing:** the model only extracts values the document states. It does not annualize pay or treat year-to-date totals as annual income.
- **Deterministic `missing_fields`:** computed in Python from the validated output, not by the LLM.
- **Synthetic data only:** sample documents are made up, because real pay stubs contain PII.

## Tech stack

Python, FastAPI, Pydantic, Anthropic Python SDK

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with `ANTHROPIC_API_KEY=your-key`, then:

```bash
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs and upload a file from `samples/`.

## Roadmap

- [ ]