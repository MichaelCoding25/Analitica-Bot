from datetime import datetime


class MembersInfo:
    """
    A class that collects all info about member and puts it into an object and adds the time the member's
    info was logged.
    :param member_name: Name and discriminator of the member.
    :param member_id: The discord id of the member.
    :param member_status: What is the member's current status? Idle, Online, Offline or DND?
    :param member_activity: What is the member's current activity?
    """

    def __init__(self, member_name, member_id, member_status, member_activity):
        # Below makes sure that all of the arguments are set as a string type (except for the now_time).
        self.member_name = f'{member_name}'
        self.member_id = f'{member_id}'
        self.member_status = f'{member_status}'
        self.member_activity = f'{member_activity}'

        self.now_time = int(datetime.timestamp(datetime.now()))
