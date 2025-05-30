# Improved CityFlow Simulation Runner with Structured Logging + Road Data Utilization

import cityflow
import time
import json
import random
import pandas as pd
from collections import defaultdict
from information_function import (
    get_phase_metadata,
    generate_simplified_prompt
)
from openai import OpenAI
client = OpenAI(api_key="")

# Config paths
roadnet_path = "roadnet.json"
config_path = "config.json"

# Start simulation engine
eng = cityflow.Engine(config_path, thread_num=1)
start_time = time.time()

vehicle_log = {}

green_phase_map = {
    "ETWT": 0,
    "ELWL": 2,
    "NTST": 4,
    "NLSL": 6,
}

phase_index = 0
time_in_phase = 0
def get_new_prompt_result():
    return [
        {"enabled_green_phases": "ETWT", "duration": 30},
        {"enabled_green_phases": "NTST", "duration": 30}
    ]

prompt_result = ""
phase_index = 0
time_in_phase = 0
phase_history = []  # 🟡 เก็บ log ของไฟที่เคยเปิด
llm_time_thinking = 60

solution = get_new_prompt_result()

for step in range(7200):
    eng.next_step()

    if step % llm_time_thinking == 0:
        metadata = get_phase_metadata(eng)
        print(f"[{step}s] Metadata: {metadata}")

        # 🟡 รวม phase_history เข้าไปใน prompt
        prompt = {
            "metadata": metadata,
            "phase_history": phase_history[-5:]  # ส่งแค่ 5 อันล่าสุดก็พอ
        }
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a traffic control assistant. Your job is to schedule green light phases "
                        f"for the next {llm_time_thinking} seconds based on the current traffic metadata and recent history. "
                        f"You must choose one or more traffic light phases from: NTST, NLSL, ETWT, ELWL. "
                        f"Assign a duration (in seconds) to each phase so the total is exactly {llm_time_thinking} seconds. "
                        f"Return only a JSON array, like: "
                        f"[{{\"enabled_green_phases\": \"ETWT\", \"duration\": 60}}, {{\"enabled_green_phases\": \"NTST\", \"duration\": 60}}]. "
                        f"No explanations, no markdown."
                    )
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt)
                }
            ]
        )

        solution = json.loads(response.choices[0].message.content)
        print(f"[{step}s] New Solution: {solution}")

    if time_in_phase == 0:
        current_phase = solution[phase_index]
        green_name = current_phase["enabled_green_phases"]
        duration = current_phase["duration"]
        eng.set_tl_phase("intersection_1_1", green_phase_map[green_name])
        print(f"[{step}s] Phase set to {green_name} for {duration} seconds")

        # 🟡 บันทึก history
        phase_history.append({
            "step": step,
            "phase": green_name,
            "duration": duration
        })

    time_in_phase += 1

    if time_in_phase >= solution[phase_index]["duration"]:
        phase_index = (phase_index + 1) % len(solution)
        time_in_phase = 0

    
for vid, info in list(vehicle_log.items())[:5]:
    print(f"รถ {vid}: เข้า {info['enter']}, ออก {info['leave']}")