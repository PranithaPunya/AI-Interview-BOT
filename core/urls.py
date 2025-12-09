from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobListCreateView, CandidateListCreateView, ApplyJobView,
    ResumeUploadView, InterviewSessionCreateView,
    GeneratedQuestionListView, SubmitAnswerView,
    FetchPendingTasksView, UpdateTaskStatusView,
    CandidateSignupView, AdminCreateUserView, LoginView,
    PasswordResetAPIView, PasswordResetConfirmAPIView,JobViewSet, QuestionBankViewSet, CandidateViewSet, ResumeViewSet
)
router = DefaultRouter()
router.register(r"admin/jobs", JobViewSet, basename="admin-jobs")
router.register(r"admin/questions", QuestionBankViewSet, basename="admin-questions")
router.register(r"admin/candidates", CandidateViewSet, basename="admin-candidates")
router.register(r"admin/resumes", ResumeViewSet, basename="admin-resumes")

urlpatterns = [

    # Job
    path("jobs/", JobListCreateView.as_view()),

    # Candidate
    path("candidates/", CandidateListCreateView.as_view()),

    # Apply job
    path("apply/", ApplyJobView.as_view()),

    # Resume upload
    path("upload_resume/", ResumeUploadView.as_view()),

    # Interview session
    path("interview/create/", InterviewSessionCreateView.as_view()),

    # Get session questions
    path("interview/<int:session_id>/questions/", GeneratedQuestionListView.as_view()),

    # Submit answer
    path("answer/submit/", SubmitAnswerView.as_view()),

    # Worker queue
    path("tasks/pending/", FetchPendingTasksView.as_view()),
    path("tasks/<int:pk>/update/", UpdateTaskStatusView.as_view()),
    # Authentication
    path("auth/signup/", CandidateSignupView.as_view(), name="signup"),
    path("auth/admin-create-user/", AdminCreateUserView.as_view(), name="admin-create-user"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/password-reset/", PasswordResetAPIView.as_view(), name="password_reset"),
    path("auth/password-reset-confirm/<uidb64>/<token>/", PasswordResetConfirmAPIView.as_view(), name="password_reset_confirm"),
    path("", include(router.urls)),

]
