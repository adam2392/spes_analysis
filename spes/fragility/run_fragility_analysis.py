import logging
from pathlib import Path

import mne
import numpy as np
import pandas as pd
from eztrack.fragility import lds_raw_fragility
from eztrack.utils import logger
from mne.utils import warn
from mne_bids import BIDSPath, get_entity_vals

from spes.read import load_data

logger.setLevel(logging.DEBUG)


def run_analysis(
        bids_path,
        reference="monopolar",
        resample_sfreq=None,
        deriv_path=None,
        figures_path=None,
        verbose=True,
        overwrite=False,
        plot_heatmap=True,
        plot_raw=True,
        **model_params,
):
    n_jobs = 3
    subject = bids_path.subject
    root = bids_path.root

    # get the root derivative path
    deriv_chain = Path("fragility") / reference / f"sub-{subject}"
    raw_figures_path = root / "derivatives" / "figures" / "raw" / f"sub-{subject}"
    figures_path = figures_path / deriv_chain
    deriv_path = deriv_path / deriv_chain

    # check if we have original dataset
    source_basename = bids_path.copy().update(extension=None, suffix=None).basename
    deriv_fpaths = deriv_path.glob(f"{source_basename}*.npy")
    if not overwrite and len(list(deriv_fpaths)) > 0:
        warn(
            f"Not overwrite and the derivative file path for {source_basename} already exists. "
            f"Skipping..."
        )
        return

    # load in raw data
    raw = load_data(
        bids_path, resample_sfreq, raw_figures_path, plot_raw=plot_raw, verbose=verbose
    )

    # use the same basename to save the data
    raw.drop_channels(raw.info["bads"])

    print(f"Analyzing {raw} with {len(raw.ch_names)} channels.")

    order = model_params.get("order", 1)

    l2penalty = raw.get_data().min() * 1e-2
    print(f"Data l2 penalty: {l2penalty}")
    l2penalty = 1e-9
    # l2penalty = 1
    print(f"Going to use l2penalty: {l2penalty}")
    model_params = {
        "winsize": 250,
        "stepsize": 125,
        "radius": 1.5,
        "method_to_use": "pinv",
        # "fb": True,
        "l2penalty": l2penalty,
    }
    # run heatmap
    perturb_deriv, state_arr_deriv, delta_vecs_arr_deriv = lds_raw_fragility(
        raw,
        order=order,
        reference=reference,
        return_all=True,
        n_jobs=n_jobs,
        **model_params,
    )

    # save the files
    perturb_deriv_fpath = deriv_path / perturb_deriv.info._expected_basename
    state_deriv_fpath = deriv_path / state_arr_deriv.info._expected_basename
    delta_vecs_deriv_fpath = deriv_path / delta_vecs_arr_deriv.info._expected_basename

    print("Saving files to: ")
    print(perturb_deriv_fpath)
    print(state_deriv_fpath)
    print(delta_vecs_deriv_fpath)
    perturb_deriv.save(perturb_deriv_fpath, overwrite=overwrite)
    state_arr_deriv.save(state_deriv_fpath, overwrite=overwrite)
    delta_vecs_arr_deriv.save(delta_vecs_deriv_fpath, overwrite=overwrite)

    # normalize and plot heatmap
    if plot_heatmap:
        figures_path.mkdir(exist_ok=True, parents=True)
        perturb_deriv.normalize()
        fig_basename = perturb_deriv_fpath.with_suffix(".pdf").name

        bids_path.update(suffix="channels", extension=".tsv")

        # read in vertical markers
        vertical_markers = {}
        events, event_id = mne.events_from_annotations(perturb_deriv)
        if "sz event" in event_id:
            _id = event_id.get("eeg sz onset")
            sz_onset = int(events[np.argwhere(events[:, -1] == _id), 0].squeeze())
            print(sz_onset)
            vertical_markers[sz_onset] = "seizure onset"
        # if "eeg sz offset" in event_id:
        #     _id = event_id.get("eeg sz offset")
        #     sz_offset = int(events[np.argwhere(events[:, -1] == _id), 0].squeeze())
        #     vertical_markers[sz_offset] = "seizure offset"

        # read in sidecar channels.tsv
        channels_pd = pd.read_csv(bids_path.fpath, sep="\t")
        description_chs = pd.Series(
            channels_pd.description.values, index=channels_pd.name
        ).to_dict()
        print(description_chs)
        resected_chs = [
            ch
            for ch, description in description_chs.items()
            if description == "resected"
        ]
        print(f"Resected channels are {resected_chs}")

        print(f"saving figure to {figures_path} {fig_basename}")
        perturb_deriv.plot_heatmap(
            soz_chs=resected_chs,
            cbarlabel="Fragility",
            cmap="turbo",
            vertical_markers=vertical_markers,
            # soz_chs=soz_chs,
            # figsize=(10, 8),
            # fontsize=12,
            # vmax=0.8,
            title=fig_basename,
            figure_fpath=(figures_path / fig_basename),
        )


def main_run_jhu():
    # the root of the BIDS dataset
    WORKSTATION = "home"

    if WORKSTATION == "home":
        # bids root to write BIDS data to
        # the root of the BIDS dataset
        root = Path("/Users/adam2392/Johns Hopkins/Rachel Smith - Ictal Clips/")
        # root = Path("/Users/adam2392/Dropbox/resection_tvb/")
        deriv_root = root / "derivatives" / "originalsampling" / "radius1.5"
        figures_path = deriv_root / "figures"
    elif WORKSTATION == "lab":
        root = Path("/home/adam2392/hdd/epilepsy_bids/")

    # define BIDS entities
    SUBJECTS = []
    acquisition = 'seeg'
    datatype = "ieeg"
    extension = ".vhdr"
    task = 'ictal'
    session = "extraoperative"  # only one session

    # derivative analysis parameters
    reference = "monopolar"
    order = 1
    sfreq = None
    overwrite = False

    # get the runs for this subject
    all_subjects = get_entity_vals(root, "subject")
    for subject in all_subjects:
        # if subject not in SUBJECTS:
        #     continue
        ignore_subs = [sub for sub in all_subjects if sub != subject]

        # get all sessions
        # sessions = get_entity_vals(root, "session", ignore_subjects=ignore_subs)
        # for session in sessions:
        #     if session not in SESSIONS:
        #         continue
        #     ignore_sessions = [ses for ses in sessions if ses != session]
        ignore_set = {
            "ignore_subjects": ignore_subs,
            # "ignore_sessions": ignore_sessions,
        }
        print(f"Ignoring these sets: {ignore_set}")
        runs = get_entity_vals(root, "run", **ignore_set)
        print(f"Found {runs} runs for {task} task.")

        for idx, run in enumerate(runs):
            # create path for the dataset
            bids_path = BIDSPath(
                subject=subject,
                session=session,
                task=task,
                run=run,
                datatype=datatype,
                acquisition=acquisition,
                suffix=datatype,
                root=root,
                extension=extension,
            )
            print(f"Analyzing {bids_path}")

            run_analysis(
                bids_path,
                reference=reference,
                resample_sfreq=sfreq,
                deriv_path=deriv_root,
                figures_path=figures_path,
                plot_heatmap=True,
                plot_raw=True,
                overwrite=overwrite,
                order=order,
            )


if __name__ == "__main__":
    main_run_jhu()
