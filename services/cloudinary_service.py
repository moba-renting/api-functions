import cloudinary.uploader
import logging
from fastapi import UploadFile, HTTPException
from core.config import settings

class CloudinaryService:
    def __init__(self):
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY, 
            api_secret=settings.CLOUDINARY_API_SECRET, 
            secure=settings.CLOUDINARY_SECURE
        )

    def upsertImage(self, folder: str, publicId: str, imageFile: UploadFile) -> str:
        try:
            fileContent = imageFile.file.read()

            response = cloudinary.uploader.upload(
                fileContent,
                folder=folder,
                public_id=publicId,
                use_filename=True,
                unique_filename=False,
                overwrite=True
            )

            return response.get("secure_url")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al subir la imagen: {str(e)}")

    def deleteImage(self, publicId: str) -> None:
        try:
            cloudinary.uploader.destroy(publicId)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}")

    def deleteImageByUrl(self, imageUrl: str) -> None:
        """
        Elimina una imagen de Cloudinary usando su URL completa.
        
        Ejemplo:
        URL: https://res.cloudinary.com/cloud/image/upload/v123/vehicles/456/uuid.jpg
        Extrae: vehicles/456/uuid y elimina esa imagen
        """
        try:
            publicId = self.extractPublicIdFromUrl(imageUrl)
            self.deleteImage(publicId)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not delete image from Cloudinary: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting image from Cloudinary: {str(e)}")

    def extractPublicIdFromUrl(self, imageUrl: str) -> str:
        """
        Extrae el public_id completo (incluyendo carpetas) de una URL de Cloudinary.
        
        Ejemplo:
        URL: https://res.cloudinary.com/cloud/image/upload/v123/vehicles/456/uuid.jpg
        Retorna: vehicles/456/uuid
        """
        try:
            # URL típica: https://res.cloudinary.com/cloud/image/upload/v123/folder/subfolder/filename.jpg
            url_parts = imageUrl.split('/upload/')
            if len(url_parts) > 1:
                path_and_file = url_parts[1]  # "v123/folder/subfolder/filename.jpg"
                # Remover la parte de versión (v123/)
                version_removed = '/'.join(path_and_file.split('/')[1:])  # "folder/subfolder/filename.jpg"
                # Remover extensión
                publicId = version_removed.rsplit('.', 1)[0]  # "folder/subfolder/filename"
                return publicId
            else:
                # Fallback: extraer de la URL completa
                parts = imageUrl.split('/')
                return parts[-1].split('.')[0]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting public_id from URL: {str(e)}")
