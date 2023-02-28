import pymongo
import os, sys
import json
import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass
class EnvironmentVariable:
    mongo_db_url:str = os.getenv("MONGO_DB_URL")


env_var = EnvironmentVariable()
mongo_client = pymongo.MongoClient(env_var.mongo_db_url)
print(env_var.mongo_db_url)
TARGET_COLUMN = "expenses"