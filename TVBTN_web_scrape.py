import requests
import pandas as pd
from bs4 import BeautifulSoup
import datetime    
   
# Define a function to loop through the URLs to create a DataFrame
# of the TV shows, their air date/time, their rating/share, and their total viewers.
        
def createHHData(url):
    
    # Turn the page into a Beautiful Soup object to make it easier to read.
    r = requests.get(url)
    b = BeautifulSoup(r.text, "html5lib")
    
    # Read in the table and air date from the web site.
    table = b.find(name='table').find(name='tbody').find_all(name='td')
    date = b.find_all(name="div",attrs={"class":"entry-content"})[0].find_all(name="strong")[1].text[54:].strip('.')
    
    # Create a list of the table values from the HTML.
    tableList = []
    for row in table:
        show = row.text
        tableList.append(show)
    
    # Separate the column names and the values.
    colList = tableList[0:4]
    data = tableList[4:]
    
    # Read the data into a list of lists so that each column has the 
    # proper value, and convert it into a DataFrame.
    dataList = [data[i:i+4] for i in range(0,len(data),4)]
    showsDF= pd.DataFrame(dataList, columns=colList)
    
    # Clean the DataFrame to remove anything unnecessary such as baseball
    # and to add a date column.
    showsDF.rename(columns={'Show':'showP','Adults 18-49 Rating/Share':'rating_share', 'Viewers (000s)':'viewers'}, inplace=True)
    showsDF = showsDF[showsDF.showP != '']
    showsDF['Time'].replace(to_replace='',method='ffill',inplace=True)
    showsDF['rating'] = [row.split('/')[0] for row in showsDF['rating_share']]
    showsDF['share'] = [row.split('/')[1] for row in showsDF['rating_share']]
    showsDF = showsDF[showsDF.showP.str.contains("Football|NFL|The OT|World Series") == False]
    showsDF['week_date'] = date
    showsDF['day'] = [row[0:3] for row in showsDF['week_date']]
    showsDF['prep_date'] = [row.split(',') for row in showsDF['week_date']]
    showsDF['air_date'] = [','.join(row[1:]) for row in showsDF['prep_date']]
    
    # Turn the date variable into a datetime variable by first turning the row into
    # a list, then replace the day of the month with a version that is readable in 
    # datetime.strptime(), then turn the variable into the datetime object and 
    # append back to the original dataFrame.
    tempD = []
    tempD = [row for row in showsDF['air_date']]
    dDate = [row.replace('. ','. 0').lstrip() if len(row) == 13 else row.lstrip() for row in tempD]
    dDate2 = [datetime.datetime.strptime(row, "%b. %d, %Y") for row in dDate]
    showsDF['air_date'] = list(map(lambda row: row, dDate2))
    
    # Just like with the date variable, turn the time variable into a 
    # datetime object for easier manipulation.
    timeD = []
    timeD = [row.replace('.','') for row in showsDF['Time']]
    timeD1 = ['0'+row if row[0] != '1' else row for row in timeD]
    timeD2 = [row.replace(' ',':00 ') if row[2] == ' ' else row for row in timeD1]
    timeD3 = [datetime.datetime.strptime(row, "%I:%M %p") for row in timeD2]
    showsDF['air_time'] = list(map(lambda row: row, timeD3))
    
    showsDF['show_list'] = [row.split(' (') for row in showsDF['showP']]
    showsDF['show'] = [row[0] for row in showsDF['show_list']]
    showsDF['network'] = [row[1].split(')')[0] for row in showsDF['show_list']]
    showsDF['viewers'] = [float(row) for row in showsDF['viewers']]
    showsDF['rating'] = [float(row) for row in showsDF['rating']]
    showsDF['share'] = [float(row) for row in showsDF['share']]    
    showsDF.drop(['Time','prep_date','week_date','show_list','showP','rating_share'],axis=1,inplace=True)
    return showsDF
    

        