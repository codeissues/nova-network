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

from gearman import GearmanClient

from encoder import Encoder
from service import Service, Server


class Client(GearmanClient):

    data_encoder = Encoder


class ClientService(Service):

    client, job = None, None

    def __init__(self, data):
        if not isinstance(data, (str, unicode)):
            raise ValueError("Unexpected value for argument 'data'")
        try:
            task, nvs = data.split("=")
        except Exception as e:
            raise ValueError("Unexpected format for argument 'data'")
        if task not in {self.WORKx01_MODE, self.WORKx16_MODE, self.WORKx24_MODE,
                        self.WORKx47_MODE, self.ANALYZE_MODE}:
            raise ValueError("Unsupported task: {}".format(task))
        self.task_name = task
        self.nvs = nvs
        self.prepare()

    def prepare(self):
        self.client = Client(Server.hosts)
        self.request = {
            "nvs": self.nvs,
            "fps": 16,
        }

    def start(self):
        self.job = self.client.submit_job(self.task_name, self.request)
        print self.job

    @classmethod
    def run(cls, *args):
        c = cls(*args)
        c.start()
