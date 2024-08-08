from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlmodel import Session

from app import crud, models
from app.views import deps, templates

router = APIRouter()


@router.get("/custom_codices", response_class=HTMLResponse)
async def list_custom_codices(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts().from_cookies(request.cookies)
    custom_codices = await crud.custom_codex.get_all(db=db)
    return templates.TemplateResponse(
        "custom_codex/list.html",
        {
            "request": request,
            "custom_codices": custom_codices,
            "current_user": current_user,
            "alerts": alerts,
        },
    )


@router.get("/custom_codex/{codex_id}", response_class=HTMLResponse)
async def view_custom_codex(
    request: Request,
    codex_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts()
    try:
        custom_codex = await crud.custom_codex.get(db=db, id=codex_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Custom Codex not found")
        response = RedirectResponse("/custom_codices", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    return templates.TemplateResponse(
        "custom_codex/view.html",
        {
            "request": request,
            "custom_codex": custom_codex,
            "current_user": current_user,
            "alerts": alerts,
        },
    )


@router.get("/custom_codices/create", response_class=HTMLResponse)
async def create_custom_codex(
    request: Request, current_user: models.User = Depends(deps.get_current_active_user)
) -> Response:
    alerts = models.Alerts().from_cookies(request.cookies)
    return templates.TemplateResponse(
        "custom_codex/create.html",
        {"request": request, "current_user": current_user, "alerts": alerts},
    )


@router.post(
    "/custom_codices/create", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED
)
async def handle_create_custom_codex(
    name: str = Form(...),
    context_length: int = Form(...),
    year_start: int = Form(None),
    year_end: int = Form(None),
    tags: str = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts()
    tags_list = tags.split(",") if tags else None
    custom_codex_create = models.CustomCodexCreate(
        name=name,
        context_length=context_length,
        year_start=year_start,
        year_end=year_end,
        tags=tags_list,
    )
    try:
        await crud.custom_codex.create(db=db, obj_in=custom_codex_create)
    except crud.RecordAlreadyExistsError:
        alerts.danger.append("Custom Codex already exists")
        response = RedirectResponse("/custom_codices/create", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    alerts.success.append("Custom Codex successfully created")
    response = RedirectResponse(url="/custom_codices", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["Method"] = "GET"
    response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
    return response


@router.get("/custom_codex/{codex_id}/edit", response_class=HTMLResponse)
async def edit_custom_codex(
    request: Request,
    codex_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts().from_cookies(request.cookies)
    try:
        custom_codex = await crud.custom_codex.get(db=db, id=codex_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Custom Codex not found")
        response = RedirectResponse("/custom_codices", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response
    return templates.TemplateResponse(
        "custom_codex/edit.html",
        {
            "request": request,
            "custom_codex": custom_codex,
            "current_user": current_user,
            "alerts": alerts,
        },
    )


@router.post("/custom_codex/{codex_id}/edit", response_class=HTMLResponse)
async def handle_edit_custom_codex(
    request: Request,
    codex_id: str,
    name: str = Form(...),
    context_length: int = Form(...),
    year_start: int = Form(None),
    year_end: int = Form(None),
    tags: str = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts()
    tags_list = tags.split(",") if tags else None
    custom_codex_update = models.CustomCodexUpdate(
        name=name,
        context_length=context_length,
        year_start=year_start,
        year_end=year_end,
        tags=tags_list,
    )

    try:
        new_custom_codex = await crud.custom_codex.update(
            db=db, obj_in=custom_codex_update, id=codex_id
        )
    except crud.RecordNotFoundError:
        alerts.danger.append("Custom Codex not found")
        response = RedirectResponse(url="/custom_codices", status_code=status.HTTP_303_SEE_OTHER)
        response.headers["Method"] = "GET"
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response
    alerts.success.append("Custom Codex updated")
    return templates.TemplateResponse(
        "custom_codex/edit.html",
        {
            "request": request,
            "custom_codex": new_custom_codex,
            "current_user": current_user,
            "alerts": alerts,
        },
    )


@router.get("/custom_codex/{codex_id}/delete", response_class=HTMLResponse)
async def delete_custom_codex(
    codex_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts()
    try:
        await crud.custom_codex.remove(db=db, id=codex_id)
        alerts.success.append("Custom Codex deleted")
    except crud.RecordNotFoundError:
        alerts.danger.append("Custom Codex not found")
    except crud.DeleteError:
        alerts.danger.append("Error deleting Custom Codex")

    response = RedirectResponse(url="/custom_codices", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="alerts", value=alerts.json(), max_age=5, httponly=True)
    return response
