

def extract_custom_field(issue_data, field_name):
    """
    Extract a custom field value from YouTrack issue data.

    Args:
        issue_data (dict): A single YouTrack issue data containing 'customFields' property. Typically returned from /api/issues/<issue_key> endpoint.
        field_name (str): Name of the custom field to extract.

    Returns:
        The value of the custom field, or None if not found.
    """
    for field in issue_data.get('customFields', []):
        if field.get('name') == field_name:
            value = field.get('value')
            if isinstance(value, dict):
                return value.get('name') or 'Unknown'
            return value if value is not None else 'Unknown'
    return 'Unknown'


def extract_linked_issues(issue_data):
    """
    Extract linked issues from YouTrack issue data.

    Args:
        issue_data (dict): A single YouTrack issue data containing 'links' property. Typically returned from /api/issues/<issue_key> endpoint.

    Returns:
        list: A list of issue keys.
    """
    return [
        linked_issue['idReadable']
        for item in issue_data.get('links', [])
        for linked_issue in item.get('issues', [])
        if linked_issue and 'idReadable' in linked_issue
    ]

def extract_project_name(issue_data):
    """
    Extract project name from a single YouTrack issue data.

    Args:
        issue_data (dict): A single YouTrack issue data. Typically returned from /api/issues/<issue_key> endpoint.

    Returns:
        str: The name of the project.
    """
    return issue_data.get('project').get('name')

def generate_issue_link(host, issue_key):
    return f"{host}/issue/{issue_key}"

def generate_comment_link(host, issue_key, comment_id):
    return f"{host}/issue/{issue_key}#comment={comment_id}"