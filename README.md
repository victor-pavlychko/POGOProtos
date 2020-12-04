<!-- define variables -->
[1.1]: http://i.imgur.com/M4fJ65n.png (ATTENTION)

POGOProtos [![Build Status](https://travis-ci.org/Furtif/POGOProtos.svg?branch=master)](https://travis-ci.org/Furtif/POGOProtos) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/rocketbot) <!-- [![Maintainability](https://api.codeclimate.com/v1/badges/f4fbd03daa49a667d1b7/maintainability)](https://codeclimate.com/github/Furtif/POGOProtos/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/f4fbd03daa49a667d1b7/test_coverage)](https://codeclimate.com/github/Furtif/POGOProtos/test_coverage)-->
===================

![alt text][1.1] <strong><em>`The contents of this repo are a proof of concept and are for educational use only`</em></strong>![alt text][1.1]<br/>

This repository contains the [ProtoBuf](https://github.com/google/protobuf) `.proto` files needed to decode the PokémonGo RPC.

<!--
### ![alt text][1.1] NOTE: All content of folder ```./src/*``` except the ```./src/Rpc``` ``(obfuscated)`` folder is deprecated ![alt text][1.1]

 * **Recommend using the base [Rpc](https://github.com/Furtif/POGOProtos/blob/master/src/POGOProtos/Rpc/Rpc.proto)**
 * **NOTE:** (__*old ```compile.py``` has a new name: ```compile_src.py```*__) works but uses ```POGOProtos.Rpc.*```
-->

### Versioning
We are following [semantic versioning](http://semver.org/) for POGOProtos.  Every version will be mapped to their current PokémonGo version.

| Version      | Base                                                                                                      | Notes                  | Extra                           |
|--------------|-----------------------------------------------------------------------------------------------------------|------------------------|---------------------------------|
| 2.53.1       |  [v0.191.2](https://github.com/Furtif/POGOProtos/blob/master/base/v0.191.2.proto)                         | Compatible   |  Protocol Buffers v3.14.0     |
| 2.53.0       |  [v0.191.2](https://github.com/Furtif/POGOProtos/blob/master/base/v0.191.2.proto)                         | Compatible (rpc only)  |  This version cant not uses base/raw* but uses [base/v0.191.2.proto](https://github.com/Furtif/POGOProtos/commit/3f861094397e86ab11194abae62a3fd1a1969589)      |
| 2.52.9       |  [v0.191.0](https://github.com/Furtif/POGOProtos/blob/master/base/v0.191.0_obf.proto)                     | Obfuscated (auto clean test) |  Protocol Buffers v3.13.0       |
| 2.52.7       |  [v0.187.x](https://github.com/Furtif/POGOProtos/blob/master/base/v0.187.1_semi_deobfuscated.proto)       | 3/4 cleanned    |  Protocol Buffers v3.13.0       |
| 2.52.2       |  [v0.181.0 __* ( or ``base.proto``) *__ ](https://github.com/Furtif/POGOProtos/blob/master/base/base.proto)         | Compatible             |  Protocol Buffers v3.13.0       |

### Usage
If you want to figure out the current version in an automated system, use this file.
[.current-version](https://github.com/Furtif/POGOProtos/raw/master/.current-version)
*Note: This file will contain pre-release versions too.*

### Preparation
Current recommended protoc version: "Protocol Buffers v3.14.0".
You can find download links [here](https://github.com/google/protobuf/releases).

#### Windows
Be sure to add `protoc` to your environmental path.

#### *nix
Ensure that you have the newest version of `protoc` installed.

#### OS X
Use `homebrew` to install `protobuf ` with `brew install --devel protobuf`.

### Compilation
The compilation creates output specifically for the target language, i.e. respecting naming conventions, etc.  
This is an example of how the generated code will be organized:

##### Compile last raw

 * _Note: the *.desc file is auto created in this function_

```
python compile_base.py -l cpp -1 -k:
 - v0.191.2.proto -> out/single_file/cpp/POGOProtos.Rpc.desc
 -                -> out/single_file/cpp/POGOProtos.Rpc.pb.cc
 -                -> out/single_file/cpp/POGOProtos.Rpc.pb.h
 -                -> out/single_file/cpp/POGOProtos.Rpc.proto
```
### Compile src with rpc

 * ``` python compile_base.py -g -r -1 ``` *(Generate new Rpc.proto)*
 * ``` python compile_src.py cpp``` __*[Optional*__ *--include_imports --include_source_info --generate_desc*__*]*__

### Addons as json

| Additional resources   | Source                                                                               | Status 
|------------------------|--------------------------------------------------------------------------------------|--------
| [V2_GAME_MASTER](https://github.com/Furtif/POGOProtos/tree/master/GM/v2_GAME_MASTER.json) | Root                                   |  OK    
| [GAME_MASTER](https://github.com/Furtif/POGOProtos/tree/master/GM/GAME_MASTER.json) | Root                                   |  OK    
| [ASSET_DIGEST](https://github.com/Furtif/POGOProtos/tree/master/GM/ASSET_DIGEST.json) | Root                                   |  OK    

### Code sources initial and credits
- [AeonLucid](https://github.com/AeonLucid/POGOProtos)
