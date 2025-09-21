from fastapi import APIRouter, Depends, UploadFile, File, Path, Query
from dependency_injector.wiring import inject, Provide
from core.container import Container
from services.category_service import CategoryService

# Definir el router con prefijo y etiqueta
router = APIRouter(
    prefix="/api/v1/categories",
    tags=["categories"]
)

@router.put("/{category_id}/image")
@inject
async def upsertCategoryImage( 
    category_id: int = Path(...),
    image: UploadFile = File(...),
    categoryService: CategoryService = Depends(Provide[Container.categoryService])
):
    url = categoryService.upsertCategoryImage(category_id, image)
    return {"url": url}

@router.delete("/image")
@inject
async def deleteCategoryImage(
    image_url: str = Query(..., description="URL of the image to delete"),
    categoryService: CategoryService = Depends(Provide[Container.categoryService])
):
    categoryService.deleteCategoryImage(image_url)
    return
