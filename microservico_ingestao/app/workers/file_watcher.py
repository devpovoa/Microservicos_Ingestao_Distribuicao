import os
import shutil
import time
from datetime import datetime

import pandas as pd
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.temp_models import ClienteTemp, CompraTemp, ProdutoTemp
from app.tasks.publisher import publish_processed_data

DATA_PATH = "/app/data"
PROCESSED_PATH = os.path.join(DATA_PATH, "processed")

os.makedirs(PROCESSED_PATH, exist_ok=True)


def cleanup_processed_folder():
    """Remove arquivos mais antigos se processed/ passar do limite"""
    files = [os.path.join(PROCESSED_PATH, f) for f in os.listdir(
        PROCESSED_PATH) if os.path.isfile(os.path.join(PROCESSED_PATH, f))]
    if len(files) > settings.processed_limit:
        files.sort(key=lambda f: os.path.getmtime(f))
        for f in files[:len(files) - settings.processed_limit]:
            os.remove(f)
            print(f"[CLEANUP] Removido arquivo antigo: {f}", flush=True)


def safe_str(value):
    return str(value).strip() if not pd.isna(value) else None


def process_excel(file_path: str):
    """Processa arquivo Excel e insere dados no banco"""
    try:
        df = pd.read_excel(file_path)

        required_cols = {
            "nome", "email", "telefone", "endereco_completo",
            "cpf_cnpj", "produto", "quantidade",
            "valor_unitario", "forma_pagamento"
        }
        if not required_cols.issubset(df.columns):
            print(
                f"[ERRO] Arquivo {file_path} inválido. Colunas obrigatórias faltando!", flush=True)
            return

        with SessionLocal() as db:
            with db.begin():
                for _, row in df.iterrows():
                    nome = safe_str(row["nome"])
                    email = safe_str(row["email"])
                    telefone = safe_str(row["telefone"])
                    endereco = safe_str(row["endereco_completo"])
                    cpf_cnpj = safe_str(row["cpf_cnpj"])

                    cliente = None
                    if cpf_cnpj:
                        cliente = db.query(ClienteTemp).filter_by(
                            cpf_cnpj=cpf_cnpj).first()
                    if not cliente:
                        cliente = db.query(ClienteTemp).filter_by(
                            nome=nome).first()
                    if not cliente:
                        cliente = ClienteTemp(
                            nome=nome,
                            email=email,
                            telefone=telefone,
                            cpf_cnpj=cpf_cnpj,
                            endereco_completo=endereco
                        )
                        db.add(cliente)
                        db.flush()

                    produto_nome = str(row["produto"]).strip()
                    produto = db.query(ProdutoTemp).filter_by(
                        nome_produto=produto_nome).first()
                    if not produto:
                        produto = ProdutoTemp(nome_produto=produto_nome)
                        db.add(produto)
                        db.flush()

                    try:
                        quantidade = int(row["quantidade"])
                        valor_unitario = float(row["valor_unitario"])
                    except (ValueError, TypeError) as err:
                        print(
                            f"[ERRO] Valores inválidos na linha: {row} -> {err}", flush=True)
                        continue

                    compra = CompraTemp(
                        cliente_id=cliente.id,
                        produto_id=produto.id,
                        quantidade=quantidade,
                        valor_unitario=valor_unitario,
                        valor_total=quantidade * valor_unitario,
                        data_hora=datetime.now(),
                        forma_pagamento=str(row["forma_pagamento"]).strip()
                    )
                    db.add(compra)
            print(
                f"[OK] {len(df)} vendas importadas de {file_path}", flush=True)

            # Buscar os dados já persistidos no banco TEMP
            clientes = db.query(ClienteTemp).all()
            produtos = db.query(ProdutoTemp).all()
            compras = db.query(CompraTemp).all()

            # Buscar os dados já persistidos no banco TEMP
            clientes = db.query(ClienteTemp).all()
            produtos = db.query(ProdutoTemp).all()
            compras = db.query(CompraTemp).all()

            # Index para montar o payload de cada compra
            cli_idx = {c.id: c for c in clientes}
            prod_idx = {p.id: p for p in produtos}

            # Publica UMA mensagem por compra
            for cp in compras:
                c = cli_idx.get(cp.cliente_id)
                p = prod_idx.get(cp.produto_id)

                if not c or not p:
                    print(
                        f"[WARN] Cliente/Produto não encontrado para compra {cp.id}", flush=True)
                    continue

                payload = {
                    "cliente": {
                        "nome": c.nome,
                        "email": c.email,
                        "telefone": c.telefone,
                        "cpf_cnpj": c.cpf_cnpj,
                        "endereco_completo": c.endereco_completo,
                    },
                    "produto": {
                        # o parser do Django já converte nome_produto -> nome
                        "nome_produto": p.nome_produto,
                    },
                    "quantidade": int(cp.quantidade),
                    "valor_unitario": float(cp.valor_unitario),
                    "valor_total": float(cp.valor_total),
                    "data_hora": cp.data_hora.isoformat(),  # o parser no Django torna aware
                    "forma_pagamento": cp.forma_pagamento,
                }

                # Enviar para RabbitMQ via Celery (publisher puro)
                try:
                    task_id = publish_processed_data(payload)
                    print(
                        f"[INFO] Publicado no RabbitMQ (processed_data). task_id={task_id}", flush=True)
                except Exception as e:
                    print(
                        f"[ERRO] Falha ao publicar compra {cp.id}: {e}", flush=True)

            print("[INFO] Todas as compras foram publicadas no RabbitMQ", flush=True)

        print("[INFO] Payload normalizado enviado para RabbitMQ", flush=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_path = os.path.join(
            PROCESSED_PATH, f"{os.path.splitext(os.path.basename(file_path))[0]}_{timestamp}.xlsx")
        shutil.move(file_path, dest_path)
        print(f"[MOVIDO] {file_path} -> {dest_path}", flush=True)

        cleanup_processed_folder()

    except Exception as e:
        print(f"[ERRO] Falha ao processar {file_path}: {e}", flush=True)


def start_file_watcher():
    """Loop para monitorar DATA_PATH e processar novos arquivos"""
    print(
        f"[SCAN] Monitorando {DATA_PATH} a cada {settings.scan_interval}s...", flush=True)

    while True:
        time.sleep(settings.scan_interval)
        for f in os.listdir(DATA_PATH):
            if f.endswith(".xlsx"):
                full_path = os.path.join(DATA_PATH, f)
                print(
                    f"[DETECTADO] Arquivo encontrado: {full_path}", flush=True)
                process_excel(full_path)
