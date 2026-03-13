# Automated Machine Learning

Essentially it creates experiments that run different algorithms within the Azure ML Service and execute hyperparameter tuning, at the same time to select the best fitting model to the situation.

AutoML gives data scientists a tool to run automatically a bunch of algorithms in seconds and evaluate performance to select the best one. What a data scientist usually does is to first, choose an algorithm, then execute and try to obtain the best hyper parameter and finally, repeat the process with a different algorithm. The whole idea is to keep doing that but in automatic with auto ML.

## Choose task

Depending on the problem Auto ML supports a specific numbers of algorithm to do some experimentation.

![alt text](./pics/image-9.png)

## Requirements

Remember that a MLTable store a schema to the tables

``Environment's requirements``

 * Need to create data assets to the datastore
 * Requires tabular data
 * **requires a MLTable**: Store the data in the same folder and the MLTable file as well
  
``Python requirements``

```python
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml import Input

my_training_data_input = Input(
    type=AssetTypes.MLTABLE,
    path='azureml:input-data-automl:1'
)
```

> **DP-100 Exam Tip**: AutoML supports these task types: **Classification**, **Regression**, **Time-series Forecasting**, **Computer Vision** (image classification, object detection, instance segmentation), and **NLP** (text classification, named entity recognition). Each task type has specific primary metrics.

### Scaling and normalization

AutoML applies scaling and normalization so we don't have any large scale feature dominating the features. It also applies some of these transformations to the data:

 * Missing value imputation or elimination of null values
 * Categorical encoding to convert text into numbers
 * Dropping high cardinality features such as ID records
 * Feature engineering: deriving individual date parts from DateFeatures
  
We could have control on which of these functionalities we want and activate it or not BUT **they aren't customizable at all**.  If you want to do an specific feature within the preprocessing, do it before this task is executed and the select which one could actually benefit the process, different that what we already have done.

## Find the best classification model  - DEMO

To create an AutoML job is quite simple. Just go to the "Auto ML" section on the left menu within Azure ML Studio. There you will find all AutoML displayed and the option to "New Automated ML job". Click there. 

Now, it is important to select an appropriate data type to the selected problem. When creating the auto ML job it could be selected the "Task type" and this is, which ML problem are we facing? A regression problem? A clustering? For this exercise we will select a Classification problem. Below, the usable data is showed and you can click it to double check the data.

![Auto ML Job creation](./pics/image-10.png)


### Task Settings tab

After that, we could select the target column (the one we want to predict). TO this example the diabetes Column will be the one selected.

 * in the `View additional configuration` button you will see some important configuration such as the Primary metric used to rank all possible models (AUCWeighted, Accuracy, NormMacroRecall, AveragePrecisionScoreWeighted, PrecisionScoreWeighted)
 * Another interesting feature (which is disabled by default) is to enable the ensemble stacking option which will use multiple models to stack predictions (LOOK DEEPER INTO THIS!!)
 * Use supported models: Basically is an option to not use some models. On the list below will appear a list of models. If you select a model and activate this option, it will use all possible models BUT if you do not select this option, we can manually select which models we want to use. `For this demo we could use LogisticRegression, SVM, KNN, DecisionTree` BUT we will use all of them.
 * View featurization settings: In this case you will basically select how the system should behave with the features one by one, what to do with it, how to fill blanks, how to treat high cardinality? By default you could leave it in "Auto" which automatically will select the best option for it
 * Limits option: We could limit compute power used for the AutoML job. 
 * Validating data: We could use cross validation of course and we could select which cross validation we want to use. We could also select the validation data with new data or the train-test split method. 
  
 * **Compute task**

     Here we will select the compute type that will be used. Remember that jobs require a compute cluster.  We can configure here the Priority of the task and how much resources it will take to train this model. By default is just fine 

Now, after all configurations are done, the job will be executed and keep in mind that the AutoML job is going to be a "Parent job" of very different children jobs and create different jobs for all models and figure out the best one based on all possible jobs run. 

## Same demo with Python SDK

