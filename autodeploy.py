import os
import sys
import subprocess
import argparse
import snowflake.connector
import logging
from datetime import datetime
from ruamel.yaml import YAML

# Constants
LOG_DIR = "deployment_logs"
ENV_DB = {'dev': 'DEV_DB', 'tst': 'TST_DB', 'prd': 'PRD_DB'}

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def get_log_filename(environment):
    """
    Create log file name including environment.
    """
    return os.path.join(
        LOG_DIR, f"deployment_log_{environment}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

def setup_logging(environment):
    """
    Setup logging
    """
    log_filename = get_log_filename(environment)
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

def load_yaml(yaml,config_file):
    """
    Load the YAML configuration file while maintaining format and comments.
    """
    with open(config_file, "r") as file:
        return yaml.load(file)


def save_yaml(config, yaml,config_file):
    """
    Save the updated YAML configuration file.
    """
    with open(config_file, "w") as file:
        yaml.dump(config, file)


def connect_snowflake(db):
    """
    Establish a Snowflake connection using the VSCode extension.
    """
    try:
        conn = snowflake.connector.connect(connection_name=db)
        logging.info("Successfully connected to Snowflake.")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to Snowflake: {str(e)}")
        raise


def get_sql(file_path):
    """
    Read the SQL file and return SQL script.
    """
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return ""

    with open(file_path, "r") as file:
        sql_query = file.read().strip()

    if not sql_query:
        logging.warning(f"Skipping {file_path}, no SQL to execute.")
        return ""
    else:
        logging.info(f"Query fetched from {file_path}")
        return sql_query


def execute_sql(file, sql_query, cur):
    """
    Execute the SQL script from the given file and log the result.
    """
    try:
        logging.info(f"Executing SQL from {file}...")
        cur.execute(sql_query, num_statements=0)
        results = []
        while True:
            results.append(cur.fetchone()[0])
            if cur.nextset() is None:
                break

        logging.info(f"Execution results: {results}")
        logging.info(f"Successfully deployed {file}")
        return "deployed"
    except Exception as e:
        logging.error(f"Execution failed for {file}: {str(e)}")
        return "failed"


def process_file_with_db_objects(schema, db_object_type, file, status, cur):
    """
    Process individual file by reading the SQL and executing it.
    """
    file_path = os.path.join(os.getcwd(), schema, db_object_type, f"{file}.sql")
    logging.info(f"Processing {schema}/{db_object_type}/{file}.sql - {status}")

    sql_query = get_sql(file_path)
    if not sql_query:
        return "failed"
    return execute_sql(file, sql_query, cur)


def get_db_objects(config, cur):
    """
    Process all files in the config dictionary.
    """
    for schema, objects in config.items():
        for db_object_type, files in objects.items():
            if not files:
                continue

            for file, status in files.items():
                if status == "deploy":
                    files[file] = process_file_with_db_objects(
                        schema, db_object_type, file, status, cur
                    )

def checkout_branch(branch):
    """
    Checkout the git branch.
    """
    if branch in ("dev","develop") or "release" in branch :
        try:
            subprocess.run(['git', 'checkout', branch], check=True)
            logging.info(f"Switched to branch {branch}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error switching to branch {branch}: {e}")
    else:
        logging.error(f"Invalid branch argument: {branch}. Valid values are 'develop' or 'release'.")
        sys.exit(1) 


def deploy(environment):
    """Process deployment based on the YAML configuration."""
    # Load YAML while preserving format and comments
    db = ENV_DB.get(environment)
    if not db:
        logging.error(f"Invalid environment argument: {environment}. Valid values are 'dev', 'tst' or 'prd'.")
        sys.exit(1) 

    config_file = f"configuration.yaml"
    yaml = YAML()
    yaml.preserve_quotes = True
    config = load_yaml(yaml, config_file)

    try:
        with connect_snowflake(db) as conn:
            with conn.cursor() as cur:
                get_db_objects(config, cur)

        save_yaml(config, yaml, config_file)
        logging.info("Deployment process completed.")

    except Exception as e:
        logging.error(f"Deployment failed: {e}")

    finally:
        logging.info("Snowflake connection closed.")

def main(branch,environment):

    checkout_branch(branch)
    deploy(environment)

if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="Autodeploy Script")
    
    # Add arguments for branch and environment
    parser.add_argument('--branch', type=str, required=True, help="Name of the branch")
    parser.add_argument('--environment', type=str, required=True, help="Deployment environment")
    
    # Parse the arguments
    args = parser.parse_args()
    
    setup_logging(args.environment.lower())
    main(args.branch,args.environment.lower())