from django.urls import path
from .views import (
    AdminLoginView,
    PollCreateView,
    PollListView,
    PollDetailView,
    StudentLoginView,
    VoteCreateView,
    PollResultsView,
    PollUpdateView,
    PollDeleteView,
    VoteListView,
    NFTVerifyView,
    dashboard,
    election_management,
    voter_management,
    results_audit,
    user_management,
    notifications,
    settings,
    help_and_support,
)
from polls import views

urlpatterns = [
    # Admin authentication endpoint
    path("admin/login/", AdminLoginView.as_view(), name="admin-login"),
    # Poll management endpoints
   path('polls/create/', PollCreateView.as_view(), name='election-create'),
    path('polls/', PollListView.as_view(), name='election-list'),
    path("polls/<int:pk>/", PollDetailView.as_view(), name="poll-detail"),
    path("polls/<int:pk>/update/", PollUpdateView.as_view(), name="poll-update"),
    path("polls/<int:pk>/delete/", PollDeleteView.as_view(), name="poll-delete"),
    # Student authentication endpoint
    path("student/login/", StudentLoginView.as_view(), name="student-login"),
    # Voting endpoints
    path("vote/", VoteCreateView.as_view(), name="vote-create"),
    path("votes/", VoteListView.as_view(), name="vote-list"),
    # NFT verification endpoint
    path('admin/mint-nft/<int:nft_id>/', views.mint_nft, name='mint_nft'),
    path("nft/verify/", NFTVerifyView.as_view(), name="nft-verify"),
    # Poll results endpoint
    path(
        "polls/<int:poll_id>/results/", PollResultsView.as_view(), name="poll-results"
    ),
    
    # path('elections/create/', CreateElectionView.as_view(), name='create-election'),
    # path('elections/vote/', SubmitVoteView.as_view(), name='submit-vote'),
    path('mint/<int:nft_id>/<int:election_id>/', views.mint_nft, name='mint_nft'),

    path('elections/nft-verify/', NFTVerifyView.as_view(), name='nft-verify'),
    # Voters Path
#    path('submit_vote/', views.submit_vote, name='submit_vote'),
#     path('election/<int:election_id>/candidates/', views.get_candidates, name='get_candidates'),

    # Dashboard
    path("dashboard", dashboard, name="dashboard"),
    path("elections", election_management, name="elections"),
    path("voters", voter_management, name="voters"),
    path("results-audit", results_audit, name="results-audit"),
    path("user-management", user_management, name="user-management"),
    path("notifications", notifications, name="notifications"),
    path("settings", settings, name="settings"),
    path("help-and-support", help_and_support, name="help-and-support"),
]
