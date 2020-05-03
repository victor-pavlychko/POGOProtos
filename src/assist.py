#!/usr/bin/env python

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("-m", "--message", help="Message to prodecure files for.")
args = parser.parse_args()


def underscore_to_camelcase(value):
    def camelcase():
        while True:
            yield str.capitalize

    c = camelcase()
    return "".join(c.next()(x) if x else '_' for x in value.split("_"))


if not args.message:
    print("Specify a message.")


def initialize_file(package, message, path):
    with open(path, 'a') as opened_file:
        opened_file.write('syntax = "proto3";\n')
        opened_file.write('package %s;\n\n' % package)
        opened_file.write('message %s {\n' % message)
        opened_file.write('\t// Initialized by assist.py\n')
        opened_file.write('}\n')

    print("Created %s" % path)


message = underscore_to_camelcase(args.message)

# Global
request_path = os.path.join("POGOProtos/Networking/Requests/Messages", "%sMessage.proto" % message)
response_path = os.path.join("POGOProtos/Networking/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Requests.Messages", "%sMessage" % message, request_path)
initialize_file("POGOProtos.Networking.Responses", "%sResponse" % message, response_path)

# Social
social_request_path = 'Social_' +  os.path.join("POGOProtos/Networking/Social/Messages", "%sMessage.proto" % message)
social_response_path = 'Social_' + os.path.join("POGOProtos/Networking/Social/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Social.Messages", "%sMessage" % message, social_request_path)
initialize_file("POGOProtos.Networking.Social.Responses", "%sResponse" % message, social_response_path)

# Platform
platform_request_path = 'Platform_' + os.path.join("POGOProtos/Networking/Platform/Requests", "%sMessage.proto" % message)
platform_response_path = 'Platform_' + os.path.join("POGOProtos/Networking/Platform/Responses", "%sResponse.proto" % message)

# Titan
platform_request_path = 'Titan_' + os.path.join("POGOProtos/Networking/Titan/Messages", "%sMessage.proto" % message)
platform_response_path = 'Titan_' + os.path.join("POGOProtos/Networking/Titan/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Platform.Requests", "%sMessage" % message, platform_request_path)
initialize_file("POGOProtos.Networking.Platform.Responses", "%sResponse" % message, platform_response_path)

# GameAccountRegistry
gameaccountregistry_request_path = 'GameAccountRegistry_' + os.path.join("POGOProtos/Networking/Game/GameAccountRegistry/Messages", "%sMessage.proto" % message)
gameaccountregistry_response_path = 'GameAccountRegistry_' + os.path.join("POGOProtos/Networking/Game/GameAccountRegistry/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GameAccountRegistry.Messages", "%sMessage" % message, gameaccountregistry_request_path)
initialize_file("POGOProtos.Networking.Game.GameAccountRegistry.Responses", "%sResponse" % message, gameaccountregistry_response_path)

# GameAnticheat
gameanticheat_request_path = 'GameAnticheat_' + os.path.join("POGOProtos/Networking/Game/GameAnticheat/Messages", "%sMessage.proto" % message)
gameanticheat_response_path = 'GameAnticheat_' + os.path.join("POGOProtos/Networking/Game/GameAnticheat/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GameAnticheat.Messages", "%sMessage" % message, gameanticheat_request_path)
initialize_file("POGOProtos.Networking.Game.GameAnticheat.Responses", "%sResponse" % message, gameanticheat_response_path)

# GameFitness
gamefitness_request_path = 'GameFitness_' + os.path.join("POGOProtos/Networking/Game/GameFitness/Messages", "%sMessage.proto" % message)
gamefitness_response_path = 'GameFitness_' + os.path.join("POGOProtos/Networking/Game/GameFitness/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GameFitness.Messages", "%sMessage" % message, gamefitness_request_path)
initialize_file("POGOProtos.Networking.Game.GameFitness.Responses", "%sResponse" % message, gamefitness_response_path)

# GameGmTemplates
gamegmtemplates_request_path = 'GameGmTemplates_' + os.path.join("POGOProtos/Networking/Game/GameGmTemplates/Messages", "%sMessage.proto" % message)
gamegmtemplates_response_path = 'GameGmTemplates_' + os.path.join("POGOProtos/Networking/Game/GameGmTemplates/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GameGmTemplates.Messages", "%sMessage" % message, gamegmtemplates_request_path)
initialize_file("POGOProtos.Networking.Game.GameGmTemplates.Responses", "%sResponse" % message, gamegmtemplates_response_path)

# GameIap
gameiap_request_path = 'GameIap_' + os.path.join("POGOProtos/Networking/Game/GameIap/Messages", "%sMessage.proto" % message)
gameiap_response_path = 'GameIap_' + os.path.join("POGOProtos/Networking/Game/GameIap/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GameIap.Messages", "%sMessage" % message, gameiap_request_path)
initialize_file("POGOProtos.Networking.Game.GameIap.Responses", "%sResponse" % message, gameiap_response_path)

# GameLocationAwareness
gamelocationawareness_request_path = 'GameLocationAwareness_' + os.path.join("POGOProtos/Networking/Game/GameLocationAwareness/Messages", "%sMessage.proto" % message)
gamelocationawareness_response_path = 'GameLocationAwareness_' + os.path.join("POGOProtos/Networking/Game/GameLocationAwareness/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GameLocationAwareness.Messages", "%sMessage" % message, gamelocationawareness_request_path)
initialize_file("POGOProtos.Networking.Game.GameLocationAwareness.Responses", "%sResponse" % message, gamelocationawareness_response_path)

