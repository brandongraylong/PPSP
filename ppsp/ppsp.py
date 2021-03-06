import os, sys, queue, re, subprocess, threading


class PPSP:
    """PPSP class is used for running a specific shell command.
    If a start condition is not provided, then processing of the stdin
    queue will begin immediately. If a start condition is provided,
    the stdin queue will only be used after the start condition is met, and
    the stdout will only start to fill up when the start condition is met.
    If an exit condition is not provided or met, all PPSP threads 
    that are started will have exited and can be successfully joined. 
    If exit condition is met, all PPSP threads will have
    exited and can be successfully joined. Must call start and stop
    explicitly.
    """

    class _Status:
        """Private class status is used for keeping track of
        the execution state of the subprocess command.
        """

        starting = False
        running = False
        stopping = False
        stopped = True

    def __init__(self, shell_command: str, **kwargs):
        """Class initialization.
        
        Args:
            shell_command (str): command to be run in subprocess
        Kwargs:
            start_condition (str): Regex string for when stdin processing should begin
            exit_condition (str): Regex string for when the process should end
        """

        # Subprocess management
        self._shell_command = shell_command

        # Regex start condition if applicable as to when commands should
        # start being processed based on an output from stdout
        if 'start_condition' in kwargs:
            if type(kwargs['start_condition']) is str:
                try:
                    self._start_condition = re.compile(
                        kwargs['start_condition']
                    )
                except re.error:
                    self._start_condition = None
            else:
                self._start_condition = None
        else:
            self._start_condition = None

        # Regex condition as to when threads should stop based on
        # an output from stdout
        if 'exit_condition' in kwargs:
            if type(kwargs['exit_condition']) is str:
                try:
                    self._exit_condition = re.compile(
                        kwargs['exit_condition']
                    )
                except re.error:
                    self._exit_condition = None
            else:
                self._exit_condition = None
        else:
            self._exit_condition = None

        # Subprocess
        self._subprocess = None

        # Threading
        self._status_tr = threading.Thread(target=self.__status)
        self._reader_tr = threading.Thread(target=self.__reader)
        self._writer_tr = threading.Thread(target=self.__writer)

        # Status
        self._status = self._Status()

        # Input and output queue
        self._stdin_queue = queue.Queue()
        self._stdout_queue = queue.Queue()

    @property
    def shell_command(self) -> str:
        """Getter for subprocess command.

        Returns:
            str: subprocess command string
        """
        
        return self._shell_command

    @property
    def subprocess(self) -> subprocess.Popen:
        """Getter for subprocess.

        Returns:
            subprocess.Popen: subprocess running the command
        """

        return self._subprocess

    @property
    def status(self) -> _Status:
        """Getter for status.

        Returns:
            PPSP._Status: current status
        """

        return self._status

    @property
    def stdout_queue(self) -> queue.Queue:
        """Getter for stdout_queue.

        Returns:
            queue.Queue: queue of the output from the subprocess
        """

        return self._stdout_queue

    def process_command(self, cmd: str) -> None:
        """Processes additional commands to be sent via stdin to
        the subprocess currently running.

        Args:
            cmd (str): command to be sent via stdin to subprocess
        """

        self._stdin_queue.put(cmd)

    def start(self) -> None:
        """Starts the subprocess with initial command.
        """

        self.__start_process()

        if self._start_condition is None:
            self._status.starting = False
            self._status.running = True
        else:
            self._status.starting = True
            self._status.running = False
            
        self._status.stopped = False
        self._status.stopping = False

        self._status_tr.start()
        self._reader_tr.start()
        self._writer_tr.start()

    def stop(self) -> None:
        """Declares the stopping of the subprocess within
        the instance and joins all the threads.
        """

        self._status.stopping = True

        self._status_tr.join()
        self._reader_tr.join()
        self._writer_tr.join()

        self._status.starting = False
        self._status.running = False
        self._status.stopping = False
        self._status.stopped = True

        if self._subprocess is not None:
            try:
                self._subprocess.kill()
            except (OSError, ProcessLookupError):
                pass

    def __start_process(self) -> None:
        """Private method for starting process via subprocess.Popen.
        """

        self._subprocess = subprocess.Popen(self._shell_command.split(), 
            stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, 
            cwd=os.getcwd())
            
    def __send_input(self) -> None:
        """Private method for sending input via stdin to subprocess.
        Gets data from stdin queue.
        """

        try:
            if self._subprocess:
                self._subprocess.stdin.write(bytes(self._stdin_queue.get() + 
                    '\n', sys.getdefaultencoding()))
                self._subprocess.stdin.flush()
        except (BrokenPipeError, AttributeError):
            pass

    def __status(self) -> None:
        """Status thread that checks if the subprocess has 
        completed and sets status to stopping if so.
        """

        while True:
            if not self._subprocess:
                continue
            
            if self._status.stopping:
                break

            if self._subprocess.poll() is not None:
                self._status.stopping = True
            
    def __reader(self) -> None:
        """Reader thread gets output from subprocess and puts the stripped data
        into the stdout queue. Sets state to running if start condition is set and met.
        Exits if status is stopping.
        """

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
                        if self._start_condition:
                            if re.match(self._start_condition, line):
                                self._status.starting = False
                                self._status.running = True
                        
                        if self._status.running:
                            self._stdout_queue.put(line.strip())

                        if self._exit_condition:
                            if re.match(self._exit_condition, line):
                                self._status.stopping = True

    def __writer(self) -> None:
        """Writer thread writes input to the subprocess if the stdin queue
        is not empty. Exits if status is stopping.
        """

        while True:
            if not self._subprocess:
                continue

            if self._status.stopping:
                break

            if self._status.running and \
                not self._stdin_queue.empty():
                self.__send_input()
