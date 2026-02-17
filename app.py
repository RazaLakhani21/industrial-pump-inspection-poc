from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

import shutil
import uuid
import os

from bedrock_report import generate_bedrock_report
# from llm_vision_report import generate_vision_report
# from llm_report import generate_llm_report
from image_diff import compare_images
from object_detect import detect_objects
from object_compare import compare_objects
from comparison_builder import build_comparison_json
# from summary_ai import generate_summary

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# ensure folders exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ================= HOME =================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "upload.html",
        {"request": request}
    )


# ================= ANALYZE =================

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    before: UploadFile = File(...),
    after: UploadFile = File(...)
):

    # ---------- save uploads ----------
    before_path = f"uploads/{uuid.uuid4()}.jpg"
    after_path = f"uploads/{uuid.uuid4()}.jpg"

    with open(before_path, "wb") as f:
        shutil.copyfileobj(before.file, f)

    with open(after_path, "wb") as f:
        shutil.copyfileobj(after.file, f)

    # ---------- run comparison ----------
    out_path = f"outputs/{uuid.uuid4()}.jpg"

    result = compare_images(before_path, after_path, out_path)

    # ---------- object detection layer ----------
    before_objs = detect_objects(before_path)
    after_objs = detect_objects(after_path)

    added, removed = compare_objects(before_objs, after_objs)

    # =====================================================
    # ✅ BUILD FINAL STRUCTURED COMPARISON JSON (PUT HERE)
    # =====================================================
    comparison_json = build_comparison_json(
        result,
        before_objs,
        after_objs,
        added,
        removed
    )

    # ---------- AI summary ----------
    # vision_summary = generate_vision_report(before_path, after_path)
    bedrock_report = generate_bedrock_report(comparison_json)

    # ---------- render UI ----------
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,

            # core metrics
            "metrics": result,

            # structured comparison (for AI / logs / export)
            "comparison_json": comparison_json,

            # objects
            "before_objs": before_objs,
            "after_objs": after_objs,
            "added": added,
            "removed": removed,

            # originals for slider
            "before_original": "/" + before_path,
            "after_original": "/" + after_path,

            # AI report
            # "vision_summary": vision_summary,
            "bedrock_report": bedrock_report,

            # images
            "output_image": "/" + out_path,
            "heatmap_image": "/" + result["heatmap_path"],
            "before_heatmap_image": "/" + result["before_heatmap_path"],

            # interactive zones
            "zone_boxes": result.get("zone_boxes", {}),
            "zone_severity": result.get("zone_severity", {}),
        }
    )