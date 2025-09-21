from fastapi import APIRouter, Depends, UploadFile, File, Query, Path
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
    return {"message": vehicleService.addVehicleImage(vehicle_id, image)}

@router.delete("/{vehicle_id}/images/remove")
@inject
async def removeVehicleImage( 
    vehicle_id: int = Path(...),
    imageUrl: str = Query(...),
    vehicleService: VehicleService = Depends(Provide[Container.vehicleService])
):
    return {"message": vehicleService.removeVehicleImage(vehicle_id, imageUrl)}