import os.path as op
import argparse
import numpy as np
import scipy.stats as ss
import pandas as pd
from psychopy import logging
from itertools import product
import yaml
from session import HCPMovieELSession

parser = argparse.ArgumentParser()
parser.add_argument('--subject', default=1, nargs='?')
parser.add_argument('--run', default=1, nargs='?')
parser.add_argument('eyelink', default=False, nargs='?')
#
cmd_args = parser.parse_args()
subject, run, eyelink = cmd_args.subject, cmd_args.run, cmd_args.eyelink


if eyelink:
    eyetracker_on = True
    logging.warn("Using eyetracker")
else:
    eyetracker_on = False
    logging.warn("Using NO eyetracker")


output_str = f'sub-{subject}_run-{run}_task-movie'
settings_fn = op.join(op.dirname(__file__), 'settings.yml')

session_object = HCPMovieELSession(output_str=output_str,
                                   output_dir=None,
                                   settings_file=settings_fn,
                                   eyetracker_on=eyetracker_on,
                                   which_movie=int(run)-1)
session_object.create_trials()
logging.warn(
    f'Writing results to: {op.join(session_object.output_dir, session_object.output_str)}')
session_object.run()
session_object.close()
