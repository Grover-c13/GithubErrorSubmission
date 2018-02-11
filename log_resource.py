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
        labels = req.get_param('labels', default=None)
        git = Github(GITUSERNAME, GITPASSWORD)
        repo = git.get_repo(REPO_NAME,)
        isposted = False
        for issue in repo.get_issues():
            ratio = SequenceMatcher(None, issue.body, stacktrace).ratio()
            if ratio > 0.7:
                isposted = True
                # this is probably a similiar issue, so attach it as comment
                if ratio != 1:
                    issue.create_comment(stacktrace)
                if labels is not None:
                    [issue.add_to_labels(label) for label in labels.split(",")]


        if not isposted:
            # create new issue
            if labels is not None:
                repo.create_issue(identifier, body=stacktrace, labels=labels.split(","))
            else:
                repo.create_issue(identifier, body=stacktrace)
        resp.status = falcon.HTTP_200
        return
