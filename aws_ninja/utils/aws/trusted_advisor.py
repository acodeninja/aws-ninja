import re
from enum import Enum
from pprint import pprint
from typing import List

from aws_ninja.utils.aws.trim_arn import trim_arn


def get_trusted_advisor_recommendations(session, include_status=None):
    if not include_status:
        include_status = ['error']

    client = session.client('trustedadvisor')
    raw_recommendations = []

    for status in include_status:
        recommendations = client.list_recommendations(status=status)['recommendationSummaries']
        for recommendation in recommendations:
            raw_recommendations.append({
                'resources': client.list_recommendation_resources(recommendationIdentifier=recommendation['arn'])['recommendationResourceSummaries'],
                'recommendation': client.get_recommendation(recommendationIdentifier=recommendation['arn'])['recommendation'],
            })

    return [TrustedAdvisorRecommendation(r, include_status) for r in raw_recommendations]


class TrustedAdvisorResource:
    arn: str
    name: str

    def __init__(self, arn: str):
        self.arn = arn
        self.name = trim_arn(arn)


class TrustedAdvisorPillar(Enum):
    COST_OPTIMIZING = 'cost_optimizing'
    PERFORMANCE = 'performance'
    SECURITY = 'security'
    SERVICE_LIMITS = 'service_limits'
    FAULT_TOLERANCE = 'fault_tolerance'
    OPERATIONAL_EXCELLENCE = 'operational_excellence'


class TrustedAdvisorRecommendation:
    name: str
    description: str
    pillars: List[TrustedAdvisorPillar]
    resources: List[TrustedAdvisorResource]

    def __init__(self, recommendation, include_status):
        self.name = recommendation['recommendation']['name']
        self.description = recommendation['recommendation']['description'].replace('h4', 'strong')
        self.pillars = [TrustedAdvisorPillar(p) for p in recommendation['recommendation']['pillars']]
        self.resources = [TrustedAdvisorResource(r['metadata']['2'] if '2' in r['metadata'] else r['awsResourceId']) for r in recommendation['resources'] if r['status'] in include_status]
