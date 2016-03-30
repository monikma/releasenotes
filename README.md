# releasenotes

This script is for outputting the release notes based on JIRA for copy-pasting.

# Requirements

You need to install https://pypi.python.org/pypi/jira first. Tested for Python 3.4.3 (won't work for Python 2.x).

# Quick start

Put this file in your git repository root directory and add to global gitignore. Run it. 
Pay attention that it picks up the right tag, if not, play with the release argument (--help displays usage info).

# Configuration

Default configuration can be changed in release_notes.py below initial description block.


# Examples

## Example usage:

```
# help
./release_notes.py --help
# long format
./release_notes.py --releases 2 --output markdown
./release_notes.py --releases 1 --output html
./release_notes.py --releases 2 --output markdown
# short format
./release_notes.py -r 1 -o html
# using default settings
./release_notes.py
```

## Example output:

```
./release_notes.py --releases 2 --output markdown

[INFO] Looking for commits since 1 last tags
[INFO] Extracting commits since tag: 4.5.0, since timestamp: 2015-11-05 13:14:46 +0100.
[INFO] Filtering STA-[0-9]+ issues
[INFO] Connecting to JIRA to retrieve the issue titles.
Enter your JIRA username (Enter to skip): monika.machunik@hybris.com
Enter your JIRA password (will be transferred insecurely):
Printing release notes:

 ### Sub-tasks
  - STA-2222 - Throw inside finally (Spot check)

 ### User stories
  - STA-2224 - Fortify findings for Servcie SDK - Compulsory

 ### Tasks
  - STA-2225 - Update Dependencies for service sdk and services

 ### Bugs
 - STA-2228 - raml-rewriter: rewrite of baseUri / fails
```