import json
import pandas as pd
from datetime import datetime


class DanswerIngestionPayloadBuilder:
    def __init__(self):
        self.payload = {
            "cc_pair_id": 0,
            "document": {
                "id": None,
                "sections": [],
                "source": None,
                "semantic_identifier": None,
                "doc_updated_at": None,
                "metadata": None
            }
        }

    def add_section(self, text, link=None):
        """
        Add a section to the content.

        :param text: The text content of the section
        :param link: Optional link associated with the section
        """
        section = {"text": text}
        if link:
            section["link"] = link
        self.payload['document']['sections'].append(section)

    def set_cc_pair_id(self, cc_pair_id: int):
        self.payload['cc_pair_id'] = cc_pair_id

    def get_payload(self, astype='dict'):
        """
        Returns the payload in the specified format.

        Args:
            astype (str): The format of the payload. Defaults to 'dict'. Options are 'dict' and 'json'.

        Returns:
            dict or str: The payload in the specified format.
        """
        if astype == 'dict':
            return self.payload
        elif astype == 'json':
            return json.dumps(self.payload)
        return self.payload

    def build_payload(self, id, sections, source, semantic_identifier, update, metadata=None, cc_pair_id=0):
        """
        Builds and returns a payload dictionary for Danswer ingestion.

        Args:
            id: this is the unique ID of the document, if a document of this ID exists it will be updated/replaced. If not provided, a document ID is generated from the semantic_identifier field instead and returned in the response.
            sections: list of sections each containing textual content and an optional link. The document chunking tries to avoid splitting sections internally and favors splitting at section borders. Also, the link of the document at query time is the link of the best matched section.
            source: Source type, full list can be checked by searching for DocumentSource here
            semantic_identifier: This is the “Title” of the document as shown in the UI (see image below)
            metadata: Used for the “Tags” feature which is displayed in the UI. The values can be either strings or list of strings
            doc_updated_at: The time that the document was last considered updated. By default, there is a time based score decay around this value when the document is considered during search.
            cc_pair_id: This is the “Connector” ID seen on the Connector Status pages. For example, if running locally, it might be http://localhost:3000/admin/connector/2. This allows attaching the ingestion doc to existing connectors so they can be assigned to groups or deleted together with the connector. If not provided or set to 1 explicitly, it is considered part of the default catch-all connector.

        Returns:
            dict: A payload dictionary containing the document information.
        """

        if id:
            self.payload['document']["id"] = id
        if sections:
            self.payload['document']["sections"] = sections
        if source:
            self.payload['document']["source"] = source
        if semantic_identifier:
            self.payload['document']["semantic_identifier"] = semantic_identifier
        if metadata:
            self.payload['document']["metadata"] = metadata
        if update:
            self.payload['document']["doc_updated_at"] = update
        if cc_pair_id:
            self.payload['document']["cc_pair_id"] = cc_pair_id
        return self.payload

    def clear_payload(self):
        """
        Clear the current sections to start building a new document.
        """
        self.payload = {"document": {}}


class DanswerJSONFileBuilder:
    def __init__(self, yt_json_data, filename):
        self.filename = filename
        self.data = yt_json_data

    def save(self):
        """
        Saves the data to a JSON file.

        Parameters:
            None

        Returns:
            None
        """
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)


class DanswerFileMetadataBuilder:
    def __init__(self, filename):
        self.filename = filename
        self.metadata = []

    def add_record_dict(self, record: dict):
        """
        Adds a record as dictionary type to the metadata list.
        If you want to add a record with separated parameters, use add_record() instead.

        Parameters:
            record (dict): The record dictionary to be added.

        Returns:
            None
        """
        self.metadata.append(record)

    def add_record(self, filename: str, file_display_name: str, primary_owners=None, link=None):
        """
        Adds a new record to the metadata list. Each parameter is passed in separately.
        If you want to add a record as dictionary type, use add_record_dict() instead.

        Parameters:
            filename (str): The filename of the record.
            file_display_name (str): The display name of the file.
            primary_owners (optional): The primary owners of the file.
            link (optional): The link to the file.

        Returns:
            None
        """
        record = {
            "filename": filename,
            "file_display_name": file_display_name,
            "primary_owners": primary_owners,
            "link": link
        }
        self.add_record_dict(record)

    def save(self):
        """
        Saves the metadata to a JSON file.

        Parameters:
            None

        Returns:
            None
        """
        with open(self.filename, 'w') as f:
            json.dump(self.metadata, f)
