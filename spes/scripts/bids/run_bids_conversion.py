from pathlib import Path
import shutil as sh
from typing import Union, List
from mne import annotations
from mne.io.meas_info import create_info
import numpy as np
from natsort import natsorted
import scipy.io
import pandas as pd
import json
import warnings

from mne.io import RawArray
from mne import Annotations, events_from_annotations
from mne_bids import (
    BIDSPath,
    make_dataset_description,
    update_sidecar_json,
    read_raw_bids, write_raw_bids
)
from mne_bids.path import get_entities_from_fname, get_entity_vals
from mne_bids.utils import _write_json
from mne_bids.tsv_handler import _from_tsv, _to_tsv

import hdf5storage
from pymatreader import read_mat
from BCI2kReader import BCI2kReader as b2k

class MatReader:
    """
    Object to read mat files into a nested dictionary if need be.
    Helps keep strucutre from matlab similar to what is used in python.
    """

    def __init__(self, filename=None):
        self.filename = filename

    def loadmat(self, filename):
        """
        this function should be called instead of direct spio.loadmat
        as it cures the problem of not properly recovering python dictionaries
        from mat files. It calls the function check keys to cure all entries
        which are still mat-objects
        """
        try:
            data = scipy.io.loadmat(
                filename, struct_as_record=False, squeeze_me=True, chars_as_strings=True
            )
        except NotImplementedError as e:
            print(e)
            data = hdf5storage.loadmat(filename)
        return self._check_keys(data)

    def _check_keys(self, dict):
        """
        checks if entries in dictionary are mat-objects. If yes
        todict is called to change them to nested dictionaries
        """
        print(f"Found these keys {dict.keys()}")
        for key in dict:
            if isinstance(dict[key], scipy.io.matlab.mio5_params.mat_struct):
                dict[key] = self._todict(dict[key])
        return dict

    def _todict(self, matobj):
        """
        A recursive function which constructs from matobjects nested dictionaries
        """
        dict = {}
        for strg in matobj._fieldnames:
            elem = matobj.__dict__[strg]
            if isinstance(elem, scipy.io.matlab.mio5_params.mat_struct):
                dict[strg] = self._todict(elem)
            elif isinstance(elem, np.ndarray):
                dict[strg] = self._tolist(elem)
            else:
                dict[strg] = elem
        return dict

    def _tolist(self, ndarray):
        """
        A recursive function which constructs lists from cellarrays
        (which are loaded as numpy ndarrays), recursing into the elements
        if they contain matobjects.
        """
        elem_list = []
        for sub_elem in ndarray:
            if isinstance(sub_elem, scipy.io.matlab.mio5_params.mat_struct):
                elem_list.append(self._todict(sub_elem))
            elif isinstance(sub_elem, np.ndarray):
                elem_list.append(self._tolist(sub_elem))
            else:
                elem_list.append(sub_elem)
        return elem_list



def _convert_stimulation_file(fname, params_file, clinical_file, bids_path):
    # read in the parameters file
    clin_data = read_mat(clinical_file)
    params_data = read_mat(params_file)

    ch_names = params_data['chanLabels']
    bad_chs_idx = params_data['artChannels']
    sfreq = params_data['fs']
    stim_ch1 = params_data['stimChan1'] - 1  # stimulation idx
    stim_ch2 = params_data['stimChan2'] - 1
    stim_vec = params_data['stimVec']
    ch_clin_labels = clin_data['clinLabels']

    # read in the dataset
    with b2k.BCI2kReader(fname) as fin: #opens a stream to the dat file
        data, my_states=fin.readall()

    # create Raw data structure
    print(my_states.keys())

    # convert to Voltage from uV
    data = np.divide(data, 1e6)

    info = create_info(ch_names, sfreq=sfreq, ch_types='seeg')
    raw = RawArray(data, info=info)
    
    # get the bad channels
    bad_mask = np.ma.make_mask(bad_chs_idx)
    bad_chs = np.array(raw.ch_names)[bad_mask]
    raw.info['bads'].extend(bad_chs)
    
    # create event annotations for the stimulation
    stim_chs = f'{ch_names[stim_ch1]}-{ch_names[stim_ch2]}'
    stim_onset = (stim_vec - 1) / raw.info['sfreq']
    stim_duration = 0
    stim_description = f'electrical stimulation {stim_chs}'
    annotations = Annotations(onset=stim_onset, duration=stim_duration,
        description=stim_description)
    return raw, ch_clin_labels, annotations


