import os
import time
import shutil
import pandas as pd
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.temp_models import ClienteTemp, CompraTemp
from datetime import datetime

DATA_PATH = "/app/data"
PROCESSED_PATH = os.path.join(DATA_PATH, "processed")
SCAN_INTERVAL = 3            # segundos entre cada varredura
PROCESSED_LIMIT = 50         # máximo de arquivos a manter na pasta processed

# Garante que a pasta processed existe
os.makedirs(PROCESSED_PATH, exist_ok=True)

def cleanup_processed_folder():
    """Remove arquivos mais antigos se processed/ passar do limite"""
    files = [os.path.join(PROCESSED_PATH, f) for f in os.listdir(PROCESSED_PATH)]
    files = [f for f in files if os.path.isfile(f)]

    if len(files) > PROCESSED_LIMIT:
        # Ordena por data de modificação (mais antigos primeiro)
        files.sort(key=lambda f: os.path.getmtime(f))
        to_remove = len(files) - PROCESSED_LIMIT

        for f in files[:to_remove]:
            os.remove(f)
            print(f"Removido arquivo antigo: {f}", flush=True)



def process_excel(file_path: str):
    """Processa arquivos Excel detectados"""
    db: Session = SessionLocal()

    try:
        if "clientes" in file_path:
            df = pd.read_excel(file_path)

            for _, row in df.iterrows():
                email = str(row["email"]).strip().lower()
                cliente_existente = db.query(ClienteTemp).filter_by(email=email).first()

                if not cliente_existente:
                    novo_cliente = ClienteTemp(
                        nome=row["nome"].strip(),
                        email=email,
                        telefone=str(row.get("telefone", "")).strip()
                    )
                    db.add(novo_cliente)

            db.commit()
            print(f"Clientes importados de {file_path}", flush=True)

        elif "compras" in file_path:
            df = pd.read_excel(file_path)

            for _, row in df.iterrows():
                email = str(row["cliente_email"]).strip().lower()
                cliente = db.query(ClienteTemp).filter_by(email=email).first()
                if cliente:
                    nova_compra = CompraTemp(
                        cliente_id=cliente.id,
                        produto=row["produto"].strip(),
                        valor=row["valor"]
                    )
                    db.add(nova_compra)

            db.commit()
            print(f"Compras importadas de {file_path}", flush=True)

        # Após processar, gera nome único com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(file_path)
        name, ext = os.path.splitext(base_name)
        new_name = f"{name}_{timestamp}{ext}"

        dest_path = os.path.join(PROCESSED_PATH, new_name)
        shutil.move(file_path, dest_path)
        print(f"Arquivo movido para {dest_path}", flush=True)

        # ✅ Limpa arquivos antigos se processed/ passar do limite
        cleanup_processed_folder()

    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}", flush=True)
    finally:
        db.close()


def start_file_watcher():
    print(f"[SCAN] Monitorando {DATA_PATH} a cada {SCAN_INTERVAL}s...", flush=True)

    # Guarda mtime dos arquivos para detectar alterações
    known_files = {}

    while True:
        time.sleep(SCAN_INTERVAL)

        for f in os.listdir(DATA_PATH):
            if f.endswith(".xlsx"):
                full_path = os.path.join(DATA_PATH, f)
                mtime = os.path.getmtime(full_path)  # última modificação

                # Se arquivo novo OU alterado
                if f not in known_files or known_files[f] != mtime:
                    print(f"Arquivo novo/atualizado detectado: {full_path}", flush=True)
                    process_excel(full_path)
                    known_files[f] = mtime
