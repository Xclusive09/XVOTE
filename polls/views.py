from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Admin, Student, Poll, Option, Vote, NFT
from .serializers import AdminSerializer, StudentSerializer, PollSerializer, OptionSerializer, VoteSerializer, NFTSerializer
from django.contrib.auth import authenticate

# Create your views here.

# Admin Authentication and Management

class AdminLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user:
            print(f"Authenticated user: {user.username}")
            try:
                admin = Admin.objects.get(user=user)
                print(f"Admin found: {admin.user.username}")
                return Response({"message": "Admin Authenticated"}, status=status.HTTP_200_OK)
            except Admin.DoesNotExist:
                return Response({"error": "Admin account not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Poll Creation, Management, and Retrieval

class PollCreateView(generics.CreateAPIView):
    serializer_class = PollSerializer
    permissions_classes = [permissions.IsAdminUser]


    def perform_create(self, serializer):
        admin = Admin.objects.get(user=self.request.user)
        serializer.save(created_by=admin)


class PollListView(generics.ListAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

class PollDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser]

# Student Authentication using the NFT

class StudentLoginView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        try:
            student = Student.objects.get(student_id=student_id)
            return Response({"message" : "Student Authenticated"}, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({"error" : "Invalid Student ID"}, status=status.HTTP_401_UNAUTHORIZED)

# Voting Functionality

class VoteCreateView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        option_id = request.data.get('option_id')
        try:
            student = Student.objects.get(student_id=student_id)
            option = Option.objects.get(id=option_id)
            vote = Vote.objects.create(student=student, option=option)
            # Here, you would mint an NFT on the Solana blockchain for the vote
            # nft = mint_nft_on_solana(vote)
            return Response({"message": "Vote recorded", "vote_id": vote.id}, status=status.HTTP_201_CREATED)
        except (Student.DoesNotExist, Option.DoesNotExist):
            return Response({"error": "Invalid Student ID or Option ID"}, status=status.HTTP_400_BAD_REQUEST)

# Real-time Vote Count Display
class PollResultsView(APIView):
    def get(self, request, poll_id):
        try:
            poll = Poll.objects.get(id=poll_id)
            options = poll.options.all()
            results = {option.option_text: option.vote_set.count() for option in options}
            return Response({"poll": poll.title, "results": results}, status=status.HTTP_200_OK)
        except Poll.DoesNotExist:
            return Response({"error": "Poll not found"}, status=status.HTTP_404_NOT_FOUND)