# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# from datetime import datetime
# import json
# import os


# class ComparisonDashboard:
#     """
#     Creates visual dashboards and reports from comparison results
#     """
    
#     def __init__(self, results, before_path, after_path):
#         self.results = results
#         self.before_path = before_path
#         self.after_path = after_path
        
#     def create_full_dashboard(self, output_path="dashboard.png"):
#         """
#         Create a comprehensive visual dashboard with all metrics and images
#         """
#         # Create figure with subplots
#         fig = plt.figure(figsize=(20, 12))
#         gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
        
#         # Load images
#         before = cv2.imread(self.before_path)
#         after = cv2.imread(self.after_path)
#         before_rgb = cv2.cvtColor(before, cv2.COLOR_BGR2RGB)
#         after_rgb = cv2.cvtColor(after, cv2.COLOR_BGR2RGB)
        
#         # Title
#         fig.suptitle('EQUIPMENT CONDITION COMPARISON DASHBOARD', 
#                      fontsize=20, fontweight='bold', y=0.98)
        
#         # ==================== ROW 1: Main Images ====================
#         ax1 = fig.add_subplot(gs[0, :2])
#         ax1.imshow(before_rgb)
#         ax1.set_title('BEFORE', fontsize=14, fontweight='bold')
#         ax1.axis('off')
        
#         ax2 = fig.add_subplot(gs[0, 2:])
#         ax2.imshow(after_rgb)
#         ax2.set_title('AFTER', fontsize=14, fontweight='bold')
#         ax2.axis('off')
        
#         # ==================== ROW 2: Heatmaps ====================
#         ax3 = fig.add_subplot(gs[1, 0])
#         before_heat = cv2.imread(self.results['before_heatmap_path'])
#         before_heat = cv2.cvtColor(before_heat, cv2.COLOR_BGR2RGB)
#         ax3.imshow(before_heat)
#         ax3.set_title('Structure Map', fontsize=11)
#         ax3.axis('off')
        
#         ax4 = fig.add_subplot(gs[1, 1])
#         diff_heat = cv2.imread(self.results['heatmap_path'])
#         diff_heat = cv2.cvtColor(diff_heat, cv2.COLOR_BGR2RGB)
#         ax4.imshow(diff_heat)
#         ax4.set_title('Change Heatmap', fontsize=11)
#         ax4.axis('off')
        
#         ax5 = fig.add_subplot(gs[1, 2])
#         diff_mask = cv2.imread(self.results['diff_mask_path'])
#         diff_mask = cv2.cvtColor(diff_mask, cv2.COLOR_BGR2RGB)
#         ax5.imshow(diff_mask)
#         ax5.set_title('Difference Mask', fontsize=11)
#         ax5.axis('off')
        
#         ax6 = fig.add_subplot(gs[1, 3])
#         # Annotated output
#         annotated = cv2.imread(self.results.get('annotated_path', self.after_path))
#         annotated = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
#         ax6.imshow(annotated)
#         ax6.set_title('Detected Changes', fontsize=11)
#         ax6.axis('off')
        
#         # ==================== ROW 3: Metrics Panels ====================
        
#         # Overall metrics panel
#         ax7 = fig.add_subplot(gs[2, 0])
#         ax7.axis('off')
#         metrics_text = self._format_overall_metrics()
#         ax7.text(0.05, 0.95, metrics_text, transform=ax7.transAxes,
#                 fontsize=10, verticalalignment='top', fontfamily='monospace',
#                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
#         # Condition metrics panel
#         ax8 = fig.add_subplot(gs[2, 1])
#         ax8.axis('off')
#         condition_text = self._format_condition_metrics()
#         ax8.text(0.05, 0.95, condition_text, transform=ax8.transAxes,
#                 fontsize=10, verticalalignment='top', fontfamily='monospace',
#                 bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
#         # Quality metrics panel
#         ax9 = fig.add_subplot(gs[2, 2])
#         ax9.axis('off')
#         quality_text = self._format_quality_metrics()
#         ax9.text(0.05, 0.95, quality_text, transform=ax9.transAxes,
#                 fontsize=10, verticalalignment='top', fontfamily='monospace',
#                 bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        
#         # Damage detection panel
#         ax10 = fig.add_subplot(gs[2, 3])
#         ax10.axis('off')
#         damage_text = self._format_damage_metrics()
#         ax10.text(0.05, 0.95, damage_text, transform=ax10.transAxes,
#                 fontsize=10, verticalalignment='top', fontfamily='monospace',
#                 bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))
        
