import pathlib
import subprocess
import re
import sys
import os

def run_new_scripts(base_directory: str):
    # Regex pattern to match directories starting with two digits
    pattern = re.compile(r'^\d{2}')
    
    # Find all directories that match the pattern
    directories = [d for d in base_directory.iterdir() if d.is_dir() and pattern.match(d.name)]
    
    # Sort directories based on their numeric prefix
    directories.sort(key=lambda d: int(d.name[:2]))

    for directory in directories:
        os.chdir(directory)

        # Find and run all Python scripts that start with 'list_'
        for script in pathlib.Path('.').rglob('list_*.py'):
            script_relative_path = script.name.replace('.py', '')

            print(f'Running script: {script_relative_path} in directory: {directory}')
            try:
                # Execute the script
                subprocess.run([sys.executable, '-m', script_relative_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f'Error running {script}: {e}')
                os.chdir('..')
                sys.exit(1)
        os.chdir('..')

def main(dir_path: str = '.'):
    # Start from the current directory
    run_new_scripts(pathlib.Path(dir_path))

if __name__ == '__main__':
    main()
