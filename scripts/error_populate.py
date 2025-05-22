import pathlib
import subprocess
import threading
import re
import sys
import os


def read_output(process):
    """Read stdout and stderr in real-time."""
    while True:
        output = process.stdout.readline()
        if output:
            print(output.strip(), flush=True)
        
        error = process.stderr.readline()
        if error:
            print(error.strip(), flush=True)

        # Check if the process has finished
        if process.poll() is not None:
            break


def run_new_scripts(base_directory: str):
    pattern = re.compile(r'^\d{2}')
    directories = [d for d in base_directory.iterdir() if d.is_dir() and pattern.match(d.name)]
    directories.sort(key=lambda d: int(d.name[:2]))

    for directory in directories:
        os.chdir(directory)

        # Casi particolari per le letture con errore.
        directory_path: pathlib.Path = pathlib.Path('.')
        if directory_path.resolve().name in [
            '40_plant_module_system_sensor_reading',
            '41_plant_battery_system_sensor_reading',
           ]:
            pattern = 'error_new_*.py'
        else:
            pattern = 'new_*.py'

        for script in directory_path.rglob(pattern):
            script_relative_path = script.name.replace('.py', '')

            print(f'Running script: {script_relative_path} in directory: {directory}')
            try:
                # Execute the script.
                if re.match(r'error_new_.*\.py', str(script)):
                    env = os.environ.copy()
                    env['PYTHONBUFFERED'] = '1'

                    # Run in background.
                    process = subprocess.Popen(
                        [sys.executable, '-m', script_relative_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,
                        env=env,
                    )
                    output_thread = threading.Thread(target=read_output, args=(process,))
                    output_thread.start()
                else:
                    subprocess.run([sys.executable, '-m', script_relative_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f'Error running {script}: {e}')
                os.chdir('..')
                sys.exit(1)
        os.chdir('..')


def main(dir_path: str = '.'):
    # Start from the current directory.
    run_new_scripts(pathlib.Path(dir_path))

if __name__ == '__main__':
    main()
