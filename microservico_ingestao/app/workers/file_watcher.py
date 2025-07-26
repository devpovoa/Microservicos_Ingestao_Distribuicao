import time
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.temp_models import ClienteTemp, CompraTemp

DATA_PATH = "/app/data"

class ExcelHandler(FileSystemEventHandler):
    def process_excel(self, file_path: str):
        """Processa arquivos Excel detectados"""
        db: Session = SessionLocal()
        
        try:
            if "clientes" in file_path:
                df = pd.read_excel(file_path)
                
                for _, row in df.iterrows():
                    # Verificar se já existe cliente pelo email.
                    cliente_existente = db.query(ClienteTemp).filter_by(email=row["email"]).first()
                    
                    if not cliente_existente:
                        novo_cliente = ClienteTemp(
                            nome = row["nome"],
                            email = row["email"],
                            telefone = row.get("telefone", "")
                        )
                        db.add(novo_cliente)
                db.commit()
                print(f'Clientes importados de {file_path}')
            elif "compras" in file_path:
                df = pd.read_excel(file_path)
                
                for _, row in df.iterrows():
                    cliente = db.query(ClienteTemp).filter_by(email=row["cliente_email"]).first()
                    
                    if cliente:
                        nova_compra = CompraTemp(
                            cliente_id = cliente.id,
                            produto = row["produto"],
                            valor = row["valor"]
                        )
                        db.add(nova_compra)
                db.commit()
                print(f'Compras importadas de {file_path}')
        except Exception as e:
            print(f'Erro ao processar {file_path}: {e}')
        finally:
            db.close()
    
    def on_created(self, event):
        """Quando um arquivo é criado"""
        if not event.is_directory and event.src_path.endswith(".xlsx"):
            print(f'Novo arquivo detectado: {event.src_path}')
            self.process_excel(event.src_path)

def start_file_watcher():
    print(f"Monitorando {DATA_PATH} por novos arquivos Excel...", flush=True)
    event_handler = ExcelHandler()
    observer = Observer()
    observer.schedule(event_handler, DATA_PATH, recursive=False)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()