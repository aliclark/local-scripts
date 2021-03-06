#!/usr/bin/python

import string

import os
import stat

import sys

import urllib
import urllib2
from cookielib import LWPCookieJar

import time
import tempfile
import hashlib

import webbrowser

from xml.dom.minidom import parseString
from HTMLParser import HTMLParser


# Todo
# ----
# > Fix login sessions and login redirects
# > Support for multiple fixVersions
# > Fix login checking
# > Local "not modified" cacheing
# > Error handling
# > Programmatically determine fixVersion, filter and project IDs from name
#   - failing that, allow user to input the ID manually, ie.
#     jirate set spa 10140


jiratePath       = os.path.expanduser('~/.jirate')
jirateCookiePath = jiratePath + '/cookies.txt'
jirateTmpPath    = os.path.expanduser('~/.jirate/tmp/')
jirateCachePath  = os.path.expanduser('~/.jirate/cache/')


# TODO: programmatically determine these values
#
# Go to http://jira/secure/BrowseProjects.jspa
# key is on URL http://jira/browse/SPA
# Go to http://jira/browse/SPA
# Project ID is hidden in parts of the source as "pid=10140"
#
projectIds = {
    'SkyPlayer Apps': '10140'
}

# TODO: programmatically determine these values
#
# to get a fixversion.
# on the project look up <project key="SPA">
# download page http://jira/browse/SPA#selectedTab=com.atlassian.jira.plugin.system.project%3Aversions-panel
# for each <fixVersion>crow</fixVersion>
# the url will be: http://jira/browse/SPA/fixforversion/10926
#
versionIds = {
    'SPA': {
        'jade': '10954'
        }
    }

# TODO: programmatically determine these values
#
# go to http://jira/secure/ManageFilters.jspa?filterView=search, searching the filter name 'spa'
# find one with that title, the link is http://jira/secure/IssueNavigator.jspa?mode=hide&requestId=10828
#
filterIds  = {
    'created':   '10830',
    'approving': '10826',
    'active':    '10827',
    'spa':       '10828'
}

# Temprorary
projectKeys = {
    'jade': 'SPA'
}


# http://jira/plugins/servlet/streams?key=10140&os_authType=basic
# http://jira/plugins/servlet/streams?filterUser=USERNAME&os_authType=basic

# jirate activity project myproj     10
# jirate activity user    john.smith 10



envExamples = {
    'JIRATE_HOST': 'http://jira',
    'JIRATE_USER': 'john.smith',
    'JIRATE_PASS': 'hunter2'
    }

loginPage         = '/login.jsp'
commentAssignPage = '/secure/CommentAssignIssue.jspa'

approveAction    = '161'
disapproveAction = '171'

fixedResolution = '1'

httpOpener = None
cookieJar  = None

jiraPath = None
jiraUser = None
jiraPass = None

loggedIn = False


### Library code

def pad(s, n):
    rv = s
    while len(rv) < n:
        rv += ' '
    return rv

def lookor(h, k, v):
    try:
        return h[k]
    except:
        return v

def fail(m):
    print m
    sys.exit(1)


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def tidyData(x):
    return strip_tags(string.replace(x, '<br/>\n', '')) #.trim()


# Adding contraints and unwrapping of data lists

def checkCount(minN=None, maxN=None):
    def checker(x, s='value'):
        l = len(x)

        if minN != None and l < minN:
            fail(s + ': has ' + l + ' items, should have minimum ' + minN)

        if maxN != None and l > maxN:
            fail(s + ': has ' + l + ' items, should have maximum ' + maxN)

        if maxN in [0, 1]:
            if l == 0:
                return None
            return x[0]

        return x

    return checker

zero      = checkCount(0, 0)
optional  = checkCount(0, 1)
one       = checkCount(1, 1)
oneToMany = checkCount(1)


def removeEmpties(l):
    return filter(lambda x: x != '', l)


