import pandas as pd
import streamlit as st

def metric_card(label, value, help_text=None):
    st.metric(label=label, value=value, help=help_text)

def human_review_banner(required: bool):
    if required:
        st.warning("⚠ Human review required before a sensitive action can proceed.")
    else:
        st.success("No additional human review is required by the current policy rule.")

def show_probability_table(probabilities: dict):
    if not probabilities:
        return
    df = pd.DataFrame([
        {"Class": key, "Probability": value}
        for key, value in probabilities.items()
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

def show_policy_fields(policy: dict):
    if not policy:
        st.info("No policy information available.")
        return

    fields = [
        "POLICY_ID","CUSTOMER_ID","POLICY_TYPE","POLICY_STATUS",
        "SALES_CHANNEL","PAYMENT_MODE","SUM_INSURED","ANNUAL_PREMIUM",
        "RISK_SCORE","RISK_BAND","CUSTOMER_RISK_SEGMENT","STATE",
        "TOTAL_CLAIMS","UW_DECISION","HAS_FINALIZED_RENEWAL","RENEWED_FLAG"
    ]

    rows = [
        {"Field": field, "Value": policy.get(field)}
        for field in fields
        if field in policy
    ]

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