#         # ==================== ROW 4: Charts ====================
        
#         # Multi-scale similarity chart
#         ax11 = fig.add_subplot(gs[3, :2])
#         self._plot_multiscale_similarity(ax11)
        
#         # Zone severity chart
#         ax12 = fig.add_subplot(gs[3, 2:])
#         self._plot_zone_severity(ax12)
        
#         # Save
#         plt.savefig(output_path, dpi=150, bbox_inches='tight')
#         plt.close()
        
#         print(f"✅ Dashboard saved to: {output_path}")
#         return output_path
    
#     def _format_overall_metrics(self):
#         """Format overall comparison metrics"""
#         r = self.results
        
#         # Determine status
#         if r['change_percent'] > 20:
#             status = "⚠️ SIGNIFICANT"
#         elif r['change_percent'] > 10:
#             status = "⚡ MODERATE"
#         else:
#             status = "✅ MINIMAL"
        
#         text = f"""OVERALL METRICS
# {'='*25}
# Similarity:     {r['similarity']:.1%}
# Change:         {r['change_percent']:.1f}%
# Status:         {status}

# Changed Regions: {r['regions']}
# Alignment:      {'✓' if r.get('alignment_success') else '✗'}
# """
#         return text
    
#     def _format_condition_metrics(self):
#         """Format condition/rust metrics"""
#         r = self.results
        
#         rust_status = "🔴 INCREASING" if r['rust_delta_pct'] > 2 else "🟢 STABLE"
        
#         text = f"""CORROSION ANALYSIS
# {'='*25}
# Before Rust:    {r['before_rust_pct']:.1f}%
# After Rust:     {r['after_rust_pct']:.1f}%
# Change:         {r['rust_delta_pct']:+.1f}%
# Status:         {rust_status}

# Brightness:     {r['brightness_delta']:+.1f}
# """
#         return text
    
#     def _format_quality_metrics(self):
#         """Format quality metrics"""
#         r = self.results
        
#         text = f"""QUALITY METRICS
# {'='*25}
# Contrast Δ:     {r['contrast_delta']:+.1f}
# Sharpness Δ:    {r['sharpness_delta']:+.1f}

# Before Entropy: {r['before_quality']['entropy']:.2f}
# After Entropy:  {r['after_quality']['entropy']:.2f}
# """
#         return text
    
#     def _format_damage_metrics(self):
#         """Format damage detection metrics"""
#         r = self.results
        
#         crack_status = "🔴 NEW CRACKS" if r['crack_delta'] > 0 else "🟢 NO NEW"
        
#         text = f"""DAMAGE DETECTION
# {'='*25}
# Before Cracks:  {r['before_cracks']}
# After Cracks:   {r['after_cracks']}
# New Cracks:     {r['crack_delta']}
# Status:         {crack_status}

# Damage Area:    {r['after_damage_pct']:.1f}%
# """
#         return text
    
#     def _plot_multiscale_similarity(self, ax):
#         """Plot multi-scale similarity scores"""
#         scales = [s['scale'] for s in self.results['multiscale_similarity']]
#         similarities = [s['similarity'] for s in self.results['multiscale_similarity']]
        
#         ax.bar(range(len(scales)), similarities, color='steelblue', alpha=0.7)
#         ax.set_xticks(range(len(scales)))
#         ax.set_xticklabels([f"{s:.0%}" for s in scales])
#         ax.set_xlabel('Scale', fontweight='bold')
#         ax.set_ylabel('Similarity', fontweight='bold')
#         ax.set_title('Multi-Scale Similarity Analysis', fontweight='bold')
#         ax.set_ylim([0, 1])
#         ax.grid(axis='y', alpha=0.3)
        
