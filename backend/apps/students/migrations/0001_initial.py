# Generated migration for Student model

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.IntegerField()),
                ('name', models.CharField(max_length=100)),
                ('age', models.IntegerField()),
                ('class_name', models.IntegerField()),
                ('section', models.CharField(max_length=5)),
                ('math_marks', models.IntegerField()),
                ('science_marks', models.IntegerField()),
                ('english_marks', models.IntegerField()),
                ('attendance_percentage', models.FloatField()),
                ('fees_paid', models.IntegerField()),
                ('fees_pending', models.IntegerField()),
                ('height', models.IntegerField()),
                ('weight', models.IntegerField()),
                ('blood_group', models.CharField(max_length=5)),
            ],
        ),
    ]
