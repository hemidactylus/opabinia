# Opabinia

A system to count people entering/exiting a room,
made with a Raspberry Pi, a proximity sensor, some software and lots of love.

## Overview

<img src="app/static/images/opabinia.png" alt="Logo" style="width: 40%;"/>

Proximity sensors (HC-SR04), attached to a Raspberry Pi, track the passage of people in front of it;
software running on the RPi keeps the counts and offers, in the local network, a simple Web interface
to keep an eye on the counts.

## Ingredients

### Required material

Opabinia is made with the following hardware (CHECK DETAILS):
  - a Raspberry Pi 2 B Quad Core CPU 900 MHz, 1 GB RAM
  - a RPi case for aesthetics
  - a microSD card with at least 4 GB space
  - an 802.11g/b/n USB dongle (for WiFi connectivity)
  - two proximity sensors of type HC-SR04
  - three LEDs
  - resistors: 3 x 2.2k, 1 x 4.7k, 1 x 3.3k
  - wiring
  - some kind of breadboard, e.g. a 8 x 12cm double side prototype pcb breadboard

### Schematics

The schematics are as follows (CHECK TO DO):

<img src="app/static/images/opabinia.png" alt="Logo" style="width: 40%;"/>

### Software components

The collected data goes to a sqlite database file: the measurement service, which wraps
a Python script (that runs as `root`), writes to it when it detects some events through
the sensors; the web application (running as user `pi`) reads from it and prepares the data
for the web UI.

The web application is a Python Flask application, served by `nginx` through the `uWSGI`
reverse proxy; it is made available in the local network (if the router policies allow
for it and the magic of `DHCP` works).

