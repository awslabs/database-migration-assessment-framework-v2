import base64
import sys, argparse
import json
import logging
import time
import csv

logger = logging.getLogger('SCT_FILE_VALIDATION')


# ---------------------------------------------------------------------------
def timestamp():

    now = time.time()
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


# ---------------------------------------------------------------------------
def parse_arguments():

    if sys.hexversion < 0x3060000:
        logger.info("At least Python 3.6 required; you have {}}".format(sys.version))
        exit(1)

    parser = argparse.ArgumentParser()
    # optional = parser._action_groups.pop()  # removes the optional arguments section
    mxg = parser.add_mutually_exclusive_group(required=True)
    mxg.add_argument(
        "-fp"
        , "--file_path"
        , dest="file_path"
        , help="The file_path to the zip file that will be placed on s3 bucket"
    )
    mxg.add_argument(
        "-c"
        , "--src_conn_str"
        , dest="src_conn_str"
        , help="Source Oracle database Connection string (Format : db_user@db_host:db_port/db_name ) "
    )
    # parser._action_groups.append(optional)  # add optional arguments section again
    parser.add_argument(
        "-r"
        , "--aws_region"
        , dest="aws_region"
        , default="us-east-1"
        , help="AWS Region to connect to RDS service"
    )
    args = parser.parse_args()
    return args




