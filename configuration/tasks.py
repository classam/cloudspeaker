import os
import signal
import sys
import time

from invoke import run as silentrun, task
from six import iteritems
from colorama import init as colorama_init, Fore

colorama_init()
sys.stderr.write(Fore.RED)

PORT = os.environ.get('DEV_PORT', 8080)
LOCAL_DIR = os.environ.get('DEV_LOCAL_DIR', '/home/vagrant/vrcloud')
CONTAINER_DIR = os.environ.get('DEV_CONTAINER_DIR', '/vrcloud')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'cloudspeaker')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'cloudspeaker')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'cloudspeaker')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', 5432)
PGDATA = os.environ.get('PGDATA', '/var/lib/postgres/data/tmp')
RAMDISK_SIZE = os.environ.get('POSTGRES_RAM', '512M')


def section(text):
    """
    Some text we want to print between major actions.
    """
    sys.stdout.write(Fore.CYAN)
    print(text)
    sys.stdout.write(Fore.RESET)


def run(cmd, **kwargs):
    """
    It's just like invoke run, but it displays the command it's running as it runs it.
    """
    if "warn" in kwargs and kwargs['warn']:
        sys.stderr.write(Fore.YELLOW)
    else:
        sys.stderr.write(Fore.RED)
    sys.stdout.write(Fore.GREEN)
    print(cmd)
    sys.stdout.write(Fore.RESET)
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
    section("Get the Docker IP.")
    result = run("ifconfig | grep docker0 -A1 | grep 'inet addr'")
    ip = [x for x in str(result.stdout).split(" ") if x.startswith("addr:")][0][5:]
    return ip


@task
def env():
    """
    Dump all environment variables to stdout
    """
    for key, value in iteritems(os.environ):
        print(key, value)


@task
def install():
    """
    Prep the docker images we'll be developing on.
    """
    run('sudo docker pull postgres')
    run('sudo docker pull redis')
    run('sudo docker build -t django-dev .')
    run('echo "dj(){ cd /home/vagrant/configuration && invoke \$1 \$2 \$3 \$4 \$5 \$6 && cd -; }" >> /home/vagrant/.bashrc')


def is_postgres_running():
    """
    Returns True if the 'postgres' image is running.
    """
    section("Is postgres running?")
    result = run('docker ps')
    return "postgres" in result.stdout


@task
def boot_postgres():
    """
    Creates a temporary RAMdisk for Postgres data, then boots a Postgres image.
    This image is for dev only - using a RAMdisk for Postgres in production is a Bad Idea.
    """
    section("Boot the postgres image.")

    if is_postgres_running():
        print("Postgres is already running!")
        return
    else:
        print("Postgres is not running!")

    # Make sure postgres is well and truly dead before we attempt to resurrect it
    kill_postgres()

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

    # Postgres needs a couple of seconds to boot up.
    time.sleep(2)


@task
def kill_postgres():
    """
    Kills the postgres image, then unmounts the RAMdisk
    """
    section("Kill & clean up the Postgres image.")
    run('docker stop dev-postgres', warn=True)
    run('docker rm dev-postgres', warn=True)
    run('sudo umount {}'.format(PGDATA), warn=True)


@task
def ps():
    """
    List all docker containers
    """
    section("List all docker containers.")
    run('docker ps -a')


@task
def recycle():
    """
    Clean up any unwanted images.
    """
    section("Clean up any unwanted images.")
    run('docker rm -v $(docker ps -a -q -f status=exited)', warn=True)
    run('docker ps -a')


@task
def manage(cmd):
    """
    Run manage.py interactively.
    """
    section("Run manage.py interactively.")

    # Intercept Ctrl-C and kill the container when we exit
    def intercept_sigint_and_kill_docker_container(*_):
        section("Cleaning up containers...")
        run("docker kill django-manage")
        sys.exit(0)

    signal.signal(signal.SIGINT, intercept_sigint_and_kill_docker_container)

    # Boot Postgres (if it's not already up)
    boot_postgres()

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
    Scan DB Models for changes to the database. Make 'migrations' entries for them.
    """
    section("Scanning DB Models for changes to the database")
    manage("makemigrations")


@task
def migrate():
    """
    Apply any outstanding 'migrations' entries to the database.
    """
    section("Apply any changes to the database")
    manage("migrate")


@task
def startapp(name):
    """
    Create an application with name --name
    """
    manage("startapp {}".format(name))


@task
def check():
    """
    Check the app for common problems
    """
    manage("check")
    manage("sendtestemail --admins")


@task
def dbshell():
    """
    Run the DB Shell
    """
    manage("dbshell")


@task
def shell():
    """
    Run the iPython Shell
    """
    manage("shell")


@task
def go():
    """
    Get the dev server ready and GO!
    """
    makemigrations()
    migrate()
    runserver()
