SynnefoSSH
==========

SynnefoSSH is a command-line tool in order to easily
perform SSH to VMs in [Synnefo](http://www.synnefo.org)
deployments.

About
-----

SynnefoSSH is using [kamaki](http://www.synnefo.org/docs/kamaki/latest/)
library to translate the name of the virtual server to server's hostname,
user and ssh port. Name resolution is performed to all available *Synnefo*
cloud services.


Configuration
-------------

The tool is using the default *kamaki* configuration file `.kamakirc`
to retrieve the available
[clouds](http://www.synnefo.org/docs/kamaki/latest/setup.html#multiple-clouds).

Basic Usage
-----------

##### List available servers

```bash

$ synsh --list
-------------
cloud:okeanos
-------------
dev1
dev2
mail

-----------
cloud: demo
-----------
dev2
```
##### Connect to server
```bash

$ synsh dev1
Connecting to Virtual Server 'dev' at cloud 'okeanos'
IPv4: 192.168.2.2
User: root
SSH command: ssh root@192.168.2.2
```

##### Connect to specific cloud

You can restrict the lookup in a specific cloud by adding
the cloud name after the server name:
`$ synsh dev2.demo`

Also, you can override the user:
`$ synsh user@dev2.demo`
