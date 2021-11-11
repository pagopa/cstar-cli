import psycopg2
import psycopg2.extras

import pandas as pd
import pandas.io.sql as psql
import random
from datetime import timedelta, datetime, date
import string
from .constants import  CITIZEN_RANKING_EXT_SCHEMA


class Awardwinner() :
  def __init__(self, args): 
    self.args = args
    self.db_connection = psycopg2.connect(args.connection_string)
  
  def create_winners(self):
    print("Winners")