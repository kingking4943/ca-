#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurazione globale per Gestionale Gitemania PORTABLE (Versione Finale Stabile)
"""
import os, sys, json
from typing import Dict, Any
from cryptography.fernet import Fernet

class Config:
    def __init__(self):
        self.base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.exports_dir = os.path.join(self.base_dir, 'exports')
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.key_file = os.path.join(self.data_dir, "app.key")
        self.db_file = os.path.join(self.data_dir, "gitemania.db")
        os.makedirs(self.data_dir, exist_ok=True)
        self._fernet = None
        self.default_config = {
            "woocommerce": {"base_url": "", "consumer_key": "", "consumer_secret": ""},
            "app": {"sync_interval": 60, "per_page": 100, "first_run": True},
        }
        self._load_or_create_config()
    def get_database_path(self) -> str: return self.db_file
    def _get_fernet(self):
        if not self._fernet:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f: key = f.read()
            else:
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f: f.write(key)
            self._fernet = Fernet(key)
        return self._fernet
    def _load_or_create_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f: self.config = json.load(f)
        else:
            self.config = self.default_config.copy()
            self.save_config()
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f: json.dump(self.config, f, indent=2)
    def get(self, section: str, key: str = None, default=None):
        return self.config.get(section, {}).get(key, default) if key else self.config.get(section, default)
    def set(self, section: str, key: str, value: Any):
        if section not in self.config: self.config[section] = {}
        self.config[section][key] = value
    def set_encrypted(self, section: str, key: str, value: str):
        self.set(section, key, self._get_fernet().encrypt(value.encode()).decode())
    def get_encrypted(self, section: str, key: str, default="") -> str:
        encrypted = self.get(section, key, "")
        return self._get_fernet().decrypt(encrypted.encode()).decode() if encrypted else default

config = Config()
