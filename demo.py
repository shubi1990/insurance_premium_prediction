from insurance.pipeline.batch_prediction import start_batch_prediction
from insurance.pipeline.training_pipeline import start_training_pipeline

#file_path='G:\Learning\Project_making\insurance_premium_prediction\insurance_premium_prediction\insurance.txt'

if __name__ == "__main__":
    try:
        #output=start_batch_prediction(input_file_path=file_path)
        output=start_training_pipeline()
        print(output)
    except Exception as e:
       print(e) 