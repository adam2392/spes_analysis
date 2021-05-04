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
    elif subject == 'PY16N011':
        bads = ['POLE',	'POLDC01',	'POLDC02',	'POLDC03', 	'POLDC04', 	'EEGFp1Ref',	'EEGFp2Ref',	'EEGC3Ref',	'EEGC4Ref',	'EEGT7Ref', 	'EEGT8Ref', 	'EEGO1Ref',	'EEGO2Ref',	'POLEKG1',	'POLEKG2',	'EDFAnnotations']
    elif subject == 'PY17N008':
        bads = ['POLGND1', 'POLGND4', 'POLE', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLRATS1', 'POLRATS2',
                'POLEKG1', 'POLEKG2', 'EEGO1Ref', 'EEGO2Ref', 'EEGP7Ref', 'EEGP8Ref', 'EEGT7Ref', 'EEGT8Ref',
                'EEGF7Ref', 'EEGF8Ref', 'EEGFp1Ref', 'EEGFp2Ref', 'EDFAnnotations']
    elif subject == 'PY17N013':
        bads = ['POLREF1', 	'POLREF2', 	'POLE', 	'POLLCPS1', 	'POLLCPS2', 	'POLDC01', 	'POLDC02', 	'POLDC03', 	'POLDC04', 	'POLLCPS1', 	'POLLCPS2', 	'POLEKG1', 	'POLEKG2', 	'POLLFPG18', 	'POLLFPG21', 	'POLLFPG28', 	'POLLFPG32', 	'EDFAnnotations']

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

    elif subject == 'PY17N018':
        bads = ['POLE', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'EEGF7Ref', 'EEGF8Ref', 'EEGF9Ref', 'EEGF10Ref',
                'EEGFp1Ref', 'EEGFp2Ref', 'POLEKG1', 'POLEKG2', 'POLLFG33', 'EDFAnnotations']
    elif subject == 'PY17N020':
        bads = ['POLSPS4', 'POLLAC1', 'POLLAC4', 'POLLAC7', 'POLLAC8', 'POLLPC1', 'POLLPC2', 'POLLPC5', 'POLLPC7',
                'POLLPC8', 'POLLIH24', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLLIH29', 'POLLIH30', 'POLLIH31',
                'POLLIH32', 'POLLAF8', 'POLLAF9', 'EEGFp1Ref', 'EEGFp2Ref', 'EEGF9Ref', 'EEGF10Ref', 'EEGA1Ref',
                'EEGA2Ref', 'POLEKG1', 'POLEKG2', 'POLLFG2', 'POLLFG6', 'POLLFG21', 'POLLFG25', 'POLLFG26', 'POLLFG28',
                'POLLFG29', 'POLLFG30', 'POLLFG32', 'POLLFG40', 'POLLFG45', 'POLLFG47', 'POLLFG49', 'POLLFG51',
                'POLLFG53', 'POLLFG55', 'POLLFG61', 'POLLFG62', 'EDFAnnotations']
    elif subject == 'PY18N002':
        bads = ['POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLRLFD9', 'POLRLFD10', 'POLEKG1', 'POLEKG2', 'POLLHD9',
                'EEGO1Ref', 'EEGO2Ref', 'EEGT7Ref', 'EEGT8Ref', 'EEGC3Ref', 'EEGC4Ref', 'EEGF7Ref', 'EEGF8Ref',
                'EEGF3Ref', 'EEGF4Ref', 'EEGFp1Ref', 'EEGFp2Ref', 'EDFAnnotations']
    elif subject == 'PY18N003':
        bads = ['POLE', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLRHAD1', 'POLRHAD2', 'POLRFTG1', 'POLRFTG2',
                'POLRFTG16', 'POLRFTG17', 'POLRFTG33', 'POLRFTG34', 'POLRFTG49', 'POLRFTG50', 'POLEKG1', 'POLEKG2',
                'EEGFp1Ref', 'EEGFp2Ref', 'EEGF7Ref', 'EEGF8Ref', 'EEGC3Ref', 'EEGC4Ref', 'EEGA1Ref', 'EEGA2Ref',
                'EEGO1Ref', 'EEGO2Ref', 'EDFAnnotations']
    elif subject == 'PY18N007':
        bads = ['POLMOTM2', 'POLA5', 'POLA6', 'POLMOTM5', 'POLMOTL8', 'POLSENM2', 'POLSENM5', 'POLDC01', 'POLDC02',
                'POLDC03', 'POLDC04', 'POLSENL1', 'POLMOTL1', 'POLMOTL2', 'POLENCM3', 'POLENCL3', 'POLENCL5',
                'POLENCL7', 'POLPF1', 'POLPF2', 'POLPF8', 'POLPF9', 'POLPF10', 'EEGAF1Ref', 'EEGAF2Ref', 'EEGAF3Ref',
                'EEGAF4Ref', 'EEGAF5Ref', 'EEGAF6Ref', 'EEGAF7Ref', 'EEGAF8Ref', 'EEGAF9Ref', 'EEGAF10Ref', 'POLEKG1',
                'POLEKG2', 'EDFAnnotations']
    elif subject == 'PY18N013':
        bads = ['POLLHP9', 'POLLHA10', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLLHA9', 'POLLHA10', 'POLLSTP2',
                'POLLSTP4', 'POLLSTP6', 'POLLTP5', 'POLLCNA11', 'POLLCNM8', 'POLLCNS11', 'POLLSTA5', 'POLEKG1',
                'POLEKG2', 'EDFAnnotations']
    elif subject == 'PY18N016':
        bads = ['POL', 'POL', 'POLLIF8', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLLSPF3', 'POLLSPF4', 'POLLA1',
                'POLLA2', 'POLLA3', 'POLLA4', 'POLLA5', 'POLLAH3', 'POLLI2', 'POLEKG1', 'POLEKG2', 'EDFAnnotations']
    elif subject == 'PY19N012':
        bads = ['POLLCN4', 'POLLCN10', 'POLLAH8', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLLAH1', 'POLLAH2',
                'POLRNA8', 'POLEKG1', 'POLEKG2', 'EDFAnnotations']
    elif subject == 'PY19N015':
        bads = ['POL', 'POL', 'POLLHA8', 'POLLHA9', 'POLLHP2', 'POLLHP4', 'POLLHP5', 'POLLBT1', 'POLLBT2', 'POLLBT7',
                'POLLBT8', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLLFSA2', 'POLLHA1', 'POLLHA2', 'POLLFSA4',
                'POLLPT5', 'POLLPT7', 'POLLPT8', 'POLLOC2', 'POLLOC8', 'POLLINS1', 'POLLINS2', 'POLLINS3', 'POLLINS4',
                'POLLPCN1', 'POLLPCN4', 'POLLPCN6', 'POLLPCN10', 'POLLPCN11', 'POLLPCN12', 'POLRA1', 'POLRA6', 'POLRA7',
                'POLRA8', 'POLRHA7', 'POLRHA8', 'POLRHA9', 'POLRHP1', 'POLRHP8', 'POLRBT2', 'POLRBT4', 'POLRBT6',
                'POLRBT7', 'POLRBT8', 'POLEKG1', 'POLEKG2', 'POLRCG48', 'POLRCG54', 'EDFAnnotations']
    elif subject == 'PY19N017':
        bads = ['POL', 'POL', 'POLROF14', 'POLRA4', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLRF9', 'POLRF10',
                'POLRAI6', 'POLEKG1', 'POLEKG2', 'POLRTP8', 'POLLAH6', 'EEGPzRef', 'EEGCzRef', 'EEGFzRef', 'EEGO1Ref',
                'EEGO2Ref', 'EEGFp1Ref', 'EEGFp2Ref', 'EEGC3Ref', 'EEGC4Ref', 'EEGT7Ref', 'EEGF8Ref', 'EEGP3Ref',
                'EEGP4Ref', 'EEGP7Ref', 'EEGF4Ref', 'EEGF3Ref', 'EEGF7Ref', 'EDFAnnotations']
    elif subject == 'PY19N020':
        bads = ['POL', 'POL', 'POLRHA1', 'POLRHA8', 'POLRPH10', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLRAD9',
                'POLRAD10', 'POLRAI2', 'POLRAI3', 'POLRAI5', 'POLEKG1', 'POLEKG2', 'POLRAC6', 'POLLAH1', 'POLLAH2',
                'POLLAH3', 'POLLAH4', 'POLLAH5', 'POLLAH6', 'POLLAH8', 'EDFAnnotations']
    elif subject == 'PY19N023':
        bads = ['POL', 'POL', 'POLE', 'POLRAH10', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLRA9', 'POLRA10',
                'POLRMI3', 'POLEKG1', 'POLEKG2', 'POLLA10', 'POLLAH1', 'EEGFzRef', 'EEGCzRef', 'EEGPzRef', 'EEGFp1Ref',
                'EEGFp2Ref', 'EEGO1Ref', 'EEGO2Ref', 'EEGTP7Ref', 'EEGTP8Ref', 'EEGC3Ref', 'EEGC4Ref', 'EEGP7Ref',
                'EEGP8Ref', 'EEGP3Ref', 'EEGP4Ref', 'EEGF7Ref', 'EEGF8Ref', 'EEGF3Ref', 'EEGF4Ref', 'EEGF9Ref',
                'EEGF10Ref', 'EEGM1Ref', 'EEGM2Ref', 'EDFAnnotations']
    elif subject == 'PY19N026':
        bads = ['POLA5', 'POLA6', 'POLE', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLRAM9', 'POLRAM10', 'POLLAM9',
                'POLEKG1', 'POLEKG2', 'EDFAnnotations']
    elif subject == 'PY20N005':
        bads = ['POLE', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLLA9', 'POLLA10', 'POLEKG1', 'POLEKG2',
                'POLRAH10', 'EDFAnnotations']
    elif subject == 'PY21N006':
        bads = ['POLLSMA2', 'POL', 'POL', 'POLLM1', 'POLE', 'POLLACD8', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04',
                'POLLM3', 'POLLM4', 'POLEKG1', 'POLEKG2', 'EDFAnnotations']
    elif subject == 'PY21N007':
        bads = ['POL', 'POL', 'POLE', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLRA9', 'POLRH1', 'POLEKG1',
                'POLEKG2', 'POLEKG1', 'POLEKG2', 'EDFAnnotations']
    elif subject == 'PY21N008':
        bads = ['POL', 'POL', 'POLE', 'POLDC01', 'POLDC02', 'POLDC03', 'POLDC04', 'POLLA9', 'POLLA10', 'POLEKG1',
                'POLEKG2', 'EDFAnnotations']

    # set strip, grid, depth electrodes
    # raw.set_channel_types({ch: "ecog" for ch in strips})
    # raw.set_channel_types({ch: "ecog" for ch in grids})
    raw.set_channel_types({ch: "seeg" for ch in raw.ch_names if ch not in raw.info['bads']})

    # set bads
    bads = [ch.replace('POL', '').upper() for ch in bads]
    bads = [ch.replace('EEG', '') for ch in bads]
    bads = [ch.replace('REF', '') for ch in bads]
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
