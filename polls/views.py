from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from .models import Admin, Student, Poll, Option, Vote, NFT
from .serializers import AdminSerializer, StudentSerializer, PollSerializer, OptionSerializer, VoteSerializer, NFTSerializer
from django.views import View
from django.views.decorators.http import require_POST
import requests
import json
from django.conf import settings
from django.urls import reverse


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


def settings_view(request):
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
        poll = serializer.save(created_by=admin)

        # Generate the poll voting link
        poll_link = self.request.build_absolute_uri(
            reverse('submit-vote', kwargs={'poll_id': poll.id})
        )
        
        # Generate the NFT minting link
        nft_link = self.request.build_absolute_uri(
            reverse('mint-nft', kwargs={'nft_id': poll.id})

        )

        # Log the links for monitoring
        print(f'Poll vote URL: {poll_link}')
        print(f'NFT minting URL: {nft_link}')

        # Optionally, save these links to the database or return them in the response
        # Poll.objects.filter(id=poll.id).update(voting_link=poll_link, nft_link=nft_link)

        # Return the poll and voting link in the response
        return Response(
            {
                "message": "Poll created successfully",
                "poll_link": poll_link,
                "nft_link": nft_link
            },
            status=status.HTTP_201_CREATED
        )


# View for rendering the voting page for the poll
class PollVoteView(APIView):
    queryset = Poll.objects.all()  # Set queryset here

    def get(self, request, poll_id):
        # Fetch the poll by its ID
        poll = get_object_or_404(Poll, id=poll_id)

        # Fetch poll options (candidates)
        options = poll.options.all()

        return render(request, 'polls/voters.html', {'poll': poll, 'options': options})


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
            results = {option.text: option.vote_set.count() for option in options}
            return Response({"poll": poll.title, "results": results}, status=status.HTTP_200_OK)
        except Poll.DoesNotExist:
            return Response({"error": "Poll not found"}, status=status.HTTP_404_NOT_FOUND)


# NFT Verification
class NFTVerifyMintView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view

    def get(self, request, nft_id):
        """
        Renders the HTML page for minting an NFT.
        """
        nft = get_object_or_404(NFT, pk=nft_id)

        context = {
            'nft': nft,
        }

        return render(request, 'mint_nft.html', context)

    def post(self, request):
        """
        Verifies if the student has the NFT in their wallet.
        """
        student_id = request.data.get('student_id')
        nft_address = request.data.get('nft_address')

        if not student_id or not nft_address:
            return Response({"error": "Student ID and NFT address are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(student_id=student_id)
            nft = NFT.objects.get(token_address=nft_address)  # Get NFT from the token address

            # Call your custom function to verify NFT ownership
            if check_nft_in_wallet(student.wallet_address, nft.token_address):
                return Response({"message": "NFT verified"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "NFT not found in wallet"}, status=status.HTTP_403_FORBIDDEN)

        except Student.DoesNotExist:
            return Response({"error": "Invalid Student ID"}, status=status.HTTP_401_UNAUTHORIZED)
        except NFT.DoesNotExist:
            return Response({"error": "NFT not found"}, status=status.HTTP_404_NOT_FOUND)


# Vote List (Admin use case)
class VoteListView(generics.ListAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAdminUser]


def mint_nft(request, nft_id):
    nft = get_object_or_404(NFT, pk=nft_id)

    # Check if the NFT has already been minted
    if nft.token_address:
        return HttpResponse("NFT already minted!")

    poll = nft.vote
    project_id = poll.id

    # Prepare the data for the API request
    data = {
        "name": f"NFT for Vote {nft.vote.id}",
        "symbol": "VOTE_NFT",
        "metadata": {
            "description": "NFT for voting",
            "image": "image_url",  # Replace with the actual image URL
        },
        "recipient": nft.recipient,
    }

    # Make the API request to mint the NFT
    response = requests.post(
        f"{settings.UNDERDOG_API_URL}/nft/mint",
        headers={"Authorization": f"Bearer {settings.UNDERDOG_API_TOKEN}"},
        json=data,
    )

    if response.status_code == 200:
        # Update the NFT record with the token address
        nft.token_address = response.json().get("token_address")
        nft.save()
        return JsonResponse({"message": "NFT minted successfully", "nft_address": nft.token_address}, status=201)
    else:
        return JsonResponse({"error": "Failed to mint NFT"}, status=response.status_code)
