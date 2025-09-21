import logging
import uuid
from typing import List
from fastapi import HTTPException, UploadFile
from services.cloudinary_service import CloudinaryService

logger = logging.getLogger(__name__)

class HomePageService:
    def __init__(self, cloudinaryService: CloudinaryService):
        self.cloudinaryService = cloudinaryService

    def addHeroBannerImage(self, imageFile: UploadFile) -> str:
        try:
            # Generar UUID
            imageId = str(uuid.uuid4())
            # Subir a Cloudinary
            url = self.cloudinaryService.upsertImage("home-page/hero-banners", imageId, imageFile)
            return url
        except Exception as e:
            logger.error(f"Error uploading hero banner image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading hero banner image: {str(e)}")

    def removeHeroBannerImage(self, imageUrls: List[str]) -> None:
        try:
            if not imageUrls or len(imageUrls) == 0:
                raise HTTPException(status_code=400, detail="At least one image URL is required")

            # Eliminar todas las imágenes de Cloudinary
            for imageUrl in imageUrls:
                if imageUrl:  # Solo procesar URLs no vacías
                    self.cloudinaryService.deleteImageByUrl(imageUrl)
        except Exception as e:
            logger.error(f"Error deleting hero banner images: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting hero banner images: {str(e)}")

    def upsertB2bBenefitsImage(self, newB2bBenefitsImage: UploadFile) -> str:
        try:
            # Subir imagen a Cloudinary
            url = self.cloudinaryService.upsertImage("home-page/b2b_benefits", "image", newB2bBenefitsImage)
            return url
        except Exception as e:
            logger.error(f"Error uploading B2B benefits image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading B2B benefits image: {str(e)}")

    def upsertB2cBenefitsImage(self, newB2cBenefitsImage: UploadFile) -> str:
        try:
            # Subir imagen a Cloudinary
            url = self.cloudinaryService.upsertImage("home-page/b2c_benefits", "image", newB2cBenefitsImage)
            return url
        except Exception as e:
            logger.error(f"Error uploading B2C benefits image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading B2C benefits image: {str(e)}")