
class IssueWrapper(object):
    seen = 0
    needs_update = False
    issue = None
    last_report = None

    def __init__(self, issue):
        self.issue = issue

    def get_stats(self):
        return "== STACKTRACK STATS ==\n Times seen: %s\n Last reported: %s" % (self.seen, self.last_report)