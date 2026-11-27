from data_handler import save_data
from validation import validate_id, validate_name, validate_credits

def add_course(data, course_code, course_name, credits):
    ok_code, res_code = validate_id(course_code)
    if not ok_code:
        return False, "Invalid Course Code."

    ok_name, res_name = validate_name(course_name)
    if not ok_name:
        return False, "Invalid Course Name."

    ok_cr, res_cr = validate_credits(credits)
    if not ok_cr:
        return False, res_cr

    if res_code in data["courses"]:
        return False, f"Course '{res_code}' already exists."

    data["courses"][res_code] = {
        "name": res_name,
        "credits": res_cr
    }
    save_data(data)
    return True, f"Course '{res_code} - {res_name}' added successfully."

def enroll_student(data, student_id, course_code):
    if student_id not in data["students"]:
        return False, "Student not found."
    if course_code not in data["courses"]:
        return False, "Course not found."
    if course_code in data["students"][student_id]["courses"]:
        return False, "Student is already enrolled in this course."

    data["students"][student_id]["courses"][course_code] = None
    save_data(data)
    return True, f"Enrolled student '{student_id}' in '{course_code}'."