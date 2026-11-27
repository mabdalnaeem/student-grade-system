import streamlit as st
import pandas as pd
from data_handler import load_data
from students import add_student, delete_student, search_students
from courses import add_course, enroll_student
from grades import assign_grade, calculate_gpa, get_transcript, score_to_letter_and_points

st.set_page_config(
    page_title="ECU Student Information & Grade Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "active_role" not in st.session_state:
    st.session_state.active_role = "Admin"

if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Overview & Students"

data = load_data()

# Full-page & role-based color themes
role_themes = {
    "Admin": {
        "primary": "#2563eb",
        "secondary": "#06b6d4",
        "gradient": "linear-gradient(135deg, #2563eb 0%, #06b6d4 100%)",
        "hero_bg": "linear-gradient(125deg, #091326 0%, #1d4ed8 55%, #0891b2 100%)",
        "page_bg": "radial-gradient(circle at 15% 15%, rgba(37, 99, 235, 0.24), transparent 42%), radial-gradient(circle at 85% 20%, rgba(6, 182, 212, 0.18), transparent 45%), linear-gradient(180deg, #071022 0%, #0b162c 55%, #071022 100%)",
        "sidebar_bg": "linear-gradient(180deg, #091224 0%, #0d1930 100%)",
        "glow": "rgba(37, 99, 235, 0.45)",
        "soft_bg": "rgba(37, 99, 235, 0.16)",
        "mode_label": "ADMIN MODE",
        "short_desc": "Full control: students, Excel, courses, grades & transcripts."
    },
    "Doctor": {
        "primary": "#059669",
        "secondary": "#10b981",
        "gradient": "linear-gradient(135deg, #059669 0%, #10b981 100%)",
        "hero_bg": "linear-gradient(125deg, #05231a 0%, #047857 55%, #0d9488 100%)",
        "page_bg": "radial-gradient(circle at 15% 15%, rgba(16, 185, 129, 0.22), transparent 42%), radial-gradient(circle at 85% 20%, rgba(13, 148, 136, 0.18), transparent 45%), linear-gradient(180deg, #061b15 0%, #09261e 55%, #061b15 100%)",
        "sidebar_bg": "linear-gradient(180deg, #061c16 0%, #0a2920 100%)",
        "glow": "rgba(16, 185, 129, 0.45)",
        "soft_bg": "rgba(16, 185, 129, 0.16)",
        "mode_label": "DOCTOR MODE",
        "short_desc": "Faculty view: enter grades & check student transcripts."
    },
    "Student": {
        "primary": "#9333ea",
        "secondary": "#ec4899",
        "gradient": "linear-gradient(135deg, #9333ea 0%, #ec4899 100%)",
        "hero_bg": "linear-gradient(125deg, #1b0d30 0%, #7e22ce 55%, #db2777 100%)",
        "page_bg": "radial-gradient(circle at 15% 15%, rgba(147, 51, 234, 0.24), transparent 42%), radial-gradient(circle at 85% 20%, rgba(236, 72, 153, 0.18), transparent 45%), linear-gradient(180deg, #120922 0%, #1b0d33 55%, #120922 100%)",
        "sidebar_bg": "linear-gradient(180deg, #130924 0%, #1d0e38 100%)",
        "glow": "rgba(236, 72, 153, 0.45)",
        "soft_bg": "rgba(147, 51, 234, 0.18)",
        "mode_label": "STUDENT MODE",
        "short_desc": "Student view: check GPA, grades & download CSV."
    }
}

role = st.session_state.active_role
rt = role_themes[role]

# Sidebar: 3 Primary Role Buttons + Compact Mode Indicator + Navigation
with st.sidebar:
    st.markdown(f"""
    <div class="compact-mode-banner" style="background:{rt['gradient']}; box-shadow:0 6px 18px {rt['glow']};">
        <span class="mode-dot"></span>
        <span>{rt['mode_label']}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='side-section-title'>MAIN ACCESS ROLES</div>", unsafe_allow_html=True)

    roles_meta = [
        ("Admin", "Full System Control"),
        ("Doctor", "Grades & Transcripts"),
        ("Student", "Personal GPA & CSV")
    ]

    for r, r_sub in roles_meta:
        is_selected = (st.session_state.active_role == r)
        marker_cls = "role-active-marker" if is_selected else "role-idle-marker"
        st.markdown(f"<div class='{marker_cls}'></div>", unsafe_allow_html=True)
        if st.button(f"{r}  •  {r_sub}", key=f"role_btn_{r}", use_container_width=True):
            st.session_state.active_role = r
            allowed_menus = {
                "Admin": ["Overview & Students", "Courses & Enrollment", "Grade Entry", "Student Transcript"],
                "Doctor": ["Grade Entry", "Student Transcript"],
                "Student": ["Student Transcript"]
            }[r]
            if st.session_state.active_nav not in allowed_menus:
                st.session_state.active_nav = allowed_menus[0]
            st.rerun()

    st.markdown(f"""
    <div class="compact-role-card" style="background:{rt['soft_bg']}; border-color:{rt['secondary']};">
        <div class="compact-role-title">{role} Active</div>
        <div class="compact-role-sub">{rt['short_desc']}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='side-section-title' style='margin-top:14px;'>NAVIGATION</div>", unsafe_allow_html=True)
    if role == "Admin":
        menu_options = ["Overview & Students", "Courses & Enrollment", "Grade Entry", "Student Transcript"]
    elif role == "Doctor":
        menu_options = ["Grade Entry", "Student Transcript"]
    else:
        menu_options = ["Student Transcript"]

    if st.session_state.active_nav not in menu_options:
        st.session_state.active_nav = menu_options[0]

    for item in menu_options:
        is_nav_selected = (st.session_state.active_nav == item)
        nav_cls = "nav-btn-active" if is_nav_selected else "nav-btn-idle"
        st.markdown(f"<div class='{nav_cls}'></div>", unsafe_allow_html=True)
        if st.button(item, key=f"nav_{item}", use_container_width=True):
            st.session_state.active_nav = item
            st.rerun()

menu = st.session_state.active_nav

# Unified sleek black cursor (no shape-switching glitch across blocks)
BLACK_CURSOR_SVG = (
    "data:image/svg+xml;utf8,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' width='28' height='28' viewBox='0 0 28 28'%3E"
    "%3Cpath d='M4 2 L23 14 L14 16 L18 25 L14 26.5 L10 17.5 L4 22 Z' "
    "fill='%2305070c' stroke='%23ffffff' stroke-width='1.6' stroke-linejoin='round'/%3E"
    "%3C/svg%3E"
)

st.markdown(f"""
<style>
    @keyframes fadeSlideDown {{
        from {{ opacity: 0; transform: translateY(-10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes pulseDot {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.35); opacity: 0.7; }}
    }}

    /* Unified black cursor across every element */
    .stApp, .stApp *,
    .stApp button, .stApp a, .stApp input, .stApp [role="combobox"],
    .stApp [data-testid="stFileUploaderDropzone"], .kpi-box, .course-tile, .hero-card {{
        cursor: url("{BLACK_CURSOR_SVG}") 4 2, auto !important;
    }}

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {{
        background: {rt['page_bg']} !important;
        color: #f8fafc !important;
        transition: background 0.35s ease, color 0.3s ease;
    }}

    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        inset: 0;
        background-image: radial-gradient(rgba(255, 255, 255, 0.06) 1px, transparent 1px);
        background-size: 24px 24px;
        pointer-events: none;
        z-index: 0;
    }}

    [data-testid="stHeader"] {{
        background: rgba(7, 11, 20, 0.72) !important;
        backdrop-filter: blur(10px);
    }}

    .block-container {{
        position: relative;
        z-index: 1;
        animation: fadeSlideDown 0.4s cubic-bezier(0.22, 1, 0.36, 1);
        padding-top: 3.4rem !important;
        padding-bottom: 2.5rem !important;
    }}

    [data-testid="stSidebar"] {{
        background: {rt['sidebar_bg']} !important;
        border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
        min-width: 225px !important;
        transition: background 0.35s ease;
    }}

    [data-testid="stSidebar"] .block-container {{
        padding-top: 1.2rem !important;
    }}

    .side-section-title {{
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        color: #cbd5e1;
        margin: 6px 0 8px 2px;
    }}

    .compact-mode-banner {{
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 11px;
        color: #ffffff;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        margin-bottom: 10px;
    }}

    .mode-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #ffffff;
        flex-shrink: 0;
        animation: pulseDot 1.8s infinite;
    }}

    .compact-role-card {{
        border: 1px solid;
        border-radius: 11px;
        padding: 9px 11px;
        margin-top: 8px;
    }}

    .compact-role-title {{
        font-size: 0.82rem;
        font-weight: 800;
        color: #ffffff;
    }}

    .compact-role-sub {{
        font-size: 0.72rem;
        color: #e2e8f0;
        line-height: 1.35;
        margin-top: 2px;
    }}

    .role-active-marker, .role-idle-marker, .nav-btn-active, .nav-btn-idle {{
        display: none;
    }}

    .role-active-marker + div [data-testid="stBaseButton-secondary"] {{
        background: {rt['gradient']} !important;
        color: #ffffff !important;
        border: 1px solid {rt['secondary']} !important;
        box-shadow: 0 5px 18px {rt['glow']} !important;
    }}

    .role-idle-marker + div [data-testid="stBaseButton-secondary"] {{
        background: rgba(15, 23, 42, 0.78) !important;
        color: #e2e8f0 !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
    }}

    .nav-btn-active + div [data-testid="stBaseButton-secondary"] {{
        background: {rt['gradient']} !important;
        color: #ffffff !important;
        border: 1px solid {rt['secondary']} !important;
        box-shadow: 0 6px 18px {rt['glow']} !important;
        font-weight: 800 !important;
    }}

    .nav-btn-idle + div [data-testid="stBaseButton-secondary"] {{
        background: rgba(15, 23, 42, 0.65) !important;
        color: #cbd5e1 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
    }}

    [data-testid="stSidebar"] .stButton > button {{
        border-radius: 10px !important;
        padding: 0.48rem 0.7rem !important;
        margin-bottom: 6px !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease !important;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        border-color: {rt['secondary']} !important;
        box-shadow: 0 6px 16px {rt['glow']} !important;
        filter: brightness(1.12) !important;
    }}

    .hero-card {{
        background: {rt['hero_bg']};
        border-radius: 20px;
        padding: 24px 28px;
        margin-bottom: 22px;
        border: 1px solid rgba(255, 255, 255, 0.16);
        box-shadow: 0 14px 34px {rt['glow']};
        transition: box-shadow 0.25s ease, filter 0.25s ease;
    }}

    .hero-card:hover {{
        box-shadow: 0 18px 42px {rt['glow']};
        filter: brightness(1.05);
    }}

    .hero-title {{
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff !important;
        margin: 0 0 6px 0;
    }}

    .hero-sub {{
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.92) !important;
        margin: 0;
    }}

    .pill-tag {{
        display: inline-block;
        margin-top: 12px;
        margin-right: 8px;
        padding: 4px 13px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.16);
        border: 1px solid rgba(255, 255, 255, 0.28);
        transition: background 0.2s ease, border-color 0.2s ease;
    }}

    .pill-tag:hover {{
        background: rgba(255, 255, 255, 0.28);
        border-color: #ffffff;
    }}

    .kpi-box {{
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 26px rgba(0, 0, 0, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.12);
        transition: box-shadow 0.25s ease, border-color 0.25s ease, filter 0.25s ease;
    }}

    .kpi-box:hover {{
        border-color: rgba(255, 255, 255, 0.55);
        box-shadow: 0 16px 34px {rt['glow']};
        filter: brightness(1.09);
    }}

    .g-blue {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); }}
    .g-emerald {{ background: linear-gradient(135deg, #059669 0%, #0d9488 100%); }}
    .g-violet {{ background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); }}
    .g-amber {{ background: linear-gradient(135deg, #d97706 0%, #ea580c 100%); }}

    .kpi-lbl {{ font-size: 0.86rem; font-weight: 600; color: rgba(255, 255, 255, 0.92) !important; margin-bottom: 6px; }}
    .kpi-val {{ font-size: 2rem; font-weight: 800; color: #ffffff !important; }}

    [data-testid="stForm"] {{
        background: rgba(15, 23, 42, 0.82) !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 18px !important;
        padding: 18px 20px !important;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.4) !important;
        transition: border-color 0.22s ease, box-shadow 0.22s ease !important;
    }}

    [data-testid="stForm"]:hover {{
        border-color: {rt['secondary']} !important;
        box-shadow: 0 14px 32px {rt['glow']} !important;
    }}

    [data-testid="stFileUploaderDropzone"] {{
        background-color: rgba(15, 23, 42, 0.82) !important;
        border: 1.5px dashed {rt['secondary']} !important;
        border-radius: 14px !important;
        transition: background-color 0.2s ease, box-shadow 0.2s ease !important;
    }}

    [data-testid="stFileUploaderDropzone"]:hover {{
        background-color: rgba(25, 39, 68, 0.92) !important;
        box-shadow: 0 10px 24px {rt['glow']} !important;
    }}

    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{
        background-color: rgba(20, 30, 52, 0.9) !important;
        color: #f8fafc !important;
        border-color: rgba(255, 255, 255, 0.18) !important;
        border-radius: 11px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease !important;
    }}

    .stTextInput input:hover, .stSelectbox div[data-baseweb="select"] > div:hover {{
        border-color: {rt['secondary']} !important;
        background-color: rgba(28, 42, 72, 0.95) !important;
    }}

    .stTextInput input:focus {{
        border-color: {rt['secondary']} !important;
        box-shadow: 0 0 0 3px {rt['glow']} !important;
    }}

    .main .stButton > button, .main .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {{
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        background: {rt['gradient']} !important;
        color: #ffffff !important;
        padding: 0.55rem 1.25rem !important;
        transition: box-shadow 0.2s ease, filter 0.2s ease !important;
    }}

    .main .stButton > button:hover, .main .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {{
        box-shadow: 0 8px 22px {rt['glow']} !important;
        filter: brightness(1.1) !important;
    }}

    .course-tile {{
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 14px;
        background: {rt['gradient']};
        box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
        transition: box-shadow 0.22s ease, filter 0.22s ease !important;
    }}

    .course-tile:hover {{
        box-shadow: 0 14px 30px {rt['glow']} !important;
        filter: brightness(1.08);
    }}

    .course-tile div {{
        color: #ffffff !important;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero-card">
    <p class="hero-title">🎓 Student Information & Grade Management System</p>
    <p class="hero-sub">Interactive Academic Records, Course Enrollment, GPA Calculation & Bulk Excel Import</p>
    <span class="pill-tag">Active Role: {role}</span>
    <span class="pill-tag">Color Mode: {rt['mode_label']}</span>
</div>
""", unsafe_allow_html=True)

def render_kpi(title, value, grad):
    st.markdown(f"""
    <div class="kpi-box {grad}">
        <div class="kpi-lbl">{title}</div>
        <div class="kpi-val">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# 1. Overview & Students (Admin)
if menu == "Overview & Students":
    total_students = len(data["students"])
    total_courses = len(data["courses"])
    gpas = [calculate_gpa(data, sid) for sid in data["students"]]
    avg_gpa = round(sum(gpas) / len(gpas), 2) if gpas else 0.0
    total_enrollments = sum(len(info["courses"]) for info in data["students"].values())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi("Total Students", total_students, "g-blue")
    with c2:
        render_kpi("Active Courses", total_courses, "g-emerald")
    with c3:
        render_kpi("Average GPA", f"{avg_gpa:.2f}", "g-violet")
    with c4:
        render_kpi("Enrollments", total_enrollments, "g-amber")

    st.divider()

    st.subheader("📥 Bulk Import Students from Excel")
    st.caption("Supports columns: `ID` or `Student ID`, `Name`, and optional `Group` or `Major`")
    uploaded_excel = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

    if uploaded_excel is not None:
        try:
            excel_df = pd.read_excel(uploaded_excel)
            excel_df.columns = [str(col).strip() for col in excel_df.columns]
            st.dataframe(excel_df.head(15), use_container_width=True)

            if st.button("🚀 Import All Valid Students"):
                id_col = "Student ID" if "Student ID" in excel_df.columns else ("ID" if "ID" in excel_df.columns else None)
                name_col = "Name" if "Name" in excel_df.columns else None

                if not id_col or not name_col:
                    st.error("Excel file must contain 'ID' (or 'Student ID') and 'Name' columns.")
                else:
                    added_count = 0
                    errors = []
                    for idx, row in excel_df.iterrows():
                        sid_val = "" if pd.isna(row[id_col]) else str(row[id_col]).strip()
                        name_val = "" if pd.isna(row[name_col]) else str(row[name_col]).strip()

                        if "Major" in excel_df.columns and not pd.isna(row["Major"]):
                            major_val = str(row["Major"]).strip()
                        elif "Group" in excel_df.columns and not pd.isna(row["Group"]):
                            major_val = f"Computer Science ({str(row['Group']).strip()})"
                        else:
                            major_val = "Computer Science"

                        ok, msg = add_student(data, sid_val, name_val, major_val)
                        if ok:
                            added_count += 1
                        else:
                            errors.append(f"Row {idx + 2}: {msg}")

                    st.toast(f"Imported {added_count} student(s)!", icon="✅")
                    if added_count > 0:
                        st.balloons()
                    st.success(f"Imported {added_count} student(s) successfully.")
                    if errors:
                        with st.expander("Skipped Rows Details"):
                            for err in errors:
                                st.warning(err)
                    st.rerun()
        except Exception as e:
            st.error(f"Could not read Excel file: {e}")

    st.divider()

    st.subheader("➕ Add New Student")
    with st.form("add_student_form"):
        f1, f2, f3 = st.columns(3)
        sid = f1.text_input("Student ID (e.g., S101)")
        name = f2.text_input("Full Name")
        major = f3.text_input("Major / Group", value="Computer Science (F3)")
        if st.form_submit_button("✨ Save Student"):
            ok, msg = add_student(data, sid, name, major)
            if ok:
                st.toast(msg, icon="🎓")
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.subheader("🔎 Search & View Students")
    query = st.text_input("Search by Student ID or Name")
    filtered = search_students(data, query) if query else data["students"]

    if filtered:
        table_rows = []
        for s_id, info in filtered.items():
            table_rows.append({
                "Student ID": s_id,
                "Name": info["name"],
                "Major": info["major"],
                "Enrolled Courses": len(info["courses"]),
                "GPA": calculate_gpa(data, s_id)
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True)

        del_id = st.selectbox("Select Student to Delete", list(filtered.keys()))
        if st.button("🗑️ Delete Selected Student"):
            ok, msg = delete_student(data, del_id)
            if ok:
                st.toast(msg, icon="🗑️")
                st.warning(msg)
            else:
                st.error(msg)
            st.rerun()
    else:
        st.info("No students found. Add a student above or upload an Excel file.")

# 2. Courses & Enrollment (Admin)
elif menu == "Courses & Enrollment":
    st.header("📚 Courses & Enrollment")

    if data["courses"]:
        st.subheader("Course Overview Cards")
        course_items = list(data["courses"].items())
        for i in range(0, len(course_items), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(course_items):
                    c_code, c_info = course_items[i + j]
                    with col:
                        st.markdown(f"""
                        <div class="course-tile">
                            <div style="font-size:0.82rem; opacity:0.88; font-weight:700;">{c_code} • {c_info['credits']} Credits</div>
                            <div style="font-size:1.15rem; font-weight:800; margin-top:4px;">{c_info['name']}</div>
                        </div>
                        """, unsafe_allow_html=True)

    st.subheader("➕ Add New Course")
    with st.form("add_course_form"):
        c1, c2, c3 = st.columns(3)
        code = c1.text_input("Course Code (e.g., CSC1100)")
        cname = c2.text_input("Course Name (e.g., Computer Programming I)")
        credits = c3.text_input("Credit Hours (1-6)", value="3")
        if st.form_submit_button("📘 Create Course"):
            ok, msg = add_course(data, code, cname, credits)
            if ok:
                st.toast(msg, icon="📘")
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.subheader("📝 Enroll Student in a Course")
    if data["students"] and data["courses"]:
        with st.form("enroll_form"):
            sel_student = st.selectbox("Select Student", list(data["students"].keys()))
            sel_course = st.selectbox("Select Course", list(data["courses"].keys()))
            if st.form_submit_button("✅ Enroll Student"):
                ok, msg = enroll_student(data, sel_student, sel_course)
                if ok:
                    st.toast(msg, icon="✅")
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    else:
        st.info("Add at least one student and one course to enroll students.")

# 3. Grade Entry (Admin & Doctor)
elif menu == "Grade Entry":
    st.header(f"📝 Grade Entry ({role} Portal)")
    if not data["students"]:
        st.info("No students available.")
    else:
        sel_student = st.selectbox("Select Student", list(data["students"].keys()))
        enrolled = list(data["students"][sel_student]["courses"].keys())
        if not enrolled:
            st.warning("This student is not enrolled in any courses yet.")
        else:
            with st.form("grade_form"):
                sel_course = st.selectbox("Select Enrolled Course", enrolled)
                grade_val = st.text_input("Enter Score (0 - 100)")
                if st.form_submit_button("💾 Save Grade"):
                    ok, msg = assign_grade(data, sel_student, sel_course, grade_val)
                    if ok:
                        letter, pts = score_to_letter_and_points(float(grade_val))
                        st.toast(f"{msg} ({letter} | {pts} pts)", icon="🏅")
                        st.success(f"{msg} — Grade: **{letter}** ({pts} points)")
                        st.rerun()
                    else:
                        st.error(msg)

# 4. Student Transcript (All Roles)
elif menu == "Student Transcript":
    st.header(f"📄 Official Student Transcript ({role} View)")
    if not data["students"]:
        st.info("No students available.")
    else:
        student_ids = list(data["students"].keys())
        sel_student = st.selectbox("Select Student ID", student_ids)
        info = data["students"][sel_student]
        gpa = calculate_gpa(data, sel_student)

        st.markdown(f"**Student Name:** {info['name']} &nbsp;|&nbsp; **ID:** `{sel_student}` &nbsp;|&nbsp; **Major:** {info['major']}")

        m1, m2 = st.columns(2)
        with m1:
            render_kpi("Cumulative GPA", f"{gpa:.2f} / 4.00", "g-violet")
        with m2:
            render_kpi("Enrolled Courses", len(info["courses"]), "g-emerald")

        st.write("")
        rows = get_transcript(data, sel_student)
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download Transcript (CSV)",
                data=csv,
                file_name=f"transcript_{sel_student}.csv",
                mime="text/csv"
            )
        else:
            st.info("No courses enrolled for this student yet.")
