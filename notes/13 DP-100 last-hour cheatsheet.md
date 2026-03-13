# DP-100 Last-Hour Cheatsheet — Review This Before Your Exam

---

## WORKSPACE RESOURCES (created automatically)

| Resource | Purpose | Created when? |
|---|---|---|
| Storage Account | Store data, logs, outputs | Immediately |
| Key Vault | Store secrets, keys, connection strings | Immediately |
| Application Insights | Monitor endpoints | Immediately |
| Container Registry (ACR) | Store environment Docker images | On-demand (first env build/deploy) |

---

## COMPUTE TYPES

| Type | Use For | Key Setting |
|---|---|---|
| **Compute Instance** | Notebooks, dev | Single VM, 1 user only |
| **Compute Cluster** | Jobs, sweeps, pipelines, AutoML, batch | `min_instances=0`, `tier=low_priority` |
| **Serverless** | On-demand jobs | No infra to manage |
| **Managed Online Endpoint** | Real-time inference | `instance_type` + `instance_count` |

---

## DATA ASSETS

| Type | Constant | Use For |
|---|---|---|
| **URI_FILE** | `AssetTypes.URI_FILE` | Single file (CSV, Parquet) |
| **URI_FOLDER** | `AssetTypes.URI_FOLDER` | Folder of files |
| **MLTABLE** | `AssetTypes.MLTABLE` | Tabular with schema → **REQUIRED for AutoML** |

**Access modes**: `ro_mount` (default input) · `rw_mount` (default output) · `download` · `upload` · `direct`

---

## AUTHENTICATION

```
DefaultAzureCredential order:
1. EnvironmentCredential (env vars)
2. ManagedIdentityCredential (Azure VMs)
3. AzureCliCredential (az login)
4. AzurePowerShellCredential
5. InteractiveBrowserCredential
```

**Storage data access roles**: `Storage Blob Data Reader` (read) · `Storage Blob Data Contributor` (read+write)
*ARM roles (Reader, Contributor) do NOT grant data access*

---

## RBAC ROLES

| Role | Can train? | Can deploy? | Can create compute? |
|---|---|---|---|
| **AzureML Data Scientist** | ✅ | ✅ | ❌ |
| **AzureML Compute Operator** | ❌ | ❌ | ✅ |
| **Contributor** | ✅ | ✅ | ✅ |

---

## ENVIRONMENTS

- **Curated**: `AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest`
- **Custom**: Docker base image + conda.yml
- **Base image**: `mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04` (current)
- Old `openmpi3.1.2-ubuntu18.04` is **deprecated**

---

## JOBS

| Job Type | Purpose |
|---|---|
| **Command** | Run a single script |
| **Sweep** | Hyperparameter tuning |
| **Pipeline** | Multi-step workflow |
| **AutoML** | Automated model selection |

**Input reference**: `${{inputs.X}}` · **Output reference**: `${{outputs.X}}`

---

## COMMAND JOB (SDK v2)

```python
from azure.ai.ml import command, Input
job = command(
    code="./src",
    command="python train.py --data ${{inputs.data}} --lr ${{inputs.lr}}",
    inputs={"data": Input(type=AssetTypes.URI_FILE, path="azureml:mydata:1"), "lr": 0.01},
    environment="AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest",
    compute="aml-cluster"
)
ml_client.jobs.create_or_update(job)
```

---

## SWEEP JOB

**Sampling algorithms**:

| Algorithm | Supports |
|---|---|
| **Grid** | `Choice` only |
| **Random** | ALL types |
| **Bayesian** | `Choice`, `Uniform`, `QUniform` only |

**Search space types**: `Choice` · `Uniform` · `LogUniform` · `Normal` · `QUniform` · `Randint`

**Early termination policies**:

| Policy | How it works |
|---|---|
| **BanditPolicy** | Kill if worse than best by `slack_factor` |
| **MedianStoppingPolicy** | Kill if worse than median of all runs |
| **TruncationSelectionPolicy** | Kill bottom X% at each interval |

