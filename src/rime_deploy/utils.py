#!/usr/bin/python
# coding:utf-8

import datetime
import os
import shutil
import subprocess
from pathlib import Path

from src.rime_deploy.config import BACKUP_DIR, SCHEMA_DIR, config, console
from src.rime_deploy.metadata import splice_proxy


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
    cmd = ["git", "clone", "--depth=1", schema_url, schema_dir]
    try:
        subp = subprocess.run(cmd, stdout=None, capture_output=True, timeout=60)
        while True:
            if subp.returncode == 0:
                return True
    except subprocess.TimeoutExpired:
        return False


def pull(schema_dir) -> bool:
    cmd = ["git", "pull", "-f"]
    try:
        subp = subprocess.run(cmd, stdout=None, capture_output=True, timeout=60, cwd=schema_dir)
        while True:
            if subp.returncode == 0:
                return True
    except subprocess.TimeoutExpired:
        return False


def backup_custom_yaml(userdata_dir: str | Path):
    backup_files = config.build_in_backup_files
    backup_files.extend(config.custom_backup_files)
    userdata_dir = Path(userdata_dir)
    backup_dir = BACKUP_DIR.joinpath(datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
    backup_dir.mkdir()
    for iter in userdata_dir.iterdir():
        if iter.name.endswith("custom.yaml") or iter.name in backup_files:
            try:
                if iter.is_dir():
                    shutil.copytree(iter, backup_dir / iter.name, dirs_exist_ok=True)
                elif iter.is_file():
                    shutil.copy(iter, backup_dir / iter.name)
            except Exception:
                return False
    return True


def copy_schema_to_userdata(userdata_dir: Path, schema_dir: Path) -> bool:
    userdata_dir = Path(userdata_dir)
    exclude_files = config.build_in_exclude_schema_files
    exclude_files.extend(config.custom_exclude_schema_files)
    for iter in schema_dir.iterdir():
        if iter not in exclude_files:
            try:
                if iter.is_dir():
                    shutil.copytree(iter, userdata_dir / iter.name, dirs_exist_ok=True)
                elif iter.is_file():
                    shutil.copy(iter, userdata_dir / iter.name)
            except Exception:
                return False
    return True


def schema_update():
    status_success = "[green]✓[/]"
    status_failure = "[red]x[/]"
    with console.status("更新方案中...", spinner="arc") as status:
        # 验证基础配置
        status.update(" [1/4] 验证基础配置...")
        url = splice_proxy(config.proxy_url + config.schema_url) if config.is_proxy else config.schema_url
        schema_dir = SCHEMA_DIR.joinpath(config.schema_name)
        console.print(f" {status_success} 基础配置验证完成")
        # 更新本地输入方案
        status.update(" [2/4] 更新本地输入方案...")
        if schema_dir.exists():
            ret = pull(schema_dir)
            tags = "更新"
        else:
            ret = clone(url, schema_dir)
            tags = "克隆"
        if ret:
            console.print(f" {status_success} 本地输入方案{tags}成功")
        else:
            console.print(f" {status_failure} 本地输入方案{tags}失败")
            console.print("\n[blue]提示: [/]请检查输入方案链接是否正确，或者尝试开启代理并重试。")
            return
        # 备份自定义配置
        status.update(" [3/4] 备份自定义配置...")
        ret = backup_custom_yaml(config.userdata_dir)
        if ret:
            console.print(f" {status_success} 自定义配置备份成功")
        else:
            console.print(f" {status_failure} 自定义配置备份失败")
        # 更新用户文件夹
        status.update(" [4/4] 更新用户文件夹...")
        ret = copy_schema_to_userdata(config.userdata_dir, schema_dir)
        if ret:
            console.print(f" {status_success} 用户文件夹更新成功")
        else:
            console.print(f" {status_failure} 用户文件夹更新失败")

        console.print("🎉 方案更新完成!")
