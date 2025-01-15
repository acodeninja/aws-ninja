from enum import Enum


def is_enrolled(session):
    response = session.client('compute-optimizer').get_enrollment_status()

    return response['status'] == 'Active'


class RecommendationResourceType(Enum):
    ECS = 'ecs'
    RDS = 'rds'


class RecommendationCategory(Enum):
    INSTANCE = 'instance'
    STORAGE = 'storage'


class RecommendationFinding(Enum):
    OPTIMIZED = 'optimized'
    UNDERPROVISIONED = 'underprovisioned'
    OVERPROVISIONED = 'overprovisioned'
    MEMORY_OVERPROVISIONED = 'memoryoverprovisioned'
    MEMORY_UNDERPROVISIONED = 'memoryunderprovisioned'
    CPU_OVERPROVISIONED = 'cpuoverprovisioned'
    CPU_UNDERPROVISIONED = 'cpuunderprovisioned'
    NEW_GENERATION_STORAGE_TYPE_AVAILABLE = 'newgenerationstoragetypeavailable'
    EBS_IOPS_OVERPROVISIONED = 'ebsiopsoverprovisioned'
    EBS_THROUGHPUT_OVERPROVISIONED = 'ebsthroughputoverprovisioned'
    NETWORK_BANDWIDTH_OVERPROVISIONED = 'networkbandwidthoverprovisioned'
    NEW_GENERATION_DB_INSTANCE_CLASS_AVAILABLE = 'newgenerationdbinstanceclassavailable'
