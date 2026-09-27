from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
import pandas as pd
import plotly.express as px
from . import calc
from django.urls import reverse_lazy
from django.views import generic
from .forms import Customizedsignupform
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from concurrent.futures import ThreadPoolExecutor
import time

#Signup Page  
class SignUpView(generic.CreateView):
    form_class = Customizedsignupform
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

def logout_view(request):
    logout(request)
    print("well well")
    # user = request.user
    # context = {'user': user,}
    # template = loader.get_template('index.html')
    return render(request, "/accounts/login/")



df=pd.DataFrame()
login_count=0
prev_model_tuples= []
prev_model_name= []
prev_model_scores= []
mode="Classification"

@login_required(login_url="/accounts/login/")
def LandingPage(request):
  user = request.user
  print(request.user)
  if str(user) != "AnonymousUser":
    global login_count
    if login_count==0:
      login_count=1
      messages.success(request, "Login Successful")
  else:
    messages.warning(request, "Some Error")
  if request.method == "POST":
    try:
    # if "myfile" in request.POST:
      print("Try")
      myfile = request.FILES['myfile']
      global df
      df=pd.read_csv(myfile, index_col=0)
      if "Name" in df.columns:
        df= df.drop(["Name"], axis=1)
      calc.load_df(df)
      context = {'user': user,
                "loaded": True,
                "l": list(df.columns),
                "graphs": ["scatter", "bar", "histogram", "line"]}
      
      template = loader.get_template('index.html')
      return HttpResponse(template.render(context, request))
    except:
      print("Except")
      x_name=request.POST.get("opt1")
      y_name= request.POST.get("opt2")
      graph= request.POST.get("graph")
      print(graph)
      if graph=="scatter":
        fig=px.scatter(x=df[x_name], y=df[y_name], labels={ "x": x_name, "y":y_name})
      if graph=="line":
        fig=px.line(x=df[x_name], y=df[y_name], labels={ "x": x_name, "y":y_name})
      if graph=="histogram":
        fig=px.histogram(df,x=x_name)
      if graph=="bar":
        fig=px.bar(x=df[x_name], y=df[y_name], labels={ "x": x_name, "y":y_name})
      context = {'user': user,
                "flag": True,
                "loaded": True,
                "l": list(df.columns),
                "graphs": ["scatter", "bar", "histogram", "line"],
                "graph": graph,
                "x_name": x_name,
                "y_name": y_name}
      fig.write_image(r"member1/static/images/tax.jpeg")
      template = loader.get_template('index.html')
      print("Rendered")
      return HttpResponse(template.render(context, request))

  else:
    context = {'user': user}
    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))
  

def NextPage(request):
  user = request.user
  global mode
  if request.method == "POST":
    target= request.POST.get("target")
    mode= request.POST.get("mode")
    calc.setMode(mode)
    # print(target)
    MV=df.isnull().sum().sum()
    calc.missing_data()
    start = time.time()
    # l= calc.hist()
    # p= calc.pie()
    # b= calc.boxplot()
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_hist = executor.submit(calc.hist)
        future_pie = executor.submit(calc.pie)
        future_box = executor.submit(calc.boxplot)

        l = future_hist.result()
        p = future_pie.result()
        b = future_box.result()
    end = time.time()
    print(f"Total time taken: {end - start:.2f} seconds")
    calc.OHE(target)
    calc.setTarget(target)
    # calc.StandardSc()
    if mode=="Classification":
      models=[ "Logistic Regression", "Random Forset Classifier", "Support Vector Machine", "Decision Tree Classifier", "Naive Bayes", "KNeighborsClassifier"]
    else:
      models=["Linear Regression", "Random Forset Regressor", "Support Vector Regressor", "Decision Tree Regressor", "Naive Bayes", "KNeighborsRegressor"]

    
    # mse=0
    # print(df.corr())
    fig = px.imshow(df.corr(numeric_only=True))
    fig.write_image(r"member1/static/images/corr.jpeg")
    context = {'user': user,
              'flag': True,
              "columns": l,
              "pie": p,
              "box": b,
              "columnsName": df.columns,
              "nrow": df.shape[0],
              "ncol": df.shape[1],
              "MV": MV,
              "DV": df.duplicated().sum(),
              "mode": mode,
              "models": models}
  

    # print(request.POST.get("option"))
  else:
    if df.empty:
      return redirect("LandingPage")
    context = {'user': user,
              "columnsName": df.columns,
              'flag': False}
  template = loader.get_template('graph.html')
  return HttpResponse(template.render(context, request))



