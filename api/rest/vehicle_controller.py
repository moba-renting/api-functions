from fastapi import APIRouter, Depends, UploadFile, File, Query, Path
from typing import List
from dependency_injector.wiring import inject, Provide
from core.container import Container
from services.vehicle_service import VehicleService

# Definir el router con prefijo y etiqueta
router = APIRouter(
    prefix="/api/v1/vehicles",
    tags=["vehicles"]
)

@router.post("/{vehicle_id}/images/add")
@inject
async def addVehicleImage( 
    vehicle_id: int = Path(...),
    image: UploadFile = File(...),
    vehicleService: VehicleService = Depends(Provide[Container.vehicleService])
):
    url = vehicleService.addVehicleImage(vehicle_id, image)
    return {"url": url}

@router.delete("/images/remove")
@inject
async def removeVehicleImage( 
    imageUrls: List[str] = Query(..., description="URLs of the images to delete"),
    vehicleService: VehicleService = Depends(Provide[Container.vehicleService])
):
    vehicleService.removeVehicleImage(imageUrls)
    return