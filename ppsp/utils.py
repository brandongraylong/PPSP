import threading

from ppsp.ppsp import PPSP



def __runner(shell_command: str, return_val: dict, 
    **kwargs) -> None:
    """Private method runner instantiates a PPSP instance and 
    sets return_val['val'] to it in order to run the instance
    in a separate daemon thread but still return the instance.

    Args:
        shell_command (str): command to be run in subprocess
        return_val (dict): dictionary which acts a PPSP instance return
    Kwargs:
        start_condition (str): Regex string for when stdin processing should begin
        exit_condition (str): Regex string for when the process should end
    """

    ppsp_instance = PPSP(shell_command, **kwargs)
    return_val['val'] = ppsp_instance


def runner(shell_command: str, **kwargs) -> PPSP:
    """Runner instantiates a PPSP instance in a daemon thread and
    returns it. Allows for multiple PPSP instances to be created at
    once.

    Args:
        shell_command (str): command to be run in subprocess
    Kwargs:
        start_condition (str): Regex string for when stdin processing should begin
        exit_condition (str): Regex string for when the process should end
    Returns:
        PPSP: instance of the PPSP class used for subprocess management
    """

    return_val = {
        'val': None
    }
    ppsp_th = threading.Thread(
        target=__runner,
        args=(
            shell_command, 
            return_val
        ),
        kwargs=kwargs,
        daemon=True
    )
    ppsp_th.start()

    while return_val['val'] is None:
        continue

    return return_val['val']
