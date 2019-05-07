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

from os import makedirs, path
from datetime import datetime
from uuid import uuid1
from gearman import GearmanWorker
from subprocess import Popen

from encoder import Encoder
from service import Service, Server


NAME = "nv_{}".format(uuid1())
DIR_PATH = "/tmp/nova/net"
LOG_SDTOUT = "log"


class Worker(GearmanWorker):

    data_encoder = Encoder
    last_activity = True

    def after_poll(self, any_activity):
        if not any_activity and self.last_activity:
            self.last_activity = False
            print("Worker idle...")
        else:
            self.last_activity = any_activity
        return True


class WorkerService(Service):

    def __init__(self, name=NAME):
        self.name = name
        self.worker = Worker(Server.hosts)
        self.worker.set_client_id(self.name)
        print("Worker {} starting...".format(self.name))

    def extract_output(self, nvs, ext=None):
        parts = nvs.split("/")
        filename, _ = parts[-1].split(".", 1)
        if ext is None:
            return filename
        return "{}.{}".format(filename, ext)

    def get_path(self, filepath, root=DIR_PATH):
        if not path.exists(root):
            makedirs(root)
        if root.endswith("/"):
            root = root[:-1]
        if filepath.startswith("/"):
            filepath = filepath[1:]
        return "{}/{}".format(root, filepath)

    def run_cmd(self, cmd, log_sdtout=LOG_SDTOUT):
        if not isinstance(cmd, list):
            raise TypeError("Unexpected parameter type passed")
        with open(log_sdtout, "wb") as log:
            proc = Popen(cmd, stdout=log, stderr=log)
            return proc.wait()
        raise Exception("Failed to run cmd: {}".format(" ".join(cmd)))

    def get_work_fps_cmd(self, input_path, fps, save_path):
        return [self.app_bin, "-vt", input_path, "--record", save_path,
                "--fps", str(fps), "--headless"]

    def func_work_fps_mode(self, worker, job):
        print("Worker receiving task '{}' at {}".format(job.task, datetime.utcnow()))
        input_path = job.data.get("nvs")
        input_fps = job.data.get("fps")
        if input_path is None or input_fps is None:
            print("Worker cannot run task because job is corrupted")
            return self.TASK_FAILED
        output_dir = self.extract_output(input_path)
        output_path = "{}/{}".format(DIR_PATH, output_dir)
        log_path = self.get_path("log", output_path)
        save_path = self.get_path("video.mp4", output_path)
        cmd = self.get_work_fps_cmd(input_path, input_fps, save_path)
        print("Launching cmd: {}".format(" ".join(cmd)))
        print("Saving output: {}".format(log_path))
        print("Saving fileas: {}".format(save_path))
        try:
            returncode = self.run_cmd(cmd, log_path)
            print("Task exitcode: {}".format(returncode))
        except Exception as e:
            print("Worker failed task at {} because: {}".format(datetime.utcnow(), e))
            return self.TASK_FAILED
        print("Worker completed task at {}".format(datetime.utcnow()))
        return self.TASK_FINISH

    def get_analyze_cmd(self, input_path):
        return [self.app_bin, "-va", input_path]

    def func_analyze_mode(self, worker, job):
        print("Worker receiving task '{}' at {}".format(job.task, datetime.utcnow()))
        input_path = job.data.get("nvs")
        if input_path is None:
            print("Worker cannot run task because job is corrupted")
            return self.TASK_FAILED
        output_dir = self.extract_output(input_path)
        log_path = self.get_path("log", "{}/{}".format(DIR_PATH, output_dir))
        cmd = self.get_analyze_cmd(input_path)
        print("Launching cmd: {}".format(" ".join(cmd)))
        print("Saving output: {}".format(log_path))
        try:
            returncode = self.run_cmd(cmd, log_path)
            print("Task exitcode: {}".format(returncode))
        except Exception as e:
            print("Worker failed task at {} because: {}".format(datetime.utcnow(), e))
            return self.TASK_FAILED
        print("Worker completed task at {}".format(datetime.utcnow()))
        return self.TASK_FINISH

    def start(self):
        self.worker.register_task(self.WORKx01_MODE, self.func_work_fps_mode)
        self.worker.register_task(self.WORKx16_MODE, self.func_work_fps_mode)
        self.worker.register_task(self.WORKx24_MODE, self.func_work_fps_mode)
        self.worker.register_task(self.WORKx47_MODE, self.func_work_fps_mode)
        self.worker.register_task(self.ANALYZE_MODE, self.func_analyze_mode)
        try:
            self.worker.work()
        except Exception:
            raise Exception
        except KeyboardInterrupt:
            raise SystemExit("\nWorker exists")

    @classmethod
    def run(cls, *args):
        w = cls()
        w.start()
