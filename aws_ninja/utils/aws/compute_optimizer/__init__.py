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
    OPTIMIZED = 'Optimized'
    UNDERPROVISIONED = 'Underprovisioned'
    OVERPROVISIONED = 'Overprovisioned'
    MEMORY_OVERPROVISIONED = 'MemoryOverprovisioned'
    MEMORY_UNDERPROVISIONED = 'MemoryUnderprovisioned'
    CPU_OVERPROVISIONED = 'CPUOverprovisioned'
    CPU_UNDERPROVISIONED = 'CPUUnderprovisioned'
    NEW_GENERATION_STORAGE_TYPE_AVAILABLE = 'NewGenerationStorageTypeAvailable'
    EBS_IOPS_OVERPROVISIONED = 'EBSIOPSOverprovisioned'
    EBS_THROUGHPUT_OVERPROVISIONED = 'EBSThroughputOverProvisioned'
    NETWORK_BANDWIDTH_OVERPROVISIONED = 'NetworkBandwidthOverprovisioned'
