import logging
import base64
import json
import re
from typing import Optional, Dict, Any
from fastapi import HTTPException, UploadFile
from openai import OpenAI
from core.config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def extract_driver_info_from_image(self, image_file: UploadFile) -> Dict[str, Any]:
        """
        Analiza una imagen de la app de conductor y extrae información relevante.
        
        Returns:
            Dict con estructura:
            {
                "app": str | None,
                "name": str | None,
                "totalTrips": int | None,
                "timeInApp": {"value": int, "unit": str} | None,
                "rawText": str
            }
        """
        try:
            # Leer y convertir la imagen a base64
            image_content = image_file.file.read()
            base64_image = base64.b64encode(image_content).decode('utf-8')
            
            # Resetear el puntero del archivo para usos posteriores si es necesario
            image_file.file.seek(0)
            
            # Crear el prompt para OpenAI
            prompt = """Analiza la imagen de la app de conductor y extrae:
- APP que usa el conductor (p.ej. INDRIVE, UBER, YANGO, CABIFY)
- Nombre del conductor
- Total de viajes (número)
- Tiempo en la app (en formato {value: número, unit: "months"/"years"})
- Calificación/Rating del conductor (número de estrellas, típicamente 1-5)

Devuelve SOLO un JSON válido con esta estructura:
{
  "app": string | null,
  "name": string | null,
  "totalTrips": number | null,
  "timeInApp": {value: number, unit: string} | null,
  "rating": number | null
}"""

            # Hacer la llamada a OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{image_file.content_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )

            # Extraer la respuesta
            raw_text = response.choices[0].message.content or ""
            clean_text = raw_text.strip()

            # Extraer JSON de la respuesta usando regex
            json_match = re.search(r'\{[\s\S]*\}', clean_text)
            if not json_match:
                logger.error(f"No se encontró JSON en la respuesta de OpenAI: {clean_text}")
                raise HTTPException(
                    status_code=500, 
                    detail="No se pudo extraer información estructurada de la imagen"
                )

            # Parsear el JSON
            try:
                parsed_data = json.loads(json_match.group(0))
            except json.JSONDecodeError as e:
                logger.error(f"Error al parsear JSON de OpenAI: {e}. Respuesta: {json_match.group(0)}")
                raise HTTPException(
                    status_code=500, 
                    detail="La respuesta de OpenAI no contiene un JSON válido"
                )

            # Validar y normalizar los datos
            result = {
                "app": self._normalize_app_name(parsed_data.get("app")),
                "name": parsed_data.get("name") if parsed_data.get("name") else None,
                "totalTrips": self._parse_int(parsed_data.get("totalTrips")),
                "timeInApp": self._validate_time_in_app(parsed_data.get("timeInApp")),
                "rating": self._parse_rating(parsed_data.get("rating")),
                "rawText": raw_text
            }

            logger.info(f"Información extraída exitosamente: {result}")
            return result

        except HTTPException:
            # Re-raise HTTPExceptions
            raise
        except Exception as e:
            logger.error(f"Error al procesar imagen con OpenAI: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error al procesar la imagen: {str(e)}"
            )

    def _normalize_app_name(self, app_name: Any) -> Optional[str]:
        """Normaliza el nombre de la app."""
        if not app_name or not isinstance(app_name, str):
            return None
        
        # Convertir a mayúsculas y limpiar
        normalized = app_name.upper().strip()
        
        # Validar que sea una app conocida
        known_apps = ["INDRIVE", "UBER", "YANGO", "CABIFY", "DIDI", "BEAT"]
        for known_app in known_apps:
            if known_app in normalized:
                return known_app
        
        return normalized if normalized else None

    def _parse_int(self, value: Any) -> Optional[int]:
        """Convierte un valor a entero de forma segura."""
        if value is None:
            return None
        
        try:
            if isinstance(value, (int, float)):
                return int(value)
            elif isinstance(value, str):
                # Extraer números de la cadena
                numbers = re.findall(r'\d+', value.replace(',', ''))
                if numbers:
                    return int(numbers[0])
            return None
        except (ValueError, TypeError):
            return None

    def _validate_time_in_app(self, time_data: Any) -> Optional[Dict[str, Any]]:
        """Valida y normaliza los datos de tiempo en la app."""
        if not time_data or not isinstance(time_data, dict):
            return None
        
        value = self._parse_int(time_data.get("value"))
        unit = time_data.get("unit")
        
        if value is None or not unit:
            return None
        
        # Normalizar la unidad
        unit = unit.lower().strip()
        if unit in ["month", "months", "mes", "meses"]:
            unit = "months"
        elif unit in ["year", "years", "año", "años"]:
            unit = "years"
        else:
            # Si la unidad no es reconocida, intentar inferir
            if value > 24:  # Probablemente meses
                unit = "months"
            else:  # Probablemente años
                unit = "years"
        
        return {"value": value, "unit": unit}

    def _parse_rating(self, value: Any) -> Optional[float]:
        """Convierte un valor a calificación de estrellas de forma segura."""
        if value is None:
            return None
        
        try:
            if isinstance(value, (int, float)):
                rating = float(value)
                # Validar que esté en el rango correcto
                if 0 <= rating <= 5:
                    return round(rating, 2)
            elif isinstance(value, str):
                # Extraer números de la cadena, incluyendo decimales
                import re
                numbers = re.findall(r'\d+\.?\d*', value.replace(',', '.'))
                if numbers:
                    rating = float(numbers[0])
                    if 0 <= rating <= 5:
                        return round(rating, 2)
            return None
        except (ValueError, TypeError):
            return None