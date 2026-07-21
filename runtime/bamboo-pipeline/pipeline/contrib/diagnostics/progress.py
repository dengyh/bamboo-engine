# -*- coding: utf-8 -*-

from datetime import timedelta

from django.db.models import Max
from django.utils import timezone

from pipeline.eri.models import Process


def stall_cutoff(threshold_seconds, now=None):
    now = now or timezone.now()
    return now - timedelta(seconds=threshold_seconds)


def stalled_root_candidates(threshold_seconds, batch, now=None):
    """root 级 Max(last_heartbeat) 超阈值的存活流程，按最久静默升序。"""
    cutoff = stall_cutoff(threshold_seconds, now=now)
    rows = (
        Process.objects.filter(dead=False)
        .values("root_pipeline_id")
        .annotate(latest=Max("last_heartbeat"))
        .filter(latest__lt=cutoff)
        .order_by("latest")[:batch]
    )
    return [(row["root_pipeline_id"], row["latest"]) for row in rows]


def root_last_progress(root_pipeline_id):
    return (
        Process.objects.filter(root_pipeline_id=root_pipeline_id, dead=False)
        .aggregate(latest=Max("last_heartbeat"))
        .get("latest")
    )
