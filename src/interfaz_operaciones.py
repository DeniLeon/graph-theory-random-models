import tkinter as tk
from tkinter import ttk, messagebox
import random
import math

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



def crear_grafo_vacio(n):
    """
    Crea un grafo vacío con n nodos etiquetados de 0 a n-1.
    """
    G = nx.Graph()
    for i in range(n):
        G.add_node(i)
    return G


def resumen_texto(G, nombre="Grafo"):
    """
    Devuelve un resumen en texto del grafo.
    """
    n = G.number_of_nodes()
    m = G.number_of_edges()

    if n > 0:
        grado_promedio = sum(dict(G.degree()).values()) / n
    else:
        grado_promedio = 0

    num_componentes = nx.number_connected_components(G) if n > 0 else 0
    nodos_aislados = len(list(nx.isolates(G))) if n > 0 else 0

    texto = (
        f"{nombre}\n"
        f"Nodos: {n}\n"
        f"Aristas: {m}\n"
        f"Grado promedio: {grado_promedio:.2f}\n"
        f"Componentes conexas: {num_componentes}\n"
        f"Nodos aislados: {nodos_aislados}\n"
    )
    return texto


def renombrar_nodos_con_prefijo(G, prefijo):
    """
    Renombra los nodos de un grafo con un prefijo para evitar colisiones.
    """
    nuevo_grafo = nx.Graph()
    mapa = {}

    for nodo in G.nodes():
        nuevo_nombre = f"{prefijo}_{nodo}"
        mapa[nodo] = nuevo_nombre
        nuevo_grafo.add_node(nuevo_nombre)

    for u, v in G.edges():
        nuevo_grafo.add_edge(mapa[u], mapa[v])

    return nuevo_grafo


# =========================================================
# 2. MODELOS DE GENERACIÓN
# =========================================================

def modelo_gnm_scratch(n, m):
    """
    Modelo G(n,m) de Erdős-Rényi desde cero.
    """
    G = crear_grafo_vacio(n)

    posibles_aristas = []
    for i in range(n):
        for j in range(i + 1, n):
            posibles_aristas.append((i, j))

    max_aristas = len(posibles_aristas)
    m = min(m, max_aristas)

    aristas_elegidas = random.sample(posibles_aristas, m)

    for u, v in aristas_elegidas:
        G.add_edge(u, v)

    return G, None


def modelo_gnp_scratch(n, p):
    """
    Modelo G(n,p) de Gilbert desde cero.
    """
    G = crear_grafo_vacio(n)

    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < p:
                G.add_edge(i, j)

    return G, None


def modelo_geografico_scratch(n, radio):
    """
    Modelo geográfico simple desde cero.
    Coloca nodos aleatoriamente en el plano unitario y conecta
    si la distancia euclidiana es menor o igual al radio.
    """
    G = crear_grafo_vacio(n)
    posiciones = {}

    for i in range(n):
        x = random.random()
        y = random.random()
        posiciones[i] = (x, y)

    for i in range(n):
        for j in range(i + 1, n):
            x1, y1 = posiciones[i]
            x2, y2 = posiciones[j]

            distancia = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            if distancia <= radio:
                G.add_edge(i, j)

    return G, posiciones


def modelo_dorogovtsev_mendes_scratch(n):
    """
    Modelo Dorogovtsev-Mendes desde cero.
    Inicia con un triángulo y en cada paso:
    - elige una arista al azar
    - agrega un nuevo nodo
    - lo conecta a los dos extremos de esa arista
    """
    if n < 3:
        raise ValueError("El modelo Dorogovtsev-Mendes requiere n >= 3.")

    G = nx.Graph()

    # Triángulo inicial
    G.add_node(0)
    G.add_node(1)
    G.add_node(2)
    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(0, 2)

    nuevo_nodo = 3

    while nuevo_nodo < n:
        aristas_actuales = list(G.edges())
        u, v = random.choice(aristas_actuales)

        G.add_node(nuevo_nodo)
        G.add_edge(nuevo_nodo, u)
        G.add_edge(nuevo_nodo, v)

        nuevo_nodo += 1

    return G, None


