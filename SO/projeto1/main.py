import threading
import time
import tkinter as tk
from tkinter import messagebox

n_canais = 0
hospedes = []
canal_semaforos = []
controle_remoto = threading.Semaphore(1)
canal_atual = None

def criar_hospede():
    global n_canais
    id_hospede = entry_id.get()
    canal = int(entry_canal.get())
    tempo_assistindo = int(entry_ttv.get())
    tempo_descansando = int(entry_td.get())
    
    if canal < 1 or canal > n_canais:
        messagebox.showerror("Erro", f"Canal inválido. Escolha entre 1 e {n_canais}.")
        return
    
    hospede = Hospede(id_hospede, canal, tempo_assistindo, tempo_descansando)
    hospedes.append(hospede)
    threading.Thread(target=hospede.iniciar_atividade).start()
    
    listbox_hospedes.insert(tk.END, f"Hóspede {id_hospede} no Canal {canal}")

class Hospede:
    def __init__(self, id_hospede, canal, tempo_assistindo, tempo_descansando):
        self.id_hospede = id_hospede
        self.canal = canal
        self.tempo_assistindo = tempo_assistindo
        self.tempo_descansando = tempo_descansando
        self.status = "Descansando"
    
    def iniciar_atividade(self):
        global canal_atual
        while True:
            self.status = "Descansando"
            atualizar_interface(self)
            time.sleep(self.tempo_descansando)
            
            with controle_remoto:

                #Nenhum canal
                if canal_atual is None:
                    canal_atual = self.canal
                    self.status = 'Assistindo TV'

                #canal ja em uso por outro usuario
                elif canal_atual == self.canal:
                    self.status = 'Assistindo TV'

                #status: descansando    
                else:
                    self.status = 'Dormindo (bloqueado)'
                    atualizar_interface(self)
                    continue
            atualizar_interface(self)
            time.sleep(self.tempo_assistindo)
            with controle_remoto:
                if canal_atual == self.canal:
                    canal_atual = None

    def __str__(self):
        return f"ID: {self.id_hospede}, Canal: {self.canal}, Assistindo: {self.tempo_assistindo}s, Descansando: {self.tempo_descansando}s"
    
def atualizar_interface(hospede):
    for i in range(listbox_hospedes.size()):
        if listbox_hospedes.get(i).startswith(f"Hóspede {hospede.id_hospede}"):
            listbox_hospedes.delete(i)
            listbox_hospedes.insert(i, f"Hóspede {hospede.id_hospede} - Canal {hospede.canal} - Status: {hospede.status}")
            break

def inicializar_semaforos():
    global n_canais
    n_canais = int(entry_n_canais.get())
    for _ in range(n_canais):
        canal_semaforos.append(threading.Semaphore(1))

def iniciar_programa():
    inicializar_semaforos()

root = tk.Tk()
root.title("Gerenciamento de Pousada - Controle de TV")

tk.Label(root, text="Número de Canais:").grid(row=0, column=0)
entry_n_canais = tk.Entry(root)
entry_n_canais.grid(row=0, column=1)

tk.Button(root, text="Iniciar Programa", command=iniciar_programa).grid(row=0, column=2)

tk.Label(root, text="ID do Hóspede:").grid(row=1, column=0)
entry_id = tk.Entry(root)
entry_id.grid(row=1, column=1)

tk.Label(root, text="Canal Preferido:").grid(row=2, column=0)
entry_canal = tk.Entry(root)
entry_canal.grid(row=2, column=1)

tk.Label(root, text="Tempo Assistindo TV (segundos):").grid(row=3, column=0)
entry_ttv = tk.Entry(root)
entry_ttv.grid(row=3, column=1)

tk.Label(root, text="Tempo Descansando (segundos):").grid(row=4, column=0)
entry_td = tk.Entry(root)
entry_td.grid(row=4, column=1)

tk.Button(root, text="Criar Hóspede", command=criar_hospede).grid(row=5, column=0, columnspan=2)

listbox_hospedes = tk.Listbox(root, width=50, height=10)
listbox_hospedes.grid(row=6, column=0, columnspan=3)

root.mainloop()
