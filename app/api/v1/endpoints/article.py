from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.api import deps

router = APIRouter()
ModelClass = models.Article
ModelReadClass = models.ArticleRead
ModelCreateClass = models.ArticleCreate
ModelUpdateClass = models.ArticleUpdate
model_crud = crud.article


@router.post("/", response_model=ModelReadClass, status_code=status.HTTP_201_CREATED)
async def create_with_uploader_id(
    *,
    db: Session = Depends(deps.get_db),
    obj_in: ModelCreateClass,
    current_active_user: models.User = Depends(deps.get_current_active_user),
) -> ModelClass:
    """
    Create a new article.

    Args:
        obj_in (ModelCreateClass): object to be created.
        db (Session): database session.
        current_active_user (models.User): Current active user.

    Returns:
        ModelClass: Created object.

    Raises:
        HTTPException: if object already exists.
    """
    try:
        return await model_crud.create_with_owner_id(
            db=db, obj_in=obj_in, owner_id=current_active_user.id
        )
    except crud.RecordAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_200_OK, detail="Article already exists"
        ) from exc


@router.get("/{id}", response_model=ModelReadClass)
async def get(
    *,
    db: Session = Depends(deps.get_db),
    id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> ModelClass:
    """
    Retrieve a article by id.

    Args:
        id (str): id of the article.
        db (Session): database session.
        current_user (Any): authenticated user.

    Returns:
        ModelClass: Retrieved object.

    Raises:
        HTTPException: if object does not exist.
        HTTPException: if user is not superuser and object does not belong to user.
    """
    article = await model_crud.get_or_none(id=id, db=db)
    if article:
        if crud.user.is_superuser(user_=current_user) or article.owner_id == current_user.id:
            return article

    elif crud.user.is_superuser(user_=current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


@router.get("/", response_model=list[ModelReadClass])
async def get_multi(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> list[ModelClass]:
    """
    Retrieve articles.

    Args:
        db (Session): database session.
        skip (int): Number of articles to skip. Defaults to 0.
        limit (int): Number of articles to return. Defaults to 100.
        current_user (models.User): Current active user.

    Returns:
        list[ModelClass]: List of objects.
    """
    return (
        await model_crud.get_multi(db=db, skip=skip, limit=limit)
        if crud.user.is_superuser(user_=current_user)
        else await model_crud.get_multi_by_owner_id(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    )


@router.patch("/{id}", response_model=ModelReadClass)
async def update(
    *,
    db: Session = Depends(deps.get_db),
    id: str,
    obj_in: ModelUpdateClass,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> ModelClass:
    """
    Update an article.

    Args:
        id (str): ID of the article to update.
        obj_in (ModelUpdateClass): object to update.
        db (Session): database session.
        current_user (Any): authenticated user.

    Returns:
        ModelClass: Updated object.

    Raises:
        HTTPException: if object not found.
    """
    article = await model_crud.get_or_none(id=id, db=db)
    if article:
        if crud.user.is_superuser(user_=current_user) or article.owner_id == current_user.id:
            return await model_crud.update(db=db, obj_in=obj_in, id=id)

    elif crud.user.is_superuser(user_=current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    *,
    db: Session = Depends(deps.get_db),
    id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> None:
    """
    Delete an article.

    Args:
        id (str): ID of the article to delete.
        db (Session): database session.
        current_user (models.User): authenticated user.

    Returns:
        None

    Raises:
        HTTPException: if article not found.
    """

    article = await model_crud.get_or_none(id=id, db=db)
    if article:
        if crud.user.is_superuser(user_=current_user) or article.owner_id == current_user.id:
            return await model_crud.remove(id=id, db=db)

    elif crud.user.is_superuser(user_=current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
