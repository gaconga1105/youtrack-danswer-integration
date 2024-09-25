import argparse
import logging
from pathlib import Path

import yaml

from integration import YouTrackDanswerIntegration


def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)


def setup_logging(logger_name: str, config: dict) -> logging.Logger:
    """Set up and return a configured logger."""
    if not config:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename='youtrack_danswer_integration.log'
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format=config['logging']['logging_format'],
            datefmt=config['logging']['logging_date_format'],
            filename=config['logging']['logging_file_name']
        )
    return logging.getLogger(logger_name)


def main():
    parser = argparse.ArgumentParser(description='YouTrack | Danswer Integration')
    parser.add_argument('--youtrack-url', required=True, help='YouTrack base URL')
    parser.add_argument('--youtrack-token', required=True, help='YouTrack API token')
    parser.add_argument('--danswer-url', help='Danswer base URL')
    parser.add_argument('--danswer-key', help='Danswer API key')
    parser.add_argument('--start-date', required=True, help='Start date for YouTrack issue query (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date for YouTrack issue query (YYYY-MM-DD)')
    parser.add_argument('--mode', choices=['api', 'file'], default='file', help='Operation mode: api or file')
    parser.add_argument('--output-path', help='Output path for file mode')
    parser.add_argument('--cc-pair-id', help='The “Connector” ID seen on the Connector Status pages. For example, if running locally, it might be http://localhost:3000/admin/connector/2')

    args = parser.parse_args()

    if args.mode == 'file' and not args.output_path:
        parser.error("--output-path is required when mode is 'file'")

    if args.mode == 'api' and not args.cc_pair_id:
        parser.error("--cc-pair-id is required when mode is 'api'")

    config = load_config('config/config.yaml')
    integration = YouTrackDanswerIntegration(
        youtrack_url=args.youtrack_url,
        youtrack_token=args.youtrack_token,
        danswer_url=args.danswer_url,
        danswer_key=args.danswer_key,
        cc_pair_id=int(args.cc_pair_id) if args.cc_pair_id else None,
        config=config,
        logger=logger
    )

    if not integration.youtrack_api.is_active():
        logger.error('YouTrack API has not been loaded correctly')
        exit(1)
    else:
        logger.info(f'YouTrack API loaded: {integration.youtrack_api.get_info()}')

    if integration.danswer_api:
        if not integration.danswer_api.is_active():
            logger.error('Danswer API has not been loaded correctly')
            exit(1)
        else:
            logger.info(f'Danswer API loaded: {integration.danswer_api.get_info()}')

    logger.info(f'Querying YouTrack for issues from {args.start_date} to {args.end_date}')
    issues_data = integration.fetch_all_youtrack_issues(
        query=template['youtrack_queries']['indexing_issues'].format(
            start_date=args.start_date,
            end_date=args.end_date
        ),
        fields=template['youtrack_fields']['default']
    )

    if args.mode == 'api':
        integration.youtrack_to_danswer_api(
            issues_data=issues_data
        )
    elif args.mode == 'file':
        integration.youtrack_to_danswer_file(
            issues_data=issues_data,
            save_path=Path(args.output_path).expanduser().resolve()
        )


template = load_config(Path(__file__).parent.parent / 'config' / 'queries.yaml')
config = load_config(Path(__file__).parent.parent / 'config' / 'config.yaml')
logger = setup_logging('youtrack_danswer_integration', config)

if __name__ == "__main__":
    main()
