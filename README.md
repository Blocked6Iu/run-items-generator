<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Run Items Configuration Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: auto;
            padding: 20px;
        }
        h1, h2 {
            color: #2c3e50;
        }
        code {
            background: #ecf0f1;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: "Courier New", Courier, monospace;
        }
        pre {
            background: #ecf0f1;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>

    <h1>Run Items Configuration Generator</h1>

    <p>This script generates a <strong>single metadata-driven configuration file</strong> called <code>run_items.json</code>, which serves as the <strong>sole input for Azure Data Factory (ADF) pipelines</strong>. The output provides a <strong>scalable and developer-friendly framework</strong> for orchestrating and executing data ingestion, transformation, and loading processes.</p>

    <h2>Key Features and Design Principles</h2>

    <h3>1. Metadata-Driven Framework</h3>
    <ul>
        <li>The script ingests structured metadata from three JSON files:</li>
        <ul>
            <li><code>datasets.json</code>: Defines datasets, their source/target details, delta processing rules, and logical grouping (<code>data_group</code>).</li>
            <li><code>parameters.json</code>: Contains global dataset parameters (e.g., <code>institute_list</code>) and ETL parameters for non-dataset processes.</li>
            <li><code>layers.json</code>: Defines the pipeline execution layers and their dependencies.</li>
        </ul>
    </ul>

    <h3>2. Scalability and Parallel Execution</h3>
    <ul>
        <li>Each layer in <code>run_items.json</code> represents a logical execution stage in ADF.</li>
        <li>ADF executes all <strong>run items within a layer in parallel</strong>, leveraging a <code>foreach</code> loop to maximize throughput.</li>
        <li>The framework allows adding new datasets, layers, or parameters without modifying ADF logic, making it highly <strong>scalable</strong>.</li>
    </ul>

    <h3>3. Dataset and ETL Parameter Handling</h3>
    <ul>
        <li><strong>Dataset-scoped layers (<code>dataset_scope = true</code>)</strong>: Generates <strong>one run item per dataset per institute</strong> using <code>institute_list</code>.</li>
        <li><strong>ETL process layers (<code>dataset_scope = false</code>)</strong>: Groups stored procedure (<code>sp_list</code>) execution by ETL category (e.g., <code>dimension</code>, <code>fact</code>).</li>
    </ul>

    <h3>4. Delta Processing with Dynamic Watermarks</h3>
    <ul>
        <li>For <strong>delta-enabled datasets (<code>delta_enabled = true</code>)</strong>, ADF applies incremental loading using <code>dtStart</code> and <code>dtEnd</code>.</li>
        <li>Initial execution uses <strong>developer-specified default date values</strong> from <code>datasets.json</code>.</li>
        <li>Thereafter, ADF <strong>automatically updates <code>dtStart</code> and <code>dtEnd</code></strong> via a separate delta pipeline, ensuring accurate <strong>incremental data processing</strong>.</li>
    </ul>

    <h3>5. Dynamic Query Generation with Placeholder Substitution</h3>
    <ul>
        <li>The script dynamically replaces:</li>
        <ul>
            <li><code>&lt;&lt;INSTITUTE_ID&gt;&gt;</code> → Injects <code>INSTITUTE_ID</code> from <code>parameters.json</code>.</li>
            <li><code>&lt;&lt;dtStart&gt;&gt;</code> and <code>&lt;&lt;dtEnd&gt;&gt;</code> → Uses defaults from <code>datasets.json</code> (if specified).</li>
        </ul>
        <li>If <code>dtStart</code> or <code>dtEnd</code> is <strong>missing</strong>, the placeholders remain, ensuring the query remains adaptable for ADF's delta update pipeline.</li>
        <li>Dates are automatically <strong>wrapped in single quotes</strong> (<code>'YYYY-MM-DD'</code>), preventing syntax errors.</li>
    </ul>

    <h3>6. Logical Data Grouping (<code>data_group</code>)</h3>
    <ul>
        <li>Each dataset is tagged with a <code>data_group</code>, allowing ADF to filter and process specific subsets of data dynamically.</li>
        <li>This enhances flexibility for batch processing or targeted data refreshes.</li>
    </ul>

    <h2>How Azure Data Factory Uses <code>run_items.json</code></h2>
    <ol>
        <li>ADF reads <code>run_items.json</code> as <strong>its only input</strong>.</li>
        <li>It loops over the <strong>layers</strong> and runs datasets in parallel within each layer.</li>
        <li>Delta-enabled datasets are initially loaded with <strong>developer-defined defaults</strong> but transition to fully <strong>automated incremental processing</strong>.</li>
        <li><strong>ETL parameters are dynamically applied</strong>, ensuring procedural logic runs only within its corresponding layer.</li>
    </ol>

    <p>This framework provides a <strong>scalable, metadata-driven, and developer-friendly</strong> approach for managing ADF data pipelines efficiently. 🚀</p>

</body>
</html>
