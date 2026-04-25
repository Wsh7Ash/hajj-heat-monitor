"""
UV Index Calculator Module

This module provides UV index calculations and protection recommendations
following WHO guidelines for UV radiation safety.
"""

from typing import Dict, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class UVIndexResult:
    """Result of UV index calculation."""
    value: float  # UV index value
    level: str  # UV danger level
    color: str  # Color code for warnings
    protection_time: str  # Recommended protection time window
    recommendations: List[str]  # Safety recommendations
    spf_recommendation: str  # Recommended SPF level


class UVIndexCalculator:
    """
    Calculator for UV index and protection recommendations.
    
    This class implements UV index calculations following WHO
    guidelines and provides protection recommendations.
    """
    
    def __init__(self):
        """Initialize the UV index calculator."""
        # WHO UV index scale
        self.uv_scale = {
            'low': {'max': 2.9, 'color': '#00FF00', 'spf': '15+'},
            'moderate': {'max': 5.9, 'color': '#FFFF00', 'spf': '15+'},
            'high': {'max': 7.9, 'color': '#FFA500', 'spf': '30+'},
            'very_high': {'max': 10.9, 'color': '#FF0000', 'spf': '50+'},
            'extreme': {'min': 11.0, 'color': '#8B0000', 'spf': '50+'}
        }
        
        # Gulf region peak UV hours
        self.peak_uv_hours = {
            'SA': ('10:00', '16:00'),
            'AE': ('10:00', '16:00'),
            'QA': ('10:00', '16:00'),
            'KW': ('10:00', '15:00'),
            'BH': ('10:00', '15:00'),
            'JO': ('10:00', '15:00')
        }
    
    def calculate_uv_index(self, uv_value: float, cloud_cover: int = 0) -> UVIndexResult:
        """
        Calculate UV index with cloud cover adjustment.
        
        Args:
            uv_value: Raw UV index value from weather API
            cloud_cover: Cloud cover percentage (0-100)
        
        Returns:
            UVIndexResult with calculated values
        """
        # Adjust UV index based on cloud cover
        adjusted_uv = self._adjust_for_cloud_cover(uv_value, cloud_cover)
        
        # Determine UV level
        level, color, spf = self._determine_uv_level(adjusted_uv)
        
        # Get protection time window
        protection_time = self._get_protection_time(adjusted_uv)
        
        # Get recommendations
        recommendations = self._get_recommendations(level)
        
        return UVIndexResult(
            value=round(adjusted_uv, 1),
            level=level,
            color=color,
            protection_time=protection_time,
            recommendations=recommendations,
            spf_recommendation=spf
        )
    
    def _adjust_for_cloud_cover(self, uv_value: float, cloud_cover: int) -> float:
        """Adjust UV index based on cloud cover."""
        # Cloud cover reduces UV radiation
        # Approximate reduction: 10% cloud cover = 5% UV reduction
        cloud_factor = 1.0 - (cloud_cover / 100.0 * 0.5)
        return uv_value * cloud_factor
    
    def _determine_uv_level(self, uv: float) -> tuple:
        """Determine UV danger level from UV index."""
        if uv < 3.0:
            return 'low', self.uv_scale['low']['color'], self.uv_scale['low']['spf']
        elif uv < 6.0:
            return 'moderate', self.uv_scale['moderate']['color'], self.uv_scale['moderate']['spf']
        elif uv < 8.0:
            return 'high', self.uv_scale['high']['color'], self.uv_scale['high']['spf']
        elif uv < 11.0:
            return 'very_high', self.uv_scale['very_high']['color'], self.uv_scale['very_high']['spf']
        else:
            return 'extreme', self.uv_scale['extreme']['color'], self.uv_scale['extreme']['spf']
    
    def _get_protection_time(self, uv: float) -> str:
        """Get recommended protection time window."""
        if uv < 3.0:
            return 'No specific time restrictions'
        elif uv < 6.0:
            return '10:00-14:00'
        elif uv < 8.0:
            return '09:00-15:00'
        elif uv < 11.0:
            return '08:00-16:00'
        else:
            return '06:00-17:00'
    
    def _get_recommendations(self, level: str) -> List[str]:
        """Get UV protection recommendations."""
        recommendations_map = {
            'low': [
                'Wear sunglasses on bright days',
                'Use sunscreen if outside for extended periods'
            ],
            'moderate': [
                'Seek shade during midday hours',
                'Wear protective clothing',
                'Use SPF 15+ sunscreen',
                'Wear sunglasses'
            ],
            'high': [
                'Seek shade, especially between 10am-4pm',
                'Wear protective clothing and hat',
                'Use SPF 30+ sunscreen',
                'Wear UV-blocking sunglasses',
                'Reapply sunscreen every 2 hours'
            ],
            'very_high': [
                'Avoid sun exposure between 10am-4pm',
                'Wear full protective clothing',
                'Use SPF 50+ sunscreen',
                'Wear UV-blocking sunglasses',
                'Stay in shade whenever possible',
                'Reapply sunscreen frequently'
            ],
            'extreme': [
                'Avoid all sun exposure if possible',
                'Stay indoors during peak hours',
                'Wear maximum protection clothing',
                'Use SPF 50+ sunscreen with zinc oxide',
                'Wear wraparound UV-blocking sunglasses',
                'Seek shade at all times',
                'Reapply sunscreen every hour'
            ]
        }
        return recommendations_map.get(level, [])
    
    def calculate_uv_forecast(self, hourly_uv_values: List[float], 
                               hourly_cloud_cover: List[int]) -> List[Dict]:
        """
        Calculate UV index forecast for multiple hours.
        
        Args:
            hourly_uv_values: List of UV values per hour
            hourly_cloud_cover: List of cloud cover percentages per hour
        
        Returns:
            List of hourly UV index results
        """
        forecast = []
        for i, uv in enumerate(hourly_uv_values):
            cloud = hourly_cloud_cover[i] if i < len(hourly_cloud_cover) else 0
            uv_result = self.calculate_uv_index(uv, cloud)
            
            forecast.append({
                'hour': i,
                'uv_index': uv_result.value,
                'level': uv_result.level,
                'color': uv_result.color,
                'recommendations': uv_result.recommendations
            })
        
        return forecast
    
    def get_peak_uv_hours(self, country: str) -> tuple:
        """Get peak UV hours for a country."""
        return self.peak_uv_hours.get(country, ('10:00', '16:00'))
    
    def calculate_uv_risk_for_skin_type(self, uv_index: float, skin_type: int) -> Dict:
        """
        Calculate UV risk based on Fitzpatrick skin type.
        
        Args:
            uv_index: UV index value
            skin_type: Fitzpatrick skin type (1-6)
        
        Returns:
            Dictionary with skin-specific risk assessment
        """
        # Fitzpatrick skin type characteristics
        skin_burn_times = {
            1: {'min_burn_time': 10, 'min_tan_time': None},  # Very fair
            2: {'min_burn_time': 15, 'min_tan_time': None},  # Fair
            3: {'min_burn_time': 20, 'min_tan_time': 30},   # Medium
            4: {'min_burn_time': 30, 'min_tan_time': 20},   # Olive
            5: {'min_burn_time': 40, 'min_tan_time': 10},   # Brown
            6: {'min_burn_time': 60, 'min_tan_time': 5}     # Dark
        }
        
        skin_info = skin_burn_times.get(skin_type, skin_burn_times[3])
        
        # Calculate safe exposure time based on UV index
        uv_factor = uv_index / 5.0  # Normalize around moderate UV
        safe_exposure = skin_info['min_burn_time'] / uv_factor
        
        # Determine risk level
        if safe_exposure < 10:
            risk_level = 'extreme'
        elif safe_exposure < 20:
            risk_level = 'very_high'
        elif safe_exposure < 30:
            risk_level = 'high'
        elif safe_exposure < 45:
            risk_level = 'moderate'
        else:
            risk_level = 'low'
        
        return {
            'skin_type': skin_type,
            'min_burn_time': skin_info['min_burn_time'],
            'min_tan_time': skin_info['min_tan_time'],
            'safe_exposure_time': round(safe_exposure, 1),
            'risk_level': risk_level,
            'recommendation': self._get_skin_type_recommendation(risk_level)
        }
    
    def _get_skin_type_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on skin type risk."""
        recommendations = {
            'extreme': 'Avoid all sun exposure, maximum protection required',
            'very_high': 'Limit sun exposure to essential activities only',
            'high': 'Minimize sun exposure, use maximum protection',
            'moderate': 'Use sun protection during peak hours',
            'low': 'Standard sun protection recommended'
        }
        return recommendations.get(risk_level, 'Use sun protection')
