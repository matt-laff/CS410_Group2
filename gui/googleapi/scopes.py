"""
    contains a list of scopes required for any googleapi endpoint.
    This should later be separated into varying scopes for each
    operation that is required. for the time being the four scopes
    listed allows for each of the primary endpoints:
    - users().draft
    - users().messages.list
    - users().messages.get
    - users.messages.send
"""
scopes = [
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose'
]
