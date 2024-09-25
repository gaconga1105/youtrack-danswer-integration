# YouTrack to Danswer Integration

## Usage

This module retrieves issues from YouTrack and sends them to Danswer for indexing.

### Parameters:

Required parameters:
- `--youtrack-url`: The base URL of your YouTrack instance
- `--youtrack-token`: Your YouTrack API token
- `--start-date`: Start date for issue query (format: YYYY-MM-DD)
- `--end-date`: End date for issue query (format: YYYY-MM-DD)
- `--mode`: Operation mode, either 'api' or 'file'

API mode parameters:
- `--danswer-url`: The base URL of your Danswer instance
- `--danswer-key`: Your Danswer API key, found in Danswer dashboard /admin/api-key
- `--cc-pair-id`: The “Connector” ID seen on the Connector Status pages. For example, if running locally, it might be http://localhost:3000/admin/connector/2

FILE mode parameters:
- `--output-path`: Output path for data files
- Using file mode requires manual zipping of data files and uploading to Danswer. See more at https://docs.danswer.dev/connectors/file

### Examples:

1. API mode:
   ```
   python src/main.py --youtrack-url https://youtrack.example.com --youtrack-token abcdef123456 --danswer-url https://danswer.example.com --danswer-key abcdef123456 --cc-pair-id 7 --start-date 2023-01-01 --end-date 2023-12-31 --mode api
   ```

2. File mode:
   ```
   python src/main.py --youtrack-url https://youtrack.example.com --youtrack-token abcdef123456 --start-date 2023-01-01 --end-date 2023-12-31 --mode file --output-path ./data.json
   ```