from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


def index(request):
    return HttpResponse('Hello, world. The AI Interview BOT is up.')




from .models import (
    Job, Candidate, CandidateJobMapping, Resume,
    InterviewSession, GeneratedQuestion, CandidateAnswer,
    AudioProcessingTask
)

from .serializers import (
    JobSerializer, CandidateSerializer, CandidateJobMappingSerializer,
    ResumeSerializer, InterviewSessionSerializer,
    GeneratedQuestionSerializer, CandidateAnswerSerializer,
    AudioProcessingTaskSerializer
)

class JobListCreateView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

# ============================================================
# CANDIDATE MANAGEMENT
# ============================================================
class CandidateListCreateView(generics.ListCreateAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]

# ============================================================
# APPLY TO JOB
# ============================================================
class ApplyJobView(generics.CreateAPIView):
    serializer_class = CandidateJobMappingSerializer

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

# ============================================================
# RESUME UPLOAD
# ============================================================
from rest_framework.views import APIView

class ResumeUploadView(APIView):
    def post(self, request):
        candidate_id = request.data.get("candidate_id")
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "File not provided"}, status=400)

        resume = Resume.objects.create(
            candidate_id=candidate_id,
            resume_file=file
        )

        return Response(ResumeSerializer(resume).data)

# ============================================================
# INTERVIEW SESSION
# ============================================================
class InterviewSessionCreateView(generics.CreateAPIView):
    serializer_class = InterviewSessionSerializer

# ============================================================
# GET QUESTIONS FOR SESSION
# ============================================================
class GeneratedQuestionListView(generics.ListAPIView):
    serializer_class = GeneratedQuestionSerializer

    def get_queryset(self):
        session_id = self.kwargs["session_id"]
        return GeneratedQuestion.objects.filter(interview_session=session_id)
    
# ============================================================
# SUBMIT CANDIDATE ANSWER (Audio)
# ============================================================
class SubmitAnswerView(APIView):
    def post(self, request):
        serializer = CandidateAnswerSerializer(data=request.data)
        if serializer.is_valid():
            answer = serializer.save()

            # Add to processing queue
            AudioProcessingTask.objects.create(
                interview_session=answer.interview_session,
                question=answer.question,
                audio_file=answer.audio_file
            )

            return Response({"message": "Answer submitted"}, status=201)
        return Response(serializer.errors, status=400)
# ============================================================
# AI WORKER — FETCH PENDING AUDIO TASKS
# ============================================================
class FetchPendingTasksView(generics.ListAPIView):
    serializer_class = AudioProcessingTaskSerializer

    def get_queryset(self):
        return AudioProcessingTask.objects.filter(task_status="pending")
# ============================================================
# UPDATE AUDIO TASK STATUS
# ============================================================
class UpdateTaskStatusView(generics.UpdateAPIView):
    queryset = AudioProcessingTask.objects.all()
    serializer_class = AudioProcessingTaskSerializer
