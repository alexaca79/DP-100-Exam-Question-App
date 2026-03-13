# DP-100 Trap Questions — What Will Trip You Up

These are the exact patterns that trick people on the real exam. Each section covers a "trap" — the wrong answer that LOOKS right, why it's wrong, and what the actual answer is.

---

## TRAP 1: MLflow Model vs Custom Model Deployment

**The question**: "You deploy a trained model to a managed online endpoint. What do you need to provide?"

**The trap**: Answering "a scoring script and environment" for EVERY deployment.

**The truth**:
- **MLflow model** (`AssetTypes.MLFLOW_MODEL`) → **NO scoring script, NO environment needed**. Azure auto-generates both.
- **Custom model** (`AssetTypes.CUSTOM_MODEL`) → **YES** scoring script (`score.py` with `init()` + `run()`) **AND** environment (conda.yml + Docker image).

**How to tell in the question**: Look for keywords like "MLflow model", "logged with mlflow.sklearn.log_model", or "AssetTypes.MLFLOW_MODEL". If any of these appear → no scoring script.

---

## TRAP 2: AutoML Requires MLTABLE (Not URI_FILE)

**The question**: "You configure an AutoML classification job with a CSV registered as a URI_FILE data asset. What happens?"

**The trap**: Assuming URI_FILE works because CSV is tabular data.

**The truth**: AutoML **ONLY** accepts `MLTABLE` data assets. URI_FILE and URI_FOLDER will cause the job to **fail**. The MLTable file defines the schema (delimiter, headers, column types) that AutoML needs.

**Remember**: AutoML = MLTABLE. Always. No exceptions.

---

## TRAP 3: log_model vs log_artifact

**The question**: "You trained a model and want to deploy it later. You call `joblib.dump(model, 'model.pkl')` then `mlflow.log_artifact('model.pkl')`. Can you deploy this model to a managed endpoint without a scoring script?"

**The trap**: Thinking `log_artifact` is enough because the model file is there.

**The truth**: **NO**. `log_artifact` saves a plain file with no metadata. Only `mlflow.<flavor>.log_model()` creates the MLmodel file with:
- Flavor info (sklearn, xgboost, etc.)
- Signature (input/output schema)
- Conda environment
- Run linkage

Without the MLmodel file, Azure ML can't auto-generate the scoring script → you need a custom deployment.

| Method | Creates MLmodel? | Deploy without score.py? |
|---|---|---|
| `mlflow.sklearn.log_model()` | Yes | Yes |
| `mlflow.log_artifact("model.pkl")` | No | No |

---

## TRAP 4: Bayesian Sampling Limitations

**The question**: "You configure a sweep job with Bayesian sampling and `LogUniform` for learning rate. What happens?"

**The trap**: Assuming Bayesian works with all distribution types.

**The truth**: Bayesian sampling ONLY supports:
- `Choice` (discrete)
- `Uniform` (continuous)
- `QUniform` (quantized)

It does **NOT** support: `Normal`, `LogNormal`, `LogUniform`, `QNormal`, `QLogNormal`, `QLogUniform`, `Randint`.

And `Grid` sampling ONLY supports `Choice`.

| Sampling | Supports |
|---|---|
| **Grid** | `Choice` only |
| **Random** | ALL types |
| **Bayesian** | `Choice`, `Uniform`, `QUniform` only |

---

## TRAP 5: ${{inputs.X}} vs ${{search_space.X}} vs ${{parent.jobs.X}}

**The question**: Shows YAML pipeline/sweep code and asks what reference syntax to use.

**The trap**: Mixing up the reference scopes.

**The truth**:

| Context | Syntax | Example |
|---|---|---|
| Job-level input | `${{inputs.X}}` | `${{inputs.training_data}}` |
| Job-level output | `${{outputs.X}}` | `${{outputs.model}}` |
| Sweep search space | `${{search_space.X}}` | `${{search_space.learning_rate}}` |
| Pipeline parent input | `${{parent.inputs.X}}` | `${{parent.inputs.raw_data}}` |
| Pipeline cross-step | `${{parent.jobs.step.outputs.X}}` | `${{parent.jobs.prep.outputs.data}}` |

The most commonly tested: `${{parent.jobs.<step_name>.outputs.<output_name>}}` for cross-step data flow in pipelines.

---

## TRAP 6: Compute Instance vs Compute Cluster

**The question**: "You need to run an AutoML job / pipeline job / training script. Which compute should you use?"

**The trap**: Picking compute instance because it's simpler.

**The truth**:

| Use Case | Correct Compute |
|---|---|
| Notebooks, experimentation, development | **Compute Instance** |
| Training jobs (command, sweep) | **Compute Cluster** |
| AutoML | **Compute Cluster** |
| Designer pipelines | **Compute Cluster** |
| Pipeline jobs | **Compute Cluster** |
| Real-time endpoint (online) | **Managed Online Endpoint** (instance_type) |
| Batch endpoint | **Compute Cluster** |

**Compute instances**: Single VM, one user only, NOT for production jobs.
**Compute clusters**: Multi-node, auto-scale, for all training and batch jobs.

---

