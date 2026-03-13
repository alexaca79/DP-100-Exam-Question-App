# Azure ML SDK v2, CLI v2 & REST API — Comprehensive Guide for DP-100

Azure Machine Learning provides **three main interfaces** to interact with the service programmatically: the **Python SDK v2**, the **CLI v2** (Azure CLI extension), and the **REST API**. For DP-100, the focus is on **SDK v2** and **CLI v2** — the REST API is rarely tested but good to know exists.

---

## 1. Overview of Interfaces

| Interface | When to Use | Format |
|---|---|---|
| **Python SDK v2** (`azure-ai-ml`) | Interactive notebooks, Python scripts, CI/CD pipelines | Python code |
| **CLI v2** (`ml` extension for Azure CLI) | Automation, shell scripts, CI/CD, GitOps | YAML + CLI commands |
| **REST API** | Language-agnostic integration, custom apps | HTTP requests + JSON |

> **Exam tip**: SDK v2 and CLI v2 are **interchangeable** — anything you can do in one, you can do in the other. The exam tests both. CLI v2 uses YAML files for configuration while SDK v2 uses Python objects.

### 1.1 Installation

```bash
# CLI v2 - Install the ml extension for Azure CLI
az extension add -n ml -y

# SDK v2 - Install Python package
pip install azure-ai-ml azure-identity
```

---

## 2. Authentication and Workspace Connection

### 2.1 SDK v2 — MLClient

The `MLClient` is the **central entry point** for all SDK v2 operations.

```python
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

# Option 1: Explicit parameters
ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id="<subscription-id>",
    resource_group_name="<resource-group>",
    workspace_name="<workspace-name>"
)

# Option 2: From config file (config.json in current dir or parent dirs)
ml_client = MLClient.from_config(credential=DefaultAzureCredential())
```

**config.json** format:
```json
{
    "subscription_id": "<subscription-id>",
    "resource_group": "<resource-group>",
    "workspace_name": "<workspace-name>"
}
```

**Authentication options** (from `azure.identity`):
```python
from azure.identity import (
    DefaultAzureCredential,          # Tries multiple auth methods in order
    InteractiveBrowserCredential,    # Browser login popup
    ManagedIdentityCredential,       # For Azure-hosted resources  
    AzureCliCredential,              # Uses az login session
    ClientSecretCredential           # Service principal (app_id + secret)
)

# Common pattern for notebooks:
try:
    credential = DefaultAzureCredential()
    credential.get_token("https://management.azure.com/.default")
except Exception:
    credential = InteractiveBrowserCredential()
```

> **Exam tip**: `DefaultAzureCredential` tries (in order): Environment variables → Managed Identity → Azure CLI → Azure PowerShell → Interactive browser. It's the recommended default.

### 2.2 CLI v2 — Login and Defaults

```bash
# Login to Azure
az login

# Set default subscription
az account set --subscription "<subscription-id>"

# Set defaults so you don't repeat them every command
az configure --defaults group=<resource-group> workspace=<workspace-name>

# Verify workspace access
az ml workspace show
```

---

## 3. Workspaces

### 3.1 SDK v2

```python
from azure.ai.ml.entities import Workspace

# Create workspace
ws = Workspace(
    name="my-workspace",
    location="eastus",
    display_name="My ML Workspace",
    description="Workspace for DP-100 prep",
    tags={"purpose": "exam-prep"}
)
ml_client.workspaces.begin_create(ws).result()

# Get workspace details
ws = ml_client.workspaces.get("my-workspace")
print(ws.mlflow_tracking_uri)

# List workspaces
for ws in ml_client.workspaces.list():
    print(ws.name, ws.location)
```

### 3.2 CLI v2

```bash
# Create workspace
az ml workspace create --name my-workspace --location eastus

# Show workspace
az ml workspace show --name my-workspace

# List workspaces
az ml workspace list
```

---

## 4. Compute Resources

Azure ML supports multiple compute types. Understanding when to use each is critical for DP-100.

| Compute Type | Use Case | Persistent? |
|---|---|---|
| **Compute Instance** | Development, notebooks, experimentation | Yes (can stop/start) |
| **Compute Cluster** | Training jobs, pipeline steps | Auto-scales (0 to N nodes) |
| **Serverless Compute** | On-demand training without managing infra | No |
| **Kubernetes Compute** | Training and inference on AKS | Yes |
| **Attached Compute** | External resources (Databricks, HDInsight) | External |

### 4.1 Compute Instance — SDK v2

```python
from azure.ai.ml.entities import ComputeInstance

ci = ComputeInstance(
    name="my-dev-instance",
    size="Standard_DS3_v2",          # VM size
    idle_time_before_shutdown_minutes=60  # Auto-shutdown
)
ml_client.compute.begin_create_or_update(ci).result()

# Start/stop
ml_client.compute.begin_start("my-dev-instance").result()
ml_client.compute.begin_stop("my-dev-instance").result()

# Delete
ml_client.compute.begin_delete("my-dev-instance").result()
```

### 4.2 Compute Cluster — SDK v2

