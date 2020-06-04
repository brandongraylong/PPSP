import os, sys, queue, re, subprocess, threading


class PPSP:
    class Exceptions:
        class PPSPException(Exception):
            pass
        
        class PPSPExitException(PPSPException):
            pass

    class _Status:
        running = False
        stopping = False
        stopped = True

    def __init__(self, shell_command: str, verbose: bool = False, exit_condition: str = None):
        # Subprocess management
        self._shell_command = shell_command

        try:
            self._exit_condition = re.compile(exit_condition) \
                if exit_condition is not None else None
        except re.error as e:
            if verbose:
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

        if self._exit_condition_met:
            raise PPSP.Exceptions.PPSPExitException

    def is_running(self) -> bool:
        return self._status.running
    
    def is_stopping(self) -> bool:
        return self._status.stopping

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
                        print(line, end='')
                        if self._exit_condition:
                            if re.match(self._exit_condition, line):
                                self._exit_condition_met = True
                                self._status.stopping = True

    def __writer(self) -> None:
        while True:
            if not self._subprocess:
                continue

            if self._status.stopping:
                break

            if not self._queue.empty():
                self.__send_input(self._queue.get())


def ppsp(shell_command: str, verbose: bool = False, exit_condition: str = None) -> None:
    if verbose:
        print('PPSP starting... Press CTRL+C to quit')

    ppsp_instance = None
    try:
        ppsp_instance = PPSP(shell_command, verbose, exit_condition)
        ppsp_instance.start()
        ppsp_instance.stop()
    except KeyboardInterrupt:
        if verbose:
            print('Keyboard Interrupt. Exiting PPSP gracefully...')

        if ppsp_instance is not None:
            if ppsp_instance.subprocess is not None:
                try:
                    ppsp_instance.subprocess.kill()
                except (OSError, ProcessLookupError):
                    pass
        sys.exit(0)
    except PPSP.Exceptions.PPSPExitException:
        if verbose:
            print('Exit condition met. Exiting PPSP gracefully...')

        if ppsp_instance is not None:
            if ppsp_instance.subprocess is not None:
                try:
                    ppsp_instance.subprocess.kill()
                except (OSError, ProcessLookupError):
                    pass
        sys.exit(0)
    except Exception:
        if verbose:
            print('Unhandled exception occured. Exiting PPSP gracefully...')
        
        if ppsp_instance is not None:
            if ppsp_instance.subprocess is not None:
                try:
                    ppsp_instance.subprocess.kill()
                except (OSError, ProcessLookupError):
                    pass
        sys.exit(0)
    else:
        if verbose:
            print('Finished normally. Exiting PPSP gracefully...')
        
        if ppsp_instance is not None:
            if ppsp_instance.subprocess is not None:
                try:
                    ppsp_instance.subprocess.kill()
                except (OSError, ProcessLookupError):
                    pass
        sys.exit(0)
