# Source CentOS configs
if [ -f /etc/bashrc ]; then
  . /etc/bashrc
fi
# Don't exit the interactive shell (i.e. docker exec session) on first error
set +e
