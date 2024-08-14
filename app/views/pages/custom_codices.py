from fastapi import APIRouter, Body, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from sqlmodel import Session
from typing import List, Optional

from app import crud, models
from app.views import deps, templates
from app.services import custom_codices
from app.services.custom_codices import update_custom_codex_article

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
) -> HTMLResponse:
    custom_codex = await crud.custom_codex.get(db=db, id=codex_id)
    if not custom_codex:
        # Handle the case where the custom codex is not found
        # You might want to redirect to an error page or the list of custom codices
        pass

    custom_codex_articles = await crud.custom_codex_article.get_multi_by_codex_id(
        db=db, codex_id=codex_id
    )

    return templates.TemplateResponse(
        "custom_codex/view.html",
        {
            "request": request,
            "custom_codex": custom_codex,
            "custom_codex_articles": custom_codex_articles,
            "current_user": current_user,
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
    context_length: int = Form(None),
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


# @router.get("/custom_codex/{codex_id}/edit", response_class=HTMLResponse)
# async def edit_custom_codex(
#     request: Request,
#     codex_id: str,
#     db: Session = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Response:
#     alerts = models.Alerts().from_cookies(request.cookies)
#     try:
#         custom_codex = await crud.custom_codex.get(db=db, id=codex_id)
#     except crud.RecordNotFoundError:
#         alerts.danger.append("Custom Codex not found")
#         response = RedirectResponse("/custom_codices", status_code=status.HTTP_302_FOUND)
#         response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
#         return response
#     return templates.TemplateResponse(
#         "custom_codex/edit.html",
#         {
#             "request": request,
#             "custom_codex": custom_codex,
#             "current_user": current_user,
#             "alerts": alerts,
#         },
#     )


# @router.post("/custom_codex/{codex_id}/edit", response_class=HTMLResponse)
# async def handle_edit_custom_codex(
#     request: Request,
#     codex_id: str,
#     name: str = Form(...),
#     context_length: int = Form(...),
#     year_start: int = Form(None),
#     year_end: int = Form(None),
#     tags: str = Form(None),
#     db: Session = Depends(deps.get_db),
#     current_user: models.User = Depends(deps.get_current_active_user),
# ) -> Response:
#     alerts = models.Alerts()
#     tags_list = tags.split(",") if tags else None
#     custom_codex_update = models.CustomCodexUpdate(
#         name=name,
#         context_length=context_length,
#         year_start=year_start,
#         year_end=year_end,
#         tags=tags_list,
#     )

#     try:
#         new_custom_codex = await crud.custom_codex.update(
#             db=db, obj_in=custom_codex_update, id=codex_id
#         )
#     except crud.RecordNotFoundError:
#         alerts.danger.append("Custom Codex not found")
#         response = RedirectResponse(url="/custom_codices", status_code=status.HTTP_303_SEE_OTHER)
#         response.headers["Method"] = "GET"
#         response.set_cookie(key="alerts", value=alerts.json(), httponly=True, max_age=5)
#         return response
#     alerts.success.append("Custom Codex updated")
#     return templates.TemplateResponse(
#         "custom_codex/edit.html",
#         {
#             "request": request,
#             "custom_codex": new_custom_codex,
#             "current_user": current_user,
#             "alerts": alerts,
#         },
#     )


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
        articles = await crud.article.get_all(db=db)
        custom_codex_articles = await crud.custom_codex_article.get_multi_by_codex_id(
            db, codex_id=codex_id
        )
        context_length = await calculate_context_length(db=db, codex_id=codex_id)

        # Create a dictionary for easier access in the template
        article_types_dict = {cca.article_id: cca.article_type for cca in custom_codex_articles}

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
            "articles": articles,
            "article_types_dict": article_types_dict,
            "context_length": context_length,
            "current_user": current_user,
            "alerts": alerts,
        },
    )


@router.post("/custom_codex/{codex_id}/edit", response_class=HTMLResponse)
async def handle_edit_custom_codex(
    request: Request,
    codex_id: str,
    name: str = Form(...),
    context_length: Optional[int] = Form(None),
    year_start: Optional[int] = Form(None),
    year_end: Optional[int] = Form(None),
    tags: Optional[str] = Form(None),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> JSONResponse:
    alerts = models.Alerts()
    tags_list = tags.split(",") if tags else None
    custom_codex_update = models.CustomCodexUpdate(
        id=codex_id,
        name=name,
        context_length=context_length,
        year_start=year_start,
        year_end=year_end,
        tags=tags_list,
    )

    try:
        # Update the CustomCodex
        await crud.custom_codex.update(db=db, obj_in=custom_codex_update, id=codex_id)

        # Get all articles
        all_articles = await crud.article.get_all(db=db)

        # Process form data for article types
        form_data = await request.form()

        # Update or create CustomCodexArticle for each article
        for article in all_articles:
            article_type_key = f"article_types_{article.id}"
            article_type = str(
                form_data.get(article_type_key, "Full")
            )  # Default to "Full" if not selected

            # Check if CustomCodexArticle already exists

            existing_cca = await crud.custom_codex_article.get_or_none(
                db=db, codex_id=codex_id, article_id=article.id
            )

            if existing_cca:
                # Update existing CustomCodexArticle
                cca_update = models.CustomCodexArticleUpdate(
                    codex_id=codex_id, article_id=article.id, article_type=article_type
                )
                await crud.custom_codex_article.update(db=db, id=existing_cca.id, obj_in=cca_update)
            else:
                # Create new CustomCodexArticle
                cca_create = models.CustomCodexArticleCreate(
                    codex_id=codex_id,
                    article_id=article.id,
                    article_type=article_type,
                )
                await crud.custom_codex_article.create(db=db, obj_in=cca_create)

        return JSONResponse(
            content={"success": True, "message": "Custom Codex and articles updated successfully"}
        )
    except crud.RecordNotFoundError:
        return JSONResponse(
            content={"success": False, "message": "Custom Codex not found"}, status_code=404
        )
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"Error updating Custom Codex: {str(e)}"},
            status_code=500,
        )


@router.post("/custom_codex/{codex_id}/calculate_context_length")
async def calculate_context_length(
    codex_id: str,
    article_types: dict = Body(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> dict:

    try:
        for article_id, article_type in article_types.items():
            await update_custom_codex_article(db, codex_id, article_id, article_type)

        context_length = await custom_codices.calculate_context_length(db, codex_id)
        return {"context_length": context_length}
    except Exception as e:
        # raise HTTPException(status_code=400, detail=str(e))
        return {"context_length": 0}
