from django.contrib import admin
from .models import Admin, Student, Poll, Option, Vote, NFT

@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_admin')
    search_fields = ('user__username', 'user__email')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'email', 'wallet_address')
    search_fields = ('student_id', 'name', 'email')

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'created_by')
    list_filter = ('start_date', 'end_date')
    search_fields = ('title', 'description')

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('poll', 'option_text')
    search_fields = ('option_text',)

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('student', 'option', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('student__name', 'option__option_text')

@admin.register(NFT)
class NFTAdmin(admin.ModelAdmin):
    list_display = ('vote', 'token_address', 'minted_at')
    search_fields = ('token_address',)
