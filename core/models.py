from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


User = settings.AUTH_USER_MODEL  # Custom user model


# ============================================================
# 1. JOB TABLE
# ============================================================
class Job(models.Model):
    job_title = models.CharField(max_length=255)
    job_code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    skills_required = models.JSONField(default=list)
    experience_level = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.job_title


# ============================================================
# 2. CANDIDATE TABLE
# ============================================================
class Candidate(models.Model):
    candidate_user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    experience_years = models.IntegerField()
    
    STATUS_CHOICES = [
        ("new", "New"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
        ("in_interview", "In Interview"),
        ("selected", "Selected"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


# ============================================================
# 3. CANDIDATE-JOB MAPPING
# ============================================================
class CandidateJobMapping(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    
    STATUS_CHOICES = [
        ("applied", "Applied"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="applied")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("candidate", "job")


# ============================================================
# 4. RESUME TABLE
# ============================================================
class Resume(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to="resumes/")
    parsed_text = models.TextField(blank=True, null=True)
    parsed_skills = models.JSONField(default=list)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume of {self.candidate.full_name}"


# ============================================================
# 5. INTERVIEW SESSION
# ============================================================
class InterviewSession(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    
    STATUS_CHOICES = [
        ("created", "Created"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    session_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created")
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    total_score = models.FloatField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Interview Session: {self.id} - {self.candidate.full_name}"


# ============================================================
# 6. QUESTION BANK (Static Questions)
# ============================================================
class QuestionBank(models.Model):
    TECH = "technical"
    BEHAVIORAL = "behavioral"
    CATEGORY_CHOICES = [
        (TECH, "Technical"),
        (BEHAVIORAL, "Behavioral"),
    ]

    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    question_text = models.TextField()
    difficulty_level = models.IntegerField(default=1)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.question_text


# ============================================================
# 7. GENERATED AI QUESTIONS
# ============================================================
class GeneratedQuestion(models.Model):
    interview_session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE)
    question_text = models.TextField()
    expected_answer = models.TextField(blank=True, null=True)
    weightage = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Generated Question for Session {self.interview_session.id}"


# ============================================================
# 8. CANDIDATE ANSWERS
# ============================================================
class CandidateAnswer(models.Model):
    interview_session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE)
    question = models.ForeignKey(GeneratedQuestion, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to="answers/audio/", null=True, blank=True)
    transcript = models.TextField(blank=True, null=True)
    ai_feedback = models.TextField(blank=True, null=True)
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


# ============================================================
# 9. AUDIO PROCESSING QUEUE
# (Internal queue instead of Redis/RabbitMQ)
# ============================================================
class AudioProcessingTask(models.Model):
    interview_session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE)
    question = models.ForeignKey(GeneratedQuestion, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to="processing/audio/")
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("done", "Done"),
        ("failed", "Failed"),
    ]
    task_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# ============================================================
# 10. ERROR LOGS
# ============================================================
class ErrorLog(models.Model):
    event_type = models.CharField(max_length=255)
    detail = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# ============================================================
# 11. ACTIVITY LOGS
# ============================================================
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


# ============================================================
# 12. APP SETTINGS
# ============================================================
class AppSettings(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.JSONField(default=dict)

    def __str__(self):
        return self.key

# ============================================================
# 13. EMPLOYEE TABLE
# ============================================================
class Employee(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)
    employee_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    # Optional fields for better admin visibility
    department = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee_name} ({self.employee_id})"

class CustomUser(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_RECRUITER = "recruiter"
    ROLE_CANDIDATE = "candidate"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_RECRUITER, "Recruiter"),
        (ROLE_CANDIDATE, "Candidate"),
    ]

    username = models.CharField(max_length=150, blank=True, null=True)  # optional
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CANDIDATE)

    # keep the rest of AbstractUser fields: password, is_staff, is_superuser, is_active, etc.

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # email + password only

    def __str__(self):
        return f"{self.email} ({self.role})"