# Read in the final Twitter data to both analyze and produce visualizations.

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn import metrics
from sklearn.linear_model import LinearRegression
import statsmodels.formula.api as smf

# Adjust the parameters of the figure sizes.
plt.rcParams['figure.figsize'] = (8, 6)
plt.rcParams['font.size'] = 14

# Import the various files.
file1 = r'F:/Python/Data_Science/Project_Data/Final_Data/final_tweet_subset_data.csv'
file2 = r'F:/Python/Data_Science/Project_Data/Final_Data/final_total_tweet_data.csv'
file3 = r'F:/Python/Data_Science/Project_Data/Final_Data/air_date_t_+-_1.csv'

liveTweets = pd.read_csv(file1, sep=',')
allTweets = pd.read_csv(file2, sep=',')
timeTweets = pd.read_csv(file3, sep=',')

# Remove the programs with obvious errors.
liveTweets = liveTweets[liveTweets.title.str.contains(
             "Arrow|Chicago PD|Empire|Supernatural|Code Black"
             ) == False]
liveTweets.reset_index(inplace=True)
liveTweets.drop('index',axis=1,inplace=True)

# Get dummy variables for the network and weekday to add as control variables
# to strengthen our model.
liveTweets = pd.concat([liveTweets, pd.get_dummies(liveTweets['network'])],axis=1)
liveTweets = pd.concat([liveTweets, pd.get_dummies(liveTweets['day'])],axis=1)

# Adjust the axes to make the output more readable.
liveTweets['unique_tweets'] = liveTweets['unique_tweets'].divide(1000)
liveTweets['total_tweets'] = liveTweets['total_tweets'].divide(1000)

# Define a program to calculate the root-mean-square error (RMSE) based on
# the feature columns as an input.
def rmse(feature_cols):
    X = liveTweets[feature_cols]
    y = liveTweets.rating
    linreg = LinearRegression()
    linreg.fit(X, y)
    y_pred = linreg.predict(X)
    return np.sqrt(metrics.mean_squared_error(y, y_pred))
    
print(rmse(['unique_tweets']))
print(rmse(['unique_tweets','ABC','CBS','FOX','NBC','Sun','Mon','Tue']))
    

# Set two lists of features to run through our regression.
features_base = ['unique_tweets']
features = ['unique_tweets','ABC','CBS','FOX','NBC','Sun','Mon','Tue']

# Set the response variable to run through our regression.
response = ['rating']

# Define a function to take an input feature variables and a response
# variable and print the intercept, coefficients, and the score which is
# the R^2 value (the coefficient of determination).
def linRegFunction(feature_cols, response):
    X = liveTweets[feature_cols]
    y = liveTweets[response]
    linReg = LinearRegression()
    linReg.fit(X, y)
    print(linReg.intercept_)
    print(linReg.coef_)
    print(linReg.score(X,y))

linRegFunction(features, response)
linRegFunction(features_base, response) # Only run this one 
                                        # for the below figures.

# A small script to examine the information that StatsModels produces
# in a linear regression.
lm = smf.ols(formula ='rating ~ unique_tweets + ABC + CBS + FOX + NBC + Sun + Mon + Tue', data=liveTweets).fit()
lm.summary()

# Produce figures used in the final paper.

# Produce the figure representing unique tweets against the Nielsen rating.
X = liveTweets[features_base]
y = liveTweets[response]
linRegPlt1 = LinearRegression()
linRegPlt1.fit(X,y)
sns.lmplot('unique_tweets','rating',hue='network',palette='bright',
           data=liveTweets,fit_reg=False)
plt.plot(liveTweets.unique_tweets,linRegPlt1.predict(X),
         color = 'navy',linewidth = 0.5)
sns.set_style("white")
plt.xlim([0,6])
plt.xlabel('Unique tweets (in thousands)')
plt.ylabel('Nielsen rating (percent of US households)')
plt.title('Twitter usage moderately predicts the Nielsen rating')
fname1 = r'F:/Python/Data_Science/Project_Data/Final_Data/unique_tweets.png'
plt.savefig(fname1)

# Produce the figure representing unique tweets against total tweets.
y = liveTweets['viewers']
linRegPlt2 = LinearRegression()
linRegPlt2.fit(X,y)
sns.lmplot('unique_tweets','viewers',hue='network',palette='bright',data=liveTweets,fit_reg=False)
plt.plot(liveTweets.unique_tweets,linRegPlt2.predict(X),color = 'navy',linewidth = 0.5)
sns.set_style("white")
plt.xlim([0,6])
plt.ylim([0,20])
plt.xlabel('Unique tweets (in thousands)')
plt.ylabel('Total viewers (in thousands)')
plt.title('Older people love CBS and are not on Twitter')
fname2 = r'F:/Python/Data_Science/Project_Data/Final_Data/total_viewers.png'
plt.savefig(fname2)

# Produce the figure on "spamminess"
y = liveTweets['total_tweets']
linRegPlt3 = LinearRegression()
linRegPlt3.fit(X,y)
sns.lmplot('unique_tweets','total_tweets',hue='network',palette='bright',data=liveTweets,fit_reg=False)
plt.plot(liveTweets.unique_tweets,linRegPlt3.predict(X),color = 'navy',linewidth = 0.5)
sns.set_style("white")
plt.xlim([0,6])
plt.ylim([0,30])
plt.xlabel('Unique tweets (in thousands)',fontsize='14')
plt.ylabel('Total tweets (in thousands)',fontsize='14')
plt.title('Relevance of the "spamminess" of some Twitter users?',fontsize='14')
fname3 = r'F:/Python/Data_Science/Project_Data/Final_Data/spamminess.png'
plt.savefig(fname3)

# Produce the figure on the percentage of tweets which occur on the air date.
columns = ['air_date_t-1','air_date','air_date_t+1']
labels=['Air date, t-1','Air date','Air date, t+1']
ax = plt.gca()
timeTweets.boxplot(column=columns,return_type='axes')
sns.set_style("white")
ax.set_xticklabels(labels)
ax.grid(b=None, which='major', axis='x')
plt.ylabel('Share of total unique tweets',fontsize='14')
plt.title('Most unique tweets happen on the air date',fontsize='16')
fname4 = r'F:/Python/Data_Science/Project_Data/Final_Data/air_date_tweets.png'
plt.savefig(fname4)



