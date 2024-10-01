from django.contrib import admin
from .models import Admin, Student, Poll, Option, Vote, NFT
from django.utils.html import format_html
import requests  # For making requests to mint NFT

class NFTAdmin(admin.ModelAdmin):
    list_display = ('vote', 'token_address', 'minted_at', 'view_image', 'mint_nft_button')
    readonly_fields = ('token_address', 'minted_at')
    
    # Form for creating NFTs
    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj:
            return fields + ('token_address',)  # Show token_address after minting
        return fields
    
    # Display the uploaded image in the admin panel
    def view_image(self, obj):
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" width="100px" />')
        return "No Image"
    
    # Custom button to trigger minting NFTs
    def mint_nft_button(self, obj):
        if not obj.token_address:  # Only show the button if NFT isn't minted
            return format_html(f'<a class="button" href="/admin/mint-nft/{obj.id}">Mint NFT</a>')
        return "Already Minted"
    
    mint_nft_button.short_description = "Mint NFT"
    view_image.short_description = "Image"

admin.site.register(NFT, NFTAdmin)


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

# @admin.register(NFT)
# class NFTAdmin(admin.ModelAdmin):
#     list_display = ('vote', 'token_address', 'minted_at')
#     search_fields = ('token_address',)
#     pass