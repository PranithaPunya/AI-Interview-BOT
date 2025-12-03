from django.urls import path
from .views import (
    JobListCreateView, CandidateListCreateView, ApplyJobView,
    ResumeUploadView, InterviewSessionCreateView,
    GeneratedQuestionListView, SubmitAnswerView,
    FetchPendingTasksView, UpdateTaskStatusView
)

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
]
