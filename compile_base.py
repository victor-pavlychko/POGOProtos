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
parser.add_argument("-o", "--out_path", help="Output path for roto single file.")
parser.add_argument("-m", "--java_multiple_files", action='store_true',
                    help='Write each message to a separate .java file.')
parser.add_argument("-g", "--generate_only", action='store_true', help='Generates only proto compilable.')
parser.add_argument("-k", "--keep_proto_file", action='store_true', help='Do not remove .proto file after compiling.')
parser.add_argument("-r", "--rpc", action='store_true', help='Generates Rpc proto.')
parser.add_argument("-1", "--generate_one_off", action='store_true', help='Include on off')
args = parser.parse_args()

# Set defaults
lang = args.lang or "proto"
out_path = args.out_path or "out/single_file/" + lang
java_multiple_files = args.java_multiple_files
gen_only = args.generate_only
gen_one_off = args.generate_one_off
keep_file = args.keep_proto_file
rpc = args.rpc

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


def finish_compile(out_path, lang):
    if lang == 'python':
        pogo_protos_path = os.path.join(out_path, "POGOProtos")

        for root, dirnames, filenames in os.walk(pogo_protos_path):
            init_path = os.path.join(root, '__init__.py')

            with open(init_path, 'w') as init_file:
                if pogo_protos_path is root:
                    init_file.write(
                        "'Generated'; import os; import sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))")


def open_proto_file(main_file, package_name):
    new_proto_single_file = main_file.replace("raw_protos.proto", "POGOProtos.Rpc.proto")
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
    head += 'package %s;\n\n' % package_name

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
    refs = []

    with open(main_file, 'r') as proto_file:
        for proto_line in proto_file.readlines():
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

            if proto_line.startswith("enum"):
                is_enum = True
                enum_name = re.split(r'\s', proto_line)[1].upper()

            # refs
            if operator.contains(proto_line, "// ref:"):
                refs.append(proto_line.replace("// ref:", "").strip())
            if operator.contains(proto_line, "}") and refs:
                refs.pop()

            # OneOf stuff here
            if operator.contains(proto_line, "//oneof"):
                is_one_off = True
            # ---
            if operator.contains(proto_line, "//") and is_one_off:
                if gen_one_off:
                    if operator.contains(proto_line, "none = 0;"):
                        continue
                    proto_line = proto_line.replace("//", "")
                    if not operator.contains(proto_line, "{") and not operator.contains(proto_line, "}"):
                        field = proto_line.split("=")[0].strip()
                        refName = "/".join(refs[-1].split("/")[:-1])
                        proto_line = "#" + refName + "#" + field + "#"
                else:
                    continue
            if is_one_off and operator.contains(proto_line, "}"):
                is_one_off = False

            if is_enum:
                if not proto_line.startswith("enum"):
                    if not proto_line.startswith("}"):
                        e = proto_line.replace(re.split(r'(\W+)', proto_line)[2],
                                               enum_name + "_" + re.split(r'(\W+)', proto_line)[2])
                        proto_line = e

            if not is_one_off and gen_one_off and operator.contains(proto_line, "=") and refs:
                split = proto_line.strip().split(" ", 2)
                field = split[1].strip()
                target = "#" + refs[-1] + "#" + field + "#"
                if target in messages:
                    messages = messages.replace(target, "\t" + proto_line)
                    continue

            messages += proto_line

            if not proto_line.startswith("}") and operator.contains(proto_line, "}"):
                messages += "\n"

            if proto_line.startswith("}"):
                messages += "\n"
                is_enum = False
                enum_name = ''

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

            if not skip and not ((operator.contains(proto_line, "// ref:") or operator.contains(proto_line,
                                                                                                "//----") or operator.contains(
                proto_line, "//}")) and gen_only):
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

    for fix_line in messages.split("\n"):
        # ignore refs
        if operator.contains(fix_line, "//"):
            continue

        if fix_line.startswith("message"):
            match = re.split(r'\s', fix_line)
            message_for_fix = match[1]
        elif fix_line.startswith("}"):
            message_for_fix = ''

        # Check for all bytes refs
        # if operator.contains(fix_line, "\tbytes"):
        #     byte = fix_line.split("=")
        #     byte_fix = byte[0].replace("\t","")[:-1]
        #     print('elif message_for_fix == "' + message_for_fix + '" and operator.contains(fix_line, "' + byte_fix +'"):')
        #     print('\tfix_line = fix_line.replace("bytes", "Good_Proto_Here")')

        # if package == "pogo":
        # Replace bytes for good proto here by condition
        # if message_for_fix == "PlatformClientGameMasterTemplateProto" and operator.contains(fix_line, "bytes data"):
        #     fix_line = fix_line.replace("bytes", "GameMasterClientTemplateProto")
        # elif message_for_fix == "PlatformDownloadSettingsResponseProto" and operator.contains(fix_line, "bytes values"):
        #     fix_line = fix_line.replace("bytes", "GlobalSettingsProto")
        # elif message_for_fix == "PlatformInventoryItemProto" and operator.contains(fix_line, "bytes item"):
        #     fix_line = fix_line.replace("bytes item", "HoloInventoryItemProto inventory_item_data")
        # elif message_for_fix == "ItemProto" and operator.contains(fix_line, "item"):
        #     fix_line = fix_line.replace("item", "item_id")

        # Need find a good proto if not found need create one
        # elif message_for_fix == "PlatformBackgroundToken" and operator.contains(fix_line, "bytes token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformBackgroundToken" and operator.contains(fix_line, "bytes iv"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformInventoryItemProto" and operator.contains(fix_line, "bytes deleted_item_key"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformProxyRequestProto" and operator.contains(fix_line, "bytes payload"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformProxyResponseProto" and operator.contains(fix_line, "bytes payload"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "FitnessReportProto" and operator.contains(fix_line, "bytes game_data"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "OpenSponsoredGiftProto" and operator.contains(fix_line, "bytes encrypted_ad_token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformClientApiSettingsProto" and operator.contains(fix_line, "bytes payload"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "RedeemPasscodeResponseProto" and operator.contains(fix_line, "bytes acquired_items_proto"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "SfidaAuthToken" and operator.contains(fix_line, "bytes response_token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "SfidaCertificationRequest" and operator.contains(fix_line, "bytes payload"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "SfidaCertificationResponse" and operator.contains(fix_line, "bytes payload"):
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
        # elif message_for_fix == "PasscodeRedemptionFlowResponse" and operator.contains(fix_line, "bytes in_game_reward"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "PlatformClientTelemetryRecordProto" and operator.contains(fix_line, "bytes encoded_message"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "AdDetails" and operator.contains(fix_line, "bytes encrypted_ad_token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "ReportAdInteractionProto" and operator.contains(fix_line, "bytes encrypted_ad_token"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")

        # # Old stuff addeded into optmise raw
        # elif message_for_fix == "AuthTicket" and operator.contains(fix_line, "bytes start"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")
        # elif message_for_fix == "AuthTicket" and operator.contains(fix_line, "bytes end"):
        #     fix_line = fix_line.replace("bytes", "Good_Proto_Here")

        # fixed_messages += fix_line + "\n"

    # messages = fixed_messages[:-1]

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


if not gen_only:
    print("Protocol Buffers version:")
    call(""""{0}" --version""".format(protoc_executable), shell=True)

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
    shutil.copy(generated_file, protos_path + '/v0.183.0_obf.proto')
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

print("Done!")
