import logging
import uuid
from typing import List
from fastapi import HTTPException, UploadFile
from services.cloudinary_service import CloudinaryService
from supabase import create_client, Client
from core.config import settings

logger = logging.getLogger(__name__)

class VehicleService:
    def __init__(self, cloudinaryService: CloudinaryService):
        self.cloudinaryService = cloudinaryService
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    def addVehicleImage(self, vehicle_id: int, imageFile: UploadFile) -> str:
        try:
            # Leer array actual
            data, count = self.supabase.table("vehicles").select("image_urls").eq("id", vehicle_id).execute()
            if not data[1]:
                raise HTTPException(status_code=404, detail="Vehicle not found")
            currentUrls = data[1][0]["image_urls"] or []
            
            # Generar UUID
            imageId = str(uuid.uuid4())
            # Subir a Cloudinary
            url = self.cloudinaryService.upsertImage(f"vehicles/{vehicle_id}", imageId, imageFile)
            # Agregar nueva URL
            currentUrls.append(url)
            # Actualizar
            self.supabase.table("vehicles").update({"image_urls": currentUrls}).eq("id", vehicle_id).execute()
            return "Image added successfully"
        except Exception as e:
            logger.error(f"Error adding vehicle image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error adding vehicle image: {str(e)}")

    def removeVehicleImage(self, vehicle_id: int, imageUrl: str) -> str:
        try:
            # Leer array actual
            data, count = self.supabase.table("vehicles").select("image_urls").eq("id", vehicle_id).execute()
            if not data[1]:
                raise HTTPException(status_code=404, detail="Vehicle not found")
            currentUrls = data[1][0]["image_urls"] or []
            
            if imageUrl not in currentUrls:
                raise HTTPException(status_code=404, detail="Image URL not found in vehicle")
            # Verificar que no quede vacío
            if len(currentUrls) == 1:
                raise HTTPException(status_code=400, detail="Cannot remove the last image from the vehicle")
            # Remover URL
            currentUrls.remove(imageUrl)
            # Actualizar
            self.supabase.table("vehicles").update({"image_urls": currentUrls}).eq("id", vehicle_id).execute()
            # Extraer public_id completo y eliminar de Cloudinary
            success = self.cloudinaryService.deleteImageByUrl(imageUrl)
            if not success:
                logger.warning(f"Could not delete vehicle image from Cloudinary: {imageUrl}")
                # No lanzamos error aquí porque el vehículo ya se actualizó en la BD
            return "Image removed successfully"
        except Exception as e:
            logger.error(f"Error removing vehicle image: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error removing vehicle image: {str(e)}")