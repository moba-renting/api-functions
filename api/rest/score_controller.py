from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from typing import Dict, Any
from dependency_injector.wiring import inject, Provide
from core.container import Container
from services.score_service import ScoreDriverService
from services.openai_service import OpenAIService

# Definir el router con prefijo y etiqueta
router = APIRouter(
    prefix="/api/v1/score",
    tags=["score"]
)

@router.post("/calculate-from-image", response_model=Dict[str, Any])
@inject
async def calculate_score_from_image(
    image: UploadFile = File(..., description="Imagen de la pantalla de la app del conductor"),
    openai_service: OpenAIService = Depends(Provide[Container.openaiService]),
    score_service: ScoreDriverService = Depends(Provide[Container.scoreService])
):
    """
    Analiza una imagen de la app del conductor y calcula su score crediticio.
    
    Este endpoint combina la extracción de datos con OpenAI y el cálculo de score.
    
    Args:
        image: Archivo de imagen (PNG, JPG, JPEG, WebP)
        
    Returns:
        Dict con toda la información del conductor y su score crediticio:
        - conductor_info: Datos extraídos de la imagen
        - score_total: Score final (0-100)
        - score_detallado: Desglose por categorías
        - capacidad_pago: Análisis financiero
        - status_aprobacion: Estado de pre-aprobación
    """
    
    # Validar tipo de archivo
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen válida (PNG, JPG, JPEG, WebP)"
        )
    
    try:
        # 1. Extraer información de la imagen con OpenAI
        driver_data = openai_service.extract_driver_info_from_image(image)
        
        # 2. Asegurar que la app esté incluida en los datos para el scoring
        driver_data_with_app = {
            "name": driver_data.get("name"),
            "totalTrips": driver_data.get("totalTrips"),
            "timeInApp": driver_data.get("timeInApp"),
            "rating": driver_data.get("rating"),
            "app": driver_data.get("app")  # Incluir explícitamente la app
        }
        
        # 3. Calcular score basado en los datos extraídos
        score_result = score_service.calcular_score_completo_desde_datos(driver_data_with_app)
        
        # 4. Combinar resultados
        complete_result = {
            **score_result,
            "extraction_info": {
                "app": driver_data.get("app"),
                "rawText": driver_data.get("rawText", "")
            }
        }
        
        return complete_result
    
    except HTTPException:
        # Re-raise HTTPExceptions from services
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando imagen y calculando score: {str(e)}"
        )

@router.post("/calculate", response_model=Dict[str, Any])
@inject
async def calculate_score_manual(
    total_trips: int = Query(..., description="Número total de viajes", ge=0),
    years_experience: float = Query(..., description="Años de experiencia", ge=0),
    rating: float = Query(..., description="Calificación (estrellas)", ge=0, le=5),
    driver_name: str = Query(None, description="Nombre del conductor (opcional)"),
    score_service: ScoreDriverService = Depends(Provide[Container.scoreService])
):
    """
    Calcula el score crediticio del conductor con parámetros manuales.
    
    Args:
        total_trips: Número total de viajes realizados
        years_experience: Años de experiencia como conductor
        rating: Calificación promedio (1-5 estrellas)
        driver_name: Nombre del conductor (opcional)
        
    Returns:
        Dict con el análisis completo del score crediticio
    """
    
    try:
        # Crear estructura de datos compatible
        driver_data = {
            "name": driver_name or "Conductor",
            "totalTrips": total_trips,
            "timeInApp": {
                "value": int(years_experience * 12),  # Convertir a meses
                "unit": "months"
            },
            "rating": rating
        }
        
        # Calcular score
        result = score_service.calcular_score_completo_desde_datos(driver_data)
        
        return result
    
    except HTTPException:
        # Re-raise HTTPExceptions from service
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculando score: {str(e)}"
        )

@router.get("/ranges", response_model=Dict[str, Any])
@inject
async def get_scoring_ranges(
    score_service: ScoreDriverService = Depends(Provide[Container.scoreService])
):
    """
    Obtiene las tablas de rangos y puntajes utilizados para el scoring.
    
    Returns:
        Dict con todos los rangos de scoring y parámetros del modelo
    """
    
    try:
        ranges = score_service.get_scoring_ranges()
        return ranges
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo rangos de scoring: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Endpoint de salud para verificar que el servicio de scoring está funcionando.
    """
    return {
        "status": "healthy",
        "service": "Score Driver Service",
        "message": "Scoring service is running correctly",
        "model_version": "v1.0",
        "parameters": {
            "ingreso_promedio_por_viaje": ScoreDriverService.INGRESO_PROMEDIO_POR_VIAJE,
            "porcentaje_destino_cuota": ScoreDriverService.PORCENTAJE_DESTINO_CUOTA
        }
    }

@router.post("/simulate", response_model=Dict[str, Any])
@inject
async def simulate_multiple_scenarios(
    scenarios: list = Query(..., description="Lista de escenarios para simular"),
    score_service: ScoreDriverService = Depends(Provide[Container.scoreService])
):
    """
    Simula múltiples escenarios de scoring para análisis comparativo.
    
    Args:
        scenarios: Lista de objetos con {total_trips, years_experience, rating, name}
        
    Returns:
        Dict con los resultados de todos los escenarios
    """
    
    try:
        results = []
        
        for i, scenario in enumerate(scenarios):
            try:
                driver_data = {
                    "name": scenario.get("name", f"Conductor {i+1}"),
                    "totalTrips": scenario.get("total_trips", 0),
                    "timeInApp": {
                        "value": int(scenario.get("years_experience", 0) * 12),
                        "unit": "months"
                    },
                    "rating": scenario.get("rating", 4.0)
                }
                
                score_result = score_service.calcular_score_completo_desde_datos(driver_data)
                results.append({
                    "scenario_id": i + 1,
                    "input": scenario,
                    "result": score_result
                })
                
            except Exception as scenario_error:
                results.append({
                    "scenario_id": i + 1,
                    "input": scenario,
                    "error": str(scenario_error)
                })
        
        return {
            "total_scenarios": len(scenarios),
            "results": results,
            "summary": {
                "successful": len([r for r in results if "error" not in r]),
                "failed": len([r for r in results if "error" in r])
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error simulando escenarios: {str(e)}"
        )