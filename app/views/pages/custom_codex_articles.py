from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlmodel import Session

from app import crud, models
from app.views import deps, templates

router = APIRouter()


@router.get("/custom_codex/{codex_id}/articles", response_class=HTMLResponse)
async def list_custom_codex_articles(
    request: Request,
    codex_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts().from_cookies(request.cookies)
    custom_codex = await crud.custom_codex.get(db=db, id=codex_id)
    custom_codex_articles = await crud.custom_codex_article.get_multi_by_codex_id(
        db=db, codex_id=codex_id
    )
    return templates.TemplateResponse(
        "custom_codex_article/list.html",
        {
            "request": request,
            "custom_codex": custom_codex,
            "custom_codex_articles": custom_codex_articles,
            "current_user": current_user,
            "alerts": alerts,
        },
    )


@router.get("/custom_codex/{codex_id}/article/{article_id}", response_class=HTMLResponse)
async def view_custom_codex_article(
    request: Request,
    codex_id: str,
    article_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts()
    try:
        custom_codex_article = await crud.custom_codex_article.get(
            db=db, codex_id=codex_id, article_id=article_id
        )
    except crud.RecordNotFoundError:
        alerts.danger.append("Custom Codex Article not found")
        response = RedirectResponse(
            f"/custom_codex/{codex_id}/articles", status_code=status.HTTP_303_SEE_OTHER
        )
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    return templates.TemplateResponse(
        "custom_codex_article/view.html",
        {
            "request": request,
            "custom_codex_article": custom_codex_article,
            "current_user": current_user,
            "alerts": alerts,
        },
    )


@router.get("/custom_codex/{codex_id}/articles/create", response_class=HTMLResponse)
async def create_custom_codex_article(
    request: Request,
    codex_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts().from_cookies(request.cookies)
    custom_codex = await crud.custom_codex.get(db=db, id=codex_id)
    articles = await crud.article.get_all(db=db)
    return templates.TemplateResponse(
        "custom_codex_article/create.html",
        {
            "request": request,
            "custom_codex": custom_codex,
            "articles": articles,
            "current_user": current_user,
            "alerts": alerts,
        },
    )


@router.post(
    "/custom_codex/{codex_id}/articles/create",
    response_class=HTMLResponse,
    status_code=status.HTTP_201_CREATED,
)
async def handle_create_custom_codex_article(
    codex_id: str,
    article_id: str = Form(...),
    article_type: str = Form(...),
    custom_text: str = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts()
    custom_codex_article_create = models.CustomCodexArticleCreate(
        codex_id=codex_id, article_id=article_id, article_type=article_type, custom_text=custom_text
    )
    try:
        await crud.custom_codex_article.create(db=db, obj_in=custom_codex_article_create)
    except crud.RecordAlreadyExistsError:
        alerts.danger.append("Custom Codex Article already exists")
        response = RedirectResponse(
            f"/custom_codex/{codex_id}/articles/create", status_code=status.HTTP_302_FOUND
        )
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    alerts.success.append("Custom Codex Article successfully created")
    response = RedirectResponse(
        url=f"/custom_codex/{codex_id}/articles", status_code=status.HTTP_303_SEE_OTHER
    )
    response.headers["Method"] = "GET"
    response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
    return response


@router.get("/custom_codex/{codex_id}/article/{article_id}/edit", response_class=HTMLResponse)
async def edit_custom_codex_article(
    request: Request,
    codex_id: str,
    article_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts().from_cookies(request.cookies)
    try:
        custom_codex_article = await crud.custom_codex_article.get(
            db=db, codex_id=codex_id, article_id=article_id
        )
    except crud.RecordNotFoundError:
        alerts.danger.append("Custom Codex Article not found")
        response = RedirectResponse(
            f"/custom_codex/{codex_id}/articles", status_code=status.HTTP_302_FOUND
        )
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response
    return templates.TemplateResponse(
        "custom_codex_article/edit.html",
        {
            "request": request,
            "custom_codex_article": custom_codex_article,
            "current_user": current_user,
            "alerts": alerts,
        },
    )


@router.post("/custom_codex/{codex_id}/article/{article_id}/edit", response_class=HTMLResponse)
async def handle_edit_custom_codex_article(
    request: Request,
    codex_id: str,
    article_id: str,
    article_type: str = Form(...),
    custom_text: str = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts()
    custom_codex_article_update = models.CustomCodexArticleUpdate(
        article_type=article_type, custom_text=custom_text
    )

    try:
        new_custom_codex_article = await crud.custom_codex_article.update(
            db=db, obj_in=custom_codex_article_update, codex_id=codex_id, article_id=article_id
        )
    except crud.RecordNotFoundError:
        alerts.danger.append("Custom Codex Article not found")
        response = RedirectResponse(
            url=f"/custom_codex/{codex_id}/articles", status_code=status.HTTP_303_SEE_OTHER
        )
        response.headers["Method"] = "GET"
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response
    alerts.success.append("Custom Codex Article updated")
    return templates.TemplateResponse(
        "custom_codex_article/edit.html",
        {
            "request": request,
            "custom_codex_article": new_custom_codex_article,
            "current_user": current_user,
            "alerts": alerts,
        },
    )


@router.get("/custom_codex/{codex_id}/article/{article_id}/delete", response_class=HTMLResponse)
async def delete_custom_codex_article(
    codex_id: str,
    article_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts()
    try:
        await crud.custom_codex_article.remove(db=db, codex_id=codex_id, article_id=article_id)
        alerts.success.append("Custom Codex Article deleted")
    except crud.RecordNotFoundError:
        alerts.danger.append("Custom Codex Article not found")
    except crud.DeleteError:
        alerts.danger.append("Error deleting Custom Codex Article")

    response = RedirectResponse(
        url=f"/custom_codex/{codex_id}/articles", status_code=status.HTTP_303_SEE_OTHER
    )
    response.set_cookie(key="alerts", value=alerts.json(), max_age=5, httponly=True)
    return response
