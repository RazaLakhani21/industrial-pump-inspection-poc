def generate_summary(result, added, removed):

    cp = result["change_percent"]

    text = f"""
AI Before–After Inspection Report

Visual Change: {cp:.2f}%

Objects Added:
{added if added else "No meaningful object category change"}

Objects Removed:
{removed if removed else "None"}
"""

    if "zone_severity" in result:
        text += "\nZone Severity Scores:\n"
        for z, s in result["zone_severity"].items():
            text += f"- {z}: severity {s}/10\n"

    if "zone_parts" in result:
        text += "\nLikely Parts Affected:\n"
        for z, p in result["zone_parts"].items():
            text += f"- {p} ({z})\n"


    # ✅ -------- Added Zones --------

    zones = result.get("zones", [])

    if zones:
        text += "\nDetailed Change Locations:\n"
        for z in zones:
            text += f"- Change detected in {z} area\n"


    # ✅ -------- CONDITION TREND LOGIC GOES HERE --------

    rust_delta = result["rust_delta_pct"]
    bright_delta = result["after_brightness"] - result["before_brightness"]

    if rust_delta > 2:
        trend = "Likely degraded / rust increased"
    elif rust_delta < -2:
        trend = "Likely improved / rust reduced"
    else:
        trend = "Rust level roughly unchanged"


    text += f"\nCondition Trend: {trend}\n"

    # ✅ -------- Interpretation Section --------

    text += "\nInterpretation:\n"

    if removed:
        text += "- Some objects/features are no longer present\n"

    if added:
        text += "- New objects/features appeared\n"

    if cp > 20:
        text += "- Major scene modification detected\n"
    elif cp > 5:
        text += "- Moderate visual change detected\n"
    else:
        text += "- Minor visual change detected\n"
        text += f"""

        Rust Coverage:
        Before: {result['before_rust_pct']:.1f}%
        After: {result['after_rust_pct']:.1f}%
        Change: {result['rust_delta_pct']:+.1f}%
        """


    return text