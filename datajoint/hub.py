import re
import requests
from requests.adapters import HTTPAdapter
from datajoint.errors import DataJointError

HUB_PROTOCOL = 'hub://'
REQUEST_PROTOCOL = 'https://'
API_ROUTE = '/api'
API_TARGETS = dict(GET_DB_FQDN='/v0.000/get_database_fqdn')

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))


def get_host(host):
    hub_path = re.findall('/[:._\-a-zA-Z0-9]+', host)
    if re.match(HUB_PROTOCOL, host) and len(hub_path) > 2:
        try:
            resp = session.post('{}{}{}{}'.format(
                REQUEST_PROTOCOL, hub_path[0][1:], API_ROUTE, API_TARGETS['GET_DB_FQDN']),
                data={'org_name': hub_path[1][1:], 'project_name': hub_path[2][1:]},
                timeout=10)
            if resp.status_code == 200:
                return resp.json()['database.host']
            elif resp.status_code == 404:
                raise DataJointError(
                    'DataJoint Hub database resource `{}/{}/{}` not found.'.format(
                    hub_path[0][1:], hub_path[1][1:], hub_path[2][1:]))
            elif resp.status_code == 501:
                raise DataJointError(
                    'DataJoint Hub endpoint `{}{}{}{}` unavailable.'.format(
                    REQUEST_PROTOCOL, hub_path[0][1:], API_ROUTE, API_TARGETS['GET_DB_FQDN']))
        except requests.exceptions.SSLError:
            raise DataJointError(
                'TLS security violation on DataJoint Hub target `{}{}{}`.'.format(
                REQUEST_PROTOCOL, hub_path[0][1:], API_ROUTE))
        except requests.exceptions.ConnectionError:
            raise DataJointError(
                'Unable to reach DataJoint Hub target `{}{}{}`.'.format(
                REQUEST_PROTOCOL, hub_path[0][1:], API_ROUTE))
    elif not re.match('.*/', host):
        return host
    else:
        raise DataJointError('Malformed database host `{}`.'.format(host))
