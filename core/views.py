from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from io import StringIO
import pandas as pd
from io import StringIO
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from core.utils import get_chart_path
import os
import uuid
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User



def register(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        pass_word = request.POST.get('password')
        confirm_password = request.POST.get('con_password')

        if pass_word == confirm_password:
            if User.objects.filter(username=user_name).exists():
                messages.warning(request, "Username already taken")
            else:
                user = User.objects.create_user(username=user_name, password=pass_word)
                user.save()
                messages.success(request, "Registration successful! You can now log in.")
                return redirect('login')
        else:
            messages.warning(request, "Confirm Password does not match Password")

    return render(request, 'register.html')
def login(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        pass_word = request.POST.get('password')
        user = authenticate(request, username=user_name, password=pass_word)
        if user is not None:
            auth_login(request, user)  
            return redirect('upload')
        else:
            messages.warning(request, "Invalid Credential")
            
    return render(request, 'login.html')



 
def upload_csv(request):
    request.session.flush()  
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        try:
            df = pd.read_csv(csv_file)
            request.session.flush()  
            request.session['csv_data'] = df.to_json() 
            request.session.modified = True
            messages.success(request, "CSV uploaded and stored successfully.")
            return redirect('preview')
        except Exception as e:
            messages.error(request, f"Error reading CSV: {e}")
            return render(request, 'upload.html')
    else:
        messages.warning(request, "No file selected.")
        return render(request, 'upload.html')


def preview_csv(request):
    if 'csv_data' not in request.session:
        messages.error(request,"Upload file to access")
        return redirect('upload')
    json_data = request.session.get('csv_data')
    if not json_data:
        return render(request, 'preview.html', {'error': 'No data in session. Please upload again.'})

    try:
        df = pd.read_json(StringIO(json_data))  
        table_html = df.head(20).to_html(classes='preview-table', index=False)
        return render(request, 'preview.html', {'table': table_html})
    except Exception as e:
        # request.session.flush()
        return render(request, 'preview.html', {'error': str(e)})


def data_stats(request):
    if 'csv_data' not in request.session:
        return redirect('upload')
    json_data = request.session.get('csv_data')
    if not json_data:
        return render(request, 'upload.html', {'error': 'No data in session. Please upload again.'})
    try:
        df = pd.read_json(StringIO(json_data)) 
        stats={
            'shape':df.shape,
            'columns': df.columns.tolist(),
            'data': df.dtypes.astype(str).to_dict(),
            'missing': df.isnull().sum().to_dict(),
            'total_missing':df.isnull().sum().sum(),
            'describe': df.describe(include='all').to_html(classes="stats-table", border=0)
        }
        return render(request, 'stats.html', {'stats': stats})
    except Exception as e:
        # request.session.flush()
        return render(request, 'stats.html', {'error': str(e)})


def data_visualizer(request):
    prev_chart_url = request.session.get('chart_url')
    if prev_chart_url:
        old_chart_path = os.path.join(settings.BASE_DIR, 'core', 'static', prev_chart_url)
        if os.path.exists(old_chart_path):
            os.remove(old_chart_path)
    if 'csv_data' not in request.session:
        return redirect('upload')
    json_data = request.session.get('csv_data')
    if not json_data:
        return redirect('upload')

    df = pd.read_json(StringIO(json_data))
    chart_path = None   
    chart_url = None
    if request.method == 'POST':
        x_col = request.POST.get('x_column')
        y_col = request.POST.get('y_column')
        chart_type = request.POST.get('chart_type')
        chart_path, chart_url = get_chart_path()
        plt.figure(figsize=(8, 5))
        try:
            if chart_type == 'line':
                sns.lineplot(data=df, x=x_col, y=y_col)
            elif chart_type == 'bar':
                sns.barplot(data=df, x=x_col, y=y_col)
            elif chart_type == 'scatter':
                sns.scatterplot(data=df, x=x_col, y=y_col)
            elif chart_type == 'hist':
                sns.histplot(data=df[x_col], bins=20, kde=True)
            elif chart_type == 'box':
                sns.boxplot(data=df, x=x_col, y=y_col)

            plt.xlabel(x_col)
            plt.ylabel(y_col)
            plt.title(f"{chart_type.title()} Chart")
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()
            request.session['chart_url'] = chart_url

            return render(request, 'visualizer.html', {'chart_path': chart_url})
            
        except Exception as e:
            return render(request,'visualizer.html', {
                'columns': df.columns,
                'error': str(e)
            })

    return render(request,'visualizer.html', {
        'columns': df.columns,
        'chart_path': chart_url,
    })
    # clean data~~

 
def clean_data(request):
    if 'csv_data' not in request.session:
        return redirect('upload')
    json_data = request.session.get('csv_data')
    if not json_data:
        return render(request, 'upload.html', {'error': 'No data in session. Please upload again.'})
    if json_data:
        df = pd.read_json(StringIO(json_data)) 
        Missed={
            'shape':df.shape,
            'missing': df.isnull().sum().to_dict(),
            'total_missing':df.isnull().sum().sum(),
        }
        if request.method == 'POST':
            if request.POST.get('remove_nulls'):
                df=df.dropna()
                
            if request.POST.get('remove_duplicates'):
                df=df.drop_duplicates()
                
            fill_mis=request.POST.get('fillna_value')
            if fill_mis:
                df=df.fillna(fill_mis)
                
            drop_col=request.POST.get('drop_columns')
            if drop_col:
                cols=[col for col in drop_col.split(',')]
                df = df.drop(columns=[col for col in cols if col in df.columns], errors='ignore')
            
            rename_col=request.POST.get('rename_columns')
            if rename_col:
                rename_dict={}
                try:
                    pairs=[pair.strip() for pair in rename_col.split(',')]
                    for pair in pairs:
                        old,new=pair.split(':')
                        rename_dict[old.strip()]=new.strip()
                        df=df.rename(columns=rename_dict)
                except ValueError:
                    messages.warning(request,"invalid rename format used,use old:new")
        request.session['csv_data'] = df.to_json()
        table_html = df.head(20).to_html(classes='table', index=False)

        return render(request, 'clean.html', {'Missed': Missed,'cleaned_table':table_html})
    return render(request, 'clean.html',{'Missed':Missed})    

 
def export_data(request):
    json_data = request.session.get('csv_data')
    if not json_data:
        return HttpResponse("No data to export", status=400)
    df = pd.read_json(StringIO(json_data))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cleaned_data.csv"'
    df.to_csv(path_or_buf=response, index=False)
    return response
