# SaltControl Pro

Aplicación de escritorio en **Python (Tkinter)** para registrar y gestionar saltos con garrocha. Combina estructuras secuenciales (arreglos y matriz) con una estructura dinámica (árbol binario de búsqueda) en dos pestañas.

<img width="1175" height="789" alt="captura_arreglos" src="https://github.com/user-attachments/assets/9b309202-62a1-4a95-a969-3f046e200379" />
<img width="1175" height="785" alt="captura_arbol" src="https://github.com/user-attachments/assets/05703b8b-ea2b-4429-bc7a-fbde361210c1" />

## Qué muestra este proyecto
- Arreglos unidimensionales y una **matriz** (atletas × alturas) para registrar saltos válidos (`X`) y nulos (`O`).
- **Ordenamiento de burbuja** por mejor marca, con conteo de intercambios.
- **Búsqueda lineal** con conteo de comparaciones.
- **Árbol binario de búsqueda (BST)** ordenado por nombre: inserción, búsqueda, eliminación (los 3 casos clásicos) y recorridos inorden, preorden y postorden.
- Dibujo del árbol en un `Canvas`, con el camino de búsqueda resaltado.
- Persistencia en archivos **JSON**.
- Interfaz gráfica con `tkinter` y `ttk`.

## Pestañas

| Pestaña | Estructura | Funciones |
|---|---|---|
| Registro por Arreglos (Matriz) | Arreglos y matriz | Agregar atletas (máx. 15) y alturas, registrar saltos, ver mejor marca, ordenar, buscar |
| Gestión por Árbol Binario (BST) | Árbol binario de búsqueda | Insertar, buscar, eliminar, recorridos, altura y cantidad de nodos |

## Cómo ejecutarlo

**Requisito:** Python 3 con Tkinter. No hay que instalar librerías externas.

```
python saltcontrol_pro.py
```

En Windows y macOS Tkinter ya viene incluido. En Linux, si falta:

```
sudo apt install python3-tk
```

## Datos
La aplicación arranca con datos de ejemplo inventados. Los botones **Guardar datos** y **Cargar datos** crean y leen `registro_saltos.json` (pestaña de arreglos) y `registro_arbol.json` (pestaña del árbol) en la carpeta donde se ejecuta el programa.
