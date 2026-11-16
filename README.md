# Home Assistant Add-on: Snapmaker Monitor

[![GitHub Release][releases-shield]][releases] ![Project Stage][project-stage-shield] [![License][license-shield]](LICENSE.md)
![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield]
[![Github Actions][github-actions-shield]][github-actions] ![Project Maintenance][maintenance-shield] [![GitHub Activity][commits-shield]][commits]
[![Community Forum][forum-shield]][forum]
[![Sponsor NemesisRE via GitHub Sponsors][github-sponsors-shield]][github-sponsors]

## About

This add-on reads the status of a Snapmaker 2.0 (3D printer, laser and CNC)
from its HTTP API and sends it to Home Assistant via webhook or MQTT.

I refactored and modified the original [version][original-script] of the script from [NiteCrwlr](https://github.com/NiteCrwlr)

[:books: Read the full add-on documentation][docs]

## Support

Got questions?

You have several options to get them answered:

- The [Home Assistant Discord chat server][discord-ha] for general Home
  Assistant discussions and questions.
- The [add-on thread][forum] in the Home Assistant Community Forum.
- Join the [Reddit subreddit][reddit] in [/r/homeassistant][reddit]

You could also [open an issue here][issue] on GitHub.

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We have set up a separate document containing our
[contribution guidelines](.github/CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Authors & contributors

The original setup of this repository is by [Steven Kurz][NemesisRE].

For a full list of all authors and contributors,
check [the contributor's page][contributors].

## License

MIT License

Copyright (c) 2019-2026 Steven "NemesisRE" Kurz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/NRE-Com-Net/hassio-addon-snapmaker-monitor
[commits]: https://github.com/NRE-Com-Net/hassio-addon-snapmaker-monitor/commits/main
[contributors]: https://github.com/NRE-Com-Net/hassio-addon-snapmaker-monitor/graphs/contributors
[discord-ha]: https://discord.gg/c5DvZ4e
[docs]: https://github.com/NRE-Com-Net/hassio-addon-snapmaker-monitor/blob/main/snapmaker-monitor/DOCS.md
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg
[forum]: https://community.home-assistant.io/t/home-assistant-add-on-snapmaker-monitor/916652?u=nemesisre
[NemesisRE]: https://github.com/NemesisRE
[github-actions-shield]: https://github.com/NRE-Com-Net/hassio-addon-snapmaker-monitor/actions/workflows/deploy.yaml/badge.svg
[github-actions]: https://github.com/NRE-Com-Net/hassio-addon-snapmaker-monitor/actions
[github-sponsors-shield]: https://img.shields.io/github/sponsors/NemesisRE
[github-sponsors]: https://github.com/sponsors/NemesisRE
[issue]: https://github.com/NRE-Com-Net/hassio-addon-snapmaker-monitor/issues
[license-shield]: https://img.shields.io/github/license/NRE-Com-Net/hassio-addon-snapmaker-monitor
[maintenance-shield]: https://img.shields.io/maintenance/yes/2026.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-production%20ready-brightgreen.svg
[reddit]: https://reddit.com/r/homeassistant
[releases-shield]: https://img.shields.io/github/release/NRE-Com-Net/hassio-addon-snapmaker-monitor.svg
[releases]: https://github.com/NRE-Com-Net/hassio-addon-snapmaker-monitor/releases
[original-script]: https://github.com/NiteCrwlr/playground/blob/main/SNStatus/SNStatusV2.py
