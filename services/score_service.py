import logging
from typing import Dict, Any, Optional, Tuple, List
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ScoreDriverService:
    # Parámetros base del modelo crediticio
    INGRESO_PROMEDIO_POR_VIAJE = 12  # soles
    PORCENTAJE_DESTINO_CUOTA = 0.30  # 30% del ingreso
    MESES_EVALUACION = 12  # para calcular promedio mensual

    def __init__(self):
        """
        Inicializar el servicio de scoring del conductor.
        """
        self.rangos_viajes, self.rangos_antiguedad, self.rangos_calificacion = self._crear_tabla_scoring()

    def _crear_tabla_scoring(self) -> Tuple[List[Tuple], List[Tuple], List[Tuple]]:
        """
        Crear las tablas de scoring por rangos.
        
        Returns:
            Tuple con los rangos de viajes, antigüedad y calificación
        """
        # Definir rangos y puntajes
        rangos_viajes = [
            (0, 1000, 10, "Muy bajo - Conductor ocasional"),
            (1001, 3000, 25, "Bajo - Conductor part-time"),
            (3001, 6000, 50, "Medio - Conductor regular"),
            (6001, 10000, 75, "Alto - Conductor activo"),
            (10001, float('inf'), 100, "Muy alto - Conductor profesional")
        ]
        
        rangos_antiguedad = [
            (0, 0.5, 5, "Menos de 6 meses - Muy nuevo"),
            (0.5, 1, 15, "6-12 meses - Nuevo"),
            (1, 2, 30, "1-2 años - Establecido"),
            (2, 3, 45, "2-3 años - Experimentado"),
            (3, float('inf'), 60, "Más de 3 años - Veterano")
        ]
        
        rangos_calificacion = [
            (0, 3.5, 0, "Muy baja - Alto riesgo"),
            (3.5, 4.0, 10, "Baja - Riesgo medio-alto"),
            (4.0, 4.3, 25, "Regular - Riesgo medio"),
            (4.3, 4.6, 40, "Buena - Riesgo bajo"),
            (4.6, 4.8, 55, "Muy buena - Muy bajo riesgo"),
            (4.8, 5.0, 70, "Excelente - Riesgo mínimo")
        ]
        
        return rangos_viajes, rangos_antiguedad, rangos_calificacion

    def calcular_capacidad_pago(self, num_viajes: int, anos_antiguedad: float) -> Dict[str, float]:
        """
        Calcular la capacidad de pago del conductor.
        
        Args:
            num_viajes: Número total de viajes
            anos_antiguedad: Años de antigüedad en la app
            
        Returns:
            Dict con viajes mensuales, ingreso mensual y capacidad de pago
        """
        try:
            # Calcular viajes mensuales promedio
            viajes_mensuales = num_viajes / (anos_antiguedad * 12) if anos_antiguedad > 0 else 0
            
            # Calcular ingreso mensual estimado
            ingreso_mensual = viajes_mensuales * self.INGRESO_PROMEDIO_POR_VIAJE
            
            # Calcular capacidad de pago (30% del ingreso)
            capacidad_pago = ingreso_mensual * self.PORCENTAJE_DESTINO_CUOTA
            
            return {
                "viajes_mensuales": round(viajes_mensuales, 0),
                "ingreso_mensual": round(ingreso_mensual, 0),
                "capacidad_pago": round(capacidad_pago, 0)
            }
        except Exception as e:
            logger.error(f"Error calculando capacidad de pago: {str(e)}")
            raise HTTPException(status_code=500, detail="Error calculando capacidad de pago")

    def calcular_score(self, num_viajes: int, anos_antiguedad: float, calificacion: float) -> Dict[str, Any]:
        """
        Calcular el score crediticio del conductor.
        
        Args:
            num_viajes: Número total de viajes
            anos_antiguedad: Años de antigüedad en la app
            calificacion: Calificación promedio (estrellas)
            
        Returns:
            Dict con el score detallado y descripción
        """
        try:
            # Validar inputs
            if num_viajes < 0:
                raise HTTPException(status_code=400, detail="El número de viajes no puede ser negativo")
            if anos_antiguedad < 0:
                raise HTTPException(status_code=400, detail="La antigüedad no puede ser negativa")
            if calificacion < 0 or calificacion > 5:
                raise HTTPException(status_code=400, detail="La calificación debe estar entre 0 y 5")

            score_total = 0
            
            # Score por número de viajes
            score_viajes = 0
            desc_viajes = ""
            for min_val, max_val, puntos, desc in self.rangos_viajes:
                if min_val <= num_viajes <= max_val:
                    score_viajes = puntos
                    desc_viajes = desc
                    break
            
            # Score por antigüedad
            score_antiguedad = 0
            desc_antiguedad = ""
            for min_val, max_val, puntos, desc in self.rangos_antiguedad:
                if min_val <= anos_antiguedad <= max_val:
                    score_antiguedad = puntos
                    desc_antiguedad = desc
                    break
            
            # Score por calificación
            score_calificacion = 0
            desc_calificacion = ""
            for min_val, max_val, puntos, desc in self.rangos_calificacion:
                if min_val <= calificacion <= max_val:
                    score_calificacion = puntos
                    desc_calificacion = desc
                    break
            
            # Calcular score total (máximo 230 puntos, normalizar a 100)
            score_bruto = score_viajes + score_antiguedad + score_calificacion
            score_normalizado = min(100, (score_bruto / 230) * 100)
            
            # Calcular capacidad de pago
            capacidad_info = self.calcular_capacidad_pago(num_viajes, anos_antiguedad)
            
            # Determinar status de aprobación
            status_aprobacion = self._determinar_status_aprobacion(score_normalizado)
            
            resultado = {
                'score_total': round(score_normalizado, 1),
                'score_viajes': score_viajes,
                'score_antiguedad': score_antiguedad,
                'score_calificacion': score_calificacion,
                'desc_viajes': desc_viajes,
                'desc_antiguedad': desc_antiguedad,
                'desc_calificacion': desc_calificacion,
                'capacidad_pago': capacidad_info,
                'status_aprobacion': status_aprobacion,
                'input_data': {
                    'num_viajes': num_viajes,
                    'anos_antiguedad': anos_antiguedad,
                    'calificacion': calificacion
                }
            }
            
            logger.info(f"Score calculado exitosamente: {score_normalizado}/100 para {num_viajes} viajes, {anos_antiguedad} años, {calificacion} estrellas")
            return resultado
            
        except HTTPException:
            # Re-raise HTTPExceptions
            raise
        except Exception as e:
            logger.error(f"Error calculando score: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error calculando score: {str(e)}")

    def _determinar_status_aprobacion(self, score: float) -> Dict[str, str]:
        """
        Determinar el status de aprobación basado en el score.
        
        Args:
            score: Score calculado (0-100)
            
        Returns:
            Dict con status y descripción
        """
        if score >= 70:
            return {
                "status": "PREAPROBADO",
                "emoji": "✅",
                "descripcion": "Conductor califica para préstamo"
            }
        elif score >= 40:
            return {
                "status": "EN_EVALUACION", 
                "emoji": "⚠️",
                "descripcion": "Requiere evaluación adicional"
            }
        else:
            return {
                "status": "NO_CALIFICA",
                "emoji": "❌", 
                "descripcion": "No califica para préstamo"
            }

    def calcular_score_completo_desde_datos(self, driver_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcular score completo desde los datos extraídos de OpenAI.
        
        Args:
            driver_data: Datos del conductor con estructura:
            {
                "name": str,
                "totalTrips": int,
                "timeInApp": {"value": int, "unit": str},
                "rating": float (opcional)
            }
            
        Returns:
            Dict con score completo y análisis
        """
        try:
            # Extraer datos
            name = driver_data.get("name", "Conductor")
            total_trips = driver_data.get("totalTrips", 0)
            time_in_app = driver_data.get("timeInApp", {})
            rating = driver_data.get("rating", 4.0)  # Default 4.0 si no se proporciona
            
            # Convertir tiempo en app a años
            time_value = time_in_app.get("value", 0) if time_in_app else 0
            time_unit = time_in_app.get("unit", "months") if time_in_app else "months"
            
            if time_unit == "months":
                anos_antiguedad = time_value / 12
            else:  # years
                anos_antiguedad = time_value
            
            # Calcular score
            score_result = self.calcular_score(total_trips, anos_antiguedad, rating)
            
            # Agregar información del conductor
            score_result["conductor_info"] = {
                "app": driver_data.get("app", "Desconocida"),
                "name": name,
                "totalTrips": total_trips,
                "timeInApp": time_in_app,
                "rating": rating,
                "anos_antiguedad_calculados": round(anos_antiguedad, 2)
            }
            
            return score_result
            
        except Exception as e:
            logger.error(f"Error calculando score desde datos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error procesando datos del conductor: {str(e)}")

    def get_scoring_ranges(self) -> Dict[str, List[Dict]]:
        """
        Obtener las tablas de rangos de scoring para referencia.
        
        Returns:
            Dict con todos los rangos y puntajes
        """
        def format_range(rangos):
            formatted = []
            for min_val, max_val, puntos, desc in rangos:
                formatted.append({
                    "min": min_val,
                    "max": max_val if max_val != float('inf') else None,
                    "puntos": puntos,
                    "descripcion": desc
                })
            return formatted
        
        return {
            "viajes": format_range(self.rangos_viajes),
            "antiguedad": format_range(self.rangos_antiguedad),
            "calificacion": format_range(self.rangos_calificacion),
            "parametros": {
                "ingreso_promedio_por_viaje": self.INGRESO_PROMEDIO_POR_VIAJE,
                "porcentaje_destino_cuota": self.PORCENTAJE_DESTINO_CUOTA,
                "meses_evaluacion": self.MESES_EVALUACION
            }
        }