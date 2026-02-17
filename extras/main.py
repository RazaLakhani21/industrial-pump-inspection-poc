#!/usr/bin/env python3
"""
Main execution script for equipment image comparison
Demonstrates complete workflow from comparison to visualization
"""

import os
import sys
from enhanced_comparison import compare_images
from extras.dashboard_generator import ComparisonDashboard


def run_comparison_pipeline(before_path, after_path, output_dir="results"):
    """
    Complete comparison pipeline:
    1. Run enhanced image comparison
    2. Generate visual dashboard
    3. Create HTML report
    4. Save JSON results
    """
    
    print("=" * 70)
    print("🔍 EQUIPMENT CONDITION COMPARISON SYSTEM")
    print("=" * 70)
    print()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Run comparison
    print("📊 Step 1: Running enhanced image comparison...")
    print(f"   Before: {before_path}")
    print(f"   After:  {after_path}")
    print()
    
    try:
        annotated_path = os.path.join(output_dir, "annotated_output.jpg")
        results = compare_images(
            before_path,
            after_path,
            annotated_path,
            enable_alignment=True
        )
        
        # Store annotated path in results
        results['annotated_path'] = annotated_path
        
        print("✅ Comparison complete!")
        print()
        
    except Exception as e:
        print(f"❌ Error during comparison: {e}")
        return None
    
    # Step 2: Print summary
    print("=" * 70)
    print("📈 COMPARISON SUMMARY")
    print("=" * 70)
    print(f"Overall Similarity:      {results['similarity']:.2%}")
    print(f"Overall Change:          {results['change_percent']:.2f}%")
    print(f"Changed Regions:         {results['regions']}")
    print(f"Image Alignment:         {'✓ Success' if results['alignment_success'] else '✗ Failed'}")
    print()
    print(f"Rust Change:             {results['rust_delta_pct']:+.2f}%")
    print(f"  Before:                {results['before_rust_pct']:.2f}%")
    print(f"  After:                 {results['after_rust_pct']:.2f}%")
    print()
    print(f"Crack Detection:")
    print(f"  Before:                {results['before_cracks']} cracks")
    print(f"  After:                 {results['after_cracks']} cracks")
    print(f"  New Cracks:            {results['crack_delta']}")
    print()
    print(f"Brightness Change:       {results['brightness_delta']:+.2f}")
    print(f"Contrast Change:         {results['contrast_delta']:+.2f}")
    print(f"Sharpness Change:        {results['sharpness_delta']:+.2f}")
    print()
    
    # Print zone details
    if results.get('zone_details'):
        print("=" * 70)
        print("📍 ZONE ANALYSIS")
        print("=" * 70)
        for zone, details in results['zone_details'].items():
            print(f"\n{zone.upper()} ({details['part_name']}):")
            print(f"  Significance:          {details['significance']}")
            print(f"  Severity:              {details['severity']}/10")
            print(f"  Area Coverage:         {details['area_percent']:.2f}%")
            print(f"  Rust Change:           {details['rust_change']:+.1f}%")
            print(f"  Location:              x={details['box']['x']}, y={details['box']['y']}")
        print()
    
    # Print multi-scale results
    print("=" * 70)
    print("🔬 MULTI-SCALE ANALYSIS")
    print("=" * 70)
    for scale_result in results['multiscale_similarity']:
        print(f"Scale {scale_result['scale']:.0%}:              {scale_result['similarity']:.4f}")
    print()
    
    # Step 3: Generate dashboard
    print("=" * 70)
    print("🎨 Step 2: Generating visual dashboard...")
    print("=" * 70)
    
    try:
        dashboard = ComparisonDashboard(results, before_path, after_path)
        
        # Create all outputs
        dashboard_path = os.path.join(output_dir, "dashboard.png")
        html_path = os.path.join(output_dir, "report.html")
        json_path = os.path.join(output_dir, "results.json")
        
        dashboard.create_full_dashboard(dashboard_path)
        dashboard.create_html_report(html_path)
        dashboard.create_json_report(json_path)
        
        print()
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 4: Summary of outputs
    print("=" * 70)
    print("📁 OUTPUT FILES")
    print("=" * 70)
    print(f"Annotated Image:         {annotated_path}")
    print(f"Comparison Dashboard:    {dashboard_path}")
    print(f"HTML Report:             {html_path}")
    print(f"JSON Results:            {json_path}")
    print(f"Change Heatmap:          {results['heatmap_path']}")
    print(f"Difference Mask:         {results['diff_mask_path']}")
    print(f"Structure Map:           {results['before_heatmap_path']}")
    print(f"Side-by-Side:            {results['comparison_path']}")
    print()
    
    print("=" * 70)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 70)
    print(f"Open {html_path} in your browser for interactive report")
    print()
    
    return results


