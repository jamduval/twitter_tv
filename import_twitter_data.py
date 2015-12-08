#Grab the necessary packages.
import json
import os
import pandas as pd
import datetime
import re

# This program takes in the Twitter data and assigns the information
# to a library.

def processTweets(folder_path):
    
    # Import the tweets from the folder in which they are stored.
    jsonPath = folder_path
    jsonFiles = [tweet for tweet in os.listdir(jsonPath) if tweet.endswith('.json')]
    
    # Write the tweets to a list.
    # NOTE: Do NOT attempt to view the entire list, or the computer will die. 
    #       Look at individual tweets instead, like tweetList[451].
    tweetList = []
    a=0
    for file in jsonFiles:
        # I use this statement for debugging, since there are occasionally bad tweets,
        # and while I print a (their locations), thy try/except method will 
        # skip over them.
        a = a + 1
        try:
            with open(os.path.join(jsonPath,file)) as jsonFile:
                tweet = [json.loads(row) for row in jsonFile]
                tweetList.append(tweet)
        except ValueError:
            print("Bad file found in jsonFiles at:", a-1)
            
    # The above places each tweet into its own list, so this list 
    # comprehension removes that, and it's simply a list of dictionaries.      
    tweetList = [row[0] for row in tweetList]      
    
    # Initialize a DataFrame for which we will write columns.
    tweetsDF = pd.DataFrame() 
    
    ##################################################################################
    #######             Add columns to my dataframe from the tweet.          #########
    
    #Indicates the user_id of the tweet.
    tweetsDF['user_id'] = list(map(lambda tweet: tweet['user']['id_str'], tweetList))
    
    # Indicates when the tweet was created.
    tweetsDF['created_at'] = list(map(lambda tweet: tweet['created_at'], tweetList))
    
    #Indicates how far off from UTC time the tweet happened at.
    tweetsDF['utc_offset'] = list(map(lambda tweet: tweet['user']['utc_offset'], tweetList))
    
    # Extract the time from the "created_at" variable
    tweetsDF['tweet_time'] = list(map(lambda tweet: tweet['created_at'][11:19], tweetList))
    tweetsDF['tweet_time'] = pd.to_datetime(tweetsDF['tweet_time'], format='%H:%M:%S')
    
    # Extract the date from the "created_at" variable and adjust for UTC time.
    tweetsDF['tMonth'] = list(map(lambda tweet: tweet['created_at'][4:10], tweetList))
    tweetsDF['tYear'] = list(map(lambda tweet: tweet['created_at'][26:30], tweetList))
    tweetsDF['air_date'] = tweetsDF['tMonth'] + ', ' + tweetsDF['tYear']
    tweetsDF['air_date'] = pd.to_datetime(tweetsDF['air_date'], format="%b %d, %Y")
    
    TT = [row for row in tweetsDF['tweet_time']]
    AD = [row for row in tweetsDF['air_date']]
    TT_AD = list(zip(TT,AD))
                                                                                    
    newAD = []
    for row in TT_AD:
        if datetime.time(21,0,0) <= row[0].time() <= datetime.time(23,59,59):
            newAD.append(row[1])
        else:
            newAD.append(row[1] - datetime.timedelta(days=1))
            
    tweetsDF['air_date'] = list(map(lambda item: item, newAD))
    
    # Create a variable which is 1 if the tweet is a "live tweet" and 0 if it 
    # happens at another point in the day.
    tempList1=[]
    tempList1 = [row for row in tweetsDF['tweet_time']]
    corTime = [1 if (datetime.time(0, 0, 0) 
                 <= item.time() 
                 <= datetime.time(11, 5, 0)) 
                 else 0 for item in tempList1]
    tweetsDF['live_tweet_ind'] = list(map(lambda item: item, corTime))
    
    # The text of the tweet.
    tweetsDF['text'] = list(map(lambda tweet: tweet['text'], tweetList))
    
    # The hashtags used in the tweet, which I first grab, and then I pull out the 
    # text part of the hashtags into a list of hashtags.
    tweetsDF['hashtags'] = list(map(lambda tweet: tweet['entities']['hashtags'], tweetList))
    htag = []
    htag = [row for row in tweetsDF['hashtags']]
    htag2 = []
    for row in htag:
        tlist = ['#'+item['text'].lower() for item in row if 'text' in item]
        htag2.append(tlist)
    tweetsDF['hashtags'] = list(map(lambda item: item, htag2))
    
    # The handles used in the tweet. First I bring the 'text' of the tweet into 
    # a list. I create a list of lists with each of the words in the tweet. I then grab
    # only the words with a handle. Then, I create a dictionary (rep) of substrings
    # I want to remove from the handles. Using regular expressions I lastly remove
    # all of the substrings that I do not want in the handle.
    
    t1 = [row.split(' ') for row in tweetsDF['text']]
    t3=[]
    for row in t1:
            t2 = [item.replace("'",'').lower() for item in row if '@' in item]
            t3.append(t2)
    t4=[]
    for row in t3:
            rep = {"'":'',':':'','"':'','.':'',"'s":'',"\n":'',",":''}
            rep = dict((re.escape(k), v) for k, v in rep.items())
            pattern = re.compile("|".join(rep.keys()))
            text = [pattern.sub(lambda m: rep[re.escape(m.group(0))], item) 
                    for item in row]
            t4.append(text)
    tweetsDF['handles'] = list(map(lambda item: item, t4))
    
    # The country and city, if available, of the twitter user.
    tweetsDF['country'] = list(map(lambda tweet: tweet['place'], tweetList))
    
    # The language of the tweet.
    tweetsDF['tweet_lang'] = list(map(lambda tweet: tweet['lang'], tweetList))
    
    # The language of the user.
    tweetsDF['user_lang'] = list(map(lambda tweet: tweet['user']['lang'], tweetList))
    
    # The number of followers of the user.
    tweetsDF['num_followers'] = list(map(lambda tweet: tweet['user']['followers_count'], tweetList))
    
    # The time zone of the user, if available.
    tweetsDF['time_zone'] = list(map(lambda tweet: tweet['user']['time_zone'], tweetList))
    
    # The location of the user, if available. This turned out to be worthless.
    tweetsDF['location'] = list(map(lambda tweet: tweet['user']['location'], tweetList))
    
    # Indicator for a US time zone.
    tweetsDF['tz_US'] = tweetsDF.time_zone.map({'Eastern Time (US & Canada)':1, 
                                                'Pacific Time (US & Canada)':1,
                                                'Central Time (US & Canada)':1,
                                                'Mountain Time (US & Canada)':1}) 
    # Indicated if the tweet is a retweet. I originally looked at this to find the
    # meaning behind 'RT' at the beginning of the text of a tweet.
    tweetsDF['retweeted'] = list(map(lambda tweet: tweet['retweeted'], tweetList))
    ##################################################################################
                                                
    
    # Now that I have created my dataframe, I will read in my original list of 
    # hashtags and handles for comparison.
    
    fname2 = r'F:/Python/Data_Science/Project_Data/Final_Data/twitter_work.csv'
    dat = pd.read_csv(fname2,sep=',')
    
    # Make lists of hashtags and handles to keep.
    handleL = [row.lstrip(' ').lower() for row in dat['handle']]
    hTagL = [row.lower() for row in dat['hashtag']]
    
    handle_test = [row for row in tweetsDF['handles']]
    hashtag_test = [row for row in tweetsDF['hashtags']]
    
    # If the hashtags or handles are in one of my lists, then keep the hashtags,
    # otherwise, replace with None.
    for row in handle_test:
        for index, item in enumerate(row):
            if item in handleL:
                row[index]=item
            else:
                row[index]=None
                
    for row in hashtag_test:
        for index, item in enumerate(row):
            if item in hTagL:
                row[index]=item
            else:
                row[index]=None
              
    # Remove the values of None from the lists and add the new lists back to 
    # the original dataframe.
    remove_none_hdle = [list(filter(None.__ne__, row)) for row in handle_test]   
    remove_none_hash = [list(filter(None.__ne__, row)) for row in hashtag_test]
          
    tweetsDF['hashtags'] = list(map(lambda item: item, remove_none_hash))
    tweetsDF['handles'] = list(map(lambda item: item, remove_none_hdle))
    
    # Require that the tweets be in English, in a US time zone, and to be a 
    # live tweet.
    filter1 = tweetsDF[tweetsDF.tweet_lang == 'en']
    filter1 = filter1[filter1.tz_US == 1]
    filter1 = filter1[filter1.live_tweet_ind == 1]
    
    # Drop variables no longer needed and reindex the dataframe.
    filter1.drop(['location','country','tweet_lang','live_tweet_ind',
                  'time_zone','created_at', 'utc_offset','retweeted',
                  'tMonth','tYear'], axis=1, inplace=True)
    filter1 = filter1.reset_index()
    filter1.drop("index",axis=1,inplace=True)
    
    # Remove tweets where at there does not exist at least one hashtag
    # or at least one handle. The reset the index.
    hashfilt = [row for row in filter1['hashtags']]
    hdlefilt = [row for row in filter1['handles']]
    
    hashfiltbool = [True if len(row) > 0 else False for row in hashfilt]
    hdlefiltbool = [True if len(row) > 0 else False for row in hdlefilt]
    
    filter1['hashtags_bool'] = list(map(lambda item: item, hashfiltbool))
    filter1['handles_bool'] = list(map(lambda item: item, hdlefiltbool))
    
    filter1 = filter1[(filter1.hashtags_bool == True) | (filter1.handles_bool == True)]
    filter1 = filter1.reset_index()
    filter1.drop(["index","handles_bool","hashtags_bool"],axis=1,inplace=True)
    
    # Remove tweets where there are multiple TV show hashtags and handles.
    # The largest set which forces this is (Arrow,The Flash) as they share
    # a very similar audience. Then reset the index.
    hashfilt2 = [True if len(row) <= 1 else False for row in filter1['hashtags']]
    hdlefilt2 = [True if len(row) <= 1 else False for row in filter1['handles']]
    
    filter1['mhtag'] = list(map(lambda item: item, hashfilt2))
    filter1['mhand'] = list(map(lambda item: item, hdlefilt2))
    
    filter1 = filter1[(filter1.mhtag) == True & (filter1.mhand == True)]
    filter1.reset_index()
    
    # Combine the hashtags and handles into one entity, as either is a viable
    # variable to create a TV show name. Note frozensets are used to keep the 
    # order in tact. Do this by creating some temporary sets, and then a final
    # variable, show_test, which is the sole identifier to match the program.
    
    set1 = [frozenset(row) for row in filter1['hashtags']]
    set2 = [frozenset(row) for row in filter1['handles']]
    
    set3 = []
    for htag, hand in zip(set1,set2):
        set3.append(htag.union(hand))
        
    set4 = [list(row)[0] for row in set3]
    
    filter1['show_test'] = list(map(lambda item: item, set4))
    filter1.drop(['hashtags','handles','mhtag','mhand'],axis=1,inplace=True)
    
    # Create temporary dataframes to merge in the name of the show so that we 
    # can match the Nielsen household information.
    titleL = [row for row in dat['title']]
    
    sTemp1 = pd.DataFrame({'show_test':hTagL,'title':titleL})
    sTemp2 = pd.DataFrame({'show_test':handleL,'title':titleL})
    
    sTemp3 = sTemp1.append(sTemp2)
    sTemp3.reset_index(inplace=True)
    sTemp3.drop(['index'],axis=1,inplace=True)
    
    filter1 = filter1.merge(sTemp3,how='left',on='show_test')
    refinedTweets = filter1.sort_values(by=['user_id','title'])
    return refinedTweets

