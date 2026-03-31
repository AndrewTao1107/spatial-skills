from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import functools
import uvicorn
import math
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

app = FastAPI(title="Resource Profiler Pro", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=10)

@functools.lru_cache(maxsize=500)
def fetch_era5_meteorology(lat: float, lon: float, start_year: int, end_year: int) -> Dict[str, Any]:
    url = f"https://archive-api.open-meteo.com/v1/archive"
    current_year = datetime.now().year
    
    end_date_str = f"{end_year}-12-31" 
    if end_year >= current_year:
        end_date_str = (datetime.now() - __import__('datetime').timedelta(days=7)).strftime("%Y-%m-%d")

    # Added wind_direction_100m for Wind Rose
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": f"{start_year}-01-01",
        "end_date": end_date_str,
        "hourly": "wind_speed_100m,wind_direction_100m,shortwave_radiation,cloud_cover",
        "timezone": "auto"
    }
    response = requests.get(url, params=params, timeout=25)
    response.raise_for_status()
    data = response.json()
    
    times = data['hourly']['time']
    wind_data = data['hourly']['wind_speed_100m']
    wind_dir = data['hourly']['wind_direction_100m']
    solar_data = data['hourly']['shortwave_radiation']
    cloud_data = data['hourly']['cloud_cover']
    
    wind_hourly_sum = [0]*24
    solar_hourly_sum = [0]*24
    counts_hourly = [0]*24
    
    wind_monthly_sum = {str(m).zfill(2): 0.0 for m in range(1, 13)}
    solar_monthly_sum = {str(m).zfill(2): 0.0 for m in range(1, 13)}
    counts_monthly = {str(m).zfill(2): 0 for m in range(1, 13)}

    global_wind_sum = 0.0
    global_solar_sum = 0.0
    global_cloud_sum = 0.0
    global_count = 0
    
    # 16-Compass bins for Wind Rose (N, NNE, NE...)
    wind_rose_bins = [0] * 16
    
    for i in range(len(times)):
        ws = wind_data[i]
        sr = solar_data[i]
        cc = cloud_data[i]
        wd = wind_dir[i]
        
        if ws is None or sr is None or cc is None or wd is None:
            continue
            
        t_str = times[i]
        hour = int(t_str[11:13]) 
        month_str = t_str[5:7] 
        
        # Diurnal
        wind_hourly_sum[hour] += ws
        solar_hourly_sum[hour] += sr
        counts_hourly[hour] += 1
        
        # Monthly
        wind_monthly_sum[month_str] += ws
        solar_monthly_sum[month_str] += sr
        counts_monthly[month_str] += 1
        
        # Wind Direction Binning (22.5 deg per bin)
        sector = int((wd + 11.25) / 22.5) % 16
        wind_rose_bins[sector] += 1
        
        # Global
        global_wind_sum += ws
        global_solar_sum += sr
        global_cloud_sum += cc
        global_count += 1
        
    avg_wind_speed = global_wind_sum / global_count if global_count > 0 else 0
    avg_cloud_cover = global_cloud_sum / global_count if global_count > 0 else 0
    avg_solar_w_m2 = global_solar_sum / global_count if global_count > 0 else 0
    avg_solar_rad = avg_solar_w_m2 * 24.0 / 1000.0
    
    wind_diurnal = [round(wind_hourly_sum[i]/counts_hourly[i], 2) if counts_hourly[i]>0 else 0 for i in range(24)]
    solar_diurnal = [round(solar_hourly_sum[i]/counts_hourly[i], 2) if counts_hourly[i]>0 else 0 for i in range(24)]
    
    # Normalize wind rose frequencies to percentage (0-100)
    wind_rose_pct = [round((count / global_count) * 100, 2) if global_count > 0 else 0 for count in wind_rose_bins]
    
    months_mapped = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    wind_monthly_dict = {}
    solar_monthly_dict = {}
    for i in range(1, 13):
        m_str = str(i).zfill(2)
        m_wind = wind_monthly_sum[m_str] / counts_monthly[m_str] if counts_monthly[m_str] > 0 else 0
        m_solar_w = solar_monthly_sum[m_str] / counts_monthly[m_str] if counts_monthly[m_str] > 0 else 0
        wind_monthly_dict[months_mapped[i-1]] = round(m_wind, 2)
        solar_monthly_dict[months_mapped[i-1]] = round(m_solar_w * 24.0 / 1000.0, 2)
        
    return {
        "global_wind_100m": avg_wind_speed,
        "global_solar_kwh": avg_solar_rad,
        "global_cloud_pct": avg_cloud_cover,
        "wind_monthly": wind_monthly_dict,
        "solar_monthly": solar_monthly_dict,
        "wind_diurnal": wind_diurnal,
        "solar_diurnal": solar_diurnal,
        "wind_rose": wind_rose_pct
    }

