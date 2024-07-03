"""
This module defines the UDS client connection configuration parameters and
codecs for DIDs needed when using e.g. service ReadDataByIdentifier().
"""
# #################### EXAMPLE ######################
# This example is based on ARS441DC13 project!      #
#####################################################

##########################################################
# Import libraries
from udsoncan import DidCodec
import struct
from enum import IntEnum

# Constants
PROJECT = 'ARS441DC13'


class DID0x0182(DidCodec):
    """
    Class for Data Identifier 0x0182 Backend CA Certificate Identification
    Encodes and decodes the server response as per the RDF03T.cdd specifications
    """
    did = 0x0182
    did_name = 'Backend CA Certificate Identification'
    units = {
    }
    defaults = {
    }
    ranges = {
    }

    # pylint: disable=too-many-locals
    @staticmethod
    def encode(value):
        """
        This method will encode the the input value.
        """
        if value['Backend_CA_SubjectKeyIdentifier']:
            byte0 = (value['Backend_CA_SubjectKeyIdentifier']
                     >> 152) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte1 = (value['Backend_CA_SubjectKeyIdentifier']
                     >> 144) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte2 = (value['Backend_CA_SubjectKeyIdentifier']
                     >> 136) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte3 = (value['Backend_CA_SubjectKeyIdentifier']
                     >> 128) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte4 = (value['Backend_CA_SubjectKeyIdentifier']
                     >> 120) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte5 = (value['Backend_CA_SubjectKeyIdentifier']
                     >> 112) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte6 = (value['Backend_CA_SubjectKeyIdentifier']
                     >> 104) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte7 = (value['Backend_CA_SubjectKeyIdentifier']
                     >> 96) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte8 = (value['Backend_CA_SubjectKeyIdentifier']
                     >> 88) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte9 = (value['Backend_CA_SubjectKeyIdentifier']
                     >> 80) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte10 = (value['Backend_CA_SubjectKeyIdentifier']
                      >> 72) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte11 = (value['Backend_CA_SubjectKeyIdentifier']
                      >> 64) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte12 = (value['Backend_CA_SubjectKeyIdentifier']
                      >> 56) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte13 = (value['Backend_CA_SubjectKeyIdentifier']
                      >> 48) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte14 = (value['Backend_CA_SubjectKeyIdentifier']
                      >> 40) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte15 = (value['Backend_CA_SubjectKeyIdentifier']
                      >> 32) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte16 = (value['Backend_CA_SubjectKeyIdentifier']
                      >> 24) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte17 = (value['Backend_CA_SubjectKeyIdentifier']
                      >> 16) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte18 = (value['Backend_CA_SubjectKeyIdentifier']
                      >> 8) & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
            byte19 = \
                value['Backend_CA_SubjectKeyIdentifier']\
                & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

        return struct.pack('>BBBBBBBBBBBBBBBBBBBB', int(byte0), int(byte1), int(byte2),
                           int(byte3), int(byte4), int(byte5), int(byte6), int(byte7),
                           int(byte8), int(byte9), int(byte10), int(byte11), int(byte12),
                           int(byte13), int(byte14), int(byte15), int(byte16), int(byte17),
                           int(byte18), int(byte19))

    # pylint: disable=no-self-use
    def decode(self, payload):
        """
        This method will decode the the input value.
        """
        vals = struct.unpack('>BBBBBBBBBBBBBBBBBBBB', payload)
        return vals

    def __len__(self):
        return 20    # encoded payload is 20 byte long


