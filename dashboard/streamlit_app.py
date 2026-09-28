import sys
import uuid
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from dashboard.api_client import InsuranceAPIClient
from dashboard.components import metric_card, human_review_banner, show_probability_table, show_policy_fields

st.set_page_config(
    page_title="Insurance AI Copilot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "api_url" not in st.session_state:
    st.session_state["api_url"] = "http://127.0.0.1:8001"

if "ai_session_id" not in st.session_state:
    st.session_state["ai_session_id"] = str(uuid.uuid4())

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

if "user_role" not in st.session_state:
    st.session_state["user_role"] = "Analyst"

def get_client():
    return InsuranceAPIClient(st.session_state["api_url"])

def show_api_error(error):
    if isinstance(error, requests.exceptions.ConnectionError):
        st.error("FastAPI backend is not reachable. Start Uvicorn on port 8001.")
        return
    if isinstance(error, requests.exceptions.HTTPError):
        try:
            detail = error.response.json()
        except Exception:
            detail = error.response.text
        st.error(f"API error: {detail}")
        return
    st.error(f"Unexpected error: {error}")

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

st.sidebar.markdown("## 🛡️ Insurance AI Copilot")
st.sidebar.caption("Analytics + ML + AI + Human Review")

st.sidebar.selectbox(
    "View As",
    ["Analyst", "Claims Reviewer", "Underwriter", "Manager"],
    key="user_role",
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "AI Copilot",
        "Policy 360",
        "Renewal Risk",
        "Fraud Screening",
        "Underwriting",
        "Human Review",
        "AI Audit",
    ],
)

st.sidebar.divider()
st.sidebar.text_input("FastAPI URL", key="api_url")
client = get_client()

if st.sidebar.button("Check Backend"):
    try:
        health = client.health()
        if health.get("api") == "healthy":
            st.sidebar.success("API connected")
        if health.get("database") == "healthy":
            st.sidebar.success("Database connected")
        else:
            st.sidebar.warning("Database not healthy")
    except Exception as error:
        show_api_error(error)

st.sidebar.caption("LLM: Ollama / Qwen3")
st.sidebar.caption("Backend: FastAPI")
st.sidebar.caption("ML: Renewal • Fraud • Underwriting")

st.title("Insurance AI Copilot")
st.caption(f"Current view: {st.session_state['user_role']}")

if page == "Overview":
    st.subheader("Portfolio Overview")
    try:
        summary = client.portfolio_summary()
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Policies", f"{summary.get('TOTAL_POLICIES', 0):,}")
        with c2:
            metric_card("Policy Customers", f"{summary.get('TOTAL_POLICY_CUSTOMERS', 0):,}")
        with c3:
            metric_card("Annual Premium", currency_inr(summary.get("TOTAL_ANNUAL_PREMIUM")))
        with c4:
            metric_card("Avg Premium", currency_inr(summary.get("AVG_ANNUAL_PREMIUM")))

        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card(
                "Source-Reported Active",
                f"{summary.get('SOURCE_REPORTED_ACTIVE_POLICIES', 0):,}",
                "Based on source POLICY_STATUS."
            )
        with c2:
            metric_card("Policies With Claims", f"{summary.get('POLICIES_WITH_CLAIMS', 0):,}")
        with c3:
            metric_card("Finalized Renewals", f"{summary.get('FINALIZED_RENEWALS', 0):,}")

        st.info("Overview KPIs come from SQL Policy-360.")
    except Exception as error:
        show_api_error(error)

