---
title: TriCell: Building My Own Three-Cell Oxygen Analyzer
date: 2026-10-29
project: TriCell
excerpt: Turning retired JJ-CCR oxygen cells into a three-sensor analyzer, from breadboard testing to a printed enclosure.
draft: false
---

One of my latest projects is TriCell, a handheld oxygen analyzer I've been developing using three oxygen sensors from my JJ-CCR rebreather.

The idea came from wanting to make better use of my retired rebreather cells. Rather than relying on a single sensor, TriCell uses three independent readings, with the goal of comparing them through voting logic to identify a sensor that's drifting or producing an inconsistent result.

The electronics are built around an ESP32 microcontroller, an ADS1115 analog-to-digital converter, and a 3.5-inch color display. The interface is designed to show oxygen percentages from all three cells, along with the calculated maximum operating depth (MOD).

Bench testing has been encouraging. All three cells have produced stable readings close to 20.9% in ambient air. I've also been working through the challenges of battery power, display stability, sensor calibration, and averaging the readings.

On the mechanical side, I've been designing and 3D printing the housing and removable sensor cartridge. The goal is a compact, rechargeable analyzer with straightforward airflow across all three sensors.

TriCell is still a work in progress. The next stages involve refining the enclosure, improving the electronics, and eventually developing a custom circuit board. Proper validation will be necessary before it can be considered a reliable diving instrument.

This project has been a great opportunity to combine electronics, programming, 3D printing, and diving into something I designed from scratch.

More updates as TriCell develops.
