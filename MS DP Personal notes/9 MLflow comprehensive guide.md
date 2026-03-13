# MLflow - Comprehensive Guide for DP-100

MLflow is an **open-source platform** for managing the end-to-end machine learning lifecycle. Azure Machine Learning **natively integrates** with MLflow, making it the recommended way to track experiments, log models, and manage the ML lifecycle within Azure ML.

---

## 1. What is MLflow?

MLflow has four main components:

| Component | Purpose |
|---|---|
| **MLflow Tracking** | Log parameters, metrics, artifacts, and models during training |
| **MLflow Models** | Package ML models in a standard format for deployment |
| **MLflow Model Registry** | Centralized model store for versioning and stage transitions |
| **MLflow Projects** | Packaging format for reproducible runs (less relevant in Azure ML) |

For DP-100, the focus is on **Tracking**, **Models**, and the **Model Registry**.

---

## 2. MLflow Tracking

MLflow Tracking is a logging API that records **parameters**, **metrics**, **artifacts**, and **models** during training runs. Azure ML **automatically configures MLflow tracking** when you run a job inside an Azure ML workspace — no extra setup needed.

### 2.1 Key Concepts

- **Experiment**: A named grouping of runs (e.g., `diabetes-classification`)
- **Run**: A single execution of training code. Each run logs its own params/metrics/artifacts
- **Artifact**: Any output file (model files, images, data files)
- **Parameter**: Input configuration values (learning rate, regularization, etc.)
- **Metric**: Numeric performance values (accuracy, loss, AUC, etc.)

### 2.2 Setting Up MLflow in Azure ML

When running **inside** an Azure ML job, MLflow tracking URI is set **automatically**. When running from a **local machine or notebook**, you must set it yourself:

```python
import mlflow

# Option 1: Get tracking URI from MLClient
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id="<sub-id>",
    resource_group_name="<rg>",
    workspace_name="<ws>"
)

mlflow_tracking_uri = ml_client.workspaces.get(ml_client.workspace_name).mlflow_tracking_uri
mlflow.set_tracking_uri(mlflow_tracking_uri)
```

```python
# Option 2: Set URI directly
azureml_tracking_uri = "azureml://<region>.api.azureml.ms/mlflow/v1.0/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/workspaces/<ws>"
mlflow.set_tracking_uri(azureml_tracking_uri)
```

> **Exam tip**: If asked how to connect MLflow to Azure ML from a local environment, the answer is `mlflow.set_tracking_uri()` using the workspace's MLflow tracking URI.

### 2.3 Creating and Setting Experiments

```python
# Create/set an experiment
mlflow.set_experiment("diabetes-experiment")

# Or get experiment by name
experiment = mlflow.get_experiment_by_name("diabetes-experiment")
print(experiment.experiment_id)
```

### 2.4 Starting and Managing Runs

```python
# Basic run
with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_metric("accuracy", 0.95)

# Named run
with mlflow.start_run(run_name="lr-experiment-01"):
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_metric("accuracy", 0.95)

# Nested runs (child runs)
with mlflow.start_run(run_name="parent-run"):
    mlflow.log_param("approach", "grid-search")
    
    for lr in [0.01, 0.1, 1.0]:
        with mlflow.start_run(nested=True, run_name=f"child-lr-{lr}"):
            mlflow.log_param("learning_rate", lr)
            mlflow.log_metric("accuracy", 0.90 + lr * 0.01)
```

> **Exam tip**: `nested=True` creates child runs. This is useful for hyperparameter sweeps.

---

## 3. Logging with MLflow

### 3.1 Logging Parameters

Parameters are **input values** to your training (hyperparameters, data paths, etc.).

```python
# Single parameter
mlflow.log_param("reg_rate", 0.1)
mlflow.log_param("n_estimators", 100)

# Multiple parameters at once
mlflow.log_params({
    "reg_rate": 0.1,
    "n_estimators": 100,
    "max_depth": 5
})
```

### 3.2 Logging Metrics

Metrics are **output values** — performance indicators.

