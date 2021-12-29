from hashlib import sha256
import pandas as pd

class Transactionfilter():
  """Utilities related to the rtd-ms-transaction-filter service, a.k.a. Batch Acquirer"""
  
  def __init__(self, args):
    self.args = args
    
  def synthetic_hashpans(self):
    """Produces a synthetic version of the CSV file obtainable from the RTD /hashed-pans endpoint"""
    synthetic_pans = [f"{self.args.hashpans_prefix}{i}" for i in range(self.args.hashpans_qty)]
    hpans = [sha256(f"{pan}{self.args.salt}".encode()).hexdigest() for pan in synthetic_pans]
    hashpans_df = pd.DataFrame(hpans, columns = ["hashed_pan"])
    print(hashpans_df.to_csv(index=False, header=False, sep=";"))