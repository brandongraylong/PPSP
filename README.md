# Python Persistent Shell Process (PPSP) v2.0.1


## About
PPSP is a useful python utility for running a command, getting command line output, and writing additional commands while the process is running.


## Python Version 
Tested with Python version 3.7.


## Sample Use Cases
- Run any shell command
- Run a game server or multiple game servers at once


## How to install
```pip install git+git://github.com/brandongraylong/PPSP@master#egg=PPSP```


## Examples
### example1.py
```
import argparse

from ppsp.utils import runner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c', 
        '--command', 
        action='store', 
        dest='command', 
        type=str, 
        required=True,
        default=None,
        help='Command to execute via shell.'
    )
    parser.add_argument(
        '-e', 
        '--exit-condition', 
        action='store', 
        dest='exit_condition',
        type=str, 
        required=False, 
        default=None,
        help='Python3 regular expression string.'
    )
    parser.add_argument(
        '-v', 
        '--verbose', 
        action='store_true', 
        dest='verbose',
        required=False,
        default=False,
        help='Verbose flag. If set, PPSP will provide helpful output.'
    )
    args = parser.parse_args()


    instance = runner(args.command, args.exit_condition)
    instance.start()
    while True:
        if instance.status.stopping:
            break
    instance.stop()

    if args.verbose:
        while not instance.stdout_queue.empty():
            print(instance.stdout_queue.get())


if __name__ == "__main__":
    main()

```

### example2.py
```
from ppsp.utils import runner


COMMANDS_TO_RUN = ['ls -l', 'ping google.com -w 5']


def main():
    instances = []
    for cmd in COMMANDS_TO_RUN:
        instance = runner(cmd)
        instance.start()
        instances += [instance]


    while True:
        all_stopped = True
        for instance in instances:
            if instance.status.running:
                all_stopped = False
            if instance.status.stopping:
                instance.stop()

        if all_stopped:
            break

    for instance in instances:
        print('Output from command \"' + instance.shell_command + '\": ')
        while not instance.stdout_queue.empty():
            print(instance.stdout_queue.get())
        print()


if __name__ == "__main__":
    main()

```