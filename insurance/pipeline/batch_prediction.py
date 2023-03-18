from insurance.exception import InsuranceException
from insurance.logger import logging
import pandas as pd
import numpy as np
from insurance.predictor import ModelResolver
from insurance.utils import load_object
from datetime import datetime
import os, sys
PREDICTOR_DIR = 'prediction'


def start_batch_prediction(input_file_path):
    try:
        os.makedirs(PREDICTOR_DIR, exist_ok=True)
        logging.info(f'Creating model resolver object')
        model_resolver=ModelResolver(model_registry='saved_models')
        logging.info(f'Reading file : {input_file_path}')
        df=pd.read_csv(input_file_path)
        df.replace({'na' : np.NAN}, inplace=True)

        logging.info(f'Loading transformer to transform dataset')
        transformer=load_object(file_path=model_resolver.get_latest_transformer_path())
        logging.info(f'Loading target encoder  to convert predicted column into categorical')
        target_encoder=load_object(file_path=model_resolver.get_latest_target_encoder_path())

        """We need to create label encoder object for each categorical variable. We will check later"""
        input_feature_name=list(transformer.feature_names_in_)
        for i in input_feature_name:
            if df[i].dtypes == 'O':
                df[i]=target_encoder.fit_transform(df[i])
        input_arr=transformer.transform(df[input_feature_name])

        logging.info(f'Loading model to make prediction')
        model=load_object(file_path=model_resolver.get_latest_model_path())
        prediction=model.predict(input_arr)
        
        df['prediction']=prediction

        prediction_file_name=os.path.basename(input_file_path).replace(".txt",f"{datetime.now().strftime('%m%d%Y__%H%M%S')}.csv")
        prediction_file_path=os.path.join(PREDICTOR_DIR, prediction_file_name)
        df.to_csv(prediction_file_path, index=False, header=True)
        return prediction_file_path

    except Exception as e:
        raise InsuranceException(e, sys)