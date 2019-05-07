#!/usr/bin/env python
#
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

from sys import argv

from srv.admin import AdminService
from srv.client import ClientService
from srv.worker import WorkerService


opts = {
    "admin": (AdminService, []),
    "client": (ClientService, argv[2:4]),
    "worker": (WorkerService, [])
}


def print_help(example=None):
    print("Usage: admin|client [task]=[nvs]|worker")
    if example is not None:
        print("Example: {}".format(example))


def main():
    try:
        option = argv[1]
        srv, args = opts.get(option)
        if option == "client" and len(args) == 0:
            return print_help("analyze=/tmp/session.nvs")
        srv.run(*args)
    except Exception as e:
        print_help()
    except KeyboardInterrupt:
        print("\nClosing...")


if __name__ == "__main__":
    main()
