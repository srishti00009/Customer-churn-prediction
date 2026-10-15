from __future__ import annotations

import sys
from pathlib import Path

from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from shared.auth_db import init_db, register_user, login_user as auth_login

from utils.predictor import (
    predict_churn,
    get_dashboard_metrics,
)

APP_TITLE = "🔮 ChurnGuard AI"
APP_SUBTITLE = "Intelligent Customer Churn Prediction System"


def initialize_state():
    init_db()
    defaults = {
        "history": [],
        "theme_mode": "light",
        "selected_nav": "predict",
        "logged_in": False,
        "user": None,
        "page": "landing",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def get_theme_colors():
    theme = st.session_state.theme_mode
    if theme == "dark":
        return dict(
            bg_primary="#0f0f1e",
            bg_secondary="#1a1a2e",
            card_bg="rgba(26, 26, 46, 0.95)",
            text_primary="#ffffff",
            text_secondary="#a0a0c0",
            accent="#8b5cf6",
            accent_secondary="#ec4899",
            success="#10b981",
            warning="#f59e0b",
            error="#ef4444",
            border="rgba(139, 92, 246, 0.2)",
        )
    else:
        return dict(
            bg_primary="#f8fafc",
            bg_secondary="#ffffff",
            card_bg="rgba(255, 255, 255, 0.95)",
            text_primary="#0f172a",
            text_secondary="#475569",
            accent="#8b5cf6",
            accent_secondary="#ec4899",
            success="#10b981",
            warning="#f59e0b",
            error="#ef4444",
            border="rgba(139, 92, 246, 0.1)",
        )


def apply_premium_theme():
    c = get_theme_colors()
    bg_primary = c["bg_primary"]
    bg_secondary = c["bg_secondary"]
    card_bg = c["card_bg"]
    text_primary = c["text_primary"]
    text_secondary = c["text_secondary"]
    accent = c["accent"]
    accent_secondary = c["accent_secondary"]
    success = c["success"]
    warning = c["warning"]
    error = c["error"]
    border = c["border"]

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {bg_primary};
            color: {text_primary};
        }}
        .glass-card {{
            background: {card_bg};
            backdrop-filter: blur(10px);
            border: 1px solid {border};
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
        }}
        .glass-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(139, 92, 246, 0.15);
            border-color: {accent};
        }}
        .hero-section {{
            background: linear-gradient(135deg, {accent}20 0%, {accent_secondary}20 100%);
            border: 1px solid {border};
            border-radius: 25px;
            padding: 2rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }}
        .hero-section::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, {accent}10 0%, transparent 70%);
            animation: rotate 20s linear infinite;
        }}
        @keyframes rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        .hero-title {{
            font-size: 3rem;
            font-weight: 800;
            background: linear-gradient(135deg, {accent} 0%, {accent_secondary} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            position: relative;
            z-index: 1;
        }}
        .hero-subtitle {{
            font-size: 1.1rem;
            color: {text_secondary};
            position: relative;
            z-index: 1;
        }}
        .metric-card {{
            background: {card_bg};
            border: 1px solid {border};
            border-radius: 15px;
            padding: 1.25rem;
            text-align: center;
            transition: all 0.3s ease;
        }}
        .metric-card:hover {{
            transform: scale(1.05);
            border-color: {accent};
            box-shadow: 0 5px 20px rgba(139, 92, 246, 0.2);
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, {accent} 0%, {accent_secondary} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .metric-label {{
            font-size: 0.85rem;
            color: {text_secondary};
            margin-top: 0.5rem;
        }}
        .stNumberInput > div > div > input,
        .stSlider > div > div > div,
        .stSelectbox > div > div {{
            background: {card_bg};
            border-color: {border};
            border-radius: 10px;
        }}
        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, {accent} 0%, {accent_secondary} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .result-card {{
            background: linear-gradient(135deg, {accent}15 0%, {accent_secondary}15 100%);
            border: 1px solid {accent}40;
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            animation: slideIn 0.5s ease-out;
        }}
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: {bg_secondary};
            border-radius: 10px;
        }}
        ::-webkit-scrollbar-thumb {{
            background: {accent};
            border-radius: 10px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {accent_secondary};
        }}
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .fade-in-up {{
            animation: fadeInUp 0.6s ease-out;
        }}
        .auth-container {{ max-width: 420px; margin: 4rem auto; padding: 2.5rem; background: {card_bg}; backdrop-filter: blur(20px); border: 1px solid {border}; border-radius: 24px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); text-align: center; }}
        .auth-title {{ font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, {accent} 0%, {accent_secondary} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem; }}
        .auth-subtitle {{ color: {text_secondary}; margin-bottom: 2rem; }}
        .auth-divider {{ border: none; height: 1px; background: linear-gradient(90deg, transparent, {accent}, transparent); margin: 2rem 0; }}
        .landing-section {{ text-align: center; padding: 3rem 1rem; }}
        .landing-title {{ font-size: 3.5rem; font-weight: 900; background: linear-gradient(135deg, {accent} 0%, {accent_secondary} 50%, {success} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem; }}
        .landing-subtitle {{ font-size: 1.3rem; color: {text_secondary}; max-width: 600px; margin: 0 auto 2.5rem; }}
        .landing-card {{ background: {card_bg}; border: 1px solid {border}; border-radius: 20px; padding: 2rem; transition: all 0.3s; height: 100%; }}
        .landing-card:hover {{ transform: translateY(-8px); border-color: {accent}; box-shadow: 0 20px 40px rgba(139,92,246,0.15); }}
        .home-header {{ display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; margin-bottom: 2rem; border-bottom: 1px solid {border}; }}
        .home-welcome {{ font-size: 2.2rem; font-weight: 800; }}
        .home-welcome span {{ background: linear-gradient(135deg, {accent} 0%, {accent_secondary} 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_logout_sidebar():
    with st.sidebar:
        user = st.session_state.user
        st.markdown(f'<div style="text-align:center;padding:0.75rem;background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.2);border-radius:12px;margin-bottom:1rem"><span style="font-size:1.1rem;">👤 {user["username"]}</span></div>', unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["logged_in", "user", "page", "history"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()


def render_sidebar():
    with st.sidebar:
        st.markdown("### 🔮 ChurnGuard AI")
        st.markdown("---")

        selected = option_menu(
            menu_title=None,
            options=["🏠 Home", "🎯 Predict", "📊 Analytics", "📜 History", "ℹ️ About"],
            icons=["house", "cursor", "graph-up", "clock-history", "info-circle"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background": "transparent"},
                "icon": {"color": "#8b5cf6", "font-size": "1.2rem"},
                "nav-link": {
                    "font-size": "1rem",
                    "text-align": "left",
                    "margin": "0.5rem 0",
                    "border-radius": "10px",
                    "transition": "all 0.3s ease",
                },
                "nav-link-hover": {
                    "background": "rgba(139, 92, 246, 0.1)",
                    "transform": "translateX(5px)",
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)",
                },
            },
        )

        st.markdown("---")

        theme_mode = st.toggle("🌙 Dark Mode", value=st.session_state.theme_mode == "dark")
        st.session_state.theme_mode = "dark" if theme_mode else "light"

        render_logout_sidebar()

        st.markdown("---")
        st.markdown("### 📈 Quick Stats")
        metrics = get_dashboard_metrics()
        st.metric("Model Accuracy", f"{metrics.get('accuracy', 0):.1%}")
        st.metric("Total Predictions", len(st.session_state.history))

        return selected


def render_hero():
    st.markdown(
        f"""
        <div class="hero-section fade-in-up">
            <h1 class="hero-title">🔮 ChurnGuard AI</h1>
            <p class="hero-subtitle">Intelligent Customer Churn Prediction System</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard():
    metrics = get_dashboard_metrics()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics.get('algorithm', 'LR')}</div>
                <div class="metric-label">🤖 Algorithm</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        accuracy = metrics.get('accuracy', 0)
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{accuracy:.1%}</div>
                <div class="metric-label">🎯 Accuracy</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{metrics.get('dataset_rows', 0):,}</div>
                <div class="metric-label">📊 Training Records</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        features = len(metrics.get('features', []))
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{features}</div>
                <div class="metric-label">🔧 Features Used</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_form():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Customer Profile</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👤 Demographics", "📡 Services", "💰 Billing"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("👤 Gender", ["Male", "Female"])
            senior_citizen = st.selectbox("🧓 Senior Citizen", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
            partner = st.selectbox("💑 Has Partner", ["Yes", "No"])
            dependents = st.selectbox("👨‍👩‍👧‍👦 Has Dependents", ["Yes", "No"])
        with col2:
            tenure = st.number_input("📅 Tenure (months)", min_value=0, max_value=72, value=12)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            phone_service = st.selectbox("📞 Phone Service", ["Yes", "No"])
            multiple_lines = st.selectbox("🔗 Multiple Lines", ["Yes", "No", "No phone service"])
            internet_service = st.selectbox("🌐 Internet Service", ["DSL", "Fiber optic", "No"])
            online_security = st.selectbox("🔒 Online Security", ["Yes", "No", "No internet service"])
            online_backup = st.selectbox("💾 Online Backup", ["Yes", "No", "No internet service"])
        with col2:
            device_protection = st.selectbox("🛡️ Device Protection", ["Yes", "No", "No internet service"])
            tech_support = st.selectbox("🔧 Tech Support", ["Yes", "No", "No internet service"])
            streaming_tv = st.selectbox("📺 Streaming TV", ["Yes", "No", "No internet service"])
            streaming_movies = st.selectbox("🎬 Streaming Movies", ["Yes", "No", "No internet service"])

    with tab3:
        st.markdown("### 💳 Payment & Charges")
        col1, col2 = st.columns(2)
        with col1:
            contract = st.selectbox("📄 Contract Type", ["Month-to-month", "One year", "Two year"])
            paperless_billing = st.selectbox("📧 Paperless Billing", ["Yes", "No"])
        with col2:
            payment_method = st.selectbox("💵 Payment Method", [
                "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
            ])
            monthly_charges = st.number_input("💲 Monthly Charges ($)", min_value=0.0, max_value=200.0, value=70.0, step=1.0)
            total_charges = st.number_input("💰 Total Charges ($)", min_value=0.0, max_value=10000.0, value=700.0, step=1.0)
        st.markdown("")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            pass
        with col2:
            pass
        with col3:
            pass

    st.markdown('</div>', unsafe_allow_html=True)

    return {
        "gender": gender,
        "senior_citizen": senior_citizen,
        "partner": partner,
        "dependents": dependents,
        "tenure": tenure,
        "phone_service": phone_service,
        "multiple_lines": multiple_lines,
        "internet_service": internet_service,
        "online_security": online_security,
        "online_backup": online_backup,
        "device_protection": device_protection,
        "tech_support": tech_support,
        "streaming_tv": streaming_tv,
        "streaming_movies": streaming_movies,
        "contract": contract,
        "paperless_billing": paperless_billing,
        "payment_method": payment_method,
        "monthly_charges": monthly_charges,
        "total_charges": total_charges,
    }


def render_probability_gauge(probability):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=probability * 100,
        title={'text': "Churn Probability", 'font': {'size': 16}},
        delta={'reference': 50, 'increasing': {'color': "#ef4444"}, 'decreasing': {'color': "#10b981"}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#8b5cf6"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "rgba(139, 92, 246, 0.3)",
            'steps': [
                {'range': [0, 30], 'color': "rgba(16, 185, 129, 0.3)"},
                {'range': [30, 70], 'color': "rgba(245, 158, 11, 0.3)"},
                {'range': [70, 100], 'color': "rgba(239, 68, 68, 0.3)"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': probability * 100
            }
        }
    ))
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': st.session_state.theme_mode == "dark" and "white" or "black"}
    )
    return fig


def render_prediction(data):
    if st.button("🔮 Predict Churn", use_container_width=True, type="primary"):
        with st.spinner("Analyzing customer profile..."):
            result = predict_churn(
                gender=data["gender"],
                senior_citizen=data["senior_citizen"],
                partner=data["partner"],
                dependents=data["dependents"],
                tenure=data["tenure"],
                phone_service=data["phone_service"],
                multiple_lines=data["multiple_lines"],
                internet_service=data["internet_service"],
                online_security=data["online_security"],
                online_backup=data["online_backup"],
                device_protection=data["device_protection"],
                tech_support=data["tech_support"],
                streaming_tv=data["streaming_tv"],
                streaming_movies=data["streaming_movies"],
                contract=data["contract"],
                paperless_billing=data["paperless_billing"],
                payment_method=data["payment_method"],
                monthly_charges=data["monthly_charges"],
                total_charges=data["total_charges"],
            )

            probability = result["probability"]
            prediction = result["prediction"]
            risk = result["risk_level"]

            add_history(prediction, probability, data["tenure"])

            st.markdown('<div class="result-card fade-in-up">', unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1.5])

            with col1:
                gauge_fig = render_probability_gauge(probability)
                st.plotly_chart(gauge_fig, use_container_width=True)

            with col2:
                st.markdown(f"### {prediction}")

                if prediction == "CHURN":
                    st.markdown(
                        f'<div style="background: #ef444420; border: 1px solid #ef4444; border-radius: 10px; padding: 1rem; margin: 1rem 0;">'
                        f'<span style="font-size: 2rem;">⚠️</span> High risk of churn!'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div style="background: #10b98120; border: 1px solid #10b981; border-radius: 10px; padding: 1rem; margin: 1rem 0;">'
                        f'<span style="font-size: 2rem;">✅</span> Low risk of churn'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                st.markdown(f"**Risk Level:** {risk}")

                if prediction == "CHURN":
                    st.markdown("**Suggested Retention Actions:**")
                    suggestions = []
                    if data["contract"] == "Month-to-month":
                        suggestions.append("📄 Offer long-term contract discount")
                    if data["internet_service"] == "Fiber optic" and data["monthly_charges"] > 80:
                        suggestions.append("🌐 Review fiber optic pricing")
                    if data["tenure"] < 12:
                        suggestions.append("🤝 Implement early-stage engagement program")
                    if data["online_security"] == "No" and data["internet_service"] != "No":
                        suggestions.append("🔒 Offer free online security trial")
                    if data["tech_support"] == "No" and data["internet_service"] != "No":
                        suggestions.append("🔧 Offer tech support inclusion")
                    if data["payment_method"] == "Electronic check":
                        suggestions.append("💳 Suggest automatic payment method")
                    if data["paperless_billing"] == "No":
                        suggestions.append("📧 Promote paperless billing discount")
                    for s in suggestions[:4]:
                        st.markdown(f"- {s}")

            st.markdown('</div>', unsafe_allow_html=True)


def add_history(result, probability, tenure):
    st.session_state.history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prediction": result,
        "probability": round(probability * 100, 2),
        "tenure": tenure,
    })


def history_to_csv():
    df = pd.DataFrame(st.session_state.history)
    return df.to_csv(index=False).encode("utf-8")


def render_history():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📜 Prediction History</div>', unsafe_allow_html=True)

    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "timestamp": "⏰ Time",
                "prediction": st.column_config.TextColumn(
                    "🎯 Result",
                    help="Churn prediction result"
                ),
                "probability": st.column_config.NumberColumn(
                    "📊 Probability",
                    format="%.2f%%"
                ),
                "tenure": st.column_config.NumberColumn(
                    "📅 Tenure",
                    format="%d months"
                )
            }
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            total = len(history_df)
            st.metric("Total Predictions", total)
        with col2:
            churn_count = (history_df['prediction'] == 'CHURN').sum()
            st.metric("Churn Predicted", churn_count)
        with col3:
            not_churn = (history_df['prediction'] != 'CHURN').sum()
            st.metric("Not Churn", not_churn)

        st.markdown("### 📊 Prediction Summary")
        for _, row in history_df.tail(5).iterrows():
            color = "#ef4444" if row['prediction'] == 'CHURN' else "#10b981"
            st.markdown(
                f"""
                <div style="
                    background: {color}10;
                    border-left: 4px solid {color};
                    padding: 0.75rem;
                    margin: 0.5rem 0;
                    border-radius: 8px;
                ">
                    <strong>{row['timestamp']}</strong><br>
                    {row['prediction']} - {row['probability']:.1f}% probability (Tenure: {row['tenure']} months)
                </div>
                """,
                unsafe_allow_html=True
            )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                "📥 Download History CSV",
                data=history_to_csv(),
                file_name="churn_predictions.csv",
                mime="text/csv",
                use_container_width=True,
            )
    else:
        st.info("No predictions made yet. Start by predicting churn for a customer!")
    st.markdown('</div>', unsafe_allow_html=True)


def render_analytics():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Analytics Dashboard</div>', unsafe_allow_html=True)

    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)

        col1, col2 = st.columns(2)

        with col1:
            churn_rate = (history_df['prediction'] == 'CHURN').mean() * 100
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{churn_rate:.1f}%</div>
                    <div class="metric-label">Predicted Churn Rate</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            avg_prob = history_df['probability'].mean()
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{avg_prob:.1f}%</div>
                    <div class="metric-label">Average Churn Probability</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("### 📈 Prediction Trends")
        fig = px.line(
            history_df,
            x='timestamp',
            y='probability',
            title='Churn Probability Over Time',
            color_discrete_sequence=['#8b5cf6']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Time",
            yaxis_title="Probability (%)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            fig_pie = px.pie(
                history_df,
                names='prediction',
                title='Prediction Distribution',
                color_discrete_sequence=['#ef4444', '#10b981']
            )
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            fig_hist = px.histogram(
                history_df,
                x='probability',
                nbins=20,
                title='Probability Distribution',
                color_discrete_sequence=['#8b5cf6']
            )
            fig_hist.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No data available. Make some predictions to see analytics!")


def render_about():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">ℹ️ About ChurnGuard AI</div>', unsafe_allow_html=True)

    st.markdown("""
    ### 🤖 Intelligent Churn Prediction System

    ChurnGuard AI uses machine learning to predict customer churn based on multiple factors:

    #### 👤 Customer Demographics
    - Gender, Age Group (Senior Citizen)
    - Partner, Dependents
    - Tenure (months with company)

    #### 📡 Services Subscribed
    - Phone Service & Multiple Lines
    - Internet Service Type
    - Online Security, Backup, Device Protection
    - Tech Support, Streaming TV & Movies

    #### 💰 Billing & Payment
    - Contract Type
    - Paperless Billing
    - Payment Method
    - Monthly & Total Charges

    ### 🎯 How It Works

    1. **Input customer details** across demographics, services, and billing
    2. **Our ML model** analyzes against historical churn data
    3. **Get instant predictions** with probability scores and risk assessment
    4. **Receive retention suggestions** for at-risk customers

    ### 📊 Model Performance

    - **Algorithm:** Logistic Regression
    - **Accuracy:** ~80% on test data
    - **Features:** 26+ key parameters
    - **Training Data:** Telco customer churn dataset

    ### 💡 Retention Tips

    - Offer long-term contract discounts
    - Provide free trials of premium services
    - Implement early-stage engagement for new customers
    - Promote automatic payment methods
    - Bundle services for better value

    ---

    **Developed with** ❤️ **using Streamlit & Scikit-learn**
    """)

    st.markdown('</div>', unsafe_allow_html=True)


def render_landing():
    c = get_theme_colors()
    text_secondary = c["text_secondary"]
    st.markdown(f"""
    <div class="landing-section fade-in-up">
        <div style="font-size:4rem;margin-bottom:1rem;">🔮</div>
        <h1 class="landing-title">ChurnGuard AI</h1>
        <p class="landing-subtitle">Predict customer churn before it happens. AI-powered retention intelligence for your business.</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="landing-card"><div style="font-size:2.5rem;margin-bottom:1rem;">🤖</div><h3>ML-Powered</h3><p style="color:{text_secondary}">Logistic Regression with 80%+ accuracy</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="landing-card"><div style="font-size:2.5rem;margin-bottom:1rem;">⚡</div><h3>Real-Time</h3><p style="color:{text_secondary}">Instant customer churn risk assessment</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="landing-card"><div style="font-size:2.5rem;margin-bottom:1rem;">💡</div><h3>Actionable</h3><p style="color:{text_secondary}">Get retention suggestions for at-risk customers</p></div>', unsafe_allow_html=True)
    st.markdown('<hr class="auth-divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
    with col2:
        if st.button("📝 Register", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()


def render_login():
    st.markdown(f"""
    <div class="auth-container fade-in-up">
        <div style="font-size:2.5rem;margin-bottom:0.5rem;">🔮</div>
        <h2 class="auth-title">Welcome Back</h2>
        <p class="auth-subtitle">Sign in to ChurnGuard AI</p>
    """, unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("🔐 Sign In", use_container_width=True, type="primary")
    if submitted:
        if not username or not password:
            st.error("Please fill in all fields!")
        else:
            success, result = auth_login(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user = result
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error(result)
    if st.button("📝 Register Instead", use_container_width=True):
        st.session_state.page = "register"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def render_register():
    st.markdown(f"""
    <div class="auth-container fade-in-up">
        <div style="font-size:2.5rem;margin-bottom:0.5rem;">🔮</div>
        <h2 class="auth-title">Create Account</h2>
        <p class="auth-subtitle">Join ChurnGuard AI today</p>
    """, unsafe_allow_html=True)
    with st.form("register_form"):
        username = st.text_input("👤 Username", placeholder="Choose a username")
        email = st.text_input("📧 Email", placeholder="your@email.com")
        password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
        confirm = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
        submitted = st.form_submit_button("📝 Create Account", use_container_width=True, type="primary")
    if submitted:
        if not username or not email or not password or not confirm:
            st.error("Please fill in all fields!")
        elif password != confirm:
            st.error("Passwords do not match!")
        elif len(password) < 4:
            st.error("Password must be at least 4 characters!")
        else:
            success, msg = register_user(username, email, password)
            if success:
                st.success(msg)
                st.session_state.page = "login"
                st.rerun()
            else:
                st.error(msg)
    if st.button("🔐 Login Instead", use_container_width=True):
        st.session_state.page = "login"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def render_home():
    c = get_theme_colors()
    text_secondary = c["text_secondary"]
    user = st.session_state.user
    st.markdown(f"""
    <div class="home-header">
        <div>
            <h1 class="home-welcome">Welcome, <span>{user["username"]}</span> 👋</h1>
            <p style="color:{text_secondary}">ChurnGuard AI is ready to analyze your customers</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    metrics = get_dashboard_metrics()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{metrics.get("algorithm", "LR")}</div><div class="metric-label">🤖 Algorithm</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{metrics.get("accuracy", 0):.1%}</div><div class="metric-label">🎯 Accuracy</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{metrics.get("dataset_rows", 0):,}</div><div class="metric-label">📊 Records</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.history)}</div><div class="metric-label">📊 Analyses</div></div>', unsafe_allow_html=True)
    st.markdown('<hr class="auth-divider">', unsafe_allow_html=True)
    st.markdown(f'<h2 style="font-size:1.5rem;font-weight:700;margin-bottom:1rem;">🚀 Quick Actions</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="landing-card"><div style="font-size:2rem;margin-bottom:0.5rem;">🎯</div><h3>Predict Churn</h3><p style="color:{text_secondary}">Analyze a customer profile for churn risk</p></div>', unsafe_allow_html=True)
        if st.button("🔍 Go to Predict", use_container_width=True):
            st.session_state.selected_nav = "predict"
            st.rerun()
    with col2:
        st.markdown(f'<div class="landing-card"><div style="font-size:2rem;margin-bottom:0.5rem;">📊</div><h3>View Analytics</h3><p style="color:{text_secondary}">Check churn trends and statistics</p></div>', unsafe_allow_html=True)
        if st.button("📈 Go to Analytics", use_container_width=True):
            st.session_state.selected_nav = "analytics"
            st.rerun()
    st.markdown('<hr class="auth-divider">', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;color:{text_secondary}">Logged in as <strong>{user["username"]}</strong> | {user.get("email", "")}</p>', unsafe_allow_html=True)


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🔮", layout="wide", initial_sidebar_state="expanded")
    initialize_state()
    apply_premium_theme()

    if not st.session_state.logged_in:
        page = st.session_state.get("page", "landing")
        if page == "landing":
            render_landing()
        elif page == "login":
            render_login()
        elif page == "register":
            render_register()
        return

    selected_page = render_sidebar()
    if selected_page == "🏠 Home":
        render_home()
        return
    if selected_page != "ℹ️ About":
        render_hero()
    if selected_page == "🎯 Predict":
        render_dashboard()
        st.divider()
        customer_data = render_form()
        render_prediction(customer_data)
    elif selected_page == "📊 Analytics":
        render_analytics()
    elif selected_page == "📜 History":
        render_history()
    elif selected_page == "ℹ️ About":
        render_about()


if __name__ == "__main__":
    main()
