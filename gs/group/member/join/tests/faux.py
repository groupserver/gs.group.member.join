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
