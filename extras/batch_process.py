# #!/usr/bin/env python3
# """
# Batch processing utility for comparing multiple image pairs
# Useful for analyzing entire folders or monitoring multiple equipment pieces
# """

# import os
# import glob
# import argparse
# from pathlib import Path
# from datetime import datetime
# import json
# from enhanced_comparison import compare_images
# from dashboard_generator import ComparisonDashboard


# def find_image_pairs(before_dir, after_dir, pattern="*.jpg"):
#     """
#     Automatically match before/after images based on filename
    
#     Args:
#         before_dir: Directory containing "before" images
#         after_dir: Directory containing "after" images  
#         pattern: Filename pattern to match (default: *.jpg)
    
#     Returns:
#         List of (before_path, after_path) tuples
#     """
#     before_files = glob.glob(os.path.join(before_dir, pattern))
#     pairs = []
    
#     for before_path in sorted(before_files):
#         filename = os.path.basename(before_path)
#         after_path = os.path.join(after_dir, filename)
        
#         if os.path.exists(after_path):
#             pairs.append((before_path, after_path))
#         else:
#             print(f"⚠️  Warning: No matching 'after' image for {filename}")
    
#     return pairs


# def process_batch(pairs, output_dir="batch_results", create_reports=True):
#     """
#     Process multiple image pairs in batch
    
#     Args:
#         pairs: List of (before_path, after_path) tuples
#         output_dir: Base directory for all outputs
#         create_reports: Whether to generate HTML/dashboard for each pair
    
#     Returns:
#         Summary dictionary with all results
#     """
#     os.makedirs(output_dir, exist_ok=True)
    
#     print("=" * 80)
#     print(f"🔄 BATCH PROCESSING - {len(pairs)} IMAGE PAIRS")
#     print("=" * 80)
#     print()
    
#     all_results = []
#     summary_stats = {
#         'total_pairs': len(pairs),
#         'successful': 0,
#         'failed': 0,
#         'critical_changes': 0,
#         'moderate_changes': 0,
#         'minimal_changes': 0,
#         'avg_change_percent': 0,
#         'avg_rust_delta': 0,
#         'total_new_cracks': 0,
#     }
    
#     for i, (before_path, after_path) in enumerate(pairs, 1):
#         print(f"\n{'='*80}")
#         print(f"📸 Processing Pair {i}/{len(pairs)}")
#         print(f"{'='*80}")
#         print(f"Before: {os.path.basename(before_path)}")
#         print(f"After:  {os.path.basename(after_path)}")
#         print()
        
#         # Create output directory for this pair
#         pair_name = Path(before_path).stem
#         pair_output_dir = os.path.join(output_dir, f"{i:03d}_{pair_name}")
#         os.makedirs(pair_output_dir, exist_ok=True)
        
#         try:
#             # Run comparison
#             annotated_path = os.path.join(pair_output_dir, "annotated.jpg")
#             results = compare_images(
#                 before_path,
#                 after_path,
#                 annotated_path,
#                 enable_alignment=True
#             )
            
#             results['annotated_path'] = annotated_path
            
#             # Quick summary
#             change = results['change_percent']
#             print(f"✅ Analysis complete!")
#             print(f"   Similarity: {results['similarity']:.2%}")
#             print(f"   Change: {change:.2f}%")
#             print(f"   Regions: {results['regions']}")
#             print(f"   Rust Δ: {results['rust_delta_pct']:+.2f}%")
#             print(f"   New Cracks: {results['crack_delta']}")
            
#             # Classify change level
#             if change > 20:
#                 level = 'CRITICAL'
#                 summary_stats['critical_changes'] += 1
#             elif change > 10:
#                 level = 'MODERATE'
#                 summary_stats['moderate_changes'] += 1
#             else:
#                 level = 'MINIMAL'
#                 summary_stats['minimal_changes'] += 1
            
#             print(f"   Status: {level}")
            
#             # Generate reports if requested
#             if create_reports:
#                 print(f"\n📊 Generating reports...")
#                 dashboard = ComparisonDashboard(results, before_path, after_path)
                
#                 dashboard.create_full_dashboard(
#                     os.path.join(pair_output_dir, "dashboard.png")
#                 )
#                 dashboard.create_html_report(
#                     os.path.join(pair_output_dir, "report.html")
#                 )
#                 dashboard.create_json_report(
#                     os.path.join(pair_output_dir, "results.json")
#                 )
            
#             # Store results
#             all_results.append({
#                 'pair_id': i,
#                 'pair_name': pair_name,
#                 'before': before_path,
#                 'after': after_path,
#                 'output_dir': pair_output_dir,
#                 'level': level,
#                 'results': results
#             })
            
#             summary_stats['successful'] += 1
#             summary_stats['avg_change_percent'] += change
#             summary_stats['avg_rust_delta'] += results['rust_delta_pct']
#             summary_stats['total_new_cracks'] += results['crack_delta']
            
