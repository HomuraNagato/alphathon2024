
from AlgorithmImports import *
from datetime import datetime
import os

class SaSData(PythonData):
 
  def get_source(self, config: SubscriptionDataConfig, date: datetime, is_live_mode: bool) -> SubscriptionDataSource:
  
    #if is_live_mode:
    #  return SubscriptionDataSource("object_store_references", SubscriptionTransportMedium.OBJECT_STORE)

    source = os.path.join(Globals.DataFolder, "10ks", config.symbol.value.lower() + ".csv")
    return SubscriptionDataSource(source, SubscriptionTransportMedium.LOCAL_FILE)

  def reader(self, config: SubscriptionDataConfig, line: str, date: datetime, is_live_mode: bool) -> BaseData:

    custom = SaSData()
    data = line.split('|')

    custom.symbol = config.symbol
    custom.time = datetime.strptime(data[3], '%Y-%m-%d')
    custom.end_time = custom.time + timedelta(days=1)
    # TODO some rows have empty prices
    try:
      price = float(data[29])
    except:
      price = 0
    #custom.open = price
    #custom.high = price
    #custom.low = price
    custom.close = price
    custom.value = price
    custom.ten_ks = {
      "item_1": data[5],
      "item_1a": data[6],
      "item_7a": data[7]
    }

    return custom

