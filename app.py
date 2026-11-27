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

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "active_role" not in st.session_state:
    st.session_state.active_role = "Admin"

if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Overview & Students"

data = load_data()

# Sidebar: Theme Switcher + Interactive Role & Navigation
with st.sidebar:
    st.markdown("### 🎨 Appearance Mode")
    theme_choice = st.segmented_control(
        "Theme",
        options=["Dark", "Light"],
        default=st.session_state.theme,
        label_visibility="collapsed"
    )
    if theme_choice and theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    st.divider()
    st.markdown("### 🔐 Role Switcher")
    roles = ["Admin", "Doctor", "Student"]
    role_cols = st.columns(3)
    for idx, r in enumerate(roles):
        with role_cols[idx]:
            if st.button(r, key=f"role_btn_{r}", use_container_width=True):
                st.session_state.active_role = r
                allowed_menus = {
                    "Admin": ["Overview & Students", "Courses & Enrollment", "Grade Entry", "Student Transcript"],
                    "Doctor": ["Grade Entry", "Student Transcript"],
                    "Student": ["Student Transcript"]
                }[r]
                if st.session_state.active_nav not in allowed_menus:
                    st.session_state.active_nav = allowed_menus[0]
                st.rerun()

    role = st.session_state.active_role
    role_badges = {
        "Admin": ("🛡️ Full Admin Access", "Students, Excel import, courses, enrollments, grades & transcripts."),
        "Doctor": ("🩺 Faculty Access", "Enter/update grades and inspect student transcripts."),
        "Student": ("🎒 Student Access", "View personal GPA, grades & download transcript CSV.")
    }
    badge_title, badge_desc = role_badges[role]
    st.markdown(f"""
    <div class="role-box">
        <div class="role-box-title">{badge_title}</div>
        <div class="role-box-desc">{badge_desc}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🧭 Navigation")
    if role == "Admin":
        menu_options = ["Overview & Students", "Courses & Enrollment", "Grade Entry", "Student Transcript"]
    elif role == "Doctor":
        menu_options = ["Grade Entry", "Student Transcript"]
    else:
        menu_options = ["Student Transcript"]

    if st.session_state.active_nav not in menu_options:
        st.session_state.active_nav = menu_options[0]

    for item in menu_options:
        is_selected = (st.session_state.active_nav == item)
        prefix = "➤ " if is_selected else "◦ "
        if st.button(f"{prefix}{item}", key=f"nav_{item}", use_container_width=True):
            st.session_state.active_nav = item
            st.rerun()

menu = st.session_state.active_nav
is_dark = (st.session_state.theme == "Dark")

# Dynamic Dark / Light Theme + Interactive Animations CSS
if is_dark:
    bg_main = "#090d16"
    bg_sidebar = "linear-gradient(180deg, #0f172a 0%, #111827 100%)"
    bg_card = "rgba(17, 24, 39, 0.85)"
    border_card = "rgba(99, 102, 241, 0.28)"
    text_main = "#f8fafc"
    text_muted = "#94a3b8"
    input_bg = "#1e293b"
    input_border = "#334155"
    shadow_card = "0 10px 28px rgba(0, 0, 0, 0.45)"
else:
    bg_main = "#f1f5f9"
    bg_sidebar = "linear-gradient(180deg, #ffffff 0%, #eef2ff 100%)"
    bg_card = "#ffffff"
    border_card = "rgba(37, 99, 235, 0.2)"
    text_main = "#0f172a"
    text_muted = "#475569"
    input_bg = "#f8fafc"
    input_border = "#cbd5e1"
    shadow_card = "0 10px 26px rgba(15, 23, 42, 0.08)"

st.markdown(f"""
<style>
    @keyframes fadeUp {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes floatSoft {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-3px); }}
    }}

    .stApp {{
        background: {bg_main};
        color: {text_main};
        transition: background 0.3s ease, color 0.3s ease;
    }}

    [data-testid="stSidebar"] {{
        background: {bg_sidebar};
        border-right: 1px solid {border_card};
        transition: all 0.3s ease;
    }}

    [data-testid="stSidebar"] .stButton > button {{
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 11px !important;
        padding: 0.52rem 0.85rem !important;
        margin-bottom: 4px !important;
        background: {input_bg} !important;
        color: {text_main} !important;
        border: 1px solid {input_border} !important;
        transition: transform 0.2s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease !important;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        transform: translateX(5px) scale(1.01) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 6px 18px rgba(56, 189, 248, 0.25) !important;
    }}

    [data-testid="stSidebar"] .stButton > button:active {{
        transform: translateX(2px) scale(0.96) !important;
    }}

    .role-box {{
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.18), rgba(124, 58, 237, 0.18));
        border: 1px solid {border_card};
        border-radius: 14px;
        padding: 12px 14px;
        margin-top: 8px;
        transition: transform 0.22s ease, box-shadow 0.22s ease;
    }}

    .role-box:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.22);
    }}

    .role-box-title {{
        font-weight: 800;
        font-size: 0.92rem;
        color: {text_main};
        margin-bottom: 4px;
    }}

    .role-box-desc {{
        font-size: 0.8rem;
        color: {text_muted};
        line-height: 1.4;
    }}

    .block-container {{
        animation: fadeUp 0.42s cubic-bezier(0.22, 1, 0.36, 1);
        padding-top: 1.2rem;
    }}

    .hero-card {{
        background: linear-gradient(125deg, #0f172a 0%, #1d4ed8 55%, #06b6d4 100%);
        border-radius: 20px;
        padding: 24px 28px;
        color: #ffffff;
        margin-bottom: 22px;
        box-shadow: 0 14px 32px rgba(29, 78, 216, 0.28);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }}

    .hero-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 18px 38px rgba(6, 182, 212, 0.34);
    }}

    .hero-title {{
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0 0 6px 0;
    }}

    .hero-sub {{
        font-size: 0.95rem;
        opacity: 0.92;
        margin: 0;
    }}

    .pill-tag {{
        display: inline-block;
        margin-top: 12px;
        margin-right: 8px;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }}

    .kpi-box {{
        border-radius: 16px;
        padding: 20px;
        color: #ffffff;
        box-shadow: {shadow_card};
        transition: transform 0.24s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.24s ease, filter 0.24s ease;
        cursor: pointer;
    }}

    .kpi-box:hover {{
        transform: translateY(-6px) scale(1.02);
        filter: brightness(1.07);
        box-shadow: 0 16px 30px rgba(59, 130, 246, 0.32);
    }}

    .kpi-box:active {{
        transform: scale(0.97);
    }}

    .g-blue {{ background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); }}
    .g-emerald {{ background: linear-gradient(135deg, #059669 0%, #0d9488 100%); }}
    .g-violet {{ background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); }}
    .g-amber {{ background: linear-gradient(135deg, #d97706 0%, #ea580c 100%); }}

    .kpi-lbl {{ font-size: 0.86rem; font-weight: 600; opacity: 0.92; margin-bottom: 6px; }}
    .kpi-val {{ font-size: 2rem; font-weight: 800; }}

    [data-testid="stForm"] {{
        background: {bg_card} !important;
        border: 1px solid {border_card} !important;
        border-radius: 18px !important;
        padding: 18px 20px !important;
        box-shadow: {shadow_card} !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
    }}

    [data-testid="stForm"]:hover {{
        border-color: #3b82f6 !important;
        box-shadow: 0 14px 32px rgba(59, 130, 246, 0.18) !important;
    }}

    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {text_main} !important;
        border-color: {input_border} !important;
        border-radius: 11px !important;
        transition: transform 0.18s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
    }}

    .stTextInput input:hover, .stSelectbox div[data-baseweb="select"] > div:hover {{
        border-color: #38bdf8 !important;
        transform: translateY(-1px);
    }}

    .stTextInput input:focus {{
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25) !important;
    }}

    .stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {{
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%) !important;
        color: #ffffff !important;
        padding: 0.55rem 1.2rem !important;
        transition: transform 0.18s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.22s ease, filter 0.2s ease !important;
    }}

    .stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {{
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 10px 22px rgba(6, 182, 212, 0.35) !important;
        filter: brightness(1.08) !important;
    }}

    .stButton > button:active, .stDownloadButton > button:active, [data-testid="stFormSubmitButton"] > button:active {{
        transform: translateY(1px) scale(0.95) !important;
        box-shadow: 0 3px 8px rgba(37, 99, 235, 0.25) !important;
    }}

    .course-tile {{
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 14px;
        color: #ffffff;
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%);
        box-shadow: {shadow_card};
        transition: transform 0.24s ease, box-shadow 0.24s ease;
    }}

    .course-tile:hover {{
        transform: translateY(-5px) scale(1.015);
        box-shadow: 0 14px 28px rgba(79, 70, 229, 0.32);
    }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero-card">
    <p class="hero-title">🎓 Student Information & Grade Management System</p>
    <p class="hero-sub">Interactive Academic Records, Course Enrollment, GPA Calculation & Bulk Excel Import</p>
    <span class="pill-tag">Role: {role}</span>
    <span class="pill-tag">Theme: {st.session_state.theme} Mode</span>
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
