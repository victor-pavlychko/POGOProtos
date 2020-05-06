#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

import argparse
import operator
import os
import re
import shutil
from subprocess import call

# Add this to your path
protoc_executable = "protoc"

# Specify desired language | output | package (defaults -l cpp -p pogo -o out_singe_file)
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--lang", help="Language to produce proto single file.")
parser.add_argument("-p", "--package", help="Package to produce roto single file uses -p pogo or -p hp.")
parser.add_argument("-o", "--out_path", help="Output path for roto single file.")
parser.add_argument("--java_multiple_files", action='store_true', help="Write each message to a separate .java file.")
parser.add_argument("-g", "--generate_only", action='store_true', help='Generates only proto compilable.')
parser.add_argument("-k", "--keep_proto_file", action='store_true', help='Do not remove .proto file after compiling.')
args = parser.parse_args()

# Set defaults
lang = args.lang or "cpp"
out_path = args.out_path or "out_singe_file"
java_multiple_files = args.java_multiple_files
gen_only = args.generate_only
package = args.package or "pogo"
keep_file = args.keep_proto_file

# Determine where path's
raw_proto_file = os.path.abspath("base/raw_protos.proto")
protos_path = os.path.abspath("base")
out_path = os.path.abspath(out_path)

# Clean up previous
try:
    os.remove(out_path)
except OSError:
    pass

if out_path and os.path.exists(out_path):
    shutil.rmtree(out_path)

# Create necessary directory
if not os.path.exists(out_path):
    os.makedirs(out_path)

commands = []


