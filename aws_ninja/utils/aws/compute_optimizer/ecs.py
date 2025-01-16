import math
from typing import List, Dict

from aws_ninja.utils.aws.container_insights import get_container_insights_data
from aws_ninja.utils.aws.trim_arn import ecs_arn_to_service_name, ecs_arn_to_cluster_name
from aws_ninja.utils.aws.compute_optimizer import RecommendationCategory
from aws_ninja.utils.aws.compute_optimizer import RecommendationFinding
from aws_ninja.utils.aws.compute_optimizer import RecommendationResourceType
from poetry.console.commands import self


def get_ecs_recommendations(session):
    response = session.client('compute-optimizer').get_ecs_service_recommendations()

    services = [ECSService(session, s) for s in response['ecsServiceRecommendations']]

    return services


class ECSServiceMetrics:
    cpu: str
    memory: str
    period: int


class ECSServiceProvisionedWith:
    cpu: str
    memory: str


class Recommendation:
    resource_type: RecommendationResourceType
    finding: RecommendationFinding
    findings: List[RecommendationFinding]
    category: RecommendationCategory
    proposed: List[ECSServiceProvisionedWith]


class ECSService:
    arn: str
    name: str
    cluster: str
    tags: Dict[str, str]
    account: str
    recommendation: Recommendation
    provisioned: ECSServiceProvisionedWith
    metrics: ECSServiceMetrics
    container_insights: List[Dict[str, str]]

    def __init__(self, session, service):
        self.arn = service['serviceArn']
        self.cluster = ecs_arn_to_cluster_name(service['serviceArn'])
        self.name = ecs_arn_to_service_name(service['serviceArn']).replace(f"{self.cluster}-", '')
        self.account = service['accountId']
        self.container_insights = get_container_insights_data(session, self.cluster, f"{self.cluster}-{self.name}")
        self.tags = {t['key']: t['value'] for t in service['tags']}

        self.recommendation = Recommendation()
        self.recommendation.resource_type = RecommendationResourceType.ECS
        self.recommendation.category = RecommendationCategory.INSTANCE
        self.recommendation.finding = RecommendationFinding(service['finding'].lower())
        self.recommendation.findings = [
            RecommendationFinding(c.lower()) for c in service['findingReasonCodes']
        ]
        self.recommendation.proposed = []

        for option in service['serviceRecommendationOptions']:
            proposal = ECSServiceProvisionedWith()
            proposal.cpu = option['cpu']
            proposal.memory = option['memory']
            self.recommendation.proposed.append(proposal)

        self.provisioned = ECSServiceProvisionedWith()
        self.provisioned.cpu = service['currentServiceConfiguration']['cpu']
        self.provisioned.memory = service['currentServiceConfiguration']['memory']

        metrics = {
            f"{m['name'].lower()}": math.ceil(m['value'])
            for m in service['utilizationMetrics'] if m['statistic'].lower() == 'maximum'
        }
        self.metrics = ECSServiceMetrics()
        self.metrics.cpu = metrics['cpu']
        self.metrics.memory = metrics['memory']
        self.metrics.period = math.ceil(service['lookbackPeriodInDays'])
