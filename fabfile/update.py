import os

from fabric.api import env, task, run, cd

from edc_fabric.fabfile.conf import put_project_conf
from edc_fabric.fabfile.environment import bootstrap_env, update_fabric_env
from edc_fabric.fabfile.pip import pip_install_from_cache
from edc_fabric.fabfile.repositories import get_repo_name
from edc_fabric.fabfile.utils import launch_webserver, update_settings

from fabric.utils import warn, abort
from fabric.colors import red
from edc_fabric.fabfile.pip import pip_install_requirements_from_cache
from edc_fabric.fabfile.virtualenv import create_venv
from .utils import update_bcpp_conf


def prepare_env(conf_filename=None, bootstrap_path=None, release=None,
                map_area=None, bootstrap_branch=None, work_online=None,
                task_callable=None):
    bootstrap_env(
        path=bootstrap_path,
        filename=conf_filename,
        bootstrap_branch=bootstrap_branch)
#     if not release:
#         abort('Specify the release')
#     if not map_area:
#         abort('Specify the map_area')
    env.project_release = release
    env.map_area = map_area
    env.project_repo_name = get_repo_name(env.project_repo_url)
    env.project_repo_root = os.path.join(
        env.deployment_root, env.project_repo_name)
    env.fabric_config_root = os.path.join(env.project_repo_root, 'fabfile')
    env.fabric_config_path = os.path.join(
        env.fabric_config_root, 'conf', env.fabric_conf)
    update_fabric_env(use_local_fabric_conf=True)
    print(env.venv_dir)


@task
def query_tx_task(**kwargs):
    """Check for any host with pending transactions.

    fab -P -R mmankgodi update.query_tx_task:bootstrap_path=/Users/erikvw/source/bcpp/fabfile/conf/  --user=django

    """
    prepare_env(**kwargs)

    # run('brew services restart mysql', quiet=True)
    run('mysql -uroot -p edc -Bse \'select  count(*) '
        'from edc_sync_outgoingtransaction where is_consumed_server=0;\' > /tmp/stats1.txt')
    result = run('cat /tmp/stats1.txt')
    if result != '0':
        warn(red(f'{env.host}: pending {result}'))

    run(
        'mysql -uroot -p edc -Bse \'select count(*) '
        'from edc_sync_files_history '
        'where sent=0;\' > /tmp/stats2.txt')
    result = run('cat /tmp/stats2.txt')
    if result != '0':
        warn(red(f'{env.host}: unsent {result}'))


@task
def update_host_task(**kwargs):

    prepare_env()

    with cd(os.path.join(env.project_repo_root)):
        run('git checkout master')
        run('git pull')

    put_project_conf()
    update_bcpp_conf()

    pip_install_requirements_from_cache()

    launch_webserver()


@task
def update_task(skip_update_project_repo=None, skip_venv=None, release=None, map_area=None, **kwargs):

    if not release:
        abort('Specify the release')
    if not map_area:
        abort('Specify the map_area')

    prepare_env(**kwargs)

    print(env.venv_dir)
    if not skip_update_project_repo:
        print('rsync -pthrvz --delete {source} {destination}'.format(
            source=os.path.join(env.deployment_root, env.project_appname),
            destination=env.remote_source_root))
        run('rsync -pthrvz --delete {source} {destination}'.format(
            source=os.path.join(env.deployment_root, env.project_appname),
            destination=env.remote_source_root))

    with cd(os.path.join(env.project_repo_root)):
        run('git checkout master')

    if not skip_venv:
        create_venv()

    # copy bcpp.conf into etc/{project_app_name}/
    put_project_conf()
    update_bcpp_conf()
    update_settings()

#     with cd(os.path.join(env.project_repo_root)):
#         run('git checkout master')
#         run('python manage.py makemigrations')
#         run('python manage.py makemigrations bcpp bcpp_subject members household plot')
