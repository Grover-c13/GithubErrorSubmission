from difflib import SequenceMatcher

import falcon
from github import Github
import time
import datetime
from issue_wrapper import IssueWrapper

REPO_NAME = "-"
SIMILIAR_THRESHOLD = 0.8
GITUSERNAME = "-"
GITPASSWORD = "-"


class LogResource(object):
    issues = None
    last_update = 0

    def __init__(self):
        git = Github(GITUSERNAME, GITPASSWORD)
        repo = git.get_repo(REPO_NAME)
        self.issues = []
        for issue in repo.get_issues():
            issue_wrapper = IssueWrapper(issue)
            for comment in issue.get_comments():
                if "== STACKTRACK STATS ==" in comment.body:
                    lines = comment.body.splitlines()
                    for line in lines:
                        if "Times seen:" in line:
                            issue_wrapper.seen = int(line.replace("Times seen:", "").strip())
                        if "Last reported:" in line:
                            issue_wrapper.last_report = line.replace("Last reported:", "").strip()
            self.issues.append(issue_wrapper)

    def do_update(self):
        self.last_update = time.time()
        for issue in self.issues:
            if issue.needs_update:
                for comment in issue.issue.get_comments():
                    if "== STACKTRACK STATS ==" in comment.body:
                        comment.edit(issue.get_stats())

    def on_post(self, req, resp):
        identifier = req.get_param('identifier', required=True)
        stacktrace = req.get_param('stacktrace', required=True)
        labels = req.get_param('labels', default=None)
        isposted = False
        for issue in self.issues:
            ratio = SequenceMatcher(None, issue.issue.body, stacktrace).ratio()

            if ratio > SIMILIAR_THRESHOLD:
                isposted = True
                issue.seen += 1
                issue.last_report = datetime.datetime.now()
                issue.needs_update = True
                if labels is not None:
                    [issue.issue.add_to_labels(label) for label in labels.split(",")]

        if not isposted:
            git = Github(GITUSERNAME, GITPASSWORD)
            repo = git.get_repo(REPO_NAME)
            # create new issue
            if labels is not None:
                issue = IssueWrapper(repo.create_issue(identifier, body="```cs\n" + stacktrace + "\n```", labels=labels.split(",")))
                issue.seen = 1
                issue.last_report = datetime.datetime.now()
                issue.issue.create_comment(issue.get_stats())
            else:
                issue = IssueWrapper(repo.create_issue(identifier, body="```cs\n" + stacktrace + "\n```"))
                issue.seen = 1
                issue.last_report = datetime.datetime.now()
                issue.issue.create_comment(issue.get_stats())
            self.issues.append(issue)
        resp.status = falcon.HTTP_200

        # if its been an hour since the last update, do an update
        if time.time()-self.last_update > 3600:
            print("Doing github update " + str(time.time()) + " - " + str(self.last_update) + " = "  + str(time.time()-self.last_update))
            self.do_update()

        return
