"""
Heat Stress Assessment Module

This module provides heat stress assessment following OSHA standards
and international guidelines for occupational safety.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class HeatStressResult:
    """Result of heat stress assessment."""
    level: str  # Heat stress level
    color: str  # Color code for warnings
    risk_score: float  # Risk score (0-10)
    recommendations: List[str]  # Safety recommendations
    work_restrictions: Dict[str, str]  # Work restrictions
    country_specific: Optional[Dict] = None  # Country-specific guidelines


class HeatStressAssessor:
    """
    Assessor for heat stress conditions.
    
    This class implements heat stress assessment following OSHA,
    international standards, and country-specific regulations.
    """
    
    def __init__(self):
        """Initialize the heat stress assessor."""
        # OSHA-based heat stress thresholds
        self.osha_thresholds = {
            'low': {'max_wbgt': 25.0, 'color': '#00FF00'},
            'moderate': {'max_wbgt': 27.9, 'color': '#FFFF00'},
            'high': {'max_wbgt': 30.0, 'color': '#FFA500'},
            'very_high': {'max_wbgt': 32.0, 'color': '#FF0000'},
            'extreme': {'min_wbgt': 32.0, 'color': '#8B0000'}
        }
        
        # Country-specific adaptations
        self.country_adaptations = {
            'SA': {
                'summer_period': ['June', 'July', 'August', 'September'],
                'peak_hours': ['12:00', '15:00'],
                'mandatory_break_interval': 30,  # minutes
                'extreme_threshold': 32.0
            },
            'AE': {
                'high_risk_threshold': 28.0,
                'work_stoppage_threshold': 32.0,
                'monitoring_interval': 15  # minutes
            },
            'QA': {
                'summer_period': ['June', 'July', 'August', 'September'],
                'peak_hours': ['11:00', '16:00'],
                'extreme_threshold': 31.5
            },
            'KW': {
                'high_risk_threshold': 28.5,
                'work_stoppage_threshold': 32.5,
                'monitoring_interval': 20
            },
            'BH': {
                'high_risk_threshold': 28.0,
                'work_stoppage_threshold': 32.0,
                'monitoring_interval': 15
            }
        }
        
        # Worker type adjustments
        self.worker_type_factors = {
            'outdoor': 1.0,  # Full exposure
            'indoor_non_ac': 0.9,  # Indoor without AC
            'indoor_ac': 0.7,  # Indoor with AC
            'light_duty': 0.85,  # Light physical work
            'moderate_duty': 1.0,  # Moderate physical work
            'heavy_duty': 1.15  # Heavy physical work
        }
    
    def assess(self, wbgt: float, location: str = 'mecca', worker_type: str = 'outdoor') -> HeatStressResult:
        """
        Assess heat stress level based on WBGT.
        
        Args:
            wbgt: WBGT temperature (°C)
            location: Location name (for country-specific rules)
            worker_type: Type of worker/work
        
        Returns:
            HeatStressResult with assessment details
        """
        # Get country code
        country = self._get_country_code(location)
        
        # Apply worker type adjustment
        adjusted_wbgt = wbgt * self.worker_type_factors.get(worker_type, 1.0)
        
        # Determine heat stress level
        level, color, risk_score = self._determine_level(adjusted_wbgt)
        
        # Get recommendations
        recommendations = self._get_recommendations(level)
        
        # Get work restrictions
        work_restrictions = self._get_work_restrictions(level, country)
        
        # Get country-specific guidelines
        country_specific = self._get_country_specific_guidelines(country, level)
        
        return HeatStressResult(
            level=level,
            color=color,
            risk_score=risk_score,
            recommendations=recommendations,
            work_restrictions=work_restrictions,
            country_specific=country_specific
        )
    
    def _get_country_code(self, location: str) -> str:
        """Get country code from location name."""
        location_countries = {
            'mecca': 'SA', 'medina': 'SA', 'riyadh': 'SA', 'jeddah': 'SA',
            'dubai': 'AE', 'abu_dhabi': 'AE',
            'doha': 'QA',
            'kuwait_city': 'KW',
            'manama': 'BH'
        }
        return location_countries.get(location.lower(), 'SA')
    
    def _determine_level(self, wbgt: float) -> tuple:
        """Determine heat stress level from WBGT."""
        if wbgt < 25.0:
            return 'low', self.osha_thresholds['low']['color'], min(wbgt / 25.0 * 3, 3.0)
        elif wbgt < 28.0:
            return 'moderate', self.osha_thresholds['moderate']['color'], 3.0 + (wbgt - 25.0) / 3.0 * 2
        elif wbgt < 30.0:
            return 'high', self.osha_thresholds['high']['color'], 5.0 + (wbgt - 28.0) / 2.0 * 2
        elif wbgt < 32.0:
            return 'very_high', self.osha_thresholds['very_high']['color'], 7.0 + (wbgt - 30.0) / 2.0 * 2
        else:
            return 'extreme', self.osha_thresholds['extreme']['color'], min(9.0 + (wbgt - 32.0) / 5.0, 10.0)
    
    def _get_recommendations(self, level: str) -> List[str]:
        """Get safety recommendations for heat stress level."""
        recommendations_map = {
            'low': [
                'Normal work conditions',
                'Stay hydrated',
                'Wear appropriate clothing'
            ],
            'moderate': [
                'Provide water every 20 minutes',
                'Schedule regular rest breaks',
                'Monitor workers for heat stress signs',
                'Educate on heat illness prevention'
            ],
            'high': [
                'Increase water intake to 500ml per 20 minutes',
                'Implement 25% work, 75% rest cycle',
                'Provide shaded rest areas',
                'Monitor worker health closely',
                'Consider adjusting work hours'
            ],
            'very_high': [
                'Implement 15% work, 85% rest cycle',
                'Provide electrolyte drinks',
                'Mandatory cooling breaks',
                'Continuous health monitoring',
                'Reschedule non-essential work'
            ],
            'extreme': [
                'Stop all outdoor work',
                'Move to air-conditioned areas',
                'Provide frequent water breaks',
                'Monitor for heat illness',
                'Activate emergency procedures'
            ]
        }
        return recommendations_map.get(level, [])
    
    def _get_work_restrictions(self, level: str, country: str) -> Dict[str, str]:
        """Get work restrictions based on level and country."""
        restrictions = {
            'outdoor_work': self._get_outdoor_work_restriction(level),
            'indoor_work': self._get_indoor_work_restriction(level),
            'emergency_procedures': self._get_emergency_status(level)
        }
        
        # Apply country-specific overrides
        if country in self.country_adaptations:
            adaptations = self.country_adaptations[country]
            if level == 'extreme':
                restrictions['outdoor_work'] = 'prohibited'
        
        return restrictions
    
    def _get_outdoor_work_restriction(self, level: str) -> str:
        """Get outdoor work restriction."""
        restrictions = {
            'low': 'normal',
            'moderate': 'with_rest_breaks',
            'high': 'limited',
            'very_high': 'severely_limited',
            'extreme': 'prohibited'
        }
        return restrictions.get(level, 'normal')
    
    def _get_indoor_work_restriction(self, level: str) -> str:
        """Get indoor work restriction."""
        restrictions = {
            'low': 'normal',
            'moderate': 'normal',
            'high': 'with_rest_breaks',
            'very_high': 'with_rest_breaks',
            'extreme': 'with_rest_breaks'
        }
        return restrictions.get(level, 'normal')
    
    def _get_emergency_status(self, level: str) -> str:
        """Get emergency procedure status."""
        status = {
            'low': 'standby',
            'moderate': 'standby',
            'high': 'ready',
            'very_high': 'active',
            'extreme': 'active'
        }
        return status.get(level, 'standby')
    
    def _get_country_specific_guidelines(self, country: str, level: str) -> Optional[Dict]:
        """Get country-specific heat stress guidelines."""
        if country not in self.country_adaptations:
            return None
        
        adaptations = self.country_adaptations[country]
        
        guidelines = {
            'country': country,
            'summer_period': adaptations.get('summer_period', []),
            'peak_hours': adaptations.get('peak_hours', []),
            'mandatory_break_interval': adaptations.get('mandatory_break_interval', 0),
            'monitoring_interval': adaptations.get('monitoring_interval', 30),
            'extreme_threshold': adaptations.get('extreme_threshold', 32.0),
            'high_risk_threshold': adaptations.get('high_risk_threshold', 28.0),
            'work_stoppage_threshold': adaptations.get('work_stoppage_threshold', 32.0)
        }
        
        return guidelines
    
    def calculate_heat_illness_risk(self, wbgt: float, worker_age: int, 
                                     acclimatized: bool, hydration_level: str) -> Dict:
        """
        Calculate individual heat illness risk factors.
        
        Args:
            wbgt: WBGT temperature
            worker_age: Worker age in years
            acclimatized: Whether worker is acclimatized
            hydration_level: Hydration status (good, moderate, poor)
        
        Returns:
            Dictionary with risk factors
        """
        base_risk = wbgt / 35.0  # Normalize to 0-1 range
        
        # Age factor (higher risk for older workers)
        age_factor = 1.0
        if worker_age > 50:
            age_factor = 1.2
        elif worker_age > 40:
            age_factor = 1.1
        
        # Acclimatization factor
        acclimatization_factor = 1.0 if acclimatized else 1.3
        
        # Hydration factor
        hydration_factors = {
            'good': 1.0,
            'moderate': 1.2,
            'poor': 1.5
        }
        hydration_factor = hydration_factors.get(hydration_level, 1.2)
        
        # Calculate overall risk
        overall_risk = base_risk * age_factor * acclimatization_factor * hydration_factor
        overall_risk = min(overall_risk, 1.0)  # Cap at 1.0
        
        return {
            'base_risk': round(base_risk, 2),
            'age_factor': round(age_factor, 2),
            'acclimatization_factor': round(acclimatization_factor, 2),
            'hydration_factor': round(hydration_factor, 2),
            'overall_risk': round(overall_risk, 2),
            'risk_category': self._categorize_risk(overall_risk)
        }
    
    def _categorize_risk(self, risk: float) -> str:
        """Categorize risk level."""
        if risk < 0.3:
            return 'low'
        elif risk < 0.5:
            return 'moderate'
        elif risk < 0.7:
            return 'high'
        else:
            return 'extreme'