class DID0x018C(DidCodec):
    """
    Class for Data Identifier 0x018C Diagnostic User Role
    Encodes and decodes the server response as per the RDF03T.cdd specifications
    """
    did = 0x018C
    did_name = 'Diagnostic User Role'
    units = {
    }
    defaults = {
    }

    # pylint: disable=too-few-public-methods
    class Values:
        """
        Class for values
        """
        # pylint: disable=too-few-public-methods
        class CebasUserRole:
            """
            Class for CebasUserRole
            """
            unauthenticated = 0x00
            Supplier = 0x01
            Development_ENHANCED = 0x02

    @staticmethod
    def encode(value):
        """
        This method will encode the input value
        """
        if value['Cebas_UserRole']:
            byte0 = value['Cebas_UserRole']

        return struct.pack('>B', int(byte0))

    # pylint: disable=no-self-use
    def decode(self, payload):
        """
        This method will decode the input value 'payload'
        """
        vals = struct.unpack('>B', payload)
        return {
            'Cebas_UserRole': vals[0],
        }

    def __len__(self):
        """
        This method returns encoded payload 1 byte long
        """
        return 1    #


class DID0xF100ActiveDiagnosticInformation(DidCodec):
    """
    Class for Data Identifier 0xF100 Active Diagnostic Information
    Encodes and decodes the server response as per the RDF03T.cdd specifications
    """
    @staticmethod
    def encode(value):
        """
        This method will encode the input value
        """
        print(value['Identification'])
        if value['Identification']:
            byte0 = (value['Identification'] >> 16) & 255
            byte1 = (value['Identification'] >> 8) & 255
            byte2 = value['Identification'] & 255

        print(value['Session'])
        if value['Session']:
            byte3 = value['Session'] & 255

        return struct.pack('>BBBB', int(byte0), int(byte1), int(byte2), int(byte3))

    # pylint: disable=no-self-use
    def decode(self, payload):
        """
        This method will decode the input value 'payload'
        """
        vals = struct.unpack('>BBBB', payload)
        # print("ECU SW Mode is " + str(hex(vals[0])))
        # print("Active Diagnostic Variant is " + str(hex(vals[1])))
        # print("Active Diagnostic Version is " + str(hex(vals[2])))
        # print("Active Diagnostic Session is " + str(hex(vals[3])))
        return {
            'ECU_Software_Mode': vals[0],
            'Active_Diagnostic_Variant': vals[1],
            'Active_Diagnostic_Version': vals[2],
            'Active_Diagnostic_Session': vals[3]
        }

    def __len__(self):
        """
        This method returns encoded payload of 4 byte long
        """
        return 4


class DID0x1205(DidCodec):
    """
    Class for Data Identifier 0x1205 GVC Activation Deactivation.
    Encodes and decodes the server response as per the RDF03T.cdd specifications.
    """
    did = 0x1205
    did_name = 'GVC_Activation-Deactivation'

    units = {
    }
    defaults = {
        'GVC_Activation-Deactivation': 0x01,
    }
    ranges = {
        'GVC_Activation-Deactivation': {'min': 0x00, 'max': 0xFF, 'step': 0x01},
    }

    @staticmethod
    def encode(value):
        """
        This method will encode the input value
        """
        return struct.pack('>B', int(value['GVC_Activation-Deactivation']))

    # pylint: disable=no-self-use
    def decode(self, payload):
        """
        This method will decode the input value 'payload'
        """
        vals = struct.unpack('>B', payload)
        return {
            'GVC_Activation-Deactivation': vals[0],
        }

    def __len__(self):
        """
        Returns encoded payload of 1 byte long
        """
        return 1


class DID0x1200(DidCodec):
    """
    Class for Data Identifier 0x1200 Vehicle Parameter Set 1.
    Encodes and decodes the server response as per the RDF03T.cdd specifications.
    """
    did = 0x1200
    did_name = 'Vehicle Parameter Set 1'
    units = {
        'vertPos': 'm',
        'latOffset': 'mm',
        'longOffset': 'mm',
        'coverDamping': 'dB',
    }
    defaults = {
        'vertPos': 0.60,
        'latOffset': 0,
        'longOffset': 700,
        'coverDamping': 2.50,
    }
    ranges = {
        'vertPos': {'min': 0.20, 'max': 1.00, 'step': 0.01},
        'latOffset': {'min': -900, 'max': 900, 'step': 0.01},
        'longOffset': {'min': 0, 'max': 3000, 'step': 1},
        'coverDamping': {'min': 0.00, 'max': 3.00, 'step': 0.01},
    }

    @staticmethod
    def encode(value):
        """
        This method will decode the input value
        """
        return struct.pack('>IIII',
                           int(value['vertPos'] * 1000),
                           int(value['latOffset'] * 1000),
                           int(value['longOffset']),
                           int(value['coverDamping'] * 100))

    # pylint: disable=no-self-use
    def decode(self, payload):
        """
        This method will decode the input value 'payload'
        """
        vals = struct.unpack('>IIII', payload)
        return {
            'vertPos': vals[0] / 1000,
            'latOffset': vals[1] / 1000,
            'longOffset': vals[2],
            'coverDamping': vals[3] / 100
        }

    def __len__(self):
        """
        Method to return encoded payload is 16 byte long
        """
        return 16