Additionally, provided the Avahi daemon on the RPi plays nice with the local network,
the app becomes available not only as `http://IP_ADDRESS/`, but also at the address
[`http://pimpa.local/`](http://pimpa.local). _Disclaimer_ : for reasons still unclear to
me, this sometimes works and sometimes doesn't, in a rather whimsical way. In the
worst case one can issue a portscan command and figure out the local IP address
of the RPi, whose ssh port 22 is open: that is, with the proper CIDR range for the
local network,

    nmap -p 22 --open -sV 192.168.1.0/24

## Software Installation

### Setting up and provisioning the RPi

Get (and unzip) the image of a Raspbian build for burning onto the SD card.
To save on disk space,
mind that [RaspbianLite](https://www.raspberrypi.org/downloads/raspbian/)
is enough (here it is assumed that Raspbian Stretch Lite is used, which
uses systemd; for older builds, based on systemv, see the note below). Once in possession
of the image, for instance `2017-11-29-raspbian-stretch-lite.img`, burn it from the
PC (without messing up the destination device name, please):

    sudo dd bs=4M if=2017-11-29-raspbian-stretch-lite.img of=/dev/mmcblk0  status=progress conv=fsync

To enable ssh access right from the start, create a file called `ssh` (no extension)
in the root folder of the boot partition of the newly-burned card, as suggested
[here](https://hackernoon.com/raspberry-pi-headless-install-462ccabd75d0).

Connect the RPi to the router with a network cable, insert the SD card into the
slot and turn it on. If the DHCP lease went through, the machine's IP address
can be found either by looking at the lease list in the router's interface
or with (a suitably adapted version of) the `nmap` command given above.

Connect via `ssh` to the RPi. _Note_: in some cases one has to purge
old ssh keys from the `known_hosts` file on the PC (as suggested by the
ssh command). Also, if connecting through the `.local` domain, sometimes
the Avahi domain name of a previous lease on the same IP may linger around
for a little while (e.g. in the router lease list).

Once on a shell in the RPi, complete the configuration with the CLI tool

    raspi-config

The following operations are suggested:
  - __changing the password for user `pi`__
  - choosing to login through CLI (as opposed to "already connected on startup")
  - setting the locale (sometimes unknown-locale errors persist, no big deal)
  - in the Advanced settings, choosing to expand the filesystem to fill up all available space
    (which happens on the next reboot)
  - setting the hostname of the RPi (this is important for Avahi. In the following
    it is assumed the hostname `pimpa`
  - setting the 802.11b/g/n networking. Either through `raspi-config` or as explained in next
    paragraph

As for the network configuration, assuming the WiFi USB dongle is plugged in and ackowledged
by the RPi, add a block to the file `/etc/wpa_supplicant/wpa_supplicant.conf` similar to:

    network={
        ssid="testing"
        psk=131e1e221f6e06e3911a2d11ff2fac9182665c004de85300f9cac208a6a80531
    }

where, as detailed [here](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md),
the `psk` value is the result of running `wpa_passphrase SSID PASSWORD`.

Finally, to make all next steps easier, inject the ssh public key of the PC
to the `authorized_keys` file on the RPi.

Now update the RPi system and install some needed software. _Disclaimer_: no virtualenvs
are used in the Python part of Opabinia. This, although a bit contrary to a general sense
of tidiness, avoids a bit of hassle withouth much collateral damage,
considering this machine will probably be dedicated to Opabinia.

    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install nginx

    sudo apt-get install python-pip

    sudo pip install Flask
    sudo pip install uwsgi
    sudo pip install pytz
    sudo pip install flask_bootstrap

Finally, install (as described [here](https://www.raspberrypi.org/forums/viewtopic.php?f=32&t=103752))
the [`pigpiod`](http://abyz.me.uk/rpi/pigpio/pigpiod.html) package by Joan, making it also into a service:

      sudo apt-get install pigpio
      sudo systemctl enable pigpiod.service

### Installing and configuring Opabinia

First clone this repo (or rsync it over) so that there is
the directory `/home/pi/web/Opabinia/` on the RPi.
Make sure `measurer.py` and `wsgi_run.py` are given execute
permission (CHECK), the former in particular for all users.

To set up the web app so that nginx acts as a reverse proxy to it: copy the
site file `Doc/nginx/site-opabinia` into `/etc/nginx/sites-available`,
__remembering to adapt its `server_name` line to the RPi's network configuration__, and
make a symlink thereto in `/etc/nginx/sites-enabled`; also replace (CHECK)
the provided `/etc/nginx/nginx.conf` with the one found
in `Doc/nginx/nginx.conf`. Finally, delete (CHECK) the `default` file found
in `etc/nginx/sites-enabled`.

_Now this would be a good moment to wire up the circuitry as
shown in the schematics above.
This should be made with the RPi powered off._

To set up both the Flask app and the measurer as system services,
the following two files must be copied into `/etc/systemd/system/`:

    /Doc/systemd/opawebapp.service
    /Doc/systemd/opacounter.service

To start the services:

    sudo systemctl start opawebapp
    sudo systemctl start opacounter

and finally to make them start at each reboot:

    sudo systemctl enable opawebapp
    sudo systemctl enable opacounter

_Note_: these instructions for the system services assume systemd is the init daemon:
in other cases, similar instructions apply, see the note below for Wheezy.

__Sensor configuration__: in most cases, the only settings that might require
some tuning are the `timeZone` in `config.py`
(refer to [`pytz`](https://pypi.python.org/pypi/pytz) for details on this)
and the range of distances triggering a positive detection:
the latter are set (in meters) by changing the two-element array `sensorDistanceRange`
in file `app/config.py` (after which `opacounter` shall be restarted).

### Notes and Caveats

__DB access__: if the FIRST task to run, which created the DB, is the measurer `opacounter`,
the database file is owned by `root`, which is a problem.
Make sure it is `pi:www-data`, either through `chown` or simply by first starting the web app
`opawebapp` after deleting `Opabinia/app/database/opabinia.db`.

### In case of Wheezy Raspbian

On older Raspbian builds (i.e. Wheezy), the systemd part is replaced by systemV scripts.
Sample scripts, replacing the systemd ones, are provided in the `Doc/systemV` directory
(make sure they are made executable with `chmod u+x`).

### Relevant links
  
[Setting up a python Flask web-app on a RPi with uWSGI and Python](https://iotbytes.wordpress.com/python-flask-web-application-on-raspberry-pi-with-nginx-and-uwsgi/)

[SystemV init scripts](https://blog.frd.mn/how-to-set-up-proper-startstop-services-ubuntu-debian-mac-windows/)
