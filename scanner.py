import socket
import threading
import queue
import ipaddress
import sqlite3
import datetime
import os
from pathlib import Path
import geoip2.database
import geoip2.errors

db_lock = threading.Lock()

state = {
    "cancelado": False,
    "total": 0,
    "concluido": 0,
    "em_andamento": False,
    "resultados": [],
    "lock": threading.Lock(),
    "task_queue": None,
    "threads": []
}

DB_PATH = 'portscan.db'
PAYLOAD_DIR = 'payloads'

DEFAULT_TIMEOUTS = {
    80: 3,
    443: 3,
    3306: 2,
    5432: 2,
    6379: 2,
    27017: 2
}

# GeoIP Load
georeader_city = None
georeader_asn = None
try:
    if os.path.exists("GeoLite2-City.mmdb"):
        georeader_city = geoip2.database.Reader("GeoLite2-City.mmdb")
    if os.path.exists("GeoLite2-ASN.mmdb"):
        georeader_asn = geoip2.database.Reader("GeoLite2-ASN.mmdb")
except Exception as e:
    print(f"[ERRO][GEO] Falha ao carregar base GeoIP: {e}")


def init_db():
    with db_lock:
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS resultados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ip TEXT,
                    porta INTEGER,
                    banner TEXT,
                    country TEXT,
                    city TEXT,
                    asn TEXT,
                    org TEXT,
                    session_id TEXT,
                    source TEXT,
                    data TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    ip TEXT,
                    porta INTEGER,
                    PRIMARY KEY (ip, porta)
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERRO][DB] Inicialização falhou: {e}")


def enrich_geo(ip):
    result = {"country": "", "city": "", "asn": "", "org": ""}
    try:
        if georeader_city:
            city = georeader_city.city(ip)
            result["country"] = city.country.name or ""
            result["city"] = city.city.name or ""
        if georeader_asn:
            asn = georeader_asn.asn(ip)
            result["asn"] = f"AS{asn.autonomous_system_number}" if asn else ""
            result["org"] = asn.autonomous_system_organization or ""
    except geoip2.errors.AddressNotFoundError:
        pass
    except Exception as e:
        print(f"[WARN][GEO] {ip}: {e}")
    return result


def enrich_banner(ip, port, banner_text):
    lowered = banner_text.lower()
    if "mysql" in lowered:
        return f"MySQL: {ip}:{port} - {banner_text}"
    elif "postgres" in lowered:
        return f"PostgreSQL: {ip}:{port} - {banner_text}"
    elif "redis" in lowered:
        return f"Redis: {ip}:{port} - {banner_text}"
    elif "mongo" in lowered:
        return f"MongoDB: {ip}:{port} - {banner_text}"
    elif "http" in lowered:
        return f"HTTP: {ip}:{port} - {banner_text}"
    elif "timeout" in lowered:
        return f"Timeout: {ip}:{port} - {banner_text}"
    elif "recusada" in lowered or "conexao recusada" in lowered:
        return f"Conexão recusada: {ip}:{port} - {banner_text}"
    elif "erro" in lowered:
        return f"Erro: {ip}:{port} - {banner_text}"
    return f"{ip}:{port} - {banner_text}"


def load_payload(port):
    mapping = {
        80: "http.bin",
        6379: "redis.bin",
        11211: "memcached.bin",
        27017: "mongodb.bin",
        5432: "pgsql.bin",
        3306: "mysql.bin",
        9200: "elasticsearch.bin",
        5984: "couchdb.bin"
    }
    fname = mapping.get(port)
    if not fname:
        return None
    path = os.path.join(PAYLOAD_DIR, fname)
    if os.path.exists(path):
        return Path(path).read_bytes()
    else:
        print(f"[INFO][PAYLOAD] '{fname}' não encontrado para porta {port}")
    return None


def get_timeout_for_port(port):
    return DEFAULT_TIMEOUTS.get(port, 2)


def service_detector(ip, port, session_id=None, source=None, dry_run=False):
    if dry_run:
        return f"{ip}:{port} - Simulação"

    payload = load_payload(port)
    timeout = get_timeout_for_port(port)

    try:
        with socket.create_connection((ip, port), timeout=timeout) as s:
            s.settimeout(timeout)
            if payload:
                try:
                    s.sendall(payload)
                except Exception as e:
                    print(f"[ERRO][SEND] {ip}:{port} - {e}")
            try:
                banner = s.recv(1024)
            except socket.timeout:
                banner = b''
            except Exception as e:
                print(f"[ERRO][RECV] {ip}:{port} - {e}")
                banner = b''
    except Exception as e:
        banner_text = f"erro: {str(e).lower()}"
    else:
        banner_text = banner.decode(errors="ignore").strip() or "sem resposta"

    geo = enrich_geo(ip)

    with db_lock:
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO resultados (ip, porta, banner, country, city, asn, org, session_id, source, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ip, port, banner_text,
                geo["country"], geo["city"], geo["asn"], geo["org"],
                session_id, source, datetime.datetime.now().isoformat()
            ))
            cur.execute("INSERT OR IGNORE INTO cache (ip, porta) VALUES (?, ?)", (ip, port))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[ERRO][DB_INSERT] {ip}:{port} - {e}")

    return enrich_banner(ip, port, banner_text)


def _worker(task_q, resultados, session_id, source, dry_run=False):
    while not task_q.empty():
        with state["lock"]:
            if state["cancelado"]:
                break
        ip, port = task_q.get()
        resultado = service_detector(ip, port, session_id=session_id, source=source, dry_run=dry_run)
        resultados.append(resultado)
        with state["lock"]:
            state["concluido"] += 1
            state["resultados"].append(resultado)
        task_q.task_done()


def scan(ip_range, ports, resultados, session_id, source=None, dry_run=False, threads=100, ignorar_cache=False):
    init_db()
    task_q = queue.Queue()

    if "/" not in ip_range:
        ip_range += "/32"

    ports = [int(p.strip()) for p in ports.split(",")]
    ips = list(ipaddress.ip_network(ip_range).hosts())

    with db_lock:
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            for ip in ips:
                for port in ports:
                    if not ignorar_cache:
                        cur.execute("SELECT 1 FROM cache WHERE ip=? AND porta=?", (str(ip), port))
                        if cur.fetchone():
                            continue
                    task_q.put((str(ip), port))
            conn.close()
        except Exception as e:
            print(f"[ERRO][CACHE] Leitura falhou: {e}")

    with state["lock"]:
        state["cancelado"] = False
        state["concluido"] = 0
        state["resultados"] = []
        state["em_andamento"] = True
        state["threads"] = []
        state["total"] = task_q.qsize()
        state["task_queue"] = task_q

    for _ in range(threads):
        t = threading.Thread(target=_worker, args=(task_q, resultados, session_id, source, dry_run))
        t.daemon = True
        t.start()
        with state["lock"]:
            state["threads"].append(t)

    task_q.join()

    with state["lock"]:
        state["em_andamento"] = False


def cancel(state: dict):
    with state["lock"]:
        state["cancelado"] = True
        task_q = state.get("task_queue")
    if isinstance(task_q, queue.Queue):
        try:
            while True:
                task_q.get_nowait()
                task_q.task_done()
        except queue.Empty:
            pass


def _join_and_cleanup(state: dict, join_timeout: float = 0.0):
    threads = list(state.get("threads", []))
    for t in threads:
        try:
            t.join(timeout=join_timeout if join_timeout and join_timeout > 0 else 0)
        except Exception:
            pass
    if not any(t.is_alive() for t in threads):
        state["threads"] = []
        state["task_queue"] = None
