# This is the main program for the project in the sense that it spits out
# the final data.

# Grab the necessary packages.
import pandas as pd
import time
from import_twitter_data import processTweets
from TVBTN_web_scrape import createHHData

# Change the width of the console to help with wrapping.
pd.set_option('display.width', 1000)

# First I will read in the Nielsen data from TVByTheNumbers.com.

# Import a list of URLs containing the links to the Nielsen data
fname = r'F:/Python/Data_Science/Project_Data/Final_Data/TVBTN_URL_LIST.txt'
urlList = []
with open(fname) as f:
    for row in f:
        urlList.append(row.strip()) #Strip the new lines.

# Loop through the createHHData function using our list of URLs. Use the sleep
# function to place 2 seconds between each pull so that we do not get
# blocked by the web site! This creates a list of DataFrames.
listDailyDFs = []
for row in urlList:
    dailyDF = createHHData(row)
    time.sleep(2)
    listDailyDFs.append(dailyDF)

# Turn the list of DataFrames into a single DataFrame.
nielsenDF = pd.DataFrame()
for row in listDailyDFs:
    nielsenDF = nielsenDF.append(row)

# Reindex the final DataFrame and do some cleaning
nielsenDF = nielsenDF.reset_index()
nielsenDF.network.replace('10:57-11:57 p.m.', 'CBS', inplace=True)
nielsenDF.drop("index",axis=1,inplace=True)

# Next, I will read in the twitter data, one day at a time.

# Define the file locations to be read in by the function.
file_location1 = r'F:/Python/Data_Science/Project_Data/Final_Data/data/sun_nov01_15/'
file_location2 = r'F:/Python/Data_Science/Project_Data/Final_Data/data/mon_nov02_15/'
file_location3 = r'F:/Python/Data_Science/Project_Data/Final_Data/data/tue_nov03_15/'
file_location4 = r'F:/Python/Data_Science/Project_Data/Final_Data/data/wed_nov04_15/'

# Read in the data for one of the folders. This can only be done one folder
# at a time due to computer limitations.
# NOTE: This function requires that a dataframe of hashtags, handles, and show
# titles be located in specific location. Edit the function with this location.

# NOTE: Ideally, I would write a for loop to just cycle through the above
# folders to get to my list of usable tweets, but this is not done here to
# show my process given the limitations of my computer.
weekdayTweets = processTweets(file_location1)

# Create a dataframe containing the total tweets for each program. Then
# subset the data to create a similar dataframe but with the unique
# tweets for each program. Lastly, merge the two dataframes and export to
# excel to be read in later.

totalTweets = weekdayTweets.groupby(['air_date','title']).title.agg(['count'])
totalTweets.rename(columns={'count':'total_tweets'},inplace=True)
totalTweets.reset_index(inplace=True)

uniquePrep = weekdayTweets.drop_duplicates(subset=['user_id','title','air_date'])

uniqueTweets = uniquePrep.groupby(['air_date','title']).title.agg(['count'])
uniqueTweets.rename(columns={'count':'unique_tweets'},inplace=True)
uniqueTweets.reset_index(inplace=True)

totalAndUnique = totalTweets.merge(uniqueTweets,how='inner',on=['air_date','title'])

totalAndUnique.to_csv(r'F:/Python/Data_Science/Project_Data/Final_Data/sunday.csv')

# Prep the Nielsen dataframe for merging.
nielsenDF.rename(columns={'show':'title'},inplace=True)
nielsenTweets = totalAndUnique.merge(nielsenDF,how='inner',on=['air_date','title'])

nielsenTweets.to_csv(r'F:/Python/Data_Science/Project_Data/Final_Data/sunday_nielsen.csv')