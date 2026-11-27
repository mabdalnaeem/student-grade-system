from data_handler import save_data
from validation import validate_grade

def score_to_letter_and_points(score):
    if score >= 96:
        return "A+", 4.0
    elif score >= 90:
        return "A", 3.7
    elif score >= 85:
        return "B+", 3.3
    elif score >= 80:
        return "B", 3.0
    elif score >= 75:
        return "C+", 2.7
    elif score >= 70:
        return "C", 2.3
    elif score >= 65:
        return "D+", 2.0
    elif score >= 60:
        return "D", 1.7
    else:
        return "F", 0.0

def assign_grade(data, student_id, course_code, grade_input):
    if student_id not in data["students"]:
        return False, "Student not found."
    if course_code not in data["students"][student_id]["courses"]:
        return False, "Student is not enrolled in this course."

    ok_grade, res_grade = validate_grade(grade_input)
    if not ok_grade:
        return False, res_grade

    data["students"][student_id]["courses"][course_code] = res_grade
    save_data(data)
    return True, f"Grade {res_grade} recorded for {student_id} in {course_code}."

def calculate_gpa(data, student_id):
    student = data["students"].get(student_id)
    if not student:
        return 0.0

    total_points = 0.0
    total_credits = 0

    for code, score in student["courses"].items():
        if score is not None and code in data["courses"]:
            credits = data["courses"][code]["credits"]
            _, points = score_to_letter_and_points(score)
            total_points += points * credits
            total_credits += credits

    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

def get_transcript(data, student_id):
    student = data["students"].get(student_id)
    if not student:
        return None

    rows = []
    for code, score in student["courses"].items():
        course_info = data["courses"].get(code, {"name": "Unknown", "credits": 0})
        if score is not None:
            letter, points = score_to_letter_and_points(score)
        else:
            letter, points = "N/A", 0.0
        rows.append({
            "Course Code": code,
            "Course Name": course_info["name"],
            "Credits": course_info["credits"],
            "Score": score if score is not None else "Not Graded",
            "Grade": letter,
            "Points": points
        })
    return rows