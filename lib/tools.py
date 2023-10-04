import subprocess
import logging


class mkgmap:
    def __init__(self, *args, **kwargs):

        self.params = kwargs.get('parameters', None)
        self.jarfile = kwargs.get('jarfile', 'bin/mkgmap/mkgmap.jar')
        self.command = kwargs.get('command', )

    def check(self):
        if not self.params:
            logging.error("No parameters specified")
            return False

        if not self.params.get('style-file'):
            logging.error("No style file specified")
            return False

        if not self.params.get('input-file'):
            logging.error("No input file specified")
            return False

        if not self.params.get('output-file'):
            logging.error("No output file specified")
            return False

    def run(self):
        command = ['java', '-jar', self.jarfile]

        for key, value in self.params.items():
            command.append(f'--{key}={value}')
        command.append('--gmapsupp')

        logging.info(f'Running {command}')
        result = subprocess.run(command)
        if result.returncode != 0:
            logging.error(f'Failed with {result.stderr} {command}')
            return False

        logging.info(f'Completed with {result.stdout}')
        return True
