#!/usr/bin/python

import subprocess
import os
import sys
import re
import getpass
import getopt
from jira import JIRA

######################################################################################################
# This script is for outputting the release notes for copy-pasting.
#
# https://github.com/monami555/releasenotes
#
# You need to install https://pypi.python.org/pypi/jira first. Tested for Python 3.5.1 and Python 2.7.11.
#
# Put this file in your git repository root directory and add to global `.gitignore` if you don't
# want to commit it. Run it.
#
# Pay attention that it picks up the right tag, if not, play with the `tags` argument (--help
# displays usage info).
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
#  - [STA-2222](https://jira.hybris.com/browse/STA-2222) - Throw inside finally (Spot check)
#
# ### User stories
#  - [STA-2224](https://jira.hybris.com/browse/STA-2224) - Fortify findings for Servcie SDK - Compulsory
#
# ### Tasks
#  - [STA-2225](https://jira.hybris.com/browse/STA-2225) - Update Dependencies for service sdk and services
#
# ### Bugs
# - [STA-2228](https://jira.hybris.com/browse/STA-2228) - raml-rewriter: rewrite of baseUri / fails
#
######################################################################################################

#### Check python version:
try:
  raw_input
except: #if it is Python 3.x
  input = input;
else:  #if it is Python 2.x
  input = raw_input;

#### General Settings
defaultTagsBack = 1;
defaultOutputType = "markdown" # markdown or html
jiraServer = "https://jira.hybris.com" # full url to jira
issuePrefixRegex = "[Ss][Tt][Aa]-"; # jira group prefix as regex
gitMode = "ref" # ref or log. use log if you experience errors in tag selection

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
def getTagnameAndTimeStampTagsBack(tagsBack):

  if gitMode == "log":
    ## log approach
    tagInfo = executeGit("log --tags --simplify-by-decoration --pretty=\"format:%ai %d\" -n" + tagsBack)
    taginfologs = re.findall('(v.*)', tagInfo)
  else:
    ## for-each-ref approach
    tagInfo = executeGit("for-each-ref --sort='-*committerdate' --format=\"%(*committerdate:iso) (tag: %(refname:short))\" refs/tags --count=" + str(tagsBack));
    taginfologs = re.findall('\(tag\:(.+?)[,\)]', tagInfo)

  timestamps = re.findall('[0-9-:]+ [0-9-:]+ [0-9-:+]+', tagInfo)
  if (len(timestamps)>0):
    timestamp = timestamps[len(timestamps)-1]
    tagname = taginfologs[len(taginfologs)-1]
    return {
      'tagname': tagname.strip(),
      'timestamp': timestamp
    };
  else:
    print("No tags found in the current project.");
    sys.exit(1);

# returns all commit messages since given timestamp, as one string
def getCommitsSince(timestamp):
  return executeGit("log --pretty=\"%s\r%n\" --since=\""+timestamp+"\"")

# authenticates the user in JIRA and returns the Jira object
def authenticateInJira():
  user = input('Enter your JIRA username (Enter to skip): ')
  if len(user)==0:
    return None
  password = getpass.getpass('Enter your JIRA password (will be transferred insecurely): ')
  return JIRA(basic_auth=(user, password), options={'server': jiraServer})

def usage():
  print("")
  print("Usage: releasenotes* --tags [number_of_tags_back] --output [markdown|html]")
  print("")
  print("Options:")
  print("-t or --tags [number_of_tags_back]: How many tags back should be considered. This is determined by number of tags in repository. Default value is 1 (since last tag).")
  print("-o or --output [type]  markdown or html output style")
  print("")
  print("  *)the script must be started in the directory of your git repository")
  print("")
  sys.exit(0)

def createReleaseNotes(tagsBack, outputType):
  log("Looking for commits since " + str(tagsBack) + " last tags")
  targetTag = getTagnameAndTimeStampTagsBack(tagsBack);

  timestamp = targetTag['timestamp']
  tagname = targetTag['tagname']

  log("Extracting commits since tag: " + tagname + ", since timestamp: " + timestamp +".")
  commitMessages = getCommitsSince(timestamp)

  log("Filtering "+issuePrefixRegex+"[0-9]+ issues")
  issues = set(re.findall(issuePrefixRegex + "[0-9]+",commitMessages))

  # TODO remove case sensitive duplicates from "issues" (case should not matter)

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

  if outputType == "markdown":
    for type in issueMap.keys():
      print("")
      if type=="User story":
        print("### User stories")
      else:
        print("### " + type + "s")
      for issue in issueMap[type]:
        if jira != None:
          print(" - [" + issue.upper() + "](" + jiraServer + "/browse/" + issue + ") - " +
                jira.issue(issue).fields.summary)
        else:
          print(" - [" + issue.upper() + "](" + jiraServer + "/browse/" + issue + ") - " +
                jiraServer + "/browse/" + issue)

  else:
    for type in issueMap.keys():
      print("")
      if type=="User story":
        print("<h2>User stories</h2>")
      else:
        print("<h2>" + type + "s<h2>")

      print("<ul>")
      for issue in issueMap[type]:
        if jira != None:
          print("    <li>[<a href='" + jiraServer + "/browse/" + issue + "'>" + issue.upper() + "</a>] - " + jira.issue(issue).fields.summary + "</li>")
        else:
          print("    <li>[<a href='" + jiraServer + "/browse/" + issue + "'>" + issue + "</a>]</li>")

      print("</ul>")
  sys.exit(0)


#### main program:
def main(argv):
  output = defaultOutputType
  tagsback = defaultTagsBack
  try:
      opts, args = getopt.getopt(argv, "h:t:o", ["help", "tags=", "output="])
  except getopt.GetoptError:
      usage()
      sys.exit(2)
  for opt, arg in opts:
      if opt in ("-h", "--help"):
          usage()
          sys.exit()
      # elif opt == '-d':
      #     global _debug
      #     _debug = 1
      elif opt in ("-t", "--tags"):
          tagsback = arg
      elif opt in ("-o", "--output"):
          output = arg

  # source = "".join(args)
  # print "source", source
  # print "output", output
  # print "tagsback", tagsback
  createReleaseNotes(tagsback, output)


if __name__ == "__main__":
    main(sys.argv[1:])
