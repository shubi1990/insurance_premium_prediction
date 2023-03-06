from insurance.entity import config_entity
from insurance.entity import artifact_entity
from insurance.logger import logging
from insurance.exception import InsuranceException
from typing import Optional
from scipy.stats import ks_2samp
import numpy as np
import pandas as pd
import os, sys
from insurance.config import TARGET_COLUMN
from insurance import utils

class DataValidation:
    def __init__(self, data_validation_config:config_entity.DataValidationConfig,
                 data_ingestion_artifact:artifact_entity.DataIngestionArtifact):
        try:
            logging.info(f"{'>>'*20} Data validation {'<<'*20}")
            self.data_validation_config = data_validation_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.validation_eror = dict()
        except Exception as e:
            raise InsuranceException(e, sys)


    def drop_missing_values_columns(self, df:pd.DataFrame, report_key_name:str)->Optional[pd.DataFrame]:
        try:
            threshold = self.data_validation_config.missing_threshold
            null_values = df.isna().sum()/df.shape[0]
            logging.info(f"Selecting column names which contain null values more than {threshold}")
            drop_column_names = null_values[null_values>threshold].index
            logging.info(f"Columns to drop : {list(drop_column_names)}")
            self.validation_eror[report_key_name] = list(drop_column_names)
            df.drop(list(drop_column_names), axis=1, inplace=True)

            #return None if no column left
            if len(df.columns)==0:
                return None
            return df
        except Exception as e:
            raise InsuranceException(e, sys)


    def is_required_columns_exists(self, base_df:pd.DataFrame, current_df:pd.DataFrame, report_key_name:str)->bool:
        try:
            base_columns = base_df.columns
            current_columns = current_df.columns
            missing_columns = []
            for base_column in base_columns:
                if base_column not in current_columns:
                    logging.info(f"Column : {base_column} is not available")
                    missing_columns.append(base_column)
            
            if len(missing_columns)>0:
                self.validation_eror[report_key_name] = missing_columns
                return False
            return True
        except Exception as e:
            raise InsuranceException(e, sys)


    def data_drift(self, base_df:pd.DataFrame, current_df:pd.DataFrame, report_key_name:str):
        try:
            drift_report = dict()
            base_columns = base_df.columns
            current_columns = current_df.columns

            for base_column in base_columns:
                base_data, current_data = base_df[base_column], current_df[base_column]
                # Null hypothesis is base column data and current column data drawn from same distribution

                logging.info(f"Hypoyhesis {base_column} : {base_data.dtype}, {current_data.dtype}")
                distribution = ks_2samp(base_data, current_data)

                if distribution.pvalue>0.05:
                    #accepting null hypothesis
                    drift_report[base_column] = {
                        "pvalue" : float(distribution.pvalue),
                        "same_distribution" : True
                    }
                else:
                    drift_report[base_column] = {
                        "pvalue" : float(distribution.pvalue),
                        "same_distribution" : False
                    }
            self.validation_eror[report_key_name] = drift_report
        except Exception as e:
            raise InsuranceException(e, sys)


    def initiate_data_validation(self)->artifact_entity.DataValidationArtifact:
        try:
            logging.info(f"Reading base dataframe")
            base_df = pd.read_csv(self.data_validation_config.base_file_path)
            logging.info(f"Replacing na values in base dataframe")
            base_df.replace({"na":np.NAN}, inplace=True)
            logging.info(f"Dropping missing values columns from base dataframe")
            base_df = self.drop_missing_values_columns(df=base_df, report_key_name="missing_values_in_base_dataset")

            logging.info(f"Reading train dataframe")
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            logging.info(f"Reading test dataframe")
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            
            logging.info(f"Dropping missing values columns from train dataframe")
            train_df = self.drop_missing_values_columns(df=train_df, report_key_name="missing_values_in_train_dataset")
            logging.info(f"Dropping missing values columns from test dataframe")
            tets_df = self.drop_missing_values_columns(df=test_df, report_key_name="missing_values_in_test_dataset")

            exclude_columns = [TARGET_COLUMN]
            base_df = utils.convert_columns_float(df=base_df, exclude_columns=exclude_columns)
            train_df = utils.convert_columns_float(df=train_df, exclude_columns=exclude_columns)
            test_df = utils.convert_columns_float(df=test_df, exclude_columns=exclude_columns)

            logging.info(f"Is all required columns present in train dataframe")
            train_df_columns_status = self.is_required_columns_exists(base_df=base_df, current_df=train_df, report_key_name="missing_columns_in_train_dataset")
            logging.info(f"Is required columns is present in test dataframe")
            test_df_columns_status = self.is_required_columns_exists(base_df=base_df, current_df=test_df, report_key_name="missing_columns_in_test_dataset")

            if train_df_columns_status:
                logging.info(f"As all columns present in train dataframe hence detecting data drift ")
                self.data_drift(base_df=base_df, current_df=train_df, report_key_name="data_drift_in_train_dataset")
            if test_df_columns_status:
                logging.info(f"As all columns present in test dataframe hence detecting data drift")
                self.data_drift(base_df=base_df, current_df=test_df, report_key_name="data_drift_in_test_dataset")


            #write the report
            logging.info(f"Write report in yaml file")
            utils.write_yaml_file(file_path=self.data_validation_config.report_file_path, data=self.validation_eror)

            #preparing artifact
            data_validation_artifact = artifact_entity.DataValidationArtifact(report_file_path=self.data_validation_config.report_file_path)
            logging.info(f"data_validation_artifact: {data_validation_artifact}")
            return data_validation_artifact

        except Exception as e:
            raise InsuranceException(e, sys)

