## start in development mode
```bash
$ vagrant up
$ vagrant ssh
$ django-runserver
```

## provision the vm
(clean geoserver data directory and postgres databases)

```bash
$ vagrant provision
```
rerun the steps to start in development mode.

## setup for maploom development

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

uncomment the following line in the Vagrantfile
```
# config.vm.synced_folder "../MapLoom", "/MapLoom"
```

provision the vm
```bash
$ vagrant provision
```

```bash
$ vagrant ssh
$ dev/setup_maploom_dev.sh
$ django-collectstatic
```
__Note:__  each time you provision the vm, you will need to rerun the last steps above.

## manage exchange services

```bash
$ sudo service exchange {start | stop | restart}
```
## logs
```
/vagrant/dev/.logs/
|
├─── geoserver_error.log    <-- geoserver error log
├─── geoserver.log          <-- geoserver stdout log
├─── supervisor.log         <-- process that runs geoserver log
```
