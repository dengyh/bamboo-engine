# -*- coding: utf-8 -*-

from django.db import connection
from django.test import TransactionTestCase

from pipeline.contrib.diagnostics.models import DiagnosticCase, DiagnosticEvent, DiagnosticOperationAudit


class DiagnosticsModelTestCase(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        super(DiagnosticsModelTestCase, cls).setUpClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(DiagnosticEvent)
            schema_editor.create_model(DiagnosticCase)
            schema_editor.create_model(DiagnosticOperationAudit)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(DiagnosticOperationAudit)
            schema_editor.delete_model(DiagnosticCase)
            schema_editor.delete_model(DiagnosticEvent)
        super(DiagnosticsModelTestCase, cls).tearDownClass()

    def test_create_diagnostic_event(self):
        event = DiagnosticEvent.objects.create(
            event_id="event-1",
            event_type=DiagnosticEvent.EVENT_TYPE_STUCK,
            source="zombie_doctor",
            pipeline_id="pipeline-1",
            node_id="node-1",
            process_id=1,
            status=DiagnosticEvent.STATUS_PENDING,
            detail={"reason": "stuck"},
        )

        loaded = DiagnosticEvent.objects.get(id=event.id)

        self.assertEqual(loaded.event_id, "event-1")
        self.assertEqual(loaded.event_type, DiagnosticEvent.EVENT_TYPE_STUCK)
        self.assertEqual(loaded.status, DiagnosticEvent.STATUS_PENDING)
        self.assertEqual(loaded.detail, {"reason": "stuck"})

    def test_create_diagnostic_case(self):
        event = DiagnosticEvent.objects.create(
            event_id="event-2",
            event_type=DiagnosticEvent.EVENT_TYPE_STUCK,
            source="zombie_doctor",
            pipeline_id="pipeline-2",
            node_id="node-2",
            process_id=2,
            status=DiagnosticEvent.STATUS_PROCESSING,
            detail={"reason": "stuck"},
        )
        case = DiagnosticCase.objects.create(
            case_id="case-1",
            event=event,
            pipeline_id="pipeline-2",
            node_id="node-2",
            process_id=2,
            status=DiagnosticCase.STATUS_OPEN,
            severity=DiagnosticCase.SEVERITY_WARNING,
            diagnosis={"matched": True},
            suggestion={"operation": "retry"},
        )

        loaded = DiagnosticCase.objects.get(id=case.id)

        self.assertEqual(loaded.case_id, "case-1")
        self.assertEqual(loaded.event_id, event.id)
        self.assertEqual(loaded.status, DiagnosticCase.STATUS_OPEN)
        self.assertEqual(loaded.severity, DiagnosticCase.SEVERITY_WARNING)
        self.assertEqual(loaded.diagnosis, {"matched": True})
        self.assertEqual(loaded.suggestion, {"operation": "retry"})

    def test_create_diagnostic_operation_audit(self):
        event = DiagnosticEvent.objects.create(
            event_id="event-3",
            event_type=DiagnosticEvent.EVENT_TYPE_STUCK,
            source="zombie_doctor",
            pipeline_id="pipeline-3",
            node_id="node-3",
            process_id=3,
            status=DiagnosticEvent.STATUS_PROCESSED,
            detail={"reason": "stuck"},
        )
        case = DiagnosticCase.objects.create(
            case_id="case-2",
            event=event,
            pipeline_id="pipeline-3",
            node_id="node-3",
            process_id=3,
            status=DiagnosticCase.STATUS_HANDLED,
            severity=DiagnosticCase.SEVERITY_CRITICAL,
            diagnosis={"matched": True},
            suggestion={"operation": "resume"},
        )
        audit = DiagnosticOperationAudit.objects.create(
            case=case,
            operator="admin",
            operation=DiagnosticOperationAudit.OPERATION_RESUME,
            status=DiagnosticOperationAudit.STATUS_SUCCESS,
            request={"dry_run": False},
            result={"ok": True},
            message="resume process",
        )

        loaded = DiagnosticOperationAudit.objects.get(id=audit.id)

        self.assertEqual(loaded.case_id, case.id)
        self.assertEqual(loaded.operator, "admin")
        self.assertEqual(loaded.operation, DiagnosticOperationAudit.OPERATION_RESUME)
        self.assertEqual(loaded.status, DiagnosticOperationAudit.STATUS_SUCCESS)
        self.assertEqual(loaded.request, {"dry_run": False})
        self.assertEqual(loaded.result, {"ok": True})
