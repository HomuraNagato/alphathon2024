
from AlgorithmImports import *

from datetime import datetime
import os

class SaSData(PythonData):
 
  def get_source(self, config: SubscriptionDataConfig, date: datetime, is_live_mode: bool) -> SubscriptionDataSource:
  
    #if is_live_mode:
    #  return SubscriptionDataSource("object_store_references", SubscriptionTransportMedium.OBJECT_STORE)

    source = os.path.join(Globals.DataFolder, "sp500_symbols", config.symbol.value.lower() + ".csv")
    return SubscriptionDataSource(source, SubscriptionTransportMedium.LOCAL_FILE)

  def reader(self, config: SubscriptionDataConfig, line: str, date: datetime, is_live_mode: bool) -> BaseData:

    custom = SaSData()
    data = line.split(',')

    custom.symbol = config.symbol
    custom.time = datetime.strptime(data[0], '%Y-%m-%d')
    custom.end_time = custom.time + timedelta(days=1)
    # TODO some rows have empty prices
    try:
      price = float(data[5])
    except:
      price = 0
    custom.open = price
    custom.high = price
    custom.low = price
    custom.close = price
    custom.value = price

    return custom

class TenKData(PythonData):

  def get_source(self, config: SubscriptionDataConfig, date: datetime, is_live_mode: bool) -> SubscriptionDataSource:
  
    source = os.path.join(Globals.DataFolder, "10ks", config.symbol.value.lower() + ".csv")
    return SubscriptionDataSource(source, SubscriptionTransportMedium.LOCAL_FILE)

  def reader(self, config: SubscriptionDataConfig, line: str, date: datetime, is_live_mode: bool) -> BaseData:

    custom = TenKData()
    data = line.split(',')

    custom.symbol = config.symbol
    custom.time = datetime.strptime(data[0], '%Y%m%d')
    custom.end_time = custom.time + timedelta(days=1)
    # TODO some rows have empty prices
    try:
      price = float(data[5])
    except:
      price = 0
    custom.open = price
    custom.high = price
    custom.low = price
    custom.close = price
    custom.value = price

    return custom

