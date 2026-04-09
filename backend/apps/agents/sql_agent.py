"""
SQL Agent for querying Student data from Neon PostgreSQL database
Works with the Student model containing: name, age, class, marks, attendance, fees, health data
"""

from apps.students.models import Student
from django.db.models import Q, Avg


def get_all_students():
    """Get all students from database"""
    students = Student.objects.all()[:10]  # Limit to 10 for display
    if not students:
        return "No students found in database"
    
    result = []
    for s in students:
        result.append(f"ID: {s.student_id} - {s.name} (Class: {s.class_name}{s.section})")
    return "\n".join(result)


def search_students_by_name(name: str):
    """Search for students by name from Neon database"""
    students = Student.objects.filter(name__icontains=name)[:10]
    if not students:
        return f"No students found with name matching '{name}'"
    
    result = []
    for student in students:
        avg_marks = (student.math_marks + student.science_marks + student.english_marks) / 3
        result.append(
            f"• {student.name} (ID: {student.student_id}, Class: {student.class_name}{student.section}) - "
            f"Avg Marks: {avg_marks:.1f}"
        )
    return "\n".join(result)


def get_full_student_by_name(name: str):
    """Get full details of a student by name from Neon database"""
    student = Student.objects.filter(name__icontains=name).first()
    if not student:
        return f"No student found with name '{name}'"
    
    avg_marks = (student.math_marks + student.science_marks + student.english_marks) / 3
    
    return (
        f"📋 Student Details:\n"
        f"  Name: {student.name}\n"
        f"  Student ID: {student.student_id}\n"
        f"  Age: {student.age}\n"
        f"  Class: {student.class_name}{student.section}\n"
        f"  Math: {student.math_marks}, Science: {student.science_marks}, English: {student.english_marks}\n"
        f"  Average Marks: {avg_marks:.1f}\n"
        f"  Attendance: {student.attendance_percentage}%\n"
        f"  Blood Group: {student.blood_group}"
    )


def get_student_by_id(student_id: int):
    """Get a specific student by ID from Neon database"""
    try:
        student = Student.objects.get(student_id=student_id)
        avg_marks = (student.math_marks + student.science_marks + student.english_marks) / 3
        
        return (
            f"📋 Student Details:\n"
            f"  Name: {student.name}\n"
            f"  Student ID: {student.student_id}\n"
            f"  Age: {student.age}\n"
            f"  Class: {student.class_name}{student.section}\n"
            f"  Math: {student.math_marks}, Science: {student.science_marks}, English: {student.english_marks}\n"
            f"  Average Marks: {avg_marks:.1f}\n"
            f"  Attendance: {student.attendance_percentage}%\n"
            f"  Blood Group: {student.blood_group}"
        )
    except Student.DoesNotExist:
        return f"Student with ID {student_id} not found in database"


def get_marks_for_student(student_id: int):
    """Get marks details for a specific student"""
    try:
        student = Student.objects.get(student_id=student_id)
        return (
            f"📊 Marks for {student.name}:\n"
            f"  Math: {student.math_marks}/100\n"
            f"  Science: {student.science_marks}/100\n"
            f"  English: {student.english_marks}/100\n"
            f"  Average: {(student.math_marks + student.science_marks + student.english_marks) / 3:.1f}/100"
        )
    except Student.DoesNotExist:
        return f"Student with ID {student_id} not found"


def search_students_by_class(class_name: str):
    """Get all students in a specific class"""
    try:
        class_num = int(class_name) if class_name.isdigit() else class_name
        students = Student.objects.filter(class_name=class_num)[:20]
    except ValueError:
        students = Student.objects.filter(class_name__icontains=class_name)[:20]
    
    if not students:
        return f"No students found in class '{class_name}'"
    
    result = [f"👥 Students in Class {class_name}:"]
    for student in students:
        result.append(f"  • {student.name} (Section: {student.section}, Attendance: {student.attendance_percentage}%)")
    
    return "\n".join(result)


def get_students_with_high_marks(subject: str, min_marks: int):
    """Get students with marks above a threshold in a subject"""
    subject_lower = subject.lower()
    
    if "math" in subject_lower:
        students = Student.objects.filter(math_marks__gte=min_marks)[:20]
        subject_name = "Math"
    elif "science" in subject_lower:
        students = Student.objects.filter(science_marks__gte=min_marks)[:20]
        subject_name = "Science"
    elif "english" in subject_lower:
        students = Student.objects.filter(english_marks__gte=min_marks)[:20]
        subject_name = "English"
    else:
        return f"Subject '{subject}' not recognized. Use: Math, Science, or English"
    
    if not students:
        return f"No students found with {min_marks}+ marks in {subject_name}"
    
    result = [f"🌟 Top Performers in {subject_name} ({min_marks}+ marks):"]
    for student in students:
        if "math" in subject_lower:
            marks = student.math_marks
        elif "science" in subject_lower:
            marks = student.science_marks
        else:
            marks = student.english_marks
        
        result.append(f"  • {student.name} ({student.class_name}{student.section}): {marks} marks")
    
    return "\n".join(result)


def get_students_by_attendance(min_attendance: float):
    """Get students with attendance above a threshold"""
    students = Student.objects.filter(attendance_percentage__gte=min_attendance)[:20]
    
    if not students:
        return f"No students found with {min_attendance}% or higher attendance"
    
    result = [f"📈 Students with {min_attendance}%+ Attendance:"]
    for student in students:
        result.append(f"  • {student.name} ({student.class_name}{student.section}): {student.attendance_percentage}%")
    
    return "\n".join(result)


