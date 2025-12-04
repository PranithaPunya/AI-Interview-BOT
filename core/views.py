from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    CandidateSignupSerializer, AdminCreateUserSerializer,
    UserSerializer, LoginSerializer
)
from .permissions import IsAdmin

User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}

class CandidateSignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CandidateSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({"user": UserSerializer(user).data, "tokens": tokens}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminCreateUserView(APIView):
    """
    Admin creates a recruiter/admin user; the created user gets an unusable password and a password-reset email is sent.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = AdminCreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # create unusable password and send reset link
            user.set_unusable_password()
            user.save()

            # send password reset email programmatically
            form = PasswordResetForm({"email": user.email})
            if form.is_valid():
                # supply request to build absolute URL inside email
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    email_template_name="registration/password_reset_email.html",
                    subject_template_name="registration/password_reset_subject.txt",
                    from_email=None,
                )
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = get_tokens_for_user(user)
        return Response({"user": UserSerializer(user).data, "tokens": tokens})

# Password reset (send reset email)
class PasswordResetAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get("email")
        form = PasswordResetForm({"email": email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure(),
                email_template_name="registration/password_reset_email.html",
                subject_template_name="registration/password_reset_subject.txt",
                from_email=None,
            )
            return Response({"detail": "Password reset email sent."})
        return Response({"detail": "Invalid email."}, status=status.HTTP_400_BAD_REQUEST)

# Confirm password reset via uid and token - set new password
class PasswordResetConfirmAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request, uidb64, token):
        new_password = request.data.get("new_password")
        new_password2 = request.data.get("new_password2")
        if new_password != new_password2:
            return Response({"detail": "Passwords do not match."}, status=400)
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail": "Invalid uid."}, status=400)
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid token."}, status=400)
        # use Django's SetPasswordForm validation
        form = SetPasswordForm(user, {'new_password1': new_password, 'new_password2': new_password2})
        if form.is_valid():
            form.save()
            return Response({"detail": "Password has been reset."})
        return Response(form.errors, status=400)



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
