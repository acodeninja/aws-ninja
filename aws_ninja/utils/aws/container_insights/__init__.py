import json
from datetime import datetime, timedelta
import time

CONTAINER_INSIGHTS_CACHE = {}

def initialise_container_insights_data(session):
    for group in session.client('logs').describe_log_groups(logGroupNamePrefix='/aws/ecs/containerinsights/')['logGroups']:
        if group['logGroupName'].endswith('performance'):
            ecs_cluster_name = group['logGroupName'].split('/')[4]
            CONTAINER_INSIGHTS_CACHE[ecs_cluster_name] = {
                'log_group_arn': group['logGroupArn'],
                'log_group_name': group['logGroupName'],
                'reports': {},
            }

def get_container_insights_data(session, cluster_name, service_name):
    if cluster_name not in CONTAINER_INSIGHTS_CACHE:
        initialise_container_insights_data(session)

    if service_name in CONTAINER_INSIGHTS_CACHE[cluster_name]['reports']:
        return CONTAINER_INSIGHTS_CACHE[cluster_name]['reports'][service_name]

    client = session.client('logs')

    query = f"""
        fields @timestamp, MemoryReserved, MemoryUtilized, CpuReserved, CpuUtilized
        | filter Type = 'Task' and TaskDefinitionFamily = '{service_name}' and ClusterName = '{cluster_name}'
        | fields tomillis(@timestamp) as @timestamp_ms
        | filter @timestamp_ms % 3600000 = 0
        | sort @timestamp desc
        | limit 100
    """

    start_query = client.start_query(
        logGroupName=CONTAINER_INSIGHTS_CACHE[cluster_name]['log_group_name'],
        startTime=int((datetime.today() - timedelta(hours=24)).timestamp()),
        endTime=int(datetime.now().timestamp()),
        queryString=query,
    )

    query_result = None

    while query_result == None or query_result['status'] == 'Running':
        time.sleep(1)
        query_result = client.get_query_results(
            queryId=start_query['queryId'],
        )

    report = []

    for result in query_result['results']:
        report_line = {}
        for field in result:
            if field['field'] != '@ptr':
                report_line[field['field']] = field['value']
        report.append(report_line)

    CONTAINER_INSIGHTS_CACHE[cluster_name]['reports'][service_name] = report

    return report