```python
from azure.ai.ml.entities import AmlCompute

cluster = AmlCompute(
    name="aml-cluster",
    type="amlcompute",
    size="Standard_DS3_v2",
    min_instances=0,          # Scale down to 0 when idle
    max_instances=4,          # Max 4 nodes
    idle_time_before_scale_down=120,  # Seconds before scaling down
    tier="Dedicated"          # or "LowPriority" for cheaper (can be preempted)
)
ml_client.compute.begin_create_or_update(cluster).result()
```

> **Exam tip**: `min_instances=0` means the cluster scales to zero when not in use — **cost-saving**. `LowPriority` tier is cheaper but VMs can be preempted (taken away).

### 4.3 Compute — CLI v2

```bash
# Create compute instance
az ml compute create --name my-dev-instance --type ComputeInstance --size Standard_DS3_v2

# Create compute cluster
az ml compute create --name aml-cluster --type AmlCompute \
    --size Standard_DS3_v2 --min-instances 0 --max-instances 4

# List compute resources
az ml compute list

# Using YAML file
az ml compute create --file compute.yml
```

**compute.yml**:
```yaml
$schema: https://azuremlschemas.azureedge.net/latest/amlCompute.schema.json
name: aml-cluster
type: amlcompute
size: Standard_DS3_v2
min_instances: 0
max_instances: 4
idle_time_before_scale_down: 120
tier: low_priority
```

---

## 5. Environments

Environments define the **runtime context** (Python packages, OS, Docker image) for training and inference.

### 5.1 Types of Environments

| Type | Description |
|---|---|
| **Curated** | Pre-built by Microsoft, ready to use (e.g., `AzureML-sklearn-1.0-ubuntu20.04-py38-cpu`) |
| **Custom from Docker** | Build from a Docker image + optional conda |
| **Custom from conda** | Base Docker image + conda specification file |
| **System-managed** | Azure ML manages the environment from a conda spec |

### 5.2 SDK v2

```python
from azure.ai.ml.entities import Environment

# Use a curated environment
env = Environment(
    image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04",
    conda_file="./conda.yml",
    name="my-custom-env",
    description="Custom env for training"
)
ml_client.environments.create_or_update(env)

# Reference a curated environment (no creation needed)
curated_env = "AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest"

# List environments
for env in ml_client.environments.list():
    print(env.name, env.latest_version)

# Get specific version
env = ml_client.environments.get("my-custom-env", version="1")
```

**conda.yml**:
```yaml
name: model-env
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.8
  - scikit-learn=1.0
  - pandas
  - numpy
  - pip:
    - mlflow
    - azureml-mlflow
    - azure-ai-ml
```

### 5.3 CLI v2

```bash
# Create environment from YAML
az ml environment create --file environment.yml

# List environments
az ml environment list

# Show specific environment
az ml environment show --name my-custom-env --version 1
```

**environment.yml**:
```yaml
$schema: https://azuremlschemas.azureedge.net/latest/environment.schema.json
name: my-custom-env
image: mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04
conda_file: conda.yml
description: Custom env with sklearn and mlflow
```

> **Exam tip**: Curated environments are referenced by name like `AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest`. Custom environments need explicit creation. Always pin versions in production.

---

## 6. Data Assets and Datastores

### 6.1 Datastores

Datastores are **abstractions** over Azure storage services. Every workspace comes with a default blob storage datastore.

```python
from azure.ai.ml.entities import AzureBlobDatastore, AccountKeyConfiguration

# Create a datastore
blob_ds = AzureBlobDatastore(
    name="my-blob-store",
    account_name="mystorageaccount",
    container_name="data-container",
    credentials=AccountKeyConfiguration(account_key="<key>")
)
ml_client.datastores.create_or_update(blob_ds)

# Get default datastore
default_ds = ml_client.datastores.get_default()

# List datastores
for ds in ml_client.datastores.list():
    print(ds.name, ds.type)
```

### 6.2 Data Assets — SDK v2

Three types of data assets:

| Type | Class/Constant | Use Case |
|---|---|---|
| **URI File** | `AssetTypes.URI_FILE` | Single file (CSV, Parquet, etc.) |
| **URI Folder** | `AssetTypes.URI_FOLDER` | Folder of files |
| **MLTable** | `AssetTypes.MLTABLE` | Tabular data with schema (for AutoML) |

```python
from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes

# URI File
file_data = Data(
    name="diabetes-csv",
    path="azureml://datastores/workspaceblobstore/paths/data/diabetes.csv",
    type=AssetTypes.URI_FILE,
    description="Diabetes CSV data",
    version="1"
)
ml_client.data.create_or_update(file_data)

# URI Folder
folder_data = Data(
    name="diabetes-folder",
    path="azureml://datastores/workspaceblobstore/paths/data/diabetes/",
    type=AssetTypes.URI_FOLDER,
    version="1"
)
ml_client.data.create_or_update(folder_data)

# MLTable
mltable_data = Data(
    name="diabetes-mltable",
    path="./data/",   # Folder must contain an MLTable file
    type=AssetTypes.MLTABLE,
    version="1"
)
ml_client.data.create_or_update(mltable_data)

# Reference existing data asset as input
from azure.ai.ml import Input
training_input = Input(type=AssetTypes.URI_FILE, path="azureml:diabetes-csv:1")
```

