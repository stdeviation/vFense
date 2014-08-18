import os
import gc
import re
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from lxml import etree
from re import sub
from vFense.plugins.vuln.cve import (
    Cve, CvssVector, CveDescriptions, CveReferences,
    CveVulnSoft, CveVulnSoftVers
)
from vFense.plugins.vuln.cve._constants import (
    CVEDataDir, NVDFeeds, CVEStrings, CVECategories
)

from vFense.plugins.vuln.cve._db import insert_cve_data
from vFense.plugins.vuln.cve.downloader import start_nvd_xml_download
from vFense.utils.common import date_parser, timestamp_verifier

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')


class NvdParser(object):
    """The purpose of this class, is to parse NVD/CVE XML 1.2 Data Files.
    """
    def get_entry_info(self, entry):
        """Parse the top level entry object in the XML file
        Args:
            entry (lxml.etree._Element): This is an lxml Element
        Returns:
            Cve instance
        """
        cve = Cve()
        cve.fill_in_defaults()
        attrib = entry.attrib
        cve.cve_id = unicode(attrib.get(CVEStrings.CVE_NAME))
        cve.severity = attrib.get(CVEStrings.CVE_SEVERITY)
        cve.date_posted = (
            timestamp_verifier(
                date_parser(attrib.get(CVEStrings.CVE_PUBLISHED_DATE))
            )
        )
        cve.date_modified = (
            timestamp_verifier(
                date_parser(attrib.get(CVEStrings.CVE_MODIFIED_DATE))
            )
        )
        cve.score = float(attrib.get(CVEStrings.CVSS_SCORE, 0.0))
        cve.base_score = float(attrib.get(CVEStrings.CVSS_BASE_SCORE, 0.0))
        cve.impact_score = (
            float(attrib.get(CVEStrings.CVSS_IMPACT_SUBSCORE, 0.0))
        )
        cve.exploit_score = (
            float(attrib.get(CVEStrings.CVSS_EXPLOIT_SUBSCORE, 0.0))
        )
        cve.vector = (
            self._parse_vectors(attrib.get(CVEStrings.CVSS_VECTOR))
        )
        cve.version = unicode(attrib.get(CVEStrings.CVSS_VERSION))

        return(cve)

    def get_descriptions(self, entry):
        """Parse the desc object under the top level entry object
        in the XML file.

        Args:
            entry (lxml.etree._Element): This is an lxml Element

        Returns:
            Tuple (descriptions, categories)
            [
                {
                    "source": "cve",
                    "description": "GnuTLS before 2.7.6, when the GNUTLS_VERIFY_ALLOW_X509_V1_CA_CRT flag is not enabled, treats version 1 X.509 certificates as intermediate CAs, whi
                        ch allows remote attackers to bypass intended restrictions by leveraging a X.509 V1 certificate from a trusted CA to issue new certificates, a different vulnerability tha
                        n CVE-2014-1959."
                }
            ]
        """
        list_of_descriptions = []
        categories = []
        for desc in entry:
            description = CveDescriptions()
            description.description = unicode(desc.text),
            description.source = (
                desc.attrib.get(CVEStrings.DESCRIPTION_SOURCE)
            )

            for category in CVECategories.get_values():
                if re.search(category, unicode(desc.text), re.IGNORECASE):
                    categories.append(category)

            list_of_descriptions.append(description.to_dict())

        return(list_of_descriptions, categories)

    def get_refs(self, entry):
        """Parse the refs object under the top level entry object
        in the XML file.

        Args:
            entry (lxml.etree._Element): This is an lxml Element

        Returns:
            [
                {
                    "url": "https://gitorious.org/gnutls/gnutls/commit/c8dcbedd1fdc312f5b1a70fcfbc1afe235d800cd",
                    "source": "CONFIRM",
                    "id": "https://gitorious.org/gnutls/gnutls/commit/c8dcbedd1fdc312f5b1a70fcfbc1afe235d800cd"
                },
                {
                    "url": "https://bugzilla.redhat.com/show_bug.cgi?id=1069301",
                    "source": "CONFIRM",
                    "id": "https://bugzilla.redhat.com/show_bug.cgi?id=1069301"
                },
                {
                    "url": "http://thread.gmane.org/gmane.comp.security.oss.general/12127",
                    "source": "MLIST",
                    "id": "[oss-security] 20140227 Re: CVE Request - GnuTLS corrects flaw in certificate verification (3.1.x/3.2.x)"
                },
            ]
        """
        list_of_refs = []
        for reference in entry:
            ref = CveReferences()
            ref.url = reference.attrib.get(CVEStrings.REF_URL)
            ref.source = reference.attrib.get(CVEStrings.REF_SOURCE)
            ref.id = reference.text
            ref.signature = reference.attrib.get(CVEStrings.REF_SIG, False)
            if ref.signature:
                ref.signature = True
            ref.advisory = reference.attrib.get(CVEStrings.REF_ADV, False)
            if ref.advisory:
                ref.advisory = True
            ref.patch = reference.attrib.get(CVEStrings.REF_PATCH, False)
            if ref.patch:
                ref.patch = True
            list_of_refs.append(ref.to_dict())

        return(list_of_refs)

    def get_vulns_soft(self, entry):
        """Parse the vuln_soft object under the top level entry object
        in the XML file.

        Args:
            entry (lxml.etree._Element): This is an lxml Element
        """
        vuln_soft_list = []
        for vulns_soft in entry:
            vuln_soft = CveVulnSoft()
            vuln_soft.fill_in_defaults()
            vuln_soft.vendor = vulns_soft.attrib.get(CVEStrings.VENDOR)
            vuln_soft.name = vulns_soft.attrib.get(CVEStrings.VENDOR_NAME)
            vulns = vulns_soft.getchildren()
            for vuln in vulns:
                version = CveVulnSoftVers()
                version.number = vuln.attrib.get("num")
                version.previous = vuln.attrib.get("prev")
                version.edition = vuln.attrib.get("edition")
                vuln_soft.versions.append(version.to_dict())
            vuln_soft_list.append(vuln_soft.to_dict())

        return(vuln_soft_list)

    def _parse_vectors(self, unformatted_vector):
        """Parse the vectors in the top level entry object in the XML file
        Args:
            unformatted_vector ():
        """
        formatted_vectors = []
        if unformatted_vector:
            vectors = sub('\(|\)', '', unformatted_vector).split('/')
            for vector in vectors:
                metric, value = vector.split(':')
                cvss_vectors = (
                    CvssVector(
                        untranslated_metric=metric, untranslated_value=value
                    )
                )
                formatted_vectors.append(cvss_vectors.to_dict())

        return(formatted_vectors)


