# app/services/star_catalog_service.py
"""
High-Precision Star Catalog Service

This service loads and manages data from the Yale Bright Star Catalog (BSC5),
providing accurate astronomical data and astrological lore for major fixed stars.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import re

import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, ICRS
import astropy.units as u

from app.core.config import settings
from app.services.content_fetch_service import get_star_lore_content

logger = logging.getLogger(__name__)

class Star:
    """Represents a single star with its astronomical and catalog data."""
    def __init__(self, raw_data_str: str):
        # This parser is specific to the bsc5.dat format
        self.hr_number = int(raw_data_str[0:4].strip())
        self.name = raw_data_str[4:14].strip()
        self.spectral_type = raw_data_str[127:147].strip()
        self.magnitude = float(raw_data_str[102:107].strip()) if raw_data_str[102:107].strip() else 99.0
        
        # Positions (RA/Dec) for J2000.0
        ra_h = float(raw_data_str[75:77].strip())
        ra_m = float(raw_data_str[77:79].strip())
        ra_s = float(raw_data_str[79:83].strip())
        self.ra = (ra_h + ra_m / 60.0 + ra_s / 3600.0) * 15.0 # Convert from hours to degrees

        dec_sign = -1 if raw_data_str[83:84] == '-' else 1
        dec_d = float(raw_data_str[84:86].strip())
        dec_m = float(raw_data_str[86:88].strip())
        dec_s = float(raw_data_str[88:90].strip())
        self.dec = dec_sign * (dec_d + dec_m / 60.0 + dec_s / 3600.0)
        
        # Proper Motion
        self.pm_ra = float(raw_data_str[148:154].strip()) * 15000 if raw_data_str[148:154].strip() else 0.0 # mas/yr
        self.pm_dec = float(raw_data_str[154:160].strip()) * 1000 if raw_data_str[154:160].strip() else 0.0 # mas/yr

    def get_astropy_coord(self, epoch: Time = None) -> SkyCoord:
        """Returns the Astropy SkyCoord object for this star at given epoch."""
        # Create initial coordinates at J2000.0
        coord = SkyCoord(
            ra=self.ra * u.degree,
            dec=self.dec * u.degree,
            pm_ra_cosdec=self.pm_ra * u.mas/u.yr,
            pm_dec=self.pm_dec * u.mas/u.yr,
            frame='icrs'
        )
        
        # Apply proper motion if epoch provided
        if epoch:
            return coord.apply_space_motion(new_obstime=epoch)
        return coord

    def calculate_precessed_position(self, target_epoch: float) -> Dict[str, float]:
        """Calculate precessed position for a specific epoch."""
        from astropy.coordinates import FK5
        coord = self.get_astropy_coord()
        
        # Convert to FK5 (needed for precession calculations)
        fk5_coord = coord.transform_to(FK5(equinox=f'J{target_epoch}'))
        
        return {
            'ra_degrees': fk5_coord.ra.degree,
            'dec_degrees': fk5_coord.dec.degree,
            'epoch': target_epoch
        }

    def calculate_topocentric_position(self, date: datetime, lat: float, lon: float, 
                                     altitude: float = 0) -> Dict[str, float]:
        """Calculate topocentric position (as viewed from a specific location on Earth)."""
        from astropy.coordinates import EarthLocation, AltAz
        from astropy.time import Time
        
        # Create observer location
        location = EarthLocation(
            lat=lat * u.deg,
            lon=lon * u.deg,
            height=altitude * u.m
        )
        
        # Get star coordinates at the current epoch
        time = Time(date)
        star_coord = self.get_astropy_coord(epoch=time)
        
        # Transform to horizontal coordinates
        altaz_frame = AltAz(obstime=time, location=location)
        altaz = star_coord.transform_to(altaz_frame)
        
        # Calculate refraction correction
        # This is a simplified atmospheric refraction formula
        R = 1.02 / np.tan(np.radians(altaz.alt.degree + 10.3/(altaz.alt.degree + 5.11)))
        if altaz.alt.degree >= 15:
            refraction = R / 60  # Convert to degrees
        else:
            # More precise formula for low altitudes
            refraction = (0.1594 + 0.0196 * altaz.alt.degree + 
                        0.00002 * altaz.alt.degree**2) / (1 + 0.505 * altaz.alt.degree + 
                        0.0845 * altaz.alt.degree**2)
        
        return {
            'altitude_degrees': altaz.alt.degree + refraction,
            'azimuth_degrees': altaz.az.degree,
            'apparent_ra_degrees': star_coord.ra.degree,
            'apparent_dec_degrees': star_coord.dec.degree,
            'refraction_correction_degrees': refraction
        }

class StarCatalogService:
    """A singleton service that loads the star catalog once and provides lookup methods."""
    _instance = None

    def __init__(self):
        logger.info("Initializing StarCatalogService singleton...")
        self.stars_by_name: Dict[str, Star] = {}
        self.lore = get_star_lore_content().get("lore", {})
        
        catalog_path = os.path.join(settings.SKYFIELD_DATA_PATH, 'bsc5.dat') # Assumes it's in your data path
        self._load_catalog(catalog_path)
        
        if not self.stars_by_name:
            raise RuntimeError("Star catalog is empty. Check that bsc5.dat exists and is readable.")
        
        logger.info(f"StarCatalogService initialized successfully with {len(self.stars_by_name)} named stars.")

    def _load_catalog(self, path: str):
        """Loads and parses the Yale Bright Star Catalog (bsc5.dat)."""
        if not os.path.exists(path):
            logger.error(f"Star catalog file not found at: {path}")
            return
        
        with open(path, 'r') as f:
            for line in f:
                # The star name is in bytes 5-14. If it's not blank, it's a named star.
                if line[4:14].strip():
                    try:
                        star = Star(line)
                        self.stars_by_name[star.name.lower()] = star
                    except (ValueError, IndexError):
                        # Skip lines that don't parse correctly
                        continue

    def get_star_details(self, star_name: str, epoch_str: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Gets full details for a star, including its position at a specific epoch.
        """
        star = self.stars_by_name.get(star_name.lower())
        if not star:
            return None

        # Determine the target epoch
        target_epoch = Time(epoch_str) if epoch_str else Time(datetime.utcnow())
        
        # Get current position corrected for proper motion
        star_coord = star.get_astropy_coord()
        current_pos = star_coord.apply_space_motion(new_obstime=target_epoch)
        
        lore = self.lore.get(star.name, {})

        return {
            "name": star.name,
            "hr_number": star.hr_number,
            "magnitude": star.magnitude,
            "spectral_type": star.spectral_type,
            "current_position_icrs": {
                "epoch": target_epoch.iso,
                "ra_degrees": round(current_pos.ra.deg, 6),
                "dec_degrees": round(current_pos.dec.deg, 6)
            },
            "catalog_position_j2000": {
                "ra_degrees": round(star.ra, 6),
                "dec_degrees": round(star.dec, 6)
            },
            "lore": {
                "constellation": lore.get("constellation"),
                "mythology": lore.get("mythology"),
                "astrological_influence": lore.get("astrological_influence")
            }
        }

    def find_stars(self, max_magnitude: float = 2.0) -> List[Dict[str, Any]]:
        """Finds all named stars brighter than a given magnitude."""
        bright_stars = [
            star for star in self.stars_by_name.values()
            if star.magnitude <= max_magnitude
        ]
        # Sort by brightness (lower magnitude is brighter)
        bright_stars.sort(key=lambda s: s.magnitude)
        
        # Return a list of simplified data
        return [{
            "name": star.name,
            "hr_number": star.hr_number,
            "magnitude": star.magnitude,
            "spectral_type": star.spectral_type
        } for star in bright_stars]

    def find_visible_stars(self, date: datetime, lat: float, lon: float, 
                          min_altitude: float = 0, max_magnitude: float = 6.0) -> List[Dict]:
        """Find all stars visible from a location at given time."""
        visible_stars = []
        
        for star in self.stars_by_name.values():
            if star.magnitude > max_magnitude:
                continue
                
            pos = star.calculate_topocentric_position(date, lat, lon)
            if pos['altitude_degrees'] > min_altitude:
                visible_stars.append({
                    'hr_number': star.hr_number,
                    'name': star.name,
                    'magnitude': star.magnitude,
                    'altitude': pos['altitude_degrees'],
                    'azimuth': pos['azimuth_degrees'],
                    'spectral_type': star.spectral_type
                })
        
        return sorted(visible_stars, key=lambda x: x['magnitude'])

    def calculate_star_phenomena(self, hr_number: int, date: datetime, 
                               lat: float, lon: float) -> Dict[str, Any]:
        """Calculate astronomical phenomena for a star."""
        from astropy.coordinates import get_sun
        star = self.stars.get(hr_number)
        if not star:
            raise ValueError(f"Star HR {hr_number} not found")
            
        time = Time(date)
        sun = get_sun(time)
        star_coord = star.get_astropy_coord(epoch=time)
        
        # Calculate angular separation from sun
        separation = sun.separation(star_coord)
        
        # Determine visibility conditions
        is_visible = False
        visibility_condition = "below_horizon"
        
        pos = star.calculate_topocentric_position(date, lat, lon)
        if pos['altitude_degrees'] > 0:
            if separation.degree > 15:  # More than 15 degrees from sun
                is_visible = True
                if separation.degree > 90:
                    visibility_condition = "dark_sky"
                else:
                    visibility_condition = "twilight"
            else:
                visibility_condition = "too_close_to_sun"
        
        return {
            'star_info': {
                'hr_number': hr_number,
                'name': star.name,
                'magnitude': star.magnitude
            },
            'position': pos,
            'phenomena': {
                'solar_separation_degrees': separation.degree,
                'is_visible': is_visible,
                'visibility_condition': visibility_condition
            },
            'timestamp': date.isoformat()
        }

# --- Create a single, shared instance for the application's lifetime ---
try:
    star_catalog_service_instance = StarCatalogService()
except RuntimeError as e:
    logger.critical(f"Could not instantiate StarCatalogService: {e}")
    star_catalog_service_instance = None