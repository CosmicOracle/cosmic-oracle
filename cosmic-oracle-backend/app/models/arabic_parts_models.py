from pydantic import BaseModel, Field
from typing import List, Dict, Any

class InterpretationDetail(BaseModel):
    title: str
    summary: str
    by_house: str

class ArabicPartDetail(BaseModel):
    name: str
    sign: str
    degree_string: str
    longitude: float
    house: int
    interpretation: InterpretationDetail

class ArabicPartsReport(BaseModel):
    chart_type: str
    parts: List[ArabicPartDetail]

class ArabicPartsResponse(BaseModel):
    arabic_parts_report: ArabicPartsReport
    natal_chart_used: Dict[str, Any]