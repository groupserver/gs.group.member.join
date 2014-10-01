from email.parser import Parser
from gs.group.list.command.tests.faux import FauxGroup  # lint:ok


class FauxSiteInfo(object):
    name = 'An Example Site'
    id = 'example'


class FauxGroupInfo(object):
    name = 'An Example Group'
    id = 'example_group'
    url = 'https://lists.example.com/groups/example_group'
    siteInfo = FauxSiteInfo()
    groupObj = 'This is not a folder'


class FauxUserInfo(object):
    name = 'An Example user'
    id = 'exampleuser'


class FauxVisibility(object):
    groupInfo = FauxGroupInfo()


def faux_email(subject='join'):
    retval = Parser().parsestr(
        'From: <member@example.com>\n'
        'To: <group@example.com>\n'
        'Subject: {0}\n'
        '\n'
        'Body would go here\n'.format(subject))
    return retval