### 6.3 Data Assets — CLI v2

```bash
az ml data create --file data-asset.yml
```

**data-asset.yml**:
```yaml
$schema: https://azuremlschemas.azureedge.net/latest/data.schema.json
name: diabetes-csv
version: 1
type: uri_file
path: azureml://datastores/workspaceblobstore/paths/data/diabetes.csv
description: Diabetes dataset
```

> **Exam tip**: `MLTable` is REQUIRED for AutoML jobs. `URI_FILE` and `URI_FOLDER` are for regular jobs. The `azureml://` URI scheme references data in datastores.

---

## 7. Jobs (Training)

Jobs are the **core unit of work** in Azure ML. There are three types:

| Job Type | Purpose |
|---|---|
| **Command** | Run a single script or command |
| **Sweep** | Hyperparameter tuning (runs multiple trials) |
| **Pipeline** | Chain multiple steps/components |

### 7.1 Command Jobs — SDK v2

```python
from azure.ai.ml import command, Input

job = command(
    code="./src",                    # Local folder with your script(s)
    command="python train.py --training_data ${{inputs.training_data}} --reg_rate ${{inputs.reg_rate}}",
    inputs={
        "training_data": Input(
            type=AssetTypes.URI_FILE,
            path="azureml:diabetes-csv:1"
        ),
        "reg_rate": 0.01
    },
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
    compute="aml-cluster",
    experiment_name="diabetes-training",
    display_name="lr-train-001",
    description="Train logistic regression with reg_rate=0.01",
    tags={"model": "logistic-regression"}
)

# Submit the job
returned_job = ml_client.jobs.create_or_update(job)
print(f"Job URL: {returned_job.studio_url}")

# Wait for completion
ml_client.jobs.stream(returned_job.name)
```

### 7.2 Command Jobs — CLI v2

```bash
az ml job create --file job.yml
```

**job.yml**:
```yaml
$schema: https://azuremlschemas.azureedge.net/latest/commandJob.schema.json
type: command
code: ./src
command: >-
  python train.py 
  --training_data ${{inputs.training_data}} 
  --reg_rate ${{inputs.reg_rate}}
inputs:
  training_data:
    type: uri_file
    path: azureml:diabetes-csv:1
  reg_rate: 0.01
environment: azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest
compute: azureml:aml-cluster
experiment_name: diabetes-training
display_name: lr-train-001
description: Train logistic regression
```

> **Exam tip**: The `${{inputs.input_name}}` syntax is how you reference inputs in the command string — both in SDK v2 and CLI v2. Same pattern for `${{outputs.output_name}}`.

### 7.3 Job Inputs and Outputs

```python
from azure.ai.ml import command, Input, Output

job = command(
    code="./src",
    command="python train.py --input_data ${{inputs.data}} --output_model ${{outputs.model}}",
    inputs={
        "data": Input(type=AssetTypes.URI_FILE, path="azureml:diabetes-csv:1")
    },
    outputs={
        "model": Output(type=AssetTypes.URI_FOLDER, mode="rw_mount")
    },
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
    compute="aml-cluster"
)
```

**Data access modes**:

| Mode | Description | Read/Write |
|---|---|---|
| `ro_mount` | Read-only mount (default for inputs) | Read |
| `rw_mount` | Read-write mount (default for outputs) | Read + Write |
| `download` | Download data to compute node | Read |
| `upload` | Upload from compute node | Write |
| `direct` | Direct access via URI (no mount/download) | Depends |

### 7.4 Managing Jobs

```python
# List jobs
for job in ml_client.jobs.list(max_results=10):
    print(job.name, job.status)

# Get job details
job = ml_client.jobs.get("job-name")
print(job.status)  # Running, Completed, Failed, Canceled

# Cancel a job
ml_client.jobs.begin_cancel("job-name")

# Download job outputs
ml_client.jobs.download(name="job-name", output_name="model", download_path="./downloads")

# Archive / restore
ml_client.jobs.archive("job-name")
ml_client.jobs.restore("job-name")
```

```bash
# CLI equivalents
az ml job list --max-results 10
az ml job show --name <job-name>
az ml job cancel --name <job-name>
az ml job stream --name <job-name>       # Stream logs
az ml job download --name <job-name> --output-name model --download-path ./downloads
```

---

## 8. Sweep Jobs (Hyperparameter Tuning)

Sweep jobs run **multiple trials** with different hyperparameter values to find the best configuration.

### 8.1 SDK v2

