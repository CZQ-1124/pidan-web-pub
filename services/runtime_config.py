import os
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv, set_key
from config.settings import ROOT_DIR

ENV_PATH = ROOT_DIR / '.env'
load_dotenv(ENV_PATH)

DEFAULTS = {
    'AI_BASE_URL': 'https://aihubmix.com/v1',
    'AI_API_KEY': '',
    'TEXT_MODEL': 'doubao-seed-2-0-mini',
    'VISION_MODEL': 'qwen3-vl-flash',
    'AUDIO_MODEL': '',
    'THINKING_MODE': 'omit',  # omit/disabled/auto/enabled
    'AI_TIMEOUT_SEC': '25',
    'PUBLIC_MODE': 'true',
    'ENABLE_RUNTIME_SETTINGS': 'false',
}

def _secret_value(key: str):
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return None

def _session_value(key: str):
    try:
        import streamlit as st
        return st.session_state.get(key)
    except Exception:
        return None

def _as_bool(value: str | bool | None) -> bool:
    return str(value).strip().lower() in {'1', 'true', 'yes', 'y', 'on', '是'}

def get_runtime_config() -> Dict[str, str]:
    cfg = {}
    public_mode = _as_bool(_secret_value('PUBLIC_MODE') or os.getenv('PUBLIC_MODE', DEFAULTS['PUBLIC_MODE']))
    runtime_settings = _as_bool(_secret_value('ENABLE_RUNTIME_SETTINGS') or os.getenv('ENABLE_RUNTIME_SETTINGS', DEFAULTS['ENABLE_RUNTIME_SETTINGS']))
    for key, default in DEFAULTS.items():
        value = _secret_value(key)
        if value in [None, '']:
            value = os.getenv(key, '')
        if value in [None, ''] and (not public_mode or runtime_settings):
            value = _session_value(key)
        if value in [None, '']:
            value = default
        cfg[key] = str(value)
    return cfg

def save_runtime_config(payload: Dict[str, str]):
    cfg = get_runtime_config()
    public_mode = _as_bool(cfg.get('PUBLIC_MODE'))
    runtime_settings = _as_bool(cfg.get('ENABLE_RUNTIME_SETTINGS'))
    if public_mode and not runtime_settings:
        raise PermissionError('Public deployment disables saving runtime AI configuration. Use Streamlit secrets or server environment variables instead.')
    ENV_PATH.touch(exist_ok=True)
    for key, default in DEFAULTS.items():
        if key in {'PUBLIC_MODE', 'ENABLE_RUNTIME_SETTINGS'}:
            continue
        value = str(payload.get(key, default))
        set_key(str(ENV_PATH), key, value)
        os.environ[key] = value
        try:
            import streamlit as st
            st.session_state[key] = value
        except Exception:
            pass

def config_status() -> Dict[str, str | bool]:
    cfg = get_runtime_config()
    text_ready = bool(cfg['AI_API_KEY'] and cfg['AI_BASE_URL'] and cfg['TEXT_MODEL'])
    vision_ready = bool(cfg['AI_API_KEY'] and cfg['AI_BASE_URL'] and cfg['VISION_MODEL'])
    audio_ready = bool(cfg['AI_API_KEY'] and cfg['AI_BASE_URL'] and cfg['AUDIO_MODEL'])
    return {
        **cfg,
        'text_ready': text_ready,
        'vision_ready': vision_ready,
        'audio_ready': audio_ready,
        'public_mode': _as_bool(cfg.get('PUBLIC_MODE')),
        'runtime_settings_enabled': _as_bool(cfg.get('ENABLE_RUNTIME_SETTINGS')),
    }
