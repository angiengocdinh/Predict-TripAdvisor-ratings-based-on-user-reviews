# -*- coding: utf-8 -*-
"""
Project: Predict TripAdvisor hotel ratings based on reviews. 

Data was scraped as a random sample from TripAdvisor website. I only scraped a
small sample for academic purpose, with approval from TripAdvisor. 

In this project, I only look at data in New York City.

Script to scrape the data. 

Created on Thu Sep 6 00:44:57 2016

@author: Angie Dinh
"""
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
import requests
import math
from threading import Thread
import random


class cityHotelUrl:
    # A seperate static class to store data on:
        #1. TripAdvisor pages of hotels in 5 cities: Rome, Paris, New York,
            #Prague, and London. However, I only scraped the data for New York
    
        #2. Length of all "next-pages" of the each TripAdvisor city page
        
    #A dictionary of cities and their corresponding TripAdvisor url
    city_url_table= dict()
    
    city_url_table["Rome"]="https://www.tripadvisor.com/Hotels-g187791-Rome_Lazio-Hotels.html"
    city_url_table["Paris"]="https://www.tripadvisor.co.uk/Hotels-g187147-Paris_Ile_de_France-Hotels.html"
    city_url_table["New York"]="https://www.tripadvisor.co.uk/Hotels-g60763-New_York_City_New_York-Hotels.html"
    city_url_table["Prague"]="https://www.tripadvisor.co.uk/Hotels-g274707-Prague_Bohemia-Hotels.html"
    city_url_table["London"]="https://www.tripadvisor.co.uk/Hotels-g186338-London_England-Hotels.html"
    
    #A dictionary of cities and the corresponding number of "next-pages"
    city_length_list_table = dict()
    city_length_list_table["New York"]=16
    city_length_list_table["Rome"]=44
    city_length_list_table["Paris"]=60
    city_length_list_table["Prague"]=23
    city_length_list_table["London"]=36

def requestPage(web_link):
    #Function to go to a web page from its url and returns the page as text 
    #format
        #Args: the link of the page
        #Returns: the web page in text format
    web_data=""
    try:
        url=requests.get(web_link)
        web_data=url.text
    except (requests.ConnectionError, requests.exceptions.SSLError) as e:
        pass
    return web_data


#Below is the logic of this program:
    
    #1. Find the TripAdvisor listing all hotel in a given city
    
    #2. All the hotels do not fit in one page, so there are multiple 
    # listing pages of hotels
    
    #3. First, get a list of all the hotel listing pages in a city (all the 
    #"next-pages")
    
def getHotelListingPage(city, page_order):
    #Function to get the link of a hotel listing page
        #Args: city name, the order of the page in the main listing page
        #(from 1 to the end)
        #Returns: link of that page
        
    #Find the url of the city in the dictionary assigned above
    main_hotel_page=cityHotelUrl.city_url_table[city]
    
    #The patterns of all hotel pages in one city is 30*the order of the page 
    #Use the patterns to find the page link
    url_change_index=main_hotel_page.find('-')+(main_hotel_page[main_hotel_page.find('-')+1:len(main_hotel_page)]).find('-')+1
    hotel_page_in_order=main_hotel_page[0:url_change_index+1]+"oa"+str(30*page_order)+"-"+main_hotel_page[url_change_index+1:len(main_hotel_page)]
    return hotel_page_in_order

    #4. Next, we go through each hotel listing page and find the links of all
    #hotels in the page
    
def getHotelLink(hotel_listing_page):
    #Function to get all urls of hotels listed in one listing page
        #Args: the listing page
        #Returns: the list of all hotel links
        
    all_hotel_urls=[]
    
    #If the listing page is not null: 
    if (len(hotel_listing_page)>0):
        
        #Request the page 
        hotel_listing=requestPage(hotel_listing_page)
        
        #Get the tags containing hotel links
        only_property_title = SoupStrainer("a", class_="property_title ")
        hotel_link_raw=BeautifulSoup(hotel_listing, "html.parser", parse_only
                                     =only_property_title)
        
        #Extract the links from each tag:
        for link in hotel_link_raw:
            hotel_url=link.get('href')
            
            #Construct full link of each hotel
            all_hotel_urls.append("https://www.tripadvisor.co.uk"+hotel_url)
    return all_hotel_urls

    #5. Next, we go to each link in the list of hotel links to get to the 
    #hotel page. To be more efficient, I make the program go to all the links
    #in parallel. Now we see reviews and ratings of each hotel. 
        #There are too many reviews to fit in a page. So we need to:
            #5.1: loop through all the review pages of each hotel. 
            #5.2: From each page, we need to scrape the review and rating. 

