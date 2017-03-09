#Project: Predict TripAdvisor rating based on reviews

#Script to perform text mining on the data and create a word frequency table 

#Load and install package
#install.packages("stringr", repos='http://cran.us.r-project.org')
#install.packages("SnowballC")
#install.packages("qdapDictionaries")
#install.packages("tm")
#install.packages("bigmemory")

library(SnowballC)
library(dplyr)
library(mosaic)
library(stringr)
library(qdapDictionaries)
library(Matrix)
library(tm)
library(bigmemory)

memory.limit(size=1000000)


createFreqTable <- function(variable){
  #Function to create the word frequency table
    #Args: variable to create the frequency on
    #Returns: the word frequency table
  
  #create Corpus
  data_corpus=Corpus(VectorSource(variable), readerControl = list(language="eng"))
  
  #Change to lower case
  data_corpus  <- tm_map(data_corpus, content_transformer(tolower), lazy=T)
  
  #Remove punctuation, numbers, and stop words
  data_corpus  <- tm_map(data_corpus, removePunctuation, lazy=T)
  data_corpus <- tm_map(data_corpus, removeNumbers, lazy=T)
  data_corpus  <- tm_map(data_corpus, removeWords, stopwords("english"), lazy=T)
  
  #Perform stemming (convert all words to its base form)
  data_corpus  <- tm_map(data_corpus, stemDocument, lazy=T)
  
  #Strip white space
  data_corpus  <- tm_map(data_corpus, stripWhitespace, lazy=T)
  
  #Create word frequency matrix
  word_freq_matrix=DocumentTermMatrix(data_corpus)
  word_freq_big_matrix=as.matrix(word_freq_matrix)
  
  #Sum all frequencies of each word for all reviews 
  freq_sum=colSums(word_freq_big_matrix)
  
  #Remove sparse terms
  index_sparse_terms=which(freq_sum<5)
  word_freq_final_matrix=word_freq_big_matrix[,-index_sparse_terms]
  
  #Create the table
  word_freq_data=data.frame(word_freq_final_matrix)
  return(word_freq_data)
}

#Load data
TripAdvisorData <- read.csv("C:/Users/stuadmin/Desktop/Projects/TripAdvisorData.csv")

#Create 2 word-frequency tables on reviews and review headers 
review_freq_table=createFreqTable(TripAdvisorData$review)
review_header_freq_table=createFreqTable(TripAdvisorData$review_header)

#Merge them, with the review header table weighing 3 times
review_freq_table[which(names(review_freq_table)%in% names(review_header_freq_table))]=review_freq_table[which(names(review_freq_table)%in% names(review_header_freq_table))]+3*(review_header_freq_table[which(names(review_header_freq_table)%in% names(review_freq_table))])
review_header_not_match=review_header_freq_table[-which(names(review_header_freq_table)%in% names(review_freq_table))]
review_header_not_match=3*review_header_not_match
review_data_final=cbind(TripAdvisorData$rating, review_freq_table, review_header_not_match)

#Write the .csv file
write.csv(review_data_final, "TripAdvisor_Frequency_Data1.csv")