import streamlit as st
import pandas as pd
from data_handler import load_data
from students import add_student, delete_student, search_students
from courses import add_course, enroll_student
from grades import assign_grade, calculate_gpa, get_transcript

st.set_page_config(page_title="Student Grade System", page_icon="🎓", layout="wide")

# Interactive UI/UX styling & hover animations
st.markdown("""
<style>
    @keyframes fadeSlideUp {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .block-container {
        animation: fadeSlideUp 0.45s ease-out;
    }

    .kpi-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.015));
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 14px;
        padding: 18px 20px;
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        cursor: pointer;
    }

    .kpi-card:hover {
        transform: translateY(-5px) scale(1.01);
        border-color: #4f8bf9;
        box-shadow: 0 10px 24px rgba(79, 139, 249, 0.2);
    }

    .kpi-title {
        font-size: 0.9rem;
        opacity: 0.78;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 10px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.22);
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 Student Information & Grade Management System")

data = load_data()

# Role Switcher in Sidebar
role = st.sidebar.selectbox("Select Active Role", ["Admin", "Doctor", "Student"])
st.sidebar.caption(f"Current Access Level: **{role}**")

if role == "Admin":
    menu_options = ["Dashboard & Students", "Courses & Enrollment", "Grade Entry", "Student Transcript"]
elif role == "Doctor":
    menu_options = ["Grade Entry", "Student Transcript"]
else:
    menu_options = ["Student Transcript"]

menu = st.sidebar.radio("Navigation", menu_options)

def render_kpi_card(title, value):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# 1. Dashboard & Students (Admin)
if menu == "Dashboard & Students":
    st.header("Student Records & Bulk Import")

    total_students = len(data["students"])
    total_courses = len(data["courses"])
    gpas = [calculate_gpa(data, sid) for sid in data["students"]]
    avg_gpa = round(sum(gpas) / len(gpas), 2) if gpas else 0.0

    col1, col2, col3 = st.columns(3)
    with col1:
        render_kpi_card("Total Students", total_students)
    with col2:
        render_kpi_card("Total Courses", total_courses)
    with col3:
        render_kpi_card("Average GPA", avg_gpa)

    st.divider()

    # Bulk Upload Students via Excel (.xlsx)
    st.subheader("📥 Bulk Import Students from Excel")
    st.caption("Expected columns: `Student ID`, `Name`, and optional `Major`")
    uploaded_excel = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

    if uploaded_excel is not None:
        try:
            excel_df = pd.read_excel(uploaded_excel)
            st.dataframe(excel_df.head(10), use_container_width=True)

            if st.button("Import All Valid Students"):
                required_cols = {"Student ID", "Name"}
                if not required_cols.issubset(set(excel_df.columns)):
                    st.error("Excel file must contain 'Student ID' and 'Name' columns.")
                else:
                    added_count = 0
                    errors = []
                    for idx, row in excel_df.iterrows():
                        sid_val = "" if pd.isna(row["Student ID"]) else str(row["Student ID"]).strip()
                        name_val = "" if pd.isna(row["Name"]) else str(row["Name"]).strip()
                        major_val = (
                            "Computer Science"
                            if "Major" not in excel_df.columns or pd.isna(row["Major"])
                            else str(row["Major"]).strip()
                        )
                        ok, msg = add_student(data, sid_val, name_val, major_val)
                        if ok:
                            added_count += 1
                        else:
                            errors.append(f"Row {idx + 2}: {msg}")

                    st.success(f"Imported {added_count} student(s) successfully.")
                    if errors:
                        with st.expander("Skipped Rows Details"):
                            for err in errors:
                                st.warning(err)
                    st.rerun()
        except Exception as e:
            st.error(f"Could not read Excel file: {e}")

    st.divider()

    st.subheader("Add New Student")
    with st.form("add_student_form"):
        c1, c2, c3 = st.columns(3)
        sid = c1.text_input("Student ID (e.g., S101)")
        name = c2.text_input("Full Name")
        major = c3.text_input("Major", value="Computer Science")
        if st.form_submit_button("Add Student"):
            ok, msg = add_student(data, sid, name, major)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.subheader("Search & View Students")
    query = st.text_input("Search by ID or Name")
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
        if st.button("Delete Selected Student"):
            ok, msg = delete_student(data, del_id)
            st.warning(msg) if ok else st.error(msg)
            st.rerun()
    else:
        st.info("No students found. Add a student above or upload an Excel sheet.")

# 2. Courses & Enrollment (Admin)
elif menu == "Courses & Enrollment":
    st.header("Courses & Enrollment")

    st.subheader("Add New Course")
    with st.form("add_course_form"):
        c1, c2, c3 = st.columns(3)
        code = c1.text_input("Course Code (e.g., CSC1100)")
        cname = c2.text_input("Course Name")
        credits = c3.text_input("Credit Hours (1-6)", value="3")
        if st.form_submit_button("Add Course"):
            ok, msg = add_course(data, code, cname, credits)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.subheader("Enroll Student in a Course")
    if data["students"] and data["courses"]:
        with st.form("enroll_form"):
            sel_student = st.selectbox("Select Student", list(data["students"].keys()))
            sel_course = st.selectbox("Select Course", list(data["courses"].keys()))
            if st.form_submit_button("Enroll"):
                ok, msg = enroll_student(data, sel_student, sel_course)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    else:
        st.info("Please add at least one student and one course first.")

# 3. Grade Entry (Admin & Doctor)
elif menu == "Grade Entry":
    st.header(f"Grade Entry ({role} View)")
    if not data["students"]:
        st.info("No students available.")
    else:
        sel_student = st.selectbox("Select Student", list(data["students"].keys()))
        enrolled = list(data["students"][sel_student]["courses"].keys())
        if not enrolled:
            st.warning("This student is not enrolled in any courses yet.")
        else:
            with st.form("grade_form"):
                sel_course = st.selectbox("Select Course", enrolled)
                grade_val = st.text_input("Enter Score (0 - 100)")
                if st.form_submit_button("Save Grade"):
                    ok, msg = assign_grade(data, sel_student, sel_course, grade_val)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

# 4. Student Transcript (All Roles)
elif menu == "Student Transcript":
    st.header(f"Official Student Transcript ({role} View)")
    if not data["students"]:
        st.info("No students available.")
    else:
        student_ids = list(data["students"].keys())
        sel_student = st.selectbox("Select Student ID", student_ids)
        info = data["students"][sel_student]
        gpa = calculate_gpa(data, sel_student)

        st.markdown(f"**Student Name:** {info['name']} | **ID:** {sel_student} | **Major:** {info['major']}")
        render_kpi_card("Cumulative GPA", f"{gpa} / 4.00")
        st.write("")

        rows = get_transcript(data, sel_student)
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Transcript (CSV)",
                data=csv,
                file_name=f"transcript_{sel_student}.csv",
                mime="text/csv"
            )
        else:
            st.info("No courses enrolled for this student yet.")
