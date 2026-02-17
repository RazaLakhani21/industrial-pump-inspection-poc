# import ollama

# MODEL = "llama3.2:3b"


# def generate_llm_report(metrics, added, removed):

#     prompt = """
# You are a senior industrial motor inspection expert and visual comparison analyst.

# Two images are provided in STRICT ORDER:
# Image 1 = BEFORE motor
# Image 2 = AFTER motor

# DO NOT assume they are the same motor.
# You must VERIFY identity first using visible evidence.

# Step 1 — Identity Check:
# Compare these visual features:
# - motor housing shape
# - cooling fin pattern and count
# - mounting base structure
# - shaft opening shape
# - paint color & texture
# - rust distribution pattern
# - size proportions
# - camera distance & angle clues

# Decide:
# SAME MOTOR or DIFFERENT MOTOR

# If DIFFERENT:
# Do NOT report condition change.
# Instead report that comparison is invalid and explain why.

# Step 2 — If SAME MOTOR:
# Report condition change and degradation trend.

# Output Format — STRICT:
# Return ONLY bullet points (max 7 lines).
# Each line must be short and technical.

# Required bullets:

# • identity: SAME or DIFFERENT motor (with confidence %)
# • key visual matching or mismatching features
# • rust change trend (increase/decrease/none)
# • main affected region
# • visible degradation or damage
# • risk level: LOW / MEDIUM / HIGH
# • recommended maintenance action

# Rules:
# - No paragraphs
# - No storytelling
# - No guessing without visual evidence
# - If uncertain, say LOW CONFIDENCE
# """


#     resp = ollama.generate(
#         model=MODEL,
#         prompt=prompt,
#         stream=False
#     )

#     return resp["response"]
