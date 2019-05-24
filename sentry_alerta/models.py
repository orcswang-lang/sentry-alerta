"""
sentry_alerta.models
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 by Orcswang, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import json

import requests
from django import forms
from django.utils.html import escape
from sentry.plugins.bases.notify import NotifyPlugin
import sentry_alerta
import logging


class AlertaOptionsForm(forms.Form):
    endpoint = forms.CharField(help_text="Alerta Endpoint", required=True,
                               widget=forms.TextInput(attrs={'placeholder': 'alerta endpoint'}))
    alerta_key = forms.CharField(help_text="Alerta Authorization Key", required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'alerta authorization key'}))
    pool_code = forms.CharField(help_text="Alerta PoolCode", required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'alerta PoolCode'}))


class AlertaMessage(NotifyPlugin):
    author = 'OrcsWang'
    author_url = 'https://github.com/jay1412008/sentry-alerta'
    version = sentry_alerta.VERSION
    description = "Event notification to Alerta."
    resource_links = [
        ('Bug Tracker', 'https://github.com/jay1412008/sentry-alerta/issues'),
        ('Source', 'https://github.com/jay1412008/sentry-alerta'),
    ]
    LEVELS = {
        'ALERT': 'red',
        'ERROR': 'major',
        'WARNING': 'warning',
        'INFO': 'normal',
        'DEBUG': 'debug',
    }
    slug = 'alerta'
    title = 'Alerta'
    conf_title = title
    conf_key = 'alerta'
    project_conf_form = AlertaOptionsForm
    logger = logging.getLogger('sentry.plugins.alerta')

    def is_configured(self, project):
        return all((self.get_option('endpoint', project), self.get_option('alerta_key', project),
                    self.get_option('pool_code', project)))

    def notify_users(self, group, event):
        project = event.project
        level = group.get_level_display().upper()
        link = group.get_absolute_url().encode('utf-8')
        alerta_key = self.get_option('alerta_key', project)
        endpoint = self.get_option('endpoint', project)
        pool_code = self.get_option('pool_code', project)
        server_name = event.get_tag('server_name').encode('utf-8') if event.get_tag('server_name') else "sentry"
        try:
            exception = event.get_interfaces()['sentry.interfaces.Exception'].to_string(event)
            msg = exception.replace('  ', '&emsp;').replace('\n', '</br>')
        except KeyError:
            msg = event.error()

        data = {
            "resource": "sentry",
            "event": '{project_name}:{level}'.format(project_name=project.name.encode('utf-8'), level=level),
            "environment": "sentry",
            "severity": self.LEVELS.get(level, 'normal'),
            "status": "open",
            "service": ["sentry"],
            "group": pool_code.encode('utf-8'),
            "value": """##{project_name}@{server_name}:{level} {msg}> [view]({link})""".format(
                project_name=project.name.encode('utf-8'),
                level=level,
                msg=escape(msg).encode('utf-8'),
                server_name=server_name,
                link=escape(link).encode('utf-8'),
            ),
            "text": """##{project_name}@{server_name}:{level} {msg}> [view]({link})""".format(
                project_name=project.name.encode('utf-8'),
                level=level,
                msg=escape(msg).encode('utf-8'),
                server_name=server_name,
                link=escape(link).encode('utf-8'),
            ),
            "tags": ['project_name=' + project.name.encode('utf-8'), 'pool_code=' + pool_code.encode('utf-8'),
                     "sentry", "sentry-" + pool_code.encode('utf-8')],
            "origin": "sentry",
            "type": "sentry",
        }
        self.send_payload(endpoint=endpoint, key=alerta_key, data=data)

    def send_payload(self, endpoint, key, data):
        headers = {
            "Content-Type": "application/json",
            "CustomAuthorization": 'Key {key}'.format(key=key)
        }
        requests.request("POST", endpoint, data=json.dumps(data), headers=headers)
