import pandas as pd
import numpy as np
import os, sys
from insurance.logger import logging
from insurance.exception import InsuranceException
from insurance.config import mongo_client
import yaml

def get_collection_as_dataframe(database_name:str, collection_name:str)->pd.DataFrame:
    try:
        logging.info(f"Reading data from database : {database_name} and collection : {collection_name}")
        df = pd.DataFrame(list(mongo_client[database_name][collection_name].find()))
        logging.info(f"found columns : {df.columns}")
        if "_id" in df.columns:
            logging.info("Dropping column : _id")
            df = df.drop("_id", axis=1)
        logging.info(f"Rows and columns in df : {df.shape}")
        return df
    except Exception as e:
        raise InsuranceException(e, sys)


def convert_columns_float(df:pd.DataFrame, exclude_columns:list)->pd.DataFrame:
    try:
        for column in df.columns:
            if (column not in exclude_columns) and (df[column].dtypes != 'O'):
                df[column] = df[column].astype('float')
        return df
    except Exception as e:
        raise InsuranceException(e, sys)


def write_yaml_file(file_path, data:dict):
    try:
        file_dir = os.path.dirname(file_path)
        os.makedirs(file_dir, exist_ok=True)
        with open(file_path, "w") as file_writer:
            yaml.dump(data, file_writer)
    except Exception as e:
        raise InsuranceException(e, sys)