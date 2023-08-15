from rest_framework import serializers
from home.models import User,subscription
class register_ser(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['name','password']
        extra_kwargs={
            'password':{'write_only':True}
        }
    def create(self,validate_data):
        return User.objects.create_user(**validate_data)

class login_ser(serializers.ModelSerializer):
    name=serializers.CharField(max_length=200)
    class Meta:
        model=User
        fields=['name','password']
class user_ser(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['email','phone','profile_pic','storage_size']
class sub_ser(serializers.ModelSerializer):
    class Meta:
        model=subscription
        fields=['shop_name','address']
    
