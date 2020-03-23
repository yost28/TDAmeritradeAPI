from datetime import datetime
import pytz
import time


client_id =<clientid>
password = <password>
account_number = <account_number>

#print (datetime.utcnow())
nyc_datetime = datetime.now(pytz.timezone('US/Eastern'))
