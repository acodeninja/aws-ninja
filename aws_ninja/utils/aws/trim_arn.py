import re


def ecs_arn_to_service_name(arn):
    trimmed = arn.split(':')[-1]
    trimmed = trimmed.split('/')[-1]
    trimmed = trimmed.replace("service/", "")
    trimmed = re.sub("-Service-[A-Za-z0-9]*", "", trimmed)

    return trimmed

def ecs_arn_to_cluster_name(arn):
    return arn.split('/')[1]
