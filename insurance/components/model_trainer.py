from insurance.entity import config_entity
from insurance.entity import artifact_entity
from insurance.logger import logging
from insurance.exception import InsuranceException
import os, sys
from sklearn.linear_model import LinearRegression
from insurance import utils
from sklearn.metrics import r2_score




class ModelTrainer:
    def __init__(self, model_trainer_config:config_entity.ModelTrainerConfig,
                data_transformation_artifact:artifact_entity.DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact= data_transformation_artifact
        except Exception as e:
            raise InsuranceException(e, sys)


    def train_model(self, X, y):
        try:
            lr = LinearRegression()
            lr.fit(X, y)
            return lr
        except Exception as e:
            raise InsuranceException(e, sys)


    def initiate_model_trainer(self,)->artifact_entity.ModelTrainerArtifact:
        try:
            logging.info(f'Loading train and test array')
            train_arr = utils.load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_train_path)
            test_arr = utils.load_numpy_array_data(file_path=self.data_transformation_artifact.transformed_test_path)

            logging.info(f'Splitting input and target feature from both train and test array. ')
            x_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            x_test, y_test = test_arr[:, :-1], test_arr[:, -1]

            logging.info(f'Train the model')
            model = self.train_model(X=x_train, y=y_train)

            logging.info(f'Calculating r2 score for training data')
            yhat_train = model.predict(x_train)
            r2_train_score =  r2_score(y_true=y_train, y_pred=yhat_train)

            logging.info(f'Calculating r2 score for test data')
            yhat_test = model.predict(x_test)
            r2_test_score =  r2_score(y_true=y_test, y_pred=yhat_test)

            logging.info(f'train score : {r2_train_score} and test score : {r2_test_score}')
            logging.info(f'Checking if our model is underfitted or not')
            if r2_test_score < self.model_trainer_config.expected_score:
                raise Exception(f'Model is not good as itis not able to give \
                    expected accuracy : {self.model_trainer_config.expected_score}, model actual score : {r2_test_score}')

            logging.info(f'Checking if our model is overfitted or not')
            diff = abs(r2_train_score-r2_test_score)
            if diff > self.model_trainer_config.overfitting_threshold:
                raise Exception(f'Train and test score difference : {diff} is more than overfitting threshold : {self.model_trainer_config.overfitting_threshold}')

            logging.info(f'Saving model object')
            utils.save_object(file_path=self.model_trainer_config.model_path, obj=model)

            logging.info(f'Preparing the artifact')
            model_trainer_artifact = artifact_entity.ModelTrainerArtifact(model_path=self.model_trainer_config.model_path,
            r2_train_score=r2_train_score, r2_test_score=r2_test_score)

            logging.info(f'Model trainer artifact : {model_trainer_artifact}')
            return model_trainer_artifact

        except Exception as e:
            raise InsuranceException(e, sys)