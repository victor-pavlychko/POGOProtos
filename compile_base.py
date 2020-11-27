#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

import argparse
import operator
import os
import re
import shutil
from subprocess import call

# Variables
protoc_executable = "protoc"
package_name = 'POGOProtos.Rpc'
input_file = "POGOProtos.Rpc.proto"


def is_blank(my_string):
    if my_string and my_string.strip():
        return False
    return True


# args
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--lang", help="Language to produce proto single file.")
parser.add_argument("-v", "--version", help="Set version out ex:. (189.0_obf)")
parser.add_argument("-o", "--out_path", help="Output path for roto single file.")
parser.add_argument("-m", "--java_multiple_files", action='store_true',
                    help='Write each message to a separate .java file.')
parser.add_argument("-g", "--generate_only", action='store_true', help='Generates only proto compilable.')
parser.add_argument("-b", "--generate_new_base", action='store_true', help='Generates new proto base refs.')
parser.add_argument("-k", "--keep_proto_file", action='store_true', help='Do not remove .proto file after compiling.')
parser.add_argument("-r", "--rpc", action='store_true', help='Generates Rpc proto.')
parser.add_argument("-1", "--generate_one_off", action='store_true', help='Include on off')
args = parser.parse_args()

# Add licenses
head = '/*\n'
head += '* Copyright 2016-2020 --=FurtiF=--.\n'
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
head += 'package %s;\n\n' % package_name

# Set defaults
lang = args.lang or "proto"
out_path = args.out_path or "out/single_file/" + lang
java_multiple_files = args.java_multiple_files
gen_only = args.generate_only
version = args.version or "193.1"
gen_base = args.generate_new_base
gen_one_off = args.generate_one_off
keep_file = args.keep_proto_file
rpc = args.rpc

# Determine where path's
raw_name = "v0.193.1.proto"
# raw_name = "raw_protos.proto"
raw_proto_file = os.path.abspath("base/" + raw_name)
base_file = os.path.abspath("base/base.proto")
protos_path = os.path.abspath("base")
out_path = os.path.abspath(out_path)

## Load Base
base_enums = {}
base_messages = {}
base_as_data = False
base_is_enum = False
base_proto_name = ''
base_data = ''

with open(base_file, 'r') as proto_file:
    for proto_line in proto_file.readlines():
        if proto_line.startswith("enum") or proto_line.startswith("message"):
            base_as_data = True
            base_proto_name = proto_line.split(" ")[1]
        if proto_line.startswith("enum"):
            base_is_enum = True
        if proto_line.startswith("message"):
            base_is_enum = False
        if proto_line.startswith("}"):
            base_data += proto_line
            if base_is_enum:
                base_enums.setdefault(base_proto_name, base_data)
            else:
                base_messages.setdefault(base_proto_name, base_data)
            base_as_data = False
            base_is_enum = False
            base_proto_name = ''
            base_data = ''
        if base_as_data:
            base_data += proto_line

# Re-order base
# Clean up previous base
try:
    os.remove(base_file)
except OSError:
    pass

open_for_new = open(base_file, 'a')
new_base_file = head

for p in sorted(base_enums):
    # print("Key: " + p + "\n" + base_enums[p])
    new_base_file += base_enums[p] + "\n"
for p in sorted(base_messages):
    # print("Key: " + p + "\n" + base_messages[p])
    new_base_file += base_messages[p] + "\n"

open_for_new.writelines(new_base_file[:-1])
open_for_new.close()

# Clean up previous out
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


def finish_compile(out_path, lang):
    if lang == 'python':
        pogo_protos_path = os.path.join(out_path, "POGOProtos")

        for root, dirnames, filenames in os.walk(pogo_protos_path):
            init_path = os.path.join(root, '__init__.py')

            with open(init_path, 'w') as init_file:
                if pogo_protos_path is root:
                    init_file.write(
                        "'Generated'; import os; import sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))")


