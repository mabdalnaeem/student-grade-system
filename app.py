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

# Vibrant Academic UI/UX + Hover & Click Animations
st.markdown("""
<style>
    @keyframes fadeInSlide {
        0% {
            opacity: 0;
            transform: translateY(14px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulseGlow {
        0%, 100% {
            box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.35);
        }
        50% {
            box-shadow: 0 0 18px 2px rgba(59, 130, 246, 0.22);
        }
    }

    .block-container {
        animation: fadeInSlide 0.45s cubic-bezier(0.22, 1, 0.36, 1);
        padding-top: 1.5rem;
    }

    .portal-banner {
        background: linear-gradient(120deg, #0f172a 0%, #1d4ed8 52%, #0ea5e9 100%);
        border-radius: 18px;
        padding: 24px 28px;
        color: #ffffff;
        margin-bottom: 22px;
        border: 1px solid rgba(255, 255, 255, 0.16);
        box-shadow: 0 12px 30px rgba(29, 78, 216, 0.25);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }

    .portal-banner:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 36px rgba(14, 165, 233, 0.32);
    }

    .portal-title {
        font-size: 1.85rem;
        font-weight: 800;
        margin: 0 0 6px 0;
        letter-spacing: -0.3px;
    }

    .portal-sub {
        font-size: 0.98rem;
        opacity: 0.92;
        margin: 0;
    }

    .role-chip {
        display: inline-block;
        margin-top: 12px;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        background: rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(6px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    .stat-card {
        border-radius: 16px;
        padding: 20px 22px;
        color: #ffffff;
        transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.25s ease, filter 0.25s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }

    .stat-card:hover {
        transform: translateY(-6px) scale(1.02);
        filter: brightness(1.06);
        box-shadow: 0 14px 28px rgba(0, 0, 0, 0.28);
    }

    .stat-card:active {
        transform: translateY(-2px) scale(0.98);
    }

    .grad-blue {
        background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    }

    .grad-teal {
        background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);
    }

    .grad-purple {
        background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
    }

    .grad-amber {
        background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
    }

    .stat-label {
        font-size: 0.88rem;
        opacity: 0.9;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .stat-num {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .course-card {
        border-radius: 15px;
        padding: 18px;
        margin-bottom: 14px;
        color: #ffffff;
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%);
        border: 1px solid rgba(255, 255, 255, 0.15);
        transition: transform 0.24s ease, box-shadow 0.24s ease;
    }

    .course-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(79, 70, 229, 0.28);
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        background: linear-gradient(135deg, #2563eb 0%, #0ea5e9 100%) !important;
        color: #ffffff !important;
        padding: 0.55rem 1.15rem !important;
        transition: transform 0.18s ease, box-shadow 0.22s ease, filter 0.2s ease !important;
        animation: pulseGlow 3s infinite;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-3px) scale(1.015) !important;
        box-shadow: 0 10px 22px rgba(14, 165, 233, 0.35) !important;
        filter: brightness(1.08) !important;
    }

    .stButton > button:active, .stDownloadButton > button:active {
        transform: translateY(1px) scale(0.96) !important;
        box-shadow: 0 3px 8px rgba(14, 165, 233, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

data = load_data()

# Sidebar Role & Access Control
st.sidebar.markdown("### 🔐 Access & Role Control")
role = st.sidebar.selectbox(
    "Select Active Role",
    ["Admin", "Doctor", "Student"],
    help="Switch between Admin, Doctor, and Student access views."
)

role_descriptions = {
    "Admin": "Full Access: Manage students, Excel bulk import, courses, enrollments, grades & transcripts.",
    "Doctor": "Faculty Access: Enter/update course grades and view student transcripts.",
    "Student": "Student Access: View personal GPA, course grades, and download transcript CSV."
}
st.sidebar.info(role_descriptions[role])

if role == "Admin":
    menu_options = ["Overview & Students", "Courses & Enrollment", "Grade Entry", "Student Transcript"]
elif role == "Doctor":
    menu_options = ["Grade Entry", "Student Transcript"]
else:
    menu_options = ["Student Transcript"]

menu = st.sidebar.radio("Navigation", menu_options)

# Top Hero Banner
st.markdown(f"""
<div class="portal-banner">
    <p class="portal-title">🎓 Student Information & Grade Management System</p>
    <p class="portal-sub">Interactive Academic Records, Course Enrollment, GPA Calculation & Bulk Excel Import</p>
    <span class="role-chip">Active Role: {role}</span>
</div>
""", unsafe_allow_html=True)

def render_stat_card(title, value, gradient_class):
    st.markdown(f"""
    <div class="stat-card {gradient_class}">
        <div class="stat-label">{title}</div>
        <div class="stat-num">{value}</div>
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
        render_stat_card("Total Students", total_students, "grad-blue")
    with c2:
        render_stat_card("Active Courses", total_courses, "grad-teal")
    with c3:
        render_stat_card("Average GPA", f"{avg_gpa:.2f}", "grad-purple")
    with c4:
        render_stat_card("Enrollments", total_enrollments, "grad-amber")

    st.divider()

    # Bulk Import Students from Excel (.xlsx)
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

    # Add New Student
    st.subheader("➕ Add New Student")
    with st.form("add_student_form"):
        f1, f2, f3 = st.columns(3)
        sid = f1.text_input("Student ID (e.g., S101)")
        name = f2.text_input("Full Name")
        major = f3.text_input("Major / Group", value="Computer Science (F3)")
        if st.form_submit_button("Save Student"):
            ok, msg = add_student(data, sid, name, major)
            if ok:
                st.toast(msg, icon="🎓")
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    # Search & View Students
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
                        <div class="course-card">
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
        if st.form_submit_button("Create Course"):
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
            if st.form_submit_button("Enroll Student"):
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
            render_stat_card("Cumulative GPA", f"{gpa:.2f} / 4.00", "grad-purple")
        with m2:
            render_stat_card("Enrolled Courses", len(info["courses"]), "grad-teal")

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
