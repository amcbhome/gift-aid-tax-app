
from __future__ import annotations
from typing import List, Tuple, Dict
from dataclasses import replace
import math

from tax_data import Band, Regime

def gross_up(donation_net: float) -> float:
    return donation_net / 0.8 if donation_net > 0 else 0.0

def apply_pa_taper(personal_allowance: float, earnings: float) -> float:
    if earnings <= 100000:
        return personal_allowance
    reduction = (earnings - 100000) / 2.0
    return max(0.0, personal_allowance - reduction)

def taxable_income(earnings: float, personal_allowance: float) -> float:
    return max(0.0, earnings - personal_allowance)

def revise_bands_for_giftaid(regime: Regime, grossed_up: float) -> List[Band]:
    bands = [replace(b) for b in regime.bands]
    if grossed_up <= 0:
        return bands
    idx = next((i for i, b in enumerate(bands) if b.name == regime.extension_boundary_band), None)
    if idx is None:
        return bands
    # increase upper of the boundary band
    if math.isfinite(bands[idx].upper):
        bands[idx].upper += grossed_up
    # shift all later bands up
    for j in range(idx + 1, len(bands)):
        bands[j].lower += grossed_up
        if math.isfinite(bands[j].upper):
            bands[j].upper += grossed_up
    return bands

def compute_tax_by_band(bands: List[Band], taxable: float) -> Tuple[Dict[str, float], float]:
    tax_by = {}
    total = 0.0
    for b in bands:
        lower, upper, rate = b.lower, b.upper, b.rate
        span = max(0.0, min(taxable, upper) - lower)
        if span > 0:
            t = span * rate
            tax_by[b.name] = t
            total += t
        else:
            tax_by[b.name] = 0.0
    return tax_by, total

def bands_to_table(bands: List[Band]):
    rows = []
    for b in bands:
        rows.append({
            "Band": b.name,
            "Lower (taxable)": 0.0 if b.lower == 0 else b.lower,
            "Upper (taxable)": float('inf') if not math.isfinite(b.upper) else b.upper,
            "Rate": f"{int(round(b.rate*100))}%",
        })
    return rows
