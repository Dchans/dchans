from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import register_ser,login_ser,user_ser,sub_ser
from django.contrib.auth import authenticate
from home.models import User,subscription
import random
from cryptography.fernet import Fernet
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import FileResponse
import json
import pysqlcipher3.dbapi2 as sq
from django.core.files.storage import default_storage
from io import BytesIO
fernet=Fernet(User.generate_fernetkey("d"))
def get_token(user):
    referesh=RefreshToken.for_user(user)
    return {
        'referesh':str(referesh),
        'access':str(referesh.access_token)
    }
class user_register(APIView):
    def post(self,request,format=None):
        ser=register_ser(data={"name":request.data.get("name"),"password":request.data.get("password")})
        if ser.is_valid():
            ser=ser.save()
            key= User.generate_fernetkey(request.data.get("password")).encode()
            return Response({'created':True,"db_password":Fernet(key).decrypt(ser.db_password).decode(),"db_key":fernet.encrypt(key),"token":get_token(ser)},status=status.HTTP_201_CREATED)
        return Response({"error":ser.errors})
       
class user_login(APIView):
    def post(self,request,format=None):
        ser=login_ser(data=request.data)
        if ser.is_valid(raise_exception=True):
            name=ser.data.get("name")
            password=ser.data.get("password")
            user=authenticate(name=name,password=password)
            if user is not None:
                sub=subscription.objects.get(user=user,app_type=0)
                if not sub.active:
                    if (sub.date_created.date()-timezone.now().date()).days>30:
                        return Response({'Trial_over':True})
                key= User.generate_fernetkey(password).encode()
                return Response({'login':True,"db_password":Fernet(key).decrypt(user.db_password).decode(),"db_key":fernet.encrypt(key),"token":get_token(user)},status=status.HTTP_201_CREATED)
        return Response({'login':False},status=status.HTTP_400_BAD_REQUEST)
class user_info(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user=user_ser(request.user)
        sub=subscription.objects.get(user=request.user,app_type=0)
        if not sub.active:
            days=30-(sub.date_created.date()-timezone.now().date()).days
        else:
            days=None
        return Response({'user_data':user.data,'extra':sub_ser(sub).data,'days':days})
    def post(request):
        ser=user_ser(request.user,data=request.data)
        if ser.is_valid():
            ser.save()
            return Response({"updated":True})
        return Response({"updated":False})
class download_database(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        data=json.loads(request.body)
        if data.get("key"):
            conn=sq.connect('main.db')
            cursor=conn.cursor()
            cursor.execute('PRAGMA key="d"')
            cursor.execute('PRAGMA rekey = "{}"'.format(Fernet(fernet.decrypt(data.get("key"))).decrypt(request.user.db_password).decode()))
            conn.commit()
            conn.close()
            f=open("temp.db",'wb')
            f.write(open("main.db","rb").read())
            f.close()
            response =FileResponse(open("temp.db",'rb'))
            response['Content-Disposition'] = 'attachment; filename="main.db"' 
            conn=sq.connect('main.db')
            cursor=conn.cursor()
            cursor.execute('PRAGMA key = "{}"'.format(Fernet(fernet.decrypt(data.get("key"))).decrypt(request.user.db_password).decode()))
            cursor.execute('PRAGMA rekey="d"')
            conn.commit()
            conn.close()
            return response 
           
        return Response({'failed':True})                   
class backup_data(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,format=None):
        data=json.loads(request.body)
        if data.get('key'):
            if data.get("upload"):
                db_fernet=Fernet(fernet.decrypt(data.get("key")))
                dates=json.loads(db_fernet.decrypt(default_storage.open(f"{request.user.id}\\config.bs",'r').read()).decode())
                current_date=str(timezone.now().date())
                if current_date in dates:
                    old_data=json.loads(db_fernet.decrypt(default_storage.open(f"{request.user.id}\\{current_date}.bs").read()))
                    old_data.extend(data["backupdata"])
                    default_storage.save(f"{request.user.id}\\{current_date}.bs",BytesIO(db_fernet.encrypt(json.dumps(old_data).encode())))
                else:
                    default_storage.save(f"{request.user.id}\\{current_date}.bs",BytesIO(db_fernet.encrypt(json.dumps(data["backupdata"]).encode())))
                    dates.append(current_date)
                    default_storage.save(f"{request.user.id}\\config.bs",BytesIO(db_fernet.encrypt(json.dumps(dates).encode())))
                return Response({'backup':True})
        return Response({'backup':False})
    
    

"""class generate_otp(APIView):
    def post(self,request):
        try:
            User.objects.get(phone=request.data.get("phone"))
            return Response({'Exist':True})
        except:
            request.session['otp']=self.generate_otp(request.data.get("phone"))
            print(request.session['otp'])
            return Response({'Generated':True})
    def generate_otp(self,phonenumber):
        otp=random.randint(1000,10000)
        print(otp)
        return str(otp)

class otp_verify(APIView):
        def post(self,request):
            if request.session.get("otp") and request.session.get("phone"):
                if request.data.get("otp")==request.session.get("otp"):
                        ser=register_ser(data={"name":request.session.get("name"),"password":request.session.get("password"),"phone":request.session.get("phone")})
                        del request.session["name"]
                        del request.session["otp"]
                        del request.session["phone"]
                        del request.session["password"]
                        if ser.is_valid(raise_exception=True):
                            ser.save()
                            request.session["db"]=True
                            return Response({'created':True,'token':get_token(ser.user)},status=status.HTTP_201_CREATED)
                        
                        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)
                return Response({'otp':False},status=status.HTTP_400_BAD_REQUEST)
            return Response({'otp':False},status=status.HTTP_400_BAD_REQUEST)"""
