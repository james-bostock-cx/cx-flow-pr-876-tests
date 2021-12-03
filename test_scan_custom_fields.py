import inspect
import json
import pathlib
import random
import string
import subprocess
import unittest
import yaml

from CheckmarxPythonSDK.CxRestAPISDK import ProjectsAPI
from CheckmarxPythonSDK.CxRestAPISDK import ScansAPI
from CheckmarxPythonSDK.CxRestAPISDK import TeamAPI
from CheckmarxPythonSDK.CxRestAPISDK.sast.projects.dto.customFields.CxCustomField import CxCustomField

class Config:

    def __init__(self, filename):

        with open(filename, 'r') as f:
            self.data = yaml.load(f, Loader=yaml.Loader)

    def print_cx_flow_output(self):

        return self.data.get('print-cx-flow-output', False)

    def update_config(self, config):

        config['checkmarx']['base-url'] = self.data['checkmarx']['base-url']
        config['checkmarx']['username'] = self.data['checkmarx']['username']
        config['checkmarx']['password'] = self.data['checkmarx']['password']

        return config


def run_cxflow(cxflow_version, config, project_name, extra_args=[], print_output=False):
    """Runs CxFlow"""

    print(f'Running CxFlow version {cxflow_version}')

    with open('application.yml', 'w') as f:
        f.write(yaml.dump(config, default_flow_style=False))

    args = [
        'java',
        '-jar',
        f'cx-flow-{cxflow_version}.jar',
        '--scan',
        f'--cx-project={project_name}'
    ]

    for extra_arg in extra_args:
        args.append(extra_arg)

    print(f'Command: {" ".join(args)}')
    proc = subprocess.run(args, capture_output=True)
    if print_output:
        print(f'stdout: {proc.stdout.decode("UTF-8")}')
        print(f'stderr: {proc.stderr.decode("UTF-8")}')
    return proc.returncode


class TestScanCustomFields(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestScanCustomFields, self).__init__(*args, **kwargs)
        self.config = Config('config.yml')
        self.base_cx_flow_config = {
            'cx-flow': {
                'bug-tracker': 'WAIT',
                'bug-tracker-impl': ['Csv', 'Jira']
            },
            'logging': {
                'file': {
                    'name': 'cx-flow.log'}
                ,
                'level': {
                    'com': {
                        'checkmarx': {
                            'flow': 'DEBUG',
                            'sdk': 'DEBUG'
                        }
                    }
                }
            },
            'checkmarx': {
                'version': 9.2,
                'client-secret': '014DF517-39D1-4453-B7B3-9930C563627C',
                'url': '${checkmarx.base-url}/cxrestapi',
                'multi-tentant': False,
                'incremental': True,
                'scan-preset': 'Checkmarx Default',
                'configuration': 'Default Configuration',
                'team': '/CxServer',
                'portal-url': '${checkmarx.base-url}/cxwebinterface/Portal/CxWebService.asmx',
                'sdk-url': '${checkmarx.base-url}/cxwebinterface/SDK/CxSDKWebService.asmx',
                'portal-wsdl': '${checkmarx.base-url}/Portal/CxWebService.asmx?wsdl',
                'sdk-wsdl': '${checkmarx.base-url}/SDK/CxSDKWebService.asmx?wsdl'
            }
        }

        self.projects_api = ProjectsAPI()
        self.scans_api = ScansAPI()
        self.team_api = TeamAPI()

    def setUp(self):

        self.cx_flow_config = self.config.update_config(self.base_cx_flow_config)
        self.project_name = self.random_string(10)
        self.project_id = self.create_project(self.project_name, '/CxServer')

    def tearDown(self):

        print(f'Deleting project {self.project_id}')
        self.projects_api.delete_project_by_id(self.project_id)

        cxConfig = pathlib.Path("cx.config")
        if cxConfig.exists():
            print(f'Deleting {cxConfig}')
            cxConfig.unlink()

    def test_cmdline(self):

        self.cmdline_common()

    def cmdline_common(self):

        extra_args = ['--f=.', '--app=App']
        expected = {}
        expected[self.random_string(5)] = self.random_string(5)
        expected[self.random_string(5)] = self.random_string(5)
        for custom_field in expected:
            extra_args.append(f'--scan-custom-field={custom_field}:{expected[custom_field]}')

        self.common(extra_args, expected)

    def test_config_as_code(self):

        self.config_as_code_common()

    def config_as_code_common(self):

        extra_args = ['--f=.', '--app=App']
        config = {
            'version': 1.0,
            'scanCustomFields': {
            }
        }
        tmp = []
        expected = {}
        expected[self.random_string(5)] = self.random_string(5)
        expected[self.random_string(5)] = self.random_string(5)
        for custom_field in expected:
            config['scanCustomFields'][custom_field] = expected[custom_field]

        with open('cx.config', 'w') as f:
            json.dump(config, f)
        print(f'cx.config: {json.dumps(config, indent="  ")}')

        self.common(extra_args, expected)

    def common(self, extra_args, expected):

        print(f'expected: {expected}')
        self.assertEqual(0, run_cxflow(self.config.data['cx-flow']['version'],
                                       self.cx_flow_config,
                                       self.project_name,
                                       extra_args,
                                       self.config.print_cx_flow_output()))
        scans = self.scans_api.get_all_scans_for_project(self.project_id,
                                                         7, 1,
                                                         api_version="1.2")
        scan = scans[0]
        print(f'actual: {scan.custom_fields}')
        self.assertEqual(expected, scan.custom_fields)

    def create_project(self, project_name, team_name):

        print(f'Creating project {project_name} (under {team_name})')
        team_id = self.team_api.get_team_id_by_team_full_name(team_name)
        resp = self.projects_api.create_project_with_default_configuration(project_name, team_id)
        project_id = resp.id
        resp = self.projects_api.update_project_by_id(project_id,
                                                      project_name,
                                                      team_id)
        return project_id

    def random_string(self, length):

        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def get_project(self, project_name):

        return self.projects_api.get_project_id_by_project_name_and_team_full_name(project_name, self.cx_flow_config['checkmarx']['team'])


if __name__ == '__main__':
    unittest.main()
