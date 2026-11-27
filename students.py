from data_handler import save_data
from validation import validate_id, validate_name

def add_student(data, student_id, name, major):
    ok_id, res_id = validate_id(student_id)
    if not ok_id:
        return False, res_id

    ok_name, res_name = validate_name(name)
    if not ok_name:
        return False, res_name

    if res_id in data["students"]:
        return False, f"Student ID '{res_id}' already exists."

    data["students"][res_id] = {
        "name": res_name,
        "major": major.strip() if major else "Computer Science",
        "courses": {}
    }
    save_data(data)
    return True, f"Student '{res_name}' added successfully."

def delete_student(data, student_id):
    if student_id in data["students"]:
        del data["students"][student_id]
        save_data(data)
        return True, f"Student '{student_id}' deleted."
    return False, "Student not found."

def search_students(data, query):
    query = query.strip().lower()
    results = {}
    for sid, info in data["students"].items():
        if query in sid.lower() or query in info["name"].lower():
            results[sid] = info
    return results