#         # Add value labels
#         for i, v in enumerate(similarities):
#             ax.text(i, v + 0.02, f'{v:.2%}', ha='center', fontsize=9)
    
#     def _plot_zone_severity(self, ax):
#         """Plot zone severity bars"""
#         zone_details = self.results.get('zone_details', {})
        
#         if not zone_details:
#             ax.text(0.5, 0.5, 'No zones detected', ha='center', va='center')
#             ax.axis('off')
#             return
        
#         zones = list(zone_details.keys())
#         severities = [zone_details[z]['severity'] for z in zones]
#         significances = [zone_details[z]['significance'] for z in zones]
        
#         # Color by significance
#         colors = []
#         for sig in significances:
#             if sig == 'CRITICAL':
#                 colors.append('red')
#             elif sig == 'MODERATE':
#                 colors.append('orange')
#             else:
#                 colors.append('green')
        
#         y_pos = np.arange(len(zones))
#         ax.barh(y_pos, severities, color=colors, alpha=0.7)
#         ax.set_yticks(y_pos)
#         ax.set_yticklabels(zones, fontsize=9)
#         ax.set_xlabel('Severity (0-10)', fontweight='bold')
#         ax.set_title('Zone Severity Analysis', fontweight='bold')
#         ax.set_xlim([0, 10])
#         ax.grid(axis='x', alpha=0.3)
        
#         # Add value labels
#         for i, v in enumerate(severities):
#             ax.text(v + 0.2, i, f'{v:.1f}', va='center', fontsize=9)
    
#     def create_html_report(self, output_path="report.html"):
#         """Create an interactive HTML report"""
        
#         html_template = """
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Image Comparison Report</title>
#     <style>
#         * {
#             margin: 0;
#             padding: 0;
#             box-sizing: border-box;
#         }
        
#         body {
#             font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             padding: 20px;
#             color: #333;
#         }
        
#         .container {
#             max-width: 1400px;
#             margin: 0 auto;
#             background: white;
#             border-radius: 15px;
#             box-shadow: 0 20px 60px rgba(0,0,0,0.3);
#             overflow: hidden;
#         }
        
#         .header {
#             background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#             color: white;
#             padding: 40px;
#             text-align: center;
#         }
        
#         .header h1 {
#             font-size: 2.5em;
#             margin-bottom: 10px;
#         }
        
#         .header .timestamp {
#             opacity: 0.9;
#             font-size: 1.1em;
#         }
        
#         .summary-cards {
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
#             gap: 20px;
#             padding: 40px;
#             background: #f8f9fa;
#         }
        
#         .card {
#             background: white;
#             border-radius: 10px;
#             padding: 25px;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#             transition: transform 0.2s;
#         }
        
#         .card:hover {
#             transform: translateY(-5px);
#             box-shadow: 0 8px 12px rgba(0,0,0,0.15);
#         }
        
#         .card-title {
#             font-size: 0.9em;
#             color: #666;
#             text-transform: uppercase;
#             letter-spacing: 1px;
#             margin-bottom: 10px;
#         }
        
#         .card-value {
#             font-size: 2.5em;
#             font-weight: bold;
#             color: #667eea;
#             margin-bottom: 5px;
#         }
        
#         .card-label {
#             font-size: 0.9em;
#             color: #888;
#         }
        
#         .status-badge {
#             display: inline-block;
#             padding: 5px 15px;
#             border-radius: 20px;
#             font-size: 0.85em;
#             font-weight: bold;
#             margin-top: 10px;
#         }
        
#         .status-critical { background: #ff6b6b; color: white; }
#         .status-moderate { background: #ffa500; color: white; }
#         .status-minimal { background: #51cf66; color: white; }
        
#         .images-section {
#             padding: 40px;
#         }
        
