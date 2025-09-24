from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import Dict, Any
from dependency_injector.wiring import inject, Provide
from core.container import Container
from services.openai_service import OpenAIService

# Definir el router con prefijo y etiqueta
router = APIRouter(
    prefix="/api/v1/ai",
    tags=["ai"]
)

@router.post("/analyze-driver-image", response_model=Dict[str, Any])
@inject
async def analyze_driver_image(
    image: UploadFile = File(..., description="Imagen de la pantalla de la app del conductor"),
    openai_service: OpenAIService = Depends(Provide[Container.openaiService])
):
    """
    Analiza una imagen de la app de conductor y extrae información relevante.
    
    Args:
        image: Archivo de imagen (PNG, JPG, JPEG, WebP)
        
    Returns:
        Dict con la información extraída:
        - app: Nombre de la aplicación (UBER, INDRIVE, etc.)
        - name: Nombre del conductor
        - totalTrips: Número total de viajes
        - timeInApp: Tiempo usando la app {value, unit}
        - rawText: Texto crudo de la respuesta de OpenAI
    """
    
    # Validar tipo de archivo
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen válida (PNG, JPG, JPEG, WebP)"
        )
    
    # Validar tamaño del archivo (máximo 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Leer el contenido para verificar el tamaño
    content = await image.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="El archivo es demasiado grande. Máximo permitido: 10MB"
        )
    
    # Recrear el UploadFile con el contenido leído
    from io import BytesIO
    image.file = BytesIO(content)
    
    try:
        # Procesar la imagen con OpenAI
        result = openai_service.extract_driver_info_from_image(image)
        return result
    
    except HTTPException:
        # Re-raise HTTPExceptions from service
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al procesar la imagen: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Endpoint de salud para verificar que el servicio de AI está funcionando.
    """
    return {
        "status": "healthy",
        "service": "OpenAI Service",
        "message": "AI service is running correctly"
    }