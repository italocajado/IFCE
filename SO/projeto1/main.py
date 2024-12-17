import threading
import tkinter as tk
from tkinter import messagebox

n_canais = 0
hospedes = []
canal_semaforos = []
espec_por_canal = {}
hospede_indice = {}
controle_remoto = threading.Semaphore(1)
canal_em_uso = None
canal_lock = threading.Lock()

def criar_hospede():
    global n_canais
    id_hospede = entry_id.get()
    canal = int(entry_canal.get())
    tempo_assistindo = int(entry_ttv.get())
    tempo_descansando = int(entry_td.get())

    if canal < 1 or canal > n_canais:
        messagebox.showerror("Erro", f"Canal inválido. Escolha entre 1 e {n_canais}.")
        return

    for hospede in hospedes:
        if hospede.id_hospede == id_hospede:
            messagebox.showerror("Erro", f"{id_hospede} já existe.")
            return

    hospede = Hospede(id_hospede, canal, tempo_assistindo, tempo_descansando)
    hospedes.append(hospede)
    index = listbox_hospedes.size()
    hospede_indice[id_hospede] = index
    listbox_hospedes.insert(tk.END, f"Hóspede {id_hospede} - Canal {canal} - Status: {hospede.status}")
    hospede.start()

class Hospede(threading.Thread):
    def __init__(self, id_hospede, canal, tempo_assistindo, tempo_descansando):
        super().__init__()
        self.id_hospede = id_hospede
        self.canal = canal
        self.tempo_assistindo = tempo_assistindo
        self.tempo_descansando = tempo_descansando
        self.status = "Descansando"
        self.ativo = True
    
    def run(self):
        while self.ativo:
            self.descansar()
            self.tentar_assistir()
    
    def iniciar_atividade(self):
        self.descansar()

    def descansar(self):
        self.status = "Descansando"
        atualizar_interface(self)
        self.timer = threading.Timer(self.tempo_descansando, self.tentar_assistir)
        self.timer.start()

    def tentar_assistir(self):
        global canal_em_uso
        
        canal_semaforo = canal_semaforos[self.canal - 1]

        with controle_remoto:
            if canal_em_uso is None or canal_em_uso == self.canal:
                if canal_semaforo.acquire(blocking=False):  
                    canal_em_uso = self.canal
                    self.assistir(canal_semaforo)
                else:
                    self.status = "Bloqueado"
                    atualizar_interface(self)
                    self.timer = threading.Timer(1, self.tentar_assistir)
                    self.timer.start()
            else:
                self.status = "Bloqueado"
                atualizar_interface(self)
                self.timer = threading.Timer(1, self.tentar_assistir)
                self.timer.start()
        
                
    def assistir(self, canal_semaforo):
        with canal_lock:
            espec_por_canal[self.canal] += 1
            self.status = "Assistindo TV"
        atualizar_interface(self)

        self.timer = threading.Timer(self.tempo_assistindo, self.finalizar_assistir, args=[canal_semaforo])
        self.timer.start()

    def finalizar_assistir(self, canal_semaforo):
        global canal_em_uso
        
        with canal_lock:
            espec_por_canal[self.canal] -= 1
            if espec_por_canal[self.canal] == 0:
                canal_em_uso = None
        canal_semaforo.release()
        self.descansar()

indice_lock = threading.Lock()       
def atualizar_interface(hospede):
    with indice_lock:
        if hospede.id_hospede not in hospede_indice:
            return
    
        index = hospede_indice[hospede.id_hospede]
        listbox_hospedes.delete(index)
        listbox_hospedes.insert(index, f"Hóspede {hospede.id_hospede} - Canal {hospede.canal} - Status: {hospede.status}")


def inicializar_semaforos():
    global n_canais, canal_semaforos, espec_por_canal
    n_canais = int(entry_n_canais.get())
    canal_semaforos = [threading.Semaphore(n_canais) for _ in range(n_canais)]
    espec_por_canal = {i+1: 0 for i in range(n_canais)}

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
