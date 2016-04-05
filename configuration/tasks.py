import os
import signal
import sys

from invoke import run as silentrun, task
from six import iteritems
from colorama import init as colorama_init, Fore

colorama_init()

PORT = os.environ.get('DEV_PORT', 8080)
LOCAL_DIR = os.environ.get('DEV_LOCAL_DIR', '/home/vagrant/vrcloud')
CONTAINER_DIR = os.environ.get('DEV_CONTAINER_DIR', '/vrcloud')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'cloudspeaker')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'cloudspeaker')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'cloudspeaker')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
PGDATA = os.environ.get('PGDATA', '/var/lib/postgres/data/tmp')
RAMDISK_SIZE = os.environ.get('POSTGRES_RAM', '512M')


def run(cmd, **kwargs):
    """
    It's just like invoke run, but it displays the command it's running as it runs it.
    """
    print(Fore.RESET)
    if 'pty' in kwargs and kwargs['pty']:
        print(cmd)
        return silentrun(cmd, **kwargs)
    print(Fore.GREEN)
    print(cmd)
    print(Fore.CYAN)
    return silentrun(cmd, **kwargs)


def docker_vars(vars_dict):
    """
    Convert a Python Dictionary to a string of variables that can be passed to Docker

    >>> docker_vars({'a':12, 'b':"helf", 'c':"wango"})
    '-e a="12" -e b="helf" -e c="wango"'
    """
    almost = " -e ".join(["{}=\"{}\"".format(key, value) for key, value in sorted(iteritems(vars_dict))])
    return "-e " + almost


def docker_ip():
    """
    Get the docker IP
    """
    result = run("ifconfig | grep docker0 -A1 | grep 'inet addr'")
    ip = [x for x in str(result.stdout).split(" ") if x.startswith("addr:")][0][5:]
    return ip


@task
def env():
    """
    Dump the environment to stdout
    """
    for key, value in iteritems(os.environ):
        print(key, value)


@task
def dev_install():
    """
    Prep the docker images we'll be developing on.
    """
    run('sudo docker pull postgres')
    run('sudo docker pull redis')
    run('sudo docker build -t django-dev .')
    run('echo "inv(){ pushd /home/vagrant/configuration && invoke $1 $2 $3 $4 $5 $6 && popd; }" >> ~/.bashrc')
    run("""echo "dj(){ pushd /home/vagrant/configuration && invoke manage '$1 $2 $3 $4 $5' && popd; }" >> ~/.bashrc""")


@task
def boot_postgres():
    """
    Creates a temporary RAMdisk for Postgres data, then boots a Postgres image.
    This image is for dev only - using a RAMdisk for Postgres in production is a Bad Idea.
    """
    postgres_args = {'POSTGRES_PASSWORD': POSTGRES_PASSWORD,
                     'POSTGRES_USER': POSTGRES_USER,
                     'POSTGRES_DB': POSTGRES_DB,
                     'PGDATA': PGDATA,
                     'RAMDISK_SIZE': RAMDISK_SIZE,
                     'POSTGRES_INITDB_ARGS': "--nosync"}

    run('sudo mkdir -p {}'.format(PGDATA))
    run('sudo mount -t tmpfs -o size={} tmpfs {}'.format(RAMDISK_SIZE, PGDATA))

    run(('docker run ' +
         '--name dev-postgres ' +
         '-p {port}:{port} ' +
         '{postgres_args} ' +
         '-d ' +
         'postgres ').format(port=POSTGRES_PORT,
                             postgres_args=docker_vars(postgres_args)))


@task
def kill_postgres():
    """
    Kills the postgres image, then unmounts the RAMdisk
    """
    run('docker stop dev-postgres', warn=True)
    run('docker rm dev-postgres', warn=True)
    run('sudo umount {}'.format(PGDATA), warn=True)


@task
def ps():
    """
    List all docker containers
    """
    run('docker ps -a')


@task
def recycle():
    """
    Clean up any unwanted images.
    """
    run('docker rm -v $(docker ps -a -q -f status=exited)', warn=True)
    run('docker ps -a')


@task
def manage(cmd):
    """
    Run manage.py interactively.
    """

    # Kill this container if it already exists
    run("docker kill django-manage", warn=True)
    run("docker rm django-manage", warn=True)

    # Intercept Ctrl-C and kill the container when we exit
    def intercept_sigint_and_kill_docker_container(*_):
        run("docker kill django-manage")
        run("docker rm django-manage")
        sys.exit(0)

    signal.signal(signal.SIGINT, intercept_sigint_and_kill_docker_container)

    run(("docker run " +
         "-p {port}:{port} " +
         "-v {local_dev_dir}:{container_dev_dir} " +
         "-w {container_dev_dir} " +
         "-i " +
         "-t " +
         "--rm " +
         "--name django-manage " +
         "-e POSTGRES_HOST='{postgres_host}' " +
         "django-dev " +
         "python3 manage.py {cmd} " +
         "").format(port=PORT,
                    postgres_host=docker_ip(),
                    local_dev_dir=LOCAL_DIR,
                    container_dev_dir=CONTAINER_DIR,
                    cmd=cmd), pty=True)


@task
def runserver():
    """
    Run the dev server!
    """
    manage("runserver 0.0.0.0:{port}".format(port=PORT))


@task
def makemigrations():
    """
    Make migrations
    """
    manage("makemigrations")
