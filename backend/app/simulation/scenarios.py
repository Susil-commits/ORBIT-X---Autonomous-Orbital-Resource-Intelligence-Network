"""Realistic Constellation Scenarios & Mission Request Generators."""

from typing import List
from app.core.schemas import MissionRequest, GeodeticLocation, MissionStatus


def get_default_missions(sim_time_s: float = 0.0) -> List[MissionRequest]:
    """Generates initial dynamic mission requests across Earth."""
    return [
        MissionRequest(
            id="MIS-AMAZON-01",
            name="Amazon Deforestation & Thermal Imaging",
            target_location=GeodeticLocation(lat=-3.4653, lon=-62.2159, alt=0.0),
            priority=4,
            reward=180.0,
            deadline_s=sim_time_s + 1800.0,
            duration_s=30.0,
            data_size_gb=14.0,
            energy_cost_wh=18.0,
            status=MissionStatus.PENDING,
            created_at_s=sim_time_s,
        ),
        MissionRequest(
            id="MIS-TOKYO-02",
            name="Tokyo Bay Maritime Traffic SAR",
            target_location=GeodeticLocation(lat=35.6190, lon=139.7800, alt=0.0),
            priority=3,
            reward=120.0,
            deadline_s=sim_time_s + 2400.0,
            duration_s=25.0,
            data_size_gb=10.0,
            energy_cost_wh=14.0,
            status=MissionStatus.PENDING,
            created_at_s=sim_time_s,
        ),
        MissionRequest(
            id="MIS-ARCTIC-03",
            name="Greenland Ice Sheet Albedo Survey",
            target_location=GeodeticLocation(lat=72.0000, lon=-40.0000, alt=2.0),
            priority=2,
            reward=90.0,
            deadline_s=sim_time_s + 3600.0,
            duration_s=40.0,
            data_size_gb=18.0,
            energy_cost_wh=22.0,
            status=MissionStatus.PENDING,
            created_at_s=sim_time_s,
        ),
        MissionRequest(
            id="MIS-CANAVERAL-04",
            name="Cape Canaveral Launch Range Clear Confirmation",
            target_location=GeodeticLocation(lat=28.3922, lon=-80.6077, alt=0.0),
            priority=5,
            reward=250.0,
            deadline_s=sim_time_s + 1200.0,
            duration_s=20.0,
            data_size_gb=8.0,
            energy_cost_wh=12.0,
            status=MissionStatus.PENDING,
            created_at_s=sim_time_s,
        ),
        MissionRequest(
            id="MIS-MEDITERRANEAN-05",
            name="Mediterranean Emergency Search & Rescue Optical Scan",
            target_location=GeodeticLocation(lat=34.5000, lon=18.0000, alt=0.0),
            priority=5,
            reward=260.0,
            deadline_s=sim_time_s + 1500.0,
            duration_s=30.0,
            data_size_gb=15.0,
            energy_cost_wh=20.0,
            status=MissionStatus.PENDING,
            created_at_s=sim_time_s,
        ),
        MissionRequest(
            id="MIS-SYDNEY-06",
            name="Great Barrier Reef Coral Bleaching Multi-Spectral",
            target_location=GeodeticLocation(lat=-18.2871, lon=147.6992, alt=0.0),
            priority=3,
            reward=130.0,
            deadline_s=sim_time_s + 3000.0,
            duration_s=35.0,
            data_size_gb=16.0,
            energy_cost_wh=19.0,
            status=MissionStatus.PENDING,
            created_at_s=sim_time_s,
        ),
        MissionRequest(
            id="MIS-DUBAI-07",
            name="Arabian Gulf Oil Spill Hyperspectral Detection",
            target_location=GeodeticLocation(lat=25.276987, lon=55.296249, alt=0.0),
            priority=4,
            reward=190.0,
            deadline_s=sim_time_s + 2100.0,
            duration_s=25.0,
            data_size_gb=12.0,
            energy_cost_wh=16.0,
            status=MissionStatus.PENDING,
            created_at_s=sim_time_s,
        ),
        MissionRequest(
            id="MIS-HIMALAYA-08",
            name="Himalayan Glacial Lake Outburst Risk Mapping",
            target_location=GeodeticLocation(lat=27.9881, lon=86.9250, alt=5.0),
            priority=4,
            reward=200.0,
            deadline_s=sim_time_s + 2700.0,
            duration_s=30.0,
            data_size_gb=15.0,
            energy_cost_wh=18.0,
            status=MissionStatus.PENDING,
            created_at_s=sim_time_s,
        ),
    ]


def generate_random_mission(sim_time_s: float, mission_num: int) -> MissionRequest:
    """Generates a random dynamic ground observation target."""
    import random
    import numpy as np
    
    # Random realistic global location
    lat = float(np.random.uniform(-65.0, 65.0))
    lon = float(np.random.uniform(-180.0, 180.0))
    prio = int(np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.2, 0.4, 0.2, 0.1]))
    dur = float(np.random.choice([20.0, 25.0, 30.0, 35.0, 45.0]))
    deadline_s = sim_time_s + float(np.random.uniform(900.0, 3600.0))
    reward = prio * 50.0 + np.random.uniform(10.0, 40.0)
    data_size = dur * 0.4
    energy_wh = dur * 0.6
    
    names = [
        "Wildfire Thermal Hotspot Scan",
        "Agricultural Soil Moisture InSAR",
        "Volcanic Ash Plume Tracking",
        "Illegal Fishing Vessel Radar",
        "Urban Heat Island Radiometry",
        "Cyclone Eye Pressure Radiometry",
        "Permafrost Thaw Subsidence SAR",
    ]
    name = f"{random.choice(names)} #{mission_num:02d}"
    
    return MissionRequest(
        id=f"MIS-DYN-{mission_num:03d}",
        name=name,
        target_location=GeodeticLocation(lat=round(lat, 4), lon=round(lon, 4), alt=0.0),
        priority=prio,
        reward=round(reward, 1),
        deadline_s=round(deadline_s, 1),
        duration_s=dur,
        data_size_gb=round(data_size, 1),
        energy_cost_wh=round(energy_wh, 1),
        status=MissionStatus.PENDING,
        created_at_s=sim_time_s,
    )
