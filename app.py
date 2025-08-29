from flask import Flask, request, render_template, jsonify, send_file, Response
import threading
import uuid
import time
import csv
import os
import sqlite3
import json
import geoip2.database
from scanner import scan, cancel, state

app = Flask(__name__)
resultados = []
lock = threading.Lock()

# Autenticação básica opcional (ajuste conforme necessário)
ENABLE_AUTH = False
USERNAME = "admin"
PASSWORD = "senha123"

# GeoIP2 Readers
georeader_city = None
georeader_asn = None
try:
    if os.path.exists("GeoLite2-City.mmdb"):
        georeader_city = geoip2.database.Reader("GeoLite2-City.mmdb")
    if os.path.exists("GeoLite2-ASN.mmdb"):
        georeader_asn = geoip2.database.Reader("GeoLite2-ASN.mmdb")
except Exception:
    pass


def autenticar():
    if not ENABLE_AUTH:
        return None
    auth = request.authorization
    if not auth or not (auth.username == USERNAME and auth.password == PASSWORD):
        return Response("Acesso negado", 401, {"WWW-Authenticate": 'Basic realm="Login required"'})


@app.route("/")
def index():
    if ENABLE_AUTH:
        resp = autenticar()
        if resp:
            return resp
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def iniciar_scan():
    if ENABLE_AUTH:
        resp = autenticar()
        if resp:
            return resp

    ip_range = request.form.get("ip_range")
    ports = request.form.get("ports")
    session_id = str(uuid.uuid4())[:8]
    source = "manual"

    with lock:
        state["em_andamento"] = True
        state["cancelado"] = False
        state["concluido"] = 0
        state["total"] = 0
        state["resultados"] = []
        resultados.clear()

    t = threading.Thread(target=scan, args=(ip_range, ports, resultados, session_id, source))
    t.daemon = True
    t.start()

    return "Scan iniciado"


@app.route("/cancelar", methods=["POST"])
def cancelar_scan():
    if ENABLE_AUTH:
        resp = autenticar()
        if resp:
            return resp

    cancel(state)
    return "Scan cancelado"


@app.route("/resultados")
def listar_resultados():
    if ENABLE_AUTH:
        resp = autenticar()
        if resp:
            return resp

    with lock:
        em_andamento = state.get("em_andamento", False)
        return jsonify({
            "em_andamento": em_andamento,
            "concluido": state.get("concluido", 0),
            "total": state.get("total", 0),
            "resultados": state.get("resultados", [])
        })


@app.route("/exportar")
def exportar_csv():
    if ENABLE_AUTH:
        resp = autenticar()
        if resp:
            return resp

    path = f"resultado_exportado_{uuid.uuid4().hex[:8]}.csv"
    try:
        with open(path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["IP", "Porta", "Banner", "País", "Cidade", "ASN", "Org", "Data"])
            conn = sqlite3.connect("portscan.db")
            cur = conn.cursor()
            cur.execute("SELECT ip, porta, banner, country, city, asn, org, data FROM resultados ORDER BY data DESC")
            for row in cur.fetchall():
                writer.writerow(row)
            conn.close()
    except Exception as e:
        return f"Erro ao exportar: {e}", 500

    return send_file(path, as_attachment=True)


@app.route("/exportar-jsonl")
def exportar_jsonl():
    if ENABLE_AUTH:
        resp = autenticar()
        if resp:
            return resp

    service = request.args.get("service", "").lower()
    country = request.args.get("country", "").upper()
    path = f"resultado_filtrado_{uuid.uuid4().hex[:8]}.jsonl"

    try:
        conn = sqlite3.connect("portscan.db")
        cur = conn.cursor()
        cur.execute("SELECT ip, porta, banner, country, city, asn, org, data FROM resultados ORDER BY data DESC")
        with open(path, "w", encoding="utf-8") as f:
            for ip, port, banner, pais, cidade, asn, org, data in cur.fetchall():
                if service and service not in banner.lower():
                    continue
                if country and (not pais or pais.upper() != country):
                    continue
                linha = {
                    "ip": ip,
                    "porta": port,
                    "banner": banner,
                    "country": pais,
                    "city": cidade,
                    "asn": asn,
                    "org": org,
                    "data": data
                }
                f.write(json.dumps(linha) + "\n")
        conn.close()
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    return send_file(path, as_attachment=True)


@app.route("/sessoes")
def listar_sessoes():
    if ENABLE_AUTH:
        resp = autenticar()
        if resp:
            return resp

    try:
        conn = sqlite3.connect("portscan.db")
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT session_id FROM resultados ORDER BY data DESC")
        sessoes = [r[0] for r in cur.fetchall()]
        conn.close()
        return jsonify(sessoes=sessoes)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@app.route("/diff", methods=["GET"])
def comparar_sessoes():
    if ENABLE_AUTH:
        resp = autenticar()
        if resp:
            return resp

    s1 = request.args.get("s1")
    s2 = request.args.get("s2")
    try:
        conn = sqlite3.connect("portscan.db")
        cur = conn.cursor()
        cur.execute("SELECT ip, porta FROM resultados WHERE session_id=?", (s1,))
        set1 = set((r[0], r[1]) for r in cur.fetchall())
        cur.execute("SELECT ip, porta FROM resultados WHERE session_id=?", (s2,))
        set2 = set((r[0], r[1]) for r in cur.fetchall())
        conn.close()
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    return jsonify({
        "s1": s1,
        "s2": s2,
        "apenas_em_s1": list(set1 - set2),
        "apenas_em_s2": list(set2 - set1)
    })


@app.after_request
def aplicar_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


if __name__ == "__main__":
    app.run(debug=False)