def batch_comparison(image_pairs, output_base_dir="batch_results"):
    """
    Run comparisons on multiple image pairs
    
    Args:
        image_pairs: List of tuples [(before1, after1), (before2, after2), ...]
        output_base_dir: Base directory for all results
    """
    print("=" * 70)
    print("🔄 BATCH COMPARISON MODE")
    print("=" * 70)
    print(f"Processing {len(image_pairs)} image pairs...")
    print()
    
    all_results = []
    
    for i, (before, after) in enumerate(image_pairs, 1):
        print(f"\n{'='*70}")
        print(f"Processing Pair {i}/{len(image_pairs)}")
        print(f"{'='*70}\n")
        
        # Create output directory for this pair
        output_dir = os.path.join(output_base_dir, f"pair_{i:02d}")
        
        results = run_comparison_pipeline(before, after, output_dir)
        
        if results:
            all_results.append({
                'pair_id': i,
                'before': before,
                'after': after,
                'output_dir': output_dir,
                'results': results
            })
    
    # Create batch summary
    print("\n" + "=" * 70)
    print("📊 BATCH SUMMARY")
    print("=" * 70)
    
    for result in all_results:
        status = "🔴 CRITICAL" if result['results']['change_percent'] > 20 else \
                 "🟡 MODERATE" if result['results']['change_percent'] > 10 else \
                 "🟢 MINIMAL"
        
        print(f"Pair {result['pair_id']:02d}: {status} - {result['results']['change_percent']:.1f}% change")
    
    print()
    return all_results


def create_test_images():
    """
    Create synthetic test images for demonstration
    """
    import cv2
    import numpy as np
    
    print("🎨 Creating test images...")
    
    # Create a simple equipment-like image
    img_size = (600, 800, 3)
    
    # Before image
    before = np.ones(img_size, dtype=np.uint8) * 200
    
    # Add some structure
    cv2.rectangle(before, (100, 100), (700, 500), (150, 150, 150), -1)
    cv2.rectangle(before, (150, 150), (650, 450), (180, 180, 180), 3)
    cv2.circle(before, (400, 300), 80, (160, 160, 160), -1)
    cv2.line(before, (200, 200), (600, 400), (140, 140, 140), 5)
    
    # Add some texture
    noise = np.random.randint(0, 30, img_size, dtype=np.uint8)
    before = cv2.add(before, noise)
    
    # After image (with changes)
    after = before.copy()
    
    # Add rust-like discoloration
    rust_mask = np.zeros(img_size[:2], dtype=np.uint8)
    cv2.circle(rust_mask, (300, 250), 60, 255, -1)
    cv2.circle(rust_mask, (500, 350), 40, 255, -1)
    rust_color = np.array([20, 80, 150], dtype=np.uint8)  # Brown/rust color
    after[rust_mask > 0] = rust_color
    
    # Add a crack
    cv2.line(after, (250, 200), (350, 400), (100, 100, 100), 2)
    
    # Add damage area
    cv2.rectangle(after, (400, 150), (550, 250), (120, 120, 120), -1)
    
    # Slightly darken overall
    after = cv2.addWeighted(after, 0.95, np.zeros_like(after), 0, -10)
    
    # Save test images
    os.makedirs("test_images", exist_ok=True)
    before_path = "test_images/before.jpg"
    after_path = "test_images/after.jpg"
    
    cv2.imwrite(before_path, before)
    cv2.imwrite(after_path, after)
    
    print(f"✅ Test images created:")
    print(f"   {before_path}")
    print(f"   {after_path}")
    print()
    
    return before_path, after_path


if __name__ == "__main__":
    
    # Check if images were provided as arguments
    if len(sys.argv) >= 3:
        before_img = sys.argv[1]
        after_img = sys.argv[2]
        output_directory = sys.argv[3] if len(sys.argv) > 3 else "results"
        
        if not os.path.exists(before_img):
            print(f"❌ Error: Before image not found: {before_img}")
            sys.exit(1)
        
        if not os.path.exists(after_img):
            print(f"❌ Error: After image not found: {after_img}")
            sys.exit(1)
        
        run_comparison_pipeline(before_img, after_img, output_directory)
    
    else:
        # Demo mode with synthetic images
        print("=" * 70)
        print("🚀 DEMO MODE - No images provided")
        print("=" * 70)
        print("Creating synthetic test images for demonstration...\n")
        
        before_path, after_path = create_test_images()
        
        print("\nRunning comparison on test images...\n")
        run_comparison_pipeline(before_path, after_path, "demo_results")
        
        print("\n" + "=" * 70)
        print("💡 TIP: To analyze your own images, run:")
        print("   python main.py <before_image> <after_image> [output_dir]")
        print("=" * 70)