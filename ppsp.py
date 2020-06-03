import os, sys, queue, re, signal, subprocess, threading, time


class PPSP:
    class Exceptions:
        class PPSPException(Exception):
            pass
        
        class PPSPExitException(PPSPException):
            pass

    class _Status:
        running = False
        stopped = True

    def __init__(self, shell_command: str, exit_condition: str = None):
        # Subprocess management
        self._shell_command = shell_command

        try:
            self._exit_condition = re.compile(exit_condition) \
                if exit_condition is not None else None
        except re.error as e:
            print('Regular expression did not compile. Skipping...')
            self._exit_condition = None
        
        self._exit_condition_met = False

        # Subprocess
        self._subprocess = None

        # Threading
        self._status_tr = threading.Thread(target=self.__status)
        self._reader_tr = threading.Thread(target=self.__reader)
        self._writer_tr = threading.Thread(target=self.__writer)

        self._status = self._Status()
        self._queue = queue.Queue()

    @property
    def subprocess(self):
        return self._subprocess

    def process_command(self, cmd: str) -> None:
        if cmd:
            self._queue.put(cmd)

    def start(self) -> None:
        self.__start_process()
        self._status.running = True
        self._status.stopped = False

        self._status_tr.start()
        self._reader_tr.start()
        self._writer_tr.start()

    def stop(self) -> None:
        self._status.running = False

        self._status_tr.join()
        self._reader_tr.join()
        self._writer_tr.join()

        self._status.stopped = True

        if self._exit_condition_met:
            raise PPSP.Exceptions.PPSPExitException

    def is_running(self) -> bool:
        return self._status.running
    
    def is_stopped(self) -> bool:
        return self._status.stopped

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

            if self._subprocess.poll() is not None:
                self._status.stopped = True
                break

    def __reader(self) -> None:
        while True:
            if not self._subprocess:
                continue

            if self._status.stopped:
                break
            
            if self._subprocess.stdout:
                for linen in self._subprocess.stdout:
                    line = linen.decode(sys.getdefaultencoding())
                    if line:
                        print(line, end='')
                        if self._exit_condition:
                            if re.match(self._exit_condition, line):
                                self._exit_condition_met = True
                                self._status.stopped = True
                                break

    def __writer(self) -> None:
        while True:
            if not self._subprocess:
                continue

            if self._status.stopped:
                break

            if not self._queue.empty():
                self.__send_input(self._queue.get())


def ppsp(shell_command: str, exit_condition: str = None) -> None:
    ppsp_instance = None
    try:
        ppsp_instance = PPSP(shell_command, exit_condition)
        ppsp_instance.start()
        ppsp_instance.stop()
    except KeyboardInterrupt:
        print('Keyboard Interrupt. Exiting PPSP gracefully...')
        if ppsp_instance is not None:
            if ppsp_instance.subprocess is not None:
                try:
                    os.killpg(os.getpgid(ppsp_instance.subprocess.pid), signal.SIGTERM)
                except (OSError, ProcessLookupError):
                    pass
        sys.exit(0)
    except PPSP.Exceptions.PPSPExitException:
        print('Exit condition met. Exiting PPSP gracefully...')
        if ppsp_instance is not None:
            if ppsp_instance.subprocess is not None:
                try:
                    os.killpg(os.getpgid(ppsp_instance.subprocess.pid), signal.SIGTERM)
                except (OSError, ProcessLookupError):
                    pass
        sys.exit(0)
    except Exception:
        print('Unhandled exception occured. Exiting PPSP gracefully...')
        if ppsp_instance is not None:
            if ppsp_instance.subprocess is not None:
                try:
                    os.killpg(os.getpgid(ppsp_instance.subprocess.pid), signal.SIGTERM)
                except (OSError, ProcessLookupError):
                    pass
        sys.exit(0)
    else:
        print('Finished normally. Exiting PPSP gracefully...')
        if ppsp_instance is not None:
            if ppsp_instance.subprocess is not None:
                try:
                    os.killpg(os.getpgid(ppsp_instance.subprocess.pid), signal.SIGTERM)
                except (OSError, ProcessLookupError):
                    pass
        sys.exit(0)
