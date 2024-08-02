import os
from enum import Enum

import boto3
import click
import jsonpickle

from aws_ninja.utils.aws.compute_optimizer import RecommendationFinding
from aws_ninja.utils.aws.trusted_advisor import TrustedAdvisorPillar


def get_available_profiles():
    return boto3.Session().available_profiles


def get_session_for_profile(profile=os.getenv("AWS_PROFILE"), region=os.getenv("AWS_REGION")):
    session = boto3.Session(profile_name=profile, region_name=region)

    identity = session.client('sts').get_caller_identity()

    click.secho("[AWS] Connected to {}:{} with identity: {}".format(profile,
                                                                    region,
                                                                    identity['UserId']),
                fg="green")

    return session


def get_client(session, client):
    return session.client(client)


def recommendation_finding_to_human(finding: RecommendationFinding):
    mapping = {
        RecommendationFinding.OPTIMIZED: 'Optimised',
        RecommendationFinding.UNDERPROVISIONED: 'Under-provisioned',
        RecommendationFinding.OVERPROVISIONED: 'Over-provisioned',
        RecommendationFinding.MEMORY_OVERPROVISIONED: 'Memory is over-provisioned',
        RecommendationFinding.MEMORY_UNDERPROVISIONED: 'Memory is under-provisioned',
        RecommendationFinding.CPU_OVERPROVISIONED: 'CPU is over-provisioned',
        RecommendationFinding.CPU_UNDERPROVISIONED: 'CPU is under-provisioned',
        RecommendationFinding.NEW_GENERATION_STORAGE_TYPE_AVAILABLE:
            'New Generation Storage is Available',
        RecommendationFinding.EBS_IOPS_OVERPROVISIONED: 'IOPS are over-provisioned',
        RecommendationFinding.EBS_THROUGHPUT_OVERPROVISIONED: 'Throughput are over-provisioned',
        RecommendationFinding.NETWORK_BANDWIDTH_OVERPROVISIONED:
            'Network Bandwidth is over-provisioned',

        TrustedAdvisorPillar.COST_OPTIMIZING: 'Cost Optimisation',
        TrustedAdvisorPillar.PERFORMANCE: 'Performance',
        TrustedAdvisorPillar.SECURITY: 'Security',
        TrustedAdvisorPillar.SERVICE_LIMITS: 'Service Limits',
        TrustedAdvisorPillar.FAULT_TOLERANCE: 'Fault Tolerance',
        TrustedAdvisorPillar.OPERATIONAL_EXCELLENCE: 'Operational Excellence',
    }

    return mapping[finding]


class EnumHandler(jsonpickle.handlers.BaseHandler):
    def flatten(self, obj: Enum, data):
        return obj.name