# =========================================================
# 3. OPERACIONES ENTRE GRAFOS DESDE SCRATCH
# =========================================================

def union_grafos_scratch(G, H):
    """
    Unión:
    V(U) = V(G) ∪ V(H)
    E(U) = E(G) ∪ E(H)
    """
    G_r = renombrar_nodos_con_prefijo(G, "G")
    H_r = renombrar_nodos_con_prefijo(H, "H")

    U = nx.Graph()

    for nodo in G_r.nodes():
        U.add_node(nodo)

    for nodo in H_r.nodes():
        U.add_node(nodo)

    for u, v in G_r.edges():
        U.add_edge(u, v)

    for u, v in H_r.edges():
        U.add_edge(u, v)

    return U


def conjuncion_grafos_scratch(G, H):
    """
    Conjunción:
    G + H = G ∪ H más todas las aristas entre nodos de G y nodos de H.
    """
    G_r = renombrar_nodos_con_prefijo(G, "G")
    H_r = renombrar_nodos_con_prefijo(H, "H")

    J = nx.Graph()

    for nodo in G_r.nodes():
        J.add_node(nodo)

    for nodo in H_r.nodes():
        J.add_node(nodo)

    for u, v in G_r.edges():
        J.add_edge(u, v)

    for u, v in H_r.edges():
        J.add_edge(u, v)

    for u in G_r.nodes():
        for v in H_r.nodes():
            J.add_edge(u, v)

    return J


def producto_cartesiano_scratch(G, H):
    """
    Producto cartesiano:
    V(P) = V(G) × V(H)

    Hay arista entre (u1,v1) y (u2,v2) si:
    - u1 = u2 y (v1,v2) es arista de H
    o
    - v1 = v2 y (u1,u2) es arista de G
    """
    P = nx.Graph()

    for u in G.nodes():
        for v in H.nodes():
            P.add_node((u, v))

    for u1, u2 in G.edges():
        for v in H.nodes():
            P.add_edge((u1, v), (u2, v))

    for v1, v2 in H.edges():
        for u in G.nodes():
            P.add_edge((u, v1), (u, v2))

    return P


# =========================================================
# 4. APLICACIÓN
# =========================================================

