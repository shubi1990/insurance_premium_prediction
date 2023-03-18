from insurance.entity import config_entity
from insurance.entity import artifact_entity
from insurance.exception import InsuranceException
from insurance.logger import logging
from insurance.predictor import ModelResolver
from insurance.utils import load_object
import os, sys
import pandas as pd
from insurance.config import TARGET_COLUMN
from sklearn.metrics import r2_score


class ModelEvaluation:
    def __init__(self,
                model_evaluation_config=config_entity.ModelEvaluationConfig,
                data_ingestion_artifact=artifact_entity.DataIngestionArtifact,
                data_transformation_artifact=artifact_entity.DataTransformationArtifact,
                model_trainer_artifact=artifact_entity.ModelTrainerArtifact):
        try:
            logging.info(f"{'>>'*20} Model Evaluation {'<<'*20}")
            self.model_evaluation_config=model_evaluation_config
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_transformation_artifact=data_transformation_artifact
            self.model_trainer_artifact=model_trainer_artifact
            self.model_resolver=ModelResolver()
        except Exception as e:
            raise InsuranceException(e, sys)


    def initiate_model_evaluation(self,)->artifact_entity.ModelEvaluationArtifact:
        try:
            logging.info(f'If saved model folder has model then we will compare which model is best, trained or model from saved model folder ')
            latest_dir_path = self.model_resolver.get_latest_dir_path()
            if latest_dir_path==None:
                model_evaluation_artifact=artifact_entity.ModelEvaluationArtifact(is_model_accepted=True, improved_accuracy=None)
                logging.info(f'Model Evaluation Artifact : {model_evaluation_artifact}')
                return model_evaluation_artifact


            logging.info(f'Finding path of previous transformer, model and encoder')
            transformer_path=self.model_resolver.get_latest_transformer_path()
            model_path=self.model_resolver.get_latest_model_path()
            target_encoder_path=self.model_resolver.get_latest_target_encoder_path()

            logging.info(f'Previous trained object of transformer, model and target encoder')
            transformer=load_object(file_path=transformer_path)
            model=load_object(file_path=model_path)
            target_encoder=load_object(file_path=target_encoder_path)

            logging.info(f'Currently trained model objects')
            current_transformer=load_object(file_path=self.data_transformation_artifact.transform_object_path)
            current_model=load_object(file_path=self.model_trainer_artifact.model_path)
            current_target_encoder=load_object(file_path=self.data_transformation_artifact.target_encoder_path)

            test_df=pd.read_csv(self.data_ingestion_artifact.test_file_path)
            target_df=test_df[TARGET_COLUMN]
            y_true=target_df

            input_feature_name=list(transformer.feature_names_in_)
            for i in input_feature_name:
                if test_df[i].dtypes == 'O':
                    test_df[i]=target_encoder.fit_transform(test_df[i])

            input_arr=transformer.transform(test_df[input_feature_name])
            y_pred=model.predict(input_arr)
            previous_model_score=r2_score(y_true=y_true, y_pred=y_pred)
            logging.info(f'Accuracy for previous trained model : {previous_model_score}')


            input_feature_name=list(current_transformer.feature_names_in_)
            input_arr=current_transformer.transform(test_df[input_feature_name]) 
            y_pred=current_model.predict(input_arr)
            current_model_score=r2_score(y_true=y_true, y_pred=y_pred)
            logging.info(f'Accuracy for current trained model : {current_model_score}')  

            if current_model_score<=previous_model_score:
                logging.info(f'Current model is not better than previous one')
                raise Exception('Current model is not better than previous one')      

            model_evaluation_artifact=artifact_entity.ModelEvaluationArtifact(is_model_accepted=True, improved_accuracy=current_model_score-previous_model_score)
            logging.info(f'Model Evaluation Artifact : {model_evaluation_artifact}')  
            return model_evaluation_artifact

        except Exception as e:
            raise InsuranceException(e, sys)