from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel, ConfigDict, Field


class Failures(BaseModel):
    time: int  # there are negative values in spaceX data T-minus - time before failure
    altitude: int | None = Field(default=None, ge=0)
    reason: str


class Rocket(BaseModel):
    """Rocket model"""

    id: str
    name: str
    # type: str
    # stages: int
    # boosters: int
    # cost_per_launch: int
    # success_rate_pct: int
    # first_flight: str
    # country: str
    # company: str
    # wikipedia: str
    # description: str

    model_config = ConfigDict(extra="ignore")


class Launch(BaseModel):
    """Launch model"""

    id: str
    name: str
    date_utc: str
    date_unix: int
    rocket: str
    launchpad: str
    success: Optional[bool] = None
    details: Optional[str] = None
    links: Dict[str, Any] = Field(default_factory=dict)
    failures: List[Failures] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


class Launchpad(BaseModel):
    """Launchpad model"""

    id: str
    name: str
    full_name: str
    locality: str
    region: str
    latitude: float
    longitude: float
    launches: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


class FilterQuery(BaseModel):
    """Filtering model"""

    date_from: Optional[int] = None
    date_to: Optional[int] = None
    success: Optional[str] = None
    rocket: Optional[str] = None
    launchpad: Optional[str] = None


class ChartData(TypedDict):
    labels: List[str]
    values: List[float]


class FrequencyData(TypedDict):
    labels: List[int]
    values: List[List[int]]


class AnalyticsResponse(TypedDict):
    successByRocket: ChartData
    launchesBySite: ChartData
    frequencyByYear: FrequencyData
