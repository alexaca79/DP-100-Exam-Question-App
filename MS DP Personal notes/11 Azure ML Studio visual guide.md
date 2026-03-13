# Azure ML Studio — The Visual Interface Guide for DP-100

Azure ML Studio is the **web-based UI** for Azure Machine Learning. While the SDK v2 and CLI v2 let you do everything programmatically, Studio gives you a visual interface to manage your workspace, monitor jobs, explore data, build pipelines, and deploy models.

> **DP-100 Note**: The exam tests both the programmatic (SDK/CLI) and the Studio UI approach. Many questions show screenshots or describe the Studio interface and ask you to pick the right tab, button, or section.

---

## 1. Navigating Azure ML Studio

When you open Studio (`ml.azure.com`), you land on the **Home** page. The left sidebar has these key sections:

| Section | What It Does |
|---|---|
| **Authoring → Notebooks** | Interactive Jupyter environment on compute instances |
| **Authoring → Automated ML** | Create AutoML jobs via UI (no code) |
| **Authoring → Designer** | Visual drag-and-drop pipeline builder |
| **Assets → Data** | Manage data assets (URI_FILE, URI_FOLDER, MLTABLE) |
| **Assets → Jobs** | View all submitted jobs (command, sweep, pipeline, AutoML) |
| **Assets → Components** | Reusable pipeline building blocks |
| **Assets → Models** | Registered models with versions and metadata |
| **Assets → Endpoints** | Online and batch endpoints for serving models |
| **Assets → Environments** | Curated and custom environments |
| **Manage → Compute** | Compute instances, clusters, attached compute |
| **Manage → Datastores** | Connections to storage accounts |
| **Manage → Linked services** | External resource connections |

> **Exam tip**: If a question says "which section of Azure ML Studio..." — know the layout above.

---

## 2. Notebooks in Studio

Azure ML Studio includes a **built-in Jupyter environment** that runs on compute instances.

### Key features:
- Files stored in the workspace's **File Share** (not Blob Storage)
- Each user gets their own folder under `/Users/<username>/`
- Can run `.ipynb` and `.py` files
- Supports **IntelliSense** and **variable explorer**
- Notebooks connect to a **compute instance** (not cluster)
- Can clone Git repos directly into the file system

### Terminal access:
- Click the **Terminal** icon to open a bash terminal on the compute instance
- Use this to install packages: `pip install <package>`
- Run scripts: `python train.py --data diabetes.csv`

> **Exam tip**: Notebooks run on **compute instances** (single VM). Training **jobs** run on **compute clusters** (scalable). Don't confuse the two.

---

## 3. Automated ML in Studio (No-Code)

The Studio UI lets you create AutoML jobs without writing Python code.

### Steps:
1. **Select data** → Choose a registered MLTABLE data asset
2. **Configure job** → Pick task type (Classification, Regression, Forecasting)
3. **Select target column** → The column to predict
4. **Configure settings**:
   - Primary metric (accuracy, AUC_weighted, RMSE, etc.)
   - Allowed/blocked algorithms
   - Enable/disable ensemble models
   - Featurization settings (auto, custom, off)
   - Cross-validation settings
5. **Set limits** → timeout, max trials, max concurrent trials
6. **Select compute** → Choose a compute cluster
7. **Review + Submit**

### Reviewing AutoML results in Studio:
- **Jobs tab** → Find your AutoML job → Click on it
- **Overview tab**: Best model summary, primary metric score
- **Models + child jobs tab**: All trained models ranked by metric
- Click on best model:
  - **Metrics tab**: precision, recall, F1, confusion matrix, ROC curve
  - **Explanations tab**: Global feature importance (SHAP values)
  - **Artifacts tab**: MLmodel file, conda.yml, model.pkl

### Key AutoML metrics visible in Studio:

| Classification | Regression | Forecasting |
|---|---|---|
| Accuracy | RMSE | RMSE |
| AUC_weighted | R² score | R² score |
| Precision/Recall | MAE | MAE |
| F1 score | MAPE | MAPE |
| Confusion matrix | Residuals plot | Forecast vs actual |

> **Exam tip**: AutoML in Studio REQUIRES MLTABLE data assets. If a question says "CSV file registered as URI_FILE" and then tries to use AutoML → that will **fail**. Must be MLTABLE.

---

## 4. Designer (Visual Pipeline Builder)

The Designer lets you build ML pipelines by **dragging and dropping components** on a canvas.

### Built-in component categories:
- **Data Input/Output**: Import data, export data, enter data manually
- **Data Transformation**: Select columns, clean missing data, normalize, SMOTE, join, split
- **Feature Selection**: Filter-based feature selection, permutation feature importance
- **ML Algorithms**: Linear regression, decision forest, boosted trees, SVM, neural network
- **Model Training**: Train model, tune model hyperparameters, cross-validate
- **Model Scoring & Evaluation**: Score model, evaluate model

