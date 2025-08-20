import cloudinary.uploader
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
