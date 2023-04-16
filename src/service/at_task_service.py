import os
from injectable import injectable


@injectable
class AtTaskService():
    def do(self, script_path:str, param1: str, param2:str, date: str):
        cmd = f"echo 'python3.10 {script_path} {param1} {param2}' | at {date}"
        os.system(cmd)
