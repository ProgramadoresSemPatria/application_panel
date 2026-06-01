from fastapi import APIRouter, Depends, Query

from app.application.dto.admin import AdminUserUpdateDTO
from app.application.use_cases.admin.users.get_seniority_breakdown import (
    GetSeniorityBreakdownUseCase,
)
from app.application.use_cases.admin.users.get_user_detail import (
    GetAdminUserDetailUseCase,
)
from app.application.use_cases.admin.users.get_user_growth import (
    GetUserGrowthUseCase,
)
from app.application.use_cases.admin.users.list_users import (
    ListAdminUsersUseCase,
)
from app.application.use_cases.admin.users.update_admin_user import (
    UpdateAdminUserUseCase,
)
from app.core.rate_limit import RateLimit
from app.presentation.dependencies import (
    AdminRepositoryDp,
    AdminUserDp,
    CacheDp,
    UserRepositoryDp,
)
from app.presentation.schemas import DetailSchema
from app.presentation.schemas.admin import (
    AdminUpdateUserSchema,
    AdminUserDetailSchema,
    PaginatedUsersSchema,
    SeniorityBreakdownSchema,
    UserGrowthPointSchema,
)

router = APIRouter(
    prefix='/admin',
    tags=['Admin - Users'],
    responses={'403': {'model': DetailSchema}},
)


@router.get(
    '/users',
    response_model=PaginatedUsersSchema,
    dependencies=[Depends(RateLimit(60, 60, scope='user'))],
)
async def list_admin_users(
    admin: AdminUserDp,
    admin_repo: AdminRepositoryDp,
    cache: CacheDp,
    search: str | None = Query(None),
    seniority: str | None = Query(None),
    sort_by: str = Query('joined_at'),
    sort_order: str = Query('desc'),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
):
    suffix = (
        f'search={search}:seniority={seniority}'
        f':sort_by={sort_by}:sort_order={sort_order}'
        f':page={page}:per_page={per_page}'
    )
    cached, setter = await cache.get('admin_users', suffix=suffix)
    if cached is not None:
        return cached

    use_case = ListAdminUsersUseCase(admin_repo)
    dto = await use_case.execute(
        admin_id=admin.id,
        search=search,
        seniority=seniority,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page,
    )
    result = PaginatedUsersSchema.model_validate(dto)
    await setter(result, ttl=30)
    return result


@router.get(
    '/users/growth',
    response_model=list[UserGrowthPointSchema],
    dependencies=[Depends(RateLimit(30, 60, scope='user'))],
)
async def get_user_growth(
    admin: AdminUserDp,
    admin_repo: AdminRepositoryDp,
    cache: CacheDp,
):
    cached, setter = await cache.get('admin_user_growth')
    if cached is not None:
        return cached

    use_case = GetUserGrowthUseCase(admin_repo)
    dtos = await use_case.execute(admin.id)
    result = [UserGrowthPointSchema.model_validate(d) for d in dtos]
    await setter(result, ttl=300)
    return result


@router.get(
    '/users/seniority',
    response_model=list[SeniorityBreakdownSchema],
    dependencies=[Depends(RateLimit(30, 60, scope='user'))],
)
async def get_seniority_breakdown(
    admin: AdminUserDp,
    admin_repo: AdminRepositoryDp,
    cache: CacheDp,
):
    cached, setter = await cache.get('admin_user_seniority')
    if cached is not None:
        return cached

    use_case = GetSeniorityBreakdownUseCase(admin_repo)
    dtos = await use_case.execute(admin.id)
    result = [SeniorityBreakdownSchema.model_validate(d) for d in dtos]
    await setter(result, ttl=300)
    return result


@router.get(
    '/users/{user_id}',
    response_model=AdminUserDetailSchema,
    dependencies=[Depends(RateLimit(60, 60, scope='user'))],
)
async def get_admin_user_detail(
    user_id: int,
    admin: AdminUserDp,
    admin_repo: AdminRepositoryDp,
    cache: CacheDp,
):
    cached, setter = await cache.get('admin_user_detail', suffix=str(user_id))
    if cached is not None:
        return cached

    use_case = GetAdminUserDetailUseCase(admin_repo)
    dto = await use_case.execute(user_id, admin.id)
    result = AdminUserDetailSchema.model_validate(dto)
    await setter(result, ttl=60)
    return result


@router.patch(
    '/users/{user_id}',
    response_model=AdminUserDetailSchema,
    dependencies=[Depends(RateLimit(30, 60, scope='user'))],
)
async def update_admin_user(
    user_id: int,
    body: AdminUpdateUserSchema,
    admin: AdminUserDp,
    user_repo: UserRepositoryDp,
    admin_repo: AdminRepositoryDp,
    cache: CacheDp,
):
    use_case = UpdateAdminUserUseCase(user_repo, admin_repo)
    data = AdminUserUpdateDTO(**body.model_dump(exclude_unset=True))
    dto = await use_case.execute(user_id, data, admin.id)
    await cache.invalidate('admin_user_detail', suffix=str(user_id))
    await cache.invalidate('admin_users')
    return AdminUserDetailSchema.model_validate(dto)
