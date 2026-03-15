# 14 DP-100 Weak Areas — Targeted Review

Practice assessment score: 60%. These are the 4 areas flagged for improvement with decision tables and MS Learn links.

---

## AREA 1: Design and Prepare a Machine Learning Solution

### Data Assets vs Datastores vs Pipelines

| Concept | What it does | Creates a copy of data? |
|---|---|---|
| **Data asset (dataset)** | Reference to data + metadata copy | No — pointer only |
| **Datastore** | Connection info to storage (Blob, ADLS, SQL) | No — connection only |
| **Pipeline** | Multi-step ML workflow | Depends on steps |
| **Azure Data Factory** | ETL — moves/transforms data | Yes |

**When to use which:**

| I need to... | Use |
|---|---|
| Point to data + store metadata, no copy | **Data asset** |
| Connect to an external storage account | **Datastore** |
| Run a multi-step training workflow | **Pipeline job** |
| Move data between services | **Azure Data Factory** |

### Compute Types — When to Use What

| Scenario | Compute Type | Class |
|---|---|---|
| Single dev VM, notebooks, 1 user | Compute Instance | `ComputeInstance` |
| Multi-node cluster for training (1-N nodes) | Compute Cluster | `AmlCompute` |
| Already have an Azure VM | Attached compute | N/A |
| No infra to manage | Serverless | N/A |

> `ComputeInstance` = ALWAYS 1 node. If the question mentions multiple nodes/instances → `AmlCompute`.

### Data Access Modes

| Mode | Default for | Description |
|---|---|---|
| `ro_mount` | Inputs | Read-only mount |
| `rw_mount` | Outputs | Read-write mount |
| `download` | N/A | Copy all data to local disk |
| `upload` | N/A | Write data to storage |
| `direct` | N/A | Pass URI only (for Spark/large data) |

