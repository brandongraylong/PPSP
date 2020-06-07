import threading

from ppsp.ppsp import PPSP



def __runner(shell_command: str, return_val: dict, 
    exit_condition: str = None) -> None:
    """Private method runner instantiates a PPSP instance and 
    sets return_val['val'] to it in order to run the instance
    in a separate daemon thread but still return the instance.

    Args:
        shell_command (str): command to be run
        return_val (dict): dictionary which acts a PPSP instance return
        exit_condition (str or None): exit condition for subprocess
    """

    ppsp_instance = PPSP(shell_command, exit_condition)
    return_val['val'] = ppsp_instance


def runner(shell_command: str, exit_condition: str = None) -> PPSP:
    """Runner instantiates a PPSP instance in a daemon thread and
    returns it. Allows for multiple PPSP instances to be created at
    once.

    Args:
        shell_command (str): command to be run
        exit_condition (str or None): exit condition for subprocess
    """

    return_val = {
        'val': None
    }
    ppsp_th = threading.Thread(
        target=__runner,
        args=(
            shell_command, 
            return_val, 
            exit_condition
        ),
        daemon=True
    )
    ppsp_th.start()

    while return_val['val'] is None:
        continue

    return return_val['val']
