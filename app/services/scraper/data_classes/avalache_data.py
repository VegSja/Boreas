from typing import Optional
from dataclasses import dataclass


@dataclass
class VarsomAvalancheResponse:
    RegId: int
    RegionId: int
    RegionName: Optional[str]
    RegionTypeId: int
    RegionTypeName: Optional[str]
    DangerLevel: Optional[str]
    ValidFrom: Optional[str]
    ValidTo: Optional[str]
    NextWarningTime: Optional[str]
    PublishTime: Optional[str]
    DangerIncreaseTime: Optional[str]
    DangerDecreaseTime: Optional[str]
    MainText: Optional[str]
    LangKey: int
