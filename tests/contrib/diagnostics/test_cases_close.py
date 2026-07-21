# -*- coding: utf-8 -*-

from datetime import timedelta

from django.utils import timezone

from pipeline.contrib.diagnostics import cases
from pipeline.contrib.diagnostics.models import DiagnosticCase
from pipeline.eri.models import Process
from tests.contrib.diagnostics.base import DiagnosticsTestCase


class CloseStaleCasesTest(DiagnosticsTestCase):
    def setUp(self):
        super(CloseStaleCasesTest, self).setUp()
        self.process_ids = []

    def tearDown(self):
        Process.objects.filter(id__in=self.process_ids).delete()
        super(CloseStaleCasesTest, self).tearDown()

    def _proc(self, root, beat_delta):
        p = Process.objects.create(
            root_pipeline_id=root, current_node_id="n1", destination_id="",
            priority=1, queue="diagnostics", pipeline_stack="[]",
        )
        self.process_ids.append(p.id)
        Process.objects.filter(id=p.id).update(
            last_heartbeat=timezone.now() - timedelta(seconds=beat_delta)
        )
        return p

    def _open_case(self, root):
        return DiagnosticCase.objects.create(
            root_pipeline_id=root, node_id="n1", stuck_type="stalled_no_progress",
            status=DiagnosticCase.STATUS_OPEN,
        )

    def test_resolve_when_root_recovered(self):
        self._proc("root-recovered", beat_delta=5)
        self._open_case("root-recovered")
        self.assertEqual(cases.close_stale_cases(threshold_seconds=1800), 1)
        self.assertEqual(
            DiagnosticCase.objects.get(root_pipeline_id="root-recovered").status,
            DiagnosticCase.STATUS_RESOLVED,
        )

    def test_resolve_when_root_has_no_live_process(self):
        self._open_case("root-finished")
        self.assertEqual(cases.close_stale_cases(threshold_seconds=1800), 1)
        self.assertEqual(
            DiagnosticCase.objects.get(root_pipeline_id="root-finished").status,
            DiagnosticCase.STATUS_RESOLVED,
        )

    def test_keep_when_root_still_stalled(self):
        self._proc("root-stuck", beat_delta=3600)
        self._open_case("root-stuck")
        self.assertEqual(cases.close_stale_cases(threshold_seconds=1800), 0)
        self.assertEqual(
            DiagnosticCase.objects.get(root_pipeline_id="root-stuck").status,
            DiagnosticCase.STATUS_OPEN,
        )

    def test_already_resolved_not_recounted(self):
        DiagnosticCase.objects.create(
            root_pipeline_id="root-x", node_id="n1", stuck_type="x",
            status=DiagnosticCase.STATUS_RESOLVED,
        )
        self.assertEqual(cases.close_stale_cases(threshold_seconds=1800), 0)