# GameNotification
gamenotification_request_path = 'GameNotification_' + os.path.join("POGOProtos/Networking/Game/GameNotification/Messages", "%sMessage.proto" % message)
gamenotification_response_path = 'GameNotification_' + os.path.join("POGOProtos/Networking/Game/GameNotification/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GameNotification.Messages", "%sMessage" % message, gamenotification_request_path)
initialize_file("POGOProtos.Networking.Game.GameNotification.Responses", "%sResponse" % message, gamenotification_response_path)

# GamePasscode
gamepasscode_request_path = 'GamePasscode_' + os.path.join("POGOProtos/Networking/Game/GamePasscode/Messages", "%sMessage.proto" % message)
gamepasscode_response_path = 'GamePasscode_' + os.path.join("POGOProtos/Networking/Game/GamePasscode/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GamePasscode.Messages", "%sMessage" % message, gamepasscode_request_path)
initialize_file("POGOProtos.Networking.Game.GamePasscode.Responses", "%sResponse" % message, gamepasscode_response_path)

# GamePing
gameping_request_path = 'GamePing_' + os.path.join("POGOProtos/Networking/Game/GamePing/Messages", "%sMessage.proto" % message)
gameping_response_path = 'GamePing_' + os.path.join("POGOProtos/Networking/Game/GamePing/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GamePing.Messages", "%sMessage" % message, gameping_request_path)
initialize_file("POGOProtos.Networking.Game.GamePing.Responses", "%sResponse" % message, gameping_response_path)

# GamePlayer
gameplayer_request_path = 'GamePlayer_' + os.path.join("POGOProtos/Networking/Game/GamePlayer/Messages", "%sMessage.proto" % message)
gameplayer_response_path = 'GamePlayer_' + os.path.join("POGOProtos/Networking/Game/GamePlayer/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GamePlayer.Messages", "%sMessage" % message, gameplayer_request_path)
initialize_file("POGOProtos.Networking.Game.GamePlayer.Responses", "%sResponse" % message, gameplayer_response_path)

# GamePoi
gamepoi_request_path = 'GamePoi_' + os.path.join("POGOProtos/Networking/Game/GamePoi/Messages", "%sMessage.proto" % message)
gamepoi_response_path = 'GamePoi_' + os.path.join("POGOProtos/Networking/Game/GamePoi/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GamePoi.Messages", "%sMessage" % message, gamepoi_request_path)
initialize_file("POGOProtos.Networking.Game.GamePoi.Responses", "%sResponse" % message, gamepoi_response_path)

# GamePushNotification
gamepushnotification_request_path = 'GamePushNotification_' + os.path.join("POGOProtos/Networking/Game/GamePushNotification/Messages", "%sMessage.proto" % message)
gamepushnotification_response_path = 'GamePushNotification_' + os.path.join("POGOProtos/Networking/Game/GamePushNotification/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GamePushNotification.Messages", "%sMessage" % message, gamepushnotification_request_path)
initialize_file("POGOProtos.Networking.Game.GamePushNotification.Responses", "%sResponse" % message, gamepushnotification_response_path)

# GameSocial
gamesocial_request_path = 'GameSocial_' + os.path.join("POGOProtos/Networking/Game/GameSocial/Messages", "%sMessage.proto" % message)
gamesocial_response_path = 'GameSocial_' + os.path.join("POGOProtos/Networking/Game/GameSocial/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GameSocial.Messages", "%sMessage" % message, gamesocial_request_path)
initialize_file("POGOProtos.Networking.Game.GameSocial.Responses", "%sResponse" % message, gamesocial_response_path)

# GameTelemetry
gametelemetry_request_path = 'GameTelemetry_' + os.path.join("POGOProtos/Networking/Game/GameTelemetry/Messages", "%sMessage.proto" % message)
gametelemetry_response_path = 'Platform_' + os.path.join("POGOProtos/Networking/Game/GameTelemetry/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GameTelemetry.Messages", "%sMessage" % message, gametelemetry_request_path)
initialize_file("POGOProtos.Networking.Game.GameTelemetry.Responses", "%sResponse" % message, gametelemetry_response_path)

# GameWebToken
gamewebtoken_request_path = 'GameWebToken_' + os.path.join("POGOProtos/Networking/Game/GameWebToken/Messages", "%sMessage.proto" % message)
gamewebtoken_response_path = 'GameWebToken_' + os.path.join("POGOProtos/Networking/Game/GameWebToken/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Game.GameWebToken.Messages", "%sMessage" % message, gamewebtoken_request_path)
initialize_file("POGOProtos.Networking.Game.GameWebToken.Responses", "%sResponse" % message, gamewebtoken_response_path)

# Vasa
vasa_request_path = 'Vasa_' + os.path.join("POGOProtos/Networking/Vasa/Messages", "%sMessage.proto" % message)
vasa_response_path = 'Vasa_' + os.path.join("POGOProtos/Networking/Vasa/Responses", "%sResponse.proto" % message)

initialize_file("POGOProtos.Networking.Vasa.Messages", "%sMessage" % message, vasa_request_path)
initialize_file("POGOProtos.Networking.Vasa.Responses", "%sResponse" % message, vasa_response_path)
