"""
    Copyright 2021 Continental Corporation

    :file: upload_doc_to_htd.py
    :platform: Windows, Linux
    :synopsis:
        Script to build and upload Sphinx html doc (user manual) to HTD (Host The Doc) server
        Usage:  python upload_doc_to_htd.py     --> command to upload already built doc
                python upload_doc_to_htd.py -d  --> command to build doc and then upload

    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

import os
import sys
import requests
import argparse
import shutil
import logging
import subprocess

import global_vars

HTD_SERVER_LINK = 'https://cip-docs.cmo.conti.de/hmfd'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.join(CURRENT_DIR, "ptf", "doc")
DOC_BUILD_FOLDER = os.path.join(CURRENT_DIR, "ptf", "doc", "build")
DOC_HTML_FOLDER = os.path.join(DOC_DIR, "build", "html")
SPHINX_DOC_BUILD_CMD = os.path.join(DOC_DIR, "make.bat html")
DOC_ZIP_FOLDER = os.path.join(CURRENT_DIR, "user_doc")
DOC_ZIP = os.path.join(CURRENT_DIR, "user_doc.zip")
NOK = 1
OK = 0
logging.basicConfig(level=logging.INFO, format='[%(levelname)s %(asctime)s] %(message)s')


def build_doc():
    """
    Function to build the user documentation
    """
    logging.info("Running doc build command %s", SPHINX_DOC_BUILD_CMD)
    logging.info("Please wait ...")
    # opening a pipe process for documentation build
    process = subprocess.Popen(
        SPHINX_DOC_BUILD_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True
    )
    # start process and fetch process output and error
    output, error = process.communicate()
    if "build succeeded" not in output:
        raise RuntimeError("Error during sphinx doc build step\n{}".format(error))
    else:
        logging.info(output)


def detect_htd_credential_env_vars():
    """
    Function to detect hostthedoc username and password by reading env vars (set by jenkins)

    :return: returns the doc_service username and password
    :rtype: tuple
    """
    htd_usr = os.getenv('HTD_USER')
    htd_pass = os.getenv('HTD_PASS')
    return htd_usr, htd_pass


def main():
    """
    Main function
    """
    exit_code = OK
    try:
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument(
            '-d', help="Bool option to build doc before publishing (optional)", required=False,
            action='store_true')

        args = parser.parse_args()

        htd_user, htd_pass = detect_htd_credential_env_vars()
        if not htd_user or not htd_pass:
            raise RuntimeError("'doc_service' credentials were not found via env vars")

        if args.d:
            logging.info("Starting to build user doc via sphinx")
            build_doc()
            logging.info("Documentation built successfully")

        logging.info("Checking 'index.html' file existence")
        if not os.path.exists(os.path.join(DOC_DIR, "build", "html", "index.html")):
            raise RuntimeError(
                "'index.html' file does not exist after doc build. "
                "Doc build was not done or was done with errors")
        logging.info("'index.html' file exists")

        logging.info("Creating zip of build doc for HTD upload")
        shutil.make_archive(DOC_ZIP_FOLDER, 'zip', DOC_HTML_FOLDER)
        logging.info("Zip folder created")

        logging.info("Checking zip folder existence")
        if not os.path.exists(DOC_ZIP):
            raise RuntimeError(
                "'{}' folder does not exists Something went wrong.".format(DOC_ZIP))
        logging.info("Zip folder exists")

        logging.info("Starting to upload doc to HTD Server.")
        logging.info("Might take a minute or two. Please wait ...")
        requests.post(
            HTD_SERVER_LINK,
            data={
                "name": "ConTest",
                "version": global_vars.DOC_VERSION,
                "description": "Continental Software Testing Tool User Manual"
            },
            auth=(htd_user, htd_pass),
            files={"archive": ("archive.zip", open(DOC_ZIP, 'rb'))})
        logging.info("User doc uploaded to HTD Server")

        logging.info("Deleting user doc zip folder")
        os.remove(DOC_ZIP)
        logging.info("Zip folder deleted")

    except RuntimeError as error:
        logging.error(error)
        exit_code = NOK

    except Exception as error:
        logging.error(error)
        exit_code = NOK

    finally:
        if os.path.exists(DOC_BUILD_FOLDER):
            logging.info("Deleting doc build folder")
            shutil.rmtree(DOC_BUILD_FOLDER)
            logging.info("Doc build folder deleted")
        if os.path.exists(DOC_ZIP):
            logging.info("Deleting user doc zip folder")
            os.remove(DOC_ZIP)
            logging.info("Zip folder deleted")
        if not exit_code:
            logging.info("Goodbye, All OK")
        sys.exit(exit_code)


if __name__ == '__main__':
    main()
