from fastapi import APIRouter, Depends, UploadFile, File, Path
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
    return {"message": categoryService.upsertCategoryImage(category_id, image)}

@router.delete("/{category_id}/image")
@inject
async def deleteCategoryImage( 
    category_id: int = Path(...),
    categoryService: CategoryService = Depends(Provide[Container.categoryService])
):
    return {"message": categoryService.deleteCategoryImage(category_id)}