def open_proto_file(main_file, package):
    if operator.contains(package, 'POGOProtos'):
        new_proto_single_file = main_file.replace("raw_protos.proto", "POGOProtos.proto")
    else:
        new_proto_single_file = main_file.replace("raw_protos.proto", "WUProtos.proto")
    # Add licenses
    head = '/*\n'
    head += '* Copyright 2016-2020 --=FurtiF=-- Co., Ltd.\n'
    head += '*\n'
    head += '* Licensed under the\n'
    head += '*	Educational Community License, Version 2.0 (the "License"); you may\n'
    head += '*	not use this file except in compliance with the License. You may\n'
    head += '*	obtain a copy of the License at\n'
    head += '*\n'
    head += '*	http://www.osedu.org/licenses/ECL-2.0\n'
    head += '*\n'
    head += '*	Unless required by applicable law or agreed to in writing,\n'
    head += '*	software distributed under the License is distributed on an "AS IS"\n'
    head += '*	BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express\n'
    head += '*	or implied. See the License for the specific language governing\n'
    head += '*	permissions and limitations under the License.\n'
    head += '*/\n\n'
    head += 'syntax = "proto3";\n'
    head += 'package %s;\n\n' % package

    if os.path.exists(new_proto_single_file):
        os.unlink(new_proto_single_file)

    open_for_new = open(new_proto_single_file, 'a')

    if not gen_only:
        # Add options by language
        if java_multiple_files and lang == "java":
            head += 'option java_multiple_files = true;\n\n'
        elif lang == "cpp":
            head += 'option optimize_for = CODE_SIZE;\n\n'

    open_for_new.writelines(head)

    messages = ''
    is_enum = False
    enum_name = ''
    is_message = False
    is_client_inbox_enum = False
    is_titan = False
    is_platform = False
    is_one_off = False

    with open(main_file, 'r') as proto_file:
        for proto_line in proto_file.readlines():
            if operator.contains(proto_line, "// ref: Niantic.Titan."):
                is_titan = True
            if operator.contains(proto_line, "// ref: Com.Nianticproject.Platform.") or operator.contains(proto_line,
                                                                                                          "// ref: Niantic.Platform."):
                is_platform = True
            if operator.contains(proto_line, "ClientInboxService.NotificationCategory"):
                is_client_inbox_enum = True
            if proto_line.startswith("message"):
                is_message = True
                match = re.split(r'\s', proto_line)
                message_name = match[1]
                if is_titan:
                    proto_line = proto_line.replace(message_name, "Titan" + message_name)
                    message_name = "Titan" + message_name
                    is_titan = False
                if is_platform:
                    proto_line = proto_line.replace(message_name, "Platform" + message_name)
                    is_platform = False
            if proto_line.startswith("enum"):
                is_enum = True
                match = re.split(r'\s', proto_line)
                enum_name = match[1].upper()
                if is_client_inbox_enum:
                    enum_name = "CLIENTINBOXSERVICE_" + enum_name
                    proto_line = proto_line.replace("NotificationCategory", "ClientInboxServiceNotificationCategory")
            if proto_line.startswith("syntax"):
                continue
            if proto_line.startswith("package"):
                continue
            # Ignore file licenses
            if proto_line.startswith("/*"):
                continue
            if proto_line.startswith("*"):
                continue
            if proto_line.startswith("*/"):
                continue
            # ---
            if isBlank(proto_line):
                continue
            # OneOf stuff here
            if operator.contains(proto_line, "//oneof"):
                is_one_off = True
            if operator.contains(proto_line, "//}"):
                is_one_off = False
            # ---
            if operator.contains(proto_line, "//") and is_one_off and gen_only:
                continue
            if (operator.contains(proto_line, "// ref:") or operator.contains(proto_line,
                                                                              "//----") or operator.contains(proto_line,
                                                                                                             "//}")) and gen_only:
                continue

            if is_enum:
                if not proto_line.startswith("enum"):
                    if not proto_line.startswith("}"):
                        e = proto_line.replace(re.split(r'(\W+)', proto_line)[2],
                                               enum_name + "_" + re.split(r'(\W+)', proto_line)[2])
                        messages += e
                    else:
                        messages += proto_line
                else:
                    messages += proto_line
            elif is_message:
                if operator.contains(proto_line, "PortalCurationImageResult.Result status = 1;"):
                    messages += proto_line.replace("PortalCurationImageResult", "PlatformPortalCurationImageResult")
                elif operator.contains(proto_line, "GymStatusAndDefendersProto gym_status"):
                    messages += proto_line
                elif operator.contains(proto_line, "ShareExRaidPassResult result"):
                    messages += proto_line
                elif operator.contains(proto_line, "CombatSeasonResult lifetime_results"):
                    messages += proto_line
                elif operator.contains(proto_line, "CombatSeasonResult current_season_results"):
                    messages += proto_line
                elif operator.contains(proto_line, "repeated VsSeekerBattleResult current_vs_seeker_set_results = 4"):
                    messages += proto_line
                elif operator.contains(proto_line, "CombatSeasonResult previous_season_results"):
                    messages += proto_line
                elif operator.contains(proto_line, "CombatSeasonResult last_season_result = 5"):
                    messages += proto_line
                elif operator.contains(proto_line, "InvasionStatus.Status status = 1"):
                    messages += proto_line
                elif operator.contains(proto_line, "BattleResultsProto battle_results = 10"):
                    messages += proto_line
                elif operator.contains(proto_line, "CombatSeasonResult current_season_result = 4"):
                    messages += proto_line
                elif operator.contains(proto_line, "CombatRewardStatus reward_status = 2"):
                    messages += proto_line
                elif operator.contains(proto_line, "OnboardingArStatus ar_status = 5"):
                    messages += proto_line
                elif operator.contains(proto_line, "WithWinRaidStatusProto with_win_raid_status = 7"):
                    messages += proto_line
                elif operator.contains(proto_line, "WithWinGymBattleStatusProto with_win_gym_battle_status = 10"):
                    messages += proto_line
                elif operator.contains(proto_line, "WithWinBattleStatusProto with_win_battle_status = 17"):
                    messages += proto_line
                elif operator.contains(proto_line, "DisplayWeatherProto.DisplayLevel cloud_level = 2"):
                    messages += proto_line
                elif operator.contains(proto_line, "DisplayWeatherProto.DisplayLevel rain_level = 3"):
                    messages += proto_line
                elif operator.contains(proto_line, "DisplayWeatherProto.DisplayLevel snow_level = 4"):
                    messages += proto_line
                elif operator.contains(proto_line, "DisplayWeatherProto.DisplayLevel fog_level = 5"):
                    messages += proto_line
                elif operator.contains(proto_line, "DisplayWeatherProto.DisplayLevel special_effect_level = 6"):
                    messages += proto_line
                elif operator.contains(proto_line, "DisplayWeatherProto.DisplayLevel cloud_level = 2"):
                    messages += proto_line
                elif operator.contains(proto_line, "DisplayWeatherProto.DisplayLevel rain_level = 3"):
                    messages += proto_line
                elif operator.contains(proto_line, "DisplayWeatherProto.DisplayLevel snow_level = 4"):
                    messages += proto_line
                elif operator.contains(proto_line, "DisplayWeatherProto.DisplayLevel fog_level = 5"):
                    messages += proto_line
                elif operator.contains(proto_line, "DisplayWeatherProto.DisplayLevel special_effect_level = 6"):
                    messages += proto_line
                elif operator.contains(proto_line, "GrapeshotAuthenticationDataProto upload_authentication = 3"):
                    messages += proto_line.replace("GrapeshotAuthenticationDataProto",
                                                   "TitanGrapeshotAuthenticationDataProto")
                elif operator.contains(proto_line, "GrapeshotAuthenticationDataProto delete_authentication = 4;"):
                    messages += proto_line.replace("GrapeshotAuthenticationDataProto",
                                                   "TitanGrapeshotAuthenticationDataProto")
                elif operator.contains(proto_line, "GrapeshotAuthenticationDataProto authentication = 2;"):
                    messages += proto_line.replace("GrapeshotAuthenticationDataProto",
                                                   "TitanGrapeshotAuthenticationDataProto")
                elif operator.contains(proto_line, "repeated GrapeshotChunkDataProto chunk_data = 1;"):
                    messages += proto_line.replace("GrapeshotChunkDataProto", "TitanGrapeshotChunkDataProto")
                elif operator.contains(proto_line, "GrapeshotComposeDataProto compose_data = 2;"):
                    messages += proto_line.replace("GrapeshotComposeDataProto", "TitanGrapeshotComposeDataProto")
                elif operator.contains(proto_line,
                                       "repeated AvailableSubmissionsPerSubmissionType availability_result_per_type = 8;"):
                    messages += proto_line.replace("AvailableSubmissionsPerSubmissionType",
                                                   "TitanAvailableSubmissionsPerSubmissionType")
                elif operator.contains(proto_line,
                                       "map<string, GrapeshotUploadingDataProto> file_context_to_grapeshot_data = 4;"):
                    messages += proto_line.replace("GrapeshotUploadingDataProto", "TitanGrapeshotUploadingDataProto")
                elif operator.contains(proto_line, "RoutePoiProto poi = 1;"):
                    messages += proto_line.replace("RoutePoiProto", "TitanRoutePoiProto")
                elif operator.contains(proto_line, "RouteGuidepostProto guidepost = 2;"):
                    messages += proto_line.replace("RouteGuidepostProto", "TitanRouteGuidepostProto")
                elif operator.contains(proto_line, "repeated RouteCheckpointProto checkpoints = 6;"):
                    messages += proto_line.replace("RouteCheckpointProto", "TitanRouteCheckpointProto")
                elif operator.contains(proto_line, "RouteImageProto main_image = 7;"):
                    messages += proto_line.replace("RouteImageProto", "TitanRouteImageProto")
                elif operator.contains(proto_line, "PoiSubmissionTelemetry poi_submission_telemetry = 1;"):
                    messages += proto_line.replace("PoiSubmissionTelemetry", "TitanPoiSubmissionTelemetry")
                elif operator.contains(proto_line,
                                       "PoiSubmissionPhotoUploadErrorTelemetry poi_submission_photo_upload_error_telemetry = 2;"):
                    messages += proto_line.replace("PoiSubmissionPhotoUploadErrorTelemetry",
                                                   "TitanPoiSubmissionPhotoUploadErrorTelemetry")
                elif operator.contains(proto_line, "PoiPlayerMetadataTelemetry player_metadata_telemetry = 3;"):
                    messages += proto_line.replace("PoiPlayerMetadataTelemetry", "TitanPoiPlayerMetadataTelemetry")
                elif operator.contains(proto_line, "repeated ClientGameMasterTemplateProto template = 2;"):
                    messages += proto_line.replace("ClientGameMasterTemplateProto",
                                                   "PlatformClientGameMasterTemplateProto")
                elif operator.contains(proto_line, "InventoryDeltaProto inventory_delta = 2;"):
                    messages += proto_line.replace("InventoryDeltaProto", "PlatformInventoryDeltaProto")
                elif operator.contains(proto_line, "repeated ClientGameMasterTemplateProto template = 2;"):
                    messages += proto_line.replace("ClientGameMasterTemplateProto",
                                                   "PlatformClientGameMasterTemplateProto")
                elif operator.contains(proto_line, "repeated InventoryItemProto inventory_item = 3;"):
                    messages += proto_line.replace("InventoryItemProto", "PlatformInventoryItemProto")
                elif operator.contains(proto_line, "repeated InventoryItemProto inventory_item = 1;"):
                    messages += proto_line.replace("InventoryItemProto", "PlatformInventoryItemProto")
                elif operator.contains(proto_line, "BackgroundModeClientSettingsProto settings = 2;"):
                    messages += proto_line.replace("BackgroundModeClientSettingsProto",
                                                   "PlatformBackgroundModeClientSettingsProto")
                elif operator.contains(proto_line, "PlayerSummaryProto friend = 2;"):
                    messages += proto_line.replace("PlayerSummaryProto", "PlatformPlayerSummaryProto")
                elif operator.contains(proto_line, "repeated LoginDetail login_detail = 2;"):
                    messages += proto_line.replace("LoginDetail", "PlatformLoginDetail")
                elif operator.contains(proto_line, "repeated TemplateVariable variables = 5;"):
                    messages += proto_line.replace("TemplateVariable", "PlatformTemplateVariable")
                elif operator.contains(proto_line, "repeated TemplateVariable builtin_variables = 2;"):
                    messages += proto_line.replace("TemplateVariable", "PlatformTemplateVariable")
                elif operator.contains(proto_line, "PlayerSummaryProto player = 1;"):
                    messages += proto_line.replace("PlayerSummaryProto", "PlatformPlayerSummaryProto")
                elif operator.contains(proto_line, "repeated FriendDetailsProto friend = 2;"):
                    messages += proto_line.replace("FriendDetailsProto", "PlatformFriendDetailsProto")
                elif operator.contains(proto_line, "repeated IncomingFriendInviteDisplayProto invites = 2;"):
                    messages += proto_line.replace("IncomingFriendInviteDisplayProto",
                                                   "PlatformIncomingFriendInviteDisplayProto")
                elif operator.contains(proto_line, "ClientInbox inbox = 2;"):
                    messages += proto_line.replace("ClientInbox", "PlatformClientInbox")
                elif operator.contains(proto_line, "repeated OutgoingFriendInviteDisplayProto invites = 2;"):
                    messages += proto_line.replace("OutgoingFriendInviteDisplayProto",
                                                   "PlatformOutgoingFriendInviteDisplayProto")
                elif operator.contains(proto_line, "IncomingFriendInviteProto invite = 1;"):
                    messages += proto_line.replace("IncomingFriendInviteProto", "PlatformIncomingFriendInviteProto")
                elif operator.contains(proto_line, "PlayerSummaryProto player = 2;"):
                    messages += proto_line.replace("PlayerSummaryProto", "PlatformPlayerSummaryProto")
                elif operator.contains(proto_line, "OutgoingFriendInviteProto invite = 1;"):
                    messages += proto_line.replace("OutgoingFriendInviteProto", "PlatformOutgoingFriendInviteProto")
                elif operator.contains(proto_line, "ApnToken apn_token = 1;"):
                    messages += proto_line.replace("ApnToken", "PlatformApnToken")
                elif operator.contains(proto_line, "GcmToken gcm_token = 2;"):
                    messages += proto_line.replace("GcmToken", "PlatformGcmToken")
                elif operator.contains(proto_line, "AddLoginActionProto new_login = 2;"):
                    messages += proto_line.replace("AddLoginActionProto", "PlatformAddLoginActionProto")
                elif operator.contains(proto_line, "LocationE6Proto location = 2;"):
                    messages += proto_line.replace("LocationE6Proto", "PlatformLocationE6Proto")
                elif operator.contains(proto_line, "LocationE6Proto location = 1;;"):
                    messages += proto_line.replace("LocationE6Proto", "PlatformLocationE6Proto")
                elif operator.contains(proto_line, "PlatformServerData server_data = 1001;"):
                    messages += proto_line.replace("PlatformServerData", "PlatformPlatformServerData")
                elif operator.contains(proto_line, "repeated GameItemContentProto game_item_content = 5;"):
                    messages += proto_line.replace("GameItemContentProto", "PlatformGameItemContentProto")
                elif operator.contains(proto_line, "repeated SkuPresentationProto presentation_data = 6;"):
                    messages += proto_line.replace("SkuPresentationProto", "PlatformSkuPresentationProto")
                elif operator.contains(proto_line, "repeated AvailableSkuProto available_sku = 1;"):
                    messages += proto_line.replace("AvailableSkuProto", "PlatformAvailableSkuProto")
                elif operator.contains(proto_line, "PlatformCommonFilterProto common_filters = 1002;"):
                    messages += proto_line.replace("PlatformCommonFilterProto", "PlatformPlatformCommonFilterProto")
                elif operator.contains(proto_line, "repeated InGamePurchaseDetails in_game_purchase_details = 7;"):
                    messages += proto_line.replace("InGamePurchaseDetails", "PlatformInGamePurchaseDetails")
                elif operator.contains(proto_line, "ClientTelemetryCommonFilterProto common_filters = 5;"):
                    messages += proto_line.replace("ClientTelemetryCommonFilterProto",
                                                   "PlatformClientTelemetryCommonFilterProto")
                elif operator.contains(proto_line, "repeated ClientTelemetryRecordProto events = 2;"):
                    messages += proto_line.replace("ClientTelemetryRecordProto", "PlatformClientTelemetryRecordProto")
                elif operator.contains(proto_line, "ServerRecordMetadata server_data = 4;"):
                    messages += proto_line.replace("ServerRecordMetadata", "PlatformServerRecordMetadata")
                elif operator.contains(proto_line, "CommonTelemetryShopView shop_view = 3;"):
                    messages += proto_line.replace("CommonTelemetryShopView", "PlatformCommonTelemetryShopView")
                elif operator.contains(proto_line, "CommonTelemetryShopClick shop_click = 2;"):
                    messages += proto_line.replace("CommonTelemetryShopClick", "PlatformCommonTelemetryShopClick")
                elif operator.contains(proto_line, "CommonTelemetryBootTime boot_time = 1;"):
                    messages += proto_line.replace("CommonTelemetryBootTime", "PlatformCommonTelemetryBootTime")
                elif operator.contains(proto_line, "LocationE6Proto location = 1;"):
                    messages += proto_line.replace("LocationE6Proto", "PlatformLocationE6Proto")
                elif operator.contains(proto_line, "PoiSubmissionTelemetry poi_submission_telemetry = 4;"):
                    messages += proto_line.replace("PoiSubmissionTelemetry", "PlatformPoiSubmissionTelemetry")
                elif operator.contains(proto_line,
                                       "PoiSubmissionPhotoUploadErrorTelemetry poi_submission_photo_upload_error_telemetry = 5;"):
                    messages += proto_line.replace("PoiSubmissionPhotoUploadErrorTelemetry",
                                                   "PlatformPoiSubmissionPhotoUploadErrorTelemetry")
                elif operator.contains(proto_line, "CommonTelemetryLogIn log_in = 6;"):
                    messages += proto_line.replace("CommonTelemetryLogIn", "PlatformCommonTelemetryLogIn")
                elif operator.contains(proto_line, "ServerRecordMetadata server_data = 7;"):
                    messages += proto_line.replace("ServerRecordMetadata", "PlatformServerRecordMetadata")
                elif operator.contains(proto_line, "repeated ClientTelemetryRecordProto metrics = 3;"):
                    messages += proto_line.replace("ClientTelemetryRecordProto", "PlatformClientTelemetryRecordProto")
                elif operator.contains(proto_line, "ClientTelemetryCommonFilterProto common_filters = 8;"):
                    messages += proto_line.replace("ClientTelemetryCommonFilterProto",
                                                   "PlatformClientTelemetryCommonFilterProto")

                # Harry poter here....
                elif operator.contains(proto_line, "BackgroundToken token = 1;") and package == 'hp':
                    messages += proto_line.replace("BackgroundToken", "PlatformBackgroundToken")
                elif operator.contains(proto_line, "AccountSettingsProto settings = 2;") and package == 'hp':
                    messages += proto_line.replace("AccountSettingsProto", "PlatformAccountSettingsProto")
                elif operator.contains(proto_line,
                                       "repeated NianticFriendDetailsProto niantic_friend_details = 2;") and package == 'hp':
                    messages += proto_line.replace("NianticFriendDetailsProto", "PlatformNianticFriendDetailsProto")
                elif operator.contains(proto_line, "SocialProto.AppKey app_key = 3;") and package == 'hp':
                    messages += proto_line.replace("SocialProto", "PlatformSocialProto")
                elif operator.contains(proto_line, "PlayerSettingsProto settings = 2;") and package == 'hp':
                    messages += proto_line.replace("PlayerSettingsProto", "PlatformPlayerSettingsProto")
                elif operator.contains(proto_line,
                                       "repeated SocialProto.AppKey niantic_social_graph_app_keys = 6;") and package == 'hp':
                    messages += proto_line.replace("SocialProto", "PlatformSocialProto")
                elif operator.contains(proto_line, "PlayerSettingsProto settings = 1;") and package == 'hp':
                    messages += proto_line.replace("PlayerSettingsProto", "PlatformPlayerSettingsProto")
                elif operator.contains(proto_line, "AccountSettingsProto settings = 1;") and package == 'hp':
                    messages += proto_line.replace("AccountSettingsProto", "PlatformAccountSettingsProto")
                elif operator.contains(proto_line,
                                       "repeated ClientTelemetryRecordProto metrics = 3;") and package == 'hp':
                    messages += proto_line.replace("ClientTelemetryRecordProto", "PlatformClientTelemetryRecordProto")
                else:
                    messages += proto_line
            else:
                messages += proto_line

            if not proto_line.startswith("}") and operator.contains(proto_line, "}"):
                messages += "\n"

            if proto_line.startswith("}"):
                messages += "\n"
                is_enum = False
                is_message = False
                is_client_inbox_enum = False
                enum_name = ''

    open_for_new.writelines(messages[:-1])
    open_for_new.close()
    compile(new_proto_single_file)


