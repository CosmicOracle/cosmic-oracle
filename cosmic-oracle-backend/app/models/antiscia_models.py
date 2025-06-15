from pydantic import BaseModel, Field
from typing import List, Dict, Any

class AntisciaPoint(BaseModel):
    original_point: str
    original_longitude: float
    antiscia_longitude: float

class ContraAntisciaPoint(BaseModel):
    original_point: str
    original_longitude: float
    contra_antiscia_longitude: float

class AntisciaAnalysis(BaseModel):
    antiscia_points: List[AntisciaPoint]
    contra_antiscia_points: List[ContraAntisciaPoint]

class AntisciaResponse(BaseModel):
    antiscia_analysis: AntisciaAnalysis
    natal_chart_used: Dict[str, Any]