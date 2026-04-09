from django.db import models

class Student(models.Model):
    student_id = models.IntegerField()
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    class_name = models.IntegerField()
    section = models.CharField(max_length=5)

    math_marks = models.IntegerField()
    science_marks = models.IntegerField()
    english_marks = models.IntegerField()

    attendance_percentage = models.FloatField()

    fees_paid = models.IntegerField()
    fees_pending = models.IntegerField()

    height = models.IntegerField()
    weight = models.IntegerField()

    blood_group = models.CharField(max_length=5)

    def __str__(self):
        return self.name