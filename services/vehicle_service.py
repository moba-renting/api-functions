import logging
import uuid
from typing import List
from fastapi import HTTPException, UploadFile
from services.cloudinary_service import CloudinaryService

logger = logging.getLogger(__name__)

class VehicleService:
    def __init__(self, cloudinaryService: CloudinaryService):
        self.cloudinaryService = cloudinaryService

    def addVehicleImage(self, vehicle_id: int, imageFile: UploadFile) -> str:
        try:
            # Generar UUID
            imageId = str(uuid.uuid4())
            # Subir a Cloudinary
            url = self.cloudinaryService.upsertImage(f"vehicles/{vehicle_id}", imageId, imageFile)
            return url
        except Exception as e:
            logger.error(f"Error uploading vehicle image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading vehicle image: {str(e)}")

    def removeVehicleImage(self, imageUrls: List[str]) -> None:
        try:
            if not imageUrls or len(imageUrls) == 0:
                raise HTTPException(status_code=400, detail="At least one image URL is required")

            # Eliminar todas las imágenes de Cloudinary
            for imageUrl in imageUrls:
                if imageUrl:  # Solo procesar URLs no vacías
                    self.cloudinaryService.deleteImageByUrl(imageUrl)
        except Exception as e:
            logger.error(f"Error deleting vehicle images: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting vehicle images: {str(e)}")