import time
import urllib
import requests
from datetime import datetime
import pytz
from splinter import Browser
from config import client_id, password, account_number
import pandas as pd
import xlsxwriter
from xlrd import open_workbook

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('/Users/mike/Documents/Daily_Data.xlsx')
worksheet = workbook.add_worksheet()


data_list=[]

executable_path = {'executable_path': r'/Users/mike/Downloads/chromedriver'}

# Create a new instance of the browser, make sure we can see it (Headless = False)
browser = Browser('chrome', **executable_path, headless=False)

method = 'GET'
url = 'https://auth.tdameritrade.com/auth?'
client_code = client_id + '@AMER.OAUTHAP'
payload = {'response_type':'code', 'redirect_uri':'http://localhost', 'client_id':client_code}

# build the URL and store it in a new variable
p = requests.Request(method, url, params=payload).prepare()
myurl = p.url

# go to the URL
browser.visit(myurl)

# define items to fillout form
payload = {'username': account_number,
           'password': password}

# fill out each part of the form and click submit
username = browser.find_by_id("username").first.fill(payload['username'])
password = browser.find_by_id("password").first.fill(payload['password'])
submit   = browser.find_by_id("accept").first.click()

# click the Accept terms button
browser.find_by_id("accept").first.click()

# give it a second, then grab the url
time.sleep(1)
new_url = browser.url

# grab the part we need, and decode it.
parse_url = urllib.parse.unquote(new_url.split('code=')[1])

# close the browser
browser.quit()

# THE AUTHENTICATION ENDPOINT

# define the endpoint
url = r"https://api.tdameritrade.com/v1/oauth2/token"

# define the headers
headers = {"Content-Type":"application/x-www-form-urlencoded"}

# define the payload
payload = {'grant_type': 'authorization_code',
           'access_type': 'offline',
           'code': parse_url,
           'client_id':client_id,
           'redirect_uri':'http://localhost'}

# post the data to get the token
authReply = requests.post(r'https://api.tdameritrade.com/v1/oauth2/token', headers = headers, data=payload)

# convert it to a dictionary
decoded_content = authReply.json()


# grab the access_token
access_token = decoded_content['access_token']
headers = {'Authorization': "Bearer {}".format(access_token)}



# THE DAILY PRICES ENDPOINT

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/pricehistory".format('GOOG')

# define the payload
payload = {'apikey':client_id,
           'periodType':'day',
           'frequencyType':'minute',
           'frequency':'1',
           'period':'2',
           'endDate':'1556158524000',
           'startDate':'1554535854000',
           'needExtendedHoursData':'true'}

# make a request
content = requests.get(url = endpoint, params = payload)

# convert it dictionary object
data = content.json()


# ACCOUNTS ENDPOINT

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/accounts"

# make a request
content = requests.get(url = endpoint, headers = headers)

# convert it dictionary object
data = content.json()

# grab the account id
account_id = data[0]['securitiesAccount']['accountId']

# THE QUOTE ENDPOINT

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/marketdata/{}/quotes".format('GOOG')

# define the payload
payload = {'apikey':client_id}

# make a request
content = requests.get(url = endpoint, params = payload)

# convert it dictionary object
data = content.json()


# THE QUOTES ENDPOINT

# define an endpoint with a stock of your choice, MUST BE UPPER
endpoint = r"https://api.tdameritrade.com/v1/marketdata/quotes"

# define the payload
payload = {'apikey':client_id,
           'symbol':'GOOG,MSFT,AAPL,BYND,SPY,/ES',
            'Authorization': "Bearer {}".format(access_token)
           }
df = pd.DataFrame(columns= ['Current_TimeStamp', 'BidPrice', 'AskPrice', 'BidSize', 'AskSize','LastPrice','LastSize','QuoteTime','TradeTime'])
row =1

while 1:
    try:
# make a request
        content = requests.get(url = endpoint, params = payload)

    # convert it dictionary object
        data = content.json()

        time.sleep(3)
        # print (data)
        # print ("GOOG bid = "+ str((data['GOOG']['bidPrice'])))
        # print ("GOOG ask = "+ str((data['GOOG']['askPrice'])))
        #
        # print ("MSFT bid = "+ str((data['MSFT']['bidPrice'])))
        # print ("MSFT ask = "+ str((data['MSFT']['askPrice'])))
        #
        # print ("AAPL bid = "+ str((data['AAPL']['bidPrice'])))
        # print ("AAPL ask = "+ str((data['AAPL']['askPrice'])))
        # print (data['AAPL']['delayed'])

        print(str(datetime.now(pytz.timezone('US/Eastern')))[:-6])
        print ("SPY bid = "+ str((data['SPY']['bidPrice'])))
        print ("SPY bid size = " + str((data['SPY']['bidSize'])))
        print ("SPY ask = "+ str((data['SPY']['askPrice'])))
        print ("SPY ask size = " + str((data['SPY']['askSize'])))
        print("SPY last price = " + str((data['SPY']['lastPrice'])))
        print("SPY last size = " + str((data['SPY']['lastSize'])))
        quote_time =(data['SPY']['quoteTimeInLong'])/1000
        quote_time = datetime.fromtimestamp(quote_time).strftime('%Y-%m-%d %H:%M:%S.%f')
        print (quote_time)
        trade_time =(data['SPY']['tradeTimeInLong'])/1000
        trade_time = datetime.fromtimestamp(trade_time).strftime('%Y-%m-%d %H:%M:%S.%f')
        print(trade_time)
        worksheet.write(row, 1, str(datetime.now(pytz.timezone('US/Eastern')))[:-6])
        worksheet.write(row, 2, str((data['/ES']['bidPriceInDouble'])))
        worksheet.write(row, 3, str((data['/ES']['bidSizeInLong'])))
        worksheet.write(row, 4, str((data['/ES']['askPriceInDouble'])))
        worksheet.write(row, 5, str((data['/ES']['askSizeInLong'])))
        worksheet.write(row, 6, str((data['/ES']['lastPriceInDouble'])))
        worksheet.write(row, 7, str((data['/ES']['lastSizeInLong'])))
        worksheet.write(row, 8, quote_time)
        worksheet.write(row, 9, trade_time)
        row = row + 1
    except:
        workbook.close()





# SAVED ORDERS ENDPOINT - POST

# define our headers
header = {'Authorization':"Bearer {}".format(access_token),
          "Content-Type":"application/json"}

# define the endpoint for Saved orders, including your account ID
endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/savedorders".format(account_id)

# define the payload, in JSON format
payload = {'orderType':'MARKET',
           'session':'NORMAL',
           'duration':'DAY',
           'orderStrategyType':'SINGLE',
           'orderLegCollection':[{'instruction':'Buy','quantity':1,'instrument':{'symbol':'PINS','assetType':'EQUITY'}}]}


# make a post, NOTE WE'VE CHANGED DATA TO JSON AND ARE USING POST
content = requests.post(url = endpoint, json = payload, headers = header)

# show the status code, we want 200
content.status_code