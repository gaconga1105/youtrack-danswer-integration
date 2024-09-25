import logging
import traceback
import subprocess
from pathlib import Path

from danswer.danswer_content_builder import *
from danswer.danswer_client import *
from youtrack.youtrack_client import *
from youtrack.youtrack_util import *
from utils import formatter as fmt


class YouTrackDanswerIntegration:
    def __init__(self, youtrack_url, youtrack_token, danswer_url=None, danswer_key=None, cc_pair_id: int = None,
                 config: dict = None, logger=None):
        use_https = config['youtrack'].get('use_https', True)
        verify_ssl = config['youtrack'].get('verify_ssl', True)

        self.youtrack_host = youtrack_url
        self.youtrack_api = YouTrackAPI(youtrack_url, youtrack_token, use_https=use_https, verify_ssl=verify_ssl)
        self.danswer_api = DanswerAPI(danswer_url, danswer_key) if danswer_url and danswer_key else None
        self.cc_pair_id = cc_pair_id
        self.logger = logger or logging.getLogger(__name__)
        self.config = config

    def convert_danswer_api(self, issue) -> DanswerIngestionPayloadBuilder:
        try:
            issue_id = issue['id']
            issue_key = issue['idReadable']

            section_1 = fmt.strip_html(issue['description'])
            if not section_1:
                section_1 = 'No description'
            source = 'ingestion_api'
            semantic_identifier = issue_key + ' - ' + issue['summary']
            update_time = datetime.now().isoformat() + "Z"
            links = extract_linked_issues(issue)
            issue_type = {
                'Support': 'Support Ticket',
                'Incidents': 'Incident'
            }.get(extract_project_name(issue), 'Unknown')

            metadata = {
                "type": issue_type,
                "issueKey": issue_key,
                "organization": extract_custom_field(issue, 'Organization'),
                "recipients": extract_custom_field(issue, 'Active recipients'),
                "created": fmt.timestamp_to_datetime(issue['created']),
                "links": list(map(lambda key: generate_issue_link(self.youtrack_host, key), links)),
                "state": extract_custom_field(issue, 'State'),
            }

            payload_builder = DanswerIngestionPayloadBuilder()

            payload_builder.build_payload(
                id=issue_id,
                sections=None,  # skip sections passing
                source=source,
                update=update_time,
                semantic_identifier=semantic_identifier,
                metadata=metadata)

            payload_builder.add_section(
                text=fmt.encode_urls(section_1),
                link=generate_issue_link(self.youtrack_host, issue_key)
            )

            payload_builder.set_cc_pair_id(self.cc_pair_id)

            # Add comments
            for cmt in issue['comments']:
                if not fmt.encode_urls(fmt.strip_html(cmt['text'])):
                    continue
                payload_builder.add_section(
                    text=fmt.encode_urls(fmt.strip_html(cmt['text'])),
                    link=generate_comment_link(self.youtrack_host, issue_key, cmt['id'])
                )

            return payload_builder
        except Exception as e:
            self.logger.error(f'Error processing {issue["idReadable"]}: {e}')
            self.logger.error(f'Stack trace of {issue["idReadable"]}: \n {traceback.format_exc()}')

    def convert_danswer_file(self, issue, save_path: Path, metadata):
        try:
            # Format html content
            issue['description'] = fmt.strip_html(issue['description'])
            for cmt in issue['comments']:
                cmt['text'] = fmt.strip_html(cmt['text'])

            # Rename fields
            issue['issueKey'] = issue['idReadable']
            issue['organization'] = extract_custom_field(issue, 'Organization')
            issue['state'] = extract_custom_field(issue, 'State')
            issue['recipients'] = extract_custom_field(issue, 'Active recipients')

            # Generate links for each linked issue
            linked_issue_keys = extract_linked_issues(issue)
            issue['links'] = list(map(lambda key: generate_issue_link(self.youtrack_host, key), linked_issue_keys))

            # Format timestamp fields
            issue['created'] = fmt.timestamp_to_datetime(issue['created'])

            # Format comments
            for cmt in issue['comments']:
                cmt['created'] = fmt.timestamp_to_datetime(cmt['created'])
                cmt['author'] = cmt['author']['name']
                # Remove unnecessary fields
                cmt.pop('$type', None)
                cmt.pop('id', None)

            # Specify Issue type
            issue['type'] = {
                'Support': 'Support Ticket',
                'Incidents': 'Incident'
            }.get(extract_project_name(issue), 'Unknown')

            issue_path = (save_path / f'{issue["issueKey"]}').with_suffix('.json')

            dr_builder = DanswerJSONFileBuilder(issue, issue_path)

            # Add metadata as guidelines at https://docs.danswer.dev/connectors/file
            metadata.add_record(
                filename=f'{issue["issueKey"]}.json',
                file_display_name=f'{issue["issueKey"]} - {issue["summary"]}',
                primary_owners=self.config['danswer']['metadata_primary_owners'],
                link=generate_issue_link(self.youtrack_host, issue['issueKey'])
            )

            # Remove unnecessary fields
            dr_builder.data.pop('$type', None)
            dr_builder.data.pop('customFields', None)
            dr_builder.data.pop('idReadable', None)
            dr_builder.data.pop('id', None)
            dr_builder.data.pop('project', None)

            # Save data to file
            dr_builder.save()

            return issue_path

        except Exception as e:
            self.logger.error(f'Error processing {issue["idReadable"]}: {e}')
            self.logger.error(traceback.format_exc())
            return None

    def youtrack_to_danswer_api(self, issues_data):
        self.logger.info(f'Sending {len(issues_data)} YouTrack issues to Danswer API')
        progress = 0
        for issue in issues_data:
            payload = self.convert_danswer_api(issue)
            cc_pair_id = payload.get_payload()['cc_pair_id']
            try:
                response = self.danswer_api.post_ingest_document(payload.get_payload(astype='dict'))
                progress += 1
                if response['already_existed']:
                    self.logger.info(f'Item {issue["idReadable"]} updated in Connector {cc_pair_id} ({progress}/{len(issues_data)}).')
                elif not response['already_existed']:
                    self.logger.info(f'Item {issue["idReadable"]} added to Connector {cc_pair_id} ({progress}/{len(issues_data)}).')
            except Exception as e:
                self.logger.error(f'Error processing issue {issue["idReadable"]}:')
                self.logger.error(f'{traceback.format_exc()}')

        self.logger.info(f'Completed sending {len(issues_data)} YouTrack items to Danswer API')

    def youtrack_to_danswer_file(self, issues_data, save_path: Path):
        mt_path = (save_path / '.danswer_metadata').with_suffix('.json')
        mt_file = DanswerFileMetadataBuilder(mt_path)

        self.logger.info(f'Converting {len(issues_data)} YouTrack items to Danswer JSON files format')
        progress = 0
        for issue in issues_data:
            item_path = self.convert_danswer_file(issue, save_path, mt_file)
            progress += 1
            self.logger.info(f'Saved {issue["issueKey"]} to {item_path} ({progress}/{len(issues_data)})')


        mt_file.save()
        self.logger.info(f'Saved metadata file {mt_path}')

        zip_command = f'zip -r {save_path / self.config["danswer"]["zip_folder_name"]} {save_path} -i \* .\*'
        try:
            subprocess.run(zip_command, shell=True, check=True)
            self.logger.info(f'Created zip file at {save_path / self.config["danswer"]["zip_folder_name"]}')
        except subprocess.CalledProcessError as e:
            self.logger.error(f'Error zipping files: {e}')

    def fetch_all_youtrack_issues(self, query, fields):
        """
        Fetches all YouTrack issues based on the provided query and fields.

        Args:
            query (str): The query string used to search for issues.
            fields (str): Comma-separated list of fields to retrieve.

        Returns:
            list: A list of all issues matching the query.
        """
        return self.youtrack_api.get_issue_from_query(query, fields)

