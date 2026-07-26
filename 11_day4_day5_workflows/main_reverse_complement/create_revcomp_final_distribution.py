#!/usr/bin/env python3
"""Create the final offline Plotly normal/revcomp distribution."""

import argparse
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


def read_summary(path: Path):
    summary = {}
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            key, value = line.split("\t", 1)
            summary[key] = value
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--direction-summary", required=True)
    parser.add_argument("--run-summary", required=True)
    parser.add_argument("--html-output", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    direction_path = Path(args.direction_summary).resolve()
    summary_path = Path(args.run_summary).resolve()
    html_path = Path(args.html_output).resolve()
    if html_path.exists() and not args.overwrite:
        raise FileExistsError(f"refusing to overwrite {html_path}")

    frame = pd.read_csv(direction_path, sep="\t")
    required = {
        "insert_id",
        "normal_reads",
        "revcomp_reads",
        "directional_reads",
        "normal_percent",
        "revcomp_percent",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(
            f"missing columns in {direction_path.name}: {sorted(missing)}"
        )
    if len(frame) != 1588:
        raise ValueError(f"expected 1588 inserts, found {len(frame)}")
    if frame["insert_id"].duplicated().any():
        raise ValueError("insert IDs are not unique")
    if not (
        frame["normal_reads"] + frame["revcomp_reads"]
        == frame["directional_reads"]
    ).all():
        raise ValueError("directional read totals are inconsistent")

    zero_zero_mask = (
        (frame["normal_reads"] == 0) & (frame["revcomp_reads"] == 0)
    )
    if not (zero_zero_mask == (frame["directional_reads"] == 0)).all():
        raise ValueError("zero-read classification is inconsistent")
    excluded_zero_zero = int(zero_zero_mask.sum())
    plot_frame = frame.loc[~zero_zero_mask].copy()

    plot_frame = plot_frame.sort_values(
        ["revcomp_percent", "insert_id"],
        ascending=[False, True],
        kind="stable",
    ).reset_index(drop=True)
    plot_frame["rank"] = plot_frame.index + 1
    summary = read_summary(summary_path)

    if summary["status"] != "PASS":
        raise ValueError(f"run status is {summary['status']}, expected PASS")
    normal_total = int(summary["normal_assigned_reads"])
    revcomp_total = int(summary["revcomp_assigned_reads"])
    assigned_total = int(summary["assigned_unique_best_reads"])
    source_total = int(summary["source_total_reads"])
    if normal_total + revcomp_total != assigned_total:
        raise ValueError("run summary orientation totals are inconsistent")
    if int(frame["directional_reads"].sum()) != assigned_total:
        raise ValueError("direction table does not reconcile to run summary")
    if int(plot_frame["directional_reads"].sum()) != assigned_total:
        raise ValueError("filtered plot data do not reconcile to run summary")

    customdata = plot_frame[
        ["insert_id", "normal_reads", "revcomp_reads", "directional_reads"]
    ]
    colors = {"Normal": "#1769aa", "Reverse-Komplement": "#d1495b"}
    figure = go.Figure()
    for series, column in (
        ("Normal", "normal_percent"),
        ("Reverse-Komplement", "revcomp_percent"),
    ):
        figure.add_trace(
            go.Scattergl(
                x=plot_frame["rank"],
                y=plot_frame[column],
                mode="lines",
                name=series,
                legendgroup=series,
                line={"color": colors[series], "width": 1.5},
                customdata=customdata,
                hovertemplate=(
                    "Rang: %{x}<br>"
                    "Insert: %{customdata[0]}<br>"
                    + series
                    + ": %{y:.2f} %<br>"
                    "Normal reads: %{customdata[1]:,}<br>"
                    "Reverse-Komplement reads: %{customdata[2]:,}<br>"
                    "Gerichtete Reads: %{customdata[3]:,}<extra></extra>"
                ),
            )
        )

    assigned_percent = 100.0 * assigned_total / source_total
    figure.update_xaxes(
        title_text=(
            "Insert-Rang mit mindestens einem gerichteten Read "
            "(absteigend nach Reverse-Komplement-%; "
            "Insert-ID im Tooltip)"
        ),
        showgrid=False,
        rangemode="tozero",
    )
    figure.update_yaxes(
        title_text="Anteil der gerichteten Reads (%)",
        range=[0, 100],
        dtick=10,
    )
    figure.update_layout(
        title=(
            "Normal-/Reverse-Komplement-Verteilung des finalen Main Runs"
            "<br><sup>Finaler Status PASS · "
            f"{source_total:,} Quellreads · "
            f"{assigned_total:,} eindeutig gerichtete Reads "
            f"({assigned_percent:.2f} % aller Quellreads) · "
            f"{excluded_zero_zero} Inserts mit 0/0 Reads ausgeblendet</sup>"
        ),
        template="plotly_white",
        hovermode="x unified",
        height=720,
        width=1400,
        margin={"l": 85, "r": 35, "t": 115, "b": 80},
        legend={
            "orientation": "h",
            "y": 1.03,
            "x": 0.5,
            "xanchor": "center",
        },
    )

    html_path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(
        html_path,
        include_plotlyjs=True,
        full_html=True,
        config={
            "displaylogo": False,
            "responsive": True,
            "scrollZoom": True,
            "toImageButtonOptions": {
                "format": "png",
                "filename": "revcomp_main_final_distribution",
                "scale": 2,
            },
        },
    )
    print(f"html_output\t{html_path}")
    print(f"source_inserts\t{len(frame)}")
    print(f"plotted_inserts\t{len(plot_frame)}")
    print(f"excluded_zero_zero_inserts\t{excluded_zero_zero}")
    print(f"source_reads\t{source_total}")
    print(f"assigned_reads\t{assigned_total}")
    print(f"assigned_percent\t{assigned_percent:.12f}")


if __name__ == "__main__":
    main()
