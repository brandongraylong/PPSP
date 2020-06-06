import threading

from ppsp.ppsp import PPSP



def __runner(shell_command: str, return_val: dict = {}, exit_condition: str = None) -> None:
    ppsp_instance = PPSP(shell_command, exit_condition)
    return_val['val'] = ppsp_instance


def runner(shell_command: str, exit_condition: str = None) -> PPSP:
    return_val = {
        'val': None
    }
    ppsp_th = threading.Thread(target=__runner, args=(shell_command, return_val, exit_condition),
        daemon=True)
    ppsp_th.start()

    while return_val['val'] is None:
        continue

    return return_val['val']
