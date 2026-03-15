# 14 DP-100 Weak Areas — Targeted Review

Based on practice assessment (60% score, March 15 2026). This covers every question you got wrong with decision tables and the exact reasoning.

---

## SECTION 1: Data & Datasets — What Creates What?

You missed: **Q6** (dataset vs pipeline for metadata reference)

| What you want | What to use | Why |
|---|---|---|
| Reference to data WITH metadata copy, NO data copy | **Create a data asset (dataset)** | Stores pointer + metadata only |
| Move/transform data between services | **Azure Data Factory / Pipeline** | ETL process, copies data |
| Store connection info to external storage | **Register a datastore** | Connection only, no metadata |
| Process data in a workflow | **Pipeline job** | Multi-step processing |

> **Key insight**: A data asset = pointer + metadata. Datastore = connection. Pipeline = workflow. These are 3 DIFFERENT things.

**MS Learn**: [Make data available in Azure Machine Learning](https://learn.microsoft.com/training/modules/make-data-available-azure-machine-learning/)

---

## SECTION 2: MLflow — Which Method Does What?

You missed: **Q9** (set tracking URI first), **Q14** (get_run vs log_artifact for retrieval)

### MLflow Setup Order (LOCAL environment)

```
1. mlflow.set_tracking_uri(uri)   ← FIRST (connect to workspace)
2. mlflow.set_experiment("name")  ← SECOND (set experiment)
3. mlflow.start_run()             ← THIRD (begin logging)
```

> **Q9 trap**: Inside Azure ML jobs, tracking URI is auto-set. From LOCAL → you MUST set it first.

### MLflow Methods Decision Table

| I want to... | Method | Returns |
|---|---|---|
| **Log** a parameter (input) | `mlflow.log_param("key", val)` | Nothing |
| **Log** a metric (output) | `mlflow.log_metric("key", val)` | Nothing |
| **Log** a file/plot | `mlflow.log_artifact("file.png")` | Nothing |
| **Log** everything automatically | `mlflow.autolog()` | Nothing |
| **Save** model versions | `mlflow.register_model()` | Model version |
| **Retrieve** run metadata, metrics, params | `MlflowClient().get_run(run_id)` | Run object with .data.metrics, .data.params |
| **Search** across runs | `mlflow.search_runs()` | DataFrame |

> **Q14 trap**: `log_artifact()` WRITES data. `get_run()` READS data. Don't confuse logging (write) with retrieval (read).

**MS Learn**: [Track ML experiments and models with MLflow](https://learn.microsoft.com/training/modules/train-models-training-mlflow-jobs/)

---

## SECTION 3: Compute — Which Class for What?

You missed: **Q10** (AmlCompute vs ComputeInstance for 4-node cluster)

| Scenario | Class | Why |
|---|---|---|
| Single dev VM, notebooks, 1 user | `ComputeInstance` | Single node ONLY, can't scale |
| Multi-node cluster for training | `AmlCompute` | Supports 1-N nodes, auto-scale |
| External VM you already have | Attached compute | Bring your own |
| No infra management needed | Serverless compute | Pay per job |
| Real-time endpoint hosting | `ManagedOnlineEndpoint` | Not a training compute |

> **Q10 trap**: `ComputeInstance` = ALWAYS 1 node. Question said "4 instances" → must be `AmlCompute`.

### Decision flow:
```
Need multiple nodes? → AmlCompute
Need just 1 VM for dev? → ComputeInstance
Have an existing VM? → Attached compute
Need GPU? → AmlCompute with GPU VM size
```

**MS Learn**: [Work with compute targets](https://learn.microsoft.com/training/modules/use-compute-contexts-in-aml/)

---

## SECTION 4: Running Scripts — SDK v2 Classes

You missed: **Q23** (command vs environment for running scripts)

| I want to... | Class/Function | Package |
|---|---|---|
| **Run** a training script as a job | `command()` | `azure.ai.ml` |
| **Define** packages/Docker for a job | `Environment()` | `azure.ai.ml.entities` |
| **Define** data inputs for a job | `Input()` | `azure.ai.ml` |
| **Register** a trained model | `Model()` | `azure.ai.ml.entities` |
| **Create** a compute cluster | `AmlCompute()` | `azure.ai.ml.entities` |
| **Submit** any job | `ml_client.jobs.create_or_update(job)` | `azure.ai.ml` |

> **Q23 trap**: `Environment` defines WHERE the script runs (packages). `command()` is HOW you run the script. The question asked "run a script" → answer is `command`.

```python
# The command() function is the entry point for running scripts
job = command(
    code="./src",                          # folder with script
    command="python train.py",             # what to execute
    environment="AzureML-sklearn@latest",  # Environment (packages)
    compute="aml-cluster"                  # Compute (hardware)
)
ml_client.jobs.create_or_update(job)       # Submit
```

**MS Learn**: [Run a training script as a command job](https://learn.microsoft.com/training/modules/run-training-script-command-job-azure-machine-learning/)

---

## SECTION 5: Hyperparameter Tuning — Sampling & Distributions

You missed: **Q17** (Grid vs Random for large space), **Q19** (continuous vs discrete distributions)

### Sampling Algorithm Decision Table

| Scenario | Algorithm | Why |
|---|---|---|
| Try ALL combinations (small space) | **Grid** | Exhaustive, only `Choice` |
| Large space, need speed | **Random** | Fast, supports ALL distributions |
| Informed search, use past results | **Bayesian** | Smart, only `Choice/Uniform/QUniform` |
| Best coverage, not truly random | **Sobol** (Random variant) | More uniform than pure random |

> **Q17 trap**: "Large search space + find optimal quickly + minimize time" → **Random**, not Grid. Grid tries EVERYTHING = slowest.

### Distribution Types — Continuous vs Discrete

| Distribution | Type | Use for |
|---|---|---|
| `Uniform` | **Continuous** | Evenly spread real values |
| `Normal` | **Continuous** | Bell curve, real values |
| `LogUniform` | **Continuous** | Learning rates (orders of magnitude) |
| `LogNormal` | **Continuous** | Log-scale bell curve |
| `Choice` | **Discrete** | Pick from a list |
| `Randint` | **Discrete** | Random integer |
| `QUniform` | **Discrete** | Quantized (rounded) uniform |
| `QNormal` | **Discrete** | Quantized (rounded) normal |
| `QLogUniform` | **Discrete** | Quantized log-uniform |
| `QLogNormal` | **Discrete** | Quantized log-normal |

> **Q19 trap**: Question said "continuous" → `Normal`, `Uniform`, `LogUniform`, `LogNormal`. The "Q" prefix = quantized = **discrete**.

### Quick rule:
- **No Q prefix** → Continuous (Normal, Uniform, LogUniform)
- **Q prefix** → Discrete/Quantized (QNormal, QUniform, QLogNormal)
- **Choice/Randint** → Always discrete

**MS Learn**: [Hyperparameter tuning a model (v2)](https://learn.microsoft.com/azure/machine-learning/how-to-tune-hyperparameters)

---

## SECTION 6: Pipelines — Passing Data, Scheduling, Components

You missed: **Q26** (monitoring), **Q27** (passing data), **Q28** (cron), **Q29** (component YAML)

### Pipeline Monitoring

| Action | Where |
|---|---|
| Submit pipeline | Authoring page (SDK, CLI, or Studio) |
| Monitor status | **Jobs page → submission list → click job link** |
| NOT here | Authoring page does NOT show job status |

> **Q26 trap**: After submitting, go to **Jobs page**, not back to the authoring page.

### Passing Data Between Steps

**SDK v2** (current exam focus):
```python
@pipeline(default_compute="aml-cluster")
def my_pipeline(raw_data):
    prep_step = prep_component(input_data=raw_data)
    train_step = train_component(
        training_data=prep_step.outputs.cleaned_data  # ← output → input
    )
```

**SDK v1** (still tested! Q27 was SDK v1):
```python
prepped_data = OutputFileDatasetConfig('prepped')  # ← MUST define this first

step1 = PythonScriptStep(name="Prepare",
    arguments=['--out_folder', prepped_data])

step2 = PythonScriptStep(name="Train",
    arguments=['--training-data', prepped_data.as_input()])  # ← .as_input()
```

> **Q27 trap**: You MUST create `OutputFileDatasetConfig` BEFORE defining the steps. The wrong answer was missing this definition.

### Cron Syntax for Scheduling

```
┌──── minute (0-59)
│ ┌── hour (0-23)
│ │ ┌── day of month (1-31)
│ │ │ ┌── month (1-12)
│ │ │ │ ┌──── day of week (0=Sun, 1=Mon, ..., 6=Sat)
│ │ │ │ │
* * * * *
```

| Schedule | Cron Expression |
|---|---|
| Every day at 1:15 PM | `15 13 * * *` |
| Every Wednesday at 1:15 PM | `15 13 * * 3` |
| Every Monday at 9:00 AM | `0 9 * * 1` |
| Every 1st of month at midnight | `0 0 1 * *` |
| Every weekday at 6:30 AM | `30 6 * * 1-5` |

> **Q28 trap**: Wednesday = `3` (0=Sun, 1=Mon, 2=Tue, **3=Wed**). The wrong answer had `*` (every day) instead of `3`.

### Component YAML — Required Sections

| Section | Required? | What it defines |
|---|---|---|
| `name`, `display_name`, `type` | **Yes** | Metadata of the component |
| `inputs` | **Yes** | What data/params the component receives |
| `outputs` | **Yes** | What data the component produces |
| `environment` | **Yes** | Docker + conda for execution |
| `code` | **Yes** | Path to the script |
| `command` | **Yes** | How to run the script |

> **Q29 trap**: ALL four are required: metadata + inputs + **outputs** + environment. The wrong answer was missing outputs.

**MS Learn**: [Run pipelines in Azure Machine Learning](https://learn.microsoft.com/training/modules/run-pipelines-azure-machine-learning/)

---

## SECTION 7: Deployment — Scoring Scripts & Classes

You missed: **Q33** (init vs main for batch), **Q34** (run method for feature engineering), **Q36** (ManagedOnlineDeployment vs OnlineEndpoint)

### Scoring Script Functions

| Function | When called | Purpose |
|---|---|---|
| `init()` | **Once** at deployment start | Load model into memory |
| `run(data)` | **Each request** (online) or **each mini-batch** (batch) | Process data, return predictions |

> **Q33 trap**: `init()` loads the model, not `main()`. `main()` is for running Python scripts directly, not for scoring scripts.

> **Q34 trap**: Feature engineering on incoming data goes in `run()` because it's called for EVERY request. `init()` only runs once at startup.

### Deployment Classes Decision Table

| I want to... | Class | What it creates |
|---|---|---|
| Define the endpoint URL + auth | `ManagedOnlineEndpoint` | The URL/entry point |
| Define model + VM + environment + scoring script | `ManagedOnlineDeployment` | The actual deployment behind the endpoint |
| Invoke/test the endpoint | `ml_client.online_endpoints.invoke()` | N/A |
| Delete everything | `ml_client.online_endpoints.begin_delete()` | N/A |

> **Q36 trap**: The question asked for "name, instance_type, environment, code_configuration" → these are DEPLOYMENT properties, not endpoint properties. Answer: `ManagedOnlineDeployment`.

### Endpoint vs Deployment — The Difference

```
Endpoint (ManagedOnlineEndpoint)     Deployment (ManagedOnlineDeployment)
├── name: "my-endpoint"              ├── name: "blue"
├── auth_mode: "key"                 ├── model: "azureml:my-model:1"
└── traffic: {"blue": 90, "green": 10}  ├── instance_type: "Standard_DS3_v2"
                                     ├── instance_count: 1
                                     ├── environment: "azureml:my-env:1"
                                     └── scoring_script: "score.py"
```

**MS Learn**: [Deploy a model to a managed online endpoint](https://learn.microsoft.com/training/modules/deploy-model-managed-online-endpoint/)

---

## SECTION 8: Prompt Flow — Nodes, Variants, YAML

You missed: **Q39** (tool node), **Q42** (flow.dag.yaml), **Q43** (variant)

### Prompt Flow Node Types

| Node Type | Purpose | Example |
|---|---|---|
| **Prompt** node | Define LLM instructions, system messages | "Summarize this article in 3 bullet points" |
| **Tool** node | Data processing, task execution, algorithms | Python script to parse JSON, call API |
| **LLM** node | Send prompts to a language model | Call GPT-4 with a constructed prompt |

> **Q39 trap**: "handles data processing, task execution, algorithmic operations" → that's a **Tool** node, not a chain or prompt.

### Prompt Flow Files

| File | Purpose |
|---|---|
| `flow.dag.yaml` | **Defines the flow structure** — nodes, connections, chaining logic |
| `flow.meta.yaml` | Flow metadata (name, description) |
| `inputs.json` | Test input data for the flow |
| `outputs.json` | Captured outputs from flow runs |

> **Q42 trap**: Chaining logic (output of node A → input of node B) is defined in `flow.dag.yaml`, NOT in inputs.json.

### Variants

A **variant** is a different version of a prompt node, used to compare which prompt produces better results.

| Concept | What it is |
|---|---|
| **Variant** | Different prompt configuration to A/B test |
| **Sample** | A single test input/case |
| **Dataset** | Collection of test inputs |
| **Endpoint** | Deployed flow for production |

> **Q43 trap**: To COMPARE metrics across different prompts → create **variants**. A sample is just one test case.

**MS Learn**: [Prompt flow in Azure AI Foundry](https://learn.microsoft.com/training/modules/create-manage-prompt-flow/)

---

## SECTION 9: Azure AI Search — Indexers & Knowledge Stores

You missed: **Q44** (knowledge store in indexer), **Q45** (enrichment pipeline in indexer)

### Azure AI Search Architecture

```
Data Source → Indexer → Skillset (AI enrichment) → Index (searchable)
                 │
                 └→ Knowledge Store (tables, JSON, images in Azure Storage)
```

### What Goes Where

| Component | Configured in | Purpose |
|---|---|---|
| Data source | Standalone resource | Points to Blob/SQL/etc. |
| Skillset | Standalone resource | AI enrichment steps (NER, sentiment, etc.) |
| Index | Standalone resource | Searchable fields |
| Knowledge store | **In the indexer** | Persist enriched data to Azure Storage |
| Enrichment pipeline | **In the indexer** | Chain skillsets to process documents |

> **Q44 trap**: Knowledge store is configured in the **indexer**, NOT in the search service or the index.
> **Q45 trap**: To add AI enrichment (like Text Analytics for health), configure an **enrichment pipeline in the indexer** with the skill and output to the same index.

### Resource Creation Order

```
1. Data source (where's the data?)
2. Skillset (how to enrich it?)
3. Index (what fields to search?)
4. Indexer (connect everything, run it)
```

> The indexer is ALWAYS last because it orchestrates everything else.

**MS Learn**: [Create a knowledge mining solution with Azure AI Search](https://learn.microsoft.com/training/modules/create-enrichment-pipeline-azure-cognitive-search/)

---

## MASTER DECISION TABLE — "If the question says X, the answer is Y"

| Question pattern | Wrong answer you picked | Correct answer | Why |
|---|---|---|---|
| "Reference to data with metadata, no copy" | Pipeline | **Data asset (dataset)** | Dataset = pointer + metadata |
| "MLflow track LOCAL experiments, what FIRST?" | Start training | **Set tracking URI** | Local needs URI; jobs don't |
| "Cluster with 4 instances" | ComputeInstance | **AmlCompute** | ComputeInstance = always 1 node |
| "Retrieve run metrics with MlflowClient" | log_artifact() | **get_run()** | log = write; get = read |
| "Large search space, fast, minimize time" | Grid | **Random** | Grid = exhaustive = slowest |
| "Continuous hyperparameter distribution" | QLogNormal | **Normal** | Q prefix = discrete |
| "Run training script with SDK v2" | Environment | **command()** | Environment = packages; command = execution |
| "Monitor pipeline after submit" | Authoring page | **Jobs → submission list** | Authoring page has no status |
| "Pass data between pipeline steps (v1)" | Missing OutputFileDatasetConfig | **Define OutputFileDatasetConfig first** | Must create intermediate data object |
| "Every Wednesday at 1:15 PM cron" | `15 13 * * *` | **`15 13 * * 3`** | Wed = 3 (0=Sun) |
| "Component YAML required sections" | Without outputs | **metadata + inputs + outputs + env** | ALL four needed |
| "Load model in batch scoring script" | main | **init()** | init = load model; run = score |
| "Feature engineering on incoming data" | Connect to workspace | **Update run() method** | run() processes each request |
| "Endpoint name, instance_type, env, code" | OnlineEndpoint | **ManagedOnlineDeployment** | These are deployment properties |
| "Node for data processing/task execution" | Chain nodes | **Configure as tool node** | Tool = processing; Prompt = LLM instructions |
| "Where is chaining logic defined?" | inputs.json | **flow.dag.yaml** | DAG file = flow structure |
| "Compare metrics across prompts" | Sample | **Variant** | Variant = A/B test prompts |
| "Where to configure knowledge store?" | Search service | **In the indexer** | Indexer orchestrates persistence |
| "Add AI enrichment to search index" | Call API at query time | **Enrichment pipeline in indexer** | Indexer applies skills and populates index |