### Creating a training pipeline:
1. Drag **dataset** onto canvas
2. Add **Select Columns** to pick features
3. Add **Split Data** (e.g., 70/30 split)
4. Add **Train Model** component → configure target column
5. Connect an **algorithm** (e.g., Two-Class Boosted Decision Tree) to Train Model
6. Add **Score Model** → connect trained model + test data
7. Add **Evaluate Model** → connect scored results
8. Set **compute target** → compute cluster
9. **Submit** the pipeline

### Creating an inference pipeline from Designer:
After training in Designer, click **Create inference pipeline**:
- **Real-time inference pipeline**: For online endpoints
- **Batch inference pipeline**: For batch scoring

Studio auto-generates the inference pipeline:
1. Removes training components (Split Data, Train Model, Evaluate)
2. Adds **Web Service Input** / **Web Service Output** components
3. Keeps the scoring pipeline (Score Model)
4. You can customize the inference pipeline before deploying

> **Exam tip**: Designer uses **compute clusters** for training (not compute instances). After the pipeline runs, the trained model can be registered and deployed to an endpoint directly from Studio.

### Designer vs SDK v2 Pipelines:

| Feature | Designer | SDK v2 / CLI v2 |
|---|---|---|
| Interface | Visual drag-and-drop | Python code / YAML |
| Compute | Compute cluster only | Cluster, instance, serverless |
| Custom code | Limited (custom scripts via Execute Python Script) | Full flexibility |
| Version control | No Git integration | Full Git support |
| CI/CD | Manual | Fully automatable |
| Best for | Exploration, learning, quick prototyping | Production MLOps |

---

## 5. Managing Data in Studio

### Datastores tab:
- View all connected datastores
- Create new datastore connections (Blob, ADLS Gen2, File Share, SQL)
- Test connections
- Set a datastore as **default**

### Data assets tab:
- View all registered data assets
- Create new data assets:
  - **From local file** → Upload and auto-register
  - **From datastore** → Point to existing path
  - **From web URL** → HTTP(S) source
- Preview data (first 50 rows for tabular data)
- View **versions** of a data asset
- See **consuming jobs** — which jobs used this data asset

> **Exam tip**: When you upload a local file via Studio, it's stored in the **default datastore** (`workspaceblobstore`) under the `LocalUpload` folder.

---

## 6. Managing Jobs in Studio

The **Jobs** section shows all submitted jobs (command, sweep, pipeline, AutoML).

### Job details view:
- **Overview**: Status, duration, compute target, experiment name
- **Metrics**: Logged metrics with interactive charts
  - Line charts for step-based metrics (loss per epoch)
  - Bar charts for final metrics (accuracy)
- **Parameters**: Logged parameters (hyperparameters)
- **Outputs + logs**: stdout, stderr, system logs, model artifacts
- **Code**: The training script snapshot (read-only)
- **Environment**: Docker image + conda spec used
- **Monitoring**: Resource utilization (CPU, memory, GPU)

### Comparing jobs:
Select multiple jobs → Click **Compare** to see metrics/params side-by-side. This is the Studio equivalent of `mlflow.search_runs()`.

### Child jobs (sweep jobs):
- Navigate to a sweep job → **Trials** tab
- See all trial runs sorted by primary metric
- Compare hyperparameter values across trials
- Click on any trial for detailed logs and metrics

> **Exam tip**: The **Outputs + logs** tab is where you find model files, generated plots (`mlflow.log_artifact()`), MLmodel files, and system logs for debugging failed jobs.

---

## 7. Managing Models in Studio

### Registering a model via Studio:
1. Go to **Models** → **+ Register** → **From a job output**
2. Select the job → Select the model artifact path
3. Choose model type: **MLflow** or **Custom**
4. Name the model → Set version → Register

### Model details:
- **Details tab**: Type (MLflow/Custom), source job, description, tags
- **Artifacts tab**: MLmodel file, conda.yaml, model.pkl, requirements.txt
- **Versions**: Version history with links to source jobs

### Deploy from Studio:
From any registered model → Click **Deploy** → Choose:
- **Real-time endpoint**: Managed online endpoint
- **Batch endpoint**: For batch scoring
- Configure instance type, instance count, endpoint name
- For MLflow models: No scoring script needed
- For Custom models: Must provide scoring script + environment

---

## 8. Managing Endpoints in Studio

### Online Endpoints:
- View all endpoints with status (Succeeded/Updating/Failed)
- Click on endpoint:
  - **Details tab**: Endpoint URI, auth keys/tokens, swagger URL
  - **Deployment logs**: Container logs for debugging
  - **Test tab**: Send sample JSON and see live predictions
  - **Monitoring tab**: Request rates, latency, errors
  - **Traffic tab**: View/edit traffic allocation across deployments

