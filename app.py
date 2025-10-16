import os
import socket
from flask import Flask, request

# Creiamo l'applicazione Flask
app = Flask(__name__)

# Leggiamo le informazioni di build dalle variabili d'ambiente, con dei valori di default
APP_VERSION = os.getenv('APP_VERSION', 'dev')
GIT_BRANCH = os.getenv('GIT_BRANCH', 'unknown')

def get_pod_info():
    """Raccoglie informazioni sull'ambiente del Pod."""
    hostname = socket.gethostname()
    
    # L'IP del pod è l'IP associato al suo hostname
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip_address = "sconosciuto"

    # Legge il namespace dal percorso standard in cui Kubernetes lo monta
    namespace = "sconosciuto"
    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
            namespace = f.read().strip()
    except FileNotFoundError:
        pass # Ignora se il file non esiste (es. in esecuzione locale)

    return hostname, namespace, ip_address

@app.route('/')
def pod_info():
    """Endpoint principale che restituisce il report tecnico."""
    hostname, namespace, ip_address = get_pod_info()

    # Costruiamo la risposta come testo semplice
    response_lines = [
        "--- Pod Info ---",
        f"Hostname:\t{hostname}",
        f"Namespace:\t{namespace}",
        f"IP Address:\t{ip_address}",
        "",
        "--- Build Info ---",
        f"Version:\t{APP_VERSION}",
        f"Git Branch:\t{GIT_BRANCH}",
        "",
        "--- Request Info ---",
        f"Method:\t\t{request.method}",
        f"URL Path:\t{request.path}",
        f"Remote Addr:\t{request.remote_addr}",
        "Headers:",
    ]

    for name, value in request.headers.items():
        response_lines.append(f"\t{name}: {value}")

    response_text = "\n".join(response_lines)
    
    return response_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    # Usiamo il development server di Flask solo per test locali
    app.run(host='0.0.0.0', port=8080)
