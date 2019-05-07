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

from __future__ import print_function

from gearman import GearmanAdminClient as AdminClient

from service import Service, Server


class AdminService(Service):

    def __init__(self):
        self.client = AdminClient(Server.hosts)
        self.server = self.client.ping_server()
        self.status = self.client.get_status()
        self.version = self.client.get_version()
        self.workers = self.client.get_workers()

    def pretty_print(self):
        print("-" * 40)
        print("Server alive {}".format(self.version))
        print("It took {}s to pingback".format(self.server))
        print("-" * 40)
        print("Tasks:")
        for s in self.status:
            func = s.get("task")
            workers = s.get("workers")
            running = s.get("running")
            queued = s.get("queued")
            print("=> Task func name: {}".format(func))
            print("   Status (q/r/w): {}/{}/{}".format(queued, running, workers))
        print("-" * 40)
        if len(self.workers) > 1:
            print("Workers:")
            for w in self.workers:
                worker = w.get("client_id")
                if worker == "-" or len(worker) == 0:
                    continue
                ipaddr = w.get("ip")
                tasks = w.get("tasks")
                print("=> Worker ID: {}".format(worker))
                print("   Worker IP: {}".format(ipaddr))
                if len(tasks) >= 1:
                    print("   Installed: {}".format(", ".join(tasks)))
                else:
                    print("   No tasks installed...")
        else:
            print("No workers")
        print("-" * 40)

    @classmethod
    def run(cls, *args):
        c = cls()
        c.pretty_print()