# Adapted from http://developer.yahoo.com/python/python-caching.html
def cachePath(url):
    m = hashlib.sha1()
    m.update(url)
    filename = m.hexdigest()
    return os.path.join(jirateCachePath, filename)

# Adapted from http://developer.yahoo.com/python/python-caching.html
# Note: jirateCacheDir will slowly fill up over time.
#       possibly make a 'jirate clearcache' command if this becomes an issue
def cacheGet(url, max_age=5):
    filepath = cachePath(url)

    if os.path.exists(filepath):
        if int(time.time()) - os.path.getmtime(filepath) < max_age:
            return open(filepath).read()
    return None

# Adapted from http://developer.yahoo.com/python/python-caching.html
def cacheSet(url, data):
    filepath = cachePath(url)
    fd, temppath = tempfile.mkstemp(dir=jirateTmpPath)
    fp = os.fdopen(fd, 'w')
    fp.write(data)
    fp.close()
    os.rename(temppath, filepath)


### Low level procedures to GET and POST data

def doLogin(continuePage=None):
    values = {
        'os_username': jiraUser,
        'os_password': jiraPass,
        'os_cookie':   'true'
        }

    if continuePage != None:
        values['os_destination'] = continuePage

    data = urllib.urlencode(values)

    cookieJar.load()
    response = httpOpener.open(jiraPath + loginPage, data)
    cookieJar.save()

    return response

def loginQueryStr():
    return 'os_username=' + urllib.quote(jiraUser, '') + '&os_password=' + urllib.quote(jiraPass, '')

def doPost(page, data):
    global loggedIn

#    if not loggedIn:
#        loggedIn = True
#        doLogin() # did it actually work?

    if data != '':
        data += '&'
    data += loginQueryStr()

    cookieJar.load()
    response = httpOpener.open(jiraPath + page, data)
    cookieJar.save()

    return response.read()

def doPostVoid(page, data): doPost(page, data)

def doPostValues(page, values):
    data = urllib.urlencode(values)
    return doPost(page, data)

def getPage(page):
    global loggedIn
    url = jiraPath + page

    cdata = cacheGet(url)
    if cdata != None:
        return cdata

    if string.find(url, '?') == -1:
        url += '?'
    else:
        url += '&'
    url += loginQueryStr()

    cookieJar.load()
    response = httpOpener.open(url)
    cookieJar.save()

    if response.info().getsubtype() != 'xml':

        # response = doLogin(page)

        if False and response.info().getsubtype() != 'xml':
            fail('Login for page failed: ' + page)
        else:
            loggedIn = True
            cdata = response.read()
            cacheSet(url, cdata)
    else:
        cdata = response.read()

    return cdata


### Higher level data getters

def getIssueXml(j):
    qj = urllib.quote(j, '')
    return getPage("/si/jira.issueviews:issue-xml/" + qj + "/" + qj + ".xml")

def getFilterXml(j, n=1000):
    if not j in filterIds:
        fail('Could not find filter ID')
    idnv = filterIds[j]
    idn = urllib.quote(idnv, '')
    n = int(n)
    return getPage("/sr/jira.issueviews:searchrequest-xml/" + idn + "/SearchRequest-" + idn + ".xml?tempMax=" + str(n))

def getQueryXml(q, n=1000):
    n = int(n)
    qq = urllib.quote(q, '')
    return getPage("/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=" + qq + "&tempMax=" + str(n))


### Low level data item extraction

def xmlDocItems(doc):
    return doc.getElementsByTagName('item')

def xmlItems(s):
    return xmlDocItems(parseString(s))

def getIssueDocItem(j):
    return one(xmlItems(getIssueXml(j)))


### Higher level data item extraction

