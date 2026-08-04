from dataclasses import dataclass, asdict, field
from typing import Optional, List


@dataclass
class Scholarship:
    title: str
    provider: str = ""
    source: str = ""
    source_type: str = "official"

    destination_countries: List[str] = field(default_factory=list)
    eligible_countries: List[str] = field(default_factory=list)

    degree_levels: List[str] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    funding_type: List[str] = field(default_factory=list)

    deadline: Optional[str] = None
    start_date: Optional[str] = None
    duration: Optional[str] = None

    description: str = ""
    official_url: str = ""

    status: str = "unknown"
    last_checked: Optional[str] = None

    def to_dict(self):
        return asdict(self)
