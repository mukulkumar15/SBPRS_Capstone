import pandas as pd
import numpy as np
import pickle
import warnings
warnings.filterwarnings("ignore")
from flask import Flask, render_template



def top5(user_input):
    
    # loading the clean data 
    df_new = pd.read_csv("dataset/updated_sample30.csv") 

    # loading the word vectorizer
    vectorizer  = pickle.load(open("pickle/vector.pkl","rb")) 

    #load the user recommendation matrix
    rec_model = pickle.load(open('pickle/recommendation_model.pkl', 'rb')) 

    
    #get top 20 products for the user
    #top_20 = rec_model.loc[user_input].sort_values(ascending=False)[0:20]
    try:

        top_20 = rec_model.loc[user_input].sort_values(ascending=False)[0:20]
        #merge the top20 products with original DF
        df1 = pd.merge(top_20,df_new,left_on='prod_name',right_on='prod_name',how = 'left') 
    
        #load the sentiment classification model
        sent_model = pickle.load(open("pickle/sentiment_model_LR.pkl", "rb")) 
    
        # to get the sentiment select review from merged DF as X
        X=df1['review'] 
        #use word vectorizer to transform X
        X_trans = vectorizer.transform(X.tolist())
        #get the prediction 
        prediction = sent_model.predict(X_trans)

        #add the predicction to merge DF  
        df1['sent_predicated'] = prediction
        #get the overall sentiment for each product 
        df2 = df1.groupby('prod_name').sent_predicated.mean() 
        # merge the overall sentiment predicted by user to top 20 data and sort by sentiment 
        df3= (pd.merge(top_20,df2,left_on='prod_name',right_on='prod_name',how = 'left').sort_values(by='sent_predicated',ascending=False))
        #convert the sentiment into percentage
        df3['sent_predicated'] = round(df3['sent_predicated']*100,2) 
        #convert into dataframe and select top 5 based on overall product sentiment percentage 
        df4 = pd.DataFrame(df3[:5]).reset_index()
        #select only product name from above DF 
        df5 = pd.DataFrame(df4['prod_name']) 
        #rename the product name column
        df5 = df5.rename(columns={"prod_name": "Product Name"})

        return  df5

    except KeyError:
        message = 'User ' + user_input + ' Does not exist!!'
        msg_list = [message]
        df5 = pd.DataFrame(msg_list,columns=['message'])
        return df5

    
    


def MissingUserError(Exception):
    status_code = 404
    message = 'No such user exists.'