#!/usr/bin/env python3
import argparse
import json
from dnd_game.narrative_diagnostics import (
    generate_conflict_timeline,
    generate_arc_map,
    generate_emotion_heatmap,
    generate_diagnostic_report
)

def main():
    parser = argparse.ArgumentParser(description="Generate narrative diagnostics for a campaign.")
    parser.add_argument('--campaign_id', required=True, help='Campaign ID')
    parser.add_argument('--output', required=True, help='Output file (JSON)')
    parser.add_argument('--report_type', default='full', choices=['full', 'timeline', 'arcs', 'heatmap'], help='Type of report to generate')
    args = parser.parse_args()

    if args.report_type == 'timeline':
        data = generate_conflict_timeline(args.campaign_id)
    elif args.report_type == 'arcs':
        data = generate_arc_map(args.campaign_id)
    elif args.report_type == 'heatmap':
        data = generate_emotion_heatmap(args.campaign_id)
    else:
        data = generate_diagnostic_report(args.campaign_id)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Diagnostic report saved to {args.output}")

if __name__ == '__main__':
    main() 