def dataItems(item, tag, attr=None):
    rv = []
    nodes = item.getElementsByTagName(tag)
    node = None
    chNode = None
    value = ''

    for i in range(len(nodes)):
        node = nodes[i]
        if attr != None:
            rv.append(node.getAttribute(attr))
        else:
            if len(node.childNodes) == 0:
                continue

            if len(node.childNodes) != 1:
                fail(tag + ' has too many childNodes')

            chNode = node.childNodes[0]

            if chNode.nodeType != chNode.TEXT_NODE:
                fail(tag + ' child is not a text node')

            value = tidyData(chNode.data)

            if value != '':
                rv.append(value)

    return rv

def getDocItemKeyId(i):
    return one(dataItems(i, 'key', 'id'))


### Converting data item values to fancy string representations

def dataLines(item, k, n=0, useTabs=False):

    def dataLine(l):
        if useTabs:
            t = '\t'
        else:
            t = ' '
        return pad(k + ':', n + 1)  + t + l

    datas = dataItems(item, k)
    return '\n'.join(map(dataLine, datas))

def issueTagLine(item, fullp):
    outer = []
    tags = [ 'key', 'type', 'priority', 'status' ]

    if fullp:
        tags.append('resolution')

    if fullp:
        joins = ' '
    else:
        joins = '\t'

    def tagVal(t): return optional(dataItems(item, t))
    def tagStr(t):
        if fullp:
            return '[' + t + ']'
        return pad('[' + t + ']', maxn + 2)

    innerVals = map(tagVal, tags)
    innerValsLeft = removeEmpties(innerVals)
    maxn = max(map(len, innerValsLeft))

    outer.append(joins.join(map(tagStr, innerValsLeft)))

    summary = optional(dataItems(item, 'summary'))
    if summary != None:
        outer.append(summary)

    return '\t'.join(outer)

def issueSmallTagLine(item):
    return issueTagLine(item, False)

def issueFullTagLine(item):
    return issueTagLine(item, True)

def issueOneLinerFields(item):
    lines = [
        'component',
        'due',
        'version',  'fixVersion',
        'reporter', 'assignee',
        'created',  'updated',
        'environment'
        ]
    maxn = max(map(len, lines))

    def getLines(li):
        return dataLines(item, li, maxn)

    vals = map(getLines, lines)
    valsLeft = removeEmpties(vals)

    return '\n'.join(valsLeft)

def issueDescriptionPart(item):
    tag = 'description'
    tmp = optional(dataItems(item, tag))

    if tmp == None:
        return ''

    return tag + ':\n' + tmp

def issueCommentsPart(item):
    tag = 'comment'
    comments = item.getElementsByTagName(tag)

    def getComment(comment):
        return ('[' + tag + ' author: "' + comment.getAttribute('author') + '", created: "' + comment.getAttribute('created') + '"]\n' +
                tidyData(comment.childNodes[0].data))

    return '\n\n'.join(map(getComment, comments))


### Full page outputs of fancy data strings

def getIssueEssentials(j):
    item = getIssueDocItem(j)
    s = None
    getters = [issueFullTagLine, issueOneLinerFields, issueDescriptionPart, issueCommentsPart]
    parts = map(lambda f: f(item), getters)
    partsLeft = removeEmpties(parts)

    if len(partsLeft) == 0:
        return ''

    s = '\n\n'.join(partsLeft)
    return '\n' + s + '\n'

def getFilterEssential(j, n=None):
    if n != None:
        xml = getFilterXml(j, n)
    else:
        xml = getFilterXml(j)

    items = xmlItems(xml)
    return '\n'.join(map(issueSmallTagLine, items))

def getQueryEssential(q, n=None):
    if n != None:
        xml = getQueryXml(q, n)
    else:
        xml = getQueryXml(q)

    items = xmlItems(xml)
    return '\n'.join(map(issueSmallTagLine, items))


### Post actions

def getFixVersionId(f):

    key = projectKeys[f]

    v1 = lookor(versionIds, key, None)
    if v1 == None:
        fail('Unknown fixVersion projectKey' + key + ' - please insert the id in the versionIds table')

    v2 = lookor(v1, f, None)
    if v2 == None:
        fail('Unknown fixVersion ' + f + ' - please insert the id in the versionIds table')

    return v2

