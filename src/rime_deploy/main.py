#!/usr/bin/python
# coding:utf-8


import sys

from src.rime_deploy.config import BACKUP_DIR, SCHEMA_DIR, config, console, set_proxy, set_schema
from src.rime_deploy.metadata import Proxy, RimeSchema
from src.rime_deploy.utils import get_default_rime_userdata_dir, schema_update

if not SCHEMA_DIR.exists():
    SCHEMA_DIR.mkdir()
if not BACKUP_DIR.exists():
    BACKUP_DIR.mkdir()

divider = "-----------------------------------------"


def home():
    proxy_tag = "[green]打开[/]" if config.is_proxy else "[red]关闭[/]"
    content = f"""
{divider}
[bold white on blue]欢迎使用 Rime-Deplay[/]
当前方案：[red]{config.schema_name}[/] 代理：{ proxy_tag }
用户文件夹：{config.userdata_dir}
{divider}
 1 [green]部署/更新[/]方案
 2 [purple]切换[/]方案
 3 切换代理
 4 备份[yellow]自定义配置[/]
 5 [red]清理[/]方案文件
 6 修改[cyan]用户文件夹[/]
{divider}
 0 退出
"""
    console.print(content)
    menu_num = console.input("请输入选择 > ")
    match menu_num:
        case "1":
            auto_deplay()
        case "2":
            switch_schema()
        case "3":
            switch_proxy()
        case "4":
            backup()
        case "5":
            clean()
        case "6":
            change_user_data_dir()
        case "0":
            sys.exit()
        case _:
            console.print("输入[red]有误[/]，请重新选择")
            home()


def auto_deplay():
    content = f"""
{divider}
[bold white on blue]部署/更新[/]
当前方案：[red]{config.schema_name}[/]
{divider}
 1 一键部署
 2 一键更新
 3 手动更新
{divider}
 0 返回上级菜单
"""
    console.print(content)
    menu_num = console.input("请输入选择 > ")
    match menu_num:
        case "1":
            console.print("[yellow]暂未实现")
            auto_deplay()
        case "2":
            if config.userdata_dir is None:
                console.print("未设置[yellow]用户文件夹[/]，更新前请设置")
                change_user_data_dir()
            schema_update()
            auto_deplay()
        case "3":
            console.print("[yellow]暂未实现")
            auto_deplay()
        case "0":
            home()
        case _:
            console.print("输入[red]有误[/]，请重新选择")
            auto_deplay()


def switch_schema():
    content = f"""
{divider}
[bold white on blue]切换配置方案[/]
当前方案：[red]{config.schema_name}[/]
{divider}
 1 雾凇拼音
 2 四叶草
{divider}
 d 自定义方案
 0 返回上级菜单
"""
    console.print(content)
    menu_num = console.input("请输入选择 > ")
    match menu_num:
        case "1":
            set_schema(RimeSchema.RIME_ICE)
            console.print("设置[green]成功[/]")
            switch_schema()
        case "2":
            set_schema(RimeSchema.RIME_CLOVER_PINYIN)
            console.print("设置[green]成功[/]")
            switch_schema()
        case "d":
            name = console.input("请输入方案名：")
            value = console.input("请输入方案仓库链接：")
            config.schema_name = name
            config.schema_url = value
            switch_schema()
        case "0":
            home()
        case _:
            console.print("输入[red]有误[/]，请重新选择")
            auto_deplay()


def switch_proxy():
    content = f"""
{divider}
[bold white on blue]切换Github代理[/]
当前代理：[red]{config.proxy_url}[/]
{divider}
 1 GHPROXY (https://ghproxy.com/)
 2 MOEYY (https://github.moeyy.xyz/)
 3 KKGITHUB (https://github.com/)
{divider}
 c 关闭代理
 0 返回上级菜单
"""
    console.print(content)
    menu_num = console.input("请输入选择 > ")
    match menu_num:
        case "1":
            set_proxy(Proxy.GHPROXY)
            console.print("设置[green]成功[/]")
            switch_proxy()
        case "2":
            set_proxy(Proxy.MOEYY)
            console.print("设置[green]成功[/]")
            switch_proxy()
        case "2":
            set_proxy(Proxy.KKGITHUB)
            console.print("设置[green]成功[/]")
            switch_proxy()
        case "c":
            config.is_proxy = False
            console.print("关闭代理[green]成功[/]")
            switch_proxy()
        case "0":
            home()
        case _:
            console.print("输入[red]有误[/]，请重新选择")
            auto_deplay()


def backup():
    content = f"""
{divider}
[bold white on blue]备份配置[/]
{divider}
 暂未实现
{divider}
 0 返回上级菜单
"""
    console.print(content)
    menu_num = console.input("请输入选择 > ")
    match menu_num:
        case "0":
            home()
        case _:
            console.print("输入[red]有误[/]，请重新选择")
            auto_deplay()


def clean():
    content = f"""
{divider}
[bold white on blue]清理配置[/]
{divider}
 暂未实现
{divider}
 0 返回上级菜单
"""
    console.print(content)
    menu_num = console.input("请输入选择 > ")
    match menu_num:
        case "0":
            home()
        case _:
            console.print("输入[red]有误[/]，请重新选择")
            auto_deplay()


def change_user_data_dir():
    default_userdir = get_default_rime_userdata_dir()
    default_userdir_tag = f"[dim]({default_userdir})[/]" if default_userdir else "[dim](未检测到)[/]"
    content = f"""
{divider}
[bold white on blue]更新用户文件夹目录[/]
当前用户文件夹目录：[red]{config.userdata_dir}[/]
{divider}
 1 自动检测 {default_userdir_tag}
 2 默认
 3 手动添加
{divider}
 0 返回上级菜单
"""
    console.print(content)
    menu_num = console.input("请输入选择 > ")
    match menu_num:
        case "1":
            if default_userdir:
                config.userdata_dir = default_userdir
                console.print("设置[green]成功[/]")
                change_user_data_dir()
            else:
                console.print("未检测到默认路径，如需强制设置请选择选项 [yellow]2[/]")
                change_user_data_dir()
        case "2":
            config.userdata_dir = default_userdir
            console.print("设置[green]成功[/]")
            change_user_data_dir()
        case "3":
            path = console.input("请输入路径：")
            config.userdata_dir = path
            change_user_data_dir()
        case "0":
            home()
        case _:
            console.print("输入[red]有误[/]，请重新选择")
            change_user_data_dir()


if __name__ == "__main__":
    home()
