from fabric.api import env, run, cd, put, get, hide, settings, sudo
from fabric.operations import local
from time import gmtime, strftime
import os

class BaseConfig(object):
    DO_DB = True
    FOLDER = '/home/podolabs/dapp-test'

class StageConfig(BaseConfig):
    HOST = os.environ.get('DAPP_STAGE_HOST', None)
    PASSWORD = os.environ.get('DAPP_STAGE_PASSWORD', None)
    BACKUP = False
    DB = "test.sqlite3"

class ProdConfig(BaseConfig):
    HOST = os.environ.get('PROD_HOST', None)
    PASSWORD = os.environ.get('PROD_PASSWORD', None)
    FOLDER = '/home/podolabs/site/kickstarter-app'
    BACKUP = True
    DB = "app.sqlite3"

def stage():
    deploy(StageConfig())

def prod_full():
    deploy(ProdConfig())

def deploy(config):
    if not setup(config.HOST, config.PASSWORD):
        return

    with cd(config.FOLDER):
        local('rsync -az --force --delete --progress --exclude-from=rsync_exclude.txt -e "ssh -p22" ./ {}:{}'.format(config.HOST, config.FOLDER))
        sudo('service dapp-test restart')

def setup(host, password):
    if not host:
        print "HOST env var not set"
        return False

    env.host_string = host
    env.password = password
    print "Using hosts {}".format(env.hosts)
    return True