def parse_cve_and_udpatedb(
    download_latest_nvd=True,
    nvd_files=[CVEDataDir.NVD_CURRENT_FILE, CVEDataDir.NVD_MODIFIED_FILE]
        ):

    """This begins the actual parsing of the xml files and loads up the data
        into the database
    Kwargs:
        download_latest_nvd (bool): Whether or not to download
            the latest nvd data
        nvd_files (list): This is a list of the files you want to parse
    """

    if download_latest_nvd:
        start_nvd_xml_download()
    parser = NvdParser()
    for nvd_file in nvd_files:
        cve_data_list = []
        cve_data = {}
        for event, entry in etree.iterparse(nvd_file, events=['start', 'end']):
            if entry.tag == NVDFeeds.ENTRY and event == 'start':
                cve = parser.get_entry_info(entry)

            if entry.tag == NVDFeeds.DESC and event == 'start':
                cve.descriptions, cve.vulnerability_categories = (
                    parser.get_descriptions(entry)
                )

            if entry.tag == NVDFeeds.REFS and event == 'start':
                cve.references = parser.get_refs(entry)

            if entry.tag == NVDFeeds.VULN_SOFT and event == 'start':
                cve.vuln_soft = parser.get_vulns_soft(entry)

            if entry.tag == NVDFeeds.ENTRY and event == 'end':
                cve_data_list.append(cve.to_dict_db())


        status, count, _, _ = insert_cve_data(cve_data_list)
        xml_file = nvd_file.split('/')[-1]
        if isinstance(count, tuple):
            msg = (
                'cves inserted %d and replaced %d for file %s' %
                (count[0], count[1], xml_file)
            )
        else:
            msg = 'cves inserted %d for file %s' % (count, xml_file)

        print msg
        logger.info(msg)
        del cve_data_list
        del cve_data
        gc.collect()


def load_up_all_xml_into_db():
    nvd_files = []
    if not os.path.exists(CVEDataDir.XML_DIR):
        os.makedirs(CVEDataDir.XML_DIR)
    #xml_exists = os.listdir(CVEDataDir.XML_DIR)
    logger.info('starting cve/nvd update process')
    logger.info('downloading nvd/cve xml data files')
    start_nvd_xml_download()
    for directory, _, files in os.walk(CVEDataDir.XML_DIR):
        for xml_file in files:
            nvd_file = os.path.join(directory, xml_file)
            nvd_files.append(nvd_file)

    nvd_files.sort()
    parse_cve_and_udpatedb(False, nvd_files)
    #update_cve_categories()
    logger.info('finished cve/nvd update process')
    gc.collect()
