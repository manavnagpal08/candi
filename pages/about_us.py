import streamlit as st

def about_us_page():
    """
    Renders the About Us page content with beautiful UI and honest, grounded information.
    """

    st.markdown('<div class="dashboard-header">🏢 About Us</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    .about-section {
        font-size: 17px;
        line-height: 1.7;
        padding-top: 10px;
    }
    .about-highlight {
        background-color: #f3f6fc;
        border-left: 4px solid #4e91f9;
        padding: 10px 15px;
        margin-top: 15px;
        border-radius: 8px;
    }
    .about-divider {
        margin: 30px 0;
        border-top: 2px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="about-section">', unsafe_allow_html=True)
    st.markdown("""
    Welcome to **ScreenerPro**, a resume screening assistant built with simplicity, clarity, and real impact in mind.

    We understand how overwhelming shortlisting can be for HR teams — going through hundreds of resumes manually, trying to find the right fit.  
    ScreenerPro is here to make that process more focused, data-backed, and efficient — without replacing human decision-making.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="about-divider"></div>', unsafe_allow_html=True)

    st.subheader("🎯 Our Mission")
    st.markdown('<div class="about-section">', unsafe_allow_html=True)
    st.markdown("""
    Our mission is to make the hiring process smoother and smarter by offering a tool that supports, not replaces, human decision-making.

    We aim to:
    - Save time during resume screening
    - Highlight important details recruiters might miss
    - Provide structured summaries to aid shortlisting
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("🚀 Our Vision")
    st.markdown('<div class="about-section">', unsafe_allow_html=True)
    st.markdown("""
    We believe in a future where hiring decisions are more objective and transparent.  
    AI should help remove noise — not add complexity.

    Our vision is to assist recruiters in finding qualified candidates faster, using responsible AI that respects privacy and fairness.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("💡 Our Values")
    st.markdown('<div class="about-highlight">', unsafe_allow_html=True)
    st.markdown("""
    - 🤝 **Respect for Recruiters**: The recruiter is always in control — we support decisions, not replace them.  
    - 🔐 **Privacy & Responsibility**: We avoid unnecessary data storage and prioritize ethical handling of candidate data.  
    - ⚙️ **Practical AI**: Our focus is usability — tools that work without needing a tech background.  
    - 📢 **Honest Communication**: We don’t overpromise. What you see is what you get.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("👥 Who We Are")
    st.markdown('<div class="about-section">', unsafe_allow_html=True)
    st.markdown("""
    ScreenerPro was built by a small but dedicated team of developers, designers, and HR enthusiasts who care about improving hiring experiences.

    We’re not a big corporation — we’re a hands-on team actively improving the product based on real user feedback.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("🧰 What We Offer")
    st.markdown('<div class="about-highlight">', unsafe_allow_html=True)
    st.markdown("""
    - A clean dashboard to upload and compare resumes  
    - AI-based scoring and keyword matching (not perfect — but helpful!)  
    - Downloadable reports and a visual view of candidate matching  
    - A simple system that doesn’t require technical training
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="about-divider"></div>', unsafe_allow_html=True)

    st.markdown("📫 **Want to learn more?** Reach us via the **'Feedback & Help'** section. We’d love to hear from you!")
