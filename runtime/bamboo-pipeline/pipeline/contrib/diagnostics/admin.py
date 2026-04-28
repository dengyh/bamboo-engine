# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.contrib import admin

from .models import DiagnosticCase, DiagnosticEvent, DiagnosticOperationAudit


@admin.register(DiagnosticEvent)
class DiagnosticEventAdmin(admin.ModelAdmin):
    list_display = ("event_id", "event_type", "source", "pipeline_id", "node_id", "process_id", "status", "created_at")
    search_fields = ("event_id", "pipeline_id", "node_id")
    list_filter = ("event_type", "source", "status")


@admin.register(DiagnosticCase)
class DiagnosticCaseAdmin(admin.ModelAdmin):
    list_display = ("case_id", "pipeline_id", "node_id", "process_id", "status", "severity", "created_at")
    search_fields = ("case_id", "pipeline_id", "node_id")
    list_filter = ("status", "severity")


@admin.register(DiagnosticOperationAudit)
class DiagnosticOperationAuditAdmin(admin.ModelAdmin):
    list_display = ("id", "case", "operator", "operation", "status", "created_at")
    search_fields = ("case__case_id", "operator")
    list_filter = ("operation", "status")
