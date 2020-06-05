from ppsp import ppsp


COMMANDS_TO_RUN = ['ls -l', 'ping google.com -w 5']


def main():
    instances = []
    for cmd in COMMANDS_TO_RUN:
        instance = ppsp(cmd)
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
