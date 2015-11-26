import subprocess
import os
import sys
import re
import getpass
from jira import JIRA

######################################################################################################
# This script is for outputting the release notes for copy-pasting.
#
# You need to install https://pypi.python.org/pypi/jira first. Tested for Python 3.4.3 (won't work for Python 2.x).
#
# Put this file in your git repository root directory and add to global gitignore. Run it. 
# Pay attention that it picks up the right tag, if not, play with the tagsBack argument (--help displays usage info).
#
# Example output:
#
# [INFO] Looking for commits since 1 last tags
# [INFO] Extracting commits since tag: 4.5.0, since timestamp: 2015-11-05 13:14:46 +0100.
# [INFO] Filtering STA-[0-9]+ issues
# [INFO] Connecting to JIRA to retrieve the issue titles.
# Enter your JIRA username (Enter to skip): monika.machunik@hybris.com
# Enter your JIRA password (will be transferred insecurely):
# Printing release notes:
#
# ### Sub-tasks
#  - STA-2222 - Throw inside finally (Spot check)
#
# ### User stories
#  - STA-2224 - Fortify findings for Servcie SDK - Compulsory
#
# ### Tasks
#  - STA-2225 - Update Dependencies for service sdk and services
#
# ### Bugs
# - STA-2228 - raml-rewriter: rewrite of baseUri / fails
#
######################################################################################################

def log(str):
  print("[INFO] " + str)

# executes given Git command in the current directory (do not include "git" in the front)
def executeGit(command): 
  pr = subprocess.Popen("git "+command, cwd = '.' , shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
  (out, error) = pr.communicate()
  if not error:
    return str(out)
  else:
    return str(error)

# returns the tag name of the tag tagsBack tags back
def getTagnameTagsBack(tagsBack):
  tagInfo = executeGit("log --tags --simplify-by-decoration --pretty=\"format:%ai %d\" -n " + tagsBack)
  taginfologs = re.findall('\(tag\:(.+?)[,\)]', tagInfo)
  taginfolog = taginfologs[len(taginfologs)-1]
  return taginfolog;
  
# returns the timestamp of the tag tagsBack tags back
def getTimestampTagsBack(tagsBack):
  tagInfo = executeGit("log --tags --simplify-by-decoration --pretty=\"format:%ai %d\" -n " + tagsBack)
  timestamps = re.findall('[0-9-:]+ [0-9-:]+ [0-9-:+]+', tagInfo)
  timestamp = timestamps[len(timestamps)-1]
  taginfologs = re.findall('\(tag\:(.+?)[,\)]', tagInfo)
  taginfolog = taginfologs[len(taginfologs)-1]  
  return timestamp;
  
# returns all commit messages since given timestamp, as one string
def getCommitsSince(timestamp):
  return executeGit("log --pretty=\"%s\r%n\" --since=\""+timestamp+"\"")
  
# authenticates the user in JIRA and returns the Jira object
def authenticateInJira():
  user = input('Enter your JIRA username (Enter to skip): ')
  if len(user)==0:
    return None
  password = getpass.getpass('Enter your JIRA password (will be transferred insecurely): ')
  return JIRA(basic_auth=(user, password), options={'server':'https://jira.hybris.com'})

#### main program:

if len(sys.argv)>1:
  if sys.argv[1] == '--help':
    print("")
    print("usage: releasenotes* [number_of_releases_back]")
    print("")
    print("Options:")
    print("  number_of_releases_back: How many releases back should be considered. This is determined by number of tags in the master branch. Default value is 1 (since last release).")
    print("")
    print("  *)the script must be started in the directory of your git repository")
    print("")
    sys.exit(0)
  else:
    tagsBack = sys.argv[1]
else:
  tagsBack = "1"

log("Looking for commits since " + tagsBack + " last tags")
timestamp = getTimestampTagsBack(tagsBack)
tagname = getTagnameTagsBack(tagsBack)

log("Extracting commits since tag:" + tagname + ", since timestamp: " + timestamp +".")
commitMessages = getCommitsSince(timestamp)

log("Filtering STA-[0-9]+ issues")
issues = set(re.findall("[sS][Tt][Aa]-[0-9]+",commitMessages))

log("Connecting to JIRA to retrieve the issue titles.")
jira = authenticateInJira()

issueMap = {}

for issue in issues:
  if jira != None:
    type = jira.issue(issue).fields.issuetype.name
  else:
    type = "Unknown"
  if not type in issueMap.keys():
    issueMap[type] = []
  issueMap[type].append(issue)

print("Printing release notes:")
  
for type in issueMap.keys():
  print()
  if type=="User story":
    print("### User stories")
  else:
    print("### " + type + "s")
  for issue in issueMap[type]:
    if jira != None:
      print(" - " + issue.upper() + " - " + jira.issue(issue).fields.summary)
    else:
      print(" - " + issue.upper() + " - " + "https://jira.hybris.com/browse/" + issue)

sys.exit(0)