import logging
import uuid
from fastapi import HTTPException, UploadFile
from services.cloudinary_service import CloudinaryService

logger = logging.getLogger(__name__)

class DriverService:
    def __init__(self, cloudinaryService: CloudinaryService):
        self.cloudinaryService = cloudinaryService

    def upsertDriverImage(self, driver_id: int, imageFile: UploadFile) -> str:
        try:
            # Subir nueva imagen con public_id fijo (Cloudinary sobrescribe automáticamente)
            url = self.cloudinaryService.upsertImage(f"drivers/{driver_id}", "image", imageFile)

            return url
        except Exception as e:
            logger.error(f"Error uploading driver image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading driver image: {str(e)}")

    def deleteDriverImage(self, image_url: str) -> None:
        try:
            if not image_url:
                raise HTTPException(status_code=400, detail="Image URL is required")

            # Intentar eliminar la imagen de Cloudinary
            self.cloudinaryService.deleteImageByUrl(image_url)

        except Exception as e:
            logger.error(f"Error deleting driver image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting driver image: {str(e)}")