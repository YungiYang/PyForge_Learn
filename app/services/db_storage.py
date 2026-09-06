"""
Централизованный сервис хранения данных PyForge (DBStorage).
Поддерживает:
1. Облачную базу данных Supabase (PostgreSQL / PostgREST JSONB хранилище).
2. Локальные JSON файлы (data/*.json) как резервный/автономный режим.
3. Автоматическую синхронизацию между локальным хранилищем и Supabase.
"""

import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, Optional, List

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

class DBStorage:
    _supabase_status_cache: Optional[Dict[str, Any]] = None
    _last_status_check: float = 0.0

    @classmethod
    def _read_env_file(cls):
        for p in [Path(".env"), Path("../.env"), DATA_DIR.parent.parent / ".env", DATA_DIR.parent / ".env"]:
            if p.exists():
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#") and "=" in line:
                                k, v = line.split("=", 1)
                                k = k.strip()
                                v = v.strip().strip("'\"")
                                if k and k not in os.environ:
                                    os.environ[k] = v
                except Exception:
                    pass

    @classmethod
    def get_config(cls) -> Dict[str, str]:
        cls._read_env_file()
        url = (os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or "").strip().rstrip("/")
        key = (
            os.environ.get("SUPABASE_KEY")
            or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("SUPABASE_ANON_KEY")
            or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
            or ""
        ).strip()
        return {"url": url, "key": key}

    @classmethod
    def is_supabase_configured(cls) -> bool:
        cfg = cls.get_config()
        return bool(cfg["url"] and cfg["key"])

    @classmethod
    def _supabase_request(cls, endpoint: str, method: str = "GET", body: Optional[Any] = None, timeout: float = 4.0) -> Any:
        cfg = cls.get_config()
        if not (cfg["url"] and cfg["key"]):
            return None

        full_url = f"{cfg['url']}{endpoint}"
        headers = {
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        if method in ("POST", "PUT", "PATCH"):
            headers["Prefer"] = "resolution=merge-duplicates,return=representation"

        data_bytes = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(full_url, data=data_bytes, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp_data = resp.read().decode("utf-8")
                if resp_data:
                    return json.loads(resp_data)
                return []
        except urllib.error.HTTPError:
            return None
        except Exception:
            return None

    @classmethod
    def test_connection(cls) -> Dict[str, Any]:
        cfg = cls.get_config()
        if not (cfg["url"] and cfg["key"]):
            return {
                "connected": False,
                "configured": False,
                "mode": "local_json",
                "message": "Supabase не настроен в переменных окружения (используется локальное JSON-хранилище)"
            }

        start = time.perf_counter()
        res = cls._supabase_request("/rest/v1/pyforge_store?select=key&limit=1", method="GET", timeout=3.0)
        latency_ms = round((time.perf_counter() - start) * 1000, 1)

        if res is not None:
            return {
                "connected": True,
                "configured": True,
                "mode": "supabase_cloud",
                "url": cfg["url"],
                "latency_ms": latency_ms,
                "message": f"🟢 Подключено к Supabase ({latency_ms} ms)"
            }
        else:
            return {
                "connected": False,
                "configured": True,
                "mode": "local_fallback",
                "url": cfg["url"],
                "message": "⚠️ Supabase настроен, но таблица `pyforge_store` не найдена. Создайте таблицу через SQL Editor!"
            }

    @classmethod
    def load_json(cls, filename: str, default: Any = None) -> Any:
        key_name = Path(filename).name
        local_file = DATA_DIR / key_name

        # 1. Попытка прочитать из Supabase
        if cls.is_supabase_configured():
            try:
                res = cls._supabase_request(f"/rest/v1/pyforge_store?key=eq.{key_name}&select=value", method="GET")
                if res and isinstance(res, list) and len(res) > 0 and "value" in res[0]:
                    cloud_val = res[0]["value"]
                    try:
                        DATA_DIR.mkdir(parents=True, exist_ok=True)
                        with open(local_file, "w", encoding="utf-8") as f:
                            json.dump(cloud_val, f, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
                    return cloud_val
            except Exception:
                pass

        # 2. Локальное чтение (основное или фолбэк)
        if local_file.exists():
            try:
                with open(local_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        return default

    @classmethod
    def save_json(cls, filename: str, data: Any):
        key_name = Path(filename).name
        local_file = DATA_DIR / key_name
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Локальное сохранение
        try:
            with open(local_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[DBStorage] Ошибка локальной записи {key_name}: {e}")

        # 2. Облачное сохранение в Supabase
        if cls.is_supabase_configured():
            try:
                payload = {
                    "key": key_name,
                    "value": data,
                    "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                cls._supabase_request("/rest/v1/pyforge_store", method="POST", body=payload)
            except Exception as e:
                print(f"[DBStorage] Ошибка отправки в Supabase ({key_name}): {e}")

    @classmethod
    def sync_local_to_supabase(cls) -> Dict[str, Any]:
        if not cls.is_supabase_configured():
            raise ValueError("Supabase не настроен в переменных окружения (SUPABASE_URL / SUPABASE_KEY)")

        filenames = [
            "users.json", "sessions.json", "custom_roles.json",
            "custom_titles.json", "forum_data.json", "ideas_data.json",
            "custom_tasks.json", "daily_quests.json", "user_profile.json"
        ]
        synced = []
        for name in filenames:
            file_path = DATA_DIR / name
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    cls._supabase_request("/rest/v1/pyforge_store", method="POST", body={
                        "key": name,
                        "value": data,
                        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    })
                    synced.append(name)
                except Exception as e:
                    print(f"Ошибка синхронизации {name}: {e}")

        return {
            "success": True,
            "synced_files": synced,
            "message": f"Синхронизировано {len(synced)} файлов в Supabase Cloud! ☁️"
        }
