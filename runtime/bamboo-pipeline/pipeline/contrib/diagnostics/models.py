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

import ujson as json
from django.db import models
from django.utils.translation import ugettext_lazy as _


class JSONTextField(models.TextField):
    def get_prep_value(self, value):
        return json.dumps(value)

    def to_python(self, value):
        value = super(JSONTextField, self).to_python(value)
        if value is None or isinstance(value, (dict, list)):
            return value
        return json.loads(value)

    def from_db_value(self, value, expression, connection, context=None):
        return self.to_python(value)


class DiagnosticEvent(models.Model):
    EVENT_TYPE_STUCK = "stuck"
    EVENT_TYPE_EXCEPTION = "exception"

    EVENT_TYPE_CHOICES = (
        (EVENT_TYPE_STUCK, _("执行卡住")),
        (EVENT_TYPE_EXCEPTION, _("执行异常")),
    )

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_PROCESSED = "processed"
    STATUS_IGNORED = "ignored"

    STATUS_CHOICES = (
        (STATUS_PENDING, _("待处理")),
        (STATUS_PROCESSING, _("处理中")),
        (STATUS_PROCESSED, _("已处理")),
        (STATUS_IGNORED, _("已忽略")),
    )

    event_id = models.CharField(_("诊断事件ID"), max_length=64, unique=True)
    event_type = models.CharField(_("诊断事件类型"), max_length=32, choices=EVENT_TYPE_CHOICES, db_index=True)
    source = models.CharField(_("诊断来源"), max_length=64)
    pipeline_id = models.CharField(_("Pipeline ID"), max_length=64, db_index=True)
    node_id = models.CharField(_("节点ID"), max_length=64, blank=True, default="", db_index=True)
    process_id = models.IntegerField(_("进程ID"), null=True, blank=True, db_index=True)
    status = models.CharField(_("处理状态"), max_length=32, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    detail = JSONTextField(_("诊断详情"), default=dict)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)

    class Meta:
        app_label = "diagnostics"
        verbose_name = _("Pipeline诊断事件")
        verbose_name_plural = _("Pipeline诊断事件")
        ordering = ["-id"]
        index_together = (("pipeline_id", "node_id"), ("status", "created_at"))

    def __unicode__(self):
        return "{}_{}_{}".format(self.event_id, self.event_type, self.status)


class DiagnosticCase(models.Model):
    STATUS_OPEN = "open"
    STATUS_HANDLED = "handled"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = (
        (STATUS_OPEN, _("待治理")),
        (STATUS_HANDLED, _("已治理")),
        (STATUS_CLOSED, _("已关闭")),
    )

    SEVERITY_INFO = "info"
    SEVERITY_WARNING = "warning"
    SEVERITY_CRITICAL = "critical"

    SEVERITY_CHOICES = (
        (SEVERITY_INFO, _("提示")),
        (SEVERITY_WARNING, _("告警")),
        (SEVERITY_CRITICAL, _("严重")),
    )

    case_id = models.CharField(_("诊断案例ID"), max_length=64, unique=True)
    event = models.ForeignKey(DiagnosticEvent, verbose_name=_("诊断事件"), related_name="cases", on_delete=models.CASCADE)
    pipeline_id = models.CharField(_("Pipeline ID"), max_length=64, db_index=True)
    node_id = models.CharField(_("节点ID"), max_length=64, blank=True, default="", db_index=True)
    process_id = models.IntegerField(_("进程ID"), null=True, blank=True, db_index=True)
    status = models.CharField(_("治理状态"), max_length=32, choices=STATUS_CHOICES, default=STATUS_OPEN, db_index=True)
    severity = models.CharField(_("严重级别"), max_length=32, choices=SEVERITY_CHOICES, default=SEVERITY_INFO, db_index=True)
    diagnosis = JSONTextField(_("诊断结论"), default=dict)
    suggestion = JSONTextField(_("治理建议"), default=dict)
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("更新时间"), auto_now=True)

    class Meta:
        app_label = "diagnostics"
        verbose_name = _("Pipeline诊断案例")
        verbose_name_plural = _("Pipeline诊断案例")
        ordering = ["-id"]
        index_together = (("pipeline_id", "node_id"), ("status", "severity"))

    def __unicode__(self):
        return "{}_{}_{}".format(self.case_id, self.status, self.severity)


class DiagnosticOperationAudit(models.Model):
    OPERATION_RETRY = "retry"
    OPERATION_RESUME = "resume"
    OPERATION_IGNORE = "ignore"

    OPERATION_CHOICES = (
        (OPERATION_RETRY, _("重试")),
        (OPERATION_RESUME, _("恢复")),
        (OPERATION_IGNORE, _("忽略")),
    )

    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = (
        (STATUS_SUCCESS, _("成功")),
        (STATUS_FAILED, _("失败")),
    )

    case = models.ForeignKey(
        DiagnosticCase, verbose_name=_("诊断案例"), related_name="operation_audits", on_delete=models.CASCADE
    )
    operator = models.CharField(_("操作人"), max_length=64)
    operation = models.CharField(_("操作类型"), max_length=32, choices=OPERATION_CHOICES, db_index=True)
    status = models.CharField(_("操作状态"), max_length=32, choices=STATUS_CHOICES, db_index=True)
    request = JSONTextField(_("操作请求"), default=dict)
    result = JSONTextField(_("操作结果"), default=dict)
    message = models.TextField(_("操作信息"), blank=True, default="")
    created_at = models.DateTimeField(_("创建时间"), auto_now_add=True, db_index=True)

    class Meta:
        app_label = "diagnostics"
        verbose_name = _("Pipeline诊断操作审计")
        verbose_name_plural = _("Pipeline诊断操作审计")
        ordering = ["-id"]
        index_together = (("operator", "operation"), ("status", "created_at"))

    def __unicode__(self):
        return "{}_{}_{}".format(self.case_id, self.operation, self.status)
