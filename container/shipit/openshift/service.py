# -*- coding: utf-8 -*-

from __future__ import absolute_import
from collections import OrderedDict


import logging

logger = logging.getLogger(__name__)


class Service(object):

    def __init__(self, config=None, project_name=None):
        self.project_name = project_name
        self.config = config

    def get_template(self):
        return self._get_task_or_config(request_type="config")

    def get_task(self, service_names=None):
        return self._get_task_or_config(request_type="task")

    def _get_task_or_config(self, request_type="task"):
        templates = []
        for name, service in self.config.get('services', {}).items():
            if service.get('ports'):
                if request_type == "task":
                    templates.append(self._create_task(name, service))
                elif request_type=="config":
                    templates.append(self._create_template(name, service))
        return templates

    def _create_template(self, name, service):
        '''
        Generate an OpenShift service configuration.
        '''

        ports = self._get_ports(service)
        name = "%s-%s" % (self.project_name, name)
        labels = dict(
            app=self.project_name,
            service=name
        )

        template = dict(
            apiVersion="v1",
            kind="Service",
            metadata=dict(
                name=name,
                labels=labels.copy()
            ),
            spec=dict(
                selector=labels.copy(),
                ports=ports,
            )
        )

        return template

    def _create_task(self, name, service):
        '''
        Generates an Ansible playbook task.

        :param service:
        :return:
        '''

        ports = self._get_ports(service)
        name = "%s-%s" % (self.project_name, name)
        labels = dict(
            app=self.project_name,
            service=name
        )
        template = dict(
            oso_service=OrderedDict(
                project_name=self.project_name,
                service_name=name,
                labels=labels.copy(),
                ports=ports,
                selector=labels.copy()
            )
        )
        return template

    @staticmethod
    def _get_ports(service):
        # TODO - handle port ranges
        ports = []
        for port in service['ports']:
            if isinstance(port, str) and ':' in port:
                parts = port.split(':')
                ports.append(dict(port=int(parts[0]), targetPort=int(parts[1]), name='port_%s' % parts[0]))
            else:
                ports.append(dict(port=int(port), targetPort=int(port), name='port_%s' % port))
        return ports