class AppGrafos:
    def __init__(self, root):
        self.root = root
        self.root.title("Interfaz de Grafos Aleatorios")
        self.root.geometry("1700x950")
        self.root.minsize(1400, 850)

        # Variables de almacenamiento
        self.G = None
        self.H = None
        self.pos_G = None
        self.pos_H = None
        self.nombre_G = ""
        self.nombre_H = ""

        # Interfaz
        self.crear_interfaz()

    # -----------------------------------------------------
    # INTERFAZ
    # -----------------------------------------------------

    def crear_interfaz(self):
        marco_superior = tk.Frame(self.root, padx=4, pady=4)
        marco_superior.pack(side=tk.TOP, fill=tk.X)

        titulo = tk.Label(
            marco_superior,
            text="Generación y Operaciones entre Grafos",
            font=("Arial", 15, "bold")
        )
        titulo.pack(pady=2)

        # Panel de configuración
        marco_config = tk.Frame(self.root, padx=4, pady=4)
        marco_config.pack(side=tk.TOP, fill=tk.X)

        self.crear_panel_modelo_1(marco_config)
        self.crear_panel_modelo_2(marco_config)
        self.crear_panel_botones(marco_config)

        # Panel central de gráficas
        marco_graficas = tk.Frame(self.root, padx=4, pady=4)
        marco_graficas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.crear_area_graficas(marco_graficas)

        # Panel inferior de resúmenes
        marco_resumenes = tk.Frame(self.root, padx=4, pady=4)
        marco_resumenes.pack(side=tk.BOTTOM, fill=tk.X)

        self.crear_area_resumenes(marco_resumenes)

    def crear_panel_modelo_1(self, parent):
        frame = tk.LabelFrame(parent, text="Configuración Grafo 1", padx=6, pady=6)
        frame.pack(side=tk.LEFT, padx=5, pady=3)

        tk.Label(frame, text="Modelo:", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.modelo1_var = tk.StringVar(value="gnm")
        self.modelo1_combo = ttk.Combobox(
            frame,
            textvariable=self.modelo1_var,
            state="readonly",
            values=["gnm", "gnp", "geo", "dm"],
            width=10
        )
        self.modelo1_combo.grid(row=0, column=1, padx=3, pady=1)
        self.modelo1_var.trace_add('write', self.actualizar_visibilidad_1)

        self.lbl_n1 = tk.Label(frame, text="n1:", font=("Arial", 9))
        self.lbl_n1.grid(row=1, column=0, sticky="w")
        self.n1_entry = tk.Entry(frame, width=8)
        self.n1_entry.insert(0, "10")
        self.n1_entry.grid(row=1, column=1, padx=3, pady=1)

        self.lbl_m1 = tk.Label(frame, text="m1:", font=("Arial", 9))
        self.lbl_m1.grid(row=2, column=0, sticky="w")
        self.m1_entry = tk.Entry(frame, width=8)
        self.m1_entry.insert(0, "12")
        self.m1_entry.grid(row=2, column=1, padx=3, pady=1)

        self.lbl_p1 = tk.Label(frame, text="p1:", font=("Arial", 9))
        self.lbl_p1.grid(row=3, column=0, sticky="w")
        self.p1_entry = tk.Entry(frame, width=8)
        self.p1_entry.insert(0, "0.3")
        self.p1_entry.grid(row=3, column=1, padx=3, pady=1)

        self.lbl_radio1 = tk.Label(frame, text="radio1:", font=("Arial", 9))
        self.lbl_radio1.grid(row=4, column=0, sticky="w")
        self.radio1_entry = tk.Entry(frame, width=8)
        self.radio1_entry.insert(0, "0.3")
        self.radio1_entry.grid(row=4, column=1, padx=3, pady=1)

        self.actualizar_visibilidad_1()

    def actualizar_visibilidad_1(self, *args):
        modelo = self.modelo1_var.get()

        self.lbl_m1.grid_remove()
        self.m1_entry.grid_remove()
        self.lbl_p1.grid_remove()
        self.p1_entry.grid_remove()
        self.lbl_radio1.grid_remove()
        self.radio1_entry.grid_remove()

        if modelo == "gnm":
            self.lbl_m1.grid()
            self.m1_entry.grid()
        elif modelo == "gnp":
            self.lbl_p1.grid()
            self.p1_entry.grid()
        elif modelo == "geo":
            self.lbl_radio1.grid()
            self.radio1_entry.grid()

    def crear_panel_modelo_2(self, parent):
        frame = tk.LabelFrame(parent, text="Configuración Grafo 2", padx=6, pady=6)
        frame.pack(side=tk.LEFT, padx=5, pady=3)

        tk.Label(frame, text="Modelo:", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.modelo2_var = tk.StringVar(value="gnp")
        self.modelo2_combo = ttk.Combobox(
            frame,
            textvariable=self.modelo2_var,
            state="readonly",
            values=["gnm", "gnp", "geo", "dm"],
            width=10
        )
        self.modelo2_combo.grid(row=0, column=1, padx=3, pady=1)
        self.modelo2_var.trace_add('write', self.actualizar_visibilidad_2)

        self.lbl_n2 = tk.Label(frame, text="n2:", font=("Arial", 9))
        self.lbl_n2.grid(row=1, column=0, sticky="w")
        self.n2_entry = tk.Entry(frame, width=8)
        self.n2_entry.insert(0, "10")
        self.n2_entry.grid(row=1, column=1, padx=3, pady=1)

        self.lbl_m2 = tk.Label(frame, text="m2:", font=("Arial", 9))
        self.lbl_m2.grid(row=2, column=0, sticky="w")
        self.m2_entry = tk.Entry(frame, width=8)
        self.m2_entry.insert(0, "12")
        self.m2_entry.grid(row=2, column=1, padx=3, pady=1)

        self.lbl_p2 = tk.Label(frame, text="p2:", font=("Arial", 9))
        self.lbl_p2.grid(row=3, column=0, sticky="w")
        self.p2_entry = tk.Entry(frame, width=8)
        self.p2_entry.insert(0, "0.3")
        self.p2_entry.grid(row=3, column=1, padx=3, pady=1)

        self.lbl_radio2 = tk.Label(frame, text="radio2:", font=("Arial", 9))
        self.lbl_radio2.grid(row=4, column=0, sticky="w")
        self.radio2_entry = tk.Entry(frame, width=8)
        self.radio2_entry.insert(0, "0.3")
        self.radio2_entry.grid(row=4, column=1, padx=3, pady=1)

        self.actualizar_visibilidad_2()

    def actualizar_visibilidad_2(self, *args):
        modelo = self.modelo2_var.get()

        self.lbl_m2.grid_remove()
        self.m2_entry.grid_remove()
        self.lbl_p2.grid_remove()
        self.p2_entry.grid_remove()
        self.lbl_radio2.grid_remove()
        self.radio2_entry.grid_remove()

        if modelo == "gnm":
            self.lbl_m2.grid()
            self.m2_entry.grid()
        elif modelo == "gnp":
            self.lbl_p2.grid()
            self.p2_entry.grid()
        elif modelo == "geo":
            self.lbl_radio2.grid()
            self.radio2_entry.grid()

    def crear_panel_botones(self, parent):
        frame = tk.LabelFrame(parent, text="Acciones", padx=6, pady=6)
        frame.pack(side=tk.LEFT, padx=5, pady=3)

        tk.Button(frame, text="Generar grafos", width=18, command=self.generar_grafos).pack(pady=2)
        tk.Button(frame, text="Unión", width=18, command=self.mostrar_union).pack(pady=2)
        tk.Button(frame, text="Conjunción", width=18, command=self.mostrar_conjuncion).pack(pady=2)
        tk.Button(frame, text="Producto cartesiano", width=18, command=self.mostrar_producto).pack(pady=2)
        tk.Button(frame, text="Resetear", width=18, command=self.resetear).pack(pady=2)

    def crear_area_graficas(self, parent):
        self.fig, self.axes = plt.subplots(1, 3, figsize=(18, 6.8))
        self.fig.subplots_adjust(left=0.03, right=0.98, top=0.92, bottom=0.08, wspace=0.32)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.limpiar_axes()
        self.canvas.draw()

    def crear_area_resumenes(self, parent):
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X)

        self.texto_g1 = tk.Text(frame, height=5, width=38, font=("Arial", 9))
        self.texto_g1.pack(side=tk.LEFT, padx=4)

        self.texto_g2 = tk.Text(frame, height=5, width=38, font=("Arial", 9))
        self.texto_g2.pack(side=tk.LEFT, padx=4)

        self.texto_res = tk.Text(frame, height=5, width=38, font=("Arial", 9))
        self.texto_res.pack(side=tk.LEFT, padx=4)

    # -----------------------------------------------------
    # LÓGICA
    # -----------------------------------------------------

    def leer_parametros(self):
        try:
            params = {
                "modelo1": self.modelo1_var.get(),
                "n1": int(self.n1_entry.get()),
                "modelo2": self.modelo2_var.get(),
                "n2": int(self.n2_entry.get()),
            }

            if params["modelo1"] == "gnm":
                params["m1"] = int(self.m1_entry.get())
                params["p1"] = 0.0
                params["radio1"] = 0.0
            elif params["modelo1"] == "gnp":
                params["m1"] = 0
                params["p1"] = float(self.p1_entry.get())
                params["radio1"] = 0.0
            elif params["modelo1"] == "geo":
                params["m1"] = 0
                params["p1"] = 0.0
                params["radio1"] = float(self.radio1_entry.get())
            else:
                params["m1"] = 0
                params["p1"] = 0.0
                params["radio1"] = 0.0

            if params["modelo2"] == "gnm":
                params["m2"] = int(self.m2_entry.get())
                params["p2"] = 0.0
                params["radio2"] = 0.0
            elif params["modelo2"] == "gnp":
                params["m2"] = 0
                params["p2"] = float(self.p2_entry.get())
                params["radio2"] = 0.0
            elif params["modelo2"] == "geo":
                params["m2"] = 0
                params["p2"] = 0.0
                params["radio2"] = float(self.radio2_entry.get())
            else:
                params["m2"] = 0
                params["p2"] = 0.0
                params["radio2"] = 0.0

            if params["n1"] <= 0 or params["n2"] <= 0:
                raise ValueError

            return params

        except ValueError:
            messagebox.showerror("Error", "Verifica que todos los parámetros numéricos sean válidos.")
            return None

    def generar_grafo_desde_modelo(self, tipo_modelo, n, m, p, radio):
        if tipo_modelo == "gnm":
            G, pos = modelo_gnm_scratch(n, m)
            nombre = f"G(n,m) con n={n}, m={m}"

        elif tipo_modelo == "gnp":
            G, pos = modelo_gnp_scratch(n, p)
            nombre = f"G(n,p) con n={n}, p={p:.2f}"

        elif tipo_modelo == "geo":
            G, pos = modelo_geografico_scratch(n, radio)
            nombre = f"Geográfico con n={n}, radio={radio:.2f}"

        elif tipo_modelo == "dm":
            G, pos = modelo_dorogovtsev_mendes_scratch(n)
            nombre = f"Dorogovtsev-Mendes con n={n}"

        else:
            raise ValueError("Modelo no reconocido.")

        return G, pos, nombre

    def generar_grafos(self):
        params = self.leer_parametros()
        if params is None:
            return

        try:
            self.G, self.pos_G, self.nombre_G = self.generar_grafo_desde_modelo(
                params["modelo1"], params["n1"], params["m1"], params["p1"], params["radio1"]
            )

            self.H, self.pos_H, self.nombre_H = self.generar_grafo_desde_modelo(
                params["modelo2"], params["n2"], params["m2"], params["p2"], params["radio2"]
            )

            self.limpiar_axes()

            self.dibujar_grafo(
                self.axes[0],
                self.G,
                "Grafo 1",
                self.pos_G,
                "#8ecae6"
            )

            self.dibujar_grafo(
                self.axes[1],
                self.H,
                "Grafo 2",
                self.pos_H,
                "#ffb703"
            )

            self.axes[2].set_title("Resultado", fontsize=11)
            self.axes[2].axis("off")

            self.canvas.draw()

            self.actualizar_texto(self.texto_g1, resumen_texto(self.G, self.nombre_G))
            self.actualizar_texto(self.texto_g2, resumen_texto(self.H, self.nombre_H))
            self.actualizar_texto(self.texto_res, "Selecciona una operación para ver el resultado.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def mostrar_union(self):
        if not self.validar_grafos_generados():
            return

        U = union_grafos_scratch(self.G, self.H)
        pos_U = self.calcular_layout_resultado(U)

        self.axes[2].clear()
        self.dibujar_grafo(self.axes[2], U, "Unión: G ∪ H", pos_U, "#90be6d")
        self.canvas.draw()

        self.actualizar_texto(self.texto_res, resumen_texto(U, "Unión G ∪ H"))

    def mostrar_conjuncion(self):
        if not self.validar_grafos_generados():
            return

        J = conjuncion_grafos_scratch(self.G, self.H)
        pos_J = self.calcular_layout_resultado(J)

        self.axes[2].clear()
        self.dibujar_grafo(self.axes[2], J, "Conjunción: G + H", pos_J, "#f28482")
        self.canvas.draw()

        self.actualizar_texto(self.texto_res, resumen_texto(J, "Conjunción G + H"))

    def mostrar_producto(self):
        if not self.validar_grafos_generados():
            return

        P = producto_cartesiano_scratch(self.G, self.H)
        pos_P = self.calcular_layout_resultado(P, tipo="producto")

        self.axes[2].clear()
        self.dibujar_grafo(self.axes[2], P, "Producto cartesiano: G × H", pos_P, "#cdb4db")
        self.canvas.draw()

        self.actualizar_texto(self.texto_res, resumen_texto(P, "Producto cartesiano G × H"))

    def resetear(self):
        self.G = None
        self.H = None
        self.pos_G = None
        self.pos_H = None
        self.nombre_G = ""
        self.nombre_H = ""

        self.limpiar_axes()
        self.canvas.draw()

        self.actualizar_texto(self.texto_g1, "")
        self.actualizar_texto(self.texto_g2, "")
        self.actualizar_texto(self.texto_res, "")

    # -----------------------------------------------------
    # VISUALIZACIÓN
    # -----------------------------------------------------

    def limpiar_axes(self):
        for ax in self.axes:
            ax.clear()
            ax.axis("off")

        self.axes[0].set_title("Grafo 1", fontsize=11)
        self.axes[1].set_title("Grafo 2", fontsize=11)
        self.axes[2].set_title("Resultado", fontsize=11)

    def calcular_layout_resultado(self, G, tipo="general"):
        n = G.number_of_nodes()

        # Para grafos pequeños
        if n <= 20:
            return nx.spring_layout(G, seed=42, k=1.4, iterations=150)

        # Para grafos medianos
        if n <= 80:
            if tipo == "producto":
                return nx.kamada_kawai_layout(G)
            return nx.spring_layout(G, seed=42, k=1.0, iterations=180)

        # Para grafos grandes
        if tipo == "producto":
            return nx.spring_layout(G, seed=42, k=0.9, iterations=220)

        return nx.spring_layout(G, seed=42, k=0.7, iterations=180)

    def dibujar_grafo(self, ax, G, titulo, pos=None, color_nodos="lightblue"):
        n = G.number_of_nodes()

        if pos is None:
            if n <= 20:
                pos = nx.spring_layout(G, seed=42, k=1.3, iterations=120)
            elif n <= 80:
                pos = nx.spring_layout(G, seed=42, k=1.0, iterations=150)
            else:
                pos = nx.spring_layout(G, seed=42, k=0.8, iterations=180)

        if n <= 15:
            node_size = 240
            font_size = 7
            edge_width = 1.0
        elif n <= 35:
            node_size = 170
            font_size = 5
            edge_width = 0.9
        elif n <= 80:
            node_size = 110
            font_size = 4
            edge_width = 0.8
        else:
            node_size = 70
            font_size = 3
            edge_width = 0.6

        nx.draw(
            G,
            pos,
            ax=ax,
            with_labels=True,
            node_size=node_size,
            node_color=color_nodos,
            edge_color="gray",
            width=edge_width,
            font_size=font_size
        )

        ax.set_title(
            f"{titulo}\n|V|={G.number_of_nodes()}   |E|={G.number_of_edges()}",
            fontsize=10
        )
        ax.axis("off")

    def actualizar_texto(self, widget, texto):
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, texto)

    def validar_grafos_generados(self):
        if self.G is None or self.H is None:
            messagebox.showwarning("Aviso", "Primero debes generar los dos grafos.")
            return False
        return True


# =========================================================
# 5. MAIN
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGrafos(root)
    root.mainloop()