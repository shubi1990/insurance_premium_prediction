import pandas as pd
import numpy as np
import os, sys
from insurance.logger import logging
from insurance.exception import InsuranceException
from insurance.config import mongo_client
import yaml
import dill

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


def save_object(file_path:str, obj:object)->None:
    try:
        logging.info("Entered the save_object method of utils")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)
        logging.info("Exited the save_object method of utils")
    except Exception as e:
        raise InsuranceException(e, sys)


def load_object(file_path:str)->object:
    try:
        if not os.path.exists(file_path):
            raise Exception(f'The file: {file_path} is not exists')
        with open(file_path, "rb") as file_obj:
            return dill.load(file_obj)
    except Exception as e:
        raise InsuranceException(e, sys)


def save_numpy_array_data(file_path:str, array:np.array):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise InsuranceException(e, sys)


def load_numpy_array_data(file_path:str)->np.array:
    try:
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise InsuranceException(e, sys)
    