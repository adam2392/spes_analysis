import os
import os
import random
from pathlib import Path
from typing import Dict

from eztrack.preprocess.bids_conversion import (
    append_original_fname_to_scans,
)
from mne.io import read_raw_edf
from mne_bids import write_raw_bids, read_raw_bids, get_anonymization_daysback
from mne_bids.path import BIDSPath, _find_matching_sidecar
from natsort import natsorted

from spes.bids.dataset.jhu import (
    _set_ch_types,
)
from spes.bids.utils import (
    _check_bids_parameters,
    _look_for_bad_channels,
    _channel_text_scrub,
)


def write_edf_to_bids(
        edf_fpath: [str, Path],
        bids_kwargs: Dict,
        bids_root: [str, Path],
        line_freq: int = 60,
        montage=None,
        dataset_name=None,
        source_dir=None,
        overwrite: bool = False,
) -> Dict:
    """Write EDF (.edf) files to BIDS format.

    This will convert files to BrainVision (.vhdr, .vmrk, .eeg) data format
    in the BIDS-compliant file-layout.

    The passed in BIDS keyword arguments must adhere to a certain standard.
    Namely, they should include::

        - ``subject``
        - ``session``
        - ``task``
        - ``acquisition``
        - ``run``
        - ``datatype``

    Parameters
    ----------
    edf_fpath : str | Path
    bids_kwargs : dict
    bids_root : str | Path
    line_freq : int

    Returns
    -------
    status_dict : dict
        The resulting status of the BIDS conversion.
    """
    # do check on BIDS kwarg parameters
    entities = _check_bids_parameters(bids_kwargs)

    # construct the BIDS path that the file will get written to
    bids_path = BIDSPath(**entities, root=bids_root)

    # load in EDF file
    raw = read_raw_edf(edf_fpath)

    # set line freq
    raw.info["line_freq"] = line_freq

    subject = bids_path.subject
    # make fake np.nan montage
    # if montage is None:
    #     ch_pos = {ch_name: [np.nan] * 3 for ch_name in raw.ch_names}
    #     montage = make_dig_montage(ch_pos=ch_pos, coord_frame="mri")
    # raw.set_montage(montage, on_missing="ignore")

    # channel text scrub
    raw = _channel_text_scrub(raw)

    # look for bad channels
    bad_chs = _look_for_bad_channels(raw.ch_names)
    print(f'Found bad channels: {bad_chs}')
    raw.info["bads"].extend(bad_chs)

    if dataset_name == "jhu":
        raw = _set_ch_types(raw, subject)

    # Get acceptable range of days back and pick random one
    daysback_min, daysback_max = get_anonymization_daysback(raw)
    daysback = random.randrange(daysback_min, daysback_max)
    anonymize = dict(daysback=1, keep_his=False)

    # write to BIDS based on path
    output_bids_path = write_raw_bids(
        raw, bids_path=bids_path,
        anonymize=anonymize, format='BrainVision',
        overwrite=overwrite, verbose=False
    )

    # add resected channels to description
    print(f"output bids path: {output_bids_path}")
    channels_tsv_fname = _find_matching_sidecar(
        output_bids_path, suffix="channels", extension=".tsv", on_error="ignore"
    )
    print(f"The channels tsv file is... {channels_tsv_fname}")
    electrodes_tsv_fname = _find_matching_sidecar(
        output_bids_path, suffix="electrodes", extension=".tsv", on_error="ignore"
    )
    print(f"The electrodes tsv file is... {electrodes_tsv_fname}")

    # output status dictionary
    status_dict = {
        "status": 1,
        "output_fname": output_bids_path.basename,
        "original_fname": os.path.basename(edf_fpath),
    }
    return status_dict


def convert_jhu_dataset():
    WORKSTATION = "home"

    if WORKSTATION == "home":
        # bids root to write BIDS data to
        bids_root = Path("/Users/adam2392/Johns Hopkins/Rachel Smith - Ictal Clips/")
        source_dir = bids_root / "sourcedata"

    elif WORKSTATION == "lab":
        bids_root = Path("/home/adam2392/hdd2/epilepsy_bids/")
        source_dir = Path("/home/adam2392/hdd2/epilepsy_bids/sourcedata")

    # define BIDS identifiers
    modality = "seeg"
    task = "ictal"
    session = 'extraoperative'
    datatype = "ieeg"
    line_freq = 60
    overwrite = True
    verbose = True

    ignore_subjects = [
        'PY16N008',
        'PY16N011', 'PY17N002'
        'PY17N008'
    ]

    subject_ids = natsorted([fdir.name for fdir in source_dir.glob('PY*') if fdir.is_dir()])
    subject_ids = [s for s in subject_ids if s not in ignore_subjects]
    print(subject_ids)
    participants_json_fname = os.path.join(bids_root, "participants.json")
    participants_tsv_fname = os.path.join(bids_root, "participants.tsv")

    # for subject in subject_ids:
    #     add_data_to_participants(subject, bids_root)
    #
    # exit(1)
    for subject in subject_ids:
        source_folder = source_dir / subject

        search_str = f"Sz_*.edf"
        filepaths = source_folder.glob(search_str)
        for run_id, fpath in enumerate(filepaths):
            # subject = fpath.name.split("_")[0]
            # if subject not in subject_ids:
            #     print("wtf?")
            #     continue

            # get the next available run
            run_id = run_id + 1

            bids_kwargs = {
                "subject": subject,
                "session": session,
                "task": task,
                "acquisition": modality,
                "run": run_id,
                "datatype": datatype,
                "suffix": datatype,
            }
            print(bids_kwargs)

            # run main bids conversion
            output_dict = write_edf_to_bids(
                edf_fpath=fpath,
                bids_kwargs=bids_kwargs,
                bids_root=bids_root,
                line_freq=line_freq,
                dataset_name="jhu",
                source_dir=source_dir,
                overwrite=overwrite
            )
            bids_fname = output_dict["output_fname"]

            # append scans original filenames
            append_original_fname_to_scans(fpath.name, bids_root, bids_fname)

            bids_path = BIDSPath(**bids_kwargs, root=bids_root)
            print(bids_path.fpath)
            raw = read_raw_bids(bids_path)


if __name__ == "__main__":
    convert_jhu_dataset()
    exit(1)