```python
from azure.ai.ml import command, Input
from azure.ai.ml.sweep import Choice, Uniform, LogUniform, BanditPolicy

# Step 1: Define the base command job with search spaces
command_job = command(
    code="./src",
    command="python train.py --training_data ${{inputs.data}} --reg_rate ${{inputs.reg_rate}} --n_estimators ${{inputs.n_estimators}}",
    inputs={
        "data": Input(type=AssetTypes.URI_FILE, path="azureml:diabetes-csv:1"),
        "reg_rate": Uniform(min_value=0.001, max_value=1.0),        # Continuous
        "n_estimators": Choice(values=[50, 100, 200, 500]),          # Discrete
    },
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
    compute="aml-cluster"
)

# Step 2: Configure the sweep
sweep_job = command_job.sweep(
    sampling_algorithm="bayesian",   # "random", "grid", "bayesian"
    primary_metric="accuracy",
    goal="maximize",                 # "minimize" for loss metrics
)

# Step 3: Set limits
sweep_job.set_limits(
    max_total_trials=20,
    max_concurrent_trials=4,
    timeout=7200                     # seconds
)

# Step 4: Early termination policy (optional but recommended)
sweep_job.early_termination = BanditPolicy(
    evaluation_interval=1,           # Check every N trials
    slack_factor=0.1                 # Allow 10% slack from best
)

# Submit
returned_job = ml_client.jobs.create_or_update(sweep_job)
```

### 8.2 Sampling Algorithms

| Algorithm | Description | Best For |
|---|---|---|
| **Grid** | Exhaustive search over all combinations | Small discrete search spaces |
| **Random** | Random sampling from search space | Large search spaces, initial exploration |
| **Bayesian** | Uses previous results to guide search | Expensive evaluations, continuous params |
| **Sobol** | Quasi-random (more uniform than random) | Better coverage than pure random |

### 8.3 Search Space Types

```python
from azure.ai.ml.sweep import Choice, Uniform, LogUniform, Normal, QUniform, QNormal, Randint

# Discrete
Choice(values=[0.01, 0.1, 1.0])           # Pick from a list
Randint(upper=10)                           # Random int [0, upper)

# Continuous
Uniform(min_value=0.0, max_value=1.0)      # Uniform distribution
LogUniform(min_value=-3, max_value=0)       # Log-scale (10^min to 10^max)
Normal(mu=0, sigma=1)                       # Normal distribution

# Quantized (rounded to q)
QUniform(min_value=1, max_value=100, q=5)  # Uniform, rounded to nearest 5
QNormal(mu=50, sigma=10, q=1)              # Normal, rounded to nearest 1
```

> **Exam tip**: `LogUniform` is ideal for **learning rates** because they span orders of magnitude. `Choice` is for categorical/discrete values. Grid sampling only works with `Choice`.

### 8.4 Early Termination Policies

| Policy | How it Works |
|---|---|
| **BanditPolicy** | Terminates runs that are worse than the best by `slack_factor` (relative) or `slack_amount` (absolute) |
| **MedianStoppingPolicy** | Terminates runs worse than the median of all runs |
| **TruncationSelectionPolicy** | Cancels the bottom X% of runs at each evaluation interval |

```python
from azure.ai.ml.sweep import BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy

# Bandit - most commonly tested
BanditPolicy(evaluation_interval=2, slack_factor=0.1, delay_evaluation=5)

# Median stopping
MedianStoppingPolicy(evaluation_interval=1, delay_evaluation=5)

# Truncation selection - cancel bottom 20%
TruncationSelectionPolicy(evaluation_interval=2, truncation_percentage=20)
```

> **Exam tip**: `BanditPolicy` is the most commonly tested. `delay_evaluation` delays the policy check for the first N intervals to let runs warm up. `evaluation_interval` defines how often to check.

### 8.5 Sweep Jobs — CLI v2

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/sweepJob.schema.json
type: sweep
trial:
  code: ./src
  command: >-
    python train.py 
    --training_data ${{inputs.data}} 
    --reg_rate ${{search_space.reg_rate}}
    --n_estimators ${{search_space.n_estimators}}
  environment: azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest
inputs:
  data:
    type: uri_file
    path: azureml:diabetes-csv:1
compute: azureml:aml-cluster
sampling_algorithm: bayesian
search_space:
  reg_rate:
    type: uniform
    min_value: 0.001
    max_value: 1.0
  n_estimators:
    type: choice
    values: [50, 100, 200, 500]
objective:
  primary_metric: accuracy
  goal: maximize
limits:
  max_total_trials: 20
  max_concurrent_trials: 4
  timeout: 7200
early_termination:
  type: bandit
  evaluation_interval: 1
  slack_factor: 0.1
```

---

## 9. Pipeline Jobs

Pipelines chain **multiple steps** together, passing data between them.

### 9.1 Components

Components are **reusable, self-contained steps**. A pipeline is made of components.

```python
from azure.ai.ml import command, Input, Output
from azure.ai.ml.constants import AssetTypes

# Define a component
prep_component = command(
    name="data_prep",
    display_name="Data Preparation",
    code="./src/prep",
    command="python prep.py --input_data ${{inputs.raw_data}} --output_data ${{outputs.cleaned_data}}",
    inputs={
        "raw_data": Input(type=AssetTypes.URI_FILE)
    },
    outputs={
        "cleaned_data": Output(type=AssetTypes.URI_FOLDER)
    },
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest"
)

