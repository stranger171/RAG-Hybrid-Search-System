from apps.students.models import Student

def get_all_students():
    students = Student.objects.all()
    return "\n".join([f"{s.id} - {s.name}" for s in students])