def issueApproved(j, comment=''):

    item    = getIssueDocItem(j)
    fixVs   = dataItems(item, 'fixVersion')
    fixVids = map(getFixVersionId, fixVs)

    # TODO: find out correct post format for 0 or multiple fixVersions
    if len(fixVids) != 1:
        fail('FIXME: script currently doesn\'t know what to do when number of fixVersions is not 1.\n' +
             'please fix the code and submit it to maintainer')

    values = {
        'resolution':   fixedResolution,
        'fixVersions':  ','.join(fixVids),   # is this correct?
        'assignee':     jiraUser,
        'comment':      comment,
        'commentLevel': '',
        'action':       approveAction,
        'id':           getDocItemKeyId(item),
        'viewIssueKey': '',
        'Approved':     'Approved'
        }

    doPostValues(commentAssignPage, values)

def issueDisapproved(j, comment=''):

    item = getIssueDocItem(j)

    # need to fix assignee
    assignee = ''

    print 'todo'
    return

    values = {
        'assignee':     assignee,
        'comment':      comment,
        'commentLevel': '',
        'action':       disapproveAction,
        'id':           getDocItemKeyId(item),
        'viewIssueKey': '',
        'Disapproved':  'Disapproved'
        }

    doPostValues(commentAssignPage, values)


### web

def doWebCreate():
    webbrowser.open(jiraPath + '/secure/CreateIssue!default.jspa')


### Help text creation

def commandExample(c):
    if c == None:
        return '\n'
    if c[1] == '':
        return c[0] + '\n'
    return c[0] + '\n\n\t' + c[1] + '\n\n'

def getHelpText(problem):

    commands = [
        ('jirate get $url',
         'Ensures login, then does a GET request to the page,\n'
         '\teg. jirate get /si/jira.issueviews:issue-xml/JOB-101/JOB-101.xml'),
        None,
        ('jirate queryxml  $query [$n]',
         'Print the RSS feed for query, limiting to $n entries. $n defaults to 1000'),
        ('jirate query     $query [$n]',
         'Print a simple data output for each item in the query, limiting to $n entries. $n defaults to 1000'),
        None,
        ('jirate filterxml $filter [$n]',
         'Print the RSS feed for filter, limiting to $n entries. $n defaults to 1000'),
        ('jirate filter    $filter [$n]',
         'Print a simple data output for each item in the filter, limiting to $n entries. $n defaults to 1000'),
        None,
        ('jirate issuexml  $issue',
         'Prints the RSS XML for the issue. This is an alias for "jirate get /si/jira.issueviews:issue-xml/${issue}/${issue}.xml"'),
        ('jirate issue     $issue',
         'Prints a simple data output for the issue'),
        None,
        ('jirate post $url $postdata',
         'Ensures login, then does a POST request to the page,\n'
         '\teg. jirate post /secure/CommentAssignIssue.jspa assignee=john.smith&Disapproved=Disapproved& ...and so on...'),
        None,
        ('jirate webcreate',
         'Opens the URL for creating issues in a web browser'),
        None,
        ('jirate approve     $issue [$comment]',
         'Approve the issue, optionally supplying a comment')
        ]
    commandsTodo = [
        ('jirate investigate $issue [$comment]', ''),
        ('jirate investigatd $issue [$comment]', ''),
        ('jirate implement   $issue [$comment]', ''),
        ('jirate implemented $issue [$comment]', ''),
        ('jirate disapprove  $issue [$comment]', ''),
        None,
        ('jirate comment $issue $comment', ''),
        ('jirate attach  $issue ($filepath | $url) [$comment]', ''),
        None,
        ('jirate create $project (opens editor for editing an "issue spec")', ''),
        None,
        ('jirate fields $issue',
         'List all of the element tag names that an issue has, one per line, with duplicates if an element occurs multiple times'),
        ('jirate values $issue $field',
         'Print the values of all elements in the issue with name $field. One per line, possibly including blank lines. If the value contains a new line, it is replaced with the text "\\n" (minus quotes), other backslash chars become "\\\\"'),
        ('jirate update $issue $field $value', '')
        ]

    problemStr = ''
    if problem != None:
        problemStr = '\nProblem: ' + problem + '\n'

    return (problemStr + '\n\tjirate help\n\n'
            'jirate is a command-line tool to interface with JIRA.\n'
            'It is not intended to cover all uses of JIRA, but to perform common tasks simply and efficiently.\n'
            'Therefore this script will not completely replace your current method of using JIRA,\n'
            'but should reduce it to sane levels of usage.\n'
            'For a more complete JIRA command line tool, try the JIRA Command Line Interface.\n\n'
            'USAGE:\n\n' +
            ''.join(map(commandExample, commands)) + 
            '\nTODO:\n\n' +
            ''.join(map(commandExample, commandsTodo)) +
            problemStr)


