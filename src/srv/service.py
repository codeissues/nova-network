# Copyright 2017 Alexandru Catrina
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import environ


NOVA_SERVERS = "NOVA_SERVERS"
NOVA_PATH = "NOVA_PATH"
NOVA_DB = "NOVA_DB"


def get_servers(default=["localhost:4730"]):
    servers = environ.get(NOVA_SERVERS)
    if not isinstance(servers, (str, unicode)):
        return default
    srv_list = servers.split(",")
    if len(srv_list) == 0:
        raise ValueError("Nova servers incorrect format")
    return srv_list


def get_nova_attr(attr):
    value = environ.get(attr)
    if not isinstance(value, (str, unicode)):
        raise ValueError("Nova {} is not in PATH".format(attr))
    if len(value) == 0:
        raise ValueError("Nova {} incorrect format".format(attr))
    return value


class Server(object):

    hosts = get_servers()


class Service(object):

    TASK_FAILED = "TASK_FAILED"
    TASK_FINISH = "TASK_FINISH"

    WORKx01_MODE = "work@1"
    WORKx16_MODE = "work@16"
    WORKx24_MODE = "work@24"
    WORKx47_MODE = "work@47"
    ANALYZE_MODE = "analyze"

    app_bin = get_nova_attr(NOVA_PATH)
    app_db = get_nova_attr(NOVA_DB)

    @classmethod
    def run(cls, *args):
        raise NotImplemented("Method not implemented")

    def func_work_fps_mode(self, fps, *args):
        raise NotImplemented("Method not implemented")

    def func_analyze_mode(self, *args):
        raise NotImplemented("Method not implemented")
