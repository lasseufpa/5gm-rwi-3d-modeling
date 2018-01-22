import subprocess
import logging
import os
import shutil

CALCPROP_BIN=r'"C:\Program Files\Remcom\Wireless InSite 3.2.0.3\bin\calc\calcprop"'

class InSiteProject:

    def __init__(self, path, output_dir, calcprop_bin=CALCPROP_BIN):
        """InSite project
        :param path: path to the .setup file
        :param output_dir: where the .setup will store the results (normally the Study Area name)
        :param calcprop_bin: the path to InSite's calcprop binary
        """
        self._path = path
        self._output_dir = output_dir
        self._calcprop_bin = calcprop_bin

    def run(self, calc_mode=None, clean_run=None, delete_temp=None, memory=None, output_dir=None):
        """Run InSite simulation and store the results in output_dir

        :param calc_mode: New, AddTransmitters, AddReceivers, ChangeHeights,
                       ChangeFrequency, ChangeAntennas, ChangeMaterials,
                       ChangeWalltypes, AddOutput, ConsolidateClusterRun
        :param clean_run: clean and then recalculate all data files
        :param delete_temp: after running, delete temporary data files
        :param memory: <n+>[.[<n+>]]K/M/G e.g. 450.5M
        :param output_dir: Move InSite's result to this path
        :return: None
        """
        cmd = ''

        def add_opt(opt, formatter):
            if opt is not None:
                return formatter.format(opt=opt)
            else:
                return ''
        cmd += self._calcprop_bin
        cmd += add_opt(calc_mode, ' --calc-mode={opt}')
        cmd += add_opt(clean_run, ' --clean-run')
        cmd += add_opt(delete_temp, ' --delete-temp')
        cmd += add_opt(memory, ' --memory={opt}')
        cmd += add_opt(self._path, ' --project={opt}')
        logging.info('Running CMD: "{}"'.format(cmd))
        subprocess.run(cmd, shell=True, check=True)
        if output_dir is not None:
            shutil.move(self._output_dir, output_dir)

if __name__=='__main__':
    logging.basicConfig(level=logging.INFO)
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'SimpleFunciona', 'model.setup')
    project_output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                      'SimpleFunciona', 'study')
    output_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              'oi')
    output_dir = None
    project = InSiteProject(path, project_output_dir)
    project.run(output_dir=output_dir)