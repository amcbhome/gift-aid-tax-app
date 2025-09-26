
from dataclasses import dataclass
from typing import List
import math

@dataclass
class Band:
    name: str
    lower: float
    upper: float
    rate: float

@dataclass
class Regime:
    name: str
    personal_allowance_default: float
    bands: List[Band]
    extension_boundary_band: str

rUK_2025_26 = Regime(
    name="Rest of UK (rUK) 2025/26",
    personal_allowance_default=12570.0,
    bands=[
        Band("Basic rate (20%)", 0, 37700, 0.20),
        Band("Higher rate (40%)", 37700, 125140, 0.40),
        Band("Additional rate (45%)", 125140, math.inf, 0.45),
    ],
    extension_boundary_band="Basic rate (20%)",
)

scotland_2025_26 = Regime(
    name="Scotland 2025/26",
    personal_allowance_default=12570.0,
    bands=[
        Band("Starter (19%)", 0, 2827, 0.19),
        Band("Basic (20%)", 2827, 14921, 0.20),
        Band("Intermediate (21%)", 14921, 31092, 0.21),
        Band("Higher (42%)", 31092, 62430, 0.42),
        Band("Advanced (45%)", 62430, 112570, 0.45),
        Band("Top (48%)", 112570, math.inf, 0.48),
    ],
    extension_boundary_band="Intermediate (21%)",
)

REGIMES = {"rUK": rUK_2025_26, "Scotland": scotland_2025_26}
