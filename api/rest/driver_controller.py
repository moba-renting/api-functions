from fastapi import APIRouter, Depends, UploadFile, File, Path
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
    return {"message": driverService.upsertDriverImage(driver_id, image)}

@router.delete("/{driver_id}/image")
@inject
async def deleteDriverImage(
    driver_id: int = Path(...),
    driverService: DriverService = Depends(Provide[Container.driverService])
):
    return {"message": driverService.deleteDriverImage(driver_id)}