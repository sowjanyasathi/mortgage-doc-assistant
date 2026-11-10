from datetime import date
from typing import Literal

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel, Field

load_dotenv()                 # loads ANTHROPIC_API_KEY from .env
client = Anthropic()          # reads the key from the environment
app = FastAPI(title="Mortgage Document Assistant")
MODEL = "claude-haiku-5-5"    # fast and cheap; enough for extraction
class IncomeDocExtraction(BaseModel):
    applicant_name: str | None = Field(None, description="Employee's full name as written")
    employer: str | None = Field(None, description="Employer company name")
    gross_annual_income: float | None = Field(
        None, description="Annual gross income ONLY if explicitly stated. Never calculate it."
    )
    pay_frequency: Literal["weekly", "biweekly", "semi_monthly", "monthly"] | None = None
    employment_start_date: date | None = Field(None, description="Hire/start date")


class ExtractionResponse(BaseModel):
    data: IncomeDocExtraction
    missing_fields: list[str]


SYSTEM_PROMPT = """You extract data from mortgage application documents.
Rules:
- Only extract values explicitly stated in the document.
- If a value is not stated, return null. Never guess, infer, or calculate.
- Do not annualize pay (e.g. never multiply per-period pay by 26)."""

@app.post("/extract", response_model=ExtractionResponse)
def extract(file: UploadFile):
    text = file.file.read().decode("utf-8")

    response = client.messages.parse(
        model=MODEL,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"<document>\n{text}\n</document>"}],
        output_format=IncomeDocExtraction,
    )

    data = response.parsed_output
    if data is None:
        raise HTTPException(status_code=502, detail="Model returned no valid extraction")

    missing = [field for field, value in data.model_dump().items() if value is None]
    return ExtractionResponse(data=data, missing_fields=missing)