```python
# Single metric
mlflow.log_metric("accuracy", 0.95)
mlflow.log_metric("auc", 0.97)

# Log metric at a step (for iterative training)
for epoch in range(100):
    loss = train_one_epoch()
    mlflow.log_metric("loss", loss, step=epoch)

# Multiple metrics at once
mlflow.log_metrics({
    "accuracy": 0.95,
    "precision": 0.93,
    "recall": 0.91,
    "f1_score": 0.92
})
```

> **Exam tip**: `log_metric` with `step` parameter is used for logging metrics over time (like training loss per epoch). This is how you get those nice charts in Azure ML Studio.

### 3.3 Logging Artifacts

Artifacts are **output files** — images, data files, or any file you want to save.

```python
# Log a single file
mlflow.log_artifact("confusion_matrix.png")

# Log all files in a directory
mlflow.log_artifacts("./outputs/plots", artifact_path="plots")

# Log a text artifact
mlflow.log_text("This is a note about the run", "notes.txt")

# Log a dictionary as JSON
mlflow.log_dict({"threshold": 0.5, "classes": ["positive", "negative"]}, "config.json")

# Log an image
mlflow.log_image(image_array, "prediction_sample.png")

# Log a figure (matplotlib)
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])
mlflow.log_figure(fig, "training_curve.png")
```

### 3.4 Logging Tables

```python
import pandas as pd

# Log a pandas dataframe as a table
results_df = pd.DataFrame({"predicted": [1, 0, 1], "actual": [1, 1, 1]})
mlflow.log_table(results_df, artifact_file="predictions.json")
```

---

## 4. Autologging

This is probably the **most important feature** for DP-100. Autologging automatically captures parameters, metrics, and model artifacts without writing explicit log statements.

### 4.1 Generic Autolog

```python
# Logs everything automatically for supported frameworks
mlflow.autolog()

# With configuration
mlflow.autolog(
    log_input_examples=True,     # Log sample input
    log_model_signatures=True,   # Log input/output schema
    log_models=True,             # Log the trained model
    disable=False,               # Enable/disable
    exclusive=False,             # If True, only autolog (ignore manual logs)
    silent=True                  # Suppress warnings
)
```

### 4.2 Framework-Specific Autologging

Each ML framework has its own autolog function that captures framework-specific information:

```python
# Scikit-learn
mlflow.sklearn.autolog()
# Logs: parameters, metrics (training & validation scores), model, 
#        pipeline visualizations, feature importances

# XGBoost
mlflow.xgboost.autolog()
# Logs: parameters, metrics, feature importances, model

# LightGBM
mlflow.lightgbm.autolog()

# TensorFlow/Keras
mlflow.tensorflow.autolog()
# Logs: parameters, metrics per epoch, model

# PyTorch
mlflow.pytorch.autolog()

# Spark ML
mlflow.spark.autolog()
```

> **Exam tip**: `mlflow.autolog()` works for **any supported framework** and auto-detects it. `mlflow.sklearn.autolog()` is **framework-specific** and captures more detailed info for scikit-learn. The exam may ask you which one captures more detail — the framework-specific one.

### 4.3 What Does Autolog Capture for Scikit-Learn?

| What | Example |
|---|---|
| **Parameters** | `C=1.0`, `max_iter=100`, `solver='lbfgs'` |
| **Metrics** | `training_score`, `training_accuracy_score` |
| **Artifacts** | Model file, pipeline visualization |
| **Tags** | `estimator_name`, `estimator_class` |
| **Model** | Serialized model with signature |

### 4.4 Combining Autolog with Manual Logging

```python
mlflow.autolog()

with mlflow.start_run():
    model = LogisticRegression(C=1.0).fit(X_train, y_train)
    
    # Autolog already captured params, metrics, model
    # But we can add MORE manually:
    mlflow.log_metric("custom_metric", calculate_custom(model, X_test, y_test))
    mlflow.log_artifact("custom_report.html")
```

---

## 5. MLflow Models

### 5.1 Model Flavors

A **flavor** defines the framework-specific format of the model. This is critical for deployment because Azure ML uses the flavor to know how to load and serve the model.

Supported flavors include:

| Flavor | Function |
|---|---|
| `mlflow.sklearn` | Scikit-learn models |
| `mlflow.xgboost` | XGBoost models |
| `mlflow.lightgbm` | LightGBM models |
| `mlflow.tensorflow` | TensorFlow/Keras |
| `mlflow.pytorch` | PyTorch models |
| `mlflow.spark` | Spark MLlib models |
| `mlflow.onnx` | ONNX format |
| `mlflow.pyfunc` | Generic Python function (custom models) |

