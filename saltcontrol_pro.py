"""
====================================================================
  SaltControl Pro - Version Unificada
  Sistema de Registro y Gestion de Saltos con Garrocha
====================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

MAX_ATLETAS = 15
ARCHIVO_DATOS_ARREGLOS = "registro_saltos.json"
ARCHIVO_DATOS_ARBOL = "registro_arbol.json"


# ======================================================================
#   ============  ESTRUCTURA DINAMICA: NODO DEL ARBOL  ================
# ======================================================================
class NodoAtleta:
    """Representa un nodo del arbol. Cada nodo es un atleta."""

    def __init__(self, nombre, mejor_marca=None):
        self.nombre = nombre
        self.mejor_marca = mejor_marca      # float o None (sin salto valido)
        self.izquierdo = None                # subarbol con nombres menores
        self.derecho = None                  # subarbol con nombres mayores


# ======================================================================
#   ============  ESTRUCTURA DINAMICA: ARBOL BINARIO  =================
#   ============  DE BUSQUEDA (BST)                    =================
# ======================================================================
class ArbolBinarioBusqueda:

    def __init__(self):
        self.raiz = None
        self.cantidad = 0

    # ------------------------------------------------------------
    # INSERCION
    # ------------------------------------------------------------
    def insertar(self, nombre, mejor_marca=None):
        if self.raiz is None:
            self.raiz = NodoAtleta(nombre, mejor_marca)
            self.cantidad += 1
            return True
        return self._insertar_rec(self.raiz, nombre, mejor_marca)

    def _insertar_rec(self, nodo, nombre, mejor_marca):
        clave_nueva = nombre.lower()
        clave_actual = nodo.nombre.lower()

        if clave_nueva == clave_actual:
            return False  # ya existe, no se duplica

        if clave_nueva < clave_actual:
            if nodo.izquierdo is None:
                nodo.izquierdo = NodoAtleta(nombre, mejor_marca)
                self.cantidad += 1
                return True
            return self._insertar_rec(nodo.izquierdo, nombre, mejor_marca)
        else:
            if nodo.derecho is None:
                nodo.derecho = NodoAtleta(nombre, mejor_marca)
                self.cantidad += 1
                return True
            return self._insertar_rec(nodo.derecho, nombre, mejor_marca)

    # ------------------------------------------------------------
    # BUSQUEDA
    # ------------------------------------------------------------
    def buscar(self, nombre):
        return self._buscar_rec(self.raiz, nombre, 0, [])

    def _buscar_rec(self, nodo, nombre, comparaciones, camino):
        if nodo is None:
            return None, comparaciones, camino

        comparaciones += 1
        camino = camino + [nodo.nombre]
        clave_buscada = nombre.lower()
        clave_actual = nodo.nombre.lower()

        if clave_buscada == clave_actual:
            return nodo, comparaciones, camino
        elif clave_buscada < clave_actual:
            return self._buscar_rec(nodo.izquierdo, nombre, comparaciones, camino)
        else:
            return self._buscar_rec(nodo.derecho, nombre, comparaciones, camino)

    # ------------------------------------------------------------
    # ELIMINACION (3 casos clasicos)
    # ------------------------------------------------------------
    def eliminar(self, nombre):
        self.raiz, eliminado = self._eliminar_rec(self.raiz, nombre)
        if eliminado:
            self.cantidad -= 1
        return eliminado

    def _eliminar_rec(self, nodo, nombre):
        if nodo is None:
            return nodo, False

        clave_buscada = nombre.lower()
        clave_actual = nodo.nombre.lower()

        if clave_buscada < clave_actual:
            nodo.izquierdo, eliminado = self._eliminar_rec(
                nodo.izquierdo, nombre)
            return nodo, eliminado
        elif clave_buscada > clave_actual:
            nodo.derecho, eliminado = self._eliminar_rec(nodo.derecho, nombre)
            return nodo, eliminado
        else:
            # Caso 1: nodo hoja (sin hijos)
            if nodo.izquierdo is None and nodo.derecho is None:
                return None, True
            # Caso 2: un solo hijo -> el nodo se reemplaza por su hijo
            if nodo.izquierdo is None:
                return nodo.derecho, True
            if nodo.derecho is None:
                return nodo.izquierdo, True
            # Caso 3: dos hijos -> se usa el sucesor inorden
            sucesor = self._minimo(nodo.derecho)
            nodo.nombre = sucesor.nombre
            nodo.mejor_marca = sucesor.mejor_marca
            nodo.derecho, _ = self._eliminar_rec(nodo.derecho, sucesor.nombre)
            return nodo, True

    def _minimo(self, nodo):
        while nodo.izquierdo is not None:
            nodo = nodo.izquierdo
        return nodo

    def _maximo(self, nodo):
        while nodo.derecho is not None:
            nodo = nodo.derecho
        return nodo

    def atleta_minimo(self):
        return None if self.raiz is None else self._minimo(self.raiz)

    def atleta_maximo(self):
        return None if self.raiz is None else self._maximo(self.raiz)

    # ------------------------------------------------------------
    # RECORRIDOS
    # ------------------------------------------------------------
    def recorrido_inorden(self):
        resultado = []
        self._inorden_rec(self.raiz, resultado)
        return resultado

    def _inorden_rec(self, nodo, resultado):
        if nodo is not None:
            self._inorden_rec(nodo.izquierdo, resultado)
            resultado.append(nodo)
            self._inorden_rec(nodo.derecho, resultado)

    def recorrido_preorden(self):
        resultado = []
        self._preorden_rec(self.raiz, resultado)
        return resultado

    def _preorden_rec(self, nodo, resultado):
        if nodo is not None:
            resultado.append(nodo)
            self._preorden_rec(nodo.izquierdo, resultado)
            self._preorden_rec(nodo.derecho, resultado)

    def recorrido_postorden(self):
        resultado = []
        self._postorden_rec(self.raiz, resultado)
        return resultado

    def _postorden_rec(self, nodo, resultado):
        if nodo is not None:
            self._postorden_rec(nodo.izquierdo, resultado)
            self._postorden_rec(nodo.derecho, resultado)
            resultado.append(nodo)

    # ------------------------------------------------------------
    # ALTURA DEL ARBOL
    # ------------------------------------------------------------
    def altura(self):
        return self._altura_rec(self.raiz)

    def _altura_rec(self, nodo):
        if nodo is None:
            return 0
        return 1 + max(self._altura_rec(nodo.izquierdo), self._altura_rec(nodo.derecho))

    def vaciar(self):
        self.raiz = None
        self.cantidad = 0


# ======================================================================
#   PESTANA 1: REGISTRO POR ARREGLOS / MATRIZ (ESTRUCTURAS SECUENCIALES)
# ======================================================================
class PestanaArreglos(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#eef2f7")

        # ---------------- ESTRUCTURAS DE DATOS (ARREGLOS) ----------------
        self.atletas = []      # Arreglo unidimensional de nombres (max 15)
        self.alturas = []      # Arreglo unidimensional de alturas (columna T)
        # Arreglo bidimensional (matriz) atletas x alturas
        self.resultados = []

        self._construir_interfaz()
        self._cargar_datos_ejemplo()
        self._refrescar_tabla()

    # ------------------------------------------------
    def _construir_interfaz(self):
        subtitulo = tk.Label(
            self, text="Estructuras secuenciales: arreglos y matriz (arreglo bidimensional)",
            font=("Segoe UI", 10, "italic"), bg="#eef2f7", fg="#446")
        subtitulo.pack(pady=(10, 6))

        panel_top = tk.Frame(self, bg="#eef2f7")
        panel_top.pack(fill="x", padx=15)

        frame_atleta = tk.LabelFrame(panel_top, text=" Atletas (max. 15) ",
                                     bg="#ffffff", font=("Segoe UI", 10, "bold"))
        frame_atleta.pack(side="left", fill="both",
                          expand=True, padx=(0, 8), pady=4)
        tk.Label(frame_atleta, text="Nombre:", bg="#ffffff").grid(
            row=0, column=0, padx=5, pady=6)
        self.entry_atleta = tk.Entry(frame_atleta, width=20)
        self.entry_atleta.grid(row=0, column=1, padx=5)
        tk.Button(frame_atleta, text="Agregar atleta", command=self.agregar_atleta,
                  bg="#2e7d32", fg="white").grid(row=0, column=2, padx=6)

        frame_altura = tk.LabelFrame(panel_top, text=" Alturas / Columna T (m) ",
                                     bg="#ffffff", font=("Segoe UI", 10, "bold"))
        frame_altura.pack(side="left", fill="both",
                          expand=True, padx=(8, 0), pady=4)
        tk.Label(frame_altura, text="Altura:", bg="#ffffff").grid(
            row=0, column=0, padx=5, pady=6)
        self.entry_altura = tk.Entry(frame_altura, width=10)
        self.entry_altura.grid(row=0, column=1, padx=5)
        tk.Button(frame_altura, text="Agregar altura", command=self.agregar_altura,
                  bg="#1565c0", fg="white").grid(row=0, column=2, padx=6)

        frame_registro = tk.LabelFrame(self, text=" Registrar salto ",
                                       bg="#ffffff", font=("Segoe UI", 10, "bold"))
        frame_registro.pack(fill="x", padx=15, pady=8)
        tk.Label(frame_registro, text="Atleta:", bg="#ffffff").grid(
            row=0, column=0, padx=6, pady=8)
        self.combo_atleta = ttk.Combobox(
            frame_registro, width=20, state="readonly")
        self.combo_atleta.grid(row=0, column=1, padx=6)
        tk.Label(frame_registro, text="Altura:",
                 bg="#ffffff").grid(row=0, column=2, padx=6)
        self.combo_altura = ttk.Combobox(
            frame_registro, width=10, state="readonly")
        self.combo_altura.grid(row=0, column=3, padx=6)
        tk.Label(frame_registro, text="Resultado:",
                 bg="#ffffff").grid(row=0, column=4, padx=6)
        self.resultado_var = tk.StringVar(value="X")
        tk.Radiobutton(frame_registro, text="X (valido)", variable=self.resultado_var,
                       value="X", bg="#ffffff").grid(row=0, column=5)
        tk.Radiobutton(frame_registro, text="O (nulo)", variable=self.resultado_var,
                       value="O", bg="#ffffff").grid(row=0, column=6)
        tk.Button(frame_registro, text="Registrar", command=self.registrar_salto,
                  bg="#ef6c00", fg="white", width=12).grid(row=0, column=7, padx=10)

        frame_tabla = tk.LabelFrame(self, text=" Tabla de resultados (arreglo bidimensional) ",
                                    bg="#ffffff", font=("Segoe UI", 10, "bold"))
        frame_tabla.pack(fill="both", expand=True, padx=15, pady=8)
        self.tree = ttk.Treeview(frame_tabla, show="headings", height=9)
        self.tree.pack(fill="both", expand=True, padx=8, pady=8, side="left")
        scrollbar = ttk.Scrollbar(
            frame_tabla, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        frame_acciones = tk.Frame(self, bg="#eef2f7")
        frame_acciones.pack(fill="x", padx=15, pady=(0, 8))
        tk.Button(frame_acciones, text="Ver mejor marca por atleta",
                  command=self.mostrar_mejores_marcas, bg="#6a1b9a", fg="white").pack(side="left", padx=4)
        tk.Button(frame_acciones, text="Ordenar por mejor marca (burbuja)",
                  command=self.ordenar_por_mejor_marca, bg="#c62828", fg="white").pack(side="left", padx=4)
        tk.Button(frame_acciones, text="Buscar atleta (lineal)",
                  command=self.buscar_atleta, bg="#0277bd", fg="white").pack(side="left", padx=4)
        tk.Button(frame_acciones, text="Guardar datos", command=self.guardar_datos,
                  bg="#00695c", fg="white").pack(side="left", padx=4)
        tk.Button(frame_acciones, text="Cargar datos", command=self.cargar_datos,
                  bg="#5d4037", fg="white").pack(side="left", padx=4)

        self.status = tk.Label(self, text="Listo.",
                               bg="#eef2f7", fg="#333", anchor="w")
        self.status.pack(fill="x", padx=15, pady=(0, 8))

    # ------------------------------------------------------------------
    def _cargar_datos_ejemplo(self):
        self.alturas = [2.00, 2.10, 2.20, 2.30, 2.35, 2.40]
        nombres = ["Garcia", "Perez", "Gil", "Mortimer"]
        matriz_ejemplo = [
            ["X", "O", "X", "X", "X", "O"],
            ["O", "X", "X", "O", "X", "O"],
            ["O", "O", "O", "O", "O", "O"],
            ["O", "O", "O", "X", "X", "X"],
        ]
        for nombre, fila in zip(nombres, matriz_ejemplo):
            self.atletas.append(nombre)
            self.resultados.append(fila[:])
        self._actualizar_combos()

    # ---------------------------------------------------
    # LOGICA: ATLETAS
    # ---------------------------------------------------
    def agregar_atleta(self):
        nombre = self.entry_atleta.get().strip()
        if not nombre:
            messagebox.showwarning("Atencion", "Escriba el nombre del atleta.")
            return
        if len(self.atletas) >= MAX_ATLETAS:
            messagebox.showerror("Limite alcanzado",
                                 f"El grupo ya tiene el maximo de {MAX_ATLETAS} atletas.")
            return
        if nombre in self.atletas:
            messagebox.showwarning("Atencion", "Ese atleta ya existe.")
            return

        self.atletas.append(nombre)
        self.resultados.append(["O"] * len(self.alturas))

        self.entry_atleta.delete(0, tk.END)
        self._actualizar_combos()
        self._refrescar_tabla()
        self.status.config(
            text=f"Atleta '{nombre}' agregado ({len(self.atletas)}/{MAX_ATLETAS}).")

    # ------------------------------------------------------------------
    # LOGICA: ALTURAS (columnas)
    # ------------------------------------------------------------------
    def agregar_altura(self):
        texto = self.entry_altura.get().strip().replace(",", ".")
        try:
            valor = float(texto)
        except ValueError:
            messagebox.showwarning(
                "Atencion", "Ingrese una altura valida, ej: 2.45")
            return
        if valor in self.alturas:
            messagebox.showwarning(
                "Atencion", "Esa altura ya existe en la tabla.")
            return

        self.alturas.append(valor)
        self.alturas.sort()
        indice_nuevo = self.alturas.index(valor)
        for fila in self.resultados:
            fila.insert(indice_nuevo, "O")

        self.entry_altura.delete(0, tk.END)
        self._actualizar_combos()
        self._refrescar_tabla()
        self.status.config(text=f"Altura {valor:.2f} m agregada a la tabla.")

    # ------------------------------------------------------------------
    # LOGICA: REGISTRO DE SALTO (escritura en la matriz)
    # ------------------------------------------------------------------
    def registrar_salto(self):
        atleta = self.combo_atleta.get()
        altura = self.combo_altura.get()
        resultado = self.resultado_var.get()

        if not atleta or not altura:
            messagebox.showwarning("Atencion", "Seleccione atleta y altura.")
            return

        i = self.atletas.index(atleta)
        j = self.alturas.index(float(altura))
        self.resultados[i][j] = resultado

        self._refrescar_tabla()
        self.status.config(
            text=f"Registrado: {atleta} - {altura} m -> {resultado}")

    # ------------------------------------------------------------------
    def _actualizar_combos(self):
        self.combo_atleta["values"] = self.atletas
        self.combo_altura["values"] = [f"{a:.2f}" for a in self.alturas]

    def _refrescar_tabla(self):
        columnas = ["Fila \\ Columna T"] + [f"{a:.2f}" for a in self.alturas]
        self.tree["columns"] = columnas
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=95, anchor="center")

        for fila_id in self.tree.get_children():
            self.tree.delete(fila_id)

        for i in range(len(self.atletas)):
            valores = [self.atletas[i]] + self.resultados[i]
            self.tree.insert("", "end", values=valores)

    # ------------------------------------------------------------------
    # ANALISIS: MEJOR MARCA POR ATLETA (recorrido de la matriz)
    # ------------------------------------------------------------------
    def mostrar_mejores_marcas(self):
        if not self.atletas:
            messagebox.showinfo(
                "Mejores marcas", "No hay atletas registrados.")
            return
        reporte = "MEJOR MARCA VALIDA POR ATLETA\n" + "-" * 34 + "\n"
        for i in range(len(self.atletas)):
            mejor = self._mejor_marca(i)
            marca = f"{mejor:.2f} m" if mejor is not None else "Sin salto valido"
            reporte += f"{self.atletas[i]:<12} -> {marca}\n"
        messagebox.showinfo("Mejores marcas", reporte)

    def _mejor_marca(self, i):
        mejor = None
        for j in range(len(self.alturas)):
            if self.resultados[i][j] == "X":
                if mejor is None or self.alturas[j] > mejor:
                    mejor = self.alturas[j]
        return mejor

    # ------------------------------------------------------------------
    # METODO DE ORDENAMIENTO: BUBBLE SORT (ordenamiento de burbuja)
    # ------------------------------------------------------------------
    def ordenar_por_mejor_marca(self):
        n = len(self.atletas)
        if n < 2:
            messagebox.showinfo(
                "Ordenar", "Se necesitan al menos 2 atletas para ordenar.")
            return

        marcas = [self._mejor_marca(i) for i in range(n)]
        intercambios_totales = 0
        for pasada in range(n - 1):
            hubo_intercambio = False
            for j in range(n - 1 - pasada):
                a_val = marcas[j] if marcas[j] is not None else -1
                b_val = marcas[j + 1] if marcas[j + 1] is not None else -1
                if a_val < b_val:
                    marcas[j], marcas[j + 1] = marcas[j + 1], marcas[j]
                    self.atletas[j], self.atletas[j +
                                                  1] = self.atletas[j + 1], self.atletas[j]
                    self.resultados[j], self.resultados[j + 1] = \
                        self.resultados[j + 1], self.resultados[j]
                    hubo_intercambio = True
                    intercambios_totales += 1
            if not hubo_intercambio:
                break

        self._actualizar_combos()
        self._refrescar_tabla()
        self.status.config(
            text=f"Atletas ordenados por mejor marca (burbuja, {intercambios_totales} intercambios).")

    # ------------------------------------------------------------------
    # METODO DE BUSQUEDA: BUSQUEDA LINEAL (Linear Search)
    # ------------------------------------------------------------------
    def buscar_atleta(self):
        if not self.atletas:
            messagebox.showinfo("Buscar atleta", "No hay atletas registrados.")
            return

        nombre = simpledialog.askstring(
            "Buscar atleta", "Nombre del atleta a buscar:")
        if not nombre:
            return
        nombre = nombre.strip()

        comparaciones = 0
        indice_encontrado = -1
        for i in range(len(self.atletas)):
            comparaciones += 1
            if self.atletas[i].lower() == nombre.lower():
                indice_encontrado = i
                break

        if indice_encontrado == -1:
            messagebox.showinfo(
                "Buscar atleta",
                f"No se encontro al atleta '{nombre}'.\nComparaciones realizadas: {comparaciones}")
            self.status.config(
                text=f"Busqueda: '{nombre}' no encontrado ({comparaciones} comparaciones).")
            return

        mejor = self._mejor_marca(indice_encontrado)
        marca_txt = f"{mejor:.2f} m" if mejor is not None else "Sin salto valido"

        fila_id = self.tree.get_children()[indice_encontrado]
        self.tree.selection_set(fila_id)
        self.tree.see(fila_id)

        messagebox.showinfo(
            "Buscar atleta",
            f"Atleta encontrado: {self.atletas[indice_encontrado]}\n"
            f"Posicion en el arreglo: {indice_encontrado}\n"
            f"Mejor marca valida: {marca_txt}\n"
            f"Comparaciones realizadas: {comparaciones}")
        self.status.config(
            text=f"Busqueda: '{nombre}' encontrado en posicion "
            f"{indice_encontrado} ({comparaciones} comparaciones).")

    # ------------------------------------------------------------------
    # PERSISTENCIA (guardar / cargar en formato JSON)
    # ------------------------------------------------------------------
    def guardar_datos(self):
        datos = {"alturas": self.alturas, "atletas": self.atletas,
                 "resultados": self.resultados}
        with open(ARCHIVO_DATOS_ARREGLOS, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        self.status.config(
            text=f"Datos guardados en '{ARCHIVO_DATOS_ARREGLOS}'.")
        messagebox.showinfo(
            "Guardado", "La informacion se guardo correctamente.")

    def cargar_datos(self):
        if not os.path.exists(ARCHIVO_DATOS_ARREGLOS):
            messagebox.showwarning(
                "Atencion", "No existe un archivo de datos guardado.")
            return
        with open(ARCHIVO_DATOS_ARREGLOS, "r", encoding="utf-8") as f:
            datos = json.load(f)
        self.alturas = datos["alturas"]
        self.atletas = datos["atletas"]
        self.resultados = datos["resultados"]
        self._actualizar_combos()
        self._refrescar_tabla()
        self.status.config(text="Datos cargados correctamente.")


# ======================================================================
#   PESTANA 2: GESTION POR ARBOL BINARIO DE BUSQUEDA (ESTRUCTURA DINAMICA)
# ======================================================================
class PestanaArbol(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#eef2f7")
        self.arbol = ArbolBinarioBusqueda()
        self._construir_interfaz()
        self._cargar_datos_ejemplo()
        self._refrescar_todo()

    # ------------------------------------------------------------
    def _construir_interfaz(self):
        subtitulo = tk.Label(
            self, text="Estructura dinamica: Arbol Binario de Busqueda (BST) ordenado por nombre",
            font=("Segoe UI", 10, "italic"), bg="#eef2f7", fg="#446")
        subtitulo.pack(pady=(10, 6))

        panel_ops = tk.Frame(self, bg="#eef2f7")
        panel_ops.pack(fill="x", padx=15)

        frame_insertar = tk.LabelFrame(panel_ops, text=" Insertar atleta ",
                                       bg="#ffffff", font=("Segoe UI", 10, "bold"))
        frame_insertar.pack(side="left", fill="both",
                            expand=True, padx=(0, 6), pady=4)
        tk.Label(frame_insertar, text="Nombre:", bg="#ffffff").grid(
            row=0, column=0, padx=4, pady=6)
        self.entry_nombre = tk.Entry(frame_insertar, width=14)
        self.entry_nombre.grid(row=0, column=1, padx=4)
        tk.Label(frame_insertar, text="Mejor marca (m):",
                 bg="#ffffff").grid(row=1, column=0, padx=4)
        self.entry_marca = tk.Entry(frame_insertar, width=14)
        self.entry_marca.grid(row=1, column=1, padx=4)
        tk.Button(frame_insertar, text="Insertar en el arbol", command=self.insertar_atleta,
                  bg="#2e7d32", fg="white").grid(row=2, column=0, columnspan=2, pady=6)

        frame_buscar = tk.LabelFrame(panel_ops, text=" Buscar atleta ",
                                     bg="#ffffff", font=("Segoe UI", 10, "bold"))
        frame_buscar.pack(side="left", fill="both",
                          expand=True, padx=6, pady=4)
        tk.Label(frame_buscar, text="Nombre:", bg="#ffffff").grid(
            row=0, column=0, padx=4, pady=6)
        self.entry_buscar = tk.Entry(frame_buscar, width=14)
        self.entry_buscar.grid(row=0, column=1, padx=4)
        tk.Button(frame_buscar, text="Buscar", command=self.buscar_atleta,
                  bg="#0277bd", fg="white").grid(row=1, column=0, columnspan=2, pady=6)

        frame_eliminar = tk.LabelFrame(panel_ops, text=" Eliminar atleta ",
                                       bg="#ffffff", font=("Segoe UI", 10, "bold"))
        frame_eliminar.pack(side="left", fill="both",
                            expand=True, padx=(6, 0), pady=4)
        tk.Label(frame_eliminar, text="Nombre:", bg="#ffffff").grid(
            row=0, column=0, padx=4, pady=6)
        self.entry_eliminar = tk.Entry(frame_eliminar, width=14)
        self.entry_eliminar.grid(row=0, column=1, padx=4)
        tk.Button(frame_eliminar, text="Eliminar", command=self.eliminar_atleta,
                  bg="#c62828", fg="white").grid(row=1, column=0, columnspan=2, pady=6)

        panel_info = tk.Frame(self, bg="#eef2f7")
        panel_info.pack(fill="x", padx=15, pady=(6, 0))

        frame_recorridos = tk.LabelFrame(panel_info, text=" Recorridos del arbol ",
                                         bg="#ffffff", font=("Segoe UI", 10, "bold"))
        frame_recorridos.pack(side="left", fill="both",
                              expand=True, padx=(0, 6))
        tk.Button(frame_recorridos, text="Inorden", command=lambda: self.mostrar_recorrido("inorden"),
                  bg="#6a1b9a", fg="white", width=10).pack(side="left", padx=6, pady=6)
        tk.Button(frame_recorridos, text="Preorden", command=lambda: self.mostrar_recorrido("preorden"),
                  bg="#6a1b9a", fg="white", width=10).pack(side="left", padx=6, pady=6)
        tk.Button(frame_recorridos, text="Postorden", command=lambda: self.mostrar_recorrido("postorden"),
                  bg="#6a1b9a", fg="white", width=10).pack(side="left", padx=6, pady=6)

        frame_stats = tk.LabelFrame(panel_info, text=" Informacion del arbol ",
                                    bg="#ffffff", font=("Segoe UI", 10, "bold"))
        frame_stats.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self.label_stats = tk.Label(frame_stats, text="", bg="#ffffff", justify="left",
                                    font=("Consolas", 10))
        self.label_stats.pack(padx=8, pady=8, anchor="w")

        panel_central = tk.Frame(self, bg="#eef2f7")
        panel_central.pack(fill="both", expand=True, padx=15, pady=8)

        frame_canvas = tk.LabelFrame(panel_central, text=" Representacion grafica del arbol ",
                                     bg="#ffffff", font=("Segoe UI", 10, "bold"))
        frame_canvas.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.canvas = tk.Canvas(frame_canvas, bg="white", height=340)
        scrollbar_h = ttk.Scrollbar(
            frame_canvas, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=scrollbar_h.set)
        self.canvas.pack(fill="both", expand=True,
                         padx=6, pady=(6, 0), side="top")
        scrollbar_h.pack(fill="x", padx=6, pady=(0, 6), side="bottom")

        frame_salida = tk.LabelFrame(panel_central, text=" Salida / resultados ",
                                     bg="#ffffff", font=("Segoe UI", 10, "bold"))
        frame_salida.pack(side="left", fill="both", expand=True, padx=(6, 0))
        self.texto_salida = tk.Text(
            frame_salida, width=42, font=("Consolas", 10))
        self.texto_salida.pack(fill="both", expand=True, padx=6, pady=6)

        frame_acciones = tk.Frame(self, bg="#eef2f7")
        frame_acciones.pack(fill="x", padx=15, pady=(0, 8))
        tk.Button(frame_acciones, text="Guardar datos", command=self.guardar_datos,
                  bg="#00695c", fg="white").pack(side="left", padx=4)
        tk.Button(frame_acciones, text="Cargar datos", command=self.cargar_datos,
                  bg="#5d4037", fg="white").pack(side="left", padx=4)

        self.status = tk.Label(self, text="Listo.",
                               bg="#eef2f7", fg="#333", anchor="w")
        self.status.pack(fill="x", padx=15, pady=(0, 8))

    # ------------------------------------------------------------
    def _cargar_datos_ejemplo(self):
        ejemplo = [
            ("Mortimer", 2.40), ("Garcia", 2.35), ("Perez", 2.35),
            ("Gil", None), ("Alvarez", 2.10), ("Torres", 2.20),
            ("Diaz", 2.15), ("Ramirez", 2.30),
        ]
        for nombre, marca in ejemplo:
            self.arbol.insertar(nombre, marca)

    # ------------------------------------------------------------
    # OPERACION: INSERTAR
    # ------------------------------------------------------------
    def insertar_atleta(self):
        nombre = self.entry_nombre.get().strip()
        marca_txt = self.entry_marca.get().strip().replace(",", ".")

        if not nombre:
            messagebox.showwarning("Atencion", "Escriba el nombre del atleta.")
            return

        marca = None
        if marca_txt:
            try:
                marca = float(marca_txt)
            except ValueError:
                messagebox.showwarning(
                    "Atencion", "La marca debe ser un numero, ej: 2.30")
                return

        insertado = self.arbol.insertar(nombre, marca)
        if not insertado:
            messagebox.showwarning(
                "Atencion", f"El atleta '{nombre}' ya existe en el arbol.")
            return

        self.entry_nombre.delete(0, tk.END)
        self.entry_marca.delete(0, tk.END)
        self._refrescar_todo()
        self.status.config(text=f"Atleta '{nombre}' insertado en el arbol.")

    # ------------------------------------------------------------
    # OPERACION: BUSCAR
    # ------------------------------------------------------------
    def buscar_atleta(self):
        nombre = self.entry_buscar.get().strip()
        if not nombre:
            messagebox.showwarning("Atencion", "Escriba el nombre a buscar.")
            return

        nodo, comparaciones, camino = self.arbol.buscar(nombre)

        self.texto_salida.delete("1.0", tk.END)
        if nodo is None:
            self.texto_salida.insert(
                tk.END, f"No se encontro a '{nombre}'.\n\n")
            self.texto_salida.insert(
                tk.END, f"Comparaciones realizadas: {comparaciones}\n")
            self.texto_salida.insert(
                tk.END, f"Camino recorrido: {' -> '.join(camino)}\n")
            self.status.config(
                text=f"'{nombre}' no encontrado ({comparaciones} comparaciones).")
        else:
            marca_txt = f"{nodo.mejor_marca:.2f} m" if nodo.mejor_marca is not None else "Sin salto valido"
            self.texto_salida.insert(
                tk.END, f"Atleta encontrado: {nodo.nombre}\n")
            self.texto_salida.insert(tk.END, f"Mejor marca: {marca_txt}\n\n")
            self.texto_salida.insert(
                tk.END, f"Comparaciones realizadas: {comparaciones}\n")
            self.texto_salida.insert(
                tk.END, f"Camino recorrido: {' -> '.join(camino)}\n")
            self.status.config(
                text=f"'{nombre}' encontrado ({comparaciones} comparaciones).")

        self._dibujar_arbol(resaltar=camino)

    # ------------------------------------------------------------
    # OPERACION: ELIMINAR
    # ------------------------------------------------------------
    def eliminar_atleta(self):
        nombre = self.entry_eliminar.get().strip()
        if not nombre:
            messagebox.showwarning("Atencion", "Escriba el nombre a eliminar.")
            return

        eliminado = self.arbol.eliminar(nombre)
        if eliminado:
            self.entry_eliminar.delete(0, tk.END)
            self._refrescar_todo()
            self.status.config(text=f"Atleta '{nombre}' eliminado del arbol.")
        else:
            messagebox.showinfo(
                "Eliminar", f"El atleta '{nombre}' no existe en el arbol.")

    # ------------------------------------------------------------
    # OPERACION: RECORRIDOS
    # ------------------------------------------------------------
    def mostrar_recorrido(self, tipo):
        if tipo == "inorden":
            nodos = self.arbol.recorrido_inorden()
            titulo = "RECORRIDO INORDEN (alfabetico)"
        elif tipo == "preorden":
            nodos = self.arbol.recorrido_preorden()
            titulo = "RECORRIDO PREORDEN"
        else:
            nodos = self.arbol.recorrido_postorden()
            titulo = "RECORRIDO POSTORDEN"

        self.texto_salida.delete("1.0", tk.END)
        self.texto_salida.insert(tk.END, f"{titulo}\n" + "-" * 30 + "\n")
        for i, nodo in enumerate(nodos, start=1):
            marca_txt = f"{nodo.mejor_marca:.2f} m" if nodo.mejor_marca is not None else "Sin salto valido"
            self.texto_salida.insert(
                tk.END, f"{i}. {nodo.nombre:<12} {marca_txt}\n")

        self.status.config(
            text=f"Recorrido {tipo} generado ({len(nodos)} atletas).")

    # ------------------------------------------------------------
    def _refrescar_todo(self):
        minimo = self.arbol.atleta_minimo()
        maximo = self.arbol.atleta_maximo()
        texto_stats = (
            f"Cantidad de atletas : {self.arbol.cantidad}\n"
            f"Altura del arbol    : {self.arbol.altura()}\n"
            f"Primero (A-Z)       : {minimo.nombre if minimo else '-'}\n"
            f"Ultimo (A-Z)        : {maximo.nombre if maximo else '-'}\n"
        )
        self.label_stats.config(text=texto_stats)
        self._dibujar_arbol()

    # ------------------------------------------------------------
    # DIBUJO DEL ARBOL EN EL CANVAS
    # ------------------------------------------------------------
    def _dibujar_arbol(self, resaltar=None):
        self.canvas.delete("all")
        if self.arbol.raiz is None:
            self.canvas.create_text(
                200, 100, text="(arbol vacio)", font=("Segoe UI", 12))
            return

        resaltar = set(resaltar) if resaltar else set()

        self._contador_x = 0
        posiciones = {}
        self._asignar_posiciones(self.arbol.raiz, 0, posiciones)

        total_nodos = self.arbol.cantidad
        paso_x = 90
        paso_y = 80
        altura_arbol = self.arbol.altura()
        ancho_total = (total_nodos + 1) * paso_x
        alto_total = (altura_arbol + 1) * paso_y + 40

        self._dibujar_lineas(self.arbol.raiz, posiciones, paso_x, paso_y)
        self._dibujar_nodos(self.arbol.raiz, posiciones,
                            paso_x, paso_y, resaltar)

        self.canvas.configure(scrollregion=(0, 0, ancho_total, alto_total))

    def _asignar_posiciones(self, nodo, profundidad, posiciones):
        if nodo is None:
            return
        self._asignar_posiciones(nodo.izquierdo, profundidad + 1, posiciones)
        self._contador_x += 1
        posiciones[id(nodo)] = (self._contador_x, profundidad)
        self._asignar_posiciones(nodo.derecho, profundidad + 1, posiciones)

    def _dibujar_lineas(self, nodo, posiciones, paso_x, paso_y):
        if nodo is None:
            return
        x1, y1 = posiciones[id(nodo)]
        for hijo in (nodo.izquierdo, nodo.derecho):
            if hijo is not None:
                x2, y2 = posiciones[id(hijo)]
                self.canvas.create_line(x1 * paso_x, y1 * paso_y + 30,
                                        x2 * paso_x, y2 * paso_y + 30,
                                        fill="#90a4ae", width=2)
                self._dibujar_lineas(hijo, posiciones, paso_x, paso_y)

    def _dibujar_nodos(self, nodo, posiciones, paso_x, paso_y, resaltar):
        if nodo is None:
            return
        x, y = posiciones[id(nodo)]
        cx, cy = x * paso_x, y * paso_y + 30
        color = "#ffca28" if nodo.nombre in resaltar else "#1565c0"
        self.canvas.create_oval(cx - 28, cy - 18, cx + 28, cy + 18,
                                fill=color, outline="#123c69", width=2)
        self.canvas.create_text(cx, cy, text=nodo.nombre,
                                fill="white", font=("Segoe UI", 9, "bold"))
        self._dibujar_nodos(nodo.izquierdo, posiciones,
                            paso_x, paso_y, resaltar)
        self._dibujar_nodos(nodo.derecho, posiciones, paso_x, paso_y, resaltar)

    # ------------------------------------------------------------
    # PERSISTENCIA (guardar / cargar en JSON via recorrido preorden)
    # ------------------------------------------------------------
    def guardar_datos(self):
        nodos = self.arbol.recorrido_preorden()
        datos = [{"nombre": n.nombre, "mejor_marca": n.mejor_marca}
                 for n in nodos]
        with open(ARCHIVO_DATOS_ARBOL, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        self.status.config(text=f"Datos guardados en '{ARCHIVO_DATOS_ARBOL}'.")
        messagebox.showinfo(
            "Guardado", "La informacion se guardo correctamente.")

    def cargar_datos(self):
        if not os.path.exists(ARCHIVO_DATOS_ARBOL):
            messagebox.showwarning(
                "Atencion", "No existe un archivo de datos guardado.")
            return
        with open(ARCHIVO_DATOS_ARBOL, "r", encoding="utf-8") as f:
            datos = json.load(f)

        self.arbol.vaciar()
        for item in datos:
            self.arbol.insertar(item["nombre"], item["mejor_marca"])

        self._refrescar_todo()
        self.status.config(text="Datos cargados correctamente.")


# ======================================================================
#   VENTANA PRINCIPAL: NOTEBOOK CON LAS DOS PESTANAS
# ======================================================================
class SaltControlProApp:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "SaltControl Pro - Sistema de Registro y Gestion de Saltos con Garrocha")
        self.root.geometry("1180x760")
        self.root.configure(bg="#eef2f7")

        titulo = tk.Label(self.root, text="SaltControl Pro",
                          font=("Segoe UI", 22, "bold"), bg="#eef2f7", fg="#123c69")
        titulo.pack(pady=(12, 0))
        subtitulo = tk.Label(
            self.root,
            text="Sistema de registro y gestion de saltos con garrocha - Alto Rendimiento",
            font=("Segoe UI", 10), bg="#eef2f7", fg="#446")
        subtitulo.pack(pady=(0, 8))

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TNotebook.Tab", font=(
            "Segoe UI", 10, "bold"), padding=(14, 8))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.tab_arreglos = PestanaArreglos(self.notebook)
        self.tab_arbol = PestanaArbol(self.notebook)

        self.notebook.add(self.tab_arreglos,
                          text="  Registro por Arreglos (Matriz)  ")
        self.notebook.add(
            self.tab_arbol, text="  Gestion por Arbol Binario (BST)  ")

        frame_salir = tk.Frame(self.root, bg="#eef2f7")
        frame_salir.pack(fill="x", padx=15, pady=(0, 10))
        tk.Button(frame_salir, text="Salir", command=self.root.destroy,
                  bg="#b71c1c", fg="white", width=12).pack(side="right")


if __name__ == "__main__":
    root = tk.Tk()
    app = SaltControlProApp(root)
    root.mainloop()
