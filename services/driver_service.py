import logging
import uuid
from fastapi import HTTPException, UploadFile
from services.cloudinary_service import CloudinaryService
from supabase import create_client, Client
from core.config import settings

logger = logging.getLogger(__name__)

class DriverService:
    def __init__(self, cloudinaryService: CloudinaryService):
        self.cloudinaryService = cloudinaryService
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    def upsertDriverImage(self, driver_id: int, imageFile: UploadFile) -> str:
        try:
            # Verificar que el driver existe
            data, count = self.supabase.table("drivers").select("id").eq("id", driver_id).execute()
            if not data[1]:
                raise HTTPException(status_code=404, detail="Driver not found")

            # Subir nueva imagen con public_id fijo (Cloudinary sobrescribe automáticamente)
            url = self.cloudinaryService.upsertImage(f"drivers/{driver_id}", "image", imageFile)

            # Actualizar base de datos
            self.supabase.table("drivers").update({"image_url": url}).eq("id", driver_id).execute()

            return "Driver image updated successfully"
        except Exception as e:
            logger.error(f"Error updating driver image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error updating driver image: {str(e)}")

    def deleteDriverImage(self, driver_id: int) -> str:
        try:
            # Obtener la imagen actual
            data, count = self.supabase.table("drivers").select("image_url").eq("id", driver_id).execute()
            if not data[1]:
                raise HTTPException(status_code=404, detail="Driver not found")

            image_url = data[1][0]["image_url"]

            if not image_url:
                raise HTTPException(status_code=400, detail="Driver has no image to delete")

            # Intentar eliminar la imagen de Cloudinary
            success = self.cloudinaryService.deleteImageByUrl(image_url)

            if success:
                # Si la eliminación fue exitosa, actualizar la base de datos
                self.supabase.table("drivers").update({"image_url": None}).eq("id", driver_id).execute()
                return "Driver image deleted successfully"
            else:
                raise HTTPException(status_code=500, detail="Failed to delete image from Cloudinary")

        except Exception as e:
            logger.error(f"Error deleting driver image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting driver image: {str(e)}")