#         except Exception as e:
#             print(f"❌ Error processing pair: {e}")
#             import traceback
#             traceback.print_exc()
#             summary_stats['failed'] += 1
    
#     # Calculate averages
#     if summary_stats['successful'] > 0:
#         summary_stats['avg_change_percent'] /= summary_stats['successful']
#         summary_stats['avg_rust_delta'] /= summary_stats['successful']
    
#     # Create batch summary report
#     create_batch_summary(all_results, summary_stats, output_dir)
    
#     return all_results, summary_stats


# def create_batch_summary(all_results, stats, output_dir):
#     """
#     Create a master summary HTML report for all pairs
#     """
#     html_template = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Batch Comparison Summary</title>
#     <style>
#         * { margin: 0; padding: 0; box-sizing: border-box; }
#         body {
#             font-family: 'Segoe UI', sans-serif;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             padding: 20px;
#         }
#         .container {
#             max-width: 1200px;
#             margin: 0 auto;
#             background: white;
#             border-radius: 15px;
#             overflow: hidden;
#             box-shadow: 0 20px 60px rgba(0,0,0,0.3);
#         }
#         .header {
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white;
#             padding: 40px;
#             text-align: center;
#         }
#         .header h1 { font-size: 2.5em; margin-bottom: 10px; }
#         .stats {
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
#             gap: 20px;
#             padding: 40px;
#             background: #f8f9fa;
#         }
#         .stat-card {
#             background: white;
#             padding: 20px;
#             border-radius: 10px;
#             text-align: center;
#             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#         }
#         .stat-value {
#             font-size: 2.5em;
#             font-weight: bold;
#             color: #667eea;
#             margin: 10px 0;
#         }
#         .stat-label {
#             color: #666;
#             font-size: 0.9em;
#             text-transform: uppercase;
#             letter-spacing: 1px;
#         }
#         .results-table {
#             padding: 40px;
#         }
#         table {
#             width: 100%;
#             border-collapse: collapse;
#             margin-top: 20px;
#         }
#         th {
#             background: #667eea;
#             color: white;
#             padding: 15px;
#             text-align: left;
#             font-weight: 600;
#         }
#         td {
#             padding: 12px 15px;
#             border-bottom: 1px solid #eee;
#         }
#         tr:hover { background: #f8f9fa; }
#         .badge {
#             display: inline-block;
#             padding: 5px 12px;
#             border-radius: 15px;
#             font-size: 0.85em;
#             font-weight: bold;
#         }
#         .badge-critical { background: #ff6b6b; color: white; }
#         .badge-moderate { background: #ffa500; color: white; }
#         .badge-minimal { background: #51cf66; color: white; }
#         a { color: #667eea; text-decoration: none; }
#         a:hover { text-decoration: underline; }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <div class="header">
#             <h1>📊 Batch Comparison Summary</h1>
#             <p>Generated: {timestamp}</p>
#         </div>
        
#         <div class="stats">
#             <div class="stat-card">
#                 <div class="stat-label">Total Pairs</div>
#                 <div class="stat-value">{total_pairs}</div>
#             </div>
#             <div class="stat-card">
#                 <div class="stat-label">Successful</div>
#                 <div class="stat-value" style="color: #51cf66;">{successful}</div>
#             </div>
#             <div class="stat-card">
#                 <div class="stat-label">Failed</div>
#                 <div class="stat-value" style="color: #ff6b6b;">{failed}</div>
#             </div>
#             <div class="stat-card">
#                 <div class="stat-label">Critical Changes</div>
#                 <div class="stat-value" style="color: #ff6b6b;">{critical}</div>
#             </div>
#             <div class="stat-card">
#                 <div class="stat-label">Moderate Changes</div>
#                 <div class="stat-value" style="color: #ffa500;">{moderate}</div>
#             </div>
#             <div class="stat-card">
#                 <div class="stat-label">Minimal Changes</div>
#                 <div class="stat-value" style="color: #51cf66;">{minimal}</div>
#             </div>
#             <div class="stat-card">
#                 <div class="stat-label">Avg Change</div>
#                 <div class="stat-value">{avg_change:.1f}%</div>
#             </div>
#             <div class="stat-card">
#                 <div class="stat-label">Total New Cracks</div>
#                 <div class="stat-value">{total_cracks}</div>
#             </div>
#         </div>
        
#         <div class="results-table">
#             <h2>Detailed Results</h2>
#             <table>
#                 <thead>
#                     <tr>
#                         <th>#</th>
#                         <th>Image Pair</th>
#                         <th>Status</th>
#                         <th>Change %</th>
#                         <th>Rust Δ</th>
#                         <th>New Cracks</th>
#                         <th>Regions</th>
#                         <th>Report</th>
#                     </tr>
#                 </thead>
#                 <tbody>
#                     {table_rows}
#                 </tbody>
#             </table>
#         </div>
#     </div>
# </body>
# </html>
# """
    
#     # Generate table rows
#     rows = ""
#     for result in all_results:
#         r = result['results']
#         badge_class = f"badge-{result['level'].lower()}"
        
