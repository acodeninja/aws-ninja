from typing import List, Dict

from aws_ninja.utils.aws.trim_arn import trim_arn
from aws_ninja.utils.aws.compute_optimizer import RecommendationFinding
from aws_ninja.utils.aws.compute_optimizer import RecommendationCategory


def get_rds_recommendations(session):
    response = session.client('compute-optimizer').get_rds_database_recommendations()

    instances = [RDSInstance(s) for s in response['rdsDBRecommendations']]

    return instances


class RDSStorageConfiguration:
    type: str
    iops: int
    allocated: int
    max_allocated: int
    throughput: int


class RDSInstanceConfiguration:
    type: str


class RDSInstanceRecommendation:
    category: RecommendationCategory
    proposed: List[RDSInstanceConfiguration]


class RDSStorageRecommendation:
    category: RecommendationCategory
    proposed: List[RDSStorageConfiguration]


class RDSInstance:
    arn: str
    tags: Dict[str, str]
    name: str
    account: str
    engine: str
    storage_current: RDSStorageConfiguration
    storage_finding: RecommendationFinding
    storage_findings: List[RecommendationFinding]
    storage_recommendations: List[RDSStorageRecommendation]
    instance_current: RDSInstanceConfiguration
    instance_finding: RecommendationFinding
    instance_findings: List[RecommendationFinding]
    instance_recommendations: List[RDSInstanceRecommendation]

    def __init__(self, service):
        self.arn = service['resourceArn']
        self.name = trim_arn(service['resourceArn'])
        self.engine = service['engine']

        self.tags = {t['key']: t['value'] for t in service['tags']}

        self.storage_finding = RecommendationFinding(service['storageFinding'])
        self.storage_findings = [RecommendationFinding(f) for f in service['storageFindingReasonCodes']]
        self.storage_current = RDSStorageConfiguration()
        self.storage_current.type = service['currentStorageConfiguration']['storageType'] if 'storageType' in service['currentStorageConfiguration'] else None
        self.storage_current.allocated = service['currentStorageConfiguration']['allocatedStorage'] if 'allocatedStorage' in service['currentStorageConfiguration'] else None
        self.storage_current.iops = service['currentStorageConfiguration']['iops'] if 'iops' in service['currentStorageConfiguration'] else None
        self.storage_current.max_allocated = service['currentStorageConfiguration']['maxAllocatedStorage'] if 'maxAllocatedStorage' in service['currentStorageConfiguration'] else None
        self.storage_current.throughput = service['currentStorageConfiguration']['storageThroughput'] if 'storageThroughput' in service['currentStorageConfiguration'] else None

        self.instance_finding = RecommendationFinding(service['instanceFinding'])
        self.instance_findings = [RecommendationFinding(f) for f in service['instanceFindingReasonCodes']]
        self.instance_current = RDSInstanceConfiguration()
        self.instance_current.type = service['currentDBInstanceClass']

        self.instance_recommendations = []

        for recommendation in service['instanceRecommendationOptions']:
            r = RDSInstanceRecommendation()

            r.category = RecommendationCategory.INSTANCE
            r.proposed = RDSInstanceConfiguration()
            r.proposed.type = recommendation['dbInstanceClass']

            self.instance_recommendations.append(r)

        self.storage_recommendations = []

        for recommendation in service['storageRecommendationOptions']:
            r = RDSStorageRecommendation()
            r.category = RecommendationCategory.STORAGE
            r.proposed = RDSStorageConfiguration()
            r.proposed.type = recommendation['storageConfiguration']['storageType'] if 'storageType' in recommendation['storageConfiguration'] else None
            r.proposed.allocated = recommendation['storageConfiguration']['allocatedStorage'] if 'allocatedStorage' in recommendation['storageConfiguration'] else None
            r.proposed.iops = recommendation['storageConfiguration']['iops'] if 'iops' in recommendation['storageConfiguration'] else None
            r.proposed.max_allocated = recommendation['storageConfiguration']['maxAllocatedStorage'] if 'maxAllocatedStorage' in recommendation['storageConfiguration'] else None
            r.proposed.throughput = recommendation['storageConfiguration']['storageThroughput'] if 'storageThroughput' in recommendation['storageConfiguration'] else None

            self.storage_recommendations.append(r)