@functools.lru_cache(maxsize=500)
def fetch_terrain_profile(lat: float, lon: float) -> Dict[str, float]:
    """Fetch 5-point DEM cross to compute Elevation and Slope Proxy"""
    try:
        delta = 0.001 # ~111 meters
        lat_n, lat_s = lat + delta, lat - delta
        lon_e, lon_w = lon + delta, lon - delta
        
        # Send batched request: Center, North, South, East, West
        url = f"https://api.open-meteo.com/v1/elevation?latitude={lat},{lat_n},{lat_s},{lat},{lat}&longitude={lon},{lon},{lon},{lon_e},{lon_w}"
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        elevations = r.json().get('elevation', [0.0]*5)
        
        if len(elevations) < 5:
            return {"elevation": 0.0, "slope": 0.0}
            
        z_c, z_n, z_s, z_e, z_w = elevations
        
        # dZ/dY (North-South gradient): 2 * delta * 111320 meters
        dy = 2 * delta * 111320.0
        # dZ/dX (East-West gradient): 2 * delta * 111320 * cos(lat)
        dx = 2 * delta * 111320.0 * math.cos(lat * math.pi / 180.0)
        
        dz_dy = (z_n - z_s) / dy
        dz_dx = (z_e - z_w) / dx
        
        slope_deg = math.degrees(math.atan(math.sqrt(dz_dx**2 + dz_dy**2)))
        
        return {"elevation": float(z_c), "slope": round(float(slope_deg), 1)}
    except:
        return {"elevation": 0.0, "slope": 0.0}

@app.get("/api/profile")
def profile_resource(
    lat: float, 
    lon: float, 
    wind_mw: float = 50.0, 
    solar_mw: float = 20.0,
    start_year: int = 2023,
    end_year: int = 2025
):
    if end_year - start_year > 5:
        raise HTTPException(status_code=400, detail="Time window cannot exceed 5 years to guarantee computational limits.")
        
    try:
        grid_lat = round(lat, 3)
        grid_lon = round(lon, 3)
        
        # Parallel Execution
        future_era5 = executor.submit(fetch_era5_meteorology, grid_lat, grid_lon, start_year, end_year)
        future_terrain = executor.submit(fetch_terrain_profile, grid_lat, grid_lon)
        
        era5_data = future_era5.result()
        terrain_data = future_terrain.result()
        
        avg_wind_speed = era5_data["global_wind_100m"]
        avg_solar_rad = era5_data["global_solar_kwh"]
        avg_cloud_amt = era5_data["global_cloud_pct"]
        elevation = terrain_data["elevation"]
        slope_deg = terrain_data["slope"]

        # -------------------------------------------------------------
        air_density = 1.225 * math.exp(-0.0001184 * elevation)
        density_derating = air_density / 1.225
        
        wind_cf_base = min(max((avg_wind_speed - 3) / 10, 0), 0.5)
        wind_cf_corrected = wind_cf_base * density_derating
        wind_annual_mwh = wind_mw * 8760 * wind_cf_corrected
        
        base_pr = 0.82
        cloud_penalty = 0.04 if avg_cloud_amt > 55.0 else (0.02 if avg_cloud_amt > 40.0 else 0.0)
        solar_pr_corrected = base_pr - cloud_penalty
        
        solar_annual_mwh = solar_mw * avg_solar_rad * 365 * solar_pr_corrected
        # -------------------------------------------------------------
        
        return {
            "coordinate": {"lat": grid_lat, "lon": grid_lon},
            "metrics": {
                "avg_wind_speed_m_s": round(avg_wind_speed, 2),
                "avg_solar_rad_kwh_m2_day": round(avg_solar_rad, 2),
                "elevation_m": round(elevation, 1),
                "slope_deg": slope_deg,
                "air_density_kg_m3": round(air_density, 3),
                "cloud_amount_percent": round(avg_cloud_amt, 1),
                "solar_pr_used": round(solar_pr_corrected * 100, 1),
                "wind_density_pr_used": round(density_derating * 100, 1)
            },
            "yields": {
                "wind_annual_10k_kwh": round(wind_annual_mwh / 10, 2),
                "solar_annual_10k_kwh": round(solar_annual_mwh / 10, 2),
            },
            "charts": {
                "wind_monthly": era5_data["wind_monthly"],
                "solar_monthly": era5_data["solar_monthly"],
                "wind_hourly": era5_data["wind_diurnal"],
                "solar_hourly": era5_data["solar_diurnal"],
                "wind_rose": era5_data["wind_rose"]
            }
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"API Data fetch failure: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Data parsing logic error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
