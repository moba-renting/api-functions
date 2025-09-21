from fastapi import APIRouter, Depends, UploadFile, File, Path, Query
from dependency_injector.wiring import inject, Provide
from core.container import Container
from services.driver_service import DriverService

# Definir el router con prefijo y etiqueta
router = APIRouter(
    prefix="/api/v1/drivers",
    tags=["drivers"]
)

@router.put("/{driver_id}/image")
@inject
async def upsertDriverImage(
    driver_id: int = Path(...),
    image: UploadFile = File(...),
    driverService: DriverService = Depends(Provide[Container.driverService])
):
    url = driverService.upsertDriverImage(driver_id, image)
    return {"url": url}

@router.delete("/image")
@inject
async def deleteDriverImage(
    image_url: str = Query(..., description="URL of the image to delete"),
    driverService: DriverService = Depends(Provide[Container.driverService])
):
    driverService.deleteDriverImage(image_url)
    return