class DID0x1201(DidCodec):
    """
    Class for Data Identifier 0x1201 Vehicle Parameter Set 2
    Encodes and decodes the server response as per the RDF03T.cdd specifications.
    """
    did = 0x1201
    did_name = 'Vehicle Parameter Set 2'

    units = {'wheelBase': 'm'}
    defaults = {'wheelBase': 3.9}
    ranges = {'wheelBase': {'min': 2.0, 'max': 15.0, 'step': 0.1}}

    @staticmethod
    def encode(value):
        """
        This method will decode the input value
        """
        return struct.pack('>III',
                           int(value['wheelBase'] * 1000),
                           0xFFFFFFFF,
                           0xFFFFFFFF)

    # pylint: disable=no-self-use
    def decode(self, payload):
        """
        This method will decode the input value 'payload'
        """
        vals = struct.unpack('>III', payload)
        return {
            'wheelBase': vals[0] / 1000,
            'reserved': vals[1],
            'reserved01': vals[2]
        }

    def __len__(self):
        """
        This method returns encoded payload is 12 byte long
        """
        return 12


class RID0x0007:
    """
    Class for Routine Identifier 0x0007 Service Alignment
    Encodes and decodes the server response as per the RDF03T.cdd specifications.
    """
    rid = 0x0007
    rid_name = 'Service-Alignment'

    @staticmethod
    def request_results_decode(payload):
        """
        This method will decode the result
        """
        vals = struct.unpack('>BfBee', payload)
        return {
            'routineInfo': StandardDataTypes.routineInfo[vals[0]],
            'Progress': int(vals[1]),
            'RoutineResult': hex(vals[2]),
            'SA_Elevation': vals[3] / 100,
            'SA_Azimuth': vals[4] / 100
        }

    def __len__(self):
        """
        return encoded payload 4 bytes long + 1 byte routineInfo
        """
        return 5


class RID0x000B:
    """
    Class for Routine Identifier 0x000B EOL Alignment Complete
    Encodes and decodes the server response as per the RDF03T.cdd specifications.
    """
    rid = 0x000B
    rid_name = 'EOL Alignment Complete'

    @staticmethod
    def start_encode(value):
        """
        This method will decode the input value
        """
        return struct.pack('>ee',
                           int(value['EOL_Elevation'] * 100),
                           int(value['EOL_Azimuth'] * 100),
                           )

    @staticmethod
    def request_results_decode(payload):
        """
        This method will decode the result
        """
        vals = struct.unpack('>BfBee', payload)
        return {
            'routineInfo': StandardDataTypes.routineInfo[vals[0]],
            'Progress': int(vals[1]),
            'RoutineResult': hex(vals[2]),
            'SA_Elevation': vals[3] / 100,
            'SA_Azimuth': vals[4] / 100
        }

    def __len__(self):
        """
        return encoded payload 4 bytes long
        """
        return 4

# pylint: disable=too-few-public-methods
class StandardDataTypes:
    """
    Class for standard data types
    """
    routineInfo = {0x00: 'Routine successfully completed',
                   0x01: 'Routine in progress',
                   0x02: 'Routine stopped without results',
                   0xFF: 'Not supported'}
    verificationResult = {
        0x00: 'Certificate verified, Ownership verification necessary',
        0x01: 'Ownership verified, authentication complete',
        0x02: 'De-authentication successful',
        0x20: 'Ownership verification failed',
        0x30: 'De-authentication failed',
    }