def OutAnalysis(request, name):
  user = request.user
  global df
  col= name[15:-5]
  if request.method == "POST":
    pass
  else:
    q1=df[col].quantile(.25)
    q3=df[col].quantile(.75)
    IQR=q3-q1
    df[col][df[col]> (q3+IQR*1.5)]=df[col].mean()
    df[col][df[col]< (q1-IQR*1.5)]=df[col].mean()
    calc.load_df(df)
    fig=px.box(df, y=col)
    fig.write_image(r"member1/static/images/boxplot/"+col+".jpeg")
    context = {'user': user,
              'flag': False,
              'name': name,
              'IQR': IQR}
  template = loader.get_template('OA.html')
  return HttpResponse(template.render(context, request))

def ModelTrainingRoot(request):
    global prev_model_name
    print(prev_model_name)
    if len(prev_model_name) == 0:
      return redirect("GraphPage")

    # normal flow
    # return redirect(request, "ModelTraining/<str:model>/", {"model": prev_model_name[-1]})
    return redirect(
    f"/ModelTraining/{prev_model_name[-1]}/?split=20&scaler=minmax"
)

def ModelTraining(request, model):
  if model==None:
      return redirect("GraphPage")
  name= model
  user = request.user
  global df, prev_model_name, prev_model_scores

  split = request.GET.get("split", 20)  # default 20%
  split = int(split)
  # print("Train/Test Split:", split)

  scaler = request.GET.get("scaler", "minmax")
  # print("Scaler:", scaler)

  calc.split(split)
  calc.StandardSc(scaler)

  if request.method == "POST":
    pass
  else:
    # print("Mt", name)
    mse= calc.modelTraining(name)
    prev_model_tuples.append((name, mse))
    if name in prev_model_name:
      prev_model_scores[prev_model_name.index(name)] =mse
    else:
      prev_model_name.append(name)
      prev_model_scores.append(mse)
    fig=px.bar(x=prev_model_name, y=prev_model_scores)
    fig.write_image(r"member1/static/images/comparison/models"+".jpeg")
    loc= 'images\\comparison\\models.jpeg'
    context = {'user': user,
              'flag': False,
              "MSE": mse,
              'name': name,
              'mode': mode,
              'prev_model_tuples': prev_model_tuples,
              'loc': loc}
  template = loader.get_template('Modeltraining.html')
  return HttpResponse(template.render(context, request))



def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")


def user_preference(request):

    if request.method == "POST":
        # Read values from form
        default_split = request.POST.get("split", "20")
        scaler = request.POST.get("scaler", "standard")
        theme = request.POST.get("theme", "light")

        # Store in session (safe for learning apps)
        request.session["default_split"] = default_split
        request.session["scaler"] = scaler
        request.session["theme"] = theme

        messages.success(request, "Preferences saved.")
        return redirect("user_preference")

    context = {
        "default_split": request.session.get("default_split", "20"),
        "scaler": request.session.get("scaler", "standard"),
        "theme": request.session.get("theme", "light"),
    }

    return render(request, "user_preference.html", context)



def interactive_plots(request):

    plot_type = request.GET.get("plot", "scatter")
    x_axis = request.GET.get("x", "Feature 1")
    y_axis = request.GET.get("y", "Feature 2")

    context = {
        "plot_type": plot_type,
        "x_axis": x_axis,
        "y_axis": y_axis,
    }

    return render(request, "interactive_plots.html", context)
