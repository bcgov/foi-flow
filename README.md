[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Lifecycle:Experimental](https://img.shields.io/badge/Lifecycle-Experimental-339999)](https://github.com/bcgov/repomountie/blob/master/doc/lifecycle-badges.md)

## foi-flow
Freedom of Information modernization. 

## Features

## Usage

## Requirements

## Installation

### For mac
1. Clone this repo
2. Copy the .env file to the root folder of entire repo
3. Change docker-compose.yml line 152 from windows.Dockerfile to mac.Dockerfile

#### Add IP address to hosts on local system if accessing remotely
1. Log into vpn
2. Click statistics icon (bottom left of AnyConnect, the graph icon)
3. Note down client address (IPv4)
4. In your terminal run the command ``` sudo nano /etc/hosts ```
5. Add the ip address from above to the list, with alias value ``` foiflow.local ```
6. Save and exit

## Project Status
The project is in the very early stages of development. The codebase will be changing frequently.

## Goals/Roadmap

## Getting Help or Reporting an Issue
To report bugs/issues/feature requests, please file an [issue.](https://github.com/bcgov/foi-flow/issues)

## How to Contribute

If you would like to contribute, please see our [contributing](CONTRIBUTING.md)
guidelines. Please note that this project is released with a
[Contributor Code of Conduct](CODE-OF-CONDUCT.md). By participating in this
project you agree to abide by its terms.

## License

    Copyright 2021 Province of British Columbia

    Licensed under the Apache License, Version 2.0 (the "License"); you may not
    use this file except in compliance with the License. You may obtain a copy
    of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.
