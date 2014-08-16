from vFense.core._constants import CommonKeys
from vFense.core._db_constants import DbTime
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes
from vFense.plugins.vuln.cve._constants import (
    CveDefaults, CVEVectors, VectorKeys, DescriptionKeys,
    CVSS_BASE_VECTORS, CVSS_BASE_VECTOR_AV_VALUES, ReferenceKeys,
    CVSS_BASE_VECTOR_AC_VALUES, CVSS_BASE_VECTOR_AU_VALUES,
    CVSS_BASE_VECTOR_C_VALUES, CVSS_BASE_VECTOR_I_VALUES,
    CVSS_BASE_VECTOR_A_VALUES, CVSS_TEMPORAL_VECTORS,
    CVSS_TEMPORAL_VECTOR_E_VALUES, CVSS_TEMPORAL_VECTOR_RL_VALUES,
    CVSS_TEMPORAL_VECTOR_RC_VALUES, CVSS_ENVIRONMENTAL_VECTORS,
    CVSS_ENVIRONMENTAL_VECTOR_CDP_VALUES, CVSS_ENVIRONMENTAL_VECTOR_TD_VALUES,
    CVSS_ENVIRONMENTAL_VECTOR_CR_VALUES, CVSS_ENVIRONMENTAL_VECTOR_IR_VALUES,
    CVSS_ENVIRONMENTAL_VECTOR_AR_VALUES
)
from vFense.plugins.vuln.cve._db_model import CveKeys