### Turn the arguments into some kind of data request / post

def getOutput():
    rv = ''
    problem = None
    action  = lookor(sys.argv, 1, None)
    argMins = {
        'get':        (1, getPage),
        'queryxml':   (1, getQueryXml),
        'query':      (1, getQueryEssential),
        'filterxml':  (1, getFilterXml),
        'filter':     (1, getFilterEssential),
        'issuexml':   (1, getIssueXml),
        'issue':      (1, getIssueEssentials),
        'post':       (2, doPostVoid),
        'webcreate':  (0, doWebCreate),
        'disapprove': (1, issueDisapproved),
        'approve':    (1, issueApproved)
        }

    if action == None:
        action = 'help'
        problem = 'Please supply an action to perform'

    def enoughArgs(action):
        if (len(sys.argv) - 2) < argMins[action][0]:
            return False
        return True

    if (action in argMins) and not enoughArgs(action):
        problem = ('Not enough args supplied for action "' + action +
                   '" (you supplied ' + str(len(sys.argv) - 2) + ' but it needs ' + str(argMins[action][0]) + ')')
        action  = 'help'

    if action == 'help':
        return getHelpText(problem)

    if action in argMins:
        rv = argMins[action][1](*sys.argv[2:])
        if rv == None:
            rv = ''
        return rv
    else:
        problem = 'Unknown command "' + action + '"'
        return getHelpText(problem)

    return rv


### Set up global variables for config items host, user, and pass

def envVarNotPresent(v):
    return not v in os.environ

def setupVars():
    global jiraPath, jiraUser, jiraPass

    def makeExample(x):
        return 'eg. ' + x + '=' + envExamples[x]

    needed = ['JIRATE_HOST', 'JIRATE_USER', 'JIRATE_PASS']

    notFound = filter(envVarNotPresent, needed)

    if len(notFound) != 0:
        fail('Required environment variables not set: ' + ', '.join(notFound) +
             '\n' + '\n'.join(map(makeExample, notFound)))

    jiraPath = os.environ[needed[0]]
    jiraUser = os.environ[needed[1]]
    jiraPass = os.environ[needed[2]]


### Setup up the cookie file

def setupDirs():
    if not os.path.isdir(jiratePath):
        os.mkdir(jiratePath, 0700)

    if not os.path.isfile(jirateCookiePath):
        open(jirateCookiePath, 'w').close()
    os.chmod(jirateCookiePath, stat.S_IREAD | stat.S_IWRITE)

    if not os.path.isdir(jirateCachePath):
        os.mkdir(jirateCachePath, 0700)

    if not os.path.isdir(jirateTmpPath):
        os.mkdir(jirateTmpPath, 0700)

def setupCookieJar():
    global httpOpener, cookieJar
    cookieJar = LWPCookieJar(jirateCookiePath)
    cookieJar.save()
    httpOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))

def main():
    setupVars()
    setupDirs()
    setupCookieJar()

    text = getOutput()

    if text != '':
        print text

if __name__ == "__main__":
    main()
