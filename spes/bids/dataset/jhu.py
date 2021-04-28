def _set_ch_types(raw, subject):
    """Set channel types manually.

    bads = bad electrophsyio chs
    grids = grid electrodes
    strips = strip electrodes
    depths = depth (sEEG) electrodes
    resected = removed during resective surgery
    disconnected_chs = disconnected to facilitate surgery.
    """
    raw.set_channel_types({ch: "misc" for ch in raw.ch_names})
    ref = ""
    if subject == "PY17N002":
        # grids = [f"C{idx}" for idx in range(1, 65)]
        # strips = []
        # ref = "C15"

        # cut out grid around here and scooped all the depths
        # underneat the 4 channel grid
        resected = []

        # electrophysiologically bad
        # append bads by clinicians without resected though
        # add bad resected channels
        bads = ['POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLLOI1', 'POLLOI2', 'POLEKG1', 'POLEKG2',
                'EDFAnnotations']
    elif subject == "PY16N008":
        # grids = [f"C{idx}" for idx in range(1, 65)]
        # strips = []
        # depths = []
        resected = []
        bads = ['POL', 'POL', 'POLE', 'POLEKG1', 'POLEKG2', 'POLRPTI18', 'POLRPTI19', 'POLDC01', 'POLDC02', 'POLDC03',
                'POLDC04', 'EEGFp1Ref', 'EEGFp2Ref', 'EEGA1Ref', 'EEGA2Ref', 'EEGT7Ref', 'EEGF7Ref', 'POL', 'POL',
                'EDFAnnotations']
    elif subject == 'PY17N008':
        bads = ['POLGND1', 'POLGND4', 'POLE', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLRATS1', 'POLRATS2',
                'POLEKG1', 'POLEKG2', 'EEGO1Ref', 'EEGO2Ref', 'EEGP7Ref', 'EEGP8Ref', 'EEGT7Ref', 'EEGT8Ref',
                'EEGF7Ref', 'EEGF8Ref', 'EEGFp1Ref', 'EEGFp2Ref', 'EDFAnnotations']

    elif subject == 'PY17N014':
        bads = ['POLLOFS3', 'POLE', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLLATS1', 'POLLATS2', 'EEGF8Ref',
                'EEGT8Ref', 'EEGP8Ref', 'EEGO1Ref', 'POLEKG1', 'POLEKG2', 'POLA51', 'POLA52', 'POLA53', 'POLA54',
                'POLA55', 'POLA56', 'POLA57', 'POLA58', 'POLA59', 'POLA60', 'POLA61', 'POLA62', 'POLA63', 'POLA64',
                'EEGC1Ref', 'EEGC2Ref', 'EEGC3Ref', 'EEGC4Ref', 'EEGC5Ref', 'EEGC6Ref', 'POLC7', 'POLC8', 'POLC9',
                'POLC10', 'POLC11', 'POLC12', 'POLC13', 'POLC14', 'POLC15', 'POLC16', 'POLC17', 'POLC18', 'POLC19',
                'POLC20', 'POLC21', 'POLC22', 'POLC23', 'POLC24', 'POLC25', 'POLC26', 'POLC27', 'POLC28', 'POLC29',
                'POLC30', 'POLC31', 'POLC32', 'POLC33', 'POLC34', 'POLC35', 'POLC36', 'POLC37', 'POLC38', 'POLC39',
                'POLC40', 'POLC41', 'POLC42', 'POLC43', 'POLC44', 'POLC45', 'POLC46', 'POLC47', 'POLC48', 'POLC49',
                'POLC50', 'POLC51', 'POLC52', 'POLC53', 'POLC54', 'POLC55', 'POLC56', 'POLC57', 'POLC58', 'POLC59',
                'POLC60', 'POLC61', 'POLC62', 'POLC63', 'POLC64', 'EDFAnnotations']

    elif subject == 'PY18N002':
        bads = ['POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLRLFD9', 'POLRLFD10', 'POLEKG1', 'POLEKG2', 'POLLHD9',
                'EEGO1Ref', 'EEGO2Ref', 'EEGT7Ref', 'EEGT8Ref', 'EEGC3Ref', 'EEGC4Ref', 'EEGF7Ref', 'EEGF8Ref',
                'EEGF3Ref', 'EEGF4Ref', 'EEGFp1Ref', 'EEGFp2Ref', 'EDFAnnotations']
    elif subject == 'PY18N003':
        bads = ['POLE',	'POLDC01',	'POLDC02',	'POLDC03',	'POLDC04',	'POLRHAD1',	'POLRHAD2',	'POLRFTG1',	'POLRFTG2',	'POLRFTG16',	'POLRFTG17',	'POLRFTG33',	'POLRFTG34',	'POLRFTG49',	'POLRFTG50',	'POLEKG1',	'POLEKG2',	'EEGFp1Ref',	'EEGFp2Ref',	'EEGF7Ref',	'EEGF8Ref',	'EEGC3Ref',	'EEGC4Ref',	'EEGA1Ref',	'EEGA2Ref',	'EEGO1Ref',	'EEGO2Ref',	'EDFAnnotations']
    # set strip, grid, depth electrodes
    # raw.set_channel_types({ch: "ecog" for ch in strips})
    # raw.set_channel_types({ch: "ecog" for ch in grids})
    raw.set_channel_types({ch: "seeg" for ch in raw.ch_names if ch not in raw.info['bads']})

    # set bads
    bads = [ch.replace('POL', '') for ch in bads]
    bads = [ch for ch in bads if ch in raw.ch_names]
    raw.info['bads'].extend(bads)
    # raw.info["bads"].extend(bads.keys())
    # raw.info["bads_description"] = bads

    # return channel mapping
    # ch_mapping = {
    #     "grid": grids,
    #     "strip": strips,
    #     "depth": depths,
    #     "resected": resected,
    #     "reference": ref,
    # }
    # return ch_mapping
    return raw