from datetime import datetime
import pytz
import time

#print (datetime.utcnow())
nyc_datetime = datetime.now(pytz.timezone('US/Eastern'))
print (nyc_datetime)

time.sleep(10)
nyc_datetime = datetime.now(pytz.timezone('US/Eastern'))
print(nyc_datetime)




