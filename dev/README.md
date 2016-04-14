## start in development mode
```bash
$ vagrant up
$ vagrant ssh
$ cd /vagrant
$ dev/activate
$ python manage.py runserver 0.0.0.0:8000
```

## provision the vm
(clean geoserver data directory and postgres databases)

```bash
$ vagrant provision
```
rerun the steps to start in development mode.

## setup for maploom development

__Note:__  if you provisioned the vm, you will need to rerun these steps.

clone the maploom repo as a sibling of exchange-dev

Example:
```

parent_dir
|
├─── exchange
|        Vagrantfile
|
└─── MapLoom
```
Build MapLoom
```
$ cd MapLoom
$ sudo npm -g install grunt-cli karma bower
$ npm install
$ bower install
$ grunt watch
```

```bash
$ cd /vagrant
$ dev/setup_maploom_dev
```

## manage geoserver service

```bash
$ sudo service gs-dev {start | stop | restart}
```
## logs
```
/vagrant/dev/.django/
|
├─── geoserver_error.log    <-- geoserver error log
├─── geoserver.log          <-- geoserver stdout log
├─── supervisor.log         <-- process that runs geoserver log
```
