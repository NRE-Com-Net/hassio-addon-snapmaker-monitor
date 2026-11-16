# Home Assistant Add-on: Snapmaker Monitor

This add-on reads the status of a Snapmaker 2.0 (3D printer, laser and CNC)
from its HTTP API once a minute and sends it to Home Assistant. It can send the
status to a Home Assistant webhook, to an MQTT topic, or to both.

It is a refactored version of the [original script][original-script] by
[NiteCrwlr](https://github.com/NiteCrwlr).

## Installation

1. Click the button below to add the repository to your Home Assistant
   instance.

   [![Open this add-on in your Home Assistant instance.][addon-badge]][addon]

1. Install the "Snapmaker Monitor" add-on from the add-on store.
1. Set `sm_ip` to the IP address of your Snapmaker in the add-on
   configuration.
1. Set up a webhook or MQTT (see below), then start the add-on.
1. The first time the add-on connects, the Snapmaker asks on its touchscreen
   whether to allow the connection. Confirm it. The token is saved in the
   add-on's data folder and reused from then on.
1. Check the add-on log to see if everything went well.

## Receiving the status in Home Assistant

The example file [`SnapMaker-Monitor.yaml`][example] in the repository has
ready-to-use configuration for both ways. The easiest place for it is a
[package][packages], for example `packages/snapmaker.yaml`.

### Webhook

1. Copy the template sensor from the example into your configuration. It
   listens on the webhook ID `wh-snapmaker`.
1. Set `ha_webhook_id` to the same ID, for example `wh-snapmaker`.

The add-on sends the webhook through the Supervisor, so it reaches Home
Assistant as a local request and works with `local_only: true`.

### MQTT

If `mqtt_broker` is empty and no webhook is set, the add-on uses the MQTT
broker that Home Assistant provides, for example the Mosquitto broker add-on.
Nothing else needs to be configured. To use another broker, set
`mqtt_broker` and, if needed, `mqtt_user` and `mqtt_password`.

The status is published as a retained JSON message to `mqtt_topic`, so Home
Assistant gets the last known state after a restart. Copy the MQTT sensor from
the example into your configuration to use it.

## Starting and stopping

The add-on is set to start manually on purpose. When the Snapmaker is
unreachable, the add-on reports `UNAVAILABLE` and stops after about ten
minutes of retries. Start it when the printer is switched on, for example with
the automation in the example file, which starts and stops the add-on together
with the smart plug of the printer.

## Configuration

**Note**: _Remember to restart the add-on when the configuration is changed._

Example add-on configuration:

```yaml
log_level: info
sm_ip: 192.168.0.10
sm_port: 8080
ha_webhook_id: wh-snapmaker
mqtt_broker: ""
mqtt_port: 1883
mqtt_topic: snapmaker/status
mqtt_user: ""
mqtt_password: ""
```

**Note**: _This is just an example, don't copy and paste it! Create your own!_

### Option: `log_level`

The `log_level` option controls the level of log output by the add-on and can
be changed to be more or less verbose, which might be useful when you are
dealing with an unknown issue. Possible values are:

- `trace`: Show every detail, like all called internal functions.
- `debug`: Shows detailed debug information.
- `info`: Normal (usually) interesting events.
- `notice`: Normal but significant events.
- `warning`: Exceptional occurrences that are not errors.
- `error`: Runtime errors that do not require immediate action.
- `fatal`: Something went terribly wrong. Add-on becomes unusable.

Please note that each level automatically includes log messages from a
more severe level, e.g., `debug` also shows `info` messages. By default,
the `log_level` is set to `info`, which is the recommended setting unless
you are troubleshooting.

### Option: `sm_ip`

The IP address of your Snapmaker 2.0. This option is required. Give the
printer a fixed IP address in your router, so it does not change.

### Option: `sm_port`

The port of the Snapmaker 2.0 HTTP API. The default is `8080`.

### Option: `ha_webhook_id`

The ID of the webhook trigger in Home Assistant that receives the status, for
example `wh-snapmaker`. Leave it empty to disable the webhook.

### Option: `mqtt_broker`

The host name or IP address of the MQTT broker. Leave it empty to use the
broker that Home Assistant provides (only when no webhook is set).

### Option: `mqtt_port`

The port of the MQTT broker. The default is `1883`.

### Option: `mqtt_topic`

The topic the status is published to. The default is `snapmaker/status`.

### Option: `mqtt_user`

The username for the MQTT broker, if it needs authentication.

### Option: `mqtt_password`

The password for the MQTT broker.

## Upgrading from version 1.x

- The options `ha_token` and `ha_webhook_url` were replaced by
  `ha_webhook_id`. A long-lived access token is no longer needed, remove it
  from your configuration and revoke it in your Home Assistant profile.
- The webhook now sends real JSON instead of a JSON encoded string. Update
  your template sensor from the [example file][example]: use
  `trigger.json.status` instead of `(trigger.json | from_json)['status']`.
- 32-bit systems (armv7) are no longer supported, because the base image and
  Home Assistant itself dropped support for them.

## Changelog & Releases

This repository keeps a change log using [GitHub's releases][releases]
functionality.

Releases are based on [Semantic Versioning][semver], and use the format
of `MAJOR.MINOR.PATCH`. In a nutshell, the version will be incremented
based on the following:

- `MAJOR`: Incompatible or major changes.
- `MINOR`: Backwards-compatible new features and enhancements.
- `PATCH`: Backwards-compatible bugfixes and package updates.

## Support

Got questions?

You have several options to get them answered:

- The [add-on thread][forum] in the Home Assistant Community Forum.
- The [Home Assistant Discord chat server][discord-ha] for general Home
  Assistant discussions and questions.
- Join the [Reddit subreddit][reddit] in [/r/homeassistant][reddit]

You could also [open an issue here][issue] on GitHub.

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

[addon-badge]: https://my.home-assistant.io/badges/supervisor_addon.svg
[addon]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?addon=71611ba3_snapmaker-monitor&repository_url=https%3A%2F%2Fgithub.com%2FNRE-Com-Net%2Fhassio-addons
[contributors]: https://github.com/NRE-Com-Net/hassio-addon-snapmaker-monitor/graphs/contributors
[discord-ha]: https://discord.gg/c5DvZ4e
[example]: https://github.com/NRE-Com-Net/hassio-addon-snapmaker-monitor/blob/main/SnapMaker-Monitor.yaml
[forum]: https://community.home-assistant.io/t/home-assistant-add-on-snapmaker-monitor/916652?u=nemesisre
[issue]: https://github.com/NRE-Com-Net/hassio-addon-snapmaker-monitor/issues
[NemesisRE]: https://github.com/NemesisRE
[original-script]: https://github.com/NiteCrwlr/playground/blob/main/SNStatus/SNStatusV2.py
[packages]: https://www.home-assistant.io/docs/configuration/packages/
[reddit]: https://reddit.com/r/homeassistant
[releases]: https://github.com/NRE-Com-Net/hassio-addon-snapmaker-monitor/releases
[semver]: https://semver.org/spec/v2.0.0.html
