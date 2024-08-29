from django.urls import path
from .views import AdminLoginView, PollCreateView, PollListView, PollDetailView, StudentLoginView, VoteCreateView, PollResultsView, PollUpdateView, PollDeleteView, VoteListView, NFTVerifyView

urlpatterns = [
    # Admin authentication endpoint
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),

    # Poll management endpoints
    path('polls/create/', PollCreateView.as_view(), name='poll-create'),         
    path('polls/', PollListView.as_view(), name='poll-list'),                  
    path('polls/<int:pk>/', PollDetailView.as_view(), name='poll-detail'),      
    path('polls/<int:pk>/update/', PollUpdateView.as_view(), name='poll-update'), 
    path('polls/<int:pk>/delete/', PollDeleteView.as_view(), name='poll-delete'), 

    # Student authentication endpoint
    path('student/login/', StudentLoginView.as_view(), name='student-login'),    

    # Voting endpoints
    path('vote/', VoteCreateView.as_view(), name='vote-create'),                 
    path('votes/', VoteListView.as_view(), name='vote-list'),                    

    # NFT verification endpoint
    path('nft/verify/', NFTVerifyView.as_view(), name='nft-verify'),              

    # Poll results endpoint
    path('polls/<int:poll_id>/results/', PollResultsView.as_view(), name='poll-results'),
]