def _write_stimulation_metadata(bids_path, stim_type, stim_site, stim_current):
    event_df = pd.read_csv(bids_path, sep='\t')

    event_df['electrical_stimulation_type'] = stim_type
    event_df['electrical_stimulation_site'] = stim_site
    event_df['electrical_stimulation_current'] = stim_current
    event_df.to_csv(bids_path, sep='\t')

    # write an events.json
    json_fpath = bids_path.update(extension='.json')
    if json_fpath.fpath.exists():
        with open(json_fpath, 'r') as fin:
            event_json = json.load(fin)
    else:
        event_json = dict()

    event_json['electrical_stimulation_type'] = {
        'Description': 'The type of stimulation.',
        'Levels': {
            'biphasic': 'Biphasic stimulation',
            'complex': 'Complex stimulation',
        }
    }

    event_json['electrical_stimulation_site'] = {
        'Description': 'Where stimulation took place in terms of electrode site.'
    }

    event_json['electrical_stimulation_current'] = {
        'Description': 'The amplitude of the stimulation current in Amps.',
        'Units': 'Milli-Amperes'
    }
    _write_json(json_fpath, event_json, overwrite=True)


def _update_sidecar_tsv_byname(
    sidecar_fname: str,
    name: Union[List, str],
    colkey: str,
    val: str,
    allow_fail=False,
    index_name="name",
    verbose=False,
):
    """Update a sidecar JSON file with a given key/value pair.

    Parameters
    ----------
    sidecar_fname : str
        Full name of the data file
    name : str
        The name of the row in column "name"
    colkey : str
        The lower-case column key in the sidecar TSV file. E.g. "type"
    val : str
        The corresponding value to change to in the sidecar JSON file.
    """
    # convert to lower case and replace keys that are
    colkey = colkey.lower()

    if isinstance(name, list):
        names = name
    else:
        names = [name]

    # load in sidecar tsv file
    sidecar_tsv = _from_tsv(sidecar_fname)

    for name in names:
        # replace certain apostrophe in Windows vs Mac machines
        name = name.replace("’", "'")

        if allow_fail:
            if name not in sidecar_tsv[index_name]:
                warnings.warn(
                    f"{name} not found in sidecar tsv, {sidecar_fname}. Here are the names: {sidecar_tsv['name']}"
                )
                continue

        # get the row index
        row_index = sidecar_tsv[index_name].index(name)

        # write value in if column key already exists,
        # else write "n/a" in and then adjust matching row
        if colkey in sidecar_tsv.keys():
            sidecar_tsv[colkey][row_index] = val
        else:
            sidecar_tsv[colkey] = ["n/a"] * len(sidecar_tsv[index_name])
            sidecar_tsv[colkey][row_index] = val

    _to_tsv(sidecar_tsv, sidecar_fname)


def update_channels_tsv(
    ch_names,
    key,
    value,
    description,
    root,
    subject,
    datatype,
    session=None,
    verbose=True,
):
    """Update channels.tsv sidecar files.

    Parameters
    ----------
    ch_names : List[str]
    key : str
    value : str
    description : str
    root : str
    subject : str
    datatype :
    session :
    verbose :
    """
    # create a BIDS Path object
    bids_path = BIDSPath(
        subject=subject,
        session=session,
        datatype=datatype,
        root=root,
        suffix="channels",
        extension=".tsv",
    )

    # get all channels tsv files
    channel_fpaths = bids_path.match()

    for channels_fpath in channel_fpaths:
        if not "channels.tsv" in str(channels_fpath):
            continue
        # update the sidecar tsv
        _update_sidecar_tsv_byname(
            sidecar_fname=channels_fpath,
            name=ch_names,
            colkey=key,
            val=value,
            allow_fail=True,
        )

        cols = dict()
        if description is None:
            description = value
        cols[key] = description

        # write in the channels tsv
        fname = channels_fpath.update(extension=".json")
        if fname.fpath.exists():
            with open(fname, "r") as fin:
                orig_cols = json.load(fin)
        else:
            orig_cols = {}
        for key, val in orig_cols.items():
            if key not in cols:
                cols[key] = val
        _write_json(fname, cols, overwrite=True)


