
import pandas as pd
import streamlit as st
from tax_data import REGIMES
from calculations import gross_up, apply_pa_taper, taxable_income, revise_bands_for_giftaid, compute_tax_by_band, bands_to_table

st.set_page_config(page_title="Gift Aid Income Tax Calculator (2025/26)", page_icon="🎁", layout="centered")
st.title("🎁 Gift Aid Income Tax Calculator — 2025/26")

st.header("Inputs")
c1, c2 = st.columns(2)
with c1:
    earnings = st.number_input("Annual earnings (£)", min_value=0.0, value=55000.0, step=100.0, format="%.2f")
    donation = st.number_input("Gift Aid (cash paid) (£)", min_value=0.0, value=4000.0, step=50.0, format="%.2f")
with c2:
    scot = st.toggle("Scottish taxpayer?", value=False)
    regime_key = "Scotland" if scot else "rUK"
    pa_default = REGIMES[regime_key].personal_allowance_default
    pa = st.number_input("Personal Allowance (£)", min_value=0.0, value=pa_default, step=10.0, format="%.2f")
    taper = st.checkbox("Apply >£100k PA taper", value=True)

if taper:
    pa = apply_pa_taper(pa, earnings)

regime = REGIMES[regime_key]
taxable = taxable_income(earnings, pa)
grossed = gross_up(donation)
revised_bands = revise_bands_for_giftaid(regime, grossed)

tax_by_orig, total_orig = compute_tax_by_band(regime.bands, taxable)
tax_by_rev, total_rev = compute_tax_by_band(revised_bands, taxable)

st.header("Summary")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Taxable income", f"£{taxable:,.2f}")
m2.metric("Gift Aid grossed-up", f"£{grossed:,.2f}")
m3.metric("Band extension", f"£{grossed:,.2f}")
m4.metric("Estimated saving", f"£{(total_orig - total_rev):,.2f}")

st.caption("Gift Aid is grossed up by dividing by **0.8**. The grossed-up amount temporarily **extends the relevant band boundary** for the year.")

st.subheader("Rates & bands (taxable income)")
left, right = st.columns(2)
with left:
    st.markdown("**Original bands**")
    st.dataframe(pd.DataFrame(bands_to_table(regime.bands)), hide_index=True, use_container_width=True)
with right:
    st.markdown("**Revised bands (with Gift Aid)**")
    st.dataframe(pd.DataFrame(bands_to_table(revised_bands)), hide_index=True, use_container_width=True)

st.subheader("Tax charged by band")
tab1, tab2, tab3 = st.tabs(["Original", "With Gift Aid extension", "Difference"])
with tab1:
    ordered = [b.name for b in regime.bands]
    df_o = pd.DataFrame({"Band": ordered, "Tax (£)": [round(tax_by_orig[b], 2) for b in ordered]})
    st.dataframe(df_o, hide_index=True, use_container_width=True)
    st.markdown(f"**Total tax:** £{total_orig:,.2f}")

with tab2:
    ordered_r = [b.name for b in revised_bands]
    df_r = pd.DataFrame({"Band": ordered_r, "Tax (£)": [round(tax_by_rev[b], 2) for b in ordered_r]})
    st.dataframe(df_r, hide_index=True, use_container_width=True)
    st.markdown(f"**Total tax (with Gift Aid):** £{total_rev:,.2f}")

with tab3:
    ordered = [b.name for b in regime.bands]
    o_vals = [round(tax_by_orig[b], 2) for b in ordered]
    r_vals = [round(tax_by_rev.get(b, 0.0), 2) for b in ordered]
    d_vals = [round(o - r, 2) for o, r in zip(o_vals, r_vals)]
    df_d = pd.DataFrame({"Band": ordered, "Original (£)": o_vals, "With Gift Aid (£)": r_vals, "Difference (£)": d_vals})
    st.dataframe(df_d, hide_index=True, use_container_width=True)
    st.markdown(f"**Total saving:** £{(total_orig - total_rev):,.2f}")

st.divider()
st.caption("Personal Allowance defaults to £12,570 and may taper above £100,000 of earnings. "
           "Scottish bands: Starter 19%, Basic 20%, Intermediate 21%, Higher 42%, Advanced 45%, Top 48%. "
           "rUK bands: Basic 20%, Higher 40%, Additional 45%.")
