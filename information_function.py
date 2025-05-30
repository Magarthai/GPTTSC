
import json

def get_phase_metadata(engine):
    lane_map = {
    "NTST": ["road_1_1_1_1", "road_1_2_3_1"],     # N ↔ S Through (lane 1 = กลาง)
    "NLSL": ["road_1_1_1_0", "road_1_2_3_0"],     # N ↔ S Left (lane 0 = เลนซ้าย)
    "ETWT": ["road_1_0_1_1", "road_2_1_2_1"],     # E ↔ W Through
    "ELWL": ["road_1_0_1_0", "road_2_1_2_0"]      # E ↔ W Left
}


    # ดึงจำนวนรถทั้งหมด
    total_vehicles = engine.get_vehicle_count()

    # ดึงจำนวนรถที่รอในแต่ละเลน (waiting = speed < 0.1 m/s)
    waiting_dict = engine.get_lane_waiting_vehicle_count()

    # พยายามดึง average travel time (ถ้า engine รองรับ)
    try:
        travel_time = engine.get_average_travel_time()
    except Exception:
        travel_time = None

    # สรุปจำนวนรถที่รอในแต่ละ Phase
    phase_summary = []
    for phase, lanes in lane_map.items():
        waiting_sum = sum([waiting_dict.get(lane, 0) for lane in lanes])
        phase_summary.append({
            "lane": phase,
            "sum_waiting_veh": waiting_sum
        })

    # รวม metadata ทั้งหมด
    metadata = {
        "sum_of_veh": total_vehicles,
        "sum_waiting_veh": sum(waiting_dict.values()),
        "average_travel_time": travel_time,
        "phase_lane_waiting_summary": phase_summary
    }

    return metadata

def generate_simplified_prompt(metadata):
    """
    สร้าง prompt ที่เรียบง่ายจาก metadata ของการจราจร เพื่อนำไปใช้กับ LLM
    รูปแบบ output เป็น JSON string ที่สามารถใช้ใน Chat API ได้เลย
    """
    prompt = {
        "sum_of_veh": metadata.get("sum_of_veh", 0),
        "sum_waiting_veh": metadata.get("sum_waiting_veh", 0),
        "average_travel_time": round(metadata.get("average_travel_time", 0), 3),
        "phase_lane_waiting_summary": metadata.get("phase_lane_waiting_summary", [])
    }

    return json.dumps(prompt)

