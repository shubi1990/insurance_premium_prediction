from insurance.entity import config_entity
from insurance.entity import artifact_entity
from insurance.logger import logging
from insurance.exception import InsuranceException
import os, sys
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
import pandas as pd
import numpy as np
from insurance.config import TARGET_COLUMN
from sklearn.preprocessing import LabelEncoder
from insurance import utils




class DataTransformation:
    def __init__(self, data_transformation_config:config_entity.DataTransformationConfig,
        data_ingestion_artifact:artifact_entity.DataIngestionArtifact):

        try:
            logging.info(f"{'>>'*20} Data Transformation {'<<'*20}")
            self.data_transformation_config=data_transformation_config
            self.data_ingestion_artifact=data_ingestion_artifact
        except Exception as e:
            raise InsuranceException(e, sys)

    @classmethod
    def get_data_transformer_object(cls)->Pipeline:
        try:
            simple_imputer = SimpleImputer(strategy='constant', fill_value=0)
            robust_scaler = RobustScaler()
            pipeline = Pipeline(steps=[
                    ('Imputer', simple_imputer),
                    ('scaler', robust_scaler)
            ])
            return pipeline
        except Exception as e:
            raise InsuranceException(e, sys)


    def initiate_data_transformation(self)->artifact_entity.DataTransformationArtifact:
        try:
            #reading training and testing file
            train_df = pd.read_csv(self.data_ingestion_artifact.train_file_path)
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)

            #selecting input feature for train and test dataframe
            input_feature_train_df = train_df.drop(TARGET_COLUMN, axis=1)
            input_feature_test_df = test_df.drop(TARGET_COLUMN, axis=1)

            #selecting target feature for train and test dataframe
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_test_df = test_df[TARGET_COLUMN]

            #converting target feature into array
            target_feature_train_arr = target_feature_train_df.squeeze()
            target_feature_test_arr = target_feature_test_df.squeeze()

            #transformation on categorical columns in input feature dataframe
            label_encoder = LabelEncoder()
            for col in input_feature_train_df.columns:
                if input_feature_test_df[col].dtypes == 'O':
                    input_feature_train_df[col] = label_encoder.fit_transform(input_feature_train_df[col])
                    input_feature_test_df[col] = label_encoder.fit_transform(input_feature_test_df[col])
                else:
                    input_feature_train_df[col] = input_feature_train_df[col]
                    input_feature_test_df[col] = input_feature_test_df[col]

            
            tranformation_pipeline = DataTransformation.get_data_transformer_object()
            tranformation_pipeline.fit(input_feature_train_df)

            input_feature_train_arr = tranformation_pipeline.transform(input_feature_train_df)
            input_feature_test_arr = tranformation_pipeline.transform(input_feature_test_df)

            #target encoder
            train_arr = np.c_[input_feature_train_arr, target_feature_train_arr]
            test_arr = np.c_[input_feature_test_arr, target_feature_test_arr]

            #save numpy array
            utils.save_numpy_array_data(file_path= self.data_transformation_config.transformed_train_path, array=train_arr)
            utils.save_numpy_array_data(file_path= self.data_transformation_config.transformed_test_path, array= test_arr)

            #save transformed objects
            utils.save_object(file_path= self.data_transformation_config.transform_object_path, obj= tranformation_pipeline)
            utils.save_object(file_path= self.data_transformation_config.target_encoder_path, obj= label_encoder)


            data_transformation_artifact = artifact_entity.DataTransformationArtifact(
                transform_object_path=self.data_transformation_config.transform_object_path,
                transformed_train_path=self.data_transformation_config.transformed_train_path,
                transformed_test_path=self.data_transformation_config.transformed_test_path,
                target_encoder_path=self.data_transformation_config.target_encoder_path)

            
            logging.info(f"Data transformation object : {data_transformation_artifact}")
            return data_transformation_artifact
        
        except Exception as e:
            raise InsuranceException(e, sys)





