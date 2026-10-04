import json
import os
import sys
import uuid
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from dashboard.api_client import (
    InsuranceAPIClient
)


# ==========================================================
# Page config
# ==========================================================

st.set_page_config(
    page_title=
        "Insurance AI Copilot",

    page_icon=
        "🛡️",

    layout=
        "wide",

    initial_sidebar_state=
        "expanded",
)


# ==========================================================
# Small visual styling
# ==========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    .risk-high {
        padding: 12px;
        border-radius: 10px;
        background: rgba(255, 75, 75, 0.12);
        border: 1px solid rgba(255, 75, 75, 0.35);
    }

    .risk-medium {
        padding: 12px;
        border-radius: 10px;
        background: rgba(255, 193, 7, 0.12);
        border: 1px solid rgba(255, 193, 7, 0.35);
    }

    .risk-low {
        padding: 12px;
        border-radius: 10px;
        background: rgba(40, 167, 69, 0.12);
        border: 1px solid rgba(40, 167, 69, 0.35);
    }

    .human-review {
        padding: 12px;
        border-radius: 10px;
        background: rgba(111, 66, 193, 0.10);
        border: 1px solid rgba(111, 66, 193, 0.30);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# State
# ==========================================================

if (
    "ai_session_id"
    not in st.session_state
):
    st.session_state[
        "ai_session_id"
    ] = str(
        uuid.uuid4()
    )


if (
    "chat_messages"
    not in st.session_state
):
    st.session_state[
        "chat_messages"
    ] = []


if (
    "api_url"
    not in st.session_state
):
    st.session_state[
        "api_url"
    ] = (
        os.getenv("API_BASE_URL", "http://127.0.0.1:8001")
    )


# ==========================================================
# Helpers
# ==========================================================

def get_client():

    return InsuranceAPIClient(
        base_url=
            st.session_state[
                "api_url"
            ]
    )


def show_api_error(
    error
):

    if isinstance(
        error,
        requests.exceptions.ConnectionError
    ):

        st.error(
            "FastAPI backend is not reachable. "
            "Start Uvicorn on port 8001."
        )

        return


    if isinstance(
        error,
        requests.exceptions.HTTPError
    ):

        response = error.response

        try:
            detail = (
                response.json()
            )

        except Exception:
            detail = response.text

        st.error(
            f"API error: {detail}"
        )

        return


    st.error(
        f"Unexpected error: {error}"
    )


def display_decision(
    decision
):

    if not decision:
        return


    if decision.get(
        "human_review_required"
    ):

        st.markdown(
            """
            <div class="human-review">
            <b>⚠ Human Review Required</b>
            </div>
            """,
            unsafe_allow_html=True,
        )


    recommended = (
        decision.get(
            "recommended_action"
        )
    )


    reason = (
        decision.get(
            "reason"
        )
    )


    if recommended:

        st.write(
            "**Recommended action:**",
            recommended
        )


    if reason:

        st.write(
            "**Reason:**",
            reason
        )


def display_risk_band(
    band
):

    if not band:
        return


    band_text = str(
        band
    ).lower()


    css_class = (
        "risk-high"
        if band_text == "high"
        else
        "risk-medium"
        if band_text == "medium"
        else
        "risk-low"
    )


    st.markdown(
        f"""
        <div class="{css_class}">
        <b>Risk Band: {band}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )


def currency_inr(value):
    try:
        value = float(value or 0)
    except Exception:
        return "-"

    crore = value / 10_000_000
    if crore >= 1:
        return f"₹{crore:,.2f} Cr"

    lakh = value / 100_000
    if lakh >= 1:
        return f"₹{lakh:,.2f} L"

    return f"₹{value:,.0f}"


# ==========================================================
# Sidebar
# ==========================================================

st.sidebar.title(
    "🛡️ Insurance AI"
)

st.sidebar.caption(
    "Decision Intelligence Copilot"
)


page = st.sidebar.radio(
    "Navigate",
    [
        "Overview",
        "AI Copilot",
        "Policy 360",
        "Renewal Risk",
        "Fraud Screening",
        "Underwriting",
        "Human Review",
        "AI Audit",
        "System Status",
    ],
)


st.sidebar.divider()


st.sidebar.text_input(
    "FastAPI URL",
    key="api_url",
)


client = get_client()


if st.sidebar.button(
    "Check Backend"
):

    try:

        health = (
            client.health()
        )

        if (
            health.get(
                "api"
            )
            ==
            "healthy"
        ):

            st.sidebar.success(
                "API connected"
            )

        else:

            st.sidebar.warning(
                str(
                    health
                )
            )


    except Exception as error:

        show_api_error(
            error
        )


st.sidebar.caption(
    "LLM: Ollama / Qwen"
)

st.sidebar.caption(
    "Backend: FastAPI"
)

st.sidebar.caption(
    "ML: Renewal + Fraud + Underwriting"
)


# ==========================================================
# OVERVIEW
# ==========================================================

if page == "Overview":

    st.title("Insurance AI Copilot")
    st.caption("Portfolio overview from the trusted SQL Policy-360 layer.")

    try:
        summary = client.portfolio_summary()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Policies", f"{summary.get('TOTAL_POLICIES', 0):,}")
        c2.metric("Policy Customers", f"{summary.get('TOTAL_POLICY_CUSTOMERS', 0):,}")
        c3.metric("Annual Premium", currency_inr(summary.get('TOTAL_ANNUAL_PREMIUM')))
        c4.metric("Avg Premium", currency_inr(summary.get('AVG_ANNUAL_PREMIUM')))

        c1, c2, c3 = st.columns(3)
        c1.metric("Source-Reported Active", f"{summary.get('SOURCE_REPORTED_ACTIVE_POLICIES', 0):,}")
        c2.metric("Policies With Claims", f"{summary.get('POLICIES_WITH_CLAIMS', 0):,}")
        c3.metric("Finalized Renewals", f"{summary.get('FINALIZED_RENEWALS', 0):,}")

        st.info("Source-reported active status is not a reconstructed as-of-date in-force calculation.")

    except Exception as error:
        show_api_error(error)


# ==========================================================
# AI COPILOT
# ==========================================================

elif page == "AI Copilot":

    st.title(
        "Insurance AI Copilot"
    )

    st.caption(
        "Ask natural-language questions. "
        "The Copilot can use SQL, ML models, "
        "insurance knowledge and human-review guardrails."
    )


    top_col_1, top_col_2 = (
        st.columns(
            [
                3,
                1
            ]
        )
    )


    with top_col_1:

        st.caption(
            "Session ID: "
            +
            st.session_state[
                "ai_session_id"
            ]
        )


    with top_col_2:

        if st.button(
            "New Conversation"
        ):

            st.session_state[
                "ai_session_id"
            ] = str(
                uuid.uuid4()
            )

            st.session_state[
                "chat_messages"
            ] = []

            st.rerun()


    for message in (
        st.session_state[
            "chat_messages"
        ]
    ):

        with st.chat_message(
            message[
                "role"
            ]
        ):

            st.markdown(
                message[
                    "content"
                ]
            )


    user_message = (
        st.chat_input(
            "Ask about a policy, renewal risk, fraud, underwriting, or insurance process..."
        )
    )


    if user_message:

        st.session_state[
            "chat_messages"
        ].append({
            "role":
                "user",

            "content":
                user_message,
        })


        with st.chat_message(
            "user"
        ):

            st.markdown(
                user_message
            )


        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Analyzing..."
            ):

                try:

                    result = (
                        client.chat_ai(
                            message=
                                user_message,

                            session_id=
                                st.session_state[
                                    "ai_session_id"
                                ],
                        )
                    )


                    assistant_text = (
                        result.get(
                            "message",
                            "No response returned."
                        )
                    )


                    st.markdown(
                        assistant_text
                    )


                    st.session_state[
                        "chat_messages"
                    ].append({
                        "role":
                            "assistant",

                        "content":
                            assistant_text,
                    })


                except Exception as error:

                    show_api_error(
                        error
                    )


# ==========================================================
# POLICY 360
# ==========================================================

elif page == "Policy 360":

    st.title("Policy 360")
    policy_id = st.text_input("Policy ID", placeholder="Enter a real policy ID")

    if st.button("Load Policy", type="primary"):
        if not policy_id:
            st.warning("Enter a Policy ID.")
        else:
            try:
                policy = client.policy_summary(policy_id.strip())
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Policy Type", policy.get("POLICY_TYPE", "-"))
                c2.metric("Status", policy.get("POLICY_STATUS", "-"))
                c3.metric("Annual Premium", currency_inr(policy.get("ANNUAL_PREMIUM")))
                c4.metric("Risk Band", policy.get("RISK_BAND", "-"))

                rows = [
                    {"Field": key, "Value": value}
                    for key, value in policy.items()
                ]
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

            except Exception as error:
                show_api_error(error)


# ==========================================================
# RENEWAL
# ==========================================================

elif page == "Renewal Risk":

    st.title(
        "Renewal Risk Assessment"
    )

    st.caption(
        "Predict non-renewal risk for an existing policy."
    )


    policy_id = st.text_input(
        "Policy ID",
        placeholder=
            "Example: POL123",
    )


    if st.button(
        "Assess Renewal Risk",
        type="primary",
    ):

        if not policy_id:

            st.warning(
                "Enter a policy ID."
            )

        else:

            try:

                result = client.renewal(
                    policy_id.strip()
                )


                prediction = (
                    result.get(
                        "prediction",
                        {}
                    )
                )


                decision = (
                    result.get(
                        "decision",
                        {}
                    )
                )


                col1, col2, col3 = (
                    st.columns(3)
                )


                col1.metric(
                    "Non-Renewal Risk",
                    (
                        f"{prediction.get('non_renewal_risk_pct', 0)}%"
                    )
                )


                col2.metric(
                    "Risk Band",
                    prediction.get(
                        "risk_band",
                        "-"
                    )
                )


                col3.metric(
                    "Human Review",
                    (
                        "Required"
                        if decision.get(
                            "human_review_required"
                        )
                        else
                        "No"
                    )
                )


                display_risk_band(
                    prediction.get(
                        "risk_band"
                    )
                )


                st.subheader(
                    "Decision Support"
                )

                display_decision(
                    decision
                )


                if result.get(
                    "message"
                ):

                    st.info(
                        result[
                            "message"
                        ]
                    )


                if result.get(
                    "human_review_id"
                ):

                    st.write(
                        "**Review ID:**",
                        result[
                            "human_review_id"
                        ]
                    )


                with st.expander(
                    "Raw API Response"
                ):

                    st.json(
                        result
                    )


            except Exception as error:

                show_api_error(
                    error
                )


# ==========================================================
# FRAUD
# ==========================================================

elif page == "Fraud Screening":

    st.title("Fraud Risk Screening")
    st.warning(
        "Fraud model output is an investigation signal, "
        "not proof of fraud and not an automatic claim rejection."
    )

    if "fraud_data" not in st.session_state:
        st.session_state.fraud_data = {}

    # Fetch section using existing Policy ID
    st.markdown("### Fetch Policy Details for Screening")
    col_f1, col_f2 = st.columns([3, 1])
    with col_f1:
        fetch_policy_id = st.text_input("Enter Policy ID to Auto-fill", value="POL00004")
    with col_f2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Fetch Data"):
            try:
                base_url = st.session_state["api_url"]
                response = requests.get(f"{base_url}/policy/{fetch_policy_id.strip()}/details")
                if response.status_code == 200:
                    st.session_state.fraud_data = response.json()
                    st.success("Data loaded successfully from Policy 360 mart!")
                else:
                    st.error("Policy ID not found.")
            except Exception as e:
                st.error("Backend connection error.")

    st.divider()
    data = st.session_state.fraud_data

    with st.form("fraud_form"):
        c1, c2, c3 = st.columns(3)
        claim_id = c1.text_input("Claim ID", value="CLM000000015")
        claim_amount = c2.number_input("Claim Amount", value=50000.0)
        reporting_delay = c3.number_input("Reporting Delay Days", value=2, step=1)

        c1, c2, c3 = st.columns(3)
        incident_month = c1.number_input("Incident Month", min_value=1, max_value=12, value=6)
        age = c2.number_input("Age", value=int(data.get("AGE", 40)))
        income = c3.number_input("Annual Income", value=float(data.get("ANNUAL_INCOME", 800000.0)))

        c1, c2, c3 = st.columns(3)
        credit_score = c3.number_input("Credit Score", value=int(data.get("CREDIT_SCORE", 700)))
        sum_insured = c1.number_input("Sum Insured", value=float(data.get("SUM_INSURED", 500000.0)))
        annual_premium = c2.number_input("Annual Premium", value=float(data.get("ANNUAL_PREMIUM", 15000.0)))

        risk_score = st.number_input("Policy Risk Score", value=float(data.get("RISK_SCORE", 0.5)))

        c1, c2, c3 = st.columns(3)
        claim_type = c1.text_input("Claim Type", value="Accident")
        source = c2.text_input("Source", value="Online")
        claim_severity = c3.text_input("Claim Severity", value="Medium")

        c1, c2, c3 = st.columns(3)
        gender = c1.text_input("Gender", value=str(data.get("GENDER", "Male")))
        marital_status = c2.text_input("Marital Status", value=str(data.get("MARITAL_STATUS", "Married")))
        occupation = c3.text_input("Occupation", value=str(data.get("OCCUPATION", "Salaried")))

        c1, c2, c3 = st.columns(3)
        state = c1.text_input("State", value=str(data.get("STATE", "Karnataka")))
        customer_risk = c2.text_input("Customer Risk Segment", value=str(data.get("CUSTOMER_RISK_SEGMENT", "Medium")))
        policy_type = c3.text_input("Policy Type", value=str(data.get("POLICY_TYPE", "Health")))

        c1, c2 = st.columns(2)
        payment_mode = c1.text_input("Payment Mode", value=str(data.get("PAYMENT_MODE", "Annual")))
        risk_band = c2.text_input("Policy Risk Band", value=str(data.get("RISK_BAND", "Medium")))

        submitted = st.form_submit_button("Run Fraud Screening", type="primary")

    if submitted:
        payload = {
            "CLAIM_ID": claim_id,
            "CLAIM_AMOUNT": claim_amount,
            "REPORTING_DELAY_DAYS": int(reporting_delay),
            "INCIDENT_MONTH": int(incident_month),
            "AGE": int(age),
            "ANNUAL_INCOME": income,
            "CREDIT_SCORE": int(credit_score),
            "SUM_INSURED": sum_insured,
            "ANNUAL_PREMIUM": annual_premium,
            "RISK_SCORE": risk_score,
            "CLAIM_TYPE": claim_type,
            "SOURCE": source,
            "CLAIM_SEVERITY": claim_severity,
            "GENDER": gender,
            "MARITAL_STATUS": marital_status,
            "OCCUPATION": occupation,
            "STATE": state,
            "CUSTOMER_RISK_SEGMENT": customer_risk,
            "POLICY_TYPE": policy_type,
            "PAYMENT_MODE": payment_mode,
            "RISK_BAND": risk_band,
        }
        try:
            result = client.fraud(payload)
            prediction = result.get("prediction", {})
            decision = result.get("decision", {})
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Fraud Risk", f"{prediction.get('fraud_risk_pct', 0)}%")
            c2.metric("Alert", prediction.get("prediction", "-"))
            c3.metric("Human Review", "Required" if decision.get("human_review_required") else "No")
            
            display_decision(decision)
            with st.expander("Raw API Response"):
                st.json(result)
        except Exception as error:
            show_api_error(error)


# elif page == "Fraud Screening":

#     st.title("Fraud Risk Screening")

#     st.warning(
#         "Fraud model output is an investigation signal, "
#         "not proof of fraud and not an automatic claim rejection."
#     )

#     # 1. Initialize State for Auto-fill Data
#     if "claim_data" not in st.session_state:
#         st.session_state.claim_data = {}

#     # 2. Fetch Section (OUTSIDE the form so it doesn't trigger a full submission)
#     st.markdown("### Fetch Claim Details")
#     col1, col2 = st.columns([3, 1])
#     with col1:
#         fetch_claim_id = st.text_input("Enter Claim ID to Auto-fill", value="POL000051250")
#     with col2:
#         st.markdown("<br>", unsafe_allow_html=True)
#         if st.button("Fetch Details"):
#             try:
#                 base_url = st.session_state["api_url"]
#                 response = requests.get(f"{base_url}/claim/{fetch_claim_id.strip()}/details")
#                 if response.status_code == 200:
#                     st.session_state.claim_data = response.json()
#                     st.session_state.claim_data["CLAIM_ID"] = fetch_claim_id.strip()
#                     st.success("Data Autofilled Successfully!")
#                 else:
#                     st.error("Claim ID not found in database.")
#             except Exception as e:
#                 st.error("Failed to connect to backend.")

#     st.divider()

#     # 3. Load Data from State (Defaulting to basic values if empty)
#     data = st.session_state.claim_data

#     with st.form("fraud_form"):
#         c1, c2, c3 = st.columns(3)

#         claim_id = c1.text_input("Claim ID", value=data.get("CLAIM_ID", ""))
        
#         claim_amount = c2.number_input(
#             "Claim Amount",
#             min_value=0.01,
#             value=float(data.get("CLAIM_AMOUNT", 50000.0)),
#         )

#         reporting_delay = c3.number_input(
#             "Reporting Delay Days",
#             min_value=0,
#             value=int(data.get("REPORTING_DELAY_DAYS", 2)),
#             step=1,
#         )

#         c1, c2, c3 = st.columns(3)

#         incident_month = c1.number_input(
#             "Incident Month",
#             min_value=1,
#             max_value=12,
#             value=int(data.get("INCIDENT_MONTH", 6)),
#             step=1,
#         )

#         age = c2.number_input(
#             "Age",
#             min_value=18,
#             max_value=120,
#             value=int(data.get("AGE", 40)),
#             step=1,
#         )

#         income = c3.number_input(
#             "Annual Income",
#             min_value=0.0,
#             value=float(data.get("ANNUAL_INCOME", 800000.0)),
#         )

#         c1, c2, c3 = st.columns(3)

#         credit_score = c1.number_input(
#             "Credit Score",
#             min_value=0,
#             value=int(data.get("CREDIT_SCORE", 700)),
#             step=1,
#         )

#         sum_insured = c2.number_input(
#             "Sum Insured",
#             min_value=0.01,
#             value=float(data.get("SUM_INSURED", 500000.0)),
#         )

#         annual_premium = c3.number_input(
#             "Annual Premium",
#             min_value=0.0,
#             value=float(data.get("ANNUAL_PREMIUM", 15000.0)),
#         )

#         risk_score = st.number_input(
#             "Policy Risk Score",
#             value=float(data.get("POLICY_RISK_SCORE", 0.5)),
#         )

#         c1, c2, c3 = st.columns(3)

#         claim_type = c1.text_input("Claim Type", value=data.get("CLAIM_TYPE", "Accident"))
#         source = c2.text_input("Source", value=data.get("SOURCE", "Online"))
#         claim_severity = c3.text_input("Claim Severity", value=data.get("CLAIM_SEVERITY", "Medium"))

#         c1, c2, c3 = st.columns(3)

#         gender = c1.text_input("Gender", value=data.get("GENDER", "Male"))
#         marital_status = c2.text_input("Marital Status", value=data.get("MARITAL_STATUS", "Married"))
#         occupation = c3.text_input("Occupation", value=data.get("OCCUPATION", "Salaried"))

#         c1, c2, c3 = st.columns(3)

#         state = c1.text_input("State", value=data.get("STATE", "Karnataka"))
#         customer_risk = c2.text_input("Customer Risk Segment", value=data.get("CUSTOMER_RISK_SEGMENT", "Medium"))
#         policy_type = c3.text_input("Policy Type", value=data.get("POLICY_TYPE", "Health"))

#         c1, c2 = st.columns(2)

#         payment_mode = c1.text_input("Payment Mode", value=data.get("PAYMENT_MODE", "Annual"))
#         risk_band = c2.text_input("Policy Risk Band", value=data.get("RISK_BAND", "Medium"))

#         submitted = st.form_submit_button(
#             "Run Fraud Screening",
#             type="primary",
#         )

#     if submitted:
#         if not claim_id:
#             st.warning("Claim ID is required.")
#         else:
#             payload = {
#                 "CLAIM_ID": claim_id,
#                 "CLAIM_AMOUNT": claim_amount,
#                 "REPORTING_DELAY_DAYS": int(reporting_delay),
#                 "INCIDENT_MONTH": int(incident_month),
#                 "AGE": int(age),
#                 "ANNUAL_INCOME": income,
#                 "CREDIT_SCORE": int(credit_score),
#                 "SUM_INSURED": sum_insured,
#                 "ANNUAL_PREMIUM": annual_premium,
#                 "RISK_SCORE": risk_score,
#                 "CLAIM_TYPE": claim_type,
#                 "SOURCE": source,
#                 "CLAIM_SEVERITY": claim_severity,
#                 "GENDER": gender,
#                 "MARITAL_STATUS": marital_status,
#                 "OCCUPATION": occupation,
#                 "STATE": state,
#                 "CUSTOMER_RISK_SEGMENT": customer_risk,
#                 "POLICY_TYPE": policy_type,
#                 "PAYMENT_MODE": payment_mode,
#                 "RISK_BAND": risk_band,
#             }

#             try:
#                 result = client.fraud(payload)
#                 prediction = result.get("prediction", {})
#                 decision = result.get("decision", {})

#                 c1, c2, c3 = st.columns(3)
#                 c1.metric("Fraud Risk", f"{prediction.get('fraud_risk_pct', 0)}%")
#                 c2.metric("Alert", prediction.get("prediction", "-"))
#                 c3.metric(
#                     "Human Review",
#                     "Required" if decision.get("human_review_required") else "No"
#                 )

#                 display_decision(decision)

#                 if result.get("message"):
#                     st.info(result["message"])

#                 with st.expander("Raw API Response"):
#                     st.json(result)

#             except Exception as error:
#                 show_api_error(error)

# elif page == "Fraud Screening":

#     st.title(
#         "Fraud Risk Screening"
#     )

#     st.warning(
#         "Fraud model output is an investigation signal, "
#         "not proof of fraud and not an automatic claim rejection."
#     )


#     with st.form(
#         "fraud_form"
#     ):

#         c1, c2, c3 = (
#             st.columns(3)
#         )


#         claim_id = c1.text_input(
#             "Claim ID"
#         )

#         claim_amount = c2.number_input(
#             "Claim Amount",
#             min_value=0.01,
#             value=50000.0,
#         )

#         reporting_delay = c3.number_input(
#             "Reporting Delay Days",
#             min_value=0,
#             value=2,
#             step=1,
#         )


#         c1, c2, c3 = (
#             st.columns(3)
#         )


#         incident_month = c1.number_input(
#             "Incident Month",
#             min_value=1,
#             max_value=12,
#             value=6,
#             step=1,
#         )

#         age = c2.number_input(
#             "Age",
#             min_value=18,
#             max_value=120,
#             value=40,
#             step=1,
#         )

#         income = c3.number_input(
#             "Annual Income",
#             min_value=0.0,
#             value=800000.0,
#         )


#         c1, c2, c3 = (
#             st.columns(3)
#         )


#         credit_score = c1.number_input(
#             "Credit Score",
#             min_value=0,
#             value=700,
#             step=1,
#         )

#         sum_insured = c2.number_input(
#             "Sum Insured",
#             min_value=0.01,
#             value=500000.0,
#         )

#         annual_premium = c3.number_input(
#             "Annual Premium",
#             min_value=0.0,
#             value=15000.0,
#         )


#         risk_score = st.number_input(
#             "Policy Risk Score",
#             value=0.5,
#         )


#         c1, c2, c3 = (
#             st.columns(3)
#         )


#         claim_type = c1.text_input(
#             "Claim Type",
#             value="Accident",
#         )

#         source = c2.text_input(
#             "Source",
#             value="Online",
#         )

#         claim_severity = c3.text_input(
#             "Claim Severity",
#             value="Medium",
#         )


#         c1, c2, c3 = (
#             st.columns(3)
#         )


#         gender = c1.text_input(
#             "Gender",
#             value="Male",
#         )

#         marital_status = c2.text_input(
#             "Marital Status",
#             value="Married",
#         )

#         occupation = c3.text_input(
#             "Occupation",
#             value="Salaried",
#         )


#         c1, c2, c3 = (
#             st.columns(3)
#         )


#         state = c1.text_input(
#             "State",
#             value="Karnataka",
#         )

#         customer_risk = c2.text_input(
#             "Customer Risk Segment",
#             value="Medium",
#         )

#         policy_type = c3.text_input(
#             "Policy Type",
#             value="Health",
#         )


#         c1, c2 = st.columns(2)


#         payment_mode = c1.text_input(
#             "Payment Mode",
#             value="Annual",
#         )

#         risk_band = c2.text_input(
#             "Policy Risk Band",
#             value="Medium",
#         )


#         submitted = st.form_submit_button(
#             "Run Fraud Screening",
#             type="primary",
#         )


#     if submitted:

#         if not claim_id:

#             st.warning(
#                 "Claim ID is required."
#             )

#         else:

#             payload = {
#                 "CLAIM_ID":
#                     claim_id,

#                 "CLAIM_AMOUNT":
#                     claim_amount,

#                 "REPORTING_DELAY_DAYS":
#                     int(
#                         reporting_delay
#                     ),

#                 "INCIDENT_MONTH":
#                     int(
#                         incident_month
#                     ),

#                 "AGE":
#                     int(
#                         age
#                     ),

#                 "ANNUAL_INCOME":
#                     income,

#                 "CREDIT_SCORE":
#                     int(
#                         credit_score
#                     ),

#                 "SUM_INSURED":
#                     sum_insured,

#                 "ANNUAL_PREMIUM":
#                     annual_premium,

#                 "RISK_SCORE":
#                     risk_score,

#                 "CLAIM_TYPE":
#                     claim_type,

#                 "SOURCE":
#                     source,

#                 "CLAIM_SEVERITY":
#                     claim_severity,

#                 "GENDER":
#                     gender,

#                 "MARITAL_STATUS":
#                     marital_status,

#                 "OCCUPATION":
#                     occupation,

#                 "STATE":
#                     state,

#                 "CUSTOMER_RISK_SEGMENT":
#                     customer_risk,

#                 "POLICY_TYPE":
#                     policy_type,

#                 "PAYMENT_MODE":
#                     payment_mode,

#                 "RISK_BAND":
#                     risk_band,
#             }


#             try:

#                 result = client.fraud(
#                     payload
#                 )


#                 prediction = result.get(
#                     "prediction",
#                     {}
#                 )

#                 decision = result.get(
#                     "decision",
#                     {}
#                 )


#                 c1, c2, c3 = st.columns(3)


#                 c1.metric(
#                     "Fraud Risk",
#                     (
#                         f"{prediction.get('fraud_risk_pct', 0)}%"
#                     )
#                 )


#                 c2.metric(
#                     "Alert",
#                     prediction.get(
#                         "prediction",
#                         "-"
#                     )
#                 )


#                 c3.metric(
#                     "Human Review",
#                     (
#                         "Required"
#                         if decision.get(
#                             "human_review_required"
#                         )
#                         else
#                         "No"
#                     )
#                 )


#                 display_decision(
#                     decision
#                 )


#                 if result.get(
#                     "message"
#                 ):

#                     st.info(
#                         result[
#                             "message"
#                         ]
#                     )


#                 with st.expander(
#                     "Raw API Response"
#                 ):

#                     st.json(
#                         result
#                     )


#             except Exception as error:

#                 show_api_error(
#                     error
#                 )


# ==========================================================
# UNDERWRITING
# ==========================================================

elif page == "Underwriting":

    st.title(
        "Underwriting Decision Support"
    )

    st.caption(
        "Model recommendation + deterministic business rules + human review."
    )


    with st.form(
        "uw_form"
    ):

        uw_id = st.text_input(
            "Underwriting ID (optional)"
        )


        c1, c2, c3, c4 = (
            st.columns(4)
        )


        age = c1.number_input(
            "Age",
            min_value=18,
            max_value=120,
            value=40,
            step=1,
        )

        health_score = c2.number_input(
            "Health Score",
            value=75.0,
        )

        bmi = c3.number_input(
            "BMI",
            min_value=1.0,
            value=25.0,
        )

        credit_score = c4.number_input(
            "Credit Score",
            min_value=0,
            value=720,
            step=1,
        )


        c1, c2 = st.columns(2)


        lifestyle = c1.text_input(
            "Lifestyle",
            value="Good",
        )

        occupation_risk = c2.text_input(
            "Occupation Risk",
            value="Low",
        )


        c1, c2 = st.columns(2)


        medical_history = c1.text_input(
            "Medical History Flag",
            value="No",
        )

        smoker = c2.text_input(
            "Smoker Flag",
            value="No",
        )


        submitted = (
            st.form_submit_button(
                "Run Underwriting Assessment",
                type="primary",
            )
        )


    if submitted:

        payload = {
            "AGE":
                int(
                    age
                ),

            "HEALTH_SCORE":
                health_score,

            "BMI":
                bmi,

            "CREDIT_SCORE":
                int(
                    credit_score
                ),

            "LIFESTYLE":
                lifestyle,

            "MEDICAL_HISTORY_FLAG":
                medical_history,

            "SMOKER_FLAG":
                smoker,

            "OCCUPATION_RISK":
                occupation_risk,
        }


        if uw_id:

            payload[
                "UNDERWRITING_ID"
            ] = uw_id


        try:

            result = (
                client.underwriting(
                    payload
                )
            )


            prediction = result.get(
                "prediction",
                {}
            )

            decision = result.get(
                "decision",
                {}
            )


            c1, c2, c3 = st.columns(3)


            c1.metric(
                "Recommendation",
                prediction.get(
                    "decision",
                    "-"
                )
            )


            c2.metric(
                "Confidence",
                (
                    f"{prediction.get('confidence_pct', 0)}%"
                )
            )


            c3.metric(
                "Human Review",
                (
                    "Required"
                    if decision.get(
                        "human_review_required"
                    )
                    else
                    "No"
                )
            )


            display_decision(
                decision
            )


            probabilities = (
                prediction.get(
                    "probabilities",
                    {}
                )
            )


            if probabilities:

                st.subheader(
                    "Class Probabilities"
                )

                probability_df = (
                    pd.DataFrame(
                        [
                            {
                                "Decision":
                                    key,

                                "Probability":
                                    value,
                            }

                            for key, value
                            in probabilities.items()
                        ]
                    )
                )


                st.dataframe(
                    probability_df,
                    width="stretch",
                    hide_index=True,
                )


            if result.get(
                "message"
            ):

                st.info(
                    result[
                        "message"
                    ]
                )


            with st.expander(
                "Raw API Response"
            ):

                st.json(
                    result
                )


        except Exception as error:

            show_api_error(
                error
            )


# ==========================================================
# HUMAN REVIEW
# ==========================================================

elif page == "Human Review":

    st.title(
        "Human Review Inbox"
    )

    st.caption(
        "Review AI-generated recommendations that require human approval."
    )


    if st.button(
        "Refresh Queue"
    ):

        st.rerun()


    try:

        response = (
            client.pending_reviews(
                limit=100
            )
        )


        items = (
            response.get(
                "items",
                []
            )
        )


        if not items:

            st.success(
                "No pending human reviews."
            )

        else:

            df = pd.DataFrame(
                items
            )


            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
            )


            review_ids = [
                item[
                    "REVIEW_ID"
                ]
                for item in items
            ]


            selected_id = (
                st.selectbox(
                    "Select Review ID",
                    review_ids,
                )
            )


            selected = next(
                item
                for item in items
                if item[
                    "REVIEW_ID"
                ] == selected_id
            )


            st.subheader(
                "Selected Review"
            )


            st.json(
                selected
            )


            with st.form(
                "review_resolution"
            ):

                reviewed_by = (
                    st.text_input(
                        "Reviewed By"
                    )
                )


                human_decision = (
                    st.selectbox(
                        "Human Decision",
                        [
                            "APPROVED",
                            "MODIFIED",
                            "REJECTED",
                        ]
                    )
                )


                comments = (
                    st.text_area(
                        "Comments"
                    )
                )


                resolve = (
                    st.form_submit_button(
                        "Submit Human Decision",
                        type="primary",
                    )
                )


            if resolve:

                if not reviewed_by:

                    st.warning(
                        "Reviewed By is required."
                    )

                else:

                    result = (
                        client.resolve_review(
                            selected_id,
                            {
                                "reviewed_by":
                                    reviewed_by,

                                "human_decision":
                                    human_decision,

                                "human_comments":
                                    comments,
                            },
                        )
                    )


                    st.success(
                        "Review completed."
                    )


                    st.json(
                        result
                    )


    except Exception as error:

        show_api_error(
            error
        )


# ==========================================================
# AUDIT
# ==========================================================

elif page == "AI Audit":

    st.title(
        "AI Session & Tool Audit"
    )

    st.caption(
        "Inspect conversation history and which tools the AI used."
    )


    default_session = (
        st.session_state[
            "ai_session_id"
        ]
    )


    audit_session_id = (
        st.text_input(
            "Session ID",
            value=
                default_session,
        )
    )


    c1, c2 = st.columns(2)


    if c1.button(
        "Load Conversation"
    ):

        try:

            result = (
                client.session(
                    audit_session_id
                )
            )


            st.subheader(
                "Session"
            )

            st.json(
                result.get(
                    "session",
                    {}
                )
            )


            messages = (
                result.get(
                    "messages",
                    []
                )
            )


            if messages:

                st.dataframe(
                    pd.DataFrame(
                        messages
                    ),
                    width="stretch",
                    hide_index=True,
                )


        except Exception as error:

            show_api_error(
                error
            )


    if c2.button(
        "Load Tool Audit"
    ):

        try:

            result = (
                client.audit(
                    audit_session_id
                )
            )


            calls = (
                result.get(
                    "tool_calls",
                    []
                )
            )


            if calls:

                st.dataframe(
                    pd.DataFrame(
                        calls
                    ),
                    width="stretch",
                    hide_index=True,
                )

            else:

                st.info(
                    "No tool calls found for this session."
                )


        except Exception as error:

            show_api_error(
                error
            )


# ==========================================================
# SYSTEM STATUS
# ==========================================================

if page == "System Status":
    st.title("System Status")
    if st.button("Run Readiness Check", type="primary"):
        try:
            result = client.readiness()
            st.success("System readiness check passed.")
            st.json(result)
        except Exception as error:
            show_api_error(error)
