from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.core.exceptions import PermissionDenied
from .models import Admin, Student, Poll, Option, Vote, NFT
from .serializers import AdminSerializer, StudentSerializer, PollSerializer, OptionSerializer, VoteSerializer, NFTSerializer
# from .utils.SolanaUtils import check_nft_in_wallet
from django.views import View
from django.views.decorators.http import require_POST
import requests
import json
from django.conf import settings



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




class NFTVerifyMintView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access this view

    def get(self, request, election_id, nft_id):
        """
        Renders the HTML page for minting an NFT.
        """
        election = get_object_or_404(Election, pk=election_id)
        nft = get_object_or_404(NFT, pk=nft_id)

        context = {
            'election': election,
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


UNDERDOG_API_KEY = settings.UNDERDOG_API_KEY
UNDERDOG_API_URL = "https://api.underdogprotocol.com/v1/nfts"

def mint_nft(request, nft_id):
    nft = get_object_or_404(NFT, pk=nft_id)

    if nft.token_address:
        return HttpResponse("NFT already minted!")

    # Prepare the data for the API request
    data = {
        "name": f"NFT for Vote {nft.vote.id}",
        "symbol": "VOTE_NFT",
        "metadata": {
            "image": request.build_absolute_uri(nft.image.url),
        }
    }

    headers = {
        "Authorization": f"Bearer {UNDERDOG_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Send a request to the Underdog API to mint the NFT
        response = requests.post(UNDERDOG_API_URL, headers=headers, data=json.dumps(data))
        response_data = response.json()

        if response.status_code == 200:
            nft.token_address = response_data['token_address']
            nft.minting_link = response_data['minting_link']  # Store the minting link
            nft.save()

            # Optionally, display or store the minting link to share with voters
            return HttpResponse(f"NFT minted successfully! Share this link with voters to mint: {nft.minting_link}")
        else:
            return HttpResponse(f"Failed to mint NFT: {response_data}")
    
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

# # View to handle vote submission
# @require_POST
# def submit_vote(request):
#     election_id = request.POST.get('election_id')
#     candidate_id = request.POST.get('candidate_id')

#     if not election_id or not candidate_id:
#         return JsonResponse({'error': 'Election ID and Candidate ID are required.'}, status=400)

#     poll = get_object_or_404(Poll, id=election_id)
#     candidate = get_object_or_404(Option, id=candidate_id)

#     if not request.user.is_authenticated:
#         return JsonResponse({'error': 'You must be logged in to vote.'}, status=401)

#     if Vote.objects.filter(voter=request.user, poll=poll).exists():
#         return JsonResponse({'error': 'You have already voted in this election.'}, status=400)

#     Vote.objects.create(voter=request.user, poll=poll, option=candidate)
#     return JsonResponse({'message': 'Your vote has been submitted successfully.'}, status=201)

# # API to fetch candidates for an election
# def get_candidates(request, election_id):
#     poll = get_object_or_404(Poll, id=election_id)
#     candidates = poll.options.all()

#     if not candidates.exists():
#         return JsonResponse({'error': 'No candidates found for this election.'}, status=404)

#     candidate_data = [{'id': candidate.id, 'option_text': candidate.option_text} for candidate in candidates]
#     return JsonResponse({'candidates': candidate_data}, status=200)
