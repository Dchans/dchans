from django.shortcuts import render
from django.core.files.storage import default_storage
from django.http import FileResponse
def home_page(request):
    return render(request,"home.html")
def busyness_page(request):
    if request.method=="POST":
        FileResponse(default_storage.open('busyness.exe'), as_attachment=True)
        return
    return render(request,"busyness.html")
# Create your views here.