`delay_evaluation` = wait N intervals before applying policy

---

## PIPELINES

**Python SDK**: `@pipeline` decorator, `step.outputs.name` for cross-step data
**CLI v2 YAML**: `${{parent.inputs.X}}` for pipeline inputs, `${{parent.jobs.step.outputs.X}}` for cross-step

**Components**: `load_component(source="component.yml")` or `az ml component create --file component.yml`

**Scheduling**: `JobSchedule` + `RecurrenceTrigger(frequency="day", interval=1)`

---

## MLFLOW — THE BIG 5

```python
mlflow.log_param("key", value)           # Input parameter
mlflow.log_metric("key", value, step=N)  # Output metric (step for charts)
mlflow.log_artifact("file.png")          # File artifact
mlflow.sklearn.log_model(model, "model") # MODEL (creates MLmodel file)
mlflow.autolog()                         # Auto-capture everything
```

- **Inside Azure ML job**: Tracking URI set automatically
- **From local**: Must call `mlflow.set_tracking_uri(uri)` first
- `mlflow.autolog()` → generic · `mlflow.sklearn.autolog()` → more detailed for sklearn
- `pyfunc.load_model()` → generic wrapper · `sklearn.load_model()` → native sklearn object

---

## MODEL SIGNATURE

```python
from mlflow.models.signature import infer_signature
signature = infer_signature(X_train, model.predict(X_train))
mlflow.sklearn.log_model(model, "model", signature=signature)
```

---

## MODEL REGISTRATION

```python
# SDK v2 approach
Model(path=f"azureml://jobs/{name}/outputs/artifacts/paths/model/",
      type=AssetTypes.MLFLOW_MODEL, name="my-model")
ml_client.models.create_or_update(model)

# MLflow approach
mlflow.register_model("runs:/{run_id}/model", "my-model")
```

---

## DEPLOYMENT DECISION TREE

```
Is it an MLflow model?
├── YES → No scoring script, no environment needed
│         Just model + endpoint + deployment config
└── NO (Custom model) → Need ALL of:
    ├── score.py (with init() + run())
    ├── Environment (conda.yml + Docker image)
    └── Model files
```

---

## ONLINE ENDPOINTS

```python
# Create endpoint
endpoint = ManagedOnlineEndpoint(name="my-ep", auth_mode="key")  # or "aml_token"
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# Create deployment
deployment = ManagedOnlineDeployment(name="blue", endpoint_name="my-ep",
    model="azureml:my-model:1", instance_type="Standard_DS3_v2", instance_count=1)
ml_client.online_deployments.begin_create_or_update(deployment).result()

# Set traffic (MUST sum to 100%)
endpoint.traffic = {"blue": 90, "green": 10}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()
```

- `auth_mode="key"` → Static API key
- `auth_mode="aml_token"` → Microsoft Entra ID token (more secure)

---

## BATCH ENDPOINTS

- Uses **compute cluster** (not instance_type)
- Output: `APPEND_ROW` (single CSV) or `SUMMARY_ONLY`
- Settings: `mini_batch_size`, `max_concurrency_per_instance`, `retry_settings`

---

## SCORING SCRIPT (Custom Models Only)

```python
def init():    # Called ONCE at startup
    global model
    model = joblib.load(os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'model.pkl'))

def run(data): # Called for EACH request
    predictions = model.predict(json.loads(data)['data'])
    return predictions.tolist()
```

---

## AUTOML

- **Requires**: `MLTABLE` data type
- **Task types**: Classification, Regression, Forecasting, Computer Vision, NLP
- **Primary metrics (Classification)**: `accuracy`, `AUC_weighted`, `norm_macro_recall`, `average_precision_score_weighted`
- **Primary metrics (Regression)**: `normalized_root_mean_squared_error`, `r2_score`
- **Controls**: `set_limits()` (timeout, max_trials), `set_training()` (allowed/blocked algos), `set_featurization()` (auto/off/custom)

