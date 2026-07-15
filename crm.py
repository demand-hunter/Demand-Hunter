import csv
import os
from datetime import datetime
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
ARQUIVO=os.path.join(BASE_DIR,"clientes_interessados.csv")
def salvar_cliente(usuario,dor,nivel_interesse,origem):
    novo=not os.path.exists(ARQUIVO)
    with open(ARQUIVO,"a",newline="",encoding="utf-8-sig") as f:
        campos=["data","usuario","dor","nivel_interesse","origem"]
        writer=csv.DictWriter(f,fieldnames=campos)
        if novo: writer.writeheader()
        writer.writerow({"data":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"usuario":usuario,"dor":dor,"nivel_interesse":nivel_interesse,"origem":origem})
