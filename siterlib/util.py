"""
    Copyright 2011 Alex Margarit

    This file is part of Siter, a static website generator.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys, time, traceback
import http.server, os, socketserver, subprocess, threading

class CUtil:
    @staticmethod
    def message(Title, Content, Color = 2):
        space = max(2, 12 - len(Title))
        head = '■' * (space // 2)
        tail = '■' * (space - space // 2)

        print(f'\033[{30 + Color};1m{head} {Title} {tail}\033[0m {Content}')

    @staticmethod
    def error(Message):
        CUtil.message('Error', Message, 1)
        CUtil.message('Call Stack', '', 1)
        traceback.print_stack()
        sys.exit(1)

    @staticmethod
    def warning(Message):
        CUtil.message('Warning', Message, 3)

    @staticmethod
    def info(Message):
        CUtil.message('Info', Message, 4)

    @staticmethod
    def time_step(Function):
        start = time.perf_counter()
        Function()

        return round(time.perf_counter() - start, 3)

    @staticmethod
    def chdir(Path):
        try:
            os.chdir(Path)
        except FileNotFoundError:
            CUtil.error(f'Invalid path {Path}')

    @staticmethod
    def run_server(RootPath):
        os.chdir(RootPath)

        host = 'localhost'
        port = 0
        server = socketserver.TCPServer(
                    (host, port), http.server.SimpleHTTPRequestHandler)

        with server:
            host, port = server.server_address
            url = f'http://{host}:{port}'

            server_thread = threading.Thread(target = server.serve_forever)
            server_thread.start()

            CUtil.info(f'Web server running at {url}')

            cmd = f'firefox -new-window {url}'
            status, output = subprocess.getstatusoutput(cmd)

            for line in output.splitlines():
                CUtil.message('Browser', line)

            if status != 0:
                sys.exit(status)

            input('\nPress ENTER to exit web server\n\n')

            server.shutdown()
            server_thread.join()
