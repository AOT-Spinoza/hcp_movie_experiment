import numpy as np
import scipy.stats as ss
import subprocess
import os

from exptools2.core import Session, PylinkEyetrackerSession
from stimuli import FixationLines
from trial import HCPMovieELTrial, InstructionTrial, DummyWaiterTrial, OutroTrial
from psychopy.visual import ImageStim, MovieStim3


def get_movie_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", str(filename)],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)


class HCPMovieELSession(PylinkEyetrackerSession):
    def __init__(self, output_str, output_dir, settings_file, which_movie, eyetracker_on=True):
        """ Initializes StroopSession object. 

        Parameters
        ----------
        output_str : str
            Basename for all output-files (like logs), e.g., "sub-01_task-stroop_run-1"
        output_dir : str
            Path to desired output-directory (default: None, which results in $pwd/logs)
        settings_file : str
            Path to yaml-file with settings (default: None, which results in the package's
            default settings file (in data/default_settings.yml)
        """
        super().__init__(output_str, output_dir=output_dir, settings_file=settings_file,
                         eyetracker_on=eyetracker_on)  # initialize parent class!
        self.n_trials = self.settings['design'].get('n_trials')
        self.which_movie = int(which_movie)

        originalsize = self.settings["stimuli"].get("movie_size_pix")
        shrink_factor = self.settings["stimuli"].get("shrink_factor")
        display_size = [l*shrink_factor for l in originalsize]
        self.shiftedpos = (0, -originalsize[1]*(1-shrink_factor)/2)

        self.fixation = FixationLines(win=self.win,
                                      circle_radius=self.settings['stimuli'].get(
                                          'aperture_radius')*2 * shrink_factor,
                                      color=self.settings['stimuli'].get(
                                                 'fix_color'),
                                      line_width=self.settings['stimuli'].get(
                                          'fix_line_width'),
                                      pos=self.shiftedpos)

        self.report_fixation = FixationLines(win=self.win,
                                             circle_radius=self.settings['stimuli'].get(
                                                 'fix_radius')*2 * shrink_factor,
                                             color=self.settings['stimuli'].get(
                                                 'fix_color'),
                                             line_width=self.settings['stimuli'].get('fix_line_width'), pos=self.shiftedpos)

        if os.path.exists(self.settings["paths"].get("stimuli_path")):
            self.movie = os.path.join(self.settings["paths"].get(
                "stimuli_path"), self.settings['stimuli'].get('movie_files')[self.which_movie])
        elif os.path.exists(self.settings['paths'].get('stimuli_path_spinoza1')):
            self.movie = os.path.join(self.settings['paths'].get(
                'stimuli_path_spinoza1'), self.settings['stimuli'].get('movie_files')[self.which_movie])
        elif os.path.exists(self.settings['paths'].get('stimuli_path_spinoza2')):
            self.movie = os.path.join(self.settings['paths'].get(
                'stimuli_path_spinoza2'), self.settings['stimuli'].get('movie_files')[self.which_movie])

        self.movie_duration = get_movie_length(self.movie)
        print(f'movie duration for this run: {self.movie_duration}')
        self.movie_stim = MovieStim3(
            self.win, filename=self.movie, size=display_size, pos=self.shiftedpos, noAudio=False, fps=None)

    def create_trials(self):
        """ Creates trials (ideally before running your session!) """

        instruction_trial = InstructionTrial(session=self,
                                             trial_nr=0,
                                             phase_durations=[np.inf],
                                             # txt='Please keep fixating at the center.',
                                             txt='ready to start',
                                             keys=['space'])

        dummy_trial = DummyWaiterTrial(session=self,
                                       trial_nr=1,
                                       phase_durations=[
                                           np.inf, self.settings['design'].get('start_duration')],
                                       txt='Waiting for experiment to start')
                                       

        outro_trial = OutroTrial(session=self,
                                 trial_nr=self.n_trials+2,
                                 phase_durations=[
                                     self.settings['design'].get('end_duration')],
                                 txt='')

        movie_trial = HCPMovieELTrial(session=self,
                                      trial_nr=0,
                                      phase_durations=[self.settings['design'].get(
                                          'fix_movie_interval'), self.movie_duration, self.settings['design'].get('fix_movie_interval')],
                                      phase_names=['fix_pre',
                                                   'movie', 'fix_post'],
                                      parameters={'movie': self.run, 'movie_duration': self.movie_duration, 'movie_file': self.movie})

        self.trials = [instruction_trial,
                       dummy_trial, movie_trial, outro_trial]

    def create_trial(self):
        pass

    def run(self):
        """ Runs experiment. """
        # self.create_trials()  # create them *before* running!

        if self.eyetracker_on:
            self.calibrate_eyetracker()

        self.start_experiment()

        if self.eyetracker_on:
            self.start_recording_eyetracker()
        for trial in self.trials:
            trial.run()

        self.close()
