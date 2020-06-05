import os, sys, queue, re, subprocess, threading


class _PPSP:
    class _Status:
        running = False
        stopping = False
        stopped = True

    def __init__(self, shell_command: str, exit_condition: str = None):
        # Subprocess management
        self._shell_command = shell_command

        try:
            self._exit_condition = re.compile(exit_condition) \
                if exit_condition is not None else None
        except re.error as e:
            pass
            
            self._exit_condition = None
        
        # Subprocess
        self._subprocess = None

        # Threading
        self._status_tr = threading.Thread(target=self.__status)
        self._reader_tr = threading.Thread(target=self.__reader)
        self._writer_tr = threading.Thread(target=self.__writer)

        self._status = self._Status()
        self._stdin_queue = queue.Queue()
        self._stdout_queue = queue.Queue()

    @property
    def shell_command(self):
        return self._shell_command

    @property
    def subprocess(self):
        return self._subprocess

    @property
    def status(self):
        return self._status

    @property
    def stdout_queue(self):
        return self._stdout_queue

    def process_command(self, cmd: str) -> None:
        if cmd:
            self._stdin_queue.put(cmd)

    def start(self) -> None:
        self.__start_process()
        self._status.running = True
        self._status.stopped = False
        self._status.stopping = False

        self._status_tr.start()
        self._reader_tr.start()
        self._writer_tr.start()

    def stop(self) -> None:
        self._status_tr.join()
        self._reader_tr.join()
        self._writer_tr.join()

        self._status.running = False
        self._status.stopping = False
        self._status.stopped = True

        if self._subprocess is not None:
            try:
                self._subprocess.kill()
            except (OSError, ProcessLookupError):
                pass

    def __start_process(self) -> None:
        self._subprocess = subprocess.Popen(self._shell_command.split(), 
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, 
            cwd=os.getcwd(), bufsize=1)
            
    def __send_input(self, msg: str) -> None:
        self._subprocess.stdin.write(bytes(msg + '\n', sys.getdefaultencoding()))
        self._subprocess.stdin.flush()

    def __status(self) -> None:
        while True:
            if not self._subprocess:
                continue
            
            if self._status.stopping:
                break

            if self._subprocess.poll() is not None:
                self._status.stopping = True
            
    def __reader(self) -> None:
        while True:
            if not self._subprocess:
                continue

            if self._status.stopping:
                break
            
            if self._subprocess.stdout:
                for linen in self._subprocess.stdout:
                    if self._status.stopping:
                        break
                    line = linen.decode(sys.getdefaultencoding())
                    if line:
                        self._stdout_queue.put(line.strip())

                        if self._exit_condition:
                            if re.match(self._exit_condition, line):
                                self._status.stopping = True

    def __writer(self) -> None:
        while True:
            if not self._subprocess:
                continue

            if self._status.stopping:
                break

            if not self._stdin_queue.empty():
                self.__send_input(self._stdin_queue.get())


def __ppsp(shell_command: str, return_val: dict = {}, exit_condition: str = None) -> None:
    ppsp_instance = _PPSP(shell_command, exit_condition)
    return_val['val'] = ppsp_instance


def ppsp(shell_command: str, exit_condition: str = None) -> _PPSP:
    return_val = {
        'val': None
    }
    ppsp_th = threading.Thread(target=__ppsp, args=(shell_command, return_val, exit_condition),
        daemon=True)
    ppsp_th.start()

    while return_val['val'] is None:
        continue

    return return_val['val']
