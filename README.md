<!-- define variables -->
[1.1]: http://i.imgur.com/M4fJ65n.png (ATTENTION)

POGOProtos [![Build Status](https://travis-ci.org/Furtif/POGOProtos.svg?branch=master)](https://travis-ci.org/Furtif/POGOProtos) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/rocketbot) <!-- [![Maintainability](https://api.codeclimate.com/v1/badges/f4fbd03daa49a667d1b7/maintainability)](https://codeclimate.com/github/Furtif/POGOProtos/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/f4fbd03daa49a667d1b7/test_coverage)](https://codeclimate.com/github/Furtif/POGOProtos/test_coverage)-->
===================

![alt text][1.1] <strong><em>`The contents of this repo are a proof of concept and are for educational use only`</em></strong>![alt text][1.1]<br/>

This repository contains the [ProtoBuf](https://github.com/google/protobuf) `.proto` files needed to decode the PokémonGo RPC.

### ![alt text][1.1] NOTE: All content of folder ```./src/*``` is deprecated ![alt text][1.1]

##### Recommend using the base [Rpc](https://github.com/Furtif/POGOProtos/blob/master/src/POGOProtos/Rpc/Rpc.proto)
####### NOTE: ```compile_src.py cpp``` works but uses POGOProtos.Rpc.*
### Versioning
We are following [semantic versioning](http://semver.org/) for POGOProtos.  Every version will be mapped to their current PokémonGo version.

| Version      | Base           | Notes           | Extra                           |
|--------------|---------------|-----------------|---------------------------------|
| 2.52.3       |  [v0.183.0](https://github.com/Furtif/POGOProtos/blob/master/base/v0.183.0_obf.proto)       | Obfuscated      |  Protocol Buffers v3.12.3       |
| 2.52.2       |  [v0.181.0](https://github.com/Furtif/POGOProtos/blob/master/base/v0.181.0.proto)       | Compatible      |  Protocol Buffers v3.12.3       |

### Usage
If you want to figure out the current version in an automated system, use this file.
[.current-version](https://github.com/Furtif/POGOProtos/raw/master/.current-version)
*Note: This file will contain pre-release versions too.*

### Preparation
Current recommended protoc version: "Protocol Buffers v3.12.3".
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

```
python compile_base.py -l cpp -1 -k:
 - raw_protos.proto -> out/single_file/cpp/POGOProtos.Rpc.desc
 -                  -> out/single_file/cpp/POGOProtos.Rpc.pb.cc
 -                  -> out/single_file/cpp/POGOProtos.Rpc.pb.h
 -                  -> out/single_file/cpp/POGOProtos.Rpc.proto
```

### Libraries
If you don't want to compile POGOProtos but instead use it directly, check out the following repository.

| Additional resources  | Source                                                                               | Status 
|-----------------------|--------------------------------------------------------------------------------------|--------
| Gamemaster Json       | https://github.com/pokemongo-dev-contrib/pokemongo-game-master                       |  OK    

### Code sources initial
- https://github.com/AeonLucid/POGOProtos
- https://github.com/pogosandbox/pogo-protos