### 5.2 Logging Models vs Artifacts

This is a **critical distinction** for the exam:

| | `log_model` | `log_artifact` |
|---|---|---|
| Creates MLmodel file | Yes | No |
| Includes signature | Yes (optional) | No |
| Includes flavor info | Yes | No |
| Can be registered directly | Yes | No |
| Can be deployed directly | Yes | No (needs wrapping) |
| Tracking | Full model tracking | Just a file |

```python
# Log as MODEL (preferred for deployment)
mlflow.sklearn.log_model(model, artifact_path="model")

# Log as ARTIFACT (just a file)
import joblib
joblib.dump(model, "model.pkl")
mlflow.log_artifact("model.pkl")
```

> **Exam tip**: If you want to deploy a model to an endpoint, log it with `log_model`, NOT `log_artifact`. Only `log_model` creates the MLmodel metadata file needed for deployment.

### 5.3 The MLmodel File

When you use `log_model`, MLflow creates an `MLmodel` file with metadata:

```yaml
artifact_path: model
flavors:
  python_function:
    env: conda.yaml
    loader_module: mlflow.sklearn
    model_path: model.pkl
    python_version: 3.8.10
  sklearn:
    code: null
    pickled_model: model.pkl
    serialization_format: cloudpickle
    sklearn_version: 1.0.2
model_uuid: abc123-def456
run_id: run_abc123
signature:
  inputs: '[{"name": "feature1", "type": "double"}, {"name": "feature2", "type": "double"}]'
  outputs: '[{"type": "long"}]'
```

Key fields:
- **artifact_path**: Where the model is stored within the run
- **flavors**: Framework info (every model has a `python_function` flavor + its native flavor)
- **signature**: Input/output schema
- **run_id**: Links back to the training run

### 5.4 Model Signature

The signature specifies the **schema of inputs and outputs**. This is important for validation at inference time.

```python
from mlflow.models.signature import infer_signature, ModelSignature
from mlflow.types.schema import Schema, ColSpec

# Option 1: Infer from data (MOST COMMON)
signature = infer_signature(X_train, model.predict(X_train))
mlflow.sklearn.log_model(model, "model", signature=signature)

# Option 2: Define manually
input_schema = Schema([
    ColSpec("double", "feature1"),
    ColSpec("double", "feature2"),
    ColSpec("long", "feature3"),
])
output_schema = Schema([ColSpec("long")])
signature = ModelSignature(inputs=input_schema, outputs=output_schema)
mlflow.sklearn.log_model(model, "model", signature=signature)
```

> **Exam tip**: `infer_signature(X_train, model.predict(X_train))` is the standard way to create a signature. It needs both input data AND prediction output.

### 5.5 Input Examples

```python
# Log model with an input example
input_example = X_train[:5]  # First 5 rows
mlflow.sklearn.log_model(model, "model", 
                          signature=signature,
                          input_example=input_example)
```

### 5.6 Custom Models with `pyfunc`

When your model doesn't fit a standard flavor, use `pyfunc`:

```python
import mlflow.pyfunc

class CustomModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        # Load model artifacts
        import joblib
        self.model = joblib.load(context.artifacts["model_path"])
        self.threshold = 0.5
    
    def predict(self, context, model_input):
        probabilities = self.model.predict_proba(model_input)
        return (probabilities[:, 1] >= self.threshold).astype(int)

# Log the custom model
artifacts = {"model_path": "model.pkl"}
mlflow.pyfunc.log_model(
    artifact_path="custom_model",
    python_model=CustomModel(),
    artifacts=artifacts,
    signature=signature
)
```

---

## 6. Model Registry in Azure ML

The Model Registry is where you **register, version, and manage** models before deployment.

### 6.1 Registering Models from Runs