## TRAP 7: begin_create_or_update vs create_or_update

**The question**: Shows SDK v2 code and asks why it's not waiting for the operation to complete, or the endpoint isn't ready.

**The trap**: Forgetting `.result()` on long-running operations.

**The truth**:
- `begin_create_or_update()` → Returns a **poller** (LRO). Call `.result()` to wait.
- `create_or_update()` (no `begin_`) → Synchronous, completes immediately.

**When is `begin_` needed?**
- Creating/deleting **compute** → `ml_client.compute.begin_create_or_update()`
- Creating/deleting **endpoints** → `ml_client.online_endpoints.begin_create_or_update()`
- Creating/deleting **deployments** → `ml_client.online_deployments.begin_create_or_update()`

**When is it NOT needed?**
- Creating **environments** → `ml_client.environments.create_or_update()`
- Creating **data assets** → `ml_client.data.create_or_update()`
- Creating **components** → `ml_client.components.create_or_update()`

---

## TRAP 8: Traffic Must Sum to 100%

**The question**: "You deploy 'blue' and 'green' to an endpoint and set `endpoint.traffic = {'green': 10}`. What happens?"

**The trap**: Thinking only specifying the new deployment is enough.

**The truth**: You must specify ALL deployments and they must sum to 100%.

```python
# WRONG — blue gets 0%, only green gets traffic
endpoint.traffic = {"green": 10}

# WRONG — sums to 110%
endpoint.traffic = {"blue": 100, "green": 10}

# CORRECT — sums to 100%
endpoint.traffic = {"blue": 90, "green": 10}
```

To test a specific deployment without affecting traffic, use `deployment_name`:
```python
ml_client.online_endpoints.invoke(
    endpoint_name="my-endpoint",
    request_file="data.json",
    deployment_name="green"  # bypasses traffic rules
)
```

---

## TRAP 9: Scoring Script Functions

**The question**: "What functions must be in a scoring script for an online endpoint?"

**The trap**: Adding `predict()`, `score()`, `main()`, or other wrong function names.

**The truth**: Exactly TWO functions:
1. `init()` — Called ONCE when deployment starts. Load model into memory.
2. `run(raw_data)` — Called for EACH request. Return predictions.

```python
def init():
    global model
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'model', 'model.pkl')
    model = joblib.load(model_path)

def run(raw_data):
    data = json.loads(raw_data)['data']
    predictions = model.predict(data)
    return predictions.tolist()
```

**Key detail**: `AZUREML_MODEL_DIR` is the env variable pointing to where the model is stored. This is set by Azure ML automatically.

---

## TRAP 10: DefaultAzureCredential Chain Order

**The question**: "DefaultAzureCredential fails on your local machine. You've run `az login`. What should you check?"

**The trap**: Not knowing the auth chain order.

**The truth**: DefaultAzureCredential tries in this exact order:
1. **EnvironmentCredential** — Checks `AZURE_CLIENT_ID` + `AZURE_TENANT_ID` + `AZURE_CLIENT_SECRET`
2. **ManagedIdentityCredential** — Works on Azure VMs, App Service (fails silently on local)
3. **AzureCliCredential** — Uses `az login` session
4. **AzurePowerShellCredential** — Uses `Connect-AzAccount`
5. **InteractiveBrowserCredential** — Opens browser login

If `az login` works but DefaultAzureCredential fails, check if environment variables (`AZURE_CLIENT_ID`, etc.) are set to wrong values — they take priority over Azure CLI!

---

## TRAP 11: Managed Identity Roles (ARM vs Data Plane)

**The question**: "You assign the 'Reader' role to your compute's managed identity on a storage account. The job fails to read data."

**The trap**: Thinking "Reader" can read blob data.

**The truth**: There are **ARM roles** (manage the resource) and **Data roles** (access the data):

| Role | Type | Can read blob data? |
|---|---|---|
| Reader | ARM | **NO** — Can only view the storage account in Azure Portal |
| Contributor | ARM | **NO** — Can manage the account but NOT read data |
| Storage Blob Data Reader | Data | **YES** — Can read blobs |
| Storage Blob Data Contributor | Data | **YES** — Can read + write blobs |
| Storage Blob Data Owner | Data | **YES** — Full control + permissions |

For compute to read training data: **Storage Blob Data Reader** is the minimum.

---

## TRAP 12: AzureML Data Scientist Role Limitations

**The question**: "A data scientist needs to train models AND create a new compute cluster. What role(s) do they need?"

**The trap**: Thinking AzureML Data Scientist covers everything.

**The truth**: **AzureML Data Scientist** can:
- Submit jobs ✓
- Register data/models ✓
- Deploy to endpoints ✓
- Cannot create/delete compute ✗
- Cannot modify workspace settings ✗

If they also need compute creation → add **AzureML Compute Operator** or **Contributor**.

---

## TRAP 13: Batch vs Online Endpoint Output

**The question**: "How do you get predictions from a batch endpoint?"

**The trap**: Expecting an HTTP response like online endpoints.

**The truth**:

