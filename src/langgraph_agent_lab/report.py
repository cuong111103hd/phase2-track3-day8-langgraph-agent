"""Reporting utilities."""

from __future__ import annotations

import os
from typing import Any

from .metrics import MetricsReport


def generate_markdown_report(report: MetricsReport) -> str:
    """Convert MetricsReport object to Markdown string."""
    md = f"# Day 08 Lab Report - Automated Summary\n\n"
    md += f"## Metrics Summary\n"
    md += f"- **Total Scenarios**: {report.total_scenarios}\n"
    md += f"- **Success Rate**: {report.success_rate:.2%}\n"
    md += f"- **Avg Nodes Visited**: {report.avg_nodes_visited:.2f}\n"
    md += f"- **Total Retries**: {report.total_retries}\n"
    md += f"- **Total Interrupts**: {report.total_interrupts}\n\n"
    
    md += "## Scenario Details\n"
    md += "| Scenario | Success | Expected | Actual | Nodes | Retries |\n"
    md += "|---|---|---|---|---:|---:|\n"
    for m in report.scenario_metrics:
        success_icon = "✅" if m.success else "❌"
        md += f"| {m.scenario_id} | {success_icon} | {m.expected_route} | {m.actual_route} | {m.nodes_visited} | {m.retry_count} |\n"
    
    return md


def write_report(report: Any, path: str):
    """Write the report to a file, converting to string if needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    if isinstance(report, MetricsReport):
        content = generate_markdown_report(report)
    else:
        content = str(report)
        
    with open(path, "w") as f:
        f.write(content)