# Register component
ml_client.components.create_or_update(prep_component)
```

### 9.2 Component from YAML

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/commandComponent.schema.json
name: data_prep
display_name: Data Preparation
type: command
code: ./src/prep
command: >-
  python prep.py 
  --input_data ${{inputs.raw_data}} 
  --output_data ${{outputs.cleaned_data}}
inputs:
  raw_data:
    type: uri_file
outputs:
  cleaned_data:
    type: uri_folder
environment: azureml:AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest
```

```bash
# Register component
az ml component create --file component.yml
```

### 9.3 Component from Decorator (@command_component)

```python
from azure.ai.ml import command
from azure.ai.ml.dsl import pipeline

# Use load_component to load from YAML
from azure.ai.ml import load_component

prep_component = load_component(source="./components/prep/component.yml")
train_component = load_component(source="./components/train/component.yml")

# Or create inline
@pipeline(
    description="End-to-end diabetes training pipeline",
    default_compute="aml-cluster"
)
def diabetes_pipeline(raw_data, reg_rate=0.01):
    prep_step = prep_component(raw_data=raw_data)
    train_step = train_component(
        training_data=prep_step.outputs.cleaned_data,
        reg_rate=reg_rate
    )
    return {"trained_model": train_step.outputs.model}

# Build and submit pipeline
pipeline_job = diabetes_pipeline(
    raw_data=Input(type=AssetTypes.URI_FILE, path="azureml:diabetes-csv:1"),
    reg_rate=0.01
)

returned_job = ml_client.jobs.create_or_update(pipeline_job)
```

### 9.4 Pipeline — CLI v2

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/pipelineJob.schema.json
type: pipeline
display_name: diabetes-training-pipeline
experiment_name: diabetes-pipeline
settings:
  default_compute: azureml:aml-cluster

inputs:
  raw_data:
    type: uri_file
    path: azureml:diabetes-csv:1
  reg_rate: 0.01

jobs:
  prep_step:
    type: command
    component: azureml:data_prep@latest
    inputs:
      raw_data: ${{parent.inputs.raw_data}}
    outputs:
      cleaned_data:
        type: uri_folder
  
  train_step:
    type: command
    component: azureml:train_model@latest
    inputs:
      training_data: ${{parent.jobs.prep_step.outputs.cleaned_data}}
      reg_rate: ${{parent.inputs.reg_rate}}
    outputs:
      model:
        type: uri_folder
```

> **Exam tip**: In pipeline YAML, `${{parent.inputs.X}}` references pipeline-level inputs. `${{parent.jobs.step_name.outputs.Y}}` references outputs from another step. This is how data flows between steps.

### 9.5 Schedule Pipelines

```python
from azure.ai.ml.entities import (
    RecurrenceTrigger, 
    RecurrencePattern,
    JobSchedule
)

schedule = JobSchedule(
    name="daily-training",
    trigger=RecurrenceTrigger(
        frequency="day",
        interval=1,
        schedule=RecurrencePattern(hours=6, minutes=0),
        time_zone="UTC"
    ),
    create_job=pipeline_job  # The pipeline to run
)
ml_client.schedules.begin_create_or_update(schedule).result()

# Disable/enable schedule
schedule.is_enabled = False
ml_client.schedules.begin_create_or_update(schedule).result()
```

---

## 10. Models

### 10.1 Register Models — SDK v2

```python
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes

# Register MLflow model from a job
mlflow_model = Model(
    path=f"azureml://jobs/{job_name}/outputs/artifacts/paths/model/",
    type=AssetTypes.MLFLOW_MODEL,
    name="diabetes-classifier",
    description="Logistic regression model",
    tags={"framework": "sklearn", "task": "classification"}
)
ml_client.models.create_or_update(mlflow_model)

# Register custom model (pickle, ONNX, etc.)
custom_model = Model(
    path="./model/model.pkl",
    type=AssetTypes.CUSTOM_MODEL,
    name="diabetes-custom",
    description="Custom sklearn model"
)
ml_client.models.create_or_update(custom_model)

# List models
for model in ml_client.models.list():
    print(model.name, model.latest_version)

# Get specific version
model = ml_client.models.get("diabetes-classifier", version="1")

# Archive model
ml_client.models.archive("diabetes-classifier", version="1")
```

### 10.2 Register Models — CLI v2

```bash
az ml model create --file model.yml
```

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/model.schema.json
name: diabetes-classifier
path: azureml://jobs/<job-name>/outputs/artifacts/paths/model/
type: mlflow_model
description: Logistic regression model for diabetes
```

> **Exam tip**: `AssetTypes.MLFLOW_MODEL` = MLflow model (no scoring script needed for deployment). `AssetTypes.CUSTOM_MODEL` = custom model (scoring script IS needed).

---

## 11. Endpoints and Deployments

### 11.1 Online Endpoints (Real-Time)

#### SDK v2

