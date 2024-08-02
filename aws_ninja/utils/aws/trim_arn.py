import re


def trim_arn(arn):
    trimmed = arn.split(':')[-1]
    trimmed = trimmed.split('/')[-1]
    trimmed = trimmed.replace("service/", "")
    trimmed = re.sub("-Service-[A-Za-z0-9]*", "", trimmed)

    return trimmed