def getReviewRatingFromPage(hotel_page):
    #Function to scrape all reviews, review header, and ratings from a specific 
    #review page of a hotel and write it to a .txt file
    #This function does step 5.1
        #Args: the specific review page urls
    try:
        
        #if hotel page is not null:
        if (len(hotel_page)>0):
            
            #request the page
            web_data=requestPage(hotel_page)
            
            #select the tags of the bigger blocks
            #that have reviews and ratings
            only_wrap_class=SoupStrainer("div", class_="wrap")
            review_rating_data=BeautifulSoup(web_data, "html.parser", 
                                             parse_only=only_wrap_class)
            
            #Create an empty list of data row. Each element in the list will
            #be a dictionary of ratings, reviews, and review headers. 
            row_list=[]
            
            #Go through all the tags
            for tag in review_rating_data:
                
                #Find the tags specifically contain reviews, review header,
                #and ratings
                
                #rating:
                rating_raw=tag.find_all("div", class_="rating reviewItemInline")                
                if (len(rating_raw)>0):
                    
                    #review header:
                    review_header_raw=tag.find_all("span", class_="noQuotes")
                    
                    #review
                    review_raw=tag.find_all("p",class_="partial_entry")
                    
                    #for each tags, get the rating, review header, and review 
                    #in text format:
                    for i in range(0,len(rating_raw)):
                        #Rating is a bubble object, so we need to grab
                        #the size of the bubble
                        rating_text=str(rating_raw[i].contents[0].get_text)
                        rating_text=rating_text[rating_text.find(' bubble_')+
                                                len(' bubble_'):rating_text.
                                                   find(' bubble_')+
                                                       len(' bubble_')+2]
                        
                        #and convert it into real rating 
                        rating=int(rating_text)/10
                                  
                        #Get the review 
                        review_text=review_raw[i].string
                                              
                        #Get the review header 
                        review_header_text=review_header_raw[i].string
                                                            
                        #Create a dictionary of rating, review header, and
                        #review 
                        row=dict()
                        row.update({'rating':rating, 'review_header':
                            review_header_text, 'review':review_text})
    
                        #Append the dictionary into a list of reviews,
                        #ratings, and review headers 
                        row_list.append(row)
            
            #Reformat the row list 
            row_list_string=str(row_list)
            row_list_string=row_list_string[1:len(row_list_string)-1]
            
            #Write it to file: 
            with open('TripAdvisorData.txt','a', encoding='utf-8') as file: 
                file.write(row_list_string)
    except (requests.ConnectionError, requests.exceptions.SSLError) as e:
        pass

def findNReview(hotel_soup_result):
    #Find the number of reviews for each hotel. This function determine
    #When to stop looping. 
        #Args: the Beautiful Result of a hotel page
        #Returns: the number of reviews the hotel has
    n_review=0
    for tag in hotel_soup_result:
        #Find the tags that contain that number 
        n_review_raw=tag.find_all("b")
        
        for word in n_review_raw:
            n_review_text=word.string
            
            #Extract the number 
            n_review_text=n_review_text.replace(",","")
            #It is the character before the space
            n_review=int(n_review_text[(n_review_text.find(" ")+1):
                (len(n_review_text)-1)])
    
    return n_review

def getReviewOneHotel(hotel_url, n_page_per_hotel):
    #Get a random sample of reviews, ratings, and review headers for each hotel
    #by: 
        #Looping through a certain number of review pages chosen at random
        #Scraping all ratings, review headers, and reviews of each page.
        
    #This is to efficiently scrape a small dataset while not creating selection
    #bias. If we specify which page to scrape, there can be selection bias
    #as higher-rated hotels are listed at the first few pages. 
    
    if (len(hotel_url)>0):
        
        #Get the hotel page and change to BeautifulSoup format
        hotel_soup=requestPage(hotel_url)
        
        #Get the number of reviews 
        soup_filtered=SoupStrainer("form", action="/SetReviewFilter#REVIEWS")
        find_n_review=BeautifulSoup(hotel_soup, "html.parser", 
                                    parse_only=soup_filtered)
        n_review=findNReview(find_n_review)
        
        #Convert to the number of review pages. Each page has 10 reviews, so 
        #the number of pages is the number of reviews devided by 10. Do not 
        #count the first page, it is scraped seperately because it has a 
        #different url pattern. 
        
        n_review_page=math.ceil((n_review/10)-1)
        
        #Get the reviews and ratings from the first page
        getReviewRatingFromPage(hotel_url)
        
        #Do the same for all the following pages
        if (n_review_page>0):
            for i in range (0, n_page_per_hotel-1):
                
                #Find which page to scrape
                page_number=random.randint(1,n_review_page)
                
                #Construct the page url using the pattern
                next_page=hotel_url[0:hotel_url.find("Reviews")+7]
                +"-or"+str(page_number*10)+hotel_url[(hotel_url.
                          find("Reviews")+7):len(hotel_url)]
    
                #Scrape it 
                getReviewRatingFromPage(next_page)

def getReviewOneHotelParallel(all_hotel_urls, n_page_per_hotel):
    #Function to perform multi-threading for better efficiency
    
    #NOTE: THIS IS NOT THE PROPER WAY TO IMPLEMENT MULTITHREADING/PARALLELISM 
    #However, for the purpose of this project - getting a small subset of data
    #for analysis purposes, without much concerns about preserving all the data,
    #this implementation works fine.
        #Args: all hotel links, the number of hotel review pages to scrape
    
    for url in all_hotel_urls:
        Thread(target=getReviewOneHotel,args=(url, n_page_per_hotel,)).start()
        #You would normally need to join the threads or use multiprocessing 
        #instead but for the purpose of this project, this works to grab the 
        #data and is faster. 
    
def getReviewOneCity(city, n_page_per_hotel):
    #Get all ratings, reviews, and review headers on randomly selected hotels
    #in a given city and print to a .txt file
        #Args: city name, number of review pages to scrape
        
    #Loop through all the hotel listing pages of a city (Step 3 and 4)
    for i in range (0, int(cityHotelUrl.city_length_list_table[city])):
        
        #Get the page's link (step 3)
        hotel_page_in_order=getHotelListingPage(city, i)
        
        #Get a list of urls of hotels listed in each page (Step 4)
        all_hotel_urls=getHotelLink(hotel_page_in_order)
        
        #Go to all the urls, in parallel, and scrape ratings, reviews, 
        #and review header. (Perform Step 5, 5.1, and 5.2 in parallel)
        getReviewOneHotelParallel(all_hotel_urls, n_page_per_hotel)

def main():
    getReviewOneCity("New York",8)
  

if __name__ == "__main__": main()