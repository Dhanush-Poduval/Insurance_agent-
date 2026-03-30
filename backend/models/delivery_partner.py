from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class DeliveryPartner(str, Enum):
    MONSANTO = "monsanto"  # Agricultural
    SYNGENTA = "syngenta"
    WORLD_BANK = "world_bank"
    MICROFINANCE_INSTITUTION = "mfi"
    NGO = "ngo"

class PartnerSpecificCoverage(BaseModel):
    partner: DeliveryPartner
    coverage_type: str  # crop_failure, drought, flood, etc.
    min_payout_trigger: float
    max_payout_limit: float
    premium_percentage: float
    geographic_focus: List[str]  # Countries/regions they operate in

class PartnerPolicy(BaseModel):
    partner_id: str
    partner: DeliveryPartner
    coverage_options: List[PartnerSpecificCoverage]
    exclusions: List[str]
    compliance_requirements: dict