class Cve(object):
    """Used to represent an instance of a cve.
    Kwargs:
    cve_id (str): The Common Vulnerability and Exposure ID
        Example.. CVE-2014-2363
    descriptions (list of dictionaries):
        Example.. [
            {
                u'source': u'cve',
                u'description': u'Morpho Itemiser 3 8.17 has hardcoded administrative credentials, which makes it easier for remote attackers to obtain access via a login request.'
            }
        ]
    severity (str): The vendor supplied severity.
        Example... Important, Critical, Security, etc..
    date_posted (int|float): The date this vulnerability was posted in
        epoch time.
        Example... 1408226168.046107 or 1408226180
    references (list): list of the vendor supplied url, id, and source.
        Example.. [
        {
            u'url': u'http://ics-cert.us-cert.gov/advisories/ICSA-14-205-01',
            u'source': u'MISC',
            u'id': u'http://ics-cert.us-cert.gov/advisories/ICSA-14-205-01'
         }
    ]
    reject (str):
    vulns_soft (list of dictionaries):
    vulnerability_categories (list): List of categories, this cve belongs too.
        Example [DDOS, Exploit, Cross Site Scripting]
    score (int): The CVSS base score. 0 - 10

    """


    def __init__(self, cve_id=None, descriptions=None, severity=None,
                 date_posted=None, date_modified=None, references=None,
                 reject=None, vulns_soft=None, vulnerability_categories=None,
                 score=None, base_score=None, impact_score=None,
                 exploit_score=None, vector=None, version=None,
                 cvss_type=None):

        self.cve_id = cve_id
        self.descriptions = descriptions
        self.date_posted = date_posted
        self.date_modified = date_modified
        self.severity = severity
        self.references = references
        self.reject = reject
        self.vuln_soft = vulns_soft
        self.vulnerability_categories = vulnerability_categories
        self.score = score
        self.base_score = base_score
        self.impact_score = impact_score
        self.exploit_score = exploit_score
        self.vector = vector
        self.version = version
        self.cvss_type = cvss_type

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """

        if not self.vulnerability_categories:
            self.vulnerability_categories = (
                CveDefaults.vulnerability_categories()
            )

        if not self.references:
            self.references = (
                CveDefaults.references()
            )

        if not self.descriptions:
            self.descriptions = (
                CveDefaults.descriptions()
            )

        if not self.date_modified:
            self.date_modified = 0

    def get_invalid_fields(self):
        """Check the app for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        invalid_fields = []

        if self.descriptions:
            if not isinstance(self.descriptions, list):
                invalid_fields.append(
                    {
                        CveKeys.Descriptions: self.descriptions,
                        CommonKeys.REASON: (
                            '{0} not a valid list'
                            .format(self.descriptions)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.references:
            if not isinstance(self.references, list):
                invalid_fields.append(
                    {
                        CveKeys.References: self.references,
                        CommonKeys.REASON: (
                            '{0} not a valid list'
                            .format(self.references)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.vulnerability_categories:
            if not isinstance(self.vulnerability_categories, list):
                invalid_fields.append(
                    {
                        CveKeys.Categories: (
                            self.vulnerability_categories
                        ),
                        CommonKeys.REASON: (
                            '{0} not a valid list'
                            .format(self.vulnerability_categories)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.date_posted:
            if (not isinstance(self.date_posted, float) and
                    not isinstance(self.date_posted, int)):
                invalid_fields.append(
                    {
                        CveKeys.DatePosted: self.date_posted,
                        CommonKeys.REASON: (
                            '{0} not a valid date, float or int only'
                            .format(type(self.date_posted))
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.date_modified:
            if (not isinstance(self.date_modified, float) and
                    not isinstance(self.date_modified, int)):
                invalid_fields.append(
                    {
                        CveKeys.DateModified: self.date_modified,
                        CommonKeys.REASON: (
                            '{0} not a valid date, float or int only'
                            .format(type(self.date_modified))
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )


        return invalid_fields

    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """

        return {
            CveKeys.CveId: self.cve_id,
            CveKeys.Descriptions: self.descriptions,
            CveKeys.Severity: self.severity,
            CveKeys.References: self.references,
            CveKeys.Reject: self.reject,
            CveKeys.VulnsSoft: self.vuln_soft,
            CveKeys.Categories: self.vulnerability_categories,
            CveKeys.Score: self.score,
            CveKeys.BaseScore: self.base_score,
            CveKeys.ImpactScore: self.impact_score,
            CveKeys.ExploitScore: self.exploit_score,
            CveKeys.Vector: self.vector,
            CveKeys.Version: self.version,
            CveKeys.Type: self.cvss_type,
        }

    def to_dict_db(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """

        data = {
            CveKeys.DatePosted: (
                DbTime.epoch_time_to_db_time(self.date_posted)
            ),
            CveKeys.DateModified: (
                DbTime.epoch_time_to_db_time(self.date_modified)
            ),
        }
        return dict(self.to_dict().items() + data.items())


    def to_dict_non_null(self):
        """ Use to get non None fields of an install. Useful when
        filling out just a few fields to perform an install.

        Returns:
            (dict): a dictionary with the non None fields of this install.
        """
        install_dict = self.to_dict()

        return {k:install_dict[k] for k in install_dict
                if install_dict[k] != None}


class CvssVector(object):
    """Used to represent an instance of a vulnerability."""

    def __init__(self, metric=None, value=None, untranslated_metric=None,
                 untranslated_value=None):
        """
        Kwargs:
        """
        self.metric = metric
        self.value = value
        self.untranslated_metric = untranslated_metric
        self.untranslated_value = untranslated_value

        if (self.untranslated_metric and self.untranslated_value and
                not self.metric and not self.value):
            self.translate()

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """
        pass

    def translate(self):
        if self.untranslated_metric in CVSS_BASE_VECTORS:
            self.metric = CVSS_BASE_VECTORS[self.untranslated_metric]

            if self.untranslated_metric == CVEVectors.BASE_METRIC_AV:
                self.value = (
                    CVSS_BASE_VECTOR_AV_VALUES[self.untranslated_value]
                )

            elif self.untranslated_metric == CVEVectors.BASE_METRIC_AC:
                self.value = (
                    CVSS_BASE_VECTOR_AC_VALUES[self.untranslated_value]
                )

            elif self.untranslated_metric == CVEVectors.BASE_METRIC_Au:
                self.value = (
                    CVSS_BASE_VECTOR_AU_VALUES[self.untranslated_value]
                )

            elif self.untranslated_metric == CVEVectors.BASE_METRIC_C:
                self.value = (
                    CVSS_BASE_VECTOR_C_VALUES[self.untranslated_value]
                )

            elif self.untranslated_metric == CVEVectors.BASE_METRIC_I:
                self.value = (
                    CVSS_BASE_VECTOR_I_VALUES[self.untranslated_value]
                )

            elif self.untranslated_metric == CVEVectors.BASE_METRIC_A:
                self.value = (
                    CVSS_BASE_VECTOR_A_VALUES[self.untranslated_value]
                )

        elif self.untranslated_metric in CVSS_TEMPORAL_VECTORS:
            self.metric = (
                CVSS_TEMPORAL_VECTORS[self.untranslated_metric]
            )

            if self.metric == CVEVectors.TEMPORAL_METRIC_E:
                self.value = (
                    CVSS_TEMPORAL_VECTOR_E_VALUES[self.untranslated_value]
                )

            elif self.untranslated_metric == CVEVectors.TEMPORAL_METRIC_RL:
                self.value = (
                    CVSS_TEMPORAL_VECTOR_RL_VALUES[self.untranslated_value]
                )

            elif self.untranslated_metric == CVEVectors.TEMPORAL_METRIC_RC:
                self.value = (
                    CVSS_TEMPORAL_VECTOR_RC_VALUES[self.untranslated_value]
                )

        elif self.untranslated_metric in CVSS_ENVIRONMENTAL_VECTORS:
            self.metric = (
                CVSS_ENVIRONMENTAL_VECTORS[self.untranslated_metric]
            )

            if self.metric == CVEVectors.ENVIRONMENTAL_METRIC_CDP:
                self.value = (
                    CVSS_ENVIRONMENTAL_VECTOR_CDP_VALUES[self.untranslated_value]
                )

            elif self.untranslated_metric == CVEVectors.ENVIRONMENTAL_METRIC_TD:
                self.value = (
                    CVSS_ENVIRONMENTAL_VECTOR_TD_VALUES[self.untranslated_value]
                )

            elif self.untranslated_metric == CVEVectors.ENVIRONMENTAL_METRIC_CR:
                self.value = (
                    CVSS_ENVIRONMENTAL_VECTOR_CR_VALUES[self.untranslated_value]
                )

            elif self.untranslated_metric == CVEVectors.ENVIRONMENTAL_METRIC_IR:
                self.value = (
                    CVSS_ENVIRONMENTAL_VECTOR_IR_VALUES[self.untranslated_value]
                )

            elif self.untranslated_metric == CVEVectors.ENVIRONMENTAL_METRIC_AR:
                self.value = (
                    CVSS_ENVIRONMENTAL_VECTOR_AR_VALUES[self.untranslated_value]
                )


    def get_invalid_fields(self):
        """Check the app for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        invalid_fields = []

        if self.metric:
            if self.metric not in CVEVectors.get_values():
                invalid_fields.append(
                    {
                        CveKeys.Vector: self.metric,
                        CommonKeys.REASON: (
                            '{0} not a valid metric'
                            .format(self.metric)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        return invalid_fields

    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """

        return {
            VectorKeys.Metric: self.metric,
            VectorKeys.Value: self.value,
        }


    def to_dict_non_null(self):
        """ Use to get non None fields of an install. Useful when
        filling out just a few fields to perform an install.

        Returns:
            (dict): a dictionary with the non None fields of this install.
        """
        install_dict = self.to_dict()

        return {k:install_dict[k] for k in install_dict
                if install_dict[k] != None}


class CveDescriptions(object):
    """Used to represent an instance of a vulnerability."""

    def __init__(self, description=None, source=None):
        """
        Kwargs:
        """
        self.description = description
        self.source = source


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """
        pass

    def get_invalid_fields(self):
        """Check the app for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        return []

    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """

        return {
            DescriptionKeys.Description: self.description,
            DescriptionKeys.Source: self.source,
        }


    def to_dict_non_null(self):
        """ Use to get non None fields of an install. Useful when
        filling out just a few fields to perform an install.

        Returns:
            (dict): a dictionary with the non None fields of this install.
        """
        install_dict = self.to_dict()

        return {k:install_dict[k] for k in install_dict
                if install_dict[k] != None}


class CveReferences(object):
    """Used to represent an instance of a vulnerability."""

    def __init__(self, url=None, source=None, id=None):
        """
        Kwargs:
        """
        self.url = url
        self.source = source
        self.id = id


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """
        pass

    def get_invalid_fields(self):
        """Check the app for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        return []

    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """

        return {
            ReferenceKeys.URL: self.url,
            ReferenceKeys.Source: self.source,
            ReferenceKeys.Id: self.id,
        }


    def to_dict_non_null(self):
        """ Use to get non None fields of an install. Useful when
        filling out just a few fields to perform an install.

        Returns:
            (dict): a dictionary with the non None fields of this install.
        """
        install_dict = self.to_dict()

        return {k:install_dict[k] for k in install_dict
                if install_dict[k] != None}
