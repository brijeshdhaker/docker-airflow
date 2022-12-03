# --------------------------------------------------------------------------------
# Load The Dependencies
# --------------------------------------------------------------------------------
"""
This is an example dag for managing twitter data.
"""

import os
from datetime import date, datetime, timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from airflow.providers.apache.hive.operators.hive import HiveOperator

ENV_ID = os.environ.get("SYSTEM_TESTS_ENV_ID")
DAG_ID = "example_twitter_dag"


@task
def fetch_tweets():
    """
    This task should call Twitter API and retrieve tweets from yesterday from and to for the four twitter
    users (Twitter_A,..,Twitter_D) There should be eight csv output files generated by this task and naming
    convention is direction(from or to)_twitterHandle_date.csv
    """


@task
def clean_tweets():
    """
    This is a placeholder to clean the eight files. In this step you can get rid of or cherry pick columns
    and different parts of the text.
    """


@task
def analyze_tweets():
    """
    This is a placeholder to analyze the twitter data. Could simply be a sentiment analysis through algorithms
    like bag of words or something more complicated. You can also take a look at Web Services to do such
    tasks.
    """


@task
def transfer_to_db():
    """
    This is a placeholder to extract summary from Hive data and store it to MySQL.
    """


with DAG(
    dag_id=DAG_ID,
    default_args={
        'owner': 'Ekhtiar',
        'retries': 1,
    },
    schedule_interval="@daily",
    start_date=datetime(2021, 1, 1),
    tags=['example'],
    catchup=False,
) as dag:
    fetch = fetch_tweets()
    clean = clean_tweets()
    analyze = analyze_tweets()
    hive_to_mysql = transfer_to_db()

    fetch >> clean >> analyze

    # --------------------------------------------------------------------------------
    # The following tasks are generated using for loop. The first task puts the eight
    # csv files to HDFS. The second task loads these files from HDFS to respected Hive
    # tables. These two for loops could be combined into one loop. However, in most cases,
    # you will be running different analysis on your incoming and outgoing tweets,
    # and hence they are kept separated in this example.
    # --------------------------------------------------------------------------------

    from_channels = ['fromTwitter_A', 'fromTwitter_B', 'fromTwitter_C', 'fromTwitter_D']
    to_channels = ['toTwitter_A', 'toTwitter_B', 'toTwitter_C', 'toTwitter_D']
    yesterday = date.today() - timedelta(days=1)
    dt = yesterday.strftime("%Y-%m-%d")
    # define where you want to store the tweets csv file in your local directory
    local_dir = "/tmp/"
    # define the location where you want to store in HDFS
    hdfs_dir = " /tmp/"

    for channel in to_channels:

        file_name = f"to_{channel}_{dt}.csv"

        load_to_hdfs = BashOperator(
            task_id=f"put_{channel}_to_hdfs",
            bash_command=(
                f"HADOOP_USER_NAME=hdfs hadoop fs -put -f {local_dir}{file_name}{hdfs_dir}{channel}/"
            ),
        )

        # [START create_hive]
        load_to_hive = HiveOperator(
            task_id=f"load_{channel}_to_hive",
            hql=(
                f"LOAD DATA INPATH '{hdfs_dir}{channel}/{file_name}'"
                f"INTO TABLE {channel}"
                f"PARTITION(dt='{dt}')"
            ),
        )
        # [END create_hive]

        analyze >> load_to_hdfs >> load_to_hive >> hive_to_mysql

    for channel in from_channels:
        file_name = f"from_{channel}_{dt}.csv"
        load_to_hdfs = BashOperator(
            task_id=f"put_{channel}_to_hdfs",
            bash_command=(
                f"HADOOP_USER_NAME=hdfs hadoop fs -put -f {local_dir}{file_name}{hdfs_dir}{channel}/"
            ),
        )

        load_to_hive = HiveOperator(
            task_id=f"load_{channel}_to_hive",
            hql=(
                f"LOAD DATA INPATH '{hdfs_dir}{channel}/{file_name}' "
                f"INTO TABLE {channel} "
                f"PARTITION(dt='{dt}')"
            ),
        )

        analyze >> load_to_hdfs >> load_to_hive >> hive_to_mysql

    from tests.system.utils.watcher import watcher

    # This test needs watcher in order to properly mark success/failure
    # when "tearDown" task with trigger rule is part of the DAG
    list(dag.tasks) >> watcher()

from tests.system.utils import get_test_run  # noqa: E402

# Needed to run the example DAG with pytest (see: tests/system/README.md#run_via_pytest)
test_run = get_test_run(dag)