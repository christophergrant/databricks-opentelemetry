from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs, compute
from concurrent.futures import ThreadPoolExecutor, as_completed


def submit_run(profile):
    w = WorkspaceClient(profile=profile)
    run = w.jobs.submit_and_wait(run_name="databricks-opentelemetry-test",
                git_source=jobs.GitSource(git_url="https://github.com/christophergrant/databricks-opentelemetry.git",
                                          git_provider=jobs.GitProvider.GIT_HUB,
                                          git_branch="main"),
                tasks=[
                    jobs.SubmitTask(
                        spark_python_task=jobs.SparkPythonTask(python_file="tests/test.py", 
                                                                source=jobs.Source.GIT),
                        new_cluster=compute.ClusterSpec(cluster_log_conf=compute.ClusterLogConf(
                            compute.DbfsStorageInfo(destination="dbfs:/tmp/cluster-logs")
                            ),
                            node_type_id=w.clusters.select_node_type(local_disk=True), 
                                                        num_workers=0, 
                                                        spark_version=w.clusters.select_spark_version(long_term_support=True),
                                                        spark_conf={
                                                            "spark.databricks.cluster.profile": "singleNode",
                                                            "spark.master": "local[*]"
                                                        }
                                                        ),
                        task_key="main"
                    )
                ])
    
    return run.state.result_state == jobs.RunResultState.SUCCESS

profiles = ["awsfe", "gcpfe", "azurefe"]

assert profiles # make sure this isn't empty

with ThreadPoolExecutor(max_workers=len(profiles)) as executor:
    # Submitting all jobs to the executor
    future_to_profile = {executor.submit(submit_run, profile): profile for profile in profiles}
    
    # Iterating over the results as they complete
    for future in as_completed(future_to_profile):
        profile = future_to_profile[future]
        try:
            result = future.result()
            print(f"Profile {profile}: Job {'succeeded' if result else 'failed'}")
        except Exception as exc:
            print(f"Profile {profile} generated an exception: {exc}")