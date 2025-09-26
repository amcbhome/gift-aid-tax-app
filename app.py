
import math
import pandas as pd
import streamlit as st

from tax_data import REGIMES
from calculations import gross_up, apply_pa_taper, taxable_income, revise_bands_for_giftaid, compute_tax_by_band, bands_to_table

st.set_page_config(page_title="Gift Aid Income Tax Calculator (2025/26)", page_icon="🎁", layout="centered")
st.title("🎁 Gift Aid Income Tax Calculator — 2025/26")

with st.expander("About & sources"):
    st.markdown(
        """
**What this app does**  
- Calculates how a **Gift Aid** donation affects your **personal income tax** for the **2025/26** tax year.  
- Handles **Scotland** (starter, basic, intermediate, higher, advanced, top) and **rUK** (basic, higher, additional) bands.  
- Shows **revised thresholds** where applicable (Gift Aid extends the relevant boundary by the grossed-up donation).  

**Assumptions**  
- Applies the standard Gift Aid gross-up (donation ÷ 0.8).  
- You can optionally apply the **>£100k Personal Allowance taper**.  
- This calculator focuses on **non-savings, non-dividend income**.  
        """
    )

st.header("Inputs")
col1, col2 = st.columns(2)
with col1:
    earnings = st.number_input("Annual earnings (£)", min_value=0.0, step=100.0, value=55000.0, format="%.2f")
    donation = st.number_input("Gift Aid (cash paid) (£)", min_value=0.0, step=50.0, value=4000.0, format="%.2f")
with col2:
    is_scot = st.toggle("Scottish taxpayer?", value=False)
    pa_default = REGIMES["Scotland" if is_scot else "rUK"].personal_allowance_default
    personal_allowance = st.number_input("Personal Allowance (£)", min_value=0.0, step=10.0, value=pa_default, format="%.2f")
    apply_taper = st.checkbox("Apply >£100k PA taper automatically", value=True)

if apply_taper:
    personal_allowance = apply_pa_taper(personal_allowance, earnings)

regime_key = "Scotland" if is_scot else "rUK"
regime = REGIMES[regime_key]

taxable = taxable_income(earnings, personal_allowance)
grossed = gross_up(donation)
revised_bands = revise_bands_for_giftaid(regime, grossed)

tax_by_original, total_original = compute_tax_by_band(regime.bands, taxable)
tax_by_revised, total_revised = compute_tax_by_band(revised_bands, taxable)

st.header("Summary")
m1, m2, m3 = st.columns(3)
m1.metric("Taxable income", f"£{taxable:,.2f}")
m2.metric("Gift Aid (grossed-up)", f"£{grossed:,.2f}")
m3.metric("Estimated tax saving", f"£{(total_original - total_revised):,.2f}")

st.caption("Gift Aid is grossed up by dividing by **0.8** (assumes 20% basic rate reclaimed by the charity). "
           "The grossed-up amount temporarily extends the relevant band boundary so that more of your income is taxed at lower rates.")

st.subheader("Rates & Bands (Taxable income)")
left, right = st.columns(2)

with left:
    st.markdown("**Original bands**")
    df_orig = pd.DataFrame(bands_to_table(regime.bands))
    st.dataframe(df_orig, hide_index=True, use_container_width=True)

with right:
    st.markdown("**Revised bands for Gift Aid**")
    df_rev = pd.DataFrame(bands_to_table(revised_bands))
    st.dataframe(df_rev, hide_index=True, use_container_width=True)

st.subheader("Tax charged by band")
tab1, tab2 = st.tabs(["Original", "With Gift Aid extension"])
with tab1:
    df_tax_o = pd.DataFrame({"Band": list(tax_by_original.keys()),
                             "Tax (£)": [round(v, 2) for v in tax_by_original.values()]})
    st.dataframe(df_tax_o, hide_index=True, use_container_width=True)
    st.markdown(f"**Total tax:** £{total_original:,.2f}")

with tab2:
    df_tax_r = pd.DataFrame({"Band": list(tax_by_revised.keys()),
                             "Tax (£)": [round(v, 2) for v in tax_by_revised.values()]})
    st.dataframe(df_tax_r, hide_index=True, use_container_width=True)
    st.markdown(f"**Total tax (with Gift Aid):** £{total_revised:,.2f}")

st.divider()
st.caption(
    "Notes:\n"
    "- Personal Allowance defaults to £12,570 and may taper above £100,000 of earnings. "
    "- Gift Aid does not restore any Personal Allowance lost to tapering; it **extends band thresholds** for the year."
)
