import pandas as pd
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVR, SVC
import math
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.preprocessing import PolynomialFeatures

df=pd.DataFrame()
X_train= X_test= y_train= y_test=0
mode="Classification"
target=""

def load_df(d):
    global df
    df=d

def hist():
    global df
    l=[]
    for c in df.columns:
        if df[c].dtype != "object":
            fig=px.histogram(df, x=c)
            fig.write_image(r"member1/static/images/hist/"+c+".jpeg")
            s='images\\hist\\'+c+'.jpeg'
            l.append(s)
    return l

def pie():
    global df
    l=[]
    for c in df.columns:
        if df[c].dtype == "object" and len(df[c].unique())<10:
            fig=px.pie(df, values=list(df[c].value_counts()), names=df[c].unique(), title=c)
            fig.write_image(r"member1/static/images/pie/"+c+".jpeg")
            s='images\\pie\\'+c+'.jpeg'
            l.append(s)
    return l

def missing_data():
    global df
    for c in df.columns:
        if df[c].isna().sum()!=0:
            df[c]=df[c].fillna(df[c].mode()[0])
    # print(df.isna().sum())

def boxplot():
    global df
    l=[]
    for c in df.columns:
        if df[c].dtype != "object":
            fig=px.box(df, y=c)
            fig.write_image(r"member1/static/images/boxplot/"+c+".jpeg")
            s='images\\boxplot\\'+c+'.jpeg'
            l.append(s)
    return l

def KNNmodel():
    if mode=="Classification":
        model= KNeighborsClassifier()
        graph(model)
        model.fit(X_train, y_train)
        y_pred= model.predict(X_test)
        return accuracy_score(y_test, y_pred)
    else:
        model= KNeighborsRegressor()
        graph(model)
        model.fit(X_train, y_train)
        y_pred= model.predict(X_test)
        return mean_squared_error(y_test, y_pred)
    
def LRmodel():
    if mode=="Classification":
        model= LogisticRegression(max_iter=1000)
        graph(model)
        model.fit(X_train, y_train)
        y_pred= model.predict(X_test)

        importance = model.coef_[0]
        x=df.drop([target], axis=1)
        fig = px.bar(y=importance, x=x.columns, labels=dict(x="Features", y="Importance"))
        fig.update_xaxes(type='category')
        fig.write_image(r"member1/static/images/comparison/Importance.jpeg")

        return accuracy_score(y_test, y_pred)
    else:
        model= LinearRegression()
        graph(model)
        model.fit(X_train, y_train)
        y_pred= model.predict(X_test)
        return mean_squared_error(y_test, y_pred)

def SVMmodel():
    if mode=="Classification":
        model= SVC()
        graph(model)
        model.fit(X_train, y_train)
        y_pred= model.predict(X_test)
        return accuracy_score(y_test, y_pred)
    else:
        model= SVR()
        graph(model)
        model.fit(X_train, y_train)
        y_pred= model.predict(X_test)
        return mean_squared_error(y_test, y_pred)
    
def RFmodel():
    if mode=="Classification":
        model= RandomForestClassifier()
        graph(model)
        model.fit(X_train, y_train)
        y_pred= model.predict(X_test)
        return accuracy_score(y_test, y_pred)
    else:
        model= RandomForestRegressor()
        graph(model)
        model.fit(X_train, y_train)
        y_pred= model.predict(X_test)
        return mean_squared_error(y_test, y_pred)

def DTmodel():
    if mode=="Classification":
        model= DecisionTreeClassifier()
        graph(model)
        model.fit(X_train, y_train)
        y_pred= model.predict(X_test)
        return accuracy_score(y_test, y_pred)
    else:
        model= DecisionTreeRegressor()
        graph(model)
        model.fit(X_train, y_train)
        y_pred= model.predict(X_test)
        return mean_squared_error(y_test, y_pred)
    

def NBmodel():
    if mode=="Classification":
        model= GaussianNB()
        graph(model)
        model.fit(X_train, y_train)
        y_pred= model.predict(X_test)
        return accuracy_score(y_test, y_pred)
    # else:
    #     model= DecisionTreeRegressor()
    #     model.fit(X_train, y_train)
    #     y_pred= model.predict(X_test)
    #     return mean_squared_error(y_test, y_pred)
    
