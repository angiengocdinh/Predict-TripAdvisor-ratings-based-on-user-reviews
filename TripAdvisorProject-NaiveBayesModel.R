#install.packages("e1071")
#install.packages("tidyverse")
#install.packages("openNLP")

#Project: Predict TripAdvisor rating based on reviews

#Script to implement Naive Bayes Model, train the model, perform prediction, 
#and perform cross-validation to test the model

library("openNLP")
library("NLP")
library(tidyverse)
library(e1071)
library(bigmemory)
memory.limit(size=1000000000000)


compute.priors <- function(x){
  #Compute prior probability (P(c_i))
    #Args: a variable
    #Returns: table of probabilities of instances in that variable
  result<-prop.table(table(x))
  return(result)
}

conditionalProb <- function(class_word_freq){
  #Calculate conditional probability of each class in the training set P(X_1=a_1???c_i):
    #Args: variable of word frequency of a class (in this case, rating)
    #Return: the conditional probability
  result=(class_word_freq+1)/(sum(class_word_freq)+length(class_word_freq))
  return(result)
}

conditionalProb_CNB <- function(class_word_freq, sum_word_freq){
  #Calculate conditional probability complement of training set (Pcom(X_j=a_jz???c_i))
    #Args: variable of word frequency of a class (in this case, rating), the sum of word frequency in 
    #all classes
    #Returns: the conditional probability complement (refer to the report for reference
    #on what this is)
  result=(sum_word_freq-class_word_freq+1)/((sum_word_freq-class_word_freq)+length(class_word_freq))
  return(result)
}

probClassEach <- function(class_prob_cond, class_prob_cond_CNB, row){
  #Calculating probability of each class (in the prediction set)
    #Args: the conditional probability of each training set class,
          #conditional probability complement of each training set class
          #the row (observation) to be classified
    #Returns: The probability that the observation belong to each classes 
    #In this case, it is a list of 5 probabilities for 5 classes 
    #Refer to the report for the formula
  result=sum((log(class_prob_cond)-log(class_prob_cond_CNB))*row)
  return(result)
}

NaiveBayesModel=function(trainData,testData){
  #Naive Bayes Model
    #Args: training set, testing set
    #Return: the vector of predicted class
  
  #Initiate the vectors
  class <- list() #list of 5 vectors for each class
  class_word_freq <- list() #word frequency of each class
  class_prob_cond <- list() #conditional probability of each class
  class_prob_cond_CNB <- list() #conditional probability complement of each class
  
  log_prob_class <- list() #summation of all the log probabilities that each word in a review belong
                            # to a certain class
  log_probability <- list() #log probability of each class (log probability that a review belong to a 
                            #class), equal to log_prob_class + log(P(C_i))
  
  testData_without_y=testData[,-c(1,2)] #remove ratings (y-value) from the test data

  for (i in 1:max(trainData$rating)){
    
    #seperate the reviews into 5 classes
    class[[i]]=subset(trainData, rating==i)
    
    #Find word frequency of each class for every word
    class_word_freq[[i]]=colSums(class[[i]][-c(1,2)])
    
    #Find conditional probability of each class 
    class_prob_cond[[i]]=conditionalProb(class_word_freq[[i]])
    
    #Initiate vectors for prediction of each class
    log_prob_class[[i]] = vector("numeric", nrow(testData_without_y))
    log_probability[[i]] = vector("numeric", nrow(testData_without_y))
  }
  
  #Find the conditional probability complement: 
  class_word_freq_df=data.frame(class_word_freq)
  for (i in 1:max(trainData$rating)){
    class_prob_cond_CNB[[i]] = (rowSums(class_word_freq_df[,-i])+1)/(sum(rowSums(class_word_freq_df[,-i]))+length(class_word_freq[[i]]))
  }
  
  #Predicting with the testing set
  test_list=as.list(data.frame(t(testData_without_y)))
  
  #Compute prior class
  class_priors=compute.priors(trainData[,2])
  
  #for all classes
  for (i in 1:max(trainData$rating)){
    
    #Find the summation of log probabilities that each word in a review belong to
    #that particular class
    log_prob_class[[i]]=lapply(test_list, function(x){probClassEach(class_prob_cond[[i]], 
                                                                    class_prob_cond_CNB[[i]], x)})
    
    #Find the probability that a review belong to that particular class:
    #log_prob_class + log(P(C_i))
    log_probability[[i]]=lapply(log_prob_class[[i]], function(x){x+log(class_priors[i])})
  }
  
  #Combine probability that a review belong to 5 classes as a data frame of 5 columns 
  result=data.frame(t(do.call(rbind, log_probability)))
  
  #Find the class with the maximum probability
  prediction=apply(result, 1, function(x){which.max(x)})
  return(prediction)
}

#Run the model:

#Load data
TripAdvisor_Frequency_Data <- read_csv("C:/Users/stuadmin/Desktop/Projects/TripAdvisor_Frequency_Data.csv")

#Rename "rating"
TripAdvisor_Frequency_Data <- TripAdvisor_Frequency_Data %>%
  rename("rating"=`TripAdvisorData$rating`)

#Perform 10-fold cross-validation
n_folds <- 10

#Randomly sample 5 folds 
folds_i <- sample(rep(1:n_folds, length.out = nrow(TripAdvisor_Frequency_Data)))

#Initiate vectors of accuracy 
percentage_accuracy_strict=rep(0,n_folds)
percentage_accuracy_flex=rep(0,n_folds)

#For all folds
for (k in 1:n_folds) {
  
  #Training/testing set split 
  test_i <- which(folds_i == k)
  train_xy <- TripAdvisor_Frequency_Data[-test_i, ]
  test_xy <- TripAdvisor_Frequency_Data[test_i, ]
  
  #Train the model and run on the testing set 
  prediction=NaiveBayesModel(train_xy, test_xy)
  
  #Find the strict accuracy percentage 
  accuracy_strict=ifelse(prediction==test_xy$rating,1,0)
  percentage_accuracy_strict[k]=sum(accuracy_strict)/length(accuracy_strict)
  
  #Find the less-strict accuracy percentage
  accuracy_flex=ifelse(abs(prediction-test_xy$rating)<2,1,0)
  percentage_accuracy_flex[k]=sum(accuracy_flex)/length(accuracy_flex)
}

#Plot the accuracy percentages

#Strict accuracy 
myplot <- ggplot(data.frame(percentage_accuracy_strict), aes(x = seq(1,length(percentage_accuracy_strict)), 
                        y = percentage_accuracy_strict*100))
myplot + geom_line(aes()) +
  labs(x="Cross-Validation Index", y="Accuracy") + 
  geom_text(aes(label=round(percentage_accuracy_strict*100,1)))

#Less-strict accuracy

myplot <- ggplot(data.frame(percentage_accuracy_flex), aes(x = seq(1,length(percentage_accuracy_flex)), 
                                                             y = percentage_accuracy_flex*100))
myplot + geom_line(aes()) +
  labs(x="Cross-Validation Index", y="Accuracy") + 
  geom_text(aes(label=round(percentage_accuracy_flex*100,1)))

#Compare to the base model
tally(~TripAdvisor_Frequency_Data$rating, format="percent")