def open_proto_file(main_file, head):
    new_proto_single_file = main_file.replace(raw_name, "POGOProtos.Rpc.proto")

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
    is_one_off = False
    enums_dic = {}
    messages_dic = {}
    ignored_one_of = {}
    is_ignored = False
    check_sub_message_end = True
    fixed_messages = ''

    with open(main_file, 'r') as proto_file:
        for proto_line in proto_file.readlines():
            if is_ignored and operator.contains(proto_line, "//}"):
                is_ignored = False
            if operator.contains(proto_line, "//ignored_"):
                proto_line = proto_line.replace("//ignored_", "//")
                is_ignored = True
            if is_ignored and operator.contains(proto_line, "=") and not operator.contains(proto_line, "//none = 0;"):
                ignored_one_of.setdefault(proto_line.strip().split("=")[1], proto_line.strip().split("=")[0].strip())
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
            if is_blank(proto_line):
                continue

            # if proto_line.startswith("enum"):
            #     is_enum = True
            #     match = re.split(r'\s', proto_line)
            #     if match[1].isupper() and len(match[1]) == 11:
            #         enum_name = match[1].upper()
            #     else:
            #         i = 0
            #         enum_name = ''
            #         for x in match[1]:
            #             if x.isupper() and i > 0:
            #                 enum_name += '_' + x
            #             else:
            #                 enum_name += x
            #             i = i + 1
            #         enum_name = enum_name.upper().replace('P_O_I_', 'POI_')

            if not proto_line.startswith("enum") and not proto_line.startswith("message") and operator.contains(
                    proto_line, "enum") or operator.contains(proto_line, "message"):
                check_sub_message_end = False
            if len(ignored_one_of) > 0 and operator.contains(proto_line,
                                                             "=") and not is_ignored and not operator.contains(
                proto_line, "//") and not is_one_off and not is_enum and check_sub_message_end:
                if proto_line.strip().split("=")[1] in ignored_one_of:
                    proto_line = proto_line.replace(proto_line.strip().split("=")[0].split(" ")[1],
                                                    ignored_one_of[proto_line.strip().split("=")[1]]).replace("//", "")
                    try:
                        ignored_one_of.pop(proto_line.strip().split("=")[1], None)
                    except KeyError:
                        pass

            messages += proto_line

            if not proto_line.startswith("}") and operator.contains(proto_line, "}"):
                check_sub_message_end = True
                messages += "\n"
                is_one_off = False
                is_enum = False

            if proto_line.startswith("}"):
                messages += "\n"
                is_enum = False
                is_one_off = False
                ignored_one_of.clear()

    ## fix enums names
    # print("Cleaning process on enums...")
    for _enum in enums_dic:
        # print("Obfuscated enum name " + _enum + " clean enum name " + enums_dic[_enum])
        messages = messages.replace(_enum, enums_dic[_enum])

    if gen_one_off:
        messagesNew = ""
        lastLine = ""

        refs = []
        is_one_off = False
        skip = False
        setSkipFalse = False
        removeLast = False

        refsCount = {}
        for proto_line in messages.split("\n"):
            if operator.contains(proto_line, "// ref:"):
                refs.append(proto_line.replace("// ref:", "").strip())

            if operator.contains(proto_line, "}") and refs:
                refs.pop()

            if operator.contains(proto_line, "oneof") and refs:
                is_one_off = True
                count = len(messages.split("// ref: " + refs[-1] + "\n")) - 1
                if not refs[-1] in refsCount:
                    refsCount[refs[-1]] = 0
                refsCount[refs[-1]] += 1
                if not count == refsCount[refs[-1]]:
                    skip = True
                    removeLast = True

            if is_one_off and operator.contains(proto_line, "}"):
                is_one_off = False
                setSkipFalse = True

            if not skip and not (
                    (operator.contains(proto_line, "// ref:") or operator.contains(proto_line, "//----")) and gen_only):
                if not removeLast:
                    messagesNew += lastLine
                removeLast = False
                lastLine = proto_line + "\n"
            elif skip:
                removeLast = False

            if setSkipFalse:
                skip = False
                setSkipFalse = False

        messages = messagesNew

    ## check messages first
    proto_name = ''
    for proto_line in messages.split("\n"):
        if is_blank(proto_line):
            continue
        if proto_line.startswith("message"):
            proto_name = proto_line.split(" ")[1]
        if proto_line == '':
            continue
        if operator.contains(proto_line, "generic_click_telemetry = 3;"):
            messages_dic.setdefault(proto_name, "HoloholoClientTelemetryOmniProto")
        elif operator.contains(proto_line, "ERROR_PLAYER_HAS_NO_STICKERS = 8;"):
            messages_dic.setdefault(proto_name, "SendGiftOutProto")
        elif operator.contains(proto_line, "ERROR_LOBBY_EXPIRED = 14;"):
            messages_dic.setdefault(proto_name, "JoinLobbyOutProto")
        elif operator.contains(proto_line, "ERROR_INSUFFICIENT_RESOURCES = 5;"):
            messages_dic.setdefault(proto_name, "UnlockPokemonMoveOutProto")
        elif operator.contains(proto_line, "pokemon_candy = 4;"):
            messages_dic.setdefault(proto_name, "LootItemProto")
        elif operator.contains(proto_line, "pokedex_entry = 3;"):
            messages_dic.setdefault(proto_name, "HoloInventoryItemProto")
        elif operator.contains(proto_line, "pokedex_entry_id = 3;"):
            messages_dic.setdefault(proto_name, "HoloInventoryKeyProto")
        elif operator.contains(proto_line, "ERROR_PLAYER_BELOW_MIN_LEVEL = 5;"):
            messages_dic.setdefault(proto_name, "StartIncidentOutProto")
        elif operator.contains(proto_line, "IncidentDisplayType") and operator.contains(proto_line, " = 6;"):
            messages_dic.setdefault(proto_name, "PokestopIncidentDisplayProto")
        elif operator.contains(proto_line, "\t\tQuestType ") and operator.contains(proto_line, " = 1;"):
            messages_dic.setdefault(proto_name, "DailyStreaksProto")
        elif operator.contains(proto_line, "exponential_buckets = 2;"):
            messages_dic.setdefault(proto_name, "Distribution")
        elif operator.contains(proto_line, "\t\tERROR_BUDDY_HAS_NOT_PICKED_UP_ANY_SOUVENIRS = 4;"):
            messages_dic.setdefault(proto_name, "OpenBuddyGiftOutProto")
        elif operator.contains(proto_line, "\t\tERROR_INVALD_NUMBER_ATTACKING_POKEMON_IDS = 2;"):
            messages_dic.setdefault(proto_name, "GetNpcCombatRewardsOutProto")
        elif operator.contains(proto_line, "\t\tPOI_INACCESSIBLE = 6;"):
            messages_dic.setdefault(proto_name, "FortSearchOutProto")
        elif operator.contains(proto_line, "TGC_TRACKING_QUEST = 7;"):
            messages_dic.setdefault(proto_name, "QuestProto")

    ## fix messages names
    # print("Cleaning process on messages...")
    for _message in messages_dic:
        # print("Obfuscated message name " + _message + " clean message name " + messages_dic[_message])
        messages = messages.replace(_message, messages_dic[_message])

    message_for_fix = None

    for fix_line in messages.split("\n"):
        # ignore refs
        if fix_line.startswith("message"):
            match = re.split(r'\s', fix_line)
            message_for_fix = match[1]
        elif fix_line.startswith("enum"):
            match = re.split(r'\s', fix_line)
            message_for_fix = match[1]

        ## Check for all bytes refs
        # if operator.contains(fix_line, "\tbytes"):
        #     byte = fix_line.split("=")
        #     byte_fix = byte[0].replace("\t", "")[:-1]
        #     print(
        #         'elif message_for_fix == "' + message_for_fix + '" and operator.contains(fix_line, "' + byte_fix + '"):')
        #     print('\tfix_line = fix_line.replace("bytes", "Good_Proto_Here")')

        # Replace bytes for good proto here by condition

        # ## Allready setted
        # if message_for_fix == "PlatformClientGameMasterTemplateProto" and operator.contains(fix_line, "bytes data"):
        #     fix_line = fix_line.replace("bytes", "GameMasterClientTemplateProto")
        # elif message_for_fix == "PlatformDownloadSettingsResponseProto" and operator.contains(fix_line, "bytes values"):
        #     fix_line = fix_line.replace("bytes", "GlobalSettingsProto")
        # elif message_for_fix == "PlatformInventoryItemProto" and operator.contains(fix_line, "bytes item"):
        #     fix_line = fix_line.replace("bytes item", "HoloInventoryItemProto inventory_item_data")
        # elif message_for_fix == "PlatformInventoryItemProto" and operator.contains(fix_line, "bytes deleted_item_key"):
        #     fix_line = fix_line.replace("bytes", "HoloInventoryKeyProto")
        # elif message_for_fix == "PlatformMapTileDataProto" and operator.contains(fix_line, "bytes tile_data"):
        #     fix_line = fix_line.replace("bytes", "PlatformMapCompositionRoot")
        # elif message_for_fix == "PlatformMapTileDataProto" and operator.contains(fix_line, "bytes label_data"):
        #     fix_line = fix_line.replace("bytes", "PlatformLabelTile")
        # ###########
        # ## Others #
        # ###########
        # elif message_for_fix == "ItemProto" and operator.contains(fix_line, "item"):
        #     fix_line = fix_line.replace("item", "item_id")
        # ## End allready setted

        ## Need find a good proto if not found need create one
        # elif message_for_fix == "PlatformBackgroundToken" and operator.contains(fix_line, "bytes token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformBackgroundToken" and operator.contains(fix_line, "bytes iv"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformProxyRequestProto" and operator.contains(fix_line, "bytes payload"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformProxyResponseProto" and operator.contains(fix_line, "bytes payload"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "ReportAdFeedbackRequest" and operator.contains(fix_line, "bytes encrypted_ad_token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "SfidaCertificationResponse" and operator.contains(fix_line, "bytes payload"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "OpenSponsoredGiftProto" and operator.contains(fix_line, "bytes encrypted_ad_token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "ReportAdInteractionProto" and operator.contains(fix_line, "bytes encrypted_ad_token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "FitnessReportProto" and operator.contains(fix_line, "bytes game_data"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "SfidaAuthToken" and operator.contains(fix_line, "bytes response_token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "SfidaCertificationRequest" and operator.contains(fix_line, "bytes payload"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "AdDetails" and operator.contains(fix_line, "bytes encrypted_ad_token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformClientApiSettingsProto" and operator.contains(fix_line, "bytes payload"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PasscodeRedemptionFlowResponse" and operator.contains(fix_line, "bytes in_game_reward"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "RedeemPasscodeResponseProto" and operator.contains(fix_line, "bytes acquired_items_proto"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformAddLoginActionProto" and operator.contains(fix_line, "bytes inner_message"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformFriendDetailsProto" and operator.contains(fix_line, "bytes friend_visible_data"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformFriendDetailsProto" and operator.contains(fix_line, "bytes data_with_me"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformGetFriendsListOutProto" and operator.contains(fix_line, "bytes data_with_me"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformGetFriendsListOutProto" and operator.contains(fix_line, "bytes shared_data"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformGetFriendsListOutProto" and operator.contains(fix_line, "bytes data_from_me"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformGetFriendsListOutProto" and operator.contains(fix_line, "bytes data_to_me"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformPlayerSummaryProto" and operator.contains(fix_line, "bytes public_data"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformTemplateVariable" and operator.contains(fix_line, "bytes byte_value"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "AssetDigestEntryProto" and operator.contains(fix_line, "bytes key"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "BackgroundToken" and operator.contains(fix_line, "bytes token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "BackgroundToken" and operator.contains(fix_line, "bytes iv"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "BelugaBleFinalizeTransfer" and operator.contains(fix_line, "bytes server_signature"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "BelugaBleTransferProto" and operator.contains(fix_line, "bytes server_signature"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "BelugaTransactionCompleteProto" and operator.contains(fix_line, "bytes app_signature"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "BelugaTransactionCompleteProto" and operator.contains(fix_line, "bytes firmware_signature"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "BelugaTransactionStartOutProto" and operator.contains(fix_line, "bytes server_signature"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "CreateBuddyMultiplayerSessionOutProto" and operator.contains(fix_line, "bytes arbe_join_token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "JoinBuddyMultiplayerSessionOutProto" and operator.contains(fix_line, "bytes arbe_join_token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "RegisterSfidaResponse" and operator.contains(fix_line, "bytes access_token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformClientTelemetryRecordProto" and operator.contains(fix_line, "bytes encoded_message"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformAuthTicket" and operator.contains(fix_line, "bytes start"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformAuthTicket" and operator.contains(fix_line, "bytes end"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")

        fixed_messages += fix_line + "\n"

    messages = fixed_messages[:-1]

    ## Reorder all this
    new_base_enums = {}
    new_base_messages = {}
    new_base_as_data = False
    new_base_is_enum = False
    new_base_proto_name = ''
    new_base_data = ''

    for proto_line in messages.split("\n"):
        if proto_line.startswith("enum") or proto_line.startswith("message"):
            new_base_as_data = True
            new_base_proto_name = proto_line.split(" ")[1]
        if proto_line.startswith("enum"):
            new_base_is_enum = True
        if proto_line.startswith("message"):
            new_base_is_enum = False
        if proto_line.startswith("}"):
            new_base_data += proto_line + "\n"
            if new_base_is_enum:
                new_base_enums.setdefault(new_base_proto_name, new_base_data)
            else:
                new_base_messages.setdefault(new_base_proto_name, new_base_data)
            new_base_as_data = False
            new_base_is_enum = False
            new_base_proto_name = ''
            new_base_data = ''
        if new_base_as_data:
            new_base_data += proto_line + "\n"

    new_base_file = ''

    for p in sorted(new_base_enums):
        new_base_file += new_base_enums[p] + "\n"
    for p in sorted(new_base_messages):
        new_base_file += new_base_messages[p] + "\n"

    messages = new_base_file
    open_for_new.writelines(messages[:-1])
    open_for_new.close()
    add_command_for_new_proto_file(new_proto_single_file)