```python
# Option 1: Register from a run URI
model_uri = f"runs:/{run_id}/model"
mlflow.register_model(model_uri, "diabetes-classifier")

# Option 2: Register during logging
with mlflow.start_run():
    mlflow.sklearn.log_model(model, "model", 
                              registered_model_name="diabetes-classifier")

# Option 3: Using Azure ML SDK v2
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes

mlflow_model = Model(
    path=f"azureml://jobs/{run_id}/outputs/artifacts/paths/model/",
    type=AssetTypes.MLFLOW_MODEL,
    name="diabetes-classifier",
    description="Logistic regression for diabetes prediction"
)
ml_client.models.create_or_update(mlflow_model)
```

### 6.2 Model Versions

Each time you register a model with the same name, the version auto-increments:

```python
# List model versions
from mlflow.tracking import MlflowClient

client = MlflowClient()
for mv in client.search_model_versions("name='diabetes-classifier'"):
    print(f"Version: {mv.version}, Stage: {mv.current_stage}, Run ID: {mv.run_id}")
```

### 6.3 Model Stages (Classic MLflow)

MLflow supports stages: `None` → `Staging` → `Production` → `Archived`

```python
client = MlflowClient()
# Transition model version to a stage
client.transition_model_version_stage(
    name="diabetes-classifier",
    version=1,
    stage="Production"
)

# Load model by stage
model = mlflow.pyfunc.load_model("models:/diabetes-classifier/Production")
```

> **Note**: Azure ML uses its own model registry with versions rather than MLflow stages. Both approaches work, but the exam typically focuses on the Azure ML SDK approach for registration.

---

## 7. Loading and Using Models

### 7.1 Loading Models

```python
# From a run
model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")

# From the registry (by version)
model = mlflow.pyfunc.load_model("models:/diabetes-classifier/1")

# From the registry (by stage)
model = mlflow.pyfunc.load_model("models:/diabetes-classifier/Production")

# From a local path
model = mlflow.sklearn.load_model("./mlruns/0/abc123/artifacts/model")
```

### 7.2 Predict with Loaded Models

```python
# Using pyfunc (generic, works for any flavor)
model = mlflow.pyfunc.load_model(model_uri)
predictions = model.predict(X_test)

# Using native flavor (sklearn-specific methods available)
model = mlflow.sklearn.load_model(model_uri)
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)  # sklearn-specific
```

> **Exam tip**: `pyfunc.load_model` returns a generic wrapper. `sklearn.load_model` returns the native sklearn model with all its methods.

---

## 8. Querying and Searching Runs

### 8.1 Search Runs

```python
import mlflow

# Search all runs in an experiment
runs = mlflow.search_runs(experiment_names=["diabetes-experiment"])
print(runs[["run_id", "metrics.accuracy", "params.reg_rate"]])

# Filter runs
best_runs = mlflow.search_runs(
    experiment_names=["diabetes-experiment"],
    filter_string="metrics.accuracy > 0.9 AND params.reg_rate = '0.01'",
    order_by=["metrics.accuracy DESC"],
    max_results=5
)

# Get the best run
best_run = mlflow.search_runs(
    experiment_names=["diabetes-experiment"],
    order_by=["metrics.accuracy DESC"],
    max_results=1
)
best_run_id = best_run.iloc[0]["run_id"]
```

### 8.2 Using MlflowClient

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Get run details
run = client.get_run(run_id)
print(run.data.params)
print(run.data.metrics)
print(run.info.status)

# List artifacts
artifacts = client.list_artifacts(run_id)
for artifact in artifacts:
    print(artifact.path, artifact.file_size)