def get_fees_status(status: str = "pending"):
    """Get students by fees payment status"""
    if status.lower() == "pending":
        students = Student.objects.filter(fees_pending__gt=0)[:20]
        title = "💰 Students with Pending Fees:"
    else:
        students = Student.objects.filter(fees_paid__gt=0)[:20]
        title = "✅ Students with Paid Fees:"
    
    if not students:
        return f"No matching records for fees {status}"
    
    result = [title]
    for student in students:
        if status.lower() == "pending":
            result.append(f"  • {student.name}: ₹{student.fees_pending} pending (Paid: ₹{student.fees_paid})")
        else:
            result.append(f"  • {student.name}: ₹{student.fees_paid} paid")
    
    return "\n".join(result)


def get_class_statistics(class_name: str):
    """Get statistics for a specific class"""
    try:
        class_num = int(class_name) if class_name.isdigit() else class_name
        students = Student.objects.filter(class_name=class_num)
    except ValueError:
        students = Student.objects.filter(class_name__icontains=class_name)
    
    if not students:
        return f"No students found in class '{class_name}'"
    
    count = students.count()
    avg_math = students.aggregate(Avg('math_marks'))['math_marks__avg'] or 0
    avg_science = students.aggregate(Avg('science_marks'))['science_marks__avg'] or 0
    avg_english = students.aggregate(Avg('english_marks'))['english_marks__avg'] or 0
    avg_attendance = students.aggregate(Avg('attendance_percentage'))['attendance_percentage__avg'] or 0
    
    return (
        f"📊 Class {class_name} Statistics:\n"
        f"  Total Students: {count}\n"
        f"  Average Marks - Math: {avg_math:.1f}, Science: {avg_science:.1f}, English: {avg_english:.1f}\n"
        f"  Average Attendance: {avg_attendance:.1f}%"
    )


def get_random_students(limit: int = 5):
    """Get random students from database for general browsing"""
    import random
    total_count = Student.objects.count()
    if total_count == 0:
        return "No students found in database"
    
    # Get random sample
    random_offset = random.randint(0, max(0, total_count - limit))
    students = Student.objects.all()[random_offset:random_offset + limit]
    
    result = ["📚 Sample Students from Database:"]
    for student in students:
        avg_marks = (student.math_marks + student.science_marks + student.english_marks) / 3
        result.append(
            f"  • {student.name} (ID: {student.student_id}, Class: {student.class_name}{student.section}) - "
            f"Avg: {avg_marks:.1f}, Attendance: {student.attendance_percentage}%"
        )
    return "\n".join(result)


def get_student_field(student_identifier, field_name: str):
    """
    Generic function to get any field/column value for a student.
    Works with any student identifier (ID or name) and any column name.
    
    Args:
        student_identifier: Either student_id (int) or name (str)
        field_name: The database column name to retrieve (e.g., 'blood_group', 'age', 'height', etc.)
    
    Returns:
        Formatted string with the field value from Neon database
    """
    try:
        # Find the student
        if isinstance(student_identifier, int):
            student = Student.objects.get(student_id=student_identifier)
        else:
            student = Student.objects.filter(name__icontains=student_identifier).first()
            if not student:
                return f"No student found with name '{student_identifier}'"
        
        # Map field names to model attributes
        field_mapping = {
            "age": "age",
            "class": "class_name",
            "class_name": "class_name",
            "section": "section",
            "math": "math_marks",
            "math_marks": "math_marks",
            "science": "science_marks",
            "science_marks": "science_marks",
            "english": "english_marks",
            "english_marks": "english_marks",
            "attendance": "attendance_percentage",
            "attendance_percentage": "attendance_percentage",
            "fees_paid": "fees_paid",
            "fees_pending": "fees_pending",
            "height": "height",
            "weight": "weight",
            "blood_group": "blood_group",
        }
        
        # Normalize field name
        normalized_field = field_mapping.get(field_name.lower(), field_name.lower())
        
        # Check if student has this attribute
        if not hasattr(student, normalized_field):
            return f"Field '{field_name}' not found in student database"
        
        # Get the value
        value = getattr(student, normalized_field)
        
        # Format the response based on field type
        field_display_names = {
            "age": "Age",
            "class_name": "Class",
            "section": "Section",
            "math_marks": "Math Marks",
            "science_marks": "Science Marks",
            "english_marks": "English Marks",
            "attendance_percentage": "Attendance",
            "fees_paid": "Fees Paid",
            "fees_pending": "Fees Pending",
            "height": "Height",
            "weight": "Weight",
            "blood_group": "Blood Group",
        }
        
        display_name = field_display_names.get(normalized_field, field_name)
        
        # Format value based on field type
        if "marks" in normalized_field:
            formatted_value = f"{value}/100"
        elif "attendance" in normalized_field:
            formatted_value = f"{value}%"
        elif "fees" in normalized_field:
            formatted_value = f"₹{value}"
        elif "height" in normalized_field:
            formatted_value = f"{value} cm"
        elif "weight" in normalized_field:
            formatted_value = f"{value} kg"
        else:
            formatted_value = str(value)
        
        return f"{display_name} of {student.name}: {formatted_value}"
        
    except Student.DoesNotExist:
        return f"Student with ID {student_identifier} not found in database"
    except Exception as e:
        return f"Error retrieving field '{field_name}': {str(e)}"