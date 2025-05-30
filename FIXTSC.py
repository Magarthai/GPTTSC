
import cityflow
import time

# Config path
config_path = "config.json"

# Start simulation engine
eng = cityflow.Engine(config_path, thread_num=1)

# Mapping ชื่อ phase กับ index
green_phase_map = {
    "NTST": 4,
    "NLSL": 6,
    "ETWT": 0,
    "ELWL": 2,
}

# ลำดับการเปิดไฟเขียว
phase_order = ["NTST", "NLSL", "ETWT", "ELWL"]
phase_index = 0
time_in_phase = 0
duration = 30  # แต่ละ phase 30 วินาที

for step in range(7200):
    eng.next_step()

    if time_in_phase == 0:
        current_phase = phase_order[phase_index]
        eng.set_tl_phase("intersection_1_1", green_phase_map[current_phase])
        print(f"[{step}s] Phase set to {current_phase} for {duration} seconds")

    time_in_phase += 1

    if time_in_phase >= duration:
        phase_index = (phase_index + 1) % len(phase_order)
        time_in_phase = 0
