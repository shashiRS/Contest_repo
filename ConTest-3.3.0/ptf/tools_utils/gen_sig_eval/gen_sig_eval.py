"""
    Copyright 2022 Continental Corporation

    :file: gen_sig_eval.py
    :platform: Windows
    :synopsis:
        Generic Signal Evaluation implementation

    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

# ignoring top level import as pip installer checker need to be above imports
import pandas as pd
from collections import Counter
import logging
import os

# custom imports
from ptf.verify_utils import ptf_asserts

LOG = logging.getLogger('GEN-SIG-EVAL')


class GenSigEval:
    """
    Class for generic evaluation of signals (Proof Of Concept - POC)

    In order to make use of this application use following example in your ``setup.pytest`` file

    :param string generic_csv: Generic CSV file containing mapping of project specific signals to
        generic signal names
    :param string project_mts_csv: CSV file containing project specific signals and their values.
        This file will come out of MTS run
    :param string csv_separator: CSV file separator used in files, Default is ``,``

    Example::

        # to be done in setup.pytest

        # in custom import section
        from ptf.ptf_utils.global_params import *
        from ptf.tools_utils.gen_sig_eval import gen_sig_eval

        # recommended to be done in 'global_setup'
        # creating object or instance of Gen Sig Eval Class
        gen_sig_eval_obj = gen_sig_eval.GenSigEval(
            generic_csv="D:/prj/gen_sig_file.csv", project_mts_csv="D:/prj/prj_mts_file.csv")
        # assigning object or instance to a global variable to be accessed later
        set_global_parameter("sig_eval_obj", gen_sig_eval_obj)

        # you can access 'gen_sig_eval_obj' object as follow in setup.pytest, .pytest or .py files
        sig_eval = get_parameter("sig_eval_obj")
    """
    def __init__(self, generic_csv=None, project_mts_csv=None, csv_separator=","):
        """Constructor"""
        # creating variables/attributes for further usage
        self.df_generic_csv = None
        self.df_prj_mts_csv = None
        self.gen_sig_mapping_dict = None
        self.project_signals = None
        self.generic_signals = None
        self.mts_signals_found = None
        self.mts_signals_not_found = None
        self.mts_signals_remap_list = None
        self.csv_separator = csv_separator
        # processing csv files if given
        if not generic_csv:
            ptf_asserts.fail("Generic Signal CSV file not provided")
        self.__process_generic_csv(generic_csv, self.csv_separator)
        if project_mts_csv:
            self.process_mts_project_csv(project_mts_csv, self.csv_separator)

    def __process_generic_csv(self, generic_csv=None, csv_sep=","):
        """
        Method for processing the generic csv and creating dataframe

        :param string generic_csv: Generic CSV file containing signal mapping information
        :param string csv_sep: CSV separator character in csv file. Default is ``,``
        """
        if not os.path.exists(generic_csv):
            ptf_asserts.fail("{}' file does not exist".format(generic_csv))
        LOG.info("Creating dataframe for Generic CSV file '%s'", generic_csv)
        # reading the generic csv file with specific separator and creating a dataframe
        self.df_generic_csv = pd.read_csv(generic_csv, sep=csv_sep)
        # checking if there are signal duplications and raise error if any
        if self.df_generic_csv.duplicated(["Signal_Name"]).any():
            # creating duplicated signals dataframe
            df_dup_sigs = self.df_generic_csv[self.df_generic_csv.duplicated(["Signal_Name"])]
            # creating dictionary with keys as project signal names and value as generic names
            dup_sigs_dict = df_dup_sigs.set_index('Signal_Name').to_dict()["Generic_Name"]
            # creating list of duplications for raising error
            dup_sigs_lst = list(dup_sigs_dict.keys())
            ptf_asserts.fail(
                "{} generic csv file contains duplicated signals names.\n"
                "Please remove duplications.\nNo. of Duplications: {}\n"
                "Duplicated signals: {}".format(generic_csv, len(dup_sigs_lst), dup_sigs_lst))
        # creating dictionary with keys as project signal names and value as generic names
        self.gen_sig_mapping_dict = self.df_generic_csv.set_index(
            'Signal_Name').to_dict()['Generic_Name']
        # saving generic as well ass project specific signals in respective lists
        self.project_signals = list(self.gen_sig_mapping_dict.keys())
        self.generic_signals = list(self.gen_sig_mapping_dict.values())
        LOG.info("Total signals in generic csv file: %s", len(self.project_signals))
        LOG.info("Generic CSV successfully read")

    def process_mts_project_csv(self, project_mts_csv=None, csv_sep=","):
        """
        Method for processing the MTS project csv and creating dataframe

        Following actions shall be taken in this API

            - creating dataframe after reading project csv file
            - remapping project specific signals to generic signals for generic evaluation
            - checking for any duplicate signals in project csv file

        .. note::
            This API will be automatically triggerred if ``project_mts_csv`` argument is given
            in the instance creation of ``GenSigEval`` class

        :param string project_mts_csv: Project MTS CSV file containing signals values information
        :param string csv_sep: CSV separator character in csv file. Default is ``,``

        Example::

            # remapping signals from project csv file to generic csv file to create a generic
            # dataframe which then shall be used for generic signal evaluation
            sig_eval.process_mts_project_csv(project_mts_csv="D:/prj/prj_mts_file.csv")
        """
        if not project_mts_csv:
            ptf_asserts.fail("Project Signal Values CSV file not provided")
        if not os.path.exists(project_mts_csv):
            ptf_asserts.fail("'{}' file does not exist".format(project_mts_csv))
        LOG.info("Creating dataframe for MTS Project CSV file '%s'", project_mts_csv)
        # creating dataframe for csv containing signal values only for signals which were found
        # in generic csv file
        self.df_prj_mts_csv = pd.read_csv(
            project_mts_csv, sep=csv_sep, low_memory=False,
            usecols=lambda x: x in self.project_signals)
        self.mts_signals_found = list(self.df_prj_mts_csv)
        self.mts_signals_not_found = list(
            set(self.mts_signals_found).symmetric_difference(set(self.project_signals)))
        LOG.info("%s Signals in Generic CSV found in MTS CSV file", len(self.mts_signals_found))
        LOG.info("%s Signals in Generic CSV not found in MTS CSV file",
                 len(self.mts_signals_not_found))
        LOG.info("MTS Project CSV successfully read")
        # renaming dataframe columns (project signal names) with generic signals names
        LOG.info("Remapping generic signals to project signals")
        self.df_prj_mts_csv.rename(self.gen_sig_mapping_dict, axis="columns", inplace=True)
        # checking duplications
        if self.df_prj_mts_csv.columns.duplicated().any():
            ptf_asserts.fail("{} project mts csv file contains duplicated signals names")
        self.mts_signals_remap_list = list(self.df_prj_mts_csv.columns)
        LOG.info("Remapped signals count: %s", len(self.mts_signals_remap_list))
        if not self.mts_signals_remap_list.sort() == self.mts_signals_found.sort():
            ptf_asserts.fail("Mismatch in remapped signal count and MTS found signals.")
        LOG.info("Remapping done successfully")

    def filter_dataframe(self, signals_list=None, ignore_missing_signals=False):
        """
        Method for returning back a filtered dataframe based on requested signal list.
        The filtering shall be done from the remapped dataframe or generic signal dataframe

        .. note::
            Duplicated signal names in ``signals_list`` are not allowed.

        :param list signals_list: List containing signals for which filtering is required
        :param bool ignore_missing_signals: Flag for ignoring if some signals is given list of
            signals are missing in filtering process. Default is ``False``

        :return: Filtered dataframe
        :rtype: dataframe

        Example::

            # requesting to filter 'signal_1' & 'signal_2' from remapped dataframe
            filter_df = sig_eval.filter_dataframe(signals_list=['signal_1', 'signal_2'])
            # the filtered dataframe could be used for further processing e.g. plotting, evaluation
            # etc.
            print(filter_df)
        """
        if self.mts_signals_remap_list is None:
            ptf_asserts.fail("Signal remapping is not done. Please check if MTS csv file is "
                             "processed via 'process_mts_project_csv' API.")
        LOG.info(
            "Starting to filter remapped dataframe with given signals {}".format(signals_list))
        if not signals_list:
            ptf_asserts.fail("Signal list not provided for filtering the remapped dataframe")
        # checking duplications and raising error
        if len(signals_list) != len(set(signals_list)):
            duplicates = [k for k, v in Counter(signals_list).items() if v > 1]
            ptf_asserts.fail("Duplications exists in provided signal list for filtering: "
                             "{}".format(duplicates))
        # checking if there are any missing signals in extracted signals
        missing_signals = list(set(signals_list) - set(self.mts_signals_remap_list))
        if missing_signals:
            if not ignore_missing_signals:
                ptf_asserts.fail("Some signals are missing in remapped dataframe.\n"
                                 "Missing Signals: {}".format(missing_signals))
            else:
                LOG.info("Ignoring missing signals in remapped dataframe: %s", missing_signals)
        LOG.info("Filtering done successfully")
        return self.df_prj_mts_csv.filter(signals_list)

    def filter_and_query_dataframe(
            self, signals_list=None, ignore_missing_signals=False, query_exp=None,
            return_bool=True):
        """
        Method for filtering as well as applying an evaluation expression over filtered dataframe.
        In this API first the filtering of remapped or generic dataframe shall be done and then
        Pandas ``query`` method shall be applied.

        .. note::
            Please note that the Pandas query engine shall be ``numexpr``

        .. note::
            Duplicated signal names in ``signals_list`` are not allowed

        :param list signals_list: List containing signals for which filtering is required
        :param bool ignore_missing_signals: Flag for ignoring if some signal(s) in given list of
            signals are missing in filtering process. Default is ``False``
        :param string query_exp: Query expression which shall be applied over filtered dataframe
        :param bool return_bool: Flag for returning back a boolean value or a dataframe

        :return: ``True`` if some values are found after applying query expression over
            filtered dataframe else ``False`` or dataframe if ``return_bool`` flag is ``False``
        :rtype: dataframe or bool

        Example::

            # filtering and querying remapped or generic dataframe with the given query expression
            test_signals_df = sig_eval.filter_and_query_dataframe(
                signals_list=test_signals,
                ignore_missing_signals=False,
                query_exp="(20 < Time_Stamp < 21) and (100 <= ars_sctl_cnt_eol_succeeded <= 101)",
                return_bool=True)
        """
        # check if query expression is given or not
        if not query_exp:
            ptf_asserts.fail("Evaluation expression not given")
        LOG.info("Applying query expression: '%s'", query_exp)
        # creating a dataframe with signals on which query expression shall be applied
        filtered_df = self.filter_dataframe(signals_list, ignore_missing_signals)
        # applying query expression on filtered expression
        query_df = filtered_df.query(query_exp)
        # return bool value only if user requested via 'return_bool' flag else return the query
        # result dataframe for user processing
        if return_bool:
            if not query_df.empty:
                return True
            else:
                return False
        else:
            return query_df

    def get_sig_val_occ_in_tf(
            self, sig_name, sig_val, tf_start, tf_end, operator, filtered_df=None,
            tf_boundary="both", return_df=True):
        """
        Method for checking the occurence of a particular signal in a dataframe in between a
        particular time frame

        :param str sig_name: Signal name
        :param str sig_val: Signal expected occurence value
        :param float/int tf_start: Time frame start value from where occurence shall be checked
        :param float/int tf_end: Time frame end value from where occurence shall be checked
        :param str operator: Pythonic evaluation operator based on which occurence shall be checked
            w.r.t expected value e.g. ``"=="``, ``>`` etc.
        :param dataframe filtered_df: In-case their is already a filtered dataframe available
            then it can be given in this argument else filtering based on ``sig_name`` shall be done
            from remapped/filtered dataframe
        :param str tf_boundary: Mention whether to include start or end time frame during the
            evaluation process or not e.g. ``both, neither, left, right``
        :param bool return_df: ``True`` if you need to get back dataframe after evaluation
            expression is applied else ``False``

        :return: tuple (signal_occurence_value_in_int, dataframe) if ``return_df`` is ``True`` else
            just signal occurence value as integer
        :rtype: tuple or int

        Example1::

            # get the occurrence of 'Cycle_ID' equal to '212' between time frame '10' to '20'
            # including time frame boundaries
            signal_occurrence = sig_eval.get_sig_val_occ_in_tf(
                "Cycle_ID", 212, 10, 20, "==", tf_boundary="both", return_df=False)
            # printing the integer value of signal occurrence
            print(signal_occurrence)

        Example2::

            # get the occurrence of 'ars_cyclecounter' greater than '5270' between time frame
            # '10' to '20' including time frame boundaries
            # with 'return_df=True' the dataframe with condition 'ars_cyclecounter > 5270' between
            # between time frame '10' to '20' including time frame boundaries shall be returned
            # which can be used for plotting etc.
            signal_occurrence, dataframe = sig_eval.get_sig_val_occ_in_tf(
                "ars_cyclecounter", 5270, 10, 20, ">", tf_boundary="both", return_df=True)
            # printing the integer value of signal occurrence and dataframe
            print(signal_occurrence, dataframe)

        Example3::

            # requesting to filter 'Time_Stamp' & 'Cycle_ID' from remapped dataframe
            filter_df = sig_eval.filter_dataframe(signals_list=['Time_Stamp', 'Cycle_ID'])
            # get the occurrence of 'Cycle_ID' equal to '212' between time frame '10' to '20'
            # including time frame boundaries
            # the occurence shall be checked with given dataframe
            signal_occurrence = sig_eval.get_sig_val_occ_in_tf(
                "Cycle_ID", 212, 10, 20, "==", filtered_df=filter_df, tf_boundary="both")
            # printing the integer value of signal occurrence
            print(signal_occurrence)
        """
        if not filtered_df:
            filter_df = self.filter_dataframe(["Time_Stamp", sig_name])
        else:
            filter_df = filtered_df
            LOG.info("Skipped the preparation of dataframe since its given by user")
        eval_exp = '((filter_df["Time_Stamp"].between({}, {}, inclusive="{}")) & (filter_df["{}"]' \
                   ' {} {}))'.format(tf_start, tf_end, tf_boundary, sig_name, operator, sig_val)
        eval_df = eval(eval_exp)
        df = filter_df[eval_df]
        if return_df:
            return len(df), df
        else:
            return len(df)