```

---

## 9. MLflow in Azure ML Jobs

### 9.1 Using MLflow in a Command Job Script

```python
# train.py - Training script
import mlflow
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from mlflow.models.signature import infer_signature

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--training_data", type=str)
    parser.add_argument("--reg_rate", type=float, default=0.01)
    args = parser.parse_args()

    # MLflow tracking is auto-configured in Azure ML jobs
    mlflow.autolog()

    with mlflow.start_run():
        # Read and split data
        df = pd.read_csv(args.training_data)
        X = df.drop("target", axis=1)
        y = df["target"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

        # Train
        model = LogisticRegression(C=1/args.reg_rate, max_iter=1000)
        model.fit(X_train, y_train)

        # Manual logging (in addition to autolog)
        accuracy = model.score(X_test, y_test)
        mlflow.log_metric("test_accuracy", accuracy)

        # Log model with signature
        signature = infer_signature(X_train, model.predict(X_train))
        mlflow.sklearn.log_model(model, "model", signature=signature)

if __name__ == "__main__":
    main()
```

### 9.2 Submitting the Job with SDK v2

```python
from azure.ai.ml import command, Input

job = command(
    code="./src",
    command="python train.py --training_data ${{inputs.training_data}} --reg_rate 0.01",
    inputs={"training_data": Input(type="uri_file", path="azureml:diabetes-data:1")},
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
    compute="aml-cluster",
    experiment_name="diabetes-experiment",
    display_name="diabetes-lr-train"
)

returned_job = ml_client.jobs.create_or_update(job)
```

### 9.3 MLflow in Pipeline Jobs

```python
# Each step in a pipeline can use MLflow independently
# MLflow automatically creates child runs for each pipeline step

@pipeline()
def diabetes_pipeline(training_data):
    prep_step = prep_component(input_data=training_data)
    train_step = train_component(
        training_data=prep_step.outputs.output_data,
        reg_rate=0.01
    )
    return {"model_output": train_step.outputs.model}
```

---

## 10. MLflow and Model Deployment in Azure ML

### 10.1 Deploy MLflow Model to Online Endpoint (No Scoring Script!)

One of the biggest advantages of MLflow models: **no scoring script or environment needed**.

```python
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Model
)
from azure.ai.ml.constants import AssetTypes

# Create endpoint
endpoint = ManagedOnlineEndpoint(
    name="diabetes-endpoint",
    auth_mode="key"
)
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Create deployment (NO scoring script, NO environment needed)
model = Model(
    path="azureml://jobs/{run_id}/outputs/artifacts/paths/model/",
    type=AssetTypes.MLFLOW_MODEL
)

deployment = ManagedOnlineDeployment(
    name="blue",
    endpoint_name="diabetes-endpoint",
    model=model,
    instance_type="Standard_DS3_v2",
    instance_count=1
)
ml_client.online_deployments.begin_create_or_update(deployment).result()

# Route 100% traffic
endpoint.traffic = {"blue": 100}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()
```

> **Exam tip**: MLflow models deployed to managed online endpoints **do NOT require a scoring script or a custom environment**. Azure ML auto-generates both. This is a MAJOR advantage over custom model deployment.

### 10.2 Deploy to Batch Endpoint

```python
from azure.ai.ml.entities import (
    BatchEndpoint,
    BatchDeployment,
    BatchRetrySettings,
    Model
)
from azure.ai.ml.constants import AssetTypes, BatchDeploymentOutputAction

# Create batch endpoint
batch_endpoint = BatchEndpoint(
    name="diabetes-batch-endpoint",
    description="Batch scoring for diabetes model"
)
ml_client.batch_endpoints.begin_create_or_update(batch_endpoint).result()

# Create batch deployment with MLflow model
model = Model(
    path="azureml://jobs/{run_id}/outputs/artifacts/paths/model/",
    type=AssetTypes.MLFLOW_MODEL
)

batch_deployment = BatchDeployment(
    name="mlflow-deployment",
    endpoint_name="diabetes-batch-endpoint",
    model=model,
    compute="aml-cluster",
    instance_count=2,
    max_concurrency_per_instance=2,
    mini_batch_size=10,
    output_action=BatchDeploymentOutputAction.APPEND_ROW,
    output_file_name="predictions.csv",
    retry_settings=BatchRetrySettings(max_retries=3, timeout=300)
)
ml_client.batch_deployments.begin_create_or_update(batch_deployment).result()
```

---

## 11. MLflow with Responsible AI

### 11.1 Logging Evaluation Metrics

```python
with mlflow.start_run():
    model = LogisticRegression().fit(X_train, y_train)
    
    # Evaluate
    result = mlflow.evaluate(
        model=model,
        data=eval_data,          # DataFrame with features + labels
        targets="target_col",
        model_type="classifier",  # "regressor" for regression
        evaluators=["default"]
    )
    
    print(result.metrics)     # All computed metrics
    print(result.artifacts)   # Evaluation artifacts (confusion matrix, etc.)