elif page == "AI Copilot":
    st.subheader("Conversational Insurance Assistant")
    c1, c2 = st.columns([4, 1])
    with c1:
        st.caption("Session: " + st.session_state["ai_session_id"])
    with c2:
        if st.button("New Chat"):
            st.session_state["ai_session_id"] = str(uuid.uuid4())
            st.session_state["chat_messages"] = []
            st.rerun()

    for message in st.session_state["chat_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask about policy, renewal, fraud, underwriting, portfolio, or process...")

    if prompt:
        st.session_state["chat_messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                with st.spinner("Analyzing..."):
                    result = client.chat_ai(
                        prompt,
                        session_id=st.session_state["ai_session_id"]
                    )
                answer = result.get("message", "No response returned.")
                st.markdown(answer)
                st.session_state["chat_messages"].append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as error:
                show_api_error(error)

elif page == "Policy 360":
    st.subheader("Policy 360")
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
                show_policy_fields(policy)
            except Exception as error:
                show_api_error(error)

elif page == "Renewal Risk":
    st.subheader("Renewal Risk Assessment")
    policy_id = st.text_input("Policy ID")
    if st.button("Assess Renewal", type="primary"):
        if not policy_id:
            st.warning("Enter a Policy ID.")
        else:
            try:
                result = client.renewal(policy_id.strip())
                prediction = result.get("prediction", {})
                decision = result.get("decision", {})
                c1, c2, c3 = st.columns(3)
                c1.metric("Non-Renewal Risk", f"{prediction.get('non_renewal_risk_pct', 0)}%")
                c2.metric("Risk Band", prediction.get("risk_band", "-"))
                c3.metric("Threshold", prediction.get("threshold", "-"))
                human_review_banner(decision.get("human_review_required", False))
                st.write("**Recommended action:**", decision.get("recommended_action", "-"))
                st.write("**Reason:**", decision.get("reason", "-"))
                if result.get("message"):
                    st.info(result["message"])
                with st.expander("Technical response"):
                    st.json(result)
            except Exception as error:
                show_api_error(error)

elif page == "Underwriting":
    st.subheader("Underwriting Decision Support")
    with st.form("underwriting_form"):
        c1, c2, c3, c4 = st.columns(4)
        age = c1.number_input("Age", 18, 120, 40)
        health_score = c2.number_input("Health Score", value=75.0)
        bmi = c3.number_input("BMI", min_value=1.0, value=25.0)
        credit_score = c4.number_input("Credit Score", min_value=0, value=720)

        c1, c2 = st.columns(2)
        lifestyle = c1.text_input("Lifestyle", value="Good")
        occupation_risk = c2.text_input("Occupation Risk", value="Low")

        c1, c2 = st.columns(2)
        medical_history = c1.text_input("Medical History Flag", value="No")
        smoker = c2.text_input("Smoker Flag", value="No")

        submit = st.form_submit_button("Assess Applicant", type="primary")

    if submit:
        payload = {
            "AGE": int(age),
            "HEALTH_SCORE": health_score,
            "BMI": bmi,
            "CREDIT_SCORE": int(credit_score),
            "LIFESTYLE": lifestyle,
            "MEDICAL_HISTORY_FLAG": medical_history,
            "SMOKER_FLAG": smoker,
            "OCCUPATION_RISK": occupation_risk,
        }
        try:
            result = client.underwriting(payload)
            prediction = result.get("prediction", {})
            decision = result.get("decision", {})
            c1, c2, c3 = st.columns(3)
            c1.metric("Recommendation", prediction.get("decision", "-"))
            c2.metric("Confidence", f"{prediction.get('confidence_pct', 0)}%")
            c3.metric(
                "Human Review",
                "Required" if decision.get("human_review_required") else "No"
            )
            human_review_banner(decision.get("human_review_required", False))
            show_probability_table(prediction.get("probabilities", {}))
            if result.get("message"):
                st.info(result["message"])
        except Exception as error:
            show_api_error(error)

elif page == "Fraud Screening":
    st.subheader("Fraud Risk Screening")
    st.warning("Fraud score is an investigation signal, not proof of fraud.")
    st.info(
        "Keep using your existing Stage-19 structured fraud form for full claim inputs. "
        "This polished bundle focuses on Overview, Policy 360, Copilot, Renewal, Underwriting, Review and Audit."
    )

elif page == "Human Review":
    st.subheader("Human Review Inbox")
    st.caption("UI role selector is not authentication yet.")
    try:
        response = client.pending_reviews(limit=100)
        items = response.get("items", [])
        if not items:
            st.success("No pending human reviews.")
        else:
            st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
            review_ids = [item["REVIEW_ID"] for item in items]
            selected_id = st.selectbox("Review ID", review_ids)
            selected = next(item for item in items if item["REVIEW_ID"] == selected_id)
            st.json(selected)

            with st.form("review_form"):
                reviewed_by = st.text_input("Reviewed By")
                decision = st.selectbox(
                    "Decision",
                    ["APPROVED", "MODIFIED", "REJECTED"]
                )
                comments = st.text_area("Comments")
                submit = st.form_submit_button("Submit Review", type="primary")

            if submit:
                if not reviewed_by:
                    st.warning("Reviewed By is required.")
                else:
                    result = client.resolve_review(
                        selected_id,
                        {
                            "reviewed_by": reviewed_by,
                            "human_decision": decision,
                            "human_comments": comments,
                        },
                    )
                    st.success("Human decision recorded.")
                    st.json(result)
    except Exception as error:
        show_api_error(error)

elif page == "AI Audit":
    st.subheader("AI Audit & Traceability")
    session_id = st.text_input(
        "Session ID",
        value=st.session_state["ai_session_id"]
    )
    c1, c2 = st.columns(2)

    if c1.button("Load Conversation"):
        try:
            result = client.session(session_id)
            st.json(result.get("session", {}))
            messages = result.get("messages", [])
            if messages:
                st.dataframe(
                    pd.DataFrame(messages),
                    use_container_width=True,
                    hide_index=True
                )
        except Exception as error:
            show_api_error(error)

    if c2.button("Load Tool Audit"):
        try:
            result = client.audit(session_id)
            calls = result.get("tool_calls", [])
            if calls:
                st.dataframe(
                    pd.DataFrame(calls),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No tool calls found.")
        except Exception as error:
            show_api_error(error)
