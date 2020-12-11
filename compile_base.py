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
version = args.version or "195.0"
gen_base = args.generate_new_base
keep_file = args.keep_proto_file
rpc = args.rpc

# Determine where path's
raw_name = "v0.195.0.proto"
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

try:
    os.remove(base_file)
except OSError:
    pass

open_for_new = open(base_file, 'a')
new_base_file = head

# Re-order base
for p in sorted(base_enums):
    new_base_file += base_enums[p] + "\n"
for p in sorted(base_messages):
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
    is_one_off = False
    ignored_one_of = {}
    is_ignored = False
    check_sub_message_end = True
    proto_name = ''

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
            if operator.contains(proto_line, "message ") or operator.contains(proto_line, "enum ") or operator.contains(
                    proto_line, "oneof ") and operator.contains(
                proto_line, "{"):
                proto_name = proto_line.split(" ")[1].strip()

            if proto_name == "HoloPokemonId" and not operator.contains(proto_line, "{") and not operator.contains(
                    proto_line, "}") and operator.contains(proto_line, "HOLO_POKEMON_ID_"):
                proto_line = proto_line.replace("HOLO_POKEMON_ID_", "").replace("POKEMON_UNSET",
                                                                                "V0000_POKEMON_MISSINGNO")
                proto_line = proto_line.replace(proto_line.split("_POKEMON_")[0].strip(), "").replace("_POKEMON_", "")
                if operator.contains(proto_line, "NIDORAN") and operator.contains(proto_line, "= 29;"):
                    proto_line = proto_line.replace("NIDORAN", "NIDORAN_FEMALE")
                elif operator.contains(proto_line, "NIDORAN") and operator.contains(proto_line, "= 32;"):
                    proto_line = proto_line.replace("NIDORAN", "NIDORAN_MALE")

            if proto_name == "HoloPokemonFamilyId" and not operator.contains(proto_line, "{") and not operator.contains(
                    proto_line, "}") and operator.contains(proto_line, "HOLO_POKEMON_FAMILY_ID_"):
                proto_line = proto_line.replace("HOLO_POKEMON_FAMILY_ID_", "").replace("FAMILY_UNSET",
                                                                                       "V0000_FAMILY_UNSET")
                proto_line = proto_line.replace(proto_line.split("_FAMILY_")[0].strip(), "").replace("_FAMILY_",
                                                                                                     "FAMILY_")
                if operator.contains(proto_line, "NIDORAN") and operator.contains(proto_line, "= 29;"):
                    proto_line = proto_line.replace("NIDORAN", "NIDORAN_FEMALE")
                elif operator.contains(proto_line, "NIDORAN") and operator.contains(proto_line, "= 32;"):
                    proto_line = proto_line.replace("NIDORAN", "NIDORAN_MALE")

            if proto_name == "HoloBadgeType" and not operator.contains(proto_line, "{") and not operator.contains(
                    proto_line, "}") and operator.contains(proto_line, "HOLO_BADGE_TYPE_"):
                proto_line = proto_line.replace("HOLO_BADGE_TYPE_", "")

            if proto_name == "BattleHubSection" and not operator.contains(proto_line, "{") and not operator.contains(
                    proto_line, "}") and operator.contains(proto_line, "BATTLE_HUB_SECTION_"):
                proto_line = proto_line.replace("BATTLE_HUB_SECTION_", "")

            if proto_name == "HoloPokemonMove" and not operator.contains(proto_line, "{") and not operator.contains(
                    proto_line, "}") and operator.contains(proto_line, "HOLO_POKEMON_MOVE_"):
                proto_line = proto_line.replace("HOLO_POKEMON_MOVE_", "").replace("MOVE_UNSET",
                                                                                  "V0000_MOVE_NOMOVE")
                proto_line = proto_line.replace(proto_line.split("_MOVE_")[0].strip(), "").replace("_MOVE_",
                                                                                                   "")

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
                # proto_name = ''

    ## check messages first
    proto_name = ''
    messages_dic = {}
    for proto_line in messages.split("\n"):
        if is_blank(proto_line):
            continue
        if operator.contains(proto_line, "message ") or operator.contains(proto_line, "enum ") or operator.contains(
                proto_line, "oneof ") and operator.contains(
            proto_line, "{"):
            proto_name = proto_line.split(" ")[1].strip()
        if proto_line == '':
            continue
        if operator.contains(proto_line, " result =") and len(
                proto_line.split(" ")[0].strip()) == 11 and proto_line.split(" ")[0].strip().isupper():
            messages_dic.setdefault(proto_line.split(" ")[0].strip(), "Result")
        elif operator.contains(proto_line, " status =") and len(
                proto_line.split(" ")[0].strip()) == 11 and proto_line.split(" ")[0].strip().isupper():
            messages_dic.setdefault(proto_line.split(" ")[0].strip(), "Status")
        elif operator.contains(proto_line, "CHARACTER_BLANCHE = 1;") and len(proto_name) == 11 and proto_name.isupper():
            messages_dic.setdefault(proto_name, "InvasionCharacter")

        if operator.contains(proto_line, "{") and len(proto_name) == 11 and proto_name.isupper():
            if operator.contains(proto_line, "oneof "):
                print("OneOf: " + proto_name)
            elif operator.contains(proto_line, "message "):
                print("Message: " + proto_name)
            else:
                print("Enum: " + proto_name)

    ## fix messages names
    # print("Cleaning process on messages...")
    for _message in messages_dic:
        # print("Obfuscated message name " + _message + " clean message name " + messages_dic[_message])
        messages = messages.replace(_message, messages_dic[_message])

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
    shutil.copy(generated_file, protos_path + '/v0.' + version + '.proto')
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
