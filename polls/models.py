from django.db import models
from django.contrib.auth.models import User

# Model for Admin (inherits from User)
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

# Model for Student
class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    wallet_address = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Model for Poll
class Poll(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_by = models.ForeignKey(Admin, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

# Model for Option (choices in a poll)
class Option(models.Model):
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=100)

    def __str__(self):
        return self.option_text

# Model for Vote (links Student to a chosen Option)
class Vote(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student.name} voted for {self.option.option_text}'

# Model for NFT (to represent a vote on Solana blockchain)
class NFT(models.Model):
    vote = models.OneToOneField(Vote, on_delete=models.CASCADE)
    token_address = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='nft_images/')  # New field for the NFT image
    minting_link = models.URLField(blank=True, null=True)  # Add this field for the minting link

    minted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'NFT for {self.vote}'
