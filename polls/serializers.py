from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Admin, Student, Poll, Option, Vote, NFT

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Admin
        fields = ['id', 'user', 'is_admin']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'name', 'email']

class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'start_date', 'end_date']
        read_only_fields = ['created_by']

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'poll', 'option_text']

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'student', 'option', 'timestamp']

class NFTSerializer(serializers.ModelSerializer):

    class Meta:
        model = NFT
        fields = ['id', 'token_address', 'minted_at']
