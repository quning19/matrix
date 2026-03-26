#coding=utf-8

import os
import re
import yaml
from matrix.base.BaseJob import BaseJob

class D2rJob(BaseJob):

    def __init__(self, options):
        BaseJob.__init__(self, options)
        self.d2r_config = self._load_config()

    def _load_config(self):
        yaml_path = os.path.join(os.path.dirname(__file__), 'D2rrConfig.yaml')
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f, yaml.FullLoader)
        
        return self._resolve_path_references(config)

    def _resolve_path_references(self, config):
        resolved = {}
        for key, value in config.items():
            if isinstance(value, str) and '$' in value:
                resolved[key] = self._resolve_path_string(value, resolved)
            else:
                resolved[key] = value
        return resolved

    def _resolve_path_string(self, path_string, resolved_config):
        pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)\\(.*)'
        matches = re.findall(pattern, path_string)
        result = path_string
        for ref, suffix in matches:
            if ref in resolved_config:
                base_path = resolved_config[ref]
                result = result.replace(f'${ref}\\{suffix}', base_path.rstrip('\\') + '\\' + suffix.lstrip('\\'))
            else:
                result = result.replace(f'${ref}\\{suffix}', ref + '\\' + suffix)
        return result

    def get_d2r_config(self, key=None, default=None):
        if key:
            return self.d2r_config.get(key, default)
        return self.d2r_config

    def get_d2r_config_path(self, key, default=None):
        value = self.d2r_config.get(key, default)
        if value and isinstance(value, str):
            return value.rstrip('\\')
        return value
