import os

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


def run(cmd, *args, **kwargs):
    """
    It's just like invoke run, but it displays the command it's running as it runs it.
    """
    if 'pty' in kwargs and kwargs['pty']:
        return silentrun(cmd, *args, **kwargs)
    print(Fore.GREEN)
    print(cmd)
    print(Fore.CYAN)
    silentrun(cmd, *args, **kwargs)
    print(Fore.RESET)


def docker_vars(vars_dict):
    """
    Convert a Python Dictionary to a string of variables that can be passed to Docker

    >>> docker_vars({'a':12, 'b':"helf", 'c':"wango"})
    '-e a="12" -e b="helf" -e c="wango"'
    """
    almost = " -e ".join(["{}=\"{}\"".format(key, value) for key, value in sorted(iteritems(vars_dict))])
    return "-e " + almost


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

    run(('sudo docker run ' +
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
    run('sudo docker stop dev-postgres', warn=True)
    run('sudo docker rm dev-postgres', warn=True)
    run('sudo umount {}'.format(PGDATA), warn=True)


@task
def recycle():
    """
    Clean up any unwanted images.
    """
    run('sudo docker rm -v $(docker ps -a -q -f status=exited)', warn=True)
    run('sudo docker ps -a')

@task
def dev_shell():
    run(("sudo docker run " +
         "-p {port} " +
         "-v {local_dev_dir}:{container_dev_dir} " +
         "-w {container_dev_dir} " +
         "-i " +
         "-t " +
         "--rm " +
         "--name django-shell " +
         "django-dev " +
         "python3 manage.py shell " +
         "").format(port=PORT,
                    local_dev_dir=LOCAL_DIR,
                    container_dev_dir=CONTAINER_DIR), pty=True)


@task
def docker_ip():
    """
    Get the docker IP
    """
    run("ifconfig | grep docker0 | grep 'inet addr'")

@task
def runserver():
    """
    Run the dev server!
    """
    run(("sudo docker run " +
         "-p {port}:{port} " +
         "-v {local_dev_dir}:{container_dev_dir} " +
         "-w {container_dev_dir} " +
         "-i " +
         "-t " +
         "--rm " +
         "--name django-runserver " +
         "-e POSTGRES_HOST='' " +
         "django-dev " +
         "python3 manage.py runserver 0.0.0.0:8080 " +
         "").format(port=PORT,
                    local_dev_dir=LOCAL_DIR,
                    container_dev_dir=CONTAINER_DIR), pty=True)

    #run("sudo docker logs django-dev --follow", pty=True)