def add_command_for_new_proto_file(file):
    command_out_path = os.path.abspath(out_path)
    options = ''
    arguments = ''
    if lang == 'js':
        options = 'import_style=commonjs,binary'
    elif lang == 'swift':
        arguments = '--swift_opt=Visibility=Public'
    # elif lang == 'csharp':
    #    arguments = '--csharp_opt=file_extension=.g.cs --csharp_opt=base_namespace'
    # elif lang == 'dart':
    #    arguments = '--plugin "pub run protoc_plugin"'
    # elif lang == 'lua':
    #    arguments = '--plugin=protoc-gen-lua="../ProtoGenLua/plugin/build.bat"'
    elif lang == 'go':
        options = 'plugins=grpc'

    commands.append(
        """{0} --proto_path={1} --{2}_out={3}:{4} {5} {6}""".format(
            protoc_executable,
            protos_path,
            lang,
            options,
            command_out_path,
            arguments,
            file
        )
    )


# print("Protocol Buffers version:")
# call(""""{0}" --version""".format(protoc_executable), shell=True)

open_proto_file(raw_proto_file, head)
generated_file = raw_proto_file.replace(raw_name, input_file)
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
    # Compile commands
    for command in commands:
        call(command, shell=True)

# Add new proto version
if gen_only:
    if rpc:
        dir_rpc = 'src/' + input_file.replace('.proto', '').replace('.', '/')
        if os.path.exists(dir_rpc):
            shutil.rmtree(dir_rpc)

        if not os.path.exists(dir_rpc):
            os.makedirs(dir_rpc)

        shutil.copy(generated_file, dir_rpc + '/Rpc.proto')
    # shutil.copy(generated_file, protos_path + '/v0.' + version + '.proto')
    # New base for next references names
    if gen_base:
        try:
            os.unlink(base_file)
        except OSError:
            pass

        shutil.copy(generated_file, base_file)
    shutil.move(generated_file, out_path)

if keep_file:
    shutil.move(generated_file, out_path)

# Add new desc version
if not gen_only:
    descriptor_file = generated_file.replace(".proto", ".desc")
    shutil.move(descriptor_file, out_path)

if lang == 'python':
    finish_compile(out_path, lang)

# Clean genererated and unneded files
try:
    os.unlink(generated_file)
except OSError:
    pass

# print("Done!")
