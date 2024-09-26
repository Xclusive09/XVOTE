from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from .models import Admin, Student, Poll, Option, Vote, NFT
from .serializers import AdminSerializer, StudentSerializer, PollSerializer, OptionSerializer, VoteSerializer, NFTSerializer
# from .utils.SolanaUtils import check_nft_in_wallet
from django.views import View


def dashboard(request):
    return render(request, 'polls/dashboard.html')


def election_management(request):
    return render(request, 'polls/election-management.html')


def voter_management(request):
    return render(request, 'polls/voter-management.html')


def results_audit(request):
    return render(request, 'polls/results-audits.html')


def user_management(request):
    return render(request, 'polls/user-management.html')


def notifications(request):
    return render(request, 'polls/notifications.html')


def settings(request):
    return render(request, 'polls/settings.html')


def help_and_support(request):
    return render(request, 'polls/help-and-support.html')

# Admin Authentication and Management


class AdminLoginView(APIView):
    queryset = Admin.objects.all()

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            try:
                admin = Admin.objects.get(user=user)
                return Response({"message": "Admin Authenticated"}, status=status.HTTP_200_OK)
            except Admin.DoesNotExist:
                return Response({"error": "Admin account not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Poll Creation, Management, and Retrieval



class PollCreateView(generics.CreateAPIView):
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        # Check if the user is authenticated
        if not self.request.user.is_authenticated:
            raise PermissionDenied("User is not authenticated")

        # Try to get the admin instance
        try:
            admin = Admin.objects.get(user=self.request.user)
        except Admin.DoesNotExist:
            raise PermissionDenied("You do not have permission to create a poll.")

        # Save the poll with the admin instance
        serializer.save(created_by=admin)

class PollListView(generics.ListAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer


class PollDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser]


class PollUpdateView(generics.UpdateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser]


class PollDeleteView(generics.DestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAdminUser]

# Student Authentication using the NFT


class StudentLoginView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        if not student_id:
            return Response({"error": "Student ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = Student.objects.get(student_id=student_id)
            return Response({"message": "Student Authenticated"}, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({"error": "Invalid Student ID"}, status=status.HTTP_401_UNAUTHORIZED)

# Voting Functionality


class VoteCreateView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        option_id = request.data.get('option_id')

        if not student_id or not option_id:
            return Response({"error": "Student ID and Option ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(student_id=student_id)
            option = Option.objects.get(id=option_id)

            # NFT Verification
            token_mint = "your_nft_mint_address_here"  # Replace with actual address
            if check_nft_in_wallet(student.wallet_address, token_mint):
                vote = Vote.objects.create(student=student, option=option)
                return Response({"message": "Vote recorded", "vote_id": vote.id}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "NFT not found in wallet"}, status=status.HTTP_403_FORBIDDEN)

        except (Student.DoesNotExist, Option.DoesNotExist):
            return Response({"error": "Invalid Student ID or Option ID"}, status=status.HTTP_400_BAD_REQUEST)

# Real-time Vote Count Display


class PollResultsView(APIView):
    def get(self, request, poll_id):
        try:
            poll = Poll.objects.get(id=poll_id)
            options = poll.options.all()
            results = {option.text: option.vote_set.count()
                       for option in options}
            return Response({"poll": poll.title, "results": results}, status=status.HTTP_200_OK)
        except Poll.DoesNotExist:
            return Response({"error": "Poll not found"}, status=status.HTTP_404_NOT_FOUND)

# NFT Verification


class NFTVerifyView(APIView):
    def post(self, request):
        student_id = request.data.get('student_id')
        nft_address = request.data.get('nft_address')

        if not student_id or not nft_address:
            return Response({"error": "Student ID and NFT address are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(student_id=student_id)

            token_mint = "your_nft_mint_address_here"  # Replace with actual address
            if check_nft_in_wallet(student.wallet_address, token_mint):
                return Response({"message": "NFT verified"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "NFT not found in wallet"}, status=status.HTTP_403_FORBIDDEN)

        except Student.DoesNotExist:
            return Response({"error": "Invalid Student ID"}, status=status.HTTP_401_UNAUTHORIZED)

# Vote List (Admin use case)


class VoteListView(generics.ListAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAdminUser]