### Testing an endpoint in Studio:
```json
{
  "input_data": {
    "columns": ["feature1", "feature2", "feature3"],
    "index": [0],
    "data": [[5.1, 3.5, 1.4]]
  }
}
```
Paste this in the **Test** tab → Click **Test** → See prediction response.

### Batch Endpoints:
- View all batch endpoints
- Invoke batch jobs → specify input data location
- View batch job results in output storage

---

## 9. Managing Compute in Studio

### Compute Instances tab:
- Create new instances (choose VM size)
- Start/Stop instances (stopped = no charge except disk)
- Configure **auto-shutdown** (idle timeout)
- Assign to specific user
- Open Terminal, Jupyter, JupyterLab, VS Code

### Compute Clusters tab:
- Create new clusters (min/max instances, VM size, tier)
- View cluster utilization
- See running/queued jobs on the cluster
- **Low Priority** flag visible in cluster details

### Key Studio actions:

| Action | Where in Studio |
|---|---|
| Create compute instance | Manage → Compute → Compute instances → + New |
| Create compute cluster | Manage → Compute → Compute clusters → + New |
| Stop compute instance | Compute instances → Select → Stop |
| Check cluster scaling | Compute clusters → Select → Overview (node count) |
| Set auto-shutdown | Compute instances → Select → Schedule |

> **Exam tip**: Compute instances can only be **assigned to one user**. They're for development only, not for production training (use clusters for that).

---

## 10. Environments in Studio

### Curated Environments:
Pre-built by Microsoft. Found under **Assets → Environments → Curated**.
- Named like `AzureML-sklearn-1.0-ubuntu20.04-py38-cpu`
- Click to see the Docker base image + conda spec
- Use the `@latest` suffix or specific version number

### Custom Environments:
Found under **Assets → Environments → Custom**.
- Create from: Docker image, conda file, or both
- View build logs if environment build failed
- Each version has its own Docker image in ACR

> **Exam tip**: If a question asks "where do you find the list of curated environments in Studio?" → **Assets → Environments → Curated tab**.

---

## 11. Responsible AI Dashboard in Studio

After creating a RAI dashboard (via pipeline), view it in Studio:

1. Go to **Models** → Select model → **Responsible AI** tab
2. Dashboard components visible:
   - **Error Analysis**: Decision tree showing error hotspots
   - **Model Overview**: Performance metrics by cohort
   - **Data Explorer**: Dataset statistics
   - **Feature Importance**: Global/local SHAP values
   - **Counterfactuals**: What-if analysis
   - **Causal Analysis**: Treatment effects

### Creating cohorts in the dashboard:
- Define subgroups (e.g., "Age > 65", "Gender = Female")
- View model performance per cohort
- Identify and compare error rates across cohorts

> **Exam tip**: The RAI dashboard is accessed through the **model details page**, not through the Jobs section. You must first run a RAI pipeline job that generates the dashboard.

---

## 12. Studio vs SDK v2 vs CLI v2 — When to Use What

| Scenario | Best Tool |
|---|---|
| Quick exploration, first-time user | **Studio UI** |
| Interactive data analysis | **Studio Notebooks** |
| No-code AutoML | **Studio AutoML** |
| Visual pipeline prototyping | **Studio Designer** |
| Production training scripts | **SDK v2** |
| CI/CD automation | **CLI v2** (with YAML) |
| GitOps / Infrastructure as Code | **CLI v2** |
| Debugging failed jobs | **Studio** (Outputs + logs tab) |
| Comparing multiple runs | **Studio** (Compare view) or **MLflow** |
| Monitoring deployed endpoints | **Studio** (Endpoints → Monitoring tab) |

> **Exam tip**: The exam often asks "what is the EASIEST way to..." — for visual/no-code tasks, the answer is usually **Studio UI**. For production/automation, it's **SDK v2 or CLI v2**.

---

## 13. Common Studio Operations — Quick Reference

| Task | Studio Path |
|---|---|
| Upload data | Assets → Data → + Create |
| Create AutoML job | Authoring → Automated ML → + New |
| Build visual pipeline | Authoring → Designer → + New |
| Submit a notebook job | Authoring → Notebooks → Run cell |
| View job metrics | Assets → Jobs → Select job → Metrics |
| Register model from job | Assets → Jobs → Select job → Register model |
| Deploy model | Assets → Models → Select → Deploy |
| Test endpoint | Assets → Endpoints → Select → Test tab |
| View endpoint logs | Assets → Endpoints → Select → Deployment logs |
| Create compute | Manage → Compute → + New |
| Manage environments | Assets → Environments |
| Check data drift | Assets → Data → Select asset → Monitoring |
| View RAI dashboard | Assets → Models → Select → Responsible AI tab |
