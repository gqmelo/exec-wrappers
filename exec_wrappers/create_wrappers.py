import glob

import os
import stat


WRAPPER_TEMPLATE = '''#!/bin/sh
{run_in_file} {wrapped_file} "$@"
'''


def create_conda_wrappers(files_to_wrap, conda_env_dir, destination_dir):
    os.path.exists(destination_dir) or os.makedirs(destination_dir)

    this_dir = os.path.dirname(__file__)

    run_in_template_filename = os.path.join(this_dir, 'templates', 'run-in_conda')
    with open(run_in_template_filename, 'r') as f:
        content = f.read().replace('@CONDA_ENV_DIR@', conda_env_dir)

    run_in_filename = os.path.join(destination_dir, 'run-in')
    with open(run_in_filename, 'w') as f:
        f.write(content)
    os.chmod(run_in_filename, os.stat(run_in_filename).st_mode | stat.S_IXUSR)

    for filename in files_to_wrap:
        basename = os.path.basename(filename)
        destination_filename = os.path.join(destination_dir, basename)
        content = WRAPPER_TEMPLATE.format(run_in_file=run_in_template_filename,
                                         wrapped_file=filename)
        with open(destination_filename, 'w') as f:
            f.write(content)

        os.chmod(destination_filename, os.stat(destination_filename).st_mode | stat.S_IXUSR)


def list_executable_files(directory):
    return sorted([
        f
        for f
        in glob.glob(directory + '/*')
        if not os.path.isdir(f) and os.access(f, os.X_OK)
    ])
