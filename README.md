# Snowflake Deployment Automation

## Overview

This repository provides an automation tool for seamless **Snowflake SQL deployments** using a structured YAML configuration. It executes SQL scripts stored in category-wise directories and logs execution details while updating deployment statuses.

The solution can be adapted for other ETL tools by modifying the connection function.

## Features

- Automates deployment of SQL scripts for snowflake .
- Tracks deployment status using `configuration.yaml`.
- Deploys SQL scripts to the specified Snowflake environment.
- Maintains logs for deployment execution.
- Supports execution of database objects such as tables, views, procedures, stages, streams, tasks, and ad hoc queries.
- Allows switching between Git branches before deployment.
- Integrates with **VSCode Snowflake extension** for execution  

## Folder Structure

Ensure your repository follows this structure:

```
├── autodeploy.py           # Main deployment script
├── configuration.yaml      # YAML config file for deployment
├── staging/           # Schema-level directory
│   ├── table/         # Tables SQL scripts
│   │   ├── staging_table.sql
│   ├── view/          # Views SQL scripts
│   │   ├── staging_view.sql
│   ├── procedure/     # Procedures SQL scripts
│   │   ├── staging_procedure.sql
│   ├── stage/         # Stages SQL scripts
│   │   ├── staging_stage.sql
│   ├── stream/        # Streams SQL scripts
│   │   ├── staging_stream.sql
│   ├── task/          # Tasks SQL scripts
│   │   ├── staging_task.sql
│   ├── adhoc/         # Ad-hoc SQL queries
│   │   ├── staging_adhoc.sql
├── ods/               # Another schema
├── curate/            # Another schema
├── deployment_logs/       # Log files generated during deployment
```

## Configuration File (`configuration.yaml`)

The YAML configuration file follows a structured format to specify deployments:

```yaml
staging:
  table:
    staging_table: deploy
  view:
    staging_view: deploy
  procedure:
    staging_procedure: deploy
  stage:
    staging_stage: deploy
  stream:
    staging_stream: deploy
  task:
    staging_task: deploy
  adhoc:
    staging_adhoc: deploy
```

- **Deploy**: Indicates that the script should execute the SQL file.
- **Deployed**: Indicates that the script has already been executed.
- **Failed**: Indicates a failed deployment (check logs for details).

## Setup & Execution

### Prerequisites

Before you begin, ensure the following prerequisites are in place:

- **Snowflake Account and Database Access**: Make sure you have access to the Snowflake instance and the required databases/schemas.
- **SnowSQL**: A command-line client to interact with Snowflake. Follow the [official installation guide](https://docs.snowflake.com/en/user-guide/snowsql-install-config.html) to install SnowSQL.
- **Git**: Installed on your machine to work with version control.
- **Python 3.x**: If you plan to use any Python-based testing or interaction with Snowflake.

### Setting Up the Project Locally

1. Clone the repository:
    ```bash
    git clone <repo-url>
    cd <repo-directory>
    ```

2. **Install required dependencies**:
    If using any dependencies for testing, installation, or data pipeline tasks, install them using `pip` or `npm` as applicable.

    Example for Python:
    ```bash
    pip install snowflake-connector-python ruamel.yaml
    ```

3. **Configure Snowflake credentials**:
    There are two ways to configure Snowflake credentials:

    - **Option 1: Using SnowSQL Configuration File**:
      - Create a configuration file `.snowsql/config` with your Snowflake credentials.

      Example `.snowsql/config`:
      ```ini
      [connections]
      my_connection = 
          account = <your_account>
          user = <your_user>
          password = <your_password>
          warehouse = <your_warehouse>
          database = <your_database>
          schema = <your_schema>
      ```

      - You can test your connection by running:
        ```bash
        snowsql -q "SELECT CURRENT_VERSION();"
        ```

    - **Option 2: Using VSCode Snowflake Official Plugin**:
      - Install the Snowflake extension for Visual Studio Code (VSCode).
      - Go to **VSCode Extensions** and search for **Snowflake** by Snowflake Computing, Inc.
      - Follow the steps in the extension's prompt to configure your Snowflake credentials, including **Account**, **User**, **Password**, **Warehouse**, **Database**, and **Schema**.
      - Once connected, you can run Snowflake queries directly within VSCode.


### Running the Deployment

```sh
python autodeploy.py --branch develop --environment dev
```

- `--branch`: Git branch to checkout before deployment (e.g., `develop`, `release`).
- `--environment`: Deployment environment (`dev`, `tst`, `prd`).

### Logs

Deployment logs are stored in the `deployment_logs/` directory with timestamps for debugging and tracking purposes.

## Customizing for Other ETL Tools

To use this script for other ETL tools, modify the `connect_snowflake()` function in `autodeploy.py` to establish a connection with your desired database or tool.

