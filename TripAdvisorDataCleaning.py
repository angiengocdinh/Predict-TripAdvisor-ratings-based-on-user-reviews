# -*- coding: utf-8 -*-
"""
Project: Predict TripAdvisor hotel ratings based on reviews. 

Data was scraped as a random sample from TripAdvisor website. I only scraped a
small sample for academic purpose, with approval from TripAdvisor. 

In this project, I only look at data in New York City.

Script to clean the data

@author: Angie Dinh
"""

import pandas as pd

def main():
    
    #load the data
    TripAdvisor_data_raw=[]
    file= open('TripAdvisorData.txt', 'r', encoding='utf-8')
    data=file.read()
    
    #Seperate the raw data into rows. The original seperator was "}, {"
    data_replace=data.replace('}{','}, {')
    TripAdvisor_data_raw=data_replace.split('}, {')
    
    #Initiate an empty list to store the clean data
    TripAdvisor_data=[]
    
    #Loop through each rows and extract texts that are reviews, review headers
    # or ratings
    for row in TripAdvisor_data_raw:
        try:
            start_rating=0
            end_rating=0
            start_review=0
            end_review=0
            start_review_header=0
            end_review_header=0
            
            #Find indices in each row that indicate the start and 
            #the end of each rating, review, and review header 
            
            if row[1:7]=="rating" or row[2:8]=="rating":
                start_review=row.find("'review':")+len('review:')+4
                end_review=len(row)
                start_review_header=row.find('review_header')+len('review_header')+4
                end_review_header=row.find("'review':")-3
                start_rating=row.find('rating:')+len('rating:')+4
                end_rating=row.find('review_header')-3
                
            elif row[1:7]=="review":
                start_review=row.find("'review':")+len('review:')+4
                end_review=row.find('rating:')-3
                start_rating=row.find("'rating':")+len('rating')+4
                end_rating=row.find('review_header')-3
                start_review_header=row.find('review_header')+len('review_header')+4
                end_review_header=len(row)
            
            #Put rating, review, and review header into key-value pairs 
            #of a dictionary
            row_dictionary=dict()
            row_dictionary['rating']=float(row[start_rating:end_rating])
            row_dictionary['review']=row[start_review:end_review]
            row_dictionary['review_header']=row[start_review_header:end_review_header]
            
            #Add the dictionary into the list of rows
            TripAdvisor_data.append(row_dictionary)
            
        except ValueError:
            print(row)
            print(row[start_rating:end_rating])
    
    #Convert the list of dictionary into a data frame and create a .csv file
    TripAdvisor_data_frame=pd.DataFrame(TripAdvisor_data)
    TripAdvisor_data_frame.to_csv("TripAdvisorData.csv")

if __name__ == "__main__": main()
