def build_comparison_json(result, before_objs, after_objs, added, removed):

    comparison = {
        "image_metrics": {
            "similarity": result.get("similarity"),
            "change_percent": result.get("change_percent"),
            "regions": result.get("regions"),
            "rust_delta_pct": result.get("rust_delta_pct"),
            "before_brightness": result.get("before_brightness"),
            "after_brightness": result.get("after_brightness"),
        },
        "zones": [],
        "objects": {
            "before": before_objs or [],
            "after": after_objs or [],
            "added": added or [],
            "removed": removed or []
        }
    }

    # Add zone details if available
    for zone, severity in result.get("zone_severity", {}).items():
        comparison["zones"].append({
            "zone": zone,
            "severity": severity,
            "part": result.get("zone_parts", {}).get(zone),
            "box": result.get("zone_boxes", {}).get(zone)
        })

    return comparison