```python
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Model,
    Environment,
    CodeConfiguration
)

# Step 1: Create endpoint
endpoint = ManagedOnlineEndpoint(
    name="diabetes-endpoint",
    description="Real-time diabetes prediction",
    auth_mode="key"     # "key" or "aml_token"
)
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Step 2a: Deploy MLflow model (NO scoring script needed!)
mlflow_deployment = ManagedOnlineDeployment(
    name="blue",
    endpoint_name="diabetes-endpoint",
    model="azureml:diabetes-classifier:1",
    instance_type="Standard_DS3_v2",
    instance_count=1
)
ml_client.online_deployments.begin_create_or_update(mlflow_deployment).result()

# Step 2b: Deploy CUSTOM model (scoring script + environment needed)
custom_deployment = ManagedOnlineDeployment(
    name="green",
    endpoint_name="diabetes-endpoint",
    model="azureml:diabetes-custom:1",
    code_configuration=CodeConfiguration(
        code="./src/scoring",
        scoring_script="score.py"
    ),
    environment="azureml:my-custom-env:1",
    instance_type="Standard_DS3_v2",
    instance_count=1
)
ml_client.online_deployments.begin_create_or_update(custom_deployment).result()

# Step 3: Set traffic allocation (Blue/Green deployment)
endpoint.traffic = {"blue": 90, "green": 10}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Invoke endpoint
ml_client.online_endpoints.invoke(
    endpoint_name="diabetes-endpoint",
    request_file="sample-request.json",
    deployment_name="blue"       # Specific deployment (ignores traffic rules)
)

# Delete
ml_client.online_endpoints.begin_delete("diabetes-endpoint").result()
```

#### Scoring Script (`score.py`)

```python
import json
import joblib
import numpy as np
import os

def init():
    """Called once when the deployment starts. Load model into memory."""
    global model
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'model', 'model.pkl')
    model = joblib.load(model_path)

def run(raw_data):
    """Called for every request. Return predictions."""
    data = np.array(json.loads(raw_data)['data'])
    predictions = model.predict(data)
    return predictions.tolist()
```

> **Exam tip**: Two mandatory functions in scoring script — `init()` (loads model once at startup) and `run(raw_data)` (handles each request). `AZUREML_MODEL_DIR` is the environment variable pointing to the model directory.

#### CLI v2 — Online Endpoint

```bash
# Create endpoint
az ml online-endpoint create --file endpoint.yml

# Create deployment
az ml online-deployment create --file deployment.yml --all-traffic

# Update traffic
az ml online-endpoint update --name diabetes-endpoint --traffic "blue=90 green=10"

# Invoke
az ml online-endpoint invoke --name diabetes-endpoint --request-file sample-request.json

# Delete
az ml online-endpoint delete --name diabetes-endpoint --yes
```

**endpoint.yml**:
```yaml
$schema: https://azuremlschemas.azureedge.net/latest/managedOnlineEndpoint.schema.json
name: diabetes-endpoint
auth_mode: key
```

**deployment.yml** (MLflow):
```yaml
$schema: https://azuremlschemas.azureedge.net/latest/managedOnlineDeployment.schema.json
name: blue
endpoint_name: diabetes-endpoint
model: azureml:diabetes-classifier:1
instance_type: Standard_DS3_v2
instance_count: 1
```

### 11.2 Batch Endpoints

```python
from azure.ai.ml.entities import (
    BatchEndpoint,
    BatchDeployment,
    BatchRetrySettings,
    Model
)
from azure.ai.ml.constants import BatchDeploymentOutputAction

# Create batch endpoint
batch_endpoint = BatchEndpoint(
    name="diabetes-batch",
    description="Batch predictions for diabetes"
)
ml_client.batch_endpoints.begin_create_or_update(batch_endpoint).result()

# Create batch deployment
batch_deployment = BatchDeployment(
    name="diabetes-batch-dp",
    endpoint_name="diabetes-batch",
    model="azureml:diabetes-classifier:1",
    compute="aml-cluster",
    instance_count=2,
    max_concurrency_per_instance=2,
    mini_batch_size=10,
    output_action=BatchDeploymentOutputAction.APPEND_ROW,
    output_file_name="predictions.csv",
    retry_settings=BatchRetrySettings(max_retries=3, timeout=300),
)
ml_client.batch_deployments.begin_create_or_update(batch_deployment).result()

# Set default deployment
batch_endpoint.defaults.deployment_name = "diabetes-batch-dp"
ml_client.batch_endpoints.begin_create_or_update(batch_endpoint).result()

# Invoke batch endpoint
job = ml_client.batch_endpoints.invoke(
    endpoint_name="diabetes-batch",
    input=Input(type=AssetTypes.URI_FOLDER, path="azureml:test-data:1")
)
```

> **Exam tip**: `APPEND_ROW` appends all predictions to a single CSV. `SUMMARY_ONLY` generates only a summary without per-row output. Batch endpoints use a **compute cluster**, not an instance type.

---

## 12. AutoML — SDK v2 & CLI v2

### 12.1 SDK v2

