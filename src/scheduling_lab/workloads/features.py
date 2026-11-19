"""
Pre-execution feature extraction for ML policy recommendation.
Strictly extracts features observable BEFORE scheduling execution begins.
"""

from __future__ import annotations

from typing import Any, Dict, List
import numpy as np

from scheduling_lab.core.models import Process


FEATURE_NAMES = [
    "process_count",
    "mean_initial_burst",
    "std_initial_burst",
    "burst_cv",
    "mean_io_wait",
    "multi_burst_ratio",
    "cpu_to_io_ratio",
    "mean_arrival_gap",
    "std_arrival_gap",
    "short_burst_ratio",
    "priority_std",
    "arrival_burstiness",
]


class PreExecutionFeatureExtractor:
    """Extracts leakage-free statistical features from initial process attributes."""

    @classmethod
    def extract_features(cls, processes: List[Process]) -> Dict[str, float]:
        if not processes:
            raise ValueError("Cannot extract features from empty process list")

        count = len(processes)

        # 1. Initial burst statistics
        initial_bursts = [p.cpu_bursts[0] for p in processes]
        mean_init = float(np.mean(initial_bursts))
        std_init = float(np.std(initial_bursts))

        # 2. All bursts coefficient of variation
        all_cpu_bursts: List[int] = []
        all_io_bursts: List[int] = []
        multi_burst_count = 0

        for p in processes:
            all_cpu_bursts.extend(p.cpu_bursts)
            all_io_bursts.extend(p.io_bursts)
            if len(p.cpu_bursts) > 1:
                multi_burst_count += 1

        all_cpu_mean = float(np.mean(all_cpu_bursts))
        all_cpu_std = float(np.std(all_cpu_bursts))
        burst_cv = (all_cpu_std / all_cpu_mean) if all_cpu_mean > 0 else 0.0

        # 3. IO waits
        mean_io = float(np.mean(all_io_bursts)) if all_io_bursts else 0.0
        multi_burst_ratio = multi_burst_count / count

        # 4. CPU to IO ratio
        total_cpu = sum(p.total_expected_cpu for p in processes)
        total_io = sum(p.total_expected_io for p in processes)
        cpu_to_io_ratio = float(total_cpu / (total_io + 1.0))

        # 5. Arrival gap statistics
        arrival_times = sorted([p.arrival_time for p in processes])
        if count > 1:
            gaps = [arrival_times[i] - arrival_times[i - 1] for i in range(1, count)]
            mean_gap = float(np.mean(gaps))
            std_gap = float(np.std(gaps))
        else:
            mean_gap = 0.0
            std_gap = 0.0

        # 6. Short burst ratio (burst <= 3)
        short_count = sum(1 for b in all_cpu_bursts if b <= 3)
        short_burst_ratio = short_count / len(all_cpu_bursts) if all_cpu_bursts else 0.0

        # 7. Priority standard deviation
        priorities = [p.priority for p in processes]
        priority_std = float(np.std(priorities))

        # 8. Arrival burstiness (max arrivals within any 5-unit time sliding window / total)
        max_in_window = 1
        for t in arrival_times:
            in_win = sum(1 for a in arrival_times if t <= a < t + 5)
            if in_win > max_in_window:
                max_in_window = in_win
        arrival_burstiness = float(max_in_window / count)

        features: Dict[str, float] = {
            "process_count": float(count),
            "mean_initial_burst": round(mean_init, 4),
            "std_initial_burst": round(std_init, 4),
            "burst_cv": round(burst_cv, 4),
            "mean_io_wait": round(mean_io, 4),
            "multi_burst_ratio": round(multi_burst_ratio, 4),
            "cpu_to_io_ratio": round(cpu_to_io_ratio, 4),
            "mean_arrival_gap": round(mean_gap, 4),
            "std_arrival_gap": round(std_gap, 4),
            "short_burst_ratio": round(short_burst_ratio, 4),
            "priority_std": round(priority_std, 4),
            "arrival_burstiness": round(arrival_burstiness, 4),
        }
        return features

    @classmethod
    def extract_vector(cls, processes: List[Process]) -> List[float]:
        feat_dict = cls.extract_features(processes)
        return [feat_dict[name] for name in FEATURE_NAMES]