def isBlank(myString):
    if myString and myString.strip():
        return False
    return True


def compile(file):
    command_out_path = os.path.abspath(out_path)
    commands.append(
        """{0} --proto_path="{1}" --{2}_out="{3}" "{4}\"""".format(
            protoc_executable,
            protos_path,
            lang,
            command_out_path,
            file
        )
    )


if package == 'pogo':
    package_name = 'POGOProtos.Rpc'
    input_file = "POGOProtos.proto"
elif package == 'hp':
    package_name = 'WUProtos.Rpc'
    input_file = "WUProtos.proto"
else:
    print(
        'Package not selected. Use -p or --package pogo for PokemonGo or -p or --package hp for Harry Potter Wizards.')
    exit()

open_proto_file(raw_proto_file, package_name)
generated_file = raw_proto_file.replace("raw_protos.proto", input_file)
descriptor_file = generated_file.replace(".proto", ".desc")
descriptor_file_arguments = ['--include_source_info', '--include_imports']

commands.append(
    """"{0}" --proto_path="{1}" --descriptor_set_out="{2}" {3} {4}""".format(
        protoc_executable,
        protos_path,
        descriptor_file,
        ' '.join(descriptor_file_arguments),
        generated_file))

if not gen_only:
    for command in commands:
        call(command, shell=True)

# Add new proto version
if gen_only:
    shutil.move(generated_file, out_path)

if keep_file:
    shutil.move(generated_file, out_path)

# Add new desc version
if not gen_only:
    descriptor_file = generated_file.replace(".proto", ".desc")
    shutil.move(descriptor_file, out_path)

# Clean genererated and unneded files
try:
    os.unlink(generated_file)
except OSError:
    pass

print("Done!")
