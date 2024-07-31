from typing import Optional
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlmodel import Session

from app import crud, models
from app.views import deps, templates
from app.services.articles import generate_new_article_summary, import_articles_from_worldanvil

router = APIRouter()


@router.get("/articles", response_class=HTMLResponse)
async def list_articles(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    Returns HTML response with list of articles.

    Args:
        request(Request): The request object
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: HTML page with the articles

    """
    # Get alerts dict from cookies
    alerts = models.Alerts().from_cookies(request.cookies)

    articles = await crud.article.get_all(db=db, sort_by="title")
    return templates.TemplateResponse(
        "article/list.html",
        {"request": request, "articles": articles, "current_user": current_user, "alerts": alerts},
    )


@router.get("/articles/all", response_class=HTMLResponse)
async def list_all_articles(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_superuser
    ),
) -> Response:
    """
    Returns HTML response with list of all articles from all users.

    Args:
        request(Request): The request object
        db(Session): The database session.
        current_user(User): The authenticated superuser.

    Returns:
        Response: HTML page with the articles

    """
    # Get alerts dict from cookies
    alerts = models.Alerts().from_cookies(request.cookies)

    articles = await crud.article.get_all(db=db, sort_by="title")
    return templates.TemplateResponse(
        "article/list.html",
        {"request": request, "articles": articles, "current_user": current_user, "alerts": alerts},
    )


@router.get("/article/{article_id}", response_class=HTMLResponse)
async def view_article(
    request: Request,
    article_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    View article.

    Args:
        request(Request): The request object
        article_id(str): The article id
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: View of the article
    """
    alerts = models.Alerts()
    try:
        article = await crud.article.get(db=db, id=article_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Article not found")
        response = RedirectResponse("/articles", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    return templates.TemplateResponse(
        "article/view.html",
        {"request": request, "article": article, "current_user": current_user, "alerts": alerts},
    )


@router.post("/articles/create", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def handle_create_article(
    title: str = Form(...),
    description: str = Form(None),
    url: str = Form(...),
    year_start: Optional[int] = Form(None),
    year_end: Optional[int] = Form(None),
    tags: str = Form(None),
    text: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    brief: Optional[str] = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    """
    Handles the creation of a new article.
    """
    alerts = models.Alerts()

    # Convert tags string to list
    tags_list = [tag.strip() for tag in tags.split(",")] if tags else None

    article_create = models.ArticleCreate(
        title=title,
        description=description,
        url=url,
        year_start=year_start,
        year_end=year_end,
        tags=tags_list,
        text=text,
        summary=summary,
        brief=brief,
    )
    try:
        await crud.article.create(db=db, obj_in=article_create)
    except crud.RecordAlreadyExistsError:
        alerts.danger.append("Article already exists")
        response = RedirectResponse("/articles/create", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    alerts.success.append("Article successfully created")
    response = RedirectResponse(url="/articles", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["Method"] = "GET"
    response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
    return response


@router.post("/articles/create", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def handle_create_article(
    title: str = Form(...),
    description: str = Form(...),
    url: str = Form(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    Handles the creation of a new article.

    Args:
        title(str): The title of the article
        description(str): The description of the article
        url(str): The url of the article
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: List of articles view
    """
    alerts = models.Alerts()
    article_create = models.ArticleCreate(
        title=title, description=description, url=url, owner_id=current_user.id
    )
    try:
        await crud.article.create(db=db, obj_in=article_create)
    except crud.RecordAlreadyExistsError:
        alerts.danger.append("Article already exists")
        response = RedirectResponse("/articles/create", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    alerts.success.append("Article successfully created")
    response = RedirectResponse(url="/articles", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["Method"] = "GET"
    response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
    return response


@router.get("/article/{article_id}/edit", response_class=HTMLResponse)
async def edit_article(
    request: Request,
    article_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    New Article form.

    Args:
        request(Request): The request object
        article_id(str): The article id
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: Form to create a new article
    """
    alerts = models.Alerts().from_cookies(request.cookies)
    try:
        article = await crud.article.get(db=db, id=article_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Article not found")
        response = RedirectResponse("/articles", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response
    return templates.TemplateResponse(
        "article/edit.html",
        {"request": request, "article": article, "current_user": current_user, "alerts": alerts},
    )


@router.post("/article/{article_id}/edit", response_class=HTMLResponse)
async def handle_edit_article(
    request: Request,
    article_id: str,
    title: str = Form(...),
    description: str = Form(None),
    url: str = Form(...),
    year_start: Optional[int] = Form(None),
    year_end: Optional[int] = Form(None),
    tags: str = Form(None),
    text: Optional[str] = Form(None),
    summary: Optional[str] = Form(None),
    brief: Optional[str] = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    """
    Handles the editing of an article.
    """
    alerts = models.Alerts()
    tags_list = [tag.strip() for tag in tags.split(",")] if tags else None
    article_update = models.ArticleUpdate(
        title=title,
        description=description,
        url=url,
        year_start=year_start,
        year_end=year_end,
        tags=tags_list,
        text=text,
        summary=summary,
        brief=brief,
    )

    try:
        new_article = await crud.article.update(db=db, obj_in=article_update, id=article_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Article not found")
        response = RedirectResponse(url="/articles", status_code=status.HTTP_303_SEE_OTHER)
        response.headers["Method"] = "GET"
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response
    alerts.success.append("Article updated")
    return templates.TemplateResponse(
        "article/edit.html",
        {
            "request": request,
            "article": new_article,
            "current_user": current_user,
            "alerts": alerts,
        },
    )


@router.get("/article/{article_id}/delete", response_class=HTMLResponse)
async def delete_article(
    article_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    New Article form.

    Args:
        article_id(str): The article id
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: Form to create a new article
    """
    alerts = models.Alerts()
    try:
        await crud.article.remove(db=db, id=article_id)
        alerts.success.append("Article deleted")
    except crud.RecordNotFoundError:
        alerts.danger.append("Article not found")
    except crud.DeleteError:
        alerts.danger.append("Error deleting article")

    response = RedirectResponse(url="/articles", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="alerts", value=alerts.json(), max_age=5, httponly=True)
    return response


@router.post("/import-articles", response_class=HTMLResponse)
async def import_articles(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    """
    Imports articles from World Anvil
    """
    alerts = models.Alerts()

    await import_articles_from_worldanvil()

    alerts.success.append("Article's Imported from World Anvil.")

    response = RedirectResponse(url="/articles", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="alerts", value=alerts.json(), max_age=5, httponly=True)
    return response


@router.get("/article/{article_id}/generate-summary", response_class=HTMLResponse)
async def generate_article_summary(
    request: Request,
    article_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(  # pylint: disable=unused-argument
        deps.get_current_active_user
    ),
) -> Response:
    """
    Generate Article Summary

    Args:
        request(Request): The request object
        article_id(str): The article id
        db(Session): The database session.
        current_user(User): The authenticated user.

    Returns:
        Response: View of the article
    """
    alerts = models.Alerts()

    await generate_new_article_summary(db=db, article_id=article_id)

    alerts.success.append("Article's summary was generated")

    response = RedirectResponse(url="/article/{article_id}", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="alerts", value=alerts.json(), max_age=5, httponly=True)
    return response