def _write_clinical_chs(bids_path, col_name, col_value, col_units):
    ch_df = pd.read_csv(bids_path, sep='\t')

    ch_df[col_name] = col_value
    ch_df.to_csv(bids_path, sep='\t')

def _extract_stim_ch(fname, subject):
    fname_parts = fname.name.split('_')
    assert fname_parts[0] == subject
    stim_chs = ''.join(fname_parts[1:3])
    stim_amt = fname_parts[3]
    return stim_chs, int(stim_amt)

def convert_jhh():
    root = Path('/Users/adam2392/Downloads/epilepsy_spes')
    source_dir = root / 'sourcedata'

    datatype = 'ieeg'
    suffix = 'ieeg'
    extension = '.edf'

    # assuming all stimulations are the same type
    stim_type = 'biphasic'

    # mapping from clinical labels to semantic meaning
    clinical_dict = {
                1:'soz', 
                2:'early spread', 3:'irritative zone',
                0:'non-epileptogenic'}

    subjects = [f.name for f in source_dir.glob('*') if f.is_dir()]
    for subject in subjects:
        subj_dir = source_dir / subject

        # get all the stimulation files
        main_stim_files = subj_dir.glob('*_.dat')

        temp_bids_path = BIDSPath(
            subject=subject, session='stim',
            root=root, datatype=datatype, suffix=suffix,
            extension=extension)

        # first loop through all main stimulation files
        for stim_fname in main_stim_files:
            params_file = str(stim_fname).replace('.dat', '_params.mat')
            clinical_file = str(stim_fname).replace('.dat', '_clinical.mat')

            # second loop through all relevant titration files
            fname_prefix = '_'.join(stim_fname.name.split('_')[:3])
            titration_files = natsorted(subj_dir.glob(f'{fname_prefix}*_titration.dat'))
            titration_files.append(stim_fname)
            for fname in titration_files:
                stim_chs, stim_amt = _extract_stim_ch(fname, subject)
                stim_amt /= 1000

                if 'titration' in fname.name:
                    task = 'titration'
                else:
                    task = 'main'

                bids_path = temp_bids_path.copy().update(
                    session=stim_chs, 
                    task=task,
                    processing=f'{stim_amt}mA'
                    )
                raw, ch_clin_labels, annotations = _convert_stimulation_file(fname, params_file, clinical_file, bids_path)

                # only Annotations of when stimulation occurred was saved for the 
                # main stimulation file, not the titrations
                if bids_path.task == 'main':
                    raw = raw.set_annotations(annotations)

                # write to BIDS
                raw._filenames = [fname]
                bids_path = write_raw_bids(raw, bids_path,
                    format='EDF', allow_preload=True, 
                    anonymize=dict(keep_source=True), overwrite=True)
                
                # augment the events.tsv 
                events_bids_path = bids_path.copy().update(extension='.tsv', suffix='events')
                if events_bids_path.fpath.exists():
                    _write_stimulation_metadata(events_bids_path, stim_type, stim_chs, stim_amt)

                # augment the channels tsv
                ch_bids_path = bids_path.copy().update(extension='.tsv', suffix='channels')
                ch_json_path = ch_bids_path.copy().update(extension='.json')
                
                ch_json = {
                    'clinical_grouping': {
                        'Description': 'Clinical annotations of epileptogenicity per channel',
                        'Levels': {
                            0: 'non-epileptogenic',
                            1: 'seizure onset zone (SOZ)',
                            2: 'early spread',
                            3: 'irritative zone',
                        }
                    }
                }
                if not ch_json_path.fpath.exists():
                    _write_json(ch_json_path, dict())
                update_sidecar_json(ch_json_path, ch_json)
                col_name = 'clinical_grouping'
                
                ch_df = pd.read_csv(ch_bids_path, sep='\t')
                ch_df[col_name] = ch_clin_labels
                ch_df.to_csv(ch_bids_path, sep='\t')

        break

if __name__ == '__main__':
    convert_jhh()   

