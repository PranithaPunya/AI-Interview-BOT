from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "role", "is_active")



from .models import (
    Job, Candidate, CandidateJobMapping, Resume,
    InterviewSession, GeneratedQuestion, CandidateAnswer,
    AudioProcessingTask
)


# 1. Job Serializer
class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"


# 2. Candidate Serializer
class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = "__all__"


# 3. Candidate-Job Mapping
class CandidateJobMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateJobMapping
        fields = "__all__"


# 4. Resume Serializer
class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = "__all__"
        extra_kwargs = {"resume_file": {"read_only": True}}


# 5. Interview Session
class InterviewSessionSerializer (serializers.ModelSerializer):
    class Meta:
        model = InterviewSession
        fields = "__all__"


# 6. Generated Question
class GeneratedQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedQuestion
        fields = "__all__"


# 7. Candidate Answer
class CandidateAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateAnswer
        fields = "__all__"
        extra_kwargs = {
            "audio_file": {"required": False},
            "transcript": {"read_only": True},
            "score": {"read_only": True},
        }


# 8. Audio Processing Queue Task
class AudioProcessingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioProcessingTask
        fields = "__all__"

# Candidate signup (public)
class CandidateSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "confirm_password", "username")  # username optional

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Password and confirm password do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.role = User.ROLE_CANDIDATE
        user.set_password(password)
        user.save()
        return user
# Admin-created user (Recruiter/Admin) - admin-only endpoint
class AdminCreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "role", "username")

    def validate_role(self, value):
        if value not in [User.ROLE_RECRUITER, User.ROLE_ADMIN]:
            raise serializers.ValidationError("Only admin or recruiter roles allowed here.")
        return value
# Login serializer may be simple (we validate in view), but provide one to type-check
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)