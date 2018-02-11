from difflib import SequenceMatcher

import falcon
from github import Github

REPO_NAME = "-"
SIMILIAR_THRESHOLD = 0.7
GITUSERNAME = "-"
GITPASSWORD = "-"


class LogResource(object):
    def on_post(self, req, resp):
        identifier = req.get_param('identifier', required=True)
        stacktrace = req.get_param('stacktrace', required=True)
        git = Github(GITUSERNAME, GITPASSWORD)
        repo = git.get_repo(REPO_NAME,)
        isposted = False
        for issue in repo.get_issues():
            if SequenceMatcher(None, issue.body, stacktrace).ratio() > 0.7:
                isposted = True
                # this is probably a similiar issue, so attach it as comment
                issue.create_comment(stacktrace)

        if not isposted:
            # create new issue
            repo.create_issue(identifier, body=stacktrace, labels=["Game Error"])
        resp.status = falcon.HTTP_200
        return