---

## RESPONSIBLE AI — 6 PRINCIPLES

| # | Principle | Key Question |
|---|---|---|
| 1 | **Fairness** | Does it discriminate? |
| 2 | **Reliability & Safety** | Could it cause harm? |
| 3 | **Privacy & Security** | Is data protected? |
| 4 | **Inclusiveness** | Can everyone use it? |
| 5 | **Transparency** | Can users understand it? |
| 6 | **Accountability** | Who is responsible? |

**RAI Dashboard components**: Error Analysis → Explainability (SHAP) → Counterfactuals → Causal Analysis

---

## RESPONSIBLE AI DASHBOARD COMPONENTS

| Component | Answers |
|---|---|
| **Error Analysis** | Where does the model fail? (subgroups) |
| **Explainability** | Which features matter? (SHAP values) |
| **Counterfactuals** | What change would flip the prediction? |
| **Causal Analysis** | What actually causes the outcome? |

---

## SDK v2 PATTERN CHEAT SHEET

```python
# Long-running → begin_ prefix → call .result()
ml_client.compute.begin_create_or_update(compute).result()
ml_client.online_endpoints.begin_create_or_update(endpoint).result()
ml_client.online_deployments.begin_create_or_update(deployment).result()

# Fast operations → no begin_ prefix
ml_client.environments.create_or_update(env)
ml_client.data.create_or_update(data)
ml_client.models.create_or_update(model)
ml_client.components.create_or_update(component)
ml_client.jobs.create_or_update(job)
```

---

## CLI v2 PATTERN CHEAT SHEET

```bash
az ml job create --file job.yml
az ml compute create --file compute.yml
az ml environment create --file env.yml
az ml model create --file model.yml
az ml online-endpoint create --file endpoint.yml
az ml online-deployment create --file deployment.yml
az ml component create --file component.yml
az ml data create --file data.yml
```

Every YAML starts with: `$schema: https://azuremlschemas.azureedge.net/latest/<type>.schema.json`

---

## YAML REFERENCE SYNTAX

| What | Syntax |
|---|---|
| Registered asset | `azureml:name:version` or `azureml:name@latest` |
| Job input | `${{inputs.name}}` |
| Job output | `${{outputs.name}}` |
| Search space (sweep) | `${{search_space.name}}` |
| Pipeline parent input | `${{parent.inputs.name}}` |
| Pipeline step output | `${{parent.jobs.step.outputs.name}}` |

---

## MLOPS MATURITY LEVELS

| Level | Description |
|---|---|
| 0 | Manual everything |
| 1 | CI/CD for app code only |
| 2 | Automated training pipelines |
| 3 | Automated training + deployment |
| 4 | Full MLOps (retraining on drift, monitoring, A/B) |

---

## QUICK DECISION MATRIX

| If the question says... | The answer is... |
|---|---|
| "no scoring script needed" | MLflow model |
| "cheapest compute for training" | `min_instances=0` + `tier=low_priority` |
| "AutoML data type" | MLTABLE |
| "least privilege for data scientist" | AzureML Data Scientist role |
| "short-lived auth tokens" | `auth_mode="aml_token"` |
| "schedule a pipeline" | `JobSchedule` + `RecurrenceTrigger` |
| "share models across workspaces" | Azure ML Registry |
| "custom inference logic in model" | `mlflow.pyfunc.PythonModel` |
| "best sampling for learning rate" | `LogUniform` with `Random` sampling |
| "stop bad trials early" | `BanditPolicy` |
| "what change flips prediction" | Counterfactual Analysis |
| "which features matter" | Model Explainability / SHAP |
| "where does model fail" | Error Analysis |
| "deploy with no infra management" | Serverless API (Model-as-a-Service) |
| "metric over time (chart)" | `mlflow.log_metric(key, val, step=epoch)` |
| "ACR created when?" | On-demand (first env build or deploy) |
