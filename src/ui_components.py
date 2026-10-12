"""UI components and modern styling for the Travel Intelligence application."""
import streamlit as st


def apply_custom_css():
    """Inject custom modern CSS for travel tech branding."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        /* Hero Container */
        .hero-banner {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0d9488 100%);
            padding: 2.8rem 2.2rem;
            border-radius: 18px;
            color: #ffffff;
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .hero-title {
            font-size: 2.4rem;
            font-weight: 800;
            margin-bottom: 0.6rem;
            letter-spacing: -0.02em;
            color: #ffffff;
        }
        .hero-subtitle {
            font-size: 1.1rem;
            color: #cbd5e1;
            margin-bottom: 1.2rem;
            line-height: 1.5;
            max-width: 750px;
        }
        .hero-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(8px);
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            color: #f8fafc;
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* Feature Card */
        .feature-card {
            background-color: #ffffff;
            border-radius: 14px;
            padding: 1.3rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease-in-out;
            height: 100%;
        }
        .feature-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.15);
        }
        .feature-icon {
            font-size: 1.8rem;
            margin-bottom: 0.6rem;
        }
        .feature-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.35rem;
        }
        .feature-desc {
            font-size: 0.88rem;
            color: #64748b;
            line-height: 1.45;
        }

        /* Destination Card */
        .dest-card {
            background-color: #ffffff;
            border-radius: 14px;
            padding: 1.25rem;
            border: 1px solid #e2e8f0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.06);
            margin-bottom: 1.2rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .dest-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 18px -2px rgba(15, 23, 42, 0.12);
            border-color: #0ea5e9;
        }
        .dest-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }
        .dest-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #0f172a;
            margin: 0;
        }
        .dest-badge {
            background: #e0f2fe;
            color: #0369a1;
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .dest-meta {
            font-size: 0.82rem;
            color: #64748b;
            margin-bottom: 0.6rem;
        }
        .dest-desc {
            font-size: 0.88rem;
            color: #334155;
            line-height: 1.45;
            margin-bottom: 0.75rem;
        }
        .dest-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #f1f5f9;
            padding-top: 0.65rem;
            margin-top: 0.5rem;
            font-size: 0.85rem;
        }
        .dest-cost {
            font-weight: 700;
            color: #059669;
        }
        .dest-rating {
            font-weight: 700;
            color: #d97706;
        }

        /* Roadmap Pill */
        .roadmap-badge {
            background: #f1f5f9;
            color: #475569;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_placeholder_page(
    page_title: str,
    page_subtitle: str,
    phase_target: str,
    key_features_planned: list[str],
    badge_label: str = "Upcoming in Phase 2/3",
):
    """Render a clean, professional placeholder section for modules scheduled in subsequent phases."""
    apply_custom_css()
    
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 2rem; border-radius: 14px; color: #ffffff; margin-bottom: 1.5rem;">
            <div style="display: inline-block; background: rgba(59, 130, 246, 0.25); color: #93c5fd; padding: 0.2rem 0.7rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; margin-bottom: 0.5rem;">
                {badge_label}
            </div>
            <h1 style="color: #ffffff; margin: 0; font-size: 2rem; font-weight: 800;">{page_title}</h1>
            <p style="color: #cbd5e1; margin-top: 0.5rem; font-size: 1rem; max-width: 700px;">{page_subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(f"📌 **Current Roadmap Status:** This module is architected and scheduled for **{phase_target}**.")

    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.subheader("Planned Engineering Capabilities")
        for item in key_features_planned:
            st.markdown(f"- 🚀 **{item}**")

    with col2:
        st.subheader("Architectural Integration")
        st.markdown(
            """
            This component will consume data directly from:
            - **`src.data_loader`**: Destination repositories
            - **`src.preprocessing`**: Feature vectors & budget categorizations
            - **Future ML Engine**: User preference embeddings & route solvers
            """
        )
