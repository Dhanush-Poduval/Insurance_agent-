from enum import Enum
from typing import List
from pydantic import BaseModel
from datetime import datetime

class ExclusionType(str, Enum):
    WAR = "war"
    PANDEMIC = "pandemic"
    CIVIL_UNREST = "civil_unrest"
    TERRORISM = "terrorism"
    NUCLEAR = "nuclear"
    BIOLOGICAL = "biological"

class Exclusion(BaseModel):
    exclusion_type: ExclusionType
    description: str
    coverage_percentage: float  # 0-100%, how much is excluded
    effective_from: datetime
    effective_to: datetime
    regions: List[str]  # Geographic applicability

class PolicyExclusions(BaseModel):
    policy_id: str
    exclusions: List[Exclusion]
    total_excluded_percentage: float
    
    def is_excluded(self, event_type: str, region: str) -> bool:
        """Check if an event is excluded for a given region"""
        for exclusion in self.exclusions:
            if exclusion.exclusion_type.value == event_type and region in exclusion.regions:
                return True
        return False