#         .images-grid {
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
#             gap: 30px;
#             margin-top: 20px;
#         }
        
#         .image-card {
#             background: white;
#             border-radius: 10px;
#             overflow: hidden;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#         }
        
#         .image-card img {
#             width: 100%;
#             height: auto;
#             display: block;
#         }
        
#         .image-card-title {
#             padding: 15px;
#             background: #f8f9fa;
#             font-weight: bold;
#             text-align: center;
#             border-top: 3px solid #667eea;
#         }
        
#         .zones-section {
#             padding: 40px;
#             background: #f8f9fa;
#         }
        
#         .section-title {
#             font-size: 1.8em;
#             margin-bottom: 20px;
#             color: #333;
#             border-bottom: 3px solid #667eea;
#             padding-bottom: 10px;
#         }
        
#         .zone-item {
#             background: white;
#             border-radius: 10px;
#             padding: 20px;
#             margin-bottom: 15px;
#             box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#             border-left: 5px solid #667eea;
#         }
        
#         .zone-header {
#             display: flex;
#             justify-content: space-between;
#             align-items: center;
#             margin-bottom: 15px;
#         }
        
#         .zone-name {
#             font-size: 1.2em;
#             font-weight: bold;
#             color: #333;
#         }
        
#         .zone-metrics {
#             display: grid;
#             grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
#             gap: 15px;
#         }
        
#         .zone-metric {
#             text-align: center;
#             padding: 10px;
#             background: #f8f9fa;
#             border-radius: 5px;
#         }
        
#         .zone-metric-label {
#             font-size: 0.85em;
#             color: #666;
#             margin-bottom: 5px;
#         }
        
#         .zone-metric-value {
#             font-size: 1.3em;
#             font-weight: bold;
#             color: #667eea;
#         }
        
#         .footer {
#             padding: 30px;
#             text-align: center;
#             background: #2c3e50;
#             color: white;
#         }
#     </style>
# </head>
# <body>
#     <div class="container">
#         <div class="header">
#             <h1>🔍 Equipment Condition Analysis Report</h1>
#             <div class="timestamp">Generated: {timestamp}</div>
#         </div>
        
#         <div class="summary-cards">
#             <div class="card">
#                 <div class="card-title">Similarity Score</div>
#                 <div class="card-value">{similarity:.1%}</div>
#                 <div class="card-label">Overall Match</div>
#                 <span class="status-badge {status_class}">{status_text}</span>
#             </div>
            
#             <div class="card">
#                 <div class="card-title">Total Change</div>
#                 <div class="card-value">{change_percent:.1f}%</div>
#                 <div class="card-label">Pixel Difference</div>
#             </div>
            
#             <div class="card">
#                 <div class="card-title">Changed Regions</div>
#                 <div class="card-value">{regions}</div>
#                 <div class="card-label">Detected Areas</div>
#             </div>
            
#             <div class="card">
#                 <div class="card-title">Rust Change</div>
#                 <div class="card-value">{rust_delta:+.1f}%</div>
#                 <div class="card-label">Corrosion Delta</div>
#             </div>
            
#             <div class="card">
#                 <div class="card-title">New Cracks</div>
#                 <div class="card-value">{crack_delta}</div>
#                 <div class="card-label">Detected</div>
#             </div>
            
#             <div class="card">
#                 <div class="card-title">Brightness</div>
#                 <div class="card-value">{brightness_delta:+.0f}</div>
#                 <div class="card-label">Delta</div>
#             </div>
#         </div>
        
#         <div class="images-section">
#             <h2 class="section-title">Visual Analysis</h2>
#             <div class="images-grid">
#                 <div class="image-card">
#                     <img src="{comparison_path}" alt="Comparison">
#                     <div class="image-card-title">Before/After Comparison</div>
#                 </div>
#                 <div class="image-card">
#                     <img src="{heatmap_path}" alt="Heatmap">
#                     <div class="image-card-title">Change Heatmap</div>
#                 </div>
#                 <div class="image-card">
#                     <img src="{diff_mask_path}" alt="Diff Mask">
#                     <div class="image-card-title">Difference Mask</div>
#                 </div>
#                 <div class="image-card">
#                     <img src="{before_heatmap_path}" alt="Structure">
#                     <div class="image-card-title">Structure Analysis</div>
#                 </div>
#             </div>
#         </div>
        
