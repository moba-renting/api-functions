import json
import logging
import uuid
from typing import List
from fastapi import HTTPException, UploadFile
from services.cloudinary_service import CloudinaryService
from supabase import create_client, Client
from core.config import settings

logger = logging.getLogger(__name__)

class HomePageService:
    def __init__(self, cloudinaryService: CloudinaryService):
        self.cloudinaryService = cloudinaryService
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    def upsertHeroBannerImages(self, newHeroBannerImages: List[UploadFile]) -> str:
        try:
            # Subir imágenes a Cloudinary
            uploadedUrls = []
            for i, imageFile in enumerate(newHeroBannerImages):
                url = self.cloudinaryService.upsertImage("home-page", f"hero_banner_{i+1}", imageFile)
                uploadedUrls.append(url)
            
            # Actualizar base de datos
            data, count = self.supabase.table("home_page_config") \
                .update({"hero_banner_urls": uploadedUrls}) \
                .eq("id", 1) \
                .execute()
            
            return "Hero banner images updated successfully"
        except Exception as e:
            logger.error(f"Error updating hero banner images: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating hero banner images: {str(e)}")

    def upsertB2bBenefitsImage(self, newB2bBenefitsImage: UploadFile) -> str:
        try:
            # Subir imagen a Cloudinary
            url = self.cloudinaryService.upsertImage("home-page", "b2b_benefits", newB2bBenefitsImage)
            
            # Actualizar base de datos
            data, count = self.supabase.table("home_page_config") \
                .update({"b2b_benefits_url": url}) \
                .eq("id", 1) \
                .execute()
            
            return "B2B benefits image updated successfully"
        except Exception as e:
            logger.error(f"Error updating B2B benefits image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating B2B benefits image: {str(e)}")

    def upsertB2cBenefitsImage(self, newB2cBenefitsImage: UploadFile) -> str:
        try:
            # Subir imagen a Cloudinary
            url = self.cloudinaryService.upsertImage("home-page", "b2c_benefits", newB2cBenefitsImage)
            
            # Actualizar base de datos
            data, count = self.supabase.table("home_page_config") \
                .update({"b2c_benefits_url": url}) \
                .eq("id", 1) \
                .execute()
            
            return "B2C benefits image updated successfully"
        except Exception as e:
            logger.error(f"Error updating B2C benefits image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating B2C benefits image: {str(e)}")