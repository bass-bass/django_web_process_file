from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from app.forms import UploadForm
from app.functions import process_file,to_csv
import csv,io
import pandas as pd

# Create your views here.
def index(request):
    if request.method == 'POST':
        upload = UploadForm(request.POST, request.FILES)

        if upload.is_valid():
            
            df = pd.read_csv(io.StringIO(request.FILES['testfile'].read().decode('utf-8')), delimiter=',')
            df = process_file(df)
            response = to_csv(df)
            

            return response

    else:
        upload = UploadForm()

        return render(request, "index.html", {'form':upload})