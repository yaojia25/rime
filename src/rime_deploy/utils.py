#!/usr/bin/python
# coding:utf-8

import datetime
import os
import shutil
import subprocess
from pathlib import Path

from src.rime_deploy.config import BACKUP_DIR, SCHEMA_DIR, config, console


def get_default_rime_userdata_dir():
    appdata = os.getenv("APPDATA", None)
    rime_dir = Path(appdata).joinpath("Rime")
    if rime_dir.exists():
        console.print(f"检测到默认用户文件夹：[green]{rime_dir}[/]")
        return rime_dir
    else:
        console.print("未检测默认用户文件夹，请确认用户文件夹是否为默认配置")
        return None


def clone(schema_url: str, schema_dir: str) -> bool:
    try:
        subp = subprocess.run(
            f"git clone --depth=1 {schema_url} {schema_dir}", stdout=subprocess.PIPE, shell=True, timeout=60
        )
        while True:
            if subp.returncode == 0:
                console.print("克隆[green]成功[/]")
                return True
    except subprocess.TimeoutExpired:
        console.print("克隆仓库[red]超时[/]")
        return False


def pull(schema_dir) -> bool:
    try:
        subp = subprocess.run("git pull -f", stdout=subprocess.PIPE, shell=True, timeout=60, cwd=schema_dir)
        while True:
            if subp.returncode == 0:
                console.print("更新本地仓库[green]成功[/]")
                return True
    except subprocess.TimeoutExpired:
        console.print("更新本地仓库[red]超时[/]")
        return False


def backup_custom_yaml(userdata_dir: str | Path):
    backup_files = ["custom_phrase.txt"]
    backup_files.extend(config.extra_backup_files)
    userdata_dir = Path(userdata_dir)
    backup_dir = BACKUP_DIR.joinpath(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    backup_dir.mkdir()
    for iter in userdata_dir.iterdir():
        if iter.name.endswith("custom.yaml") or iter.name in backup_files:
            if iter.is_dir():
                shutil.copytree(iter, backup_dir / iter.name, dirs_exist_ok=True)
            elif iter.is_file():
                shutil.copy(iter, backup_dir / iter.name)
    console.print("备份自定义配置[green]成功[/]")


def copy_schema_to_userdata(userdata_dir: Path, schema_dir: Path) -> bool:
    userdata_dir = Path(userdata_dir)
    exclude_files = [".git", ".gitignore", "LICENSE", "README.md"]
    exclude_files.extend(config.exclude_schema_files)
    for iter in schema_dir.iterdir():
        if iter not in exclude_files:
            try:
                if iter.is_dir():
                    shutil.copytree(iter, userdata_dir / iter.name, dirs_exist_ok=True)
                elif iter.is_file():
                    shutil.copy(iter, userdata_dir / iter.name)
            except Exception as e:
                console.log(e)
                console.print("复制方案到用户文件夹[red]失败[/]")
                return False
    console.print("复制方案到用户文件夹[green]成功[/]")
    return True


def schema_update():
    with console.status("更新方案中...") as status:
        status.update("[1] 检测基础配置")
        if config.userdata_dir is None:
            console.print("未设置[yellow]用户文件夹[/]")
            return
        url = config.proxy_url + config.schema_url if config.is_proxy else config.schema_url
        schema_dir = SCHEMA_DIR.joinpath(config.schema_name)

        status.update("[2] 更新本地方案")
        if schema_dir.exists():
            if not pull(schema_dir):
                return
        else:
            if not clone(url, schema_dir):
                return

        status.update("[3] 备份自定义配置")
        backup_custom_yaml(config.userdata_dir)

        status.update("[4] 复制配置")
        copy_schema_to_userdata(config.userdata_dir, schema_dir)
