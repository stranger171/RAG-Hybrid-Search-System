from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=100)
    student_class = models.CharField(max_length=10)

class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)
    marks = models.IntegerField()