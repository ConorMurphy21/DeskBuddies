from cmnSys.action import Action
from client.clientConfig import ClientConfig
from cmnSys.responseCode import ResponseCode
from cmnUtils import configManager
from cmnSys import directoryFinder
from networking import tcpClient
from networking.packets import packet as pct
from networking.packets.packet import Packet


def main(args):
    settings = ClientConfig(directoryFinder.client_config_file())
    if args.action == Action.CONFIG:
        _config(settings)
        return

    if settings['host'] == '' or settings['uid'] == '':
        _required_config(settings)
    _ask_server(vars(args), settings)


def _required_config(settings):
    print("It looks like this is your first time using it. For now we will just configure some essentials, but you can"
          " use the config flag to customize further.")
    host = input("Please enter the hostname or ip of your DeskBuddies server: ")
    uid = input("Please enter your user id: ")
    settings['host'] = host
    settings['uid'] = uid
    settings.write()


def _config(settings):
    configManager.user_config_interface(settings)
    settings.write()


def _ask_server(args, settings):
    # just in case any required info for the packet creation is configured (like uid)
    args = {**args, **settings.data}
    packet = pct.from_args(args)
    response = tcpClient.send_packet(packet, settings['host'], settings['port'])
    print(response.encode().decode('utf-8'))
    print(_parse_response(response))


def _add_response(response: Packet) -> str:
    data = response.data
    code = ResponseCode(data['responseCode'])
    if code == ResponseCode.OK:
        return "Successfully added you to the schedule!"
    elif code == ResponseCode.CONFLICT:
        return "Can't work on the same day as " + ', '.join(data['results'])
    elif code == ResponseCode.UNEXPECTED:
        return "You are already scheduled to work this day."
    elif code == ResponseCode.NOT_FOUND:
        return "There is no user id with the uid: " + data['results'][0] + ". Please contact your administrator."
    elif code == ResponseCode.FORBIDDEN:
        return "Something has gone terribly wrong."


def _remove_response(response: Packet) -> str:
    data = response.data
    code = ResponseCode(data['responseCode'])
    if code == ResponseCode.OK:
        return "Successfully removed you from the schedule!"
    elif code == ResponseCode.NOT_FOUND:
        return "You are not scheduled for this day and therefore do not need to be removed"
    elif code == ResponseCode.UNEXPECTED:
        return "Unsuccessfully removed you from the schedule."
    elif code == ResponseCode.NOT_FOUND:
        return "There is no user id with the uid: " + data['results'][0] + ". Please contact your administrator."
    elif code == ResponseCode.FORBIDDEN:
        return "Something has gone terribly wrong."


def _get_response(response: Packet) -> str:
    data = response.data
    code = ResponseCode(data['responseCode'])
    if code == ResponseCode.OK:
        return "Successfully got uids from the schedule:" + ", ".join(data['results'])
    elif code == ResponseCode.UNEXPECTED:
        return "Unsuccessfully got uids from the schedule!"
    elif code == ResponseCode.FORBIDDEN:
        return "Something has gone terribly wrong."


def _parse_response(response: Packet) -> str:
    funcs = {Action.GET: _get_response,
             Action.QUERY: _add_response,
             Action.REMOVE: _remove_response}
    return funcs[response.action](response)