| | Online Endpoint | Batch Endpoint |
|---|---|---|
| Response | Synchronous HTTP response | Asynchronous — file in storage |
| Output | JSON in HTTP body | `predictions.csv` in Blob Storage |
| Compute | Managed instances | Compute cluster |
| Output config | N/A | `APPEND_ROW` or `SUMMARY_ONLY` |

`APPEND_ROW` → All predictions appended to single CSV.
`SUMMARY_ONLY` → Only job summary, no per-row predictions.

---

## TRAP 14: @latest vs Specific Version

**The question**: "Your job references `AzureML-sklearn-1.0-ubuntu20.04-py38-cpu@latest` but the environment was recently updated and your code broke."

**The trap**: Always using `@latest` in production.

**The truth**:
- `@latest` → Gets newest version. Great for dev, risky for prod.
- `@1` or specific version → Pinned. Safe for production.
- In registered assets: `azureml:my-model:1` → version 1.

**Best practice**: Use `@latest` during development, pin specific versions for production jobs and deployments.

---

## TRAP 15: Pipeline YAML — Python vs CLI Syntax

**The question**: Shows code that mixes Python and YAML syntax for pipelines.

**The trap**: Using `${{parent.jobs...}}` in Python code or `.outputs.name` in YAML.

**The truth**:

| Feature | Python SDK v2 | CLI v2 YAML |
|---|---|---|
| Reference step output | `prep_step.outputs.cleaned_data` | `${{parent.jobs.prep_step.outputs.cleaned_data}}` |
| Reference pipeline input | Function parameter | `${{parent.inputs.raw_data}}` |
| Define pipeline | `@pipeline` decorator | `type: pipeline` in YAML |
| Load component | `load_component(source="file.yml")` | `component: azureml:name@latest` |

---

## TRAP 16: ACR Is NOT Created At Workspace Creation

**The question**: "Which resources are created when you create an Azure ML workspace?"

**The trap**: Including Azure Container Registry in the list.

**The truth**: Created **immediately**:
1. Azure Storage Account ✓
2. Azure Key Vault ✓
3. Application Insights ✓

Created **on-demand** (when first needed):
4. Azure Container Registry ✗ — Only when you build a custom environment or deploy a model

---

## TRAP 17: Responsible AI Principles Confusion

**The question**: Describes a scenario and asks which RAI principle applies.

**The trap**: Confusing fairness with inclusiveness, or transparency with accountability.

**Cheat sheet**:

| Principle | Ask yourself... |
|---|---|
| **Fairness** | Does the model discriminate against a group? |
| **Reliability & Safety** | Could the model cause harm or produce dangerous outputs? |
| **Privacy & Security** | Is user data being collected/used without consent? |
| **Inclusiveness** | Is the system leaving some users out or inaccessible? |
| **Transparency** | Can users understand HOW the model works and WHY it decided? |
| **Accountability** | Is someone responsible for the model's behavior? |

**Common confusion**:
- Disparate outcomes across demographics → **Fairness** (not Inclusiveness)
- Users can't understand predictions → **Transparency** (not Accountability)
- AI system not usable by disabled people → **Inclusiveness** (not Fairness)

---

## TRAP 18: Sweep Job Primary Metric Must Be LOGGED

**The question**: "Your sweep job completes but the best trial selection shows 'N/A' for the primary metric."

**The trap**: Setting `primary_metric="accuracy"` in sweep config but logging it as `"Accuracy"` (capital A) or not logging it at all.

**The truth**: The `primary_metric` name in sweep config must **exactly match** what you log with `mlflow.log_metric()`. Case-sensitive!

```python
# In training script:
mlflow.log_metric("val_accuracy", 0.95)  # ← this name

# In sweep config:
sweep_job = command_job.sweep(
    primary_metric="val_accuracy",  # ← must match EXACTLY
    goal="maximize"
)
```

---

## TRAP 19: MLflow Tracking URI — Local vs Job

**The question**: "You run `mlflow.log_metric('accuracy', 0.95)` from a local notebook. The metric doesn't appear in Azure ML Studio."

**The trap**: Assuming MLflow automatically connects to Azure ML.

**The truth**:
- **Inside an Azure ML job**: Tracking URI is set AUTOMATICALLY. No setup needed.
- **From local/external machine**: You MUST call `mlflow.set_tracking_uri(uri)` first.

```python
# Get URI from workspace
uri = ml_client.workspaces.get("my-workspace").mlflow_tracking_uri
mlflow.set_tracking_uri(uri)
# NOW your logs go to Azure ML
```

---

## TRAP 20: Early Termination delay_evaluation

**The question**: "You set BanditPolicy(evaluation_interval=1, slack_factor=0.1). All your trials get terminated after the first evaluation."

**The trap**: Not using `delay_evaluation` to let trials warm up.

**The truth**: Without `delay_evaluation`, the policy starts checking from the FIRST interval. Early trials may have bad metrics while still warming up.

```python
BanditPolicy(
    evaluation_interval=2,    # Check every 2 intervals
    slack_factor=0.1,         # Allow 10% slack
    delay_evaluation=5        # Don't check until after interval 5
)
```

`delay_evaluation=5` means: "Don't terminate anything for the first 5 evaluation intervals, regardless of performance." This gives models time to converge.