#         <div class="zones-section">
#             <h2 class="section-title">Detailed Zone Analysis</h2>
#             {zones_html}
#         </div>
        
#         <div class="footer">
#             <p>Automated Image Comparison System v2.0</p>
#             <p style="margin-top: 10px; opacity: 0.7;">Powered by OpenCV & Advanced Computer Vision</p>
#         </div>
#     </div>
# </body>
# </html>
# """
        
#         # Determine status
#         change = self.results['change_percent']
#         if change > 20:
#             status_class = "status-critical"
#             status_text = "SIGNIFICANT CHANGE"
#         elif change > 10:
#             status_class = "status-moderate"
#             status_text = "MODERATE CHANGE"
#         else:
#             status_class = "status-minimal"
#             status_text = "MINIMAL CHANGE"
        
#         # Generate zones HTML
#         zones_html = ""
#         for zone, details in self.results.get('zone_details', {}).items():
#             sig_class = f"status-{details['significance'].lower()}"
            
#             zones_html += f"""
#             <div class="zone-item">
#                 <div class="zone-header">
#                     <div class="zone-name">📍 {zone.upper()}</div>
#                     <span class="status-badge {sig_class}">{details['significance']}</span>
#                 </div>
#                 <div class="zone-metrics">
#                     <div class="zone-metric">
#                         <div class="zone-metric-label">Severity</div>
#                         <div class="zone-metric-value">{details['severity']}/10</div>
#                     </div>
#                     <div class="zone-metric">
#                         <div class="zone-metric-label">Area</div>
#                         <div class="zone-metric-value">{details['area_percent']:.2f}%</div>
#                     </div>
#                     <div class="zone-metric">
#                         <div class="zone-metric-label">Rust Change</div>
#                         <div class="zone-metric-value">{details['rust_change']:+.1f}%</div>
#                     </div>
#                     <div class="zone-metric">
#                         <div class="zone-metric-label">Part</div>
#                         <div class="zone-metric-value" style="font-size: 0.9em;">{details['part_name']}</div>
#                     </div>
#                 </div>
#             </div>
#             """
        
#         if not zones_html:
#             zones_html = "<p style='text-align: center; color: #666;'>No significant zones detected</p>"
        
#         # Fill template
#         html = html_template.format(
#             timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             similarity=self.results['similarity'],
#             change_percent=self.results['change_percent'],
#             regions=self.results['regions'],
#             rust_delta=self.results['rust_delta_pct'],
#             crack_delta=self.results['crack_delta'],
#             brightness_delta=self.results['brightness_delta'],
#             status_class=status_class,
#             status_text=status_text,
#             comparison_path=os.path.basename(self.results.get('comparison_path', '')),
#             heatmap_path=os.path.basename(self.results['heatmap_path']),
#             diff_mask_path=os.path.basename(self.results['diff_mask_path']),
#             before_heatmap_path=os.path.basename(self.results['before_heatmap_path']),
#             zones_html=zones_html
#         )
        
#         with open(output_path, 'w') as f:
#             f.write(html)
        
#         print(f"✅ HTML report saved to: {output_path}")
#         return output_path
    
#     def create_json_report(self, output_path="report.json"):
#         """Save results as JSON for integration with other systems"""
        
#         report = {
#             "timestamp": datetime.now().isoformat(),
#             "files": {
#                 "before": self.before_path,
#                 "after": self.after_path
#             },
#             "metrics": self.results
#         }
        
#         with open(output_path, 'w') as f:
#             json.dump(report, f, indent=2)
        
#         print(f"✅ JSON report saved to: {output_path}")
#         return output_path