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

    def addHeroBannerImage(self, imageFile: UploadFile) -> str:
        try:
            # Generar UUID
            imageId = str(uuid.uuid4())
            # Subir a Cloudinary
            url = self.cloudinaryService.upsertImage("home-page/hero-banners", imageId, imageFile)
            # Leer array actual
            data, count = self.supabase.table("home_page_config").select("hero_banner_urls").eq("id", 1).execute()
            currentUrls = data[1][0]["hero_banner_urls"] if data[1] else []
            # Agregar nueva URL
            currentUrls.append(url)
            # Actualizar
            self.supabase.table("home_page_config").update({"hero_banner_urls": currentUrls}).eq("id", 1).execute()
            return "Image added successfully"
        except Exception as e:
            logger.error(f"Error adding hero banner image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error adding hero banner image: {str(e)}")

    def removeHeroBannerImage(self, imageUrl: str) -> str:
        try:
            # Leer array actual
            data, count = self.supabase.table("home_page_config").select("hero_banner_urls").eq("id", 1).execute()
            currentUrls = data[1][0]["hero_banner_urls"] if data[1] else []
            if imageUrl not in currentUrls:
                raise HTTPException(status_code=404, detail="Image URL not found in banner")
            # Verificar que no quede vacío
            if len(currentUrls) == 1:
                raise HTTPException(status_code=400, detail="Cannot remove the last image from the banner")
            # Remover URL
            currentUrls.remove(imageUrl)
            # Actualizar
            self.supabase.table("home_page_config").update({"hero_banner_urls": currentUrls}).eq("id", 1).execute()
            # Extraer public_id completo y eliminar de Cloudinary
            success = self.cloudinaryService.deleteImageByUrl(imageUrl)
            if not success:
                logger.warning(f"Could not delete hero banner image from Cloudinary: {imageUrl}")
                # No lanzamos error aquí porque el array ya se actualizó en la BD
            return "Image removed successfully"
        except Exception as e:
            logger.error(f"Error removing hero banner image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error removing hero banner image: {str(e)}")

    def upsertB2bBenefitsImage(self, newB2bBenefitsImage: UploadFile) -> str:
        try:
            # Subir imagen a Cloudinary
            url = self.cloudinaryService.upsertImage("home-page/b2b_benefits", "image", newB2bBenefitsImage)
            
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
            url = self.cloudinaryService.upsertImage("home-page/b2c_benefits", "image", newB2cBenefitsImage)

            # Actualizar base de datos
            data, count = self.supabase.table("home_page_config") \
                .update({"b2c_benefits_url": url}) \
                .eq("id", 1) \
                .execute()
            
            return "B2C benefits image updated successfully"
        except Exception as e:
            logger.error(f"Error updating B2C benefits image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating B2C benefits image: {str(e)}")