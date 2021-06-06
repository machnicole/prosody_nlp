
import os
import re
import glob
from collections import Counter
import pickle


def get_stats_eng(lang, time):
    sentence_id2recording = dict()
    sentence_id2speaker = dict()

    wor_counter = 0
    mau_counter = 0
    no_time_info = 0

    total_syntactic_trees = 0
    total_sentences = 0
    total_phrases = 0
    total_tokens = 0
    total_tokens_with_time_info = 0
    links_to_recordings = []
    no_recording = []
    dialogs = set()
    speaker = set()

    for export_filename, tree_filename in zip(os.listdir(path_to_vm_exports),
                                              os.listdir(path_to_vm_trees)):
        # open export file
        with open(os.path.join(path_to_vm_exports, export_filename), "r",
                  encoding="ISO-8859-1") as export_file:

            id_prefix = export_filename.split(".")[0]
            recordings_for_id_prefix = True
            # no recordings, just english translations
            if id_prefix == "cd15english_00":
                continue
            if id_prefix == "cd32english_00":
                continue


            # open tree file
            with open(os.path.join(path_to_vm_trees, tree_filename), "r",
                      encoding="ISO-8859-1") as tree_file:
                sentence_ids_from_trees = []
                links_to_recordings_per_file = []


                for line in tree_file:
                    get_sent_id = re.search('%% sent.\sno.\s(\d+)', line)
                    if get_sent_id:
                        sentence_ids_from_trees.append(get_sent_id.group(1))
                if sentence_ids_from_trees == []:
                    print("No sentence IDs in tree file found:", tree_filename)


                syntactic_trees_in_file = len(sentence_ids_from_trees)

            for line in export_file:
                # recording ids have a strange number at the end - maybe important but removed for now
                if lang == "eng":
                    re_sent_tokens_phrases = re.search("%% (\d+) sentences \((\d+) tokens, (\d+) phrases\)", line)
                    if re_sent_tokens_phrases:
                        sentences = re_sent_tokens_phrases.group(1)
                        tokens = re_sent_tokens_phrases.group(2)
                        phrases = re_sent_tokens_phrases.group(3)
                    else:
                        sentences = 0
                        tokens = 0
                        phrases = 0

                    # only match german IDs
                    re_link_to_recording = re.search(
                        '#BOS\s(\d+).*?<.*?((?:e|m|s id=r)(?:\S*?\w{3}|))(_\d+)?>', line)

                    if re_link_to_recording:
                        assumed_sentence_id = re_link_to_recording.group(1)
                        link_to_recording = re_link_to_recording.group(2)
                        if link_to_recording.startswith("s id=r"):
                            link_to_recording = link_to_recording[5:] # get rid of s id=
                            speakerID = link_to_recording[6:9]
                            turn_number = link_to_recording[9:12]
                            link_to_recording = link_to_recording[:6] + turn_number + "_" + speakerID
                            # print(link_to_recording)
                    else:
                        assumed_sentence_id = ""
                        link_to_recording = ""
                # each sentence from the tree file should be linked to a recording

                if link_to_recording:
                    # 14th - 16th character:
                    #       <sp_id> speaker ID
                    # dialog name (char 1-5)
                    recording_infos = link_to_recording.split("_")
                    dialog_name = recording_infos[0][0:5]
                    turn_number = recording_infos[1]
                    speakerID = recording_infos[-1]
                    # dialog_name = link_to_recording[0:5]
                    # turn_number = link_to_recording[0:5]
                    # speakerID = link_to_recording[13:16]

                    links_to_recordings_per_file.append(link_to_recording)
                    links_to_recordings.append(link_to_recording)

                    if glob.glob(path_to_vm_annotations_2 + "/"
                                         + dialog_name + "/" + "*_"
                                         + turn_number + "_" + speakerID + ".par"):
                        file = glob.glob(path_to_vm_annotations_2 + "/"
                                         + dialog_name + "/" + "*_"
                                         + turn_number + "_" + speakerID + ".par")
                        if len(file) == 1:
                            file = file[0]
                        else:
                            print("Something off with file pattern matching", file)

                        with open(file, "r", encoding = "ISO-8859-1") as parfile:
                            partext = parfile.read()

                            # check if some time information exists
                            wor = re.search('WOR', partext)
                            mau = re.search('MAU', partext)
                            tr2 = re.findall('TR2:\s\d+\s.*', partext)

                            if wor:
                                wor_counter += 1
                                time_info = True
                            elif mau:
                                mau_counter += 1
                                time_info = True
                            else:
                                no_time_info += 1
                                time_info = False

                            token_number = int(tr2[-1].split("\t")[1])
                            # last token number + 1 = number of tokens in the turn
                        if time:
                            time_info = time_info
                        else:
                            time_info = True
                        if time_info:
                            link_to_wav_file = file[:-4]
                            if glob.glob(link_to_wav_file + ".wav"):
                                sentence_id2recording[id_prefix+"_"+assumed_sentence_id] = link_to_wav_file + ".wav"
                                sentence_id2speaker[id_prefix+"_"+assumed_sentence_id] = speakerID
                                dialogs.add(dialog_name)
                                speaker.add(speakerID)
                                total_tokens_with_time_info += token_number
                            elif glob.glob(link_to_wav_file + "_ENG.wav"):
                                sentence_id2recording[
                                    id_prefix + "_" + assumed_sentence_id] = link_to_wav_file + "_ENG.wav"
                                sentence_id2speaker[
                                    id_prefix + "_" + assumed_sentence_id] = speakerID
                                dialogs.add(dialog_name)
                                speaker.add(speakerID)
                                total_tokens_with_time_info += token_number
                            else:
                                print("No wav file found!", link_to_wav_file)

                    elif glob.glob(path_to_vm_annotations_1 + "/"
                                         + dialog_name + "/" + "*_"
                                         + turn_number + "_" + speakerID + ".par"):
                        file = glob.glob(path_to_vm_annotations_1 + "/"
                                         + dialog_name + "/" + "*_"
                                         + turn_number + "_" + speakerID + ".par")
                        if len(file) == 1:
                            file = file[0]
                        else:
                            print("Something off with file pattern matching", file)
                        with open(file, "r", encoding = "ISO-8859-1") as parfile:
                            partext = parfile.read()
                            wor = re.search('WOR', partext)
                            mau = re.search('MAU', partext)
                            tr2 = re.findall('TR2:\s\d+\s.*', partext)

                            if wor:
                                wor_counter += 1
                                time_info = True
                            elif mau:
                                mau_counter += 1
                                time_info = True
                            else:
                                no_time_info += 1
                                time_info = False

                            token_number = int(tr2[-1].split("\t")[1])
                            # last token number + 1 = number of tokens in the turn
                        if time:
                            time_info = time_info
                        else:
                            time_info = True
                        if time_info:
                            link_to_wav_file = file[:-4]
                            if glob.glob(link_to_wav_file + ".wav"):
                                sentence_id2recording[id_prefix+"_"+assumed_sentence_id] = link_to_wav_file + ".wav"
                                sentence_id2speaker[
                                    id_prefix + "_" + assumed_sentence_id] = speakerID
                                dialogs.add(dialog_name)
                                speaker.add(speakerID)
                                total_tokens_with_time_info += token_number

                            elif glob.glob(link_to_wav_file + "_ENG.wav"):
                                sentence_id2recording[
                                    id_prefix + "_" + assumed_sentence_id] = link_to_wav_file + "_ENG.wav"
                                sentence_id2speaker[
                                    id_prefix + "_" + assumed_sentence_id] = speakerID
                                dialogs.add(dialog_name)
                                speaker.add(speakerID)
                                total_tokens_with_time_info += token_number

                            else:
                                print("No wav file found!")
                    else:
                        # we have a sentence from a tree file with no recording!
                        no_recording.append(id_prefix + "_" + assumed_sentence_id)
                        recordings_for_id_prefix = False

            if len(sentence_ids_from_trees) != len(links_to_recordings_per_file):
                print("ID has no recording link")

            if recordings_for_id_prefix:
                total_syntactic_trees += syntactic_trees_in_file
                total_sentences += int(sentences)
                total_phrases += int(phrases)
                total_tokens += int(tokens)

    print("Pickling sentence_id2recording dictionary...")
    with open('sentence_id2recording_eng.pickle', 'wb') as handle:
        pickle.dump(sentence_id2recording, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print("Pickling sentence_id2speaker dictionary...")
    with open('sentence_id2speaker_eng.pickle', 'wb') as handle:
        pickle.dump(sentence_id2speaker, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # this information is not really relevant
    print("Total syntactic trees/sentences:", total_syntactic_trees)
    print("Links to recordings:", len(links_to_recordings))

    print("Total sentences:", total_sentences)
    print("Total phrases:", total_phrases)
    print("Total tokens:", total_tokens)
    print("WOR annotation:", wor_counter)
    print("MAU annotation:", mau_counter)
    print("No time info:", no_time_info)
    print("No recording:", len(no_recording))
    # print(no_recording)
    print("Number of sentences with time info:", len(sentence_id2recording))
    print("Number of turns:", len(set(sentence_id2recording.values())))
    print("Number of tokens in those turns", total_tokens_with_time_info)
    print("Number of speakers:", len(speaker))
    print("Number of dialogs:", len(dialogs))

    sexes = list()
    dialects = list()



    for speakerID in speaker:
        if glob.glob(os.path.join(path_to_vm_spr_2, "e_"+speakerID.lower()+".spr")):
            with open(os.path.join(path_to_vm_spr_2, "e_"+speakerID.lower()+".spr"), "r", encoding = "ISO-8859-1") as sprfile:
                for line in sprfile:
                    sex = re.search('sex\s(\w)', line)
                    dialect = re.search('dialect\s(.*)', line)
                    if sex:
                        sexes.append(sex.group(1))
                    if dialect: # dialect info only in VM2
                        dialects.append(dialect.group(1))
        elif glob.glob(os.path.join(path_to_vm_annotations_1, "AufDat.csv")):
            with open(os.path.join(path_to_vm_annotations_1, "AufDat.csv"),
                      "r",
                      encoding="ISO-8859-1") as csvfile:
                for line in csvfile:
                    line_list = line.split("\t")
                    if line_list[14] == speakerID:
                        sexes.append(line_list[15])
                    elif line_list[23] == speakerID:
                        sexes.append(line_list[24])
        else:
            print("No speaker info found.")

    print("Sexes:",Counter(sexes))
    print("Dialects:",Counter(dialects))


def get_stats(lang, time):
    sentence_id2recording = dict()

    wor_counter = 0
    mau_counter = 0
    no_time_info = 0

    total_syntactic_trees = 0
    total_sentences = 0
    total_phrases = 0
    total_tokens = 0
    total_tokens_with_time_info = 0
    links_to_recordings = []
    no_recording = []
    dialogs = set()
    speaker = set()

    for export_filename, tree_filename in zip(os.listdir(path_to_vm_exports),
                                              os.listdir(path_to_vm_trees)):
        # open export file
        with open(os.path.join(path_to_vm_exports, export_filename), "r",
                  encoding="ISO-8859-1") as export_file:

            id_prefix = export_filename.split(".")[0]
            recordings_for_id_prefix = True
            # we don't have siemens recordings
            if id_prefix == "siemens":
                continue

            # open tree file
            with open(os.path.join(path_to_vm_trees, tree_filename), "r",
                      encoding="ISO-8859-1") as tree_file:
                sentence_ids_from_trees = []
                links_to_recordings_per_file = []


                for line in tree_file:
                    get_sent_id = re.search('%% sent.\sno.\s(\d+)', line)
                    if get_sent_id:
                        sentence_ids_from_trees.append(get_sent_id.group(1))
                if sentence_ids_from_trees == []:
                    print("No sentence IDs in tree file found:", tree_filename)


                syntactic_trees_in_file = len(sentence_ids_from_trees)

            for line in export_file:
                # recording ids have a strange number at the end - maybe important but removed for now
                if lang == "ger":
                    re_sent_tokens_phrases = re.search("%% (\d+) sentences \((\d+) tokens, (\d+) phrases\)", line)
                    if re_sent_tokens_phrases:
                        sentences = re_sent_tokens_phrases.group(1)
                        tokens = re_sent_tokens_phrases.group(2)
                        phrases = re_sent_tokens_phrases.group(3)
                    else:
                        sentences = 0
                        tokens = 0
                        phrases = 0

                    # only match german IDs
                    re_link_to_recording = re.search(
                        '#BOS\s(\d+).*?<.*?((?:g|m).*?\w)_\d+>', line)

                    if re_link_to_recording:
                        assumed_sentence_id = re_link_to_recording.group(1)
                        link_to_recording = re_link_to_recording.group(2)
                    else:
                        assumed_sentence_id = ""
                        link_to_recording = ""
                # each sentence from the tree file should be linked to a recording

                if link_to_recording:
                    # 14th - 16th character:
                    #       <sp_id> speaker ID
                    # dialog name (char 1-5)
                    recording_infos = link_to_recording.split("_")
                    dialog_name = recording_infos[0][0:5]
                    turn_number = recording_infos[1]
                    speakerID = recording_infos[-1]

                    links_to_recordings_per_file.append(link_to_recording)
                    links_to_recordings.append(link_to_recording)

                    # link_to_par_file_vm2 = path_to_vm_annotations_2\
                    #                    + "/"+ link_to_recording[0:5] + "/"\
                    #                    + link_to_recording + ".par"
                    #
                    # link_to_par_file_vm1 = path_to_vm_annotations_1 \
                    #                        + "/"+ link_to_recording[0:5] + "/" \
                    #                        + link_to_recording + ".par"

                    if glob.glob(path_to_vm_annotations_2 + "/"
                                 + dialog_name + "/" + "*_"
                                 + turn_number + "_" + speakerID + ".par"):
                        file = glob.glob(path_to_vm_annotations_2 + "/"
                                         + dialog_name + "/" + "*_"
                                         + turn_number + "_" + speakerID + ".par")
                        # if len(file) == 1:
                        file = file[0]
                        # else:
                        #     print("Something off with file pattern matching",
                        #           file)

                        with open(file, "r", encoding = "ISO-8859-1") as parfile:
                            partext = parfile.read()

                            # check if some time information exists
                            wor = re.search('WOR', partext)
                            mau = re.search('MAU', partext)
                            tr2 = re.findall('TR2:\s\d+\s.*', partext)

                            if wor:
                                wor_counter += 1
                                time_info = True
                            elif mau:
                                mau_counter += 1
                                time_info = True
                            else:
                                no_time_info += 1
                                time_info = False

                            token_number = int(tr2[-1].split("\t")[1])
                            # last token number + 1 = number of tokens in the turn
                        if time:
                            time_info = time_info
                        else:
                            time_info = True
                        if time_info:
                            link_to_wav_file = file[:-4]
                            if glob.glob(link_to_wav_file + ".wav"):
                                sentence_id2recording[id_prefix+"_"+assumed_sentence_id] = link_to_wav_file + ".wav"
                                dialogs.add(dialog_name)
                                speaker.add(speakerID)
                                total_tokens_with_time_info += token_number
                            elif glob.glob(link_to_wav_file + "_GER.wav"):
                                sentence_id2recording[
                                    id_prefix + "_" + assumed_sentence_id] = link_to_wav_file + "_GER.wav"
                                dialogs.add(dialog_name)
                                speaker.add(speakerID)
                                total_tokens_with_time_info += token_number
                            else:
                                print("No wav file found!", link_to_wav_file)

                    elif glob.glob(path_to_vm_annotations_1 + "/"
                                   + dialog_name + "/" + "*_"
                                   + turn_number + "_" + speakerID + ".par"):
                        file = glob.glob(path_to_vm_annotations_1 + "/"
                                         + dialog_name + "/" + "*_"
                                         + turn_number + "_" + speakerID + ".par")
                        # if len(file) == 1:
                        file = file[0]
                        # else:
                        #     print(
                        #         "Something off with file pattern matching",
                        #         file)

                        with open(file, "r", encoding = "ISO-8859-1") as parfile:
                            partext = parfile.read()
                            wor = re.search('WOR', partext)
                            mau = re.search('MAU', partext)
                            tr2 = re.findall('TR2:\s\d+\s.*', partext)

                            if wor:
                                wor_counter += 1
                                time_info = True
                            elif mau:
                                mau_counter += 1
                                time_info = True
                            else:
                                no_time_info += 1
                                time_info = False

                            token_number = int(tr2[-1].split("\t")[1])
                            # last token number + 1 = number of tokens in the turn
                        if time:
                            time_info = time_info
                        else:
                            time_info = True
                        if time_info:
                            link_to_wav_file = file[:-4]

                            if glob.glob(link_to_wav_file + ".wav"):
                                sentence_id2recording[id_prefix+"_"+assumed_sentence_id] = link_to_wav_file + ".wav"
                                dialogs.add(dialog_name)
                                speaker.add(speakerID)
                                total_tokens_with_time_info += token_number

                            elif glob.glob(link_to_wav_file + "_GER.wav"):
                                sentence_id2recording[
                                    id_prefix + "_" + assumed_sentence_id] = link_to_wav_file + "_GER.wav"
                                dialogs.add(dialog_name)
                                speaker.add(speakerID)
                                total_tokens_with_time_info += token_number

                            else:
                                print("No wav file found!")
                    else:
                        # we have a sentence from a tree file with no recording!
                        no_recording.append(id_prefix + "_" + assumed_sentence_id)
                        recordings_for_id_prefix = False

            if len(sentence_ids_from_trees) != len(links_to_recordings_per_file):
                print("ID has no recording link")

            if recordings_for_id_prefix:
                total_syntactic_trees += syntactic_trees_in_file
                total_sentences += int(sentences)
                total_phrases += int(phrases)
                total_tokens += int(tokens)

    # this information is not really relevant
    print("Total syntactic trees/sentences:", total_syntactic_trees)
    print("Links to recordings:", len(links_to_recordings))

    print("Total sentences:", total_sentences)
    print("Total phrases:", total_phrases)
    print("Total tokens:", total_tokens)
    print("WOR annotation:", wor_counter)
    print("MAU annotation:", mau_counter)
    print("No time info:", no_time_info)
    print("No recording:", len(no_recording))
    print("Number of sentences with time info:", len(sentence_id2recording))
    print("Number of turns:", len(set(sentence_id2recording.values())))
    print("Number of tokens in those turns", total_tokens_with_time_info)
    print("Number of speakers:", len(speaker))
    print("Number of dialogs:", len(dialogs))

    sexes = list()
    dialects = list()



    for speakerID in speaker:
        if glob.glob(os.path.join(path_to_vm_spr_2, "g_"+speakerID.lower()+".spr")):
            with open(os.path.join(path_to_vm_spr_2, "g_"+speakerID.lower()+".spr"), "r", encoding = "ISO-8859-1") as sprfile:
                for line in sprfile:
                    sex = re.search('sex\s(\w)', line)
                    dialect = re.search('dialect\s(.*)', line)
                    if sex:
                        sexes.append(sex.group(1))
                    if dialect: # dialect info only in VM2
                        dialects.append(dialect.group(1))
        elif glob.glob(os.path.join(path_to_vm_annotations_1, "AufDat.csv")):
            with open(os.path.join(path_to_vm_annotations_1, "AufDat.csv"),
                      "r",
                      encoding="ISO-8859-1") as csvfile:
                for line in csvfile:
                    line_list = line.split("\t")
                    if line_list[14] == speakerID:
                        sexes.append(line_list[15])
                    elif line_list[23] == speakerID:
                        sexes.append(line_list[24])
        else:
            print("No speaker info found.")

    print("Sexes:",Counter(sexes))
    print("Dialects:",Counter(dialects))





    # print(no_recording)



def get_stats_jap(lang, time):
    sentence_id2recording = dict()

    wor_counter = 0
    mau_counter = 0
    no_time_info = 0

    total_syntactic_trees = 0
    total_sentences = 0
    total_phrases = 0
    total_tokens = 0
    total_tokens_with_time_info = 0
    links_to_recordings = []
    no_recording = []
    dialogs = set()
    speaker = set()

    for export_filename in os.listdir(path_to_vm_exports):
        # open export file
        with open(os.path.join(path_to_vm_exports, export_filename), "r",
                  encoding="ISO-8859-1") as export_file:

            id_prefix = export_filename.split(".")[0]
            recordings_for_id_prefix = True

            for line in export_file:
                # recording ids have a strange number at the end - maybe important but removed for now
                if lang == "jap":
                    re_sent_tokens_phrases = re.search("%% (\d+) sentences \((\d+) tokens, (\d+) phrases\)", line)
                    if re_sent_tokens_phrases:
                        sentences = re_sent_tokens_phrases.group(1)
                        tokens = re_sent_tokens_phrases.group(2)
                        phrases = re_sent_tokens_phrases.group(3)
                    else:
                        sentences = 0
                        tokens = 0
                        phrases = 0

                    # only match german IDs
                    re_link_to_recording = re.search(
                        '#BOS\s(\d+).*?<.*?((?:j|m).*?\w)_\d+>', line)

                    if re_link_to_recording:
                        assumed_sentence_id = re_link_to_recording.group(1)
                        link_to_recording = re_link_to_recording.group(2)
                    else:
                        assumed_sentence_id = ""
                        link_to_recording = ""
                # each sentence from the tree file should be linked to a recording

                if link_to_recording:
                    # 14th - 16th character:
                    #       <sp_id> speaker ID
                    # dialog name (char 1-5)
                    recording_infos = link_to_recording.split("_")
                    dialog_name = recording_infos[0][0:5]
                    turn_number = recording_infos[1]
                    speakerID = recording_infos[-1]

                    links_to_recordings.append(link_to_recording)


                    if glob.glob(path_to_vm_annotations_2 + "/"
                                 + dialog_name + "/" + "*_"
                                 + turn_number + "_" + speakerID + ".par"):
                        file = glob.glob(path_to_vm_annotations_2 + "/"
                                         + dialog_name + "/" + "*_"
                                         + turn_number + "_" + speakerID + ".par")
                        # if len(file) == 1:
                        file = file[0]

                        with open(file, "r", encoding = "ISO-8859-1") as parfile:
                            partext = parfile.read()

                            # check if some time information exists
                            wor = re.search('WOR', partext)
                            mau = re.search('MAU', partext)
                            tr2 = re.findall('TR2:\s\d+\s.*', partext)

                            if wor:
                                wor_counter += 1
                                time_info = True
                            elif mau:
                                mau_counter += 1
                                time_info = True
                            else:
                                no_time_info += 1
                                time_info = False

                            token_number = int(tr2[-1].split("\t")[1])
                            # last token number + 1 = number of tokens in the turn
                        if time:
                            time_info = time_info
                        else:
                            time_info = True
                        if time_info:
                            link_to_wav_file = file[:-4]
                            if glob.glob(link_to_wav_file + ".wav"):
                                sentence_id2recording[id_prefix+"_"+assumed_sentence_id] = link_to_wav_file + ".wav"
                                dialogs.add(dialog_name)
                                speaker.add(speakerID)
                                total_tokens_with_time_info += token_number
                            elif glob.glob(link_to_wav_file + "_GER.wav"):
                                sentence_id2recording[
                                    id_prefix + "_" + assumed_sentence_id] = link_to_wav_file + "_GER.wav"
                                dialogs.add(dialog_name)
                                speaker.add(speakerID)
                                total_tokens_with_time_info += token_number
                            else:
                                print("No wav file found!", link_to_wav_file)

                    elif glob.glob(path_to_vm_annotations_1 + "/"
                                   + dialog_name + "/" + "*_"
                                   + turn_number + "_" + speakerID + ".par"):
                        file = glob.glob(path_to_vm_annotations_1 + "/"
                                         + dialog_name + "/" + "*_"
                                         + turn_number + "_" + speakerID + ".par")
                        # if len(file) == 1:
                        file = file[0]

                        with open(file, "r", encoding = "ISO-8859-1") as parfile:
                            partext = parfile.read()
                            wor = re.search('WOR', partext)
                            mau = re.search('MAU', partext)
                            tr2 = re.findall('TR2:\s\d+\s.*', partext)

                            if wor:
                                wor_counter += 1
                                time_info = True
                            elif mau:
                                mau_counter += 1
                                time_info = True
                            else:
                                no_time_info += 1
                                time_info = False

                            token_number = int(tr2[-1].split("\t")[1])
                            # last token number + 1 = number of tokens in the turn
                        if time:
                            time_info = time_info
                        else:
                            time_info = True
                        if time_info:
                            link_to_wav_file = file[:-4]
                            if glob.glob(link_to_wav_file + ".wav"):
                                sentence_id2recording[id_prefix+"_"+assumed_sentence_id] = link_to_wav_file + ".wav"
                                dialogs.add(dialog_name)
                                speaker.add(speakerID)
                                total_tokens_with_time_info += token_number

                            elif glob.glob(link_to_wav_file + "_GER.wav"):
                                sentence_id2recording[
                                    id_prefix + "_" + assumed_sentence_id] = link_to_wav_file + "_GER.wav"
                                dialogs.add(dialog_name)
                                speaker.add(speakerID)
                                total_tokens_with_time_info += token_number

                            else:
                                print("No wav file found!")
                    else:
                        # we have a sentence from a tree file with no recording!
                        no_recording.append(id_prefix + "_" + assumed_sentence_id)
                        recordings_for_id_prefix = False



            if recordings_for_id_prefix:
                total_sentences += int(sentences)
                total_phrases += int(phrases)
                total_tokens += int(tokens)

    # this information is not really relevant
    print("Links to recordings:", len(links_to_recordings))

    print("Total sentences:", total_sentences)
    print("Total phrases:", total_phrases)
    print("Total tokens:", total_tokens)
    print("WOR annotation:", wor_counter)
    print("MAU annotation:", mau_counter)
    print("No time info:", no_time_info)
    print("No recording:", len(no_recording))
    print("Number of sentences with time info:", len(sentence_id2recording))
    print("Number of turns:", len(set(sentence_id2recording.values())))
    print("Number of tokens in those turns", total_tokens_with_time_info)
    print("Number of speakers:", len(speaker))
    print("Number of dialogs:", len(dialogs))

    sexes = list()
    dialects = list()



    for speakerID in speaker:
        if glob.glob(os.path.join(path_to_vm_spr_2, "j_"+speakerID.lower()+".spr")):
            with open(os.path.join(path_to_vm_spr_2, "j_"+speakerID.lower()+".spr"), "r", encoding = "ISO-8859-1") as sprfile:
                for line in sprfile:
                    sex = re.search('sex\s(\w)', line)
                    dialect = re.search('dialect\s(.*)', line)
                    if sex:
                        sexes.append(sex.group(1))
                    if dialect: # dialect info only in VM2
                        dialects.append(dialect.group(1))
        elif glob.glob(os.path.join(path_to_vm_annotations_1, "AufDat.csv")):
            with open(os.path.join(path_to_vm_annotations_1, "AufDat.csv"),
                      "r",
                      encoding="ISO-8859-1") as csvfile:
                for line in csvfile:
                    line_list = line.split("\t")
                    if line_list[14] == speakerID:
                        sexes.append(line_list[15])
                    elif line_list[23] == speakerID:
                        sexes.append(line_list[24])
        else:
            print("No speaker info found.")

    print("Sexes:",Counter(sexes))
    print("Dialects:",Counter(dialects))


if __name__ == '__main__':
    path_to_vm_annotations_1 = "/group/corporapublic/verbmobil/1.3"
    path_to_vm_annotations_2 = "/group/corpora/large4/verbmobil/2.3"

    path_to_vm_spr_2 = "/group/corpora/large4/verbmobil/2.3/spr"

    # lang = "ger"
    lang = "eng"
    # German data
    # path_to_vm_trees = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/ger/penn_files/penn_files"
    # path_to_vm_exports = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/ger/export_files/export_files"
    # path_to_vm_trees = "verbmobil_treebank/ger/penn_files/penn_files"
    # path_to_vm_exports = "verbmobil_treebank/ger/export_files/export_files"

    # English data
    # path_to_vm_trees = "verbmobil_treebank/eng/penn_files/penn_files"
    # path_to_vm_exports = "verbmobil_treebank/eng/export_files/export_files"
    path_to_vm_trees = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/eng/penn_files/penn_files"
    path_to_vm_exports = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/eng/export_files/export_files"

    # Japanese data
    # path_to_vm_exports = "/afs/inf.ed.ac.uk/user/s20/s2096077/prosody_nlp/verbmobil/verbmobil_treebank/jap/export_files/export_files"

    get_stats_eng("eng", time=False)
    # get_stats("ger", time=True)
    # get_stats_jap("jap", time=True)