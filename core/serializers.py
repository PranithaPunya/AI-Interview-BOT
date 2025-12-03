from rest_framework import serializers
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
