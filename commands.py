#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, sys, multiprocessing, subprocess
from subprocess import Popen, CalledProcessError, PIPE, STDOUT

class CommandExecutor:

    CORES = multiprocessing.cpu_count()

    def __init__(self):
        pass

    def call_process(self, cmd):
        proc = Popen(cmd, stdout=None, stderr=None)
        proc.communicate()
        if proc.returncode != 0:
            raise Exception('Command \'%s\' returned not-zero exit status %s' % (' '.join(cmd), proc.returncode))

    def run_commands( self, commands, cores = 0 ):
        cores = min(len(commands), max(cores, self.CORES))
        if cores <= 1:
            for command in commands:
                self.call_process(command)
        else:
            pool = multiprocessing.Pool(processes = cores)
            pool.map(self.call_process, commands, chunksize = 1)
            pool.close()
            pool.join()