```python
from azure.ai.ml import automl, Input
from azure.ai.ml.constants import AssetTypes

# Classification
classification_job = automl.classification(
    compute="aml-cluster",
    experiment_name="automl-diabetes",
    training_data=Input(type=AssetTypes.MLTABLE, path="azureml:diabetes-mltable:1"),
    target_column_name="Diabetic",
    primary_metric="accuracy",
    n_cross_validations=5,
    enable_model_explainability=True
)

# Set limits
classification_job.set_limits(
    timeout_minutes=60,
    trial_timeout_minutes=20,
    max_trials=20,
    max_concurrent_trials=4,
    enable_early_termination=True
)

# Set training settings
classification_job.set_training(
    allowed_training_algorithms=["LogisticRegression", "LightGBM", "XGBoostClassifier"],
    # OR blocked:
    # blocked_training_algorithms=["KNN"]
    enable_stack_ensemble=True,
    enable_vote_ensemble=True
)

# Set featurization
classification_job.set_featurization(mode="auto")  # "auto", "off", "custom"

# Submit
returned_job = ml_client.jobs.create_or_update(classification_job)
```

```python
# Regression
regression_job = automl.regression(
    compute="aml-cluster",
    training_data=Input(type=AssetTypes.MLTABLE, path="azureml:house-prices:1"),
    target_column_name="Price",
    primary_metric="normalized_root_mean_squared_error",
    n_cross_validations=5
)

# Forecasting
forecasting_job = automl.forecasting(
    compute="aml-cluster",
    training_data=Input(type=AssetTypes.MLTABLE, path="azureml:sales-data:1"),
    target_column_name="Sales",
    primary_metric="normalized_root_mean_squared_error",
    n_cross_validations=5,
    forecasting_settings=ForecastingSettings(
        time_column_name="Date",
        forecast_horizon=30,
        frequency="D"
    )
)

# Image Classification, Object Detection, NLP — also available!
```

### 12.2 AutoML — CLI v2

```yaml
$schema: https://azuremlschemas.azureedge.net/latest/autoMLClassificationJob.schema.json
type: automl
task: classification
training_data:
  type: mltable
  path: azureml:diabetes-mltable:1
target_column_name: Diabetic
primary_metric: accuracy
compute: azureml:aml-cluster
limits:
  timeout_minutes: 60
  max_trials: 20
  max_concurrent_trials: 4
  enable_early_termination: true
training:
  enable_stack_ensemble: true
  enable_vote_ensemble: true
n_cross_validations: 5
featurization:
  mode: auto
```

> **Exam tip**: AutoML requires `MLTABLE` data type. Primary metrics: Classification → `accuracy`, `AUC_weighted`; Regression → `normalized_root_mean_squared_error`, `r2_score`; Forecasting → `normalized_root_mean_squared_error`.

---

## 13. Responsible AI

### 13.1 Responsible AI Dashboard — SDK v2

```python
from azure.ai.ml.entities import (
    ResponsibleAIInsights,
    ResponsibleAIModelAnalysis
)

# Create RAI insights
rai_job = ml_client.jobs.create_or_update(
    ResponsibleAIModelAnalysis(
        model=model,
        test_data=test_data,
        target_column_name="target",
        task_type="classification",
        components=[
            "error_analysis",
            "explanation",        # Feature importance / SHAP
            "counterfactual",
            "causal"
        ]
    )
)
```

Key RAI components:

| Component | Purpose |
|---|---|
| **Error Analysis** | Identify cohorts where model performs poorly |
| **Model Explainability** | Feature importance (global/local), SHAP values |
| **Counterfactuals** | "What-if" analysis — what changes would flip the prediction |
| **Causal Analysis** | Causal relationships (what actually CAUSES the outcome) |
| **Fairness** | Detect bias across demographic groups |

---

## 14. Managed Feature Store

```python
from azure.ai.ml.entities import (
    FeatureStore,
    FeatureSet,
    FeatureStoreEntity
)

# Feature stores centralize feature engineering so teams can share and reuse features
# Key concepts: Feature Store → Feature Set → Feature (column)
```

---

## 15. RBAC and Security

### 15.1 Built-in Roles

| Role | Permissions |
|---|---|
| **Owner** | Full access including role assignments |
| **Contributor** | Full access except role assignments |
| **Reader** | View only |
| **AzureML Data Scientist** | Run experiments, deploy models, manage compute (CANNOT manage workspace settings) |
| **AzureML Compute Operator** | Create/manage compute resources |

> **Exam tip**: `AzureML Data Scientist` is the **least-privilege** role for someone who needs to train models and deploy endpoints but shouldn't manage workspace infrastructure.

### 15.2 Managed Identities

```python
# Use managed identity for compute to access datastores
from azure.ai.ml.entities import AmlCompute, ManagedIdentityConfiguration, IdentityConfiguration

compute = AmlCompute(
    name="aml-cluster",
    size="Standard_DS3_v2",
    min_instances=0,
    max_instances=4,
    identity=IdentityConfiguration(
        type="SystemAssigned"  # or "UserAssigned"
    )
)
```

---

## 16. CLI v2 vs SDK v2 — Side-by-Side Comparison

