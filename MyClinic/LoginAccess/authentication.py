from django.contrib.auth.backends import ModelBackend
from .models import User

class CustomAuthBackend(ModelBackend):
    def authenticate(self,request,mobile_number=None,password=None,**kwargs):
        try:
            if mobile_number:
                user = User.objects.get(mobile_number=mobile_number)
               
            else:
                return None
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        


