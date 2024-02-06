#!/usr/bin/python
# coding:utf-8


import atexit
import json
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path

from rich.console import Console

from src.rime_deploy.metadata import Proxy, RimeSchema

console = Console()

src_path = Path(__file__).parent.parent
SCHEMA_DIR = src_path.joinpath("schema")
BACKUP_DIR = src_path.joinpath("backup")
DATA = src_path.joinpath("data.json")


@dataclass
class Config:
    is_proxy: bool = True
    """是否使用代理"""
    proxy_name: str = Proxy.GHPROXY.name
    proxy_url: str = Proxy.GHPROXY.value
    schema_name: str = RimeSchema.RIME_ICE.name
    schema_url: str = RimeSchema.RIME_ICE.value
    userdata_dir: str = None
    custom_backup_files: list[str] = field(default_factory=list)
    custom_exclude_schema_files: list[str] = field(default_factory=list)

    _instance = None
    _lock = threading.Lock()
    _registered = False

    @property
    def build_in_backup_files():
        return ["custom_phrase.txt"]

    @property
    def build_in_exclude_schema_files():
        return [".git", ".gitignore", "LICENSE", "README.md"]

    def __new__(cls, *args, **kw):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def load_from_file(self):
        if DATA.exists():
            try:
                with DATA.open() as f:
                    json_data = json.load(f)
                    for key, value in json_data.items():
                        setattr(self, key, value)
            except Exception as err:
                print(f"Failed to load config from file: {err}")
        else:
            print(f"Config file '{DATA}' not exists. Using default values.")

    def save_to_file(self):
        """保存配置到文件"""
        json_str = json.dumps(asdict(self), indent=4)
        with DATA.open("w") as f:
            f.write(json_str)

    @classmethod
    def register_atexit(cls):
        """注册在程序退出时保存配置到配置文件"""
        with cls._lock:
            if not cls._registered:
                atexit.register(cls._instance.save_to_file)
                cls._registered = True

    def __post_init__(self):
        self.load_from_file()
        self.register_atexit()


def set_schema(schema: RimeSchema):
    config.schema_name = schema.name
    config.schema_url = schema.value
    console.print("设置[green]成功[/]")


def set_proxy(proxy: Proxy):
    config.proxy_name = proxy.name
    config.proxy_url = proxy.value
    console.print("设置[green]成功[/]")


def set_custom_exclude_schema_files(input: str) -> list:
    _input = input.split(",")
    config.build_in_exclude_schema_files = _input
    return _input


config = Config()