### MS Learn for this section:
- [Make data available in Azure Machine Learning](https://learn.microsoft.com/training/modules/make-data-available-azure-machine-learning/)
- [Work with compute targets](https://learn.microsoft.com/training/modules/use-compute-contexts-in-aml/)
- [Data concepts in Azure ML](https://learn.microsoft.com/azure/machine-learning/concept-data)

---

## AREA 2: Explore Data and Run Experiments

### MLflow — Setup Order (from local machine)

```
1. mlflow.set_tracking_uri(uri)   ← FIRST (connect to workspace)
2. mlflow.set_experiment("name")  ← SECOND (name the experiment)
3. mlflow.start_run()             ← THIRD (begin logging)
```

> Inside Azure ML jobs → tracking URI is set AUTOMATICALLY. From local → YOU must set it first.

### MLflow Methods — Read vs Write

| I want to... | Method | Action |
|---|---|---|
| Log a parameter (input config) | `mlflow.log_param("key", val)` | **Write** |
| Log a metric (output number) | `mlflow.log_metric("key", val)` | **Write** |
| Log a file/plot | `mlflow.log_artifact("file.png")` | **Write** |
| Log everything automatically | `mlflow.autolog()` | **Write** |
| Save model versions to registry | `mlflow.register_model()` | **Write** |
| **Retrieve** run metadata/metrics | `MlflowClient().get_run(id)` | **Read** |
| **Search** across multiple runs | `mlflow.search_runs()` | **Read** |

> `log_*` methods = WRITE. `get_run()` / `search_runs()` = READ. Don't mix them up.

### Hyperparameter Tuning — Sampling Algorithms

| Algorithm | When to use | Supports |
|---|---|---|
| **Grid** | Small space, try ALL combos | `Choice` only |
| **Random** | Large space, need speed | ALL distributions |
| **Bayesian** | Informed search, fewer trials | `Choice`, `Uniform`, `QUniform` only |

> "Large search space + minimize time" → **Random** (not Grid). Grid is the slowest.

### Distributions — Continuous vs Discrete

| Continuous (no Q prefix) | Discrete (Q prefix or Choice) |
|---|---|
| `Uniform` | `QUniform` |
| `Normal` | `QNormal` |
| `LogUniform` | `QLogUniform` |
| `LogNormal` | `QLogNormal` |
| — | `Choice` |
| — | `Randint` |

> **Rule**: Q prefix = Quantized = Discrete. No Q prefix = Continuous.

### Early Termination Policies

| Policy | Stops runs that are... | Key param |
|---|---|---|
| **BanditPolicy** | Worse than best by `slack_factor`/`slack_amount` | `slack_amount=0.35` → 35% worse |
| **MedianStoppingPolicy** | Worse than the median of all runs | `evaluation_interval` |
| **TruncationSelectionPolicy** | In the bottom X% | `truncation_percentage` |

> `delay_evaluation` = wait N intervals before applying any policy (lets trials warm up).

### MS Learn for this section:
- [Track ML experiments with MLflow](https://learn.microsoft.com/training/modules/train-models-training-mlflow-jobs/)
- [Find the best model with Automated ML](https://learn.microsoft.com/training/modules/automate-model-selection-with-azure-automl/)
- [Hyperparameter tuning a model (v2)](https://learn.microsoft.com/azure/machine-learning/how-to-tune-hyperparameters)

---

## AREA 3: Train and Deploy Models

### Running Scripts in SDK v2

| I want to... | Use | Not this |
|---|---|---|
| **Run** a script as a job | `command()` | ~~Environment~~ |
| **Define** packages for a job | `Environment()` | ~~command~~ |
| **Define** input data | `Input()` | ~~Output~~ |
| **Submit** the job | `ml_client.jobs.create_or_update()` | — |

> `command()` = how to RUN. `Environment()` = packages/Docker WHERE it runs. Different things.

### Pipelines

**Monitoring**: After submitting → go to **Jobs page → submission list**. The authoring page does NOT show job status.

**Passing data between steps (SDK v2)**:
```python
prep_step = prep_component(input_data=raw_data)
train_step = train_component(training_data=prep_step.outputs.cleaned_data)
```

**Cron scheduling**:
```
minute  hour  day_of_month  month  day_of_week
  15     13       *           *        3         ← Wednesday 1:15 PM
```
Days: 0=Sun, 1=Mon, 2=Tue, **3=Wed**, 4=Thu, 5=Fri, 6=Sat

**Component YAML — ALL 4 required**: metadata + inputs + outputs + environment

### Scoring Script (for endpoints)

| Function | Called when | Purpose |
|---|---|---|
| `init()` | **Once** at startup | Load model into memory |
| `run(data)` | **Each request** | Process data + return predictions |

> `init()` loads model. `run()` does inference. Feature engineering on incoming data → put it in `run()`.

### Endpoint vs Deployment

| Class | What it defines |
|---|---|
| `ManagedOnlineEndpoint` | URL + auth mode + traffic routing |
| `ManagedOnlineDeployment` | Model + VM size + instance count + environment + scoring script |

> If the question mentions `instance_type`, `environment`, `scoring_script` → that's a **Deployment** property, not an Endpoint.

### Batch Endpoints

| Setting | Purpose |
|---|---|
| `mini_batch_size` | Records per mini-batch (e.g., 50) |
| `instance_count` | Number of nodes |
| `output_action` | `APPEND_ROW` (single CSV) or `SUMMARY_ONLY` |
| `max_concurrency_per_instance` | Parallel processing per node |

### MS Learn for this section:
- [Run pipelines in Azure Machine Learning](https://learn.microsoft.com/training/modules/run-pipelines-azure-machine-learning/)
- [Deploy a model to a managed online endpoint](https://learn.microsoft.com/training/modules/deploy-model-managed-online-endpoint/)
- [Deploy batch inference pipelines](https://learn.microsoft.com/training/modules/deploy-batch-inference-pipelines-with-azure-machine-learning/)
- [Run a training script as a command job](https://learn.microsoft.com/training/modules/run-training-script-command-job-azure-machine-learning/)

---

## AREA 4: Optimize Language Models for AI Applications

### Prompt Flow Node Types

| Node Type | Purpose | Example |
|---|---|---|
| **Prompt** | Instructions/system messages for the LLM | "Summarize in 3 bullets" |
| **Tool** | Data processing, task execution, API calls | Python script to parse JSON |
| **LLM** | Send prompts to a language model | Call GPT-4 |

> "Data processing + task execution + algorithms" → **Tool** node.

### Prompt Flow Key Files

| File | What it does |
|---|---|
| `flow.dag.yaml` | Defines flow structure + chaining logic between nodes |
| `flow.meta.yaml` | Flow metadata (name, description) |
| `inputs.json` | Test input data |
| `outputs.json` | Captured output data |

> "Chaining logic" (output A → input B) → defined in `flow.dag.yaml`.

### Prompt Flow Concepts

| Term | What it is |
|---|---|
| **Variant** | Different version of a prompt to A/B test and compare metrics |
| **Sample** | A single test input case |
| **Dataset** | Collection of test inputs |
| **Endpoint** | Deployed flow for production |

> "Compare different prompts side by side" → create **variants**.

### Azure AI Search Architecture

```
Data Source → Indexer → Skillset → Index (searchable)
                 │
                 └→ Knowledge Store (Azure Storage)
```

**Creation order**: Data source → Skillset → Index → Indexer (always last)

| What | Configured where |
|---|---|
| Knowledge store persistence | **In the indexer** |
| AI enrichment (NER, sentiment, etc.) | **Enrichment pipeline in the indexer** |
| Searchable fields | In the index |

> Knowledge store and enrichment pipeline are BOTH configured in the **indexer**, not in the search service or index.

### Evaluation Metrics for LLM Flows

| Metric | Measures |
|---|---|
| **Fluency** | Grammar, spelling, readability |
| **Groundedness** | Is the output supported by source evidence? |
| **Relevance** | Does the output address the user's question? |
| **Similarity** | How close is output to a reference answer? |
| **Coherence** | Does the output flow logically? |

> Misspellings + bad grammar → evaluate **fluency**.

### MS Learn for this section:
- [Prompt flow in Azure AI Foundry](https://learn.microsoft.com/training/modules/create-manage-prompt-flow/)
- [Azure AI Search (knowledge mining)](https://learn.microsoft.com/training/modules/create-enrichment-pipeline-azure-cognitive-search/)
- [Fine-tune Azure OpenAI models](https://learn.microsoft.com/training/modules/fine-tune-azure-openai/)
- [Deploy models as serverless APIs](https://learn.microsoft.com/training/modules/deploy-models-serverless-api/)
