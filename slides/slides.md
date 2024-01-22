---
title: Image Builder
theme: solarized
separator: <!--s-->
verticalSeparator: <!--v-->
revealOptions:
  transition: none
---

# Image Builder

building up-to-date, customised operating system images the easy way

<!--v-->-

# Why?

- Building bootable operating system images isn't **that** hard, but:
  - how to do it consistently and reliably
  - how to do it for all possible target platforms (in a nice way)

Note:

It's not that hard until you need one for different purposes, different targets, different
architectures, AWS, GCP, Azure.

Now cloud platforms ofr instances often offer their own workflow to build images for their platform,
but vendor lock-in.

TODO compare with other build tools?

<!--s-->

## OSBuild

- Takes as input a manifest
  - Divided into pipelines and stages
- Produces the actual disk images

- The image build happens inside of a buildroot container:
  - one pipeline for the buildroot
  - the rest for the image

<small>let's take a look at a manifest...</small>

<!-- <table style="font-size: 0.5em"> -->
<!--     <tr> -->
<!--         <td rowspan="3"><b>OSBuild</b></td> -->
<!--         <td rowspan="3">Composer</td> -->
<!--         <td>Weldr client (cli)</td> -->
<!--     </tr> -->
<!--     <tr> -->
<!--         <td>Cockpit composer plugin</td> -->
<!--     </tr> -->
<!--     <tr> -->
<!--         <td>Hosted service</td> -->
<!--     </tr> -->
<!-- </table> -->



<!-- | OSBuild | Composer | Composer-CLI -->

<!--v-->

OSBuild Manifest
```json
{
  "version": "2",
  "pipelines": [
    {
      "runner": "org.osbuild.fedora38",
      "name": "build",
      "stages": [
        {
          "type": "org.osbuild.rpm",
          "inputs": {...}
        },
        {
          "type": "org.osbuild.selinux",
          "options": {...}
        }
      ]
    },
    {
      "name": "os",
      "build": "name:build",
      "stages": [
        {
          "type": "org.osbuild.kernel-cmdline",
          "options": {
            "root_fs_uuid": "6e4ff95f-f662-45ee-a82a-bdf44a2d0b75",
            "kernel_opts": "ro no_timer_check console=ttyS0,115200n8 biosdevname=0 net.ifnames=0"
          }
        },
        {
          "type": "org.osbuild.rpm",
          "inputs": {...},
          "options": {...}
        },
        {
          "type": "org.osbuild.fix-bls",
          "options": {...}
        },
        {
          "type": "org.osbuild.locale",
          "options": {...}
        },
        {
          "type": "org.osbuild.hostname",
          "options": {...}
        },
        {
          "type": "org.osbuild.timezone",
          "options": {...}
        },
        {
          "type": "org.osbuild.fstab",
          "options": {...}
        },
        {
          "type": "org.osbuild.grub2",
          "options": {...}
        },
        {
          "type": "org.osbuild.systemd",
          "options": {...}
        },
        {
          "type": "org.osbuild.test",
          "options": {...}
        },
        {
          "type": "org.osbuild.selinux",
          "options": {...}
        }
      ]
    },
    {
      "name": "image",
      "build": "name:build",
      "stages": [
        {
          "type": "org.osbuild.truncate",
          "options": {...}
        },
        {
          "type": "org.osbuild.sfdisk",
          "options": {...},
          "devices": {...}
        },
        {
          "type": "org.osbuild.mkfs.fat",
          "options": {...},
          "devices": {...}
        },
        {
          "type": "org.osbuild.mkfs.ext4",
          "options": {...},
          "devices": {...}
        },
        {
          "type": "org.osbuild.mkfs.ext4",
          "options": {...},
          "devices": {...}
        },
        {
          "type": "org.osbuild.copy",
          "inputs": {...},
          "options": {...}
          "devices": {...},
          "mounts": [...]
        },
        {
          "type": "org.osbuild.grub2.inst",
          "options": {...}
        }
      ]
    }
  ],
  "sources": {...}
}
```
<small><b>Caveat</b>: OSBuild isn't aware of what makes up a specific distribution.</small>

Note:
The core input of osbuild
Stages, ...

