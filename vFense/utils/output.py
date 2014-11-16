import logging
import logging.config
import re

from prettytable import PrettyTable
from vFense._constants import VFENSE_LOGGING_CONFIG


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

def tableify(data):
    """Convert either a dictionary or a list of dictionaries into a table
    Args:
        data (list|dict): List of dictionaries or a dictionary of the data.

    Basic Usage:
        >>> from vFense.utils.output import tableify
        >>> data [{'name': 'linuxdynasty'}]
        >>> tableify(data)

    Returns:
        String
    """
    table_output = None
    try:
        if isinstance(data, list):
            if isinstance(data[0], dict):
                table = PrettyTable(data[0].keys())
                for item in data:
                    table.add_row(item.values())
                table_output = table.get_string()

        elif isinstance(data, dict):
            table = PrettyTable(data.keys())
            table.add_row(data.values())
            table_output = table.get_string()

    except Exception as e:
        logger.exception(e)

    return table_output

def csvify(data):
    """Convert either a dictionary or a list of dictionaries into csv output
    Args:
        data (list|dict): List of dictionaries or a dictionary of the data.

    Basic Usage:
        >>> from vFense.utils.output import csvify
        >>> data [{'name': 'linuxdynasty'}]
        >>> csvify(data)

    Returns:
        String
    """
    csv_string = None
    try:
        if isinstance(data, list):
            if isinstance(data[0], dict):
                csv_string = ';'.join(data[0].keys()) + '\n'
                for item in data:
                    csv_string += (
                        ';'.join(str(v) for v in item.values()) + '\n'
                    )

        elif isinstance(data, dict):
            csv_string = ';'.join(data.keys()) + '\n'
            csv_string += (
                ';'.join(str(v) for v in data.values()) + '\n'
            )

    except Exception as e:
        logger.exception(e)

    return csv_string
