# import ollama

# MODEL = "llava:7b"


# def generate_vision_report(before_path, after_path):

#     prompt = """
# You are an industrial motor inspection expert.

# You are given TWO images in this exact order:

# IMAGE 1 = BEFORE (new / cleaned / good condition motor)
# IMAGE 2 = AFTER (used / older / possibly rusted motor)

# IMPORTANT:
# Treat image 1 strictly as BEFORE state.
# Treat image 2 strictly as AFTER state.

# Compare condition changes from BEFORE → AFTER.

# Report:
# - rust increase or decrease
# - surface degradation or damage
# - which areas worsened
# - whether condition degraded or improved
# - risk level (LOW / MEDIUM / HIGH)
# - maintenance recommendation

# Do NOT reverse the order.
# Do NOT assume improvement unless visually justified.
# Keep report under 120 words.
# """

#     resp = ollama.chat(
#         model=MODEL,
#         messages=[
#             {
#                 "role": "user",
#                 "content": prompt,
#                 "images": [before_path, after_path]
#             }
#         ]
#     )

#     return resp["message"]["content"]


import ollama

MODEL = "llava:7b"

def generate_vision_report(before_path, after_path):

    prompt = """
You are an industrial motor inspection expert.

Images are provided in strict order:
Image 1 = BEFORE (new / clean motor)
Image 2 = AFTER (used / rusted motor)

Follow order strictly. Do not reverse.

Output ONLY short bullet points (max 6).
Each point must be one line.
Be concise and technical.

Include:
- rust change (increase/decrease)
- visible damage or degradation
- main changed area
- overall condition trend
- risk level (LOW/MEDIUM/HIGH)
- maintenance action
- state percentage increased of Rust
"""

    resp = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
                "images": [before_path, after_path]
            }
        ]
    )

    return resp["message"]["content"]
