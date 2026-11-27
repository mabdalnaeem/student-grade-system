def validate_id(student_id):
    if not student_id or not student_id.strip():
        return False, "Student ID cannot be empty."
    if not student_id.strip().isalnum():
        return False, "Student ID must contain letters or numbers only."
    return True, student_id.strip().upper()

def validate_name(name):
    if not name or not name.strip():
        return False, "Name cannot be empty."
    if len(name.strip()) < 2:
        return False, "Name is too short."
    return True, name.strip()

def validate_grade(grade_input):
    try:
        grade = float(grade_input)
        if 0 <= grade <= 100:
            return True, grade
        return False, "Grade must be between 0 and 100."
    except (ValueError, TypeError):
        return False, "Invalid input! Please enter a numeric grade."

def validate_credits(credits_input):
    try:
        credits = int(credits_input)
        if 1 <= credits <= 6:
            return True, credits
        return False, "Credits must be between 1 and 6."
    except (ValueError, TypeError):
        return False, "Invalid input! Credits must be a whole number."