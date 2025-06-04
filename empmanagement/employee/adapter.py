from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class RestrictMicrosoftDomainAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        email = sociallogin.user.email
        return email.endswith('@yourcompany.com') 