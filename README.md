# Python Persistent Shell Process (PPSP) v3.0.0


## About
PPSP is a useful python utility for running a command, getting command line output, and writing additional commands while the process is running.


## Python Version 
Tested with Python version 3.7.


## Sample Use Cases
- Run any shell command
- Run a game server or multiple game servers at once (optionally continually providing them all command line input when necessary)


## How to install
```pip install git+git://github.com/brandongraylong/PPSP@master#egg=PPSP```


## Example Program
### example.py
```
from ppsp.utils import runner


RUNNNERS = [
    {
        'command': 'ls -l'
    }, 
    {
        'command': 'ping google.com -w 10',
        'start_condition': '(.*)icmp_seq=5(.*)',
        'exit_condition': '(.*)icmp_seq=9(.*)'
    }
]


def main():
    instances = []
    for r in RUNNNERS:
        instance = runner(
            r['command'],
            start_condition=r['start_condition'] if 'start_condition' in r else None,
            exit_condition=r['exit_condition'] if 'exit_condition' in r else None,
        )
        
        instance.start()
        instances += [instance]


    # In this loop, it's a good idea to get output from stdout_queue every time
    # to avoid high memory usage of long running processes (and to check
    # if you need to do something in response to your process output, if applicable). 
    # Furthermore, memory usage caps aren't yet implemented in PPSP.
    while True:
        all_stopped = True
        for instance in instances:
            if instance.status.running or instance.status.starting:
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