```

---

## 12. Key Exam Topics — Quick Reference

### Common Exam Scenarios

| Scenario | Answer |
|---|---|
| Track experiments in Azure ML | Use `mlflow.autolog()` or manual `mlflow.log_*` calls |
| Connect MLflow to Azure ML from local | `mlflow.set_tracking_uri(workspace.mlflow_tracking_uri)` |
| Log model for deployment | `mlflow.sklearn.log_model()` (NOT `log_artifact`) |
| Deploy without scoring script | Use MLflow model format (`AssetTypes.MLFLOW_MODEL`) |
| Compare runs | `mlflow.search_runs()` with `order_by` |
| Register model from run | `mlflow.register_model("runs:/{run_id}/model", "name")` |
| Get model signature | `infer_signature(X_train, model.predict(X_train))` |
| Log metric over time | `mlflow.log_metric("loss", value, step=epoch)` |
| Child runs for sweeps | `mlflow.start_run(nested=True)` |
| Custom model deployment | Use `mlflow.pyfunc.PythonModel` |

### MLflow Functions Cheat Sheet

```python
# TRACKING
mlflow.set_tracking_uri(uri)           # Set tracking server
mlflow.set_experiment("name")          # Set/create experiment
mlflow.start_run()                     # Start a run
mlflow.end_run()                       # End a run
mlflow.active_run()                    # Get current active run

# LOGGING
mlflow.log_param("key", value)         # Log single parameter
mlflow.log_params(dict)                # Log multiple parameters
mlflow.log_metric("key", value, step)  # Log single metric
mlflow.log_metrics(dict)               # Log multiple metrics
mlflow.log_artifact("path")            # Log file as artifact
mlflow.log_artifacts("dir")            # Log directory contents
mlflow.log_text("text", "file.txt")    # Log text
mlflow.log_dict(dict, "file.json")     # Log dict as JSON
mlflow.log_figure(fig, "plot.png")     # Log matplotlib figure
mlflow.log_table(df, "table.json")     # Log dataframe

# AUTOLOGGING
mlflow.autolog()                       # Generic autolog
mlflow.sklearn.autolog()               # Sklearn-specific

# MODELS
mlflow.sklearn.log_model(model, path)  # Log sklearn model
mlflow.sklearn.load_model(uri)         # Load sklearn model
mlflow.pyfunc.load_model(uri)          # Load as generic pyfunc
mlflow.register_model(uri, name)       # Register model

# MODEL SIGNATURE
from mlflow.models.signature import infer_signature
sig = infer_signature(input, output)   # Infer signature

# SEARCH
mlflow.search_runs(...)                # Search runs
mlflow.search_experiments(...)         # Search experiments
```

### Important Gotchas

1. **`autolog()` vs `sklearn.autolog()`**: Framework-specific autolog captures MORE information
2. **`log_model` vs `log_artifact`**: Only `log_model` creates the MLmodel metadata → only `log_model` allows direct deployment
3. **MLflow model deployment**: No scoring script needed. Custom model deployment: scoring script IS needed
4. **Tracking URI**: Auto-set in Azure ML jobs. Must be manually set for local development
5. **`pyfunc.load_model`** returns a wrapper, **`sklearn.load_model`** returns the native object
6. **Model signatures** are optional but recommended — they enable input validation at inference time
7. **In Azure ML**, MLflow experiments map to Azure ML experiments. Runs map to Azure ML jobs
8. **`mlflow.evaluate()`** can compute standard metrics automatically — no need to manually calculate accuracy, precision, etc.

---

## 13. Practice Questions Hints

- If a question asks about **tracking without code changes** → `mlflow.autolog()`
- If a question asks about **deploying with minimal config** → MLflow model (no scoring script)
- If a question asks about **comparing multiple runs** → `mlflow.search_runs()` with `order_by`
- If a question asks about **logging a model for reuse** → `mlflow.<flavor>.log_model()` with signature
- If a question asks about **connecting local notebook to Azure ML** → `mlflow.set_tracking_uri()`
- If a question asks about **what's in the MLmodel file** → flavors, signature, run_id, model_uuid
- If a question mentions **custom inference logic** → `mlflow.pyfunc.PythonModel`
- If a question asks about **model versioning** → `mlflow.register_model()` auto-increments versions