| Operation | CLI v2 | SDK v2 |
|---|---|---|
| Create compute | `az ml compute create --file compute.yml` | `ml_client.compute.begin_create_or_update(compute)` |
| Create environment | `az ml environment create --file env.yml` | `ml_client.environments.create_or_update(env)` |
| Submit job | `az ml job create --file job.yml` | `ml_client.jobs.create_or_update(job)` |
| Create data | `az ml data create --file data.yml` | `ml_client.data.create_or_update(data)` |
| Register model | `az ml model create --file model.yml` | `ml_client.models.create_or_update(model)` |
| Create endpoint | `az ml online-endpoint create --file endpoint.yml` | `ml_client.online_endpoints.begin_create_or_update(ep)` |
| Create deployment | `az ml online-deployment create --file deploy.yml` | `ml_client.online_deployments.begin_create_or_update(dp)` |
| Create component | `az ml component create --file component.yml` | `ml_client.components.create_or_update(comp)` |

> **Pattern**: CLI v2 always follows `az ml <resource> <action> --file <yaml>`. SDK v2 always follows `ml_client.<resource>.begin_create_or_update(<entity>)` (with `begin_` prefix for long-running operations).

---

## 17. Key YAML Schemas Reference

Every CLI v2 YAML file starts with `$schema` to enable validation:

```
# Jobs
commandJob:     https://azuremlschemas.azureedge.net/latest/commandJob.schema.json
sweepJob:       https://azuremlschemas.azureedge.net/latest/sweepJob.schema.json
pipelineJob:    https://azuremlschemas.azureedge.net/latest/pipelineJob.schema.json

# Resources
amlCompute:     https://azuremlschemas.azureedge.net/latest/amlCompute.schema.json
environment:    https://azuremlschemas.azureedge.net/latest/environment.schema.json
data:           https://azuremlschemas.azureedge.net/latest/data.schema.json
model:          https://azuremlschemas.azureedge.net/latest/model.schema.json

# Endpoints
managedOnlineEndpoint:    .../latest/managedOnlineEndpoint.schema.json
managedOnlineDeployment:  .../latest/managedOnlineDeployment.schema.json
batchEndpoint:            .../latest/batchEndpoint.schema.json
batchDeployment:          .../latest/batchDeployment.schema.json

# Components
commandComponent: .../latest/commandComponent.schema.json
```

---

## 18. Exam Cheat Sheet — SDK v2 / CLI v2 Key Points

### Must-Know Patterns

1. **MLClient** is the entry point for ALL SDK v2 operations
2. **`begin_` prefix** = long-running operation (returns a poller, call `.result()` to wait)
3. **`${{inputs.X}}`** and **`${{outputs.X}}`** for referencing inputs/outputs in commands
4. **`azureml:resource-name:version`** is how you reference registered resources
5. **YAML `$schema`** is required for CLI v2 validation
6. **`@latest`** suffix gets the latest version of an environment or component

### Common Exam Traps

| Trap | Correct Answer |
|---|---|
| "Which data type for AutoML?" | `MLTABLE` (not URI_FILE or URI_FOLDER) |
| "Deploy MLflow model — what's needed?" | Just the model. No scoring script, no environment |
| "Deploy custom model — what's needed?" | Model + scoring script (`score.py`) + environment |
| "What functions in scoring script?" | `init()` and `run(raw_data)` |
| "Cheapest compute cluster?" | `min_instances=0` + `tier=low_priority` |
| "How to reference parent pipeline input?" | `${{parent.inputs.input_name}}` |
| "How to reference step output in pipeline?" | `${{parent.jobs.step_name.outputs.output_name}}` |
| "Which auth for managed online endpoints?" | `key` or `aml_token` |
| "Which role for data scientist?" | `AzureML Data Scientist` (least privilege) |
| "How to run a pipeline on schedule?" | `JobSchedule` with `RecurrenceTrigger` |
| "How to do blue/green deployment?" | Set `endpoint.traffic = {"blue": 90, "green": 10}` |
| "Batch vs online endpoint compute?" | Batch = compute cluster, Online = instance type |

### SDK v2 Import Cheat Sheet

```python
# Core
from azure.ai.ml import MLClient, command, Input, Output
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import load_component
from azure.identity import DefaultAzureCredential

# Constants
from azure.ai.ml.constants import AssetTypes  # URI_FILE, URI_FOLDER, MLTABLE, MLFLOW_MODEL, CUSTOM_MODEL
from azure.ai.ml.constants import BatchDeploymentOutputAction  # APPEND_ROW, SUMMARY_ONLY

# Entities
from azure.ai.ml.entities import (
    AmlCompute, ComputeInstance,
    Environment,
    Data, Model,
    ManagedOnlineEndpoint, ManagedOnlineDeployment,
    BatchEndpoint, BatchDeployment,
    CodeConfiguration,
    AzureBlobDatastore, AccountKeyConfiguration,
    JobSchedule, RecurrenceTrigger
)

# Sweep
from azure.ai.ml.sweep import Choice, Uniform, LogUniform, Normal
from azure.ai.ml.sweep import BanditPolicy, MedianStoppingPolicy, TruncationSelectionPolicy

# AutoML
from azure.ai.ml import automl
```
