# Run Items Configuration Generator

This script generates a **single metadata-driven configuration file** called `run_items.json`, which serves as the **sole input for Azure Data Factory (ADF) pipelines**. The output provides a **scalable and developer-friendly framework** for orchestrating and executing data ingestion, transformation, and loading processes.

## Key Features and Design Principles

### 1. Metadata-Driven Framework
- The script ingests structured metadata from three JSON files:
  - **`datasets.json`**: Defines datasets, their source/target details, delta processing rules, and logical grouping (`data_group`).
  - **`parameters.json`**: Contains global dataset parameters (e.g., `institute_list`) and ETL parameters for non-dataset processes.
  - **`layers.json`**: Defines the pipeline execution layers and their dependencies.

### 2. Scalability and Parallel Execution
- Each layer in `run_items.json` represents a logical execution stage in ADF.
- ADF executes all **run items within a layer in parallel**, leveraging a `foreach` loop to maximize throughput.
- The framework allows adding new datasets, layers, or parameters without modifying ADF logic, making it highly **scalable**.

### 3. Dataset and ETL Parameter Handling
- **Dataset-scoped layers (`dataset_scope = true`)**: Generates **one run item per dataset per institute** using `institute_list`.
- **ETL process layers (`dataset_scope = false`)**: Groups stored procedure (`sp_list`) execution by ETL category (e.g., `dimension`, `fact`).

### 4. Delta Processing with Dynamic Watermarks
- For **delta-enabled datasets (`delta_enabled = true`)**, ADF applies incremental loading using `dtStart` and `dtEnd`.
- Initial execution uses **developer-specified default date values** from `datasets.json`.
- Thereafter, ADF **automatically updates `dtStart` and `dtEnd`** via a separate delta pipeline, ensuring accurate **incremental data processing**.

### 5. Dynamic Query Generation with Placeholder Substitution
- The script dynamically replaces:
  - `<<INSTITUTE_ID>>` → Injects `INSTITUTE_ID` from `parameters.json`.
  - `<<dtStart>>` and `<<dtEnd>>` → Uses defaults from `datasets.json` (if specified).
- If `dtStart` or `dtEnd` is **missing**, the placeholders remain, ensuring the query remains adaptable for ADF's delta update pipeline.
- Dates are automatically **wrapped in single quotes** (`'YYYY-MM-DD'`), preventing syntax errors.

### 6. Logical Data Grouping (`data_group`)
- Each dataset is tagged with a `data_group`, allowing ADF to filter and process specific subsets of data dynamically.
- This enhances flexibility for batch processing or targeted data refreshes.

### 7. Run Parameters for Controlled Execution and Recovery
The `run_parameters` section within `parameters.json` allows **fine-grained control over execution**, making the framework highly **re-runnable and failure-resilient**. These parameters dictate how ADF executes the pipelines:

- **`run_from_layer`** → Starts execution from a specific layer, skipping all preceding layers.
- **`run_layer_only`** → Executes a **single specified layer** and nothing else.
- **`run_from_first_failure`** → Identifies the first failed run item (based on `state_details`) and resumes execution from there.
- **`run_failed_items_only`** → Retries only the run items marked as `failed`, allowing quick recovery without reprocessing everything.

These options ensure **minimal reprocessing** and provide **flexibility for handling failures efficiently**, improving overall execution efficiency.

## How Azure Data Factory Uses `run_items.json`
1. ADF reads `run_items.json` as **its only input**.
2. It loops over the **layers** and runs datasets in parallel within each layer.
3. **Run parameters determine execution behavior**, whether it starts from a failure point, executes a specific layer, or runs only failed items.
4. Delta-enabled datasets are initially loaded with **developer-defined defaults** but transition to fully **automated incremental processing**.
5. **ETL parameters are dynamically applied**, ensuring procedural logic runs only within its corresponding layer.

This framework provides a **scalable, metadata-driven, and developer-friendly** approach for managing ADF data pipelines efficiently. 🚀
