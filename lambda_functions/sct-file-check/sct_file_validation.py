#!/usr/bin/env python
import logging
import argparse
import datetime
import os
import sys
import utils
import sct_file_utils as sfu
import json
import pathlib
import pandas as pd
import subprocess
# import streamlit as st

def sct_file_check_main(file_path):
    try:
        sct_tree_data = None
        # FILE_PATH1 = "/Users/vksgupta/WorkDocs/PYTHON/Code/DMAFV2/input/JPMC_BATCH1"
        # FILE_PATH2 = "/Users/vksgupta/WorkDocs/PYTHON/Code/DMAFV2/input/JPMC_SYB1"
        # FILE_PATH3 = "/Users/vksgupta/WorkDocs/PYTHON/Code/DMAFV2/input/JPMC_SYB2"
        # FILE_PATH4 = "/Users/vksgupta/WorkDocs/__Work/DMAFV3/Sybase/User_Data_Moody/Moodys_Batch3"
        #
        # FILE_PATH_LIST = [FILE_PATH1, FILE_PATH2, FILE_PATH3, FILE_PATH4]

        FILE_PATH = file_path
        print (f"{FILE_PATH}")
        # target = 'WEB'
        target = 'FILE'

        LEVEL = set()
        # UNICODE for check mark id u'\u2713'
        usr = pathlib.PurePosixPath(FILE_PATH)
        print(f"Folder Path - {usr}")
        REASON = set()
        SCT_TREE = list()

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logging.info(f"Folder Path - {usr}")
        # st.set_page_config(page_title='SCT_MSA_Validation', page_icon=None, layout='wide',
        #                    initial_sidebar_state='auto', )
        # st.title('Validate SCT Output')

        current_time = datetime.datetime.now()
        dateMY = "{0}{1}{2}-{3}{4}{5}".format(current_time.year, current_time.month, current_time.day, current_time.hour,
                                              current_time.minute, current_time.second)
        logger.info("PWD={}".format(os.getcwd()))
        cmd = 'ls'
        temp = subprocess.Popen([cmd, '-ltr', 'input'], stdout = subprocess.PIPE) 
        # get the output as a string
        output = str(temp.communicate()) 
        logger.info("ls output = {}".format(output))
        LEVEL, REASON, SCT_TREE = sfu.sct_file_tree(FILE_PATH, LEVEL, REASON, SCT_TREE)
        logger.info(f"MAX LEVEL = {max(LEVEL) + 1}")
        logger.info(f"-------------------")
        logger.info('>> ' + '\n>> '.join(sorted(REASON)))
        sct_tree_data = "{0}{1}{2}{3}{4}{5}".format('\n'.join(SCT_TREE), '\n'+'More Details:' + '\n', f"-------------------" + '\n', f"MAX LEVEL = {max(LEVEL) + 1}", '\n' + '>> ' , '\n>> '.join(sorted(REASON)))

        # Web
        # if target == 'WEB':
        #     st.subheader(f"Full Path - `{FILE_PATH}`")
        #     st.header('Folder Analysis')

        #     with st.expander("Details ..."):
        #         if REASON:
        #             p = '\n'.join(sorted(REASON))
        #             st.code(f"{p}", language='log')
        #         else:
        #             st.success(f"No exception")

        #     st.header('SCT - Folder Structure')
        #     with st.expander("Details ..."):
        #         with st.spinner('Wait for it...'):
        #             # time.sleep(5)
        #             st.code(f"{sct_tree_data}")

    except Exception as e:
        logger.error("Error: {}".format(str(e)))

    return sct_tree_data
