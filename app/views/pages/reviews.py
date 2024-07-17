from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlmodel import Session

from app import crud, models
from app.views import deps, templates

router = APIRouter()


@router.get("/reviews", response_class=HTMLResponse)
async def list_reviews(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts().from_cookies(request.cookies)
    reviews = await crud.review.get_all(db=db)
    return templates.TemplateResponse(
        "review/list.html",
        {"request": request, "reviews": reviews, "current_user": current_user, "alerts": alerts},
    )


@router.get("/review/{review_id}", response_class=HTMLResponse)
async def view_review(
    request: Request,
    review_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts()
    try:
        review = await crud.review.get(db=db, id=review_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Review not found")
        response = RedirectResponse("/reviews", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    return templates.TemplateResponse(
        "review/view.html",
        {"request": request, "review": review, "current_user": current_user, "alerts": alerts},
    )


@router.get("/reviews/create", response_class=HTMLResponse)
async def create_review(
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts().from_cookies(request.cookies)
    articles = await crud.article.get_all(db=db)
    return templates.TemplateResponse(
        "review/create.html",
        {"request": request, "articles": articles, "current_user": current_user, "alerts": alerts},
    )


@router.post("/reviews/create", response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
async def handle_create_review(
    article_id: str = Form(...),
    old_summary: str = Form(None),
    new_summary: str = Form(None),
    old_brief: str = Form(None),
    new_brief: str = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts()
    review_create = models.ReviewCreate(
        article_id=article_id,
        old_summary=old_summary,
        new_summary=new_summary,
        old_brief=old_brief,
        new_brief=new_brief,
    )
    try:
        await crud.review.create(db=db, obj_in=review_create)
    except crud.RecordAlreadyExistsError:
        alerts.danger.append("Review already exists")
        response = RedirectResponse("/reviews/create", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response

    alerts.success.append("Review successfully created")
    response = RedirectResponse(url="/reviews", status_code=status.HTTP_303_SEE_OTHER)
    response.headers["Method"] = "GET"
    response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
    return response


@router.get("/review/{review_id}/edit", response_class=HTMLResponse)
async def edit_review(
    request: Request,
    review_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts().from_cookies(request.cookies)
    try:
        review = await crud.review.get(db=db, id=review_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Review not found")
        response = RedirectResponse("/reviews", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response
    return templates.TemplateResponse(
        "review/edit.html",
        {"request": request, "review": review, "current_user": current_user, "alerts": alerts},
    )


@router.post("/review/{review_id}/edit", response_class=HTMLResponse)
async def handle_edit_review(
    review_id: str,
    old_summary: str = Form(None),
    new_summary: str = Form(None),
    old_brief: str = Form(None),
    new_brief: str = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts()
    review_update = models.ReviewUpdate(
        old_summary=old_summary, new_summary=new_summary, old_brief=old_brief, new_brief=new_brief
    )

    try:
        new_review = await crud.review.update(db=db, obj_in=review_update, id=review_id)
    except crud.RecordNotFoundError:
        alerts.danger.append("Review not found")
        response = RedirectResponse(url="/reviews", status_code=status.HTTP_303_SEE_OTHER)
        response.headers["Method"] = "GET"
        response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
        return response
    alerts.success.append("Review updated")
    return templates.TemplateResponse(
        "review/edit.html",
        {
            "request": request,
            "review": new_review,
            "current_user": current_user,
            "alerts": alerts,
        },
    )


@router.get("/review/{review_id}/delete", response_class=HTMLResponse)
async def delete_review(
    review_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Response:
    alerts = models.Alerts()
    try:
        await crud.review.remove(db=db, id=review_id)
        alerts.success.append("Review deleted")
    except crud.RecordNotFoundError:
        alerts.danger.append("Review not found")
    except crud.DeleteError:
        alerts.danger.append("Error deleting Review")

    response = RedirectResponse(url="/reviews", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="alerts", value=alerts.json(), max_age=5, httponly=True)
    return response
