# Run Items Configuration Generator

This script generates a **single metadata-driven configuration file** called `run_items.json`, which serves as the **sole input for Azure Data Factory (ADF) pipelines**. The output provides a **scalable and developer-friendly framework** for orchestrating and executing data ingestion, transformation, and loading processes.

## Key Features and Design Principles

### 1. Metadata-Driven Framework

- The script ingests structured metadata from three JSON files:
  - **`datasets.json`**: Defines datasets, their source/target details, delta processing rules, and logical grouping (`data_group`).
  - **`parameters.json`**: Contains global dataset parameters (e.g., `customer`) and ETL parameters for non-dataset processes.
  - **`layers.json`**: Defines the pipeline execution layers and their dependencies.

### 2. Scalability and Parallel Execution

- Each layer in `run_items.json` represents a logical execution grouping in ADF.
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

## **7. Run Parameters for Controlled Execution and Recovery**

The **`01-Main` pipeline** supports **six parameters**, allowing fine-grained control over execution and recovery.

- **Four Integer Parameters** (`Int` type) control layer and run-item execution.
- **Two Boolean Parameters** (`Bool` type) enable failure-based recovery.

### **Pipeline Parameters Overview**

#### **🔢 Integer Parameters**

| Parameter                  | Description                                                                 |
| -------------------------- | --------------------------------------------------------------------------- |
| **`run_from_layer`**       | Starts execution from a specific layer, skipping all preceding layers.      |
| **`run_layer_only`**       | Executes only the specified layer, skipping all others.                     |
| **`run_from_run_item_id`** | Starts execution from the specified `run_item_id`, skipping previous items. |
| **`run_run_item_id_only`** | Executes only the specified `run_item_id` and no others.                    |

#### **✅ Boolean Parameters**

| Parameter                    | Description                                                                                         |
| ---------------------------- | --------------------------------------------------------------------------------------------------- |
| **`run_from_first_failure`** | Identifies the first failed `run_item` (based on `state_details`) and resumes execution from there. |
| **`run_failed_items_only`**  | Retries only failed `run_items`, allowing quick recovery without reprocessing everything.           |

### **🚀 Parameter Validation Rules**

The pipeline **validates input parameters** using `02-Parameter-Check` to ensure consistency. Execution proceeds only if one of the following conditions is met:

1️⃣ **Default Execution (Run All)**

- All **integer parameters** = `0`
- Both **boolean parameters** = `false`

2️⃣ **Failure Recovery Mode**

- All **integer parameters** = `0`
- Only **one boolean parameter** = `true`

3️⃣ **Targeted Execution Mode**

- Only **one integer parameter** > `0`
- All other **integer parameters** = `0`
- Both **boolean parameters** = `false`

❌ **Invalid Configurations**  
Any other combination of parameters is **not allowed**, and the pipeline will **halt execution**.

### **✨ Why Use These Parameters?**

These controls ensure:  
✅ **Minimal reprocessing** – Avoid re-executing unnecessary steps.  
✅ **Efficient failure handling** – Quickly recover from failures without restarting everything.  
✅ **Flexible execution** – Run specific layers or items as needed.

## How Azure Data Factory Uses `run_items.json`

1. ADF reads `run_items.json` as **its only input**.
2. It loops over the **layers** and runs datasets in parallel within each layer.
3. **Run parameters determine execution behavior**, whether it starts from a failure point, executes a specific layer, or runs only failed items.
4. Delta-enabled datasets are initially loaded with **developer-defined defaults** but transition to fully **automated incremental processing**.
5. **ETL parameters are dynamically applied**, ensuring procedural logic runs only within its corresponding layer.

This framework provides a `scalable, metadata-driven, and developer-friendly` approach for managing ADF data pipelines efficiently. 🚀
