import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from scipy import ndimage


# =========================================================
# HELPER — Brightness Score
# =========================================================
def image_brightness_score(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray.mean()


# =========================================================
# HELPER — Contrast & Sharpness Metrics
# =========================================================
def image_quality_metrics(img):
    """Compute contrast, sharpness, and texture entropy"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Contrast (standard deviation)
    contrast = gray.std()
    
    # Sharpness (Laplacian variance)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    sharpness = laplacian.var()
    
    # Texture entropy
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist = hist.flatten() / hist.sum()
    hist = hist[hist > 0]  # Remove zeros
    entropy = -np.sum(hist * np.log2(hist))
    
    return {
        'contrast': float(contrast),
        'sharpness': float(sharpness),
        'entropy': float(entropy)
    }


# =========================================================
# HELPER — Enhanced Rust/Corrosion Detection
# Multi-range detection with texture analysis
# =========================================================
def enhanced_rust_score(img):
    """
    Improved rust detection using:
    - Multiple HSV ranges (rust, orange, brown)
    - Texture analysis for corroded surfaces
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Multiple rust color ranges
    rust_ranges = [
        # Orange-brown rust
        (np.array([5, 50, 50]), np.array([25, 255, 255])),
        # Darker rust
        (np.array([0, 30, 30]), np.array([15, 150, 150])),
        # Reddish corrosion
        (np.array([0, 100, 50]), np.array([10, 255, 200])),
    ]
    
    combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
    
    for lower, upper in rust_ranges:
        mask = cv2.inRange(hsv, lower, upper)
        combined_mask = cv2.bitwise_or(combined_mask, mask)
    
    # Texture-based corrosion detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # High-frequency texture (rough surfaces)
    kernel = np.array([[-1, -1, -1],
                       [-1,  8, -1],
                       [-1, -1, -1]])
    texture = cv2.filter2D(gray, -1, kernel)
    texture_mask = cv2.threshold(texture, 50, 255, cv2.THRESH_BINARY)[1]
    
    # Combine color and texture
    corrosion_mask = cv2.bitwise_or(combined_mask, texture_mask)
    
    rust_pixels = np.sum(corrosion_mask > 0)
    total_pixels = corrosion_mask.size
    
    return {
        'rust_ratio': rust_pixels / total_pixels,
        'rust_mask': corrosion_mask
    }


# =========================================================
# HELPER — Crack/Damage Detection
# =========================================================
def detect_cracks_and_damage(img):
    """
    Detect linear features and surface damage:
    - Canny edge detection
    - Hough line detection for cracks
    - Morphological operations for damage patterns
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Enhanced edge detection
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # Detect lines (potential cracks)
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi/180,
        threshold=50,
        minLineLength=30,
        maxLineGap=10
    )
    
    crack_count = 0
    if lines is not None:
        crack_count = len(lines)
    
    # Morphological damage detection
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    
    # Detect pits and holes (dark spots)
    _, dark_spots = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    dark_spots = cv2.morphologyEx(dark_spots, cv2.MORPH_OPEN, kernel, iterations=2)
    
    damage_pixels = np.sum(dark_spots > 0)
    total_pixels = dark_spots.size
    
    return {
        'crack_count': crack_count,
        'damage_ratio': damage_pixels / total_pixels,
        'edge_map': edges
    }


# =========================================================
# HELPER — Image Alignment (Feature-based)
# =========================================================
def align_images(img1, img2, max_features=500):
    """
    Align images using ORB feature matching
    Corrects for slight camera movements or angle differences
    """
    # Convert to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Detect ORB features
    orb = cv2.ORB_create(max_features)
    kp1, desc1 = orb.detectAndCompute(gray1, None)
    kp2, desc2 = orb.detectAndCompute(gray2, None)
    
    if desc1 is None or desc2 is None:
        return img2, False
    
    # Match features
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    matches = matcher.knnMatch(desc1, desc2, k=2)
    
    # Apply Lowe's ratio test
    good_matches = []
    for m_n in matches:
        if len(m_n) == 2:
            m, n = m_n
            if m.distance < 0.75 * n.distance:
                good_matches.append(m)
    
    # Need at least 10 good matches
    if len(good_matches) < 10:
        return img2, False
    
    # Extract matched keypoints
    pts1 = np.float32([kp1[m.queryIdx].pt for m in good_matches])
    pts2 = np.float32([kp2[m.trainIdx].pt for m in good_matches])
    
    # Find homography
    H, mask = cv2.findHomography(pts2, pts1, cv2.RANSAC, 5.0)
    
    if H is None:
        return img2, False
    
    # Warp image
    h, w = img1.shape[:2]
    aligned = cv2.warpPerspective(img2, H, (w, h))
    
    return aligned, True


# =========================================================
# HELPER — Multi-Scale Analysis
# =========================================================
def multiscale_comparison(img1, img2, scales=[1.0, 0.5, 0.25]):
    """
    Compare images at multiple scales to detect both large and small changes
    """
    scores = []
    
    for scale in scales:
        h, w = img1.shape[:2]
        new_h, new_w = int(h * scale), int(w * scale)
        
        img1_scaled = cv2.resize(img1, (new_w, new_h))
        img2_scaled = cv2.resize(img2, (new_w, new_h))
        
        gray1 = cv2.cvtColor(img1_scaled, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2_scaled, cv2.COLOR_BGR2GRAY)
        
        score = ssim(gray1, gray2)
        scores.append({'scale': scale, 'similarity': float(score)})
    
    return scores


# =========================================================
# HELPER — Advanced Difference Highlighting
# =========================================================
def create_advanced_diff_mask(before_gray, after_gray):
    """
    Enhanced difference detection using:
    - Adaptive thresholding
    - Morphological operations
    - Multi-method fusion
    """
    # Method 1: Absolute difference
    diff_abs = cv2.absdiff(before_gray, after_gray)
    
    # Method 2: SSIM-based difference
    _, diff_ssim = ssim(before_gray, after_gray, full=True)
    diff_ssim = ((1 - diff_ssim) * 255).astype("uint8")
    
    # Method 3: Adaptive threshold on difference
    diff_adaptive = cv2.adaptiveThreshold(
        diff_abs,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    
    # Combine methods
    diff_combined = cv2.bitwise_or(diff_ssim, diff_adaptive)
    diff_combined = cv2.bitwise_or(diff_combined, 
                                    cv2.threshold(diff_abs, 30, 255, cv2.THRESH_BINARY)[1])
    
    # Morphological cleaning
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    diff_combined = cv2.morphologyEx(diff_combined, cv2.MORPH_CLOSE, kernel)
    diff_combined = cv2.morphologyEx(diff_combined, cv2.MORPH_OPEN, kernel)
    
    return diff_combined, diff_ssim


# =========================================================
# HELPER — Structure Heatmap
# =========================================================
def structure_heatmap(img, out_path):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    grad_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    
    magnitude = cv2.magnitude(grad_x, grad_y)
    
    mag_norm = cv2.normalize(
        magnitude, None, 0, 255, cv2.NORM_MINMAX
    ).astype("uint8")
    
    heat = cv2.applyColorMap(mag_norm, cv2.COLORMAP_TURBO)
    
    cv2.imwrite(out_path, heat)
    return out_path


# =========================================================
# HELPER — Part Naming
# =========================================================
def part_name_from_zone(zone):
    if "top" in zone:
        return "upper assembly"
    if "middle" in zone:
        return "core body"
    if "bottom" in zone:
        return "base / mounting area"
    return "unknown part"


# =========================================================
# HELPER — Change Significance Classifier
# =========================================================
def classify_change_significance(zone_data, metrics):
    """
    Classify changes as:
    - CRITICAL: Major structural changes, large rust increase
    - MODERATE: Visible changes, moderate degradation
    - MINOR: Small changes, minimal impact
    """
    severity = zone_data.get('severity', 0)
    area_pct = zone_data.get('area_percent', 0)
    
    rust_delta = metrics.get('rust_delta_pct', 0)
    brightness_delta = abs(metrics.get('after_brightness', 0) - metrics.get('before_brightness', 0))
    
    # Critical if: large area + high severity OR significant rust increase
    if (area_pct > 5 and severity > 7) or rust_delta > 10:
        return "CRITICAL"
    
    # Moderate if: medium area OR moderate changes
    if area_pct > 2 or severity > 4 or rust_delta > 5:
        return "MODERATE"
    
    return "MINOR"


# =========================================================
# MAIN — ENHANCED IMAGE COMPARISON ENGINE
# =========================================================
def compare_images(before_path, after_path, out_path, enable_alignment=True):
    """
    Enhanced image comparison with:
    - Feature-based alignment
    - Multi-method difference detection
    - Advanced defect detection
    - Multi-scale analysis
    - Comprehensive metrics
    """
    
    # ---------- Load images ----------
    before = cv2.imread(before_path)
    after = cv2.imread(after_path)
    
    if before is None or after is None:
        raise ValueError("One of the images could not be read")
    
    # ---------- Size normalization ----------
    MAX_W = 800
    h, w = before.shape[:2]
    
    if w > MAX_W:
        scale = MAX_W / w
        before = cv2.resize(before, (int(w*scale), int(h*scale)))
    
    h, w = before.shape[:2]
    after = cv2.resize(after, (w, h))
    
    # ---------- Image Alignment ----------
    aligned = after
    alignment_success = False
    
    if enable_alignment:
        aligned, alignment_success = align_images(before, after)
        if not alignment_success:
            print("Warning: Image alignment failed, using unaligned images")
            aligned = after
    
    # ---------- Grayscale conversion ----------
    before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(aligned, cv2.COLOR_BGR2GRAY)
    
    # ---------- Histogram equalization for better comparison ----------
    before_eq = cv2.equalizeHist(before_gray)
    after_eq = cv2.equalizeHist(after_gray)
    
    # =====================================================
    # CONDITION METRICS
    # =====================================================
    before_metrics = image_quality_metrics(before)
    after_metrics = image_quality_metrics(aligned)
    
    before_brightness = image_brightness_score(before)
    after_brightness = image_brightness_score(aligned)
    
    # Enhanced rust detection
    before_rust_data = enhanced_rust_score(before)
    after_rust_data = enhanced_rust_score(aligned)
    
    # Crack and damage detection
    before_damage = detect_cracks_and_damage(before)
    after_damage = detect_cracks_and_damage(aligned)
    
    # =====================================================
    # MULTI-SCALE COMPARISON
    # =====================================================
    multiscale_results = multiscale_comparison(before, aligned)
    
    # =====================================================
    # SSIM COMPARISON (on equalized images for better accuracy)
    # =====================================================
    score, diff = ssim(before_eq, after_eq, full=True)
    diff = (diff * 255).astype("uint8")
    
    # =====================================================
    # ADVANCED DIFFERENCE DETECTION
    # =====================================================
    diff_mask, diff_ssim = create_advanced_diff_mask(before_gray, after_gray)
    
    # =====================================================
    # VISUALIZATIONS
    # =====================================================
    
    # Before structure heatmap
    before_heatmap_path = out_path.replace(".jpg", "_before_heatmap.jpg")
    structure_heatmap(before, before_heatmap_path)
    
    # Difference heatmap
    heatmap = cv2.applyColorMap(diff_ssim, cv2.COLORMAP_JET)
    heatmap_path = out_path.replace(".jpg", "_heatmap.jpg")
    cv2.imwrite(heatmap_path, heatmap)
    
    # Enhanced diff mask visualization
    diff_mask_colored = cv2.applyColorMap(diff_mask, cv2.COLORMAP_HOT)
    diff_mask_path = out_path.replace(".jpg", "_diff_mask.jpg")
    cv2.imwrite(diff_mask_path, diff_mask_colored)
    
    # Side-by-side comparison
    comparison = np.hstack([before, aligned])
    comparison_path = out_path.replace(".jpg", "_comparison.jpg")
    cv2.imwrite(comparison_path, comparison)
    
    # =====================================================
    # CONTOUR DETECTION & REGION ANALYSIS
    # =====================================================
    
    # Use enhanced diff mask for contour detection
    contours, _ = cv2.findContours(
        diff_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    
    changed_regions = 0
    change_zones = []
    zone_details = {}
    
    img_h, img_w = aligned.shape[:2]
    total_area = img_w * img_h
    
    # Create output image
    output_img = aligned.copy()
    
    for c in contours:
        area = cv2.contourArea(c)
        
        # Noise filter
        if area < 500:
            continue
        
        x, y, cw, ch = cv2.boundingRect(c)
        
        # Draw rectangle
        cv2.rectangle(
            output_img,
            (x, y),
            (x + cw, y + ch),
            (0, 0, 255),
            2
        )
        
        changed_regions += 1
        
        # Spatial zone
        cx = x + cw / 2
        cy = y + ch / 2
        
        horiz = (
            "left" if cx < img_w / 3
            else "center" if cx < 2 * img_w / 3
            else "right"
        )
        
        vert = (
            "top" if cy < img_h / 3
            else "middle" if cy < 2 * img_h / 3
            else "bottom"
        )
        
        zone = f"{vert}-{horiz}"
        change_zones.append(zone)
        
        # Calculate metrics for this zone
        area_percent = (area / total_area) * 100
        severity = min(10, round(area_percent * 10, 2))
        
        # Extract region for detailed analysis
        region_before = before[y:y+ch, x:x+cw]
        region_after = aligned[y:y+ch, x:x+cw]
        
        # Region-specific metrics
        region_rust_before = enhanced_rust_score(region_before)['rust_ratio']
        region_rust_after = enhanced_rust_score(region_after)['rust_ratio']
        
        zone_data = {
            "severity": severity,
            "area_percent": float(area_percent),
            "area_pixels": int(area),
            "rust_before": float(region_rust_before * 100),
            "rust_after": float(region_rust_after * 100),
            "rust_change": float((region_rust_after - region_rust_before) * 100),
            "part_name": part_name_from_zone(zone),
            "box": {
                "x": int(x),
                "y": int(y),
                "w": int(cw),
                "h": int(ch)
            }
        }
        
        # Classify significance
        zone_data["significance"] = classify_change_significance(
            zone_data,
            {
                'rust_delta_pct': after_rust_data['rust_ratio'] - before_rust_data['rust_ratio'],
                'after_brightness': after_brightness,
                'before_brightness': before_brightness
            }
        )
        
        zone_details[zone] = zone_data
    
    # ---------- Save annotated image ----------
    cv2.imwrite(out_path, output_img)
    
    change_percent = (1 - score) * 100
    
    # =====================================================
    # COMPREHENSIVE RESULTS
    # =====================================================
        # =====================================================
    # UI-COMPATIBLE RETURN STRUCTURE (OLD FORMAT RESTORED)
    # =====================================================

    # Convert new zone_details → old structure
    zone_severity = {}
    zone_parts = {}
    zone_boxes = {}

    for zone, details in zone_details.items():
        zone_severity[zone] = details["severity"]
        zone_parts[zone] = details["part_name"]
        zone_boxes[zone] = details["box"]

    change_percent = (1 - score) * 100

    return {
        # === ORIGINAL UI FIELDS (DO NOT BREAK FRONTEND) ===
        "similarity": float(score),
        "change_percent": float(change_percent),
        "regions": changed_regions,

        "before_brightness": float(before_brightness),
        "after_brightness": float(after_brightness),

        "before_rust_pct": float(before_rust_data['rust_ratio'] * 100),
        "after_rust_pct": float(after_rust_data['rust_ratio'] * 100),
        "rust_delta_pct": float(
            (after_rust_data['rust_ratio'] - before_rust_data['rust_ratio']) * 100
        ),

        "zones": list(set(change_zones)),
        "zone_severity": zone_severity,
        "zone_parts": zone_parts,
        "zone_boxes": zone_boxes,

        "heatmap_path": heatmap_path,
        "before_heatmap_path": before_heatmap_path,

        # === EXTRA ADVANCED DATA (OPTIONAL FOR FUTURE UI) ===
        "alignment_success": alignment_success,
        "multiscale_similarity": multiscale_results,
        "contrast_delta": float(after_metrics['contrast'] - before_metrics['contrast']),
        "sharpness_delta": float(after_metrics['sharpness'] - before_metrics['sharpness']),
        "crack_delta": after_damage['crack_count'] - before_damage['crack_count'],
        "diff_mask_path": diff_mask_path,
        "comparison_path": comparison_path,
        "zone_details": zone_details  # keep for advanced popup later
    }



# =========================================================
# EXAMPLE USAGE
# =========================================================
if __name__ == "__main__":
    # Example usage
    results = compare_images(
        "before.jpg",
        "after.jpg",
        "output_annotated.jpg",
        enable_alignment=True
    )
    
    print("=" * 60)
    print("IMAGE COMPARISON RESULTS")
    print("=" * 60)
    print(f"Overall Similarity: {results['similarity']:.2%}")
    print(f"Overall Change: {results['change_percent']:.2f}%")
    print(f"Changed Regions: {results['regions']}")
    print(f"Alignment Success: {results['alignment_success']}")
    print()
    print(f"Rust Change: {results['rust_delta_pct']:.2f}%")
    print(f"New Cracks: {results['crack_delta']}")
    print(f"Brightness Change: {results['brightness_delta']:.2f}")
    print()
    print("Zone Details:")
    for zone, details in results['zone_details'].items():
        print(f"  {zone} ({details['part_name']}):")
        print(f"    Significance: {details['significance']}")
        print(f"    Severity: {details['severity']}/10")
        print(f"    Area: {details['area_percent']:.2f}%")