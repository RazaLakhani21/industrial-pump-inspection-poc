from ultralytics import YOLO

model = YOLO("yolov8n.pt")

DOMAIN_MAP = {
    "car": "machine_part",
    "truck": "machine_part",
    "bus": "machine_part",
    "bench": "machine_part",
    "chair": "machine_part"
}


def normalize_label(label):
    return DOMAIN_MAP.get(label, label)


def detect_objects(image_path):

    results = model(image_path)

    labels = []

    for r in results:
        for box in r.boxes:

            conf = float(box.conf[0])

            # ✅ confidence filter
            if conf < 0.6:
                continue

            cls_id = int(box.cls[0])
            name = model.names[cls_id]

            name = normalize_label(name)

            labels.append(name)

    return list(set(labels))
