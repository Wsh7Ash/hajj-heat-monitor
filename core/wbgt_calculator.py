"""
Wet Bulb Globe Temperature (WBGT) Calculator

This module provides comprehensive WBGT calculations for heat stress
assessment following ISO 7243 and OSHA standards.
"""

import math
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class WBGTInputs:
    """Input parameters for WBGT calculation."""
    air_temperature: float  # Dry bulb temperature (°C)
    relative_humidity: float  # Relative humidity (%)
    wind_speed: float  # Wind speed (m/s)
    solar_radiation: Optional[float] = None  # Solar radiation (W/m²)
    globe_temperature: Optional[float] = None  # Globe temperature (°C)


@dataclass
class WBGTResult:
    """Result of WBGT calculation."""
    wbgt: float  # WBGT temperature (°C)
    wet_bulb: float  # Wet bulb temperature (°C)
    globe_temperature: float  # Globe temperature (°C)
    air_temperature: float  # Air temperature (°C)
    relative_humidity: float  # Relative humidity (%)
    wind_speed: float  # Wind speed (m/s)
    solar_radiation: float  # Solar radiation (W/m²)
    heat_stress_level: str  # Heat stress level
    risk_score: float  # Risk score (0-10)
    color_code: str  # Color code for warnings


class WBGTCalculator:
    """
    Calculator for Wet Bulb Globe Temperature (WBGT).
    
    This class implements standard WBGT calculations for heat stress
    assessment in occupational and outdoor settings.
    """
    
    def __init__(self):
        """Initialize the WBGT calculator."""
        self.stefan_boltzmann = 5.67e-8  # Stefan-Boltzmann constant
        self.emissivity = 0.95  # Emissivity of black globe
        
        # Heat stress thresholds (ISO 7243)
        self.thresholds = {
            'low': {'max_wbgt': 25.0, 'color': '#00FF00', 'level': 'low'},
            'moderate': {'max_wbgt': 27.9, 'color': '#FFFF00', 'level': 'moderate'},
            'high': {'max_wbgt': 30.0, 'color': '#FFA500', 'level': 'high'},
            'very_high': {'max_wbgt': 32.0, 'color': '#FF0000', 'level': 'very_high'},
            'extreme': {'min_wbgt': 32.0, 'color': '#8B0000', 'level': 'extreme'}
        }
    
    def calculate_wbgt(self, inputs: WBGTInputs) -> WBGTResult:
        """
        Calculate WBGT from input parameters.
        
        Args:
            inputs: WBGT input parameters
        
        Returns:
            WBGTResult with calculated values
        """
        try:
            # Calculate wet bulb temperature
            wet_bulb = self._calculate_wet_bulb(
                inputs.air_temperature,
                inputs.relative_humidity
            )
            
            # Calculate or estimate globe temperature
            if inputs.globe_temperature:
                globe_temp = inputs.globe_temperature
            else:
                globe_temp = self._estimate_globe_temperature(
                    inputs.air_temperature,
                    inputs.solar_radiation or 800,  # Default solar radiation
                    inputs.wind_speed
                )
            
            # Calculate WBGT
            wbgt = self._calculate_wbgt_from_components(wet_bulb, globe_temp)
            
            # Determine heat stress level
            stress_level, risk_score, color = self._assess_heat_stress(wbgt)
            
            return WBGTResult(
                wbgt=wbgt,
                wet_bulb=wet_bulb,
                globe_temperature=globe_temp,
                air_temperature=inputs.air_temperature,
                relative_humidity=inputs.relative_humidity,
                wind_speed=inputs.wind_speed,
                solar_radiation=inputs.solar_radiation or 800,
                heat_stress_level=stress_level,
                risk_score=risk_score,
                color_code=color
            )
            
        except Exception as e:
            logger.error(f"WBGT calculation failed: {e}")
            raise
    
    def _calculate_wet_bulb(self, air_temp: float, rh: float) -> float:
        """
        Calculate wet bulb temperature using Stull's formula.
        
        Args:
            air_temp: Air temperature (°C)
            rh: Relative humidity (%)
        
        Returns:
            Wet bulb temperature (°C)
        """
        # Stull (2011) formula for wet bulb temperature
        # This is an approximation with good accuracy for typical conditions
        
        # Convert to Kelvin for calculations
        T = air_temp + 273.15
        
        # Calculate dew point temperature
        a = 17.27
        b = 237.7
        
        alpha = ((a * air_temp) / (b + air_temp)) + math.log(rh / 100.0)
        dew_point = (b * alpha) / (a - alpha)
        
        # Calculate wet bulb temperature
        gamma = 0.00066 * 1013.25  # psychrometric constant
        c1 = 0.00066
        c2 = 4030.0
        
        # Iterative solution for wet bulb
        wb = air_temp  # Initial guess
        for _ in range(10):  # Maximum 10 iterations
            es_wb = 6.112 * math.exp((17.67 * wb) / (wb + 243.5))
            es = 6.112 * math.exp((17.67 * air_temp) / (air_temp + 243.5))
            
            wb_new = (wb * c1 + air_temp * c2 * (es - es_wb) / (wb + 273.15)) / (c1 + c2 * (es - es_wb) / (wb + 273.15))
            
            if abs(wb_new - wb) < 0.01:
                break
            wb = wb_new
        
        return wb
    
    def _estimate_globe_temperature(self, air_temp: float, solar_rad: float, wind_speed: float) -> float:
        """
        Estimate globe temperature from air temperature, solar radiation, and wind speed.
        
        Args:
            air_temp: Air temperature (°C)
            solar_rad: Solar radiation (W/m²)
            wind_speed: Wind speed (m/s)
        
        Returns:
            Estimated globe temperature (°C)
        """
        # Convert to Kelvin
        T_air = air_temp + 273.15
        
        # Calculate heat transfer coefficients
        h_conv = 10.45 - wind_speed + 10 * math.sqrt(wind_speed)  # Convection coefficient
        h_rad = 4 * self.emissivity * self.stefan_boltzmann * T_air**3  # Radiation coefficient
        
        # Total heat transfer coefficient
        h_total = h_conv + h_rad
        
        # Calculate globe temperature
        # Simplified model assuming black globe
        T_globe = T_air + (solar_rad * self.emissivity) / h_total
        
        # Convert back to Celsius
        return T_globe - 273.15
    
    def _calculate_wbgt_from_components(self, wet_bulb: float, globe_temp: float) -> float:
        """
        Calculate WBGT from wet bulb and globe temperatures.
        
        Args:
            wet_bulb: Wet bulb temperature (°C)
            globe_temp: Globe temperature (°C)
        
        Returns:
            WBGT temperature (°C)
        """
        # Standard WBGT formula: WBGT = 0.7 * Twb + 0.3 * Tg
        wbgt = 0.7 * wet_bulb + 0.3 * globe_temp
        return round(wbgt, 1)
    
    def _assess_heat_stress(self, wbgt: float) -> Tuple[str, float, str]:
        """
        Assess heat stress level based on WBGT.
        
        Args:
            wbgt: WBGT temperature (°C)
        
        Returns:
            Tuple of (level, risk_score, color_code)
        """
        if wbgt < 25.0:
            level = 'low'
            risk_score = min(wbgt / 25.0 * 3, 3.0)
            color = self.thresholds['low']['color']
        elif wbgt < 28.0:
            level = 'moderate'
            risk_score = 3.0 + (wbgt - 25.0) / 3.0 * 2
            color = self.thresholds['moderate']['color']
        elif wbgt < 30.0:
            level = 'high'
            risk_score = 5.0 + (wbgt - 28.0) / 2.0 * 2
            color = self.thresholds['high']['color']
        elif wbgt < 32.0:
            level = 'very_high'
            risk_score = 7.0 + (wbgt - 30.0) / 2.0 * 2
            color = self.thresholds['very_high']['color']
        else:
            level = 'extreme'
            risk_score = min(9.0 + (wbgt - 32.0) / 5.0, 10.0)
            color = self.thresholds['extreme']['color']
        
        return level, round(risk_score, 1), color
    
    def calculate_from_simple_inputs(self, air_temp: float, rh: float, wind_speed: float = 1.0) -> WBGTResult:
        """
        Calculate WBGT from simplified inputs.
        
        Args:
            air_temp: Air temperature (°C)
            rh: Relative humidity (%)
            wind_speed: Wind speed (m/s)
        
        Returns:
            WBGTResult with calculated values
        """
        inputs = WBGTInputs(
            air_temperature=air_temp,
            relative_humidity=rh,
            wind_speed=wind_speed,
            solar_radiation=800  # Default moderate solar radiation
        )
        
        return self.calculate_wbgt(inputs)
    
    def get_work_recommendations(self, wbgt_result: WBGTResult) -> Dict[str, any]:
        """
        Get work recommendations based on WBGT result.
        
        Args:
            wbgt_result: WBGT calculation result
        
        Returns:
            Dictionary with recommendations
        """
        level = wbgt_result.heat_stress_level
        
        recommendations = {
            'work_rest_ratio': self._get_work_rest_ratio(level),
            'water_intake': self._get_water_intake_recommendations(level),
            'monitoring_frequency': self._get_monitoring_frequency(level),
            'protective_measures': self._get_protective_measures(level),
            'emergency_procedures': self._get_emergency_procedures(level)
        }
        
        return recommendations
    
    def _get_work_rest_ratio(self, level: str) -> str:
        """Get work:rest ratio recommendations."""
        ratios = {
            'low': 'Normal work, no special requirements',
            'moderate': '50% work, 50% rest',
            'high': '25% work, 75% rest',
            'very_high': '15% work, 85% rest',
            'extreme': 'Stop all outdoor work'
        }
        return ratios.get(level, 'Unknown')
    
    def _get_water_intake_recommendations(self, level: str) -> str:
        """Get water intake recommendations."""
        recommendations = {
            'low': 'Drink water when thirsty',
            'moderate': 'Drink 250ml every 20 minutes',
            'high': 'Drink 500ml every 20 minutes',
            'very_high': 'Drink 750ml every 15 minutes',
            'extreme': 'Drink 1L every 15 minutes, electrolyte drinks recommended'
        }
        return recommendations.get(level, 'Consult safety guidelines')
    
    def _get_monitoring_frequency(self, level: str) -> str:
        """Get monitoring frequency recommendations."""
        frequencies = {
            'low': 'Every 2 hours',
            'moderate': 'Every hour',
            'high': 'Every 30 minutes',
            'very_high': 'Every 15 minutes',
            'extreme': 'Continuous monitoring'
        }
        return frequencies.get(level, 'Regular monitoring')
    
    def _get_protective_measures(self, level: str) -> list:
        """Get protective measures recommendations."""
        measures = {
            'low': ['Wear light clothing', 'Stay hydrated'],
            'moderate': ['Light clothing', 'Frequent water breaks', 'Shade available'],
            'high': ['Light, loose clothing', 'Frequent water/electrolyte breaks', 'Mandatory shade periods'],
            'very_high': ['Minimal clothing', 'Frequent electrolyte drinks', 'Mandatory rest in shade', 'Cooling stations'],
            'extreme': ['Stop outdoor work', 'Move to air conditioning', 'Medical monitoring', 'Emergency response ready']
        }
        return measures.get(level, [])
    
    def _get_emergency_procedures(self, level: str) -> list:
        """Get emergency procedures recommendations."""
        procedures = {
            'low': ['Know heat illness symptoms'],
            'moderate': ['First aid available', 'Know emergency contacts'],
            'high': ['First aid station ready', 'Emergency contacts posted', 'Training on heat illness'],
            'very_high': ['Medical personnel on-site', 'Emergency response plan active', 'Cooling equipment ready'],
            'extreme': ['Emergency services on standby', 'Medical evacuation ready', 'Continuous medical monitoring']
        }
        return procedures.get(level, [])
    
    def calculate_acclimatization_factor(self, days_acclimatized: int) -> float:
        """
        Calculate acclimatization factor for heat stress assessment.
        
        Args:
            days_acclimatized: Number of days of acclimatization
        
        Returns:
            Acclimatization factor (0.7 to 1.0)
        """
        # Full acclimatization typically takes 7-14 days
        if days_acclimatized >= 14:
            return 1.0
        elif days_acclimatized >= 7:
            return 0.9
        elif days_acclimatized >= 3:
            return 0.8
        else:
            return 0.7
    
    def adjust_for_acclimatization(self, wbgt_result: WBGTResult, days_acclimatized: int) -> WBGTResult:
        """
        Adjust WBGT assessment for worker acclimatization.
        
        Args:
            wbgt_result: Original WBGT result
            days_acclimatized: Number of days of acclimatization
        
        Returns:
            Adjusted WBGT result
        """
        factor = self.calculate_acclimatization_factor(days_acclimatized)
        
        # Adjust the effective WBGT for acclimatized workers
        adjusted_wbgt = wbgt_result.wbgt - (1.0 - factor) * 5.0  # Reduce by up to 5°C
        
        # Reassess heat stress with adjusted WBGT
        stress_level, risk_score, color = self._assess_heat_stress(adjusted_wbgt)
        
        # Create new result with adjustments
        adjusted_result = WBGTResult(
            wbgt=adjusted_wbgt,
            wet_bulb=wbgt_result.wet_bulb,
            globe_temperature=wbgt_result.globe_temperature,
            air_temperature=wbgt_result.air_temperature,
            relative_humidity=wbgt_result.relative_humidity,
            wind_speed=wbgt_result.wind_speed,
            solar_radiation=wbgt_result.solar_radiation,
            heat_stress_level=stress_level,
            risk_score=risk_score,
            color_code=color
        )
        
        return adjusted_result