<!--s-->

## Composer:
- defines what makes up a specific distribution
- houses a matrix of:
  - distributions
  - target platforms
  - user customisations
- ultimately generates the manifest from user input

Note:
Defines the policies around the images

<!--v-->

### User input:
```
{
  "distribution": "fedora-39",
  "image_requests": [
    {
      "architecture": "x86_64",
      "image_type": "qcow2",
      "repositories": [{
        "baseurl": "https://mirrors.fedoraproject.org/metalink?repo=fedora-39&arch=x86_64",
        "rhsm": false
      }, {
        "baseurl": "https://mirrors.fedoraproject.org/metalink?repo=updates-released-f39&arch=x86_64",
        "rhsm": false
      }, {
        "baseurl": "https://mirrors.fedoraproject.org/metalink?repo=fedora-modular-39&arch=x86_64",
        "rhsm": false
      },
      {
        "baseurl": "https://mirrors.fedoraproject.org/metalink?repo=updates-released-modular-f39&arch=x86_64",
        "rhsm": false
      }]
    }
  ],
  "customizations": {
    "packages": [
      "test"
    ],
  }
}
```

<!--s-->

## The fluff on top

On how to make this easy

<!--v-->

### CLI

A blueprint as input:
```toml
name = "second-disk"

[[customizations.files]]
path = "/etc/systemd/system/prepare-data-disk.service"
data = """
[Unit]
Description=Prepare the data disk during the first boot
ConditionPathExists=!/var/lib/prepare-data-disk-first-boot

[Service]
Type=oneshot
ExecStart=mkfs.ext4 /dev/sdb
ExecStart=mkdir /mnt/data
ExecStart=mount /dev/sdb /mnt/data
ExecStart=bash -c "echo '/dev/sdb /mnt/data ext4 defaults 0 2' >>/etc/fstab"
ExecStartPost=touch /var/lib/prepare-data-disk-first-boot

[Install]
WantedBy=default.target
"""

[customizations.services]
enabled = ["prepare-data-disk"]

[[customizations.user]]
name = "user"
groups = ["wheel"]
key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPB1jFl4p6FTBixHT6wOk6X8nj/Z7eoPNQE/M0wK485K ondrej@budai.cz"
```
<small>sourced from https://budai.cz/posts/2023-07-18-first-boot-automation-in-image-builder/</small>

<!--v-->

### CLI

```toml
# Push the blueprint
$ composer-cli blueprints push second-disk.toml

# Start a qcow2 build
$ composer-cli compose start second-disk qcow2
Compose 14107a91-edbd-419b-820a-cb813f8063d6 added to the queue

# Wait for the build to finish
$ composer-cli compose list | grep 14107a91-edbd-419b-820a-cb813f8063d6
14107a91-edbd-419b-820a-cb813f8063d6   RUNNING    second-disk   0.0.1     qcow2

# ...
$ composer-cli compose list | grep 14107a91-edbd-419b-820a-cb813f8063d6
14107a91-edbd-419b-820a-cb813f8063d6   FINISHED   second-disk   0.0.1     qcow2

# Download the image
$ composer-cli compose image 14107a91-edbd-419b-820a-cb813f8063d6 --filename image.qcow2
```
<small>sourced from https://budai.cz/posts/2023-07-18-first-boot-automation-in-image-builder/</small>

<!--v-->

### <a href="https://localhost:9091/composer" target="_blank">Cockpit composer</a>

<!--v-->

### Fedora hosted service!

Demo:

```json
{
  "image_name": "guest-image",
  "distribution": "fedora-38",
  "image_requests": [
    {
      "architecture": "x86_64",
      "image_type": "guest-image",
      "upload_request": {
        "type": "aws.s3",
        "options": {}
      }
    }
  ],
  "customizations": {
    ""
    "packages": [
      ""
    ],
    "payload_repositories": [
      {
        "baseurl": "https://cdn.redhat.com/content/dist/layered/rhel8/x86_64/satellite/6.14/os",
        "check_gpg": false,
        "check_repo_gpg": false,
        "rhsm": true,
        "module_hotfixes": true
      }
    ]
  }
}
```


Note:
Service

Fedora service!
