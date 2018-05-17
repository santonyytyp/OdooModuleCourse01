# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, models


class ReportSession(models.AbstractModel):
    _name = "report.openacademy.report_session"

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env["report"]
        report = report_obj._get_report_from_name("openacademy.report_session")
        docargs = {
            "doc_ids": self._ids,
            "doc_model": report.model,
            "docs": self,
	    "other_variable": 'other value',
        }
        return report_obj.render("openacademy.report_session", docargs)