To watch the entire notebook with a deeper explanation of how to use auto ML with Azure in Python go to [this file]("./labs/3 Classification with Automated Machine Learning.ipynb"). Here we will look at the most important commands to have in mind.

Remember to run the commands to verify access to AzureML workspace and data. Those are:

```python
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.ml import MLClient

try:
    credential = DefaultAzureCredential()
    # Check if given credential can get token successfully.
    credential.get_token("https://management.azure.com/.default")
except Exception as ex:
    # Fall back to InteractiveBrowserCredential in case DefaultAzureCredential not work
    credential = InteractiveBrowserCredential()

# Get a handle to workspace
ml_client = MLClient.from_config(credential=credential)
```
After these validations are done, we can proceed. The idea to create an AutoML job via Python is the same as the CLI in Azure Portal. 

from azure.ai.ml.constants import AssetTypes
from azure.ai.ml import Input

```python

# creates a dataset based on the files in the local data folder
my_training_data_input = Input(type=AssetTypes.MLTABLE, path="azureml:diabetes-training:1")
```

```output
# This uploads the MLTable to the local environment
```

```python
from azure.ai.ml import automl

# configure the classification job
classification_job = automl.classification(
    compute="aml-cluster",
    experiment_name="auto-ml-class-dev",
    training_data=my_training_data_input,
    target_column_name="Diabetic",
    primary_metric="accuracy",
    n_cross_validations=5,
    enable_model_explainability=True
)

# set the limits (optional)
classification_job.set_limits(
    timeout_minutes=60, 
    trial_timeout_minutes=20, 
    max_trials=5,
    enable_early_termination=True,
)

# set the training properties (optional)
classification_job.set_training(
    blocked_training_algorithms=["LogisticRegression"], 
    enable_onnx_compatible_models=True
)
```


```python
# Submit the AutoML job
returned_job = ml_client.jobs.create_or_update(
    classification_job
)  

# submit the job to the backend
aml_url = returned_job.studio_url
print("Monitor your job at", aml_url)
```

```output
# And URL with the job itself
```

### Setting limits

One important thing is to create limits to the whole autoML process. With this we could control resource consuming

```python
classification_job.set_limits(
    timeout_minutes = 60, # Number of minutes after which the autoML process will be terminated
    trial_timeout_minutes = 20, # max minutes of a trial can take
    max_trials = 5, # max number of trials or models to be used
    enable_early_termination = True # in case the experiment's score isn't improving in the short term 
)
```

## Reviewing results

After jobs are done we could actually look into the possible results of the autoML process. Just simply go to the "Jobs" tab and there you will be able to see all possible jobs. There will appear the child job and it will include a tag to see "the best job".

Inside job tab go to the "Models and child jobs" to look deeper into the trained models within each job. Then look into the best job and go to the explanation of the model. Here you will find some info regarding the model itself and its performance


### Experiments 

We can group models used in different environments/jobs with a "tag" that we will call "experiments" so, when we see an experiment we will review all the models that have that "tag".

Now to track models outside the Azure ML environment we could use the **MLflow** package. That is an open source library that allows tracking and logging everything about a model we're training into the Azure ML service with its parameters, metrics and artifacts.

To use MLFlow we need to install some libraries and do some preparations

 - install `mlflow` and `azureml-mlflow` packages
 - Get the value to the MLflow URI we are tracking from the Azure portal (Inside the task/job ion the overview page we could find the URI)
 - Use the following code inside the local machine to point to that. 

```python
mlflow.set_tracking_uri("MLFLOW-TRACKING-URI")
```

> **DP-100 Note**: When running inside an Azure ML job, the MLflow tracking URI is set **automatically** — no manual setup needed. You only need `mlflow.set_tracking_uri()` when running from a **local machine** or **external notebook**. For the full guide on MLflow, see [9 MLflow comprehensive guide](./9%20MLflow%20comprehensive%20guide.md).

**``NOTE: THIS TOPIC WILL BE STUDIED DEEPER IN NEXT DOCUMENTS``**