def modelTraining(name):
    score="N/A"
    # print(name)
    if name=="Logistic Regression" or name=="Linear Regression":
        # print("he")
        score=LRmodel()
    if name=="Random Forset Classifier" or name=="Random Forset Regressor":
        score=RFmodel()
    if name=="Support Vector Machine" or name=="Support Vector Regressor":
        score=SVMmodel()
    if name== "Decision Tree Classifier" or name=="Decision Tree Regressor":
        score=DTmodel()
    if name== "Naive Bayes":
        score=NBmodel()
    if name== "KNeighborsClassifier" or name=="KNeighborsRegressor":
        score=KNNmodel()
    # print(score)
    return score

def OHE(target):
    global df    
    new_df= df.copy()
    for i in df.columns:
        if df[i].dtype == "object":
            if i!= target:
                en=OneHotEncoder()
                f=np.array(df[i]).reshape(-1,1)
                en_df=en.fit_transform(f).toarray()
                col=[i+'_'+j for j in list(en.categories_[0].astype(str))]
                en_df=pd.DataFrame(en_df, columns=col, index=df.index)
                new_df=new_df.join(en_df)
                new_df=new_df.drop(i,axis=1)
            else:
                lb= LabelEncoder()
                new_df[i]= lb.fit_transform(df[target])
    # print(new_df)
    df= new_df


def StandardSc(scaler):
    global df, X_train, X_test
    if scaler=="minmax":
        sc=MinMaxScaler()
    elif scaler=="standard":
        sc=StandardScaler()
    elif scaler=="robust":
        sc=RobustScaler()
    else:
        return  
    X_train=sc.fit_transform(X_train) 
    X_test=sc.fit_transform(X_test)
    # print(df)
    
def setTarget(tar):
    global target
    target= tar

def split(split_ratio):
    global df, X_train, X_test, y_train, y_test, target
    # target=tar
    x=df.drop([target], axis=1)
    y=df[target]
    X_train, X_test, y_train, y_test = train_test_split(x,y, test_size=split_ratio/100, random_state=42)

def setMode(mod):
    global mode
    mode= mod


def graph(model):
    et=[]
    ev=[]
    for i in range(10, min(2000, len(X_train))):
        m = model
        m.fit(X_train[:i], y_train[:i])
        y_pred=m.predict(X_train[:i])
        et.append(math.sqrt(mean_squared_error(y_train[:i], y_pred)))
        y_pred=m.predict(X_test)
        ev.append(math.sqrt(mean_squared_error(y_test, y_pred)))
    
    df_graph= pd.DataFrame([et, ev])
    df_graph= df_graph.T
    df_graph.columns=["Training","Validation"]
    fig=px.line(df_graph)
    
    fig.update_layout(
    font_family="Courier New",
    font_color="blue",
    title_font_family="Times New Roman",
    title_font_color="red",
    legend_title_font_color="green",
    xaxis_title="Number of training samples",
    yaxis_title="Cost",
    legend_title="Cost VS Number of training samples",
    )

    fig.write_image(r"member1/static/images/comparison/CostVSm.jpeg")
    # print("Here")



    et=[]
    ev=[]
    for i in range(1,5):
        m = model
        poly = PolynomialFeatures(i)
        X_poly=poly.fit_transform(X_train)
        m.fit(X_poly, y_train)
        y_pred=m.predict(X_poly)
        et.append(math.sqrt(mean_squared_error(y_train, y_pred)))
        y_pred=m.predict(poly.transform(X_test))
        ev.append(math.sqrt(mean_squared_error(y_test, y_pred)))
    
    df_graph= pd.DataFrame([et, ev])
    df_graph= df_graph.T
    df_graph.columns=["Training","Validation"]
    fig=px.line(df_graph)
    
    fig.update_layout(
    font_family="Courier New",
    font_color="blue",
    title_font_family="Times New Roman",
    title_font_color="red",
    legend_title_font_color="green",
    xaxis_title="Number of Polynomial features",
    yaxis_title="Cost",
    legend_title="Cost VS Number of Polynomial features",
    )

    fig.write_image(r"member1/static/images/comparison/CostVSpoly.jpeg")
    # print("Here")