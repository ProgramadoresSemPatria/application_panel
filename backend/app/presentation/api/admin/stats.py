from fastapi import APIRouter, Depends

from app.application.use_cases.admin.stats.get_activity_heatmap import (
    GetActivityHeatmapUseCase,
)
from app.application.use_cases.admin.stats.get_platform_stats import (
    GetPlatformStatsUseCase,
)
from app.application.use_cases.admin.stats.get_top_companies import (
    GetTopCompaniesUseCase,
)
from app.application.use_cases.admin.stats.get_top_platforms import (
    GetTopPlatformsUseCase,
)
from app.core.rate_limit import RateLimit
from app.presentation.dependencies import (
    AdminRepositoryDp,
    AdminUserDp,
    CacheDp,
)
from app.presentation.schemas import DetailSchema
from app.presentation.schemas.admin import (
    ActivityHeatmapPointSchema,
    AdminPlatformStatsSchema,
    TopCompanyStatSchema,
    TopPlatformStatSchema,
)

router = APIRouter(
    prefix='/admin',
    tags=['Admin - Stats'],
    responses={'403': {'model': DetailSchema}},
)


@router.get(
    '/stats',
    response_model=AdminPlatformStatsSchema,
    dependencies=[Depends(RateLimit(30, 60, scope='user'))],
)
async def get_admin_stats(
    admin: AdminUserDp,
    admin_repo: AdminRepositoryDp,
    cache: CacheDp,
):
    cached, setter = await cache.get('admin_stats')
    if cached is not None:
        return cached

    use_case = GetPlatformStatsUseCase(admin_repo)
    dto = await use_case.execute(admin.id)
    result = AdminPlatformStatsSchema.model_validate(dto)
    await setter(result, ttl=120)
    return result


@router.get(
    '/stats/top-platforms',
    response_model=list[TopPlatformStatSchema],
    dependencies=[Depends(RateLimit(30, 60, scope='user'))],
)
async def get_top_platforms(
    admin: AdminUserDp,
    admin_repo: AdminRepositoryDp,
    cache: CacheDp,
):
    cached, setter = await cache.get('admin_stats_top_platforms')
    if cached is not None:
        return cached

    use_case = GetTopPlatformsUseCase(admin_repo)
    dtos = await use_case.execute(admin.id)
    result = [TopPlatformStatSchema.model_validate(d) for d in dtos]
    await setter(result, ttl=120)
    return result


@router.get(
    '/stats/top-companies',
    response_model=list[TopCompanyStatSchema],
    dependencies=[Depends(RateLimit(30, 60, scope='user'))],
)
async def get_top_companies(
    admin: AdminUserDp,
    admin_repo: AdminRepositoryDp,
    cache: CacheDp,
):
    cached, setter = await cache.get('admin_stats_top_companies')
    if cached is not None:
        return cached

    use_case = GetTopCompaniesUseCase(admin_repo)
    dtos = await use_case.execute(admin.id)
    result = [TopCompanyStatSchema.model_validate(d) for d in dtos]
    await setter(result, ttl=120)
    return result


@router.get(
    '/stats/activity-heatmap',
    response_model=list[ActivityHeatmapPointSchema],
    dependencies=[Depends(RateLimit(30, 60, scope='user'))],
)
async def get_activity_heatmap(
    admin: AdminUserDp,
    admin_repo: AdminRepositoryDp,
    cache: CacheDp,
):
    cached, setter = await cache.get('admin_stats_activity_heatmap')
    if cached is not None:
        return cached

    use_case = GetActivityHeatmapUseCase(admin_repo)
    dtos = await use_case.execute(admin.id)
    result = [ActivityHeatmapPointSchema.model_validate(d) for d in dtos]
    await setter(result, ttl=120)
    return result
