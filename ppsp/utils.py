import threading, json

from ppsp.ppsp import PPSP


# Methods for running a specific PPSP instance
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
        cwd (str): Absolute directory path to subprocess current working directory
    """

    ppsp_instance = PPSP(shell_command, **kwargs)
    return_val['val'] = ppsp_instance


def runner(shell_command: str, **kwargs) -> PPSP, threading.Thread:
    """Runner instantiates a PPSP instance in a daemon thread and
    returns it. Allows for multiple PPSP instances to be created at
    once.

    Args:
        shell_command (str): command to be run in subprocess
    Kwargs:
        start_condition (str): Regex string for when stdin processing should begin
        exit_condition (str): Regex string for when the process should end
        cwd (str): Absolute directory path to subprocess current working directory
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

    return return_val['val'], ppsp_th


# Class for managing multiple PPSP instances
class PPSPManager:
    def __init__(self):
        # instance_id: instance
        self._instances = {}

    @property
    def instances(self) -> list:
        return self._instances

    def get_instance(self, instance_id: str) -> PPSP or None:
        if instance_id in self._instances:
            return self._instances[instance_id]
        else:
            return None

    def add_instance(self, shell_command: str, **kwargs) -> str:
        instance = runner(shell_command, **kwargs)
        self._instances.update({
            instance.id: instance
        })

        return instance.id

    def save_all_instance_data(self, abs_path: str) -> bool:
        save_data = []
        for instance_id, instance in self._instances.items():
            save_data += [{
                instance_id: {
                    'shell_command': instance.shell_command,
                    'cwd': instance.cwd,
                    'start_condition': instance.start_condition,
                    'exit_condition': instance.exit_condition
                }
            }]
        
        try:
            with open(abs_path, 'w') as f:
                json.dump(save_data, f, indent=4)
            return True
        except FileNotFoundError:
            return False

    def load_all_instance_data(self, abs_path: str) -> bool:
        try:
            data = None
            with open(abs_path, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return False

        if data is not None and data != []:
            for item in data:
                for key in item:
                    if 'shell_command' not in item[key]:
                        return False
                    else:
                        kwargs = {
                            'id': key
                        }
                        kwargs.update(item[key])
                        shell_command = kwargs.pop('shell_command')

                    self._instances += [
                        runner(shell_command, **kwargs)
                    ]

            return True
        else:
            return False
