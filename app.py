import streamlit as st
import pandas as pd
from data_handler import load_data
from students import add_student, delete_student, search_students
from courses import add_course, enroll_student
from grades import assign_grade, calculate_gpa, get_transcript

st.set_page_config(page_title="Student Grade System", page_icon="🎓", layout="wide")
st.title("🎓 Student Information & Grade Management System")

data = load_data()

menu = st.sidebar.radio(
    "Navigation",
    ["Dashboard & Students", "Courses & Enrollment", "Grade Entry", "Student Transcript"]
)

# 1. Dashboard & Students
if menu == "Dashboard & Students":
    st.header("Student Records")

    total_students = len(data["students"])
    total_courses = len(data["courses"])
    gpas = [calculate_gpa(data, sid) for sid in data["students"]]
    avg_gpa = round(sum(gpas) / len(gpas), 2) if gpas else 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students", total_students)
    col2.metric("Total Courses", total_courses)
    col3.metric("Average GPA", avg_gpa)

    st.subheader("Add New Student")
    with st.form("add_student_form"):
        c1, c2, c3 = st.columns(3)
        sid = c1.text_input("Student ID (e.g., S101)")
        name = c2.text_input("Full Name")
        major = c3.text_input("Major", value="Computer Science")
        submitted = st.form_submit_button("Add Student")
        if submitted:
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
        st.info("No students found. Add a student above to get started.")

# 2. Courses & Enrollment
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

# 3. Grade Entry
elif menu == "Grade Entry":
    st.header("Grade Entry")
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

# 4. Student Transcript
elif menu == "Student Transcript":
    st.header("Official Student Transcript")
    if not data["students"]:
        st.info("No students available.")
    else:
        sel_student = st.selectbox("Select Student", list(data["students"].keys()))
        info = data["students"][sel_student]
        gpa = calculate_gpa(data, sel_student)

        st.markdown(f"**Student Name:** {info['name']} | **ID:** {sel_student} | **Major:** {info['major']}")
        st.metric("Cumulative GPA", f"{gpa} / 4.00")

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