POGOProtos [![Build Status](https://travis-ci.org/Furtif/POGOProtos.svg?branch=master)](https://travis-ci.org/Furtif/POGOProtos) [![Maintainability](https://api.codeclimate.com/v1/badges/f4fbd03daa49a667d1b7/maintainability)](https://codeclimate.com/github/Furtif/POGOProtos/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/f4fbd03daa49a667d1b7/test_coverage)](https://codeclimate.com/github/Furtif/POGOProtos/test_coverage)  [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=SNATC29B4ZJD4)
===================

This repository contains the [ProtoBuf](https://github.com/google/protobuf) `.proto` files needed to decode the PokémonGo RPC.

If you want to know which messages are implemented right now, click [here](https://github.com/Furtif/POGOProtos/blob/master/src/POGOProtos/Networking/Requests/RequestType.proto).

#### Versioning

We are following [semantic versioning](http://semver.org/) for POGOProtos.  Every version will be mapped to their current PokémonGo version.

| Version      | Android       | iOS           | Extra                     |
|--------------|---------------|---------------|---------------------------|
| 2.32.0       | 0.117.2       | 1.87.2        |  Protocol Buffers v3.6.1  |

# Usage

If you want to figure out the current version in an automated system, use this file.

https://raw.githubusercontent.com/Furtif/POGOProtos/master/.current-version

*Note: This file will contain pre-release versions too.*

## Preparation

Current recommended protoc version: "Protocol Buffers v3.6.1".

You can find download links [here](https://github.com/google/protobuf/releases).

### Windows
Be sure to add `protoc` to your environmental path.

### *nix
Ensure that you have the newest version of `protoc` installed.

### OS X
Use `homebrew` to install `protobuf ` with `brew install --devel protobuf`.

## Compilation
The compilation creates output specifically for the target language, i.e. respecting naming conventions, etc.  
This is an example of how the generated code will be organized:

```
python compile.py cpp:
 - POGOProtos/Data/PlayerData.proto -> POGOProtos/Data/PlayerData.pb.cpp
```
```
python compile.py csharp:
 - POGOProtos/Data/PlayerData.proto -> POGOProtos/Data/PlayerData.g.cs
 ```
 ```
python compile.py go:
 - POGOProtos/Data/*.proto -> github.com/aeonlucid/pogoprotos/data
 - POGOProtos/Data/PlayerData.proto -> github.com/aeonlucid/pogoprotos/data/player_data.pb.go
```
```
python compile.py java:
 - POGOProtos/Data/*.proto -> com/github/aeonlucid/pogoprotos/Data.java
 ```
 ```
python compile.py js:
 - POGOProtos/**/*.proto -> pogoprotos.js
```
```
python compile.py objc:
 - POGOProtos/Data/PlayerData.proto -> POGOProtos/Data/PlayerData.pbobjc.m
```
```
python compile.py python:
 - POGOProtos/Data/*.proto -> pogoprotos/data/__init__.py
 - POGOProtos/Data/PlayerData.proto -> pogoprotos/data/player_data_pb2.py
```
```
python compile.py ruby:
 - POGOProtos/Data/*.proto -> pogoprotos/data.rb
 - POGOProtos/Data/PlayerData.proto -> pogoprotos/data/player_data.rb
```

## Extra information

 - Run ```python compile.py --help``` for help.
 - You can find all available languages here [https://github.com/google/protobuf](https://github.com/google/protobuf).

#### Libraries

If you don't want to compile POGOProtos but instead use it directly, check out the following repository.

| Language              | Source                                                         |
|-----------------------|----------------------------------------------------------------|
| NodeJS                | https://github.com/pogosandbox/pogobuf                         |
| NodeJS (pure JS)      | https://github.com/pogosandbox/node-pogo-protos                |
| .NET (nuget pack)     | https://www.nuget.org/packages/POGOProtos.Core                 |
| PHP                   | https://github.com/jaspervdm/pogoprotos-php                    |
| Go                    | https://github.com/pkmngo-odi/pogo-protos                      |
| Haskell               | https://github.com/relrod/pokemon-go-protobuf-types            |
| Rust                  | https://github.com/rockneurotiko/pokemon-go-protobuf-rs        |
| Java                  | https://github.com/pokemongo-dev-contrib/pogoprotos-java       |

| Additional resources  | Source                                                         |
|-----------------------|----------------------------------------------------------------|
| Gamemaster Json       | https://github.com/pokemongo-dev-contrib/pokemongo-game-master |

### CREDITS

 - [AeonLucid](https://github.com/AeonLucid)
 - [pogosandbox (niicojs)](https://github.com/pogosandbox)
 - [ZeChrales](https://github.com/ZeChrales)