#         report_link = f"{result['pair_id']:03d}_{result['pair_name']}/report.html"
        
#         rows += f"""
#         <tr>
#             <td>{result['pair_id']}</td>
#             <td>{result['pair_name']}</td>
#             <td><span class="badge {badge_class}">{result['level']}</span></td>
#             <td>{r['change_percent']:.2f}%</td>
#             <td>{r['rust_delta_pct']:+.2f}%</td>
#             <td>{r['crack_delta']}</td>
#             <td>{r['regions']}</td>
#             <td><a href="{report_link}">View Report →</a></td>
#         </tr>
#         """
    
#     # Fill template
#     html = html_template.format(
#         timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         total_pairs=stats['total_pairs'],
#         successful=stats['successful'],
#         failed=stats['failed'],
#         critical=stats['critical_changes'],
#         moderate=stats['moderate_changes'],
#         minimal=stats['minimal_changes'],
#         avg_change=stats['avg_change_percent'],
#         total_cracks=stats['total_new_cracks'],
#         table_rows=rows
#     )
    
#     # Save
#     summary_path = os.path.join(output_dir, "batch_summary.html")
#     with open(summary_path, 'w') as f:
#         f.write(html)
    
#     # Also save JSON
#     json_path = os.path.join(output_dir, "batch_summary.json")
#     with open(json_path, 'w') as f:
#         json.dump({
#             'timestamp': datetime.now().isoformat(),
#             'statistics': stats,
#             'results': [
#                 {
#                     'pair_id': r['pair_id'],
#                     'pair_name': r['pair_name'],
#                     'level': r['level'],
#                     'before': r['before'],
#                     'after': r['after'],
#                     'output_dir': r['output_dir'],
#                     'metrics': {
#                         'similarity': r['results']['similarity'],
#                         'change_percent': r['results']['change_percent'],
#                         'rust_delta_pct': r['results']['rust_delta_pct'],
#                         'crack_delta': r['results']['crack_delta'],
#                         'regions': r['results']['regions'],
#                     }
#                 }
#                 for r in all_results
#             ]
#         }, f, indent=2)
    
#     print(f"\n✅ Batch summary saved:")
#     print(f"   HTML: {summary_path}")
#     print(f"   JSON: {json_path}")


# def main():
#     parser = argparse.ArgumentParser(
#         description='Batch process multiple image pairs for comparison',
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         epilog="""
# Examples:
#   # Process all JPG images from two directories
#   python batch_process.py --before before_images/ --after after_images/
  
#   # Process specific image pairs
#   python batch_process.py --pairs before1.jpg,after1.jpg before2.jpg,after2.jpg
  
#   # Quick mode (no HTML/dashboard generation)
#   python batch_process.py --before before/ --after after/ --quick
#         """
#     )
    
#     parser.add_argument('--before', help='Directory containing before images')
#     parser.add_argument('--after', help='Directory containing after images')
#     parser.add_argument('--pairs', nargs='+', help='Explicit pairs as before,after')
#     parser.add_argument('--pattern', default='*.jpg', help='Filename pattern (default: *.jpg)')
#     parser.add_argument('--output', default='batch_results', help='Output directory')
#     parser.add_argument('--quick', action='store_true', help='Skip HTML/dashboard generation')
    
#     args = parser.parse_args()
    
#     # Determine image pairs
#     pairs = []
    
#     if args.pairs:
#         # Explicit pairs from command line
#         for pair_str in args.pairs:
#             before, after = pair_str.split(',')
#             if os.path.exists(before) and os.path.exists(after):
#                 pairs.append((before, after))
#             else:
#                 print(f"⚠️  Warning: Could not find pair: {pair_str}")
    
#     elif args.before and args.after:
#         # Auto-match from directories
#         pairs = find_image_pairs(args.before, args.after, args.pattern)
    
#     else:
#         parser.print_help()
#         return
    
#     if not pairs:
#         print("❌ No valid image pairs found!")
#         return
    
#     # Process batch
#     results, stats = process_batch(
#         pairs,
#         output_dir=args.output,
#         create_reports=not args.quick
#     )
    
#     # Print final summary
#     print("\n" + "=" * 80)
#     print("📊 BATCH PROCESSING COMPLETE")
#     print("=" * 80)
#     print(f"Total Pairs:         {stats['total_pairs']}")
#     print(f"Successful:          {stats['successful']}")
#     print(f"Failed:              {stats['failed']}")
#     print(f"Critical Changes:    {stats['critical_changes']}")
#     print(f"Moderate Changes:    {stats['moderate_changes']}")
#     print(f"Minimal Changes:     {stats['minimal_changes']}")
#     print(f"Average Change:      {stats['avg_change_percent']:.2f}%")
#     print(f"Total New Cracks:    {stats['total_new_cracks']}")
#     print()
#     print(f"Results saved to: {args.output}/")
#     print(f"Open batch_summary.html for interactive overview")
#     print("=" * 80)


# if __name__ == "__main__":
#     main()