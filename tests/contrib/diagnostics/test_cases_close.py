# -*- coding: utf-8 -*-

from pipeline.contrib.diagnostics import cases
from pipeline.contrib.diagnostics.models import DiagnosticCase
from tests.contrib.diagnostics.base import DiagnosticsTestCase


class CloseStaleCasesTest(DiagnosticsTestCase):
    def _open_case(self, root, node="n1", stuck_type="stalled_no_progress"):
        return DiagnosticCase.objects.create(
            root_pipeline_id=root,
            node_id=node,
            stuck_type=stuck_type,
            status=DiagnosticCase.STATUS_OPEN,
        )

    def test_close_when_root_not_in_active_set(self):
        self._open_case("root-gone")
        closed = cases.close_stale_cases(active_root_ids=set())
        self.assertEqual(closed, 1)
        self.assertEqual(
            DiagnosticCase.objects.get(root_pipeline_id="root-gone").status,
            DiagnosticCase.STATUS_RESOLVED,
        )

    def test_keep_when_root_still_active(self):
        self._open_case("root-live")
        closed = cases.close_stale_cases(active_root_ids={"root-live"})
        self.assertEqual(closed, 0)
        self.assertEqual(
            DiagnosticCase.objects.get(root_pipeline_id="root-live").status,
            DiagnosticCase.STATUS_OPEN,
        )

    def test_already_resolved_not_recounted(self):
        DiagnosticCase.objects.create(
            root_pipeline_id="root-resolved", node_id="n1", stuck_type="x",
            status=DiagnosticCase.STATUS_RESOLVED,
        )
        closed = cases.close_stale_cases(active_root_ids=set())
        self.assertEqual(closed, 0)
