import pandas as pd
import os
import pathlib
import logging

logger = logging.getLogger('SCT_FILE_VALIDATION')


def read_aggr_file(file):
    df = pd.read_csv(file)
    target_db = set()
    valid_path_set = set()

    # print(df[['Name', 'Schema name']])
    # print(df.columns)

    for n, col_list in enumerate(list(df.columns), 1):
        if '% for' in col_list:
            tgt_db_name = (col_list.split('% for')[1]).replace('"', '').strip().upper()
            if 'POSTGRESQL' in tgt_db_name:
                if 'RDS' in tgt_db_name:
                    target_db.add('POSTGRESQL')
                elif 'AURORA' in tgt_db_name:
                    target_db.add('AURORA_POSTGRESQL')

    for index, row in df.iterrows():
        for i in list(target_db):
            p = os.path.join('/', row['Name'], row['Schema name'], i)
            valid_path_set.add(p)
            # p = os.path.join('/', row['Name'], row['Schema name'], list(target_db)[1])
            # valid_path_set.add(p)

    return list(valid_path_set)


def check_fname_count(src_file_list, folder_tgtschema, folder_tgtschema_usr):
    missing_file = set()
    file_name_list = sct_schema_files_list(folder_tgtschema, folder_tgtschema_usr)
    src_file_upper_dict = {x.upper(): x for x in src_file_list}
    for fname in file_name_list:
        if fname not in src_file_upper_dict.keys():
            missing_file.add(fname)
    return missing_file


def check_fname_convention(file, folder_tgtschema, folder_tgtschema_usr):
    file_name_list = sct_schema_files_list(folder_tgtschema, folder_tgtschema_usr)
    valid = True if file.upper() in file_name_list else False
    return valid


def sct_schema_files_list(folder_tgtschema, folder_tgtschema_usr):
    file_name_suffix = ['CSV-REPORT.CSV', 'CSV-REPORT_SUMMARY.CSV', 'PDF-REPORT.PDF',
                        'CSV-REPORT_ACTION_ITEMS_SUMMARY.CSV']
    file_name_list = list()
    for i in file_name_suffix:
        filename = folder_tgtschema_usr.upper() + '-' + folder_tgtschema.upper() + '-' + i
        file_name_list.append(filename)
    # pprint.pprint(file_name_list)
    return file_name_list


def check_aggr_file(file_list, level):
    reason = set()
    valid_name, valid_level = False, False

    for file in file_list:
        if file in (".DS_Store", "__MACOSX"):
            continue
        if file.upper() == 'Aggregated_report.csv'.upper():
            valid_name = True
            if level == 0:
                valid_level = True
            else:
                reason.add(f"LEVEL-{level}: 'Aggregated_report.csv' file should be at level-0")
        elif file.upper() != 'Aggregated_report.csv'.upper():
            reason.add(f"LEVEL-{level}: '{file}' file should not be at level-0 (except 'Aggregated_report.csv')")
        else:
            reason.add(f"LEVEL-{level}: 'Aggregated_report.csv' file should be at level-0")

    # print(f"valid_file_count-{valid_file_count}\nvalid_name-{valid_name}\nvalid_suffix-{valid_suffix}")

    return all([valid_name, valid_level]), reason


def sct_file_tree(startpath, LEVEL, REASON, SCT_TREE):
    # File_Name =p2+folder_basename+
    valid_path_list = list()
    valid_path = True
    for root, dirs, files in os.walk(startpath):
        logger.info("root={0}, dirs={1}, files={2}".format(root, dirs, files))
        usr = pathlib.PurePosixPath(str(root))
        logger.info("usr = {}".format(usr))
        rel_path_curr = root.replace(startpath, '')
        folder_tgtDB = os.path.basename(root)
        logger.info("folder_tgtDB = {}".format(folder_tgtDB))
        logger.info("folder_tgtschema_usr = {}".format(type(usr)))
        folder_tgtschema_usr = os.path.basename(str(usr.parents[0]))
        logger.info("folder_tgtschema_usr = {}".format(folder_tgtschema_usr))
        level = rel_path_curr.count(os.sep)
        LEVEL.add(level)
        indent = ' ' * 2 * (level)
        SCT_TREE.append(f'LEVEL-{level}{indent}{folder_tgtDB}/')
        logger.info(f'LEVEL-{level}{indent}{folder_tgtDB}/')
        # print(f'{level}{indent}{root}/')
        subindent = ' ' * 2 * (level + 1)  # print(f'{level}{subindent}Folder_Count* = {len(dirs)}')

        if files:
            for fname in files:
                if fname in (".DS_Store", "__MACOSX"):
                    continue
                if level == 0:
                    valid, reason = check_aggr_file(files, level=level)
                    [REASON.add(r) for r in reason]
                    valid = '\u2713' if valid else 'x'
                    if not fname.startswith('.'):
                        if valid and fname == 'Aggregated_report.csv':
                            SCT_TREE.append(f'LEVEL-{level}{subindent}|__ {valid} {fname}')
                            logger.info(f'LEVEL-{level}{subindent}|__ {valid} {fname}')
                            valid_path_list = read_aggr_file(os.path.join(root, fname))
                        else:
                            SCT_TREE.append(f'LEVEL-{level}{subindent}|__ ? {fname}')
                            logger.info(f'LEVEL-{level}{subindent}|__ ? {fname}')
                    else:
                        SCT_TREE.append(f'LEVEL-{level}{subindent}|__ ? {fname}')
                        logger.info(f'LEVEL-{level}{subindent}|__ ? {fname}')
                else:
                    valid_fname = check_fname_convention(fname, folder_tgtDB, folder_tgtschema_usr)
                    missing_file = check_fname_count(files, folder_tgtDB, folder_tgtschema_usr)
                    if valid_path_list:
                        valid_path = True if rel_path_curr in valid_path_list else False
                    if fname == 'Aggregated_report.csv' and level > 0:
                        REASON.add(
                            f"LEVEL-{level}: ({fname}) should be at LEVEL-0 - ({rel_path_curr}).")
                        REASON.add(
                            f"LEVEL-0: Check if you have extracted SCT files using MSA (Multi Server Assessment) mode")
                    valid = '\u2713' if valid_fname and valid_path else 'x'
                    SCT_TREE.append(f'LEVEL-{level}{subindent}|__ {valid} {rel_path_curr}/{fname}')
                    logger.info(f'LEVEL-{level}{subindent}|__ {valid} {rel_path_curr}/{fname}')
                    if not valid_fname:
                        REASON.add(
                            f"LEVEL-{level}: '{fname}' is not a valid file in this folder - ({rel_path_curr})")
                    if not valid_path:
                        REASON.add(
                            f"LEVEL-{level}: '{rel_path_curr}' is not a valid path - ({rel_path_curr})")
                    if missing_file:
                        REASON.add(
                            f"LEVEL-{level}: Missing file in folder - ({rel_path_curr}) : ({missing_file})")
        elif not dirs:
            REASON.add(f"LEVEL-{level}: Blank folder - '{rel_path_curr}'")
    return LEVEL, REASON, SCT_TREE