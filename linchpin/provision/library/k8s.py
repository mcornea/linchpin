#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2018, Chris Houseknecht <@chouseknecht>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''

module: k8s

short_description: Manage Kubernetes (K8s) objects

version_added: "2.6"

author:
    - "Chris Houseknecht (@chouseknecht)"
    - "Fabian von Feilitzsch (@fabianvf)"

description:
  - Use the OpenShift Python client to perform CRUD operations on K8s objects.
  - Pass the object definition from a source file or inline. See examples for reading
    files and using Jinja templates or vault-encrypted files.
  - Access to the full range of K8s APIs.
  - Use the M(k8s_facts) module to obtain a list of items about an object of type C(kind)
  - Authenticate using either a config file, certificates, password or token.
  - Supports check mode.

extends_documentation_fragment:
  - k8s_state_options
  - k8s_name_options
  - k8s_resource_options
  - k8s_auth_options

options:
  merge_type:
    description:
    - Whether to override the default patch merge approach with a specific type. By default, the strategic
      merge will typically be used.
    - For example, Custom Resource Definitions typically aren't updatable by the usual strategic merge. You may
      want to use C(merge) if you see "strategic merge patch format is not supported"
    - See U(https://kubernetes.io/docs/tasks/run-application/update-api-object-kubectl-patch/#use-a-json-merge-patch-to-update-a-deployment)
    - Requires openshift >= 0.6.2
    - If more than one merge_type is given, the merge_types will be tried in order
    - If openshift >= 0.6.2, this defaults to C(['strategic-merge', 'merge']), which is ideal for using the same parameters
      on resource kinds that combine Custom Resources and built-in resources. For openshift < 0.6.2, the default
      is simply C(strategic-merge).
    choices:
    - json
    - merge
    - strategic-merge
    type: list
    version_added: "2.7"
  wait:
    description:
    - Whether to wait for certain resource kinds to end up in the desired state. By default the module exits once Kubernetes has
      received the request
    - Implemented for C(state=present) for C(Deployment), C(DaemonSet) and C(Pod), and for C(state=absent) for all resource kinds.
    - For resource kinds without an implementation, C(wait) returns immediately.
    default: no
    type: bool
    version_added: "2.8"
  wait_timeout:
    description:
    - How long in seconds to wait for the resource to end up in the desired state. Ignored if C(wait) is not set.
    default: 120
    version_added: "2.8"
  validate:
    description:
      - how (if at all) to validate the resource definition against the kubernetes schema.
        Requires the kubernetes-validate python module
    suboptions:
      fail_on_error:
        description: whether to fail on validation errors.
        required: yes
        type: bool
      version:
        description: version of Kubernetes to validate against. defaults to Kubernetes server version
      strict:
        description: whether to fail when passing unexpected properties
        default: no
        type: bool
    version_added: "2.8"

requirements:
  - "python >= 2.7"
  - "openshift >= 0.6"
  - "PyYAML >= 3.11"
'''

EXAMPLES = '''
- name: Create a k8s namespace
  k8s:
    name: testing
    api_version: v1
    kind: Namespace
    state: present

- name: Create a Service object from an inline definition
  k8s:
    state: present
    definition:
      apiVersion: v1
      kind: Service
      metadata:
        name: web
        namespace: testing
        labels:
          app: galaxy
          service: web
      spec:
        selector:
          app: galaxy
          service: web
        ports:
        - protocol: TCP
          targetPort: 8000
          name: port-8000-tcp
          port: 8000

- name: Create a Service object by reading the definition from a file
  k8s:
    state: present
    src: /testing/service.yml

- name: Remove an existing Service object
  k8s:
    state: absent
    api_version: v1
    kind: Service
    namespace: testing
    name: web

# Passing the object definition from a file

- name: Create a Deployment by reading the definition from a local file
  k8s:
    state: present
    src: /testing/deployment.yml

- name: >-
    Read definition file from the Ansible controller file system.
    If the definition file has been encrypted with Ansible Vault it will automatically be decrypted.
  k8s:
    state: present
    definition: "{{ lookup('file', '/testing/deployment.yml') }}"

- name: Read definition file from the Ansible controller file system after Jinja templating
  k8s:
    state: present
    definition: "{{ lookup('template', '/testing/deployment.yml') }}"

- name: fail on validation errors
  k8s:
    state: present
    definition: "{{ lookup('template', '/testing/deployment.yml') }}"
    validate:
      fail_on_error: yes

- name: warn on validation errors, check for unexpected properties
  k8s:
    state: present
    definition: "{{ lookup('template', '/testing/deployment.yml') }}"
    validate:
      fail_on_error: no
      strict: yes
'''

RETURN = '''
result:
  description:
  - The created, patched, or otherwise present object. Will be empty in the case of a deletion.
  returned: success
  type: complex
  contains:
     api_version:
       description: The versioned schema of this representation of an object.
       returned: success
       type: str
     kind:
       description: Represents the REST resource this object represents.
       returned: success
       type: str
     metadata:
       description: Standard object metadata. Includes name, namespace, annotations, labels, etc.
       returned: success
       type: complex
     spec:
       description: Specific attributes of the object. Will vary based on the I(api_version) and I(kind).
       returned: success
       type: complex
     status:
       description: Current status details for the object.
       returned: success
       type: complex
     items:
       description: Returned only when multiple yaml documents are passed to src or resource_definition
       returned: when resource_definition or src contains list of objects
       type: list
     duration:
       description: elapsed time of task in seconds
       returned: when C(wait) is true
       type: int
       sample: 48
'''

from ansible.module_utils.k8s.raw import KubernetesRawModule


def main():
    KubernetesRawModule().execute_module()


if __name__ == '__main__':
    main()