class DTC(IntEnum):
    """
    Enum class for DTC and respective descriptions
    """
    ECU_BLOCKAGE_DETECTION = 0x02fbff
    ECU_SPEED_CORRECTION_VALUE = 0x04fbe2
    ECU_PARAMETER_ERROR = 0x05fbff
    ECU_GGW_DATA_ERROR = 0x05fff3
    ECU_SECURITY_MODULE_ERROR_INVALID_DATA = 0x06ffe2
    ECU_RADOME_HEATING_SC_TO_GROUND = 0x07fbe6
    ECU_SECURITY_MODULE_ERROR_SIGNAL_PROTECTION_INCORRECT = 0x07ffe2
    ECU_RADOME_HEATING_SC_TO_BATTERY = 0x08fbe3
    ECU_SECURITY_MODULE_ERROR_MISSING_MESSAGE = 0x08ffe2
    ECU_RADOME_HEATING_CIRCUIT_OPEN = 0x09fbe5
    ECU_INCOMPATIBLE_SW_COMPONENT = 0x09ffff
    ECU_RADOME_HEATING_UNDERVOLTAGE = 0x0afbe4
    ECU_INCORRECT_VARIANT_CODING = 0x0affff
    ECU_RADOME_HEATING_OVERVOLTAGE = 0x0bfbe3
    ECU_INTERNAL_FAULTS = 0x0bffec
    ECU_STORED_CERTIFICATES = 0x0bffff
    ECU_RADOME_HEATING_RESISTANCE_OUT_OF_RANGE = 0x0cfbe2
    ECU_RADOME_HEATING_INTERNAL_ERROR = 0x0dfbff
    ECU_RADOME_HEATING_ACTIVATION_SIGNAL_INCOMPLETE = 0x0efbe2
    ECU_RADOME_HEATING_UNDERVOLTAGE_SHUTDOWN_FAILURE = 0x0ffbe4
    ECU_CLCS_MONITORING_DTC = 0x0fffe2
    ECU_CLCS_TIMEOUT = 0x0fffe9
    ECU_CLCS_DATA_ERROR = 0x0ffff3
    ECU_VEHICLE_OUTSIDE_DRIVING_LEVEL = 0x0fffff
    ECU_VEHICLE_DATA_ERROR = 0x10f4f3
    ECU_RADOME_HEATING_HW_INCOMPATIBILITY = 0x10fbe7
    ECU_RADOME_HEATING_NOT_ACTIVATED_DIAGNOSTIC = 0x11fbe7
    ECU_INCORRECT_CONFIGURATION = 0x164456
    ECU_HW_TEMP_DTC_FAILURE = 0x16fbeb
    ECU_INTIAL_STARTUP_NOT_PERFORMED = 0x1ca000
    ECU_ETHERNET_LINK_DOWN = 0x4d200b
    ECU_SHORT_DETECTION_WL_TO_UBATT = 0x550a03
    ECU_ETHERNET_BUS_OFF = 0x7f020b
    ECU_DEM_ORC = 0x99ab00
    ECU_DEM_PARK = 0x99ac00
    ECU_DEM_DAS = 0x99ae00
    ECU_DEM_ESP = 0x99b000
    ECU_WAKEUP_LINE_2_MALFUNCTION = 0x99cb00
    ECU_ACCESS_PROTECTION_MALFUNCTION = 0x9a6857
    ECU_SUPPLY_VOLTAGE_TOO_HIGH = 0x9e0000
    ECU_SUPPLY_VOLTAGE_TOO_LOW = 0x9e0001
    ECU_WAKEUP_LINE_MALFUNCTION = 0x9f9700
    ECU_POWER_SUPPLY_SYSTEM_TOO_LOW = 0xa10a00
    ECU_POWER_SUPPLY_SYSTEM_TOO_HIGH = 0xa10b00
    ECU_POWER_SUPPLY_TOO_LOW = 0xa10d00
    ECU_POWER_SUPPLY_TOO_HIGH = 0xa10e00
    ECU_SUPPLY_VOLTAGE_TOO_HIGH_1 = 0xa80003
    ECU_SUPPLY_VOLTAGE_TOO_LOW_1 = 0xa80004
    ECU_INTERIOR_BUS_OFF = 0xc01988
    ECU_POWERTRAIN_BUS_OFF = 0xc02888
    ECU_CHASSIS_BUS_OFF = 0xc03788
    ECU_ENGINE_MISSING_MSG = 0xc10087
    ECU_AQUISITION_MISSING_MSG = 0xc14187
    ECU_CENTRAL_GW_MISSING_MSG = 0xc14687
    ECU_INSTRUMENT_CLUSTER_MISSING_MSG = 0xc15587
    ECU_IGNITION_LOCK_MISSING_MSG = 0xc16887
    ECU_PSM_TIMEOUT = 0xc6ffe9
    ECU_PSM_DATA_ERROR = 0xc6fff3
    ECU_VRDU_TIMEOUT = 0xc8ffe9
    ECU_VRDU_DATA_ERROR = 0xc8fff3
    ECU_FRONT_END_BUS_OFF = 0xd03788
    ECU_DIAGNOSTIC_BUS_OFF = 0xd03888
    ECU_CHASSIS_BUS_2_OFF = 0xd03d88
    ECU_ETHERNET_MALFUNCTION = 0xd03f00
    ECU_SECURITY_MODULE_ERROR_INVALID_DATA_1 = 0xd12081
    ECU_SECURITY_MODULE_ERROR_MISSING_MESSAGE_1 = 0xd12083
    ECU_SECURITY_MODULE_ERROR_SIGNAL_PROTECTION_INCORRECT_1 = 0xd12087
    ECU_ACCESS_TO_LIN_BUS_FAILED = 0xd13d00
    ECU_EBS_TIMEOUT = 0xebfee9
    ECU_EBS_DATA_ERROR = 0xebfef3
    ECU_HW_MALFUNCTION = 0xf8faec
    ECU_DISTURBANCE = 0xf9faec
    ECU_DISTURBANCE_CAT2 = 0xf9faff
    ECU_INPALUSIBLE_ENV_SIGNAL = 0xfafaff
    ECU_DPU_RESET_ERROR = 0xfbfaed
    ECU_NOT_ALLIGNED = 0xfcfaed
    ECU_MISALLIGNED_EOL_SERVICE = 0xfdfae7
    ECU_MISALLIGNED_MONITORING = 0xfdfaed

    @classmethod
    def has_value(cls, value):
        """
        This method will check and return the value
        """
        return any(x for x in cls if x.value == value)


CLIENT_CONFIG = {
    'exception_on_negative_response': True,
    'exception_on_invalid_response': True,
    'exception_on_unexpected_response': True,
    'security_algo': None,
    'security_algo_params': None,
    'tolerate_zero_padding': True,
    'ignore_all_zero_dtc': True,
    # Not specified in standard. 2 bytes matches other services format.
    'dtc_snapshot_did_size': 2,
    'server_address_format': None,		# 8,16,24,32,40
    'server_memorysize_format': None,		# 8,16,24,32,40
    'data_identifiers': {
        0xF100: DID0xF100ActiveDiagnosticInformation(),
        0x1200: DID0x1200(),
        0x1201: DID0x1201(),
        0x1205: DID0x1205(),
        0x0182: DID0x0182(),
        0x018C: DID0x018C(),
    },
    'routine_identifiers': {
        0x0007: RID0x0007(),
        0x000B: RID0x000B()
    },
    'input_output': {},
    'request_timeout': 5,
    'p2_timeout': 5,      # TCP connection timeout
    'p2_star_timeout': 5,
    'standard_version': 2020,   # 2006, 2013, 2020
    'use_server_timing': False,
}
