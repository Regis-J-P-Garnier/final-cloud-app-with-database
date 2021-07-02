import sys
from django.utils.timezone import now
from django.template.defaultfilters import default
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings
import uuid


# Instructor model
class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    id=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    id=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return self.user.username + "," + \
               self.occupation


# Course model
class Course(models.Model):
    id=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return "Name: " + self.name + "," + \
               "Description: " + self.description


# Lesson model
class Lesson(models.Model):
    id=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()


# Enrollment model
# <HINT> Once a user enrolled a class, an enrollment entry should be created between the user and course
# And we could use the enrollment to track information such as exam submissions
class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    id=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    # ternary data link as composite primary key (why an PK id ?)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    #
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)

class Question(models.Model):
    '''Used to persist question content for a course'''
    id=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    text = models.CharField(max_length=200)# Has question content
    grade=models.FloatField(default=1.0)# Has a grade point for each question
    course= models.ForeignKey(Course, on_delete=models.CASCADE)# Has a One-To-Many (or Many-To-Many if you want to reuse questions) relationship with course
    #lesson = models.ManyToManyField(Lesson, on_delete=models.CASCADE, through='Course') # Foreign key to lesson # ???
    def is_get_score(self, selected_ids):
        #print(selected_ids)
        #for selected in self.choice_set.filter(is_correct=True):
            #print(selected)
        all_answers = self.choice_set.filter(is_correct=True).count()
        selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
        selected_not_correct =self.choice_set.filter(is_correct=False, id__in=selected_ids).count()
        if all_answers == selected_correct and selected_not_correct == 0:
            return True
        else:
            return False      
    
class Choice(models.Model):
    ''' Used to persist choice content for a question '''
    id=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    text = models.CharField(max_length=200) # Choice content
    is_correct = models.BooleanField(default=False) # Indicate if this choice of the question is a correct one or not
    question= models.ForeignKey(Question, on_delete=models.CASCADE) # One-To-Many (or Many-To-Many if you want to reuse choices) relationship with Question
    
class Submission(models.Model): 
    ''' Used to link an enrollment to multiples choices''' 
    id=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    enrollment=models.ForeignKey(Enrollment, on_delete=models.CASCADE) # One enrollment could have multiple submission AND one submission is for one enrollment only
    choices = models.ManyToManyField(Choice) # One submission could have multiple choices AND One choice could belong to multiple submissions
    