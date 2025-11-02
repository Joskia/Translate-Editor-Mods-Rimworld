import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import xml.etree.ElementTree as ET
import threading
from deep_translator import GoogleTranslator
import re
import json
import time
import requests
import shutil
import webbrowser
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class EditorTematico:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Editor Temático Profesional")
        self.ventana.state('zoomed')
        
        # Variables de tema
        self.tema_oscuro = True
        self.colores = self.obtener_tema_oscuro()
        
        self.carpeta_mod = ""
        self.idioma_cargado = ""
        self.archivos_xml = []
        self.archivo_actual = ""
        self.textos_actuales = []
        self.traducciones = {}
        
        # Variables para edición
        self.celda_editando = None
        self.entry_edicion = None
        
        # Variables para deshacer/rehacer
        self.historial_about = []
        self.indice_historial_about = -1
        self.max_historial = 50
        
        self.configurar_ventana()
        self.crear_interfaz_mejorada()
        self.configurar_bindings()
    
    def obtener_tema_oscuro(self):
        return {
            'fondo_principal': '#1e1e1e',
            'fondo_secundario': '#2d2d2d',
            'fondo_terciario': '#3c3c3c',
            'texto_principal': '#e0e0e0',
            'texto_secundario': '#b0b0b0',
            'acento': '#007acc',
            'verde': '#4ec9b0',
            'naranja': '#ce9178',
            'morado': '#c586c0',
            'gris_boton': '#5a5a5a',
            'borde': '#404040',
            'exito': '#4caf50',
            'advertencia': '#ff9800',
            'error': '#f44336'
        }
    
    def obtener_tema_claro(self):
        return {
            'fondo_principal': '#ffffff',
            'fondo_secundario': '#f5f5f5',
            'fondo_terciario': '#e8e8e8',
            'texto_principal': '#333333',
            'texto_secundario': '#666666',
            'acento': '#007acc',
            'verde': '#28a745',
            'naranja': '#fd7e14',
            'morado': '#6f42c1',
            'gris_boton': '#6c757d',
            'borde': '#cccccc',
            'exito': '#28a745',
            'advertencia': '#ffc107',
            'error': '#dc3545'
        }
    
    def configurar_ventana(self):
        self.ventana.configure(bg=self.colores['fondo_principal'])
        self.ventana.grid_rowconfigure(1, weight=1)
        self.ventana.grid_columnconfigure(0, weight=1)
    
    def cambiar_tema(self):
        self.tema_oscuro = not self.tema_oscuro
        self.colores = self.obtener_tema_oscuro() if self.tema_oscuro else self.obtener_tema_claro()
        self.actualizar_tema()
    
    def actualizar_tema(self):
        self.ventana.configure(bg=self.colores['fondo_principal'])
        self.frame_superior.configure(bg=self.colores['fondo_secundario'])
        
        for widget in self.frame_superior.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=self.colores['fondo_secundario'], fg=self.colores['texto_principal'])
        
        self.entry_ruta.configure(
            bg=self.colores['fondo_terciario'], 
            fg=self.colores['texto_principal'],
            insertbackground=self.colores['texto_principal']
        )
        self.entry_buscar.configure(
            bg=self.colores['fondo_terciario'], 
            fg=self.colores['texto_principal'],
            insertbackground=self.colores['texto_principal']
        )
        
        self.btn_tema.configure(
            text="🌙" if self.tema_oscuro else "☀️",
            bg=self.colores['gris_boton'], 
            fg='white'
        )
        
        self.status_bar.configure(bg=self.colores['acento'], fg='white')
        self.label_estadisticas.configure(
            bg=self.colores['fondo_secundario'], 
            fg=self.colores['texto_secundario']
        )
        
        # Actualizar botones
        botones = ['btn_cargar', 'btn_traducir', 'btn_corregir', 'btn_guardar', 'btn_crear_idioma', 'btn_recargar_idiomas', 'btn_editar_about']
        for btn_name in botones:
            if hasattr(self, btn_name):
                btn = getattr(self, btn_name)
                btn.configure(fg='white')
        
        self.actualizar_estilo_tabla()
    
    def actualizar_estilo_tabla(self):
        style = ttk.Style()
        
        style.configure("Tema.Vertical.TScrollbar",
                       background=self.colores['fondo_principal'],
                       troughcolor=self.colores['fondo_principal'],
                       borderwidth=0,
                       relief='flat')
        
        style.configure("Tema.Horizontal.TScrollbar",
                       background=self.colores['fondo_principal'],
                       troughcolor=self.colores['fondo_principal'],
                       borderwidth=0,
                       relief='flat')
        
        if self.tema_oscuro:
            style.configure("Tema.Treeview", 
                           background=self.colores['fondo_terciario'],
                           foreground=self.colores['texto_principal'],
                           fieldbackground=self.colores['fondo_terciario'],
                           borderwidth=0,
                           font=('Segoe UI', 10))
            
            style.configure("Tema.Treeview.Heading", 
                           background=self.colores['fondo_secundario'],
                           foreground=self.colores['texto_principal'],
                           relief="flat",
                           borderwidth=0,
                           font=('Segoe UI', 10, 'bold'))
        else:
            style.configure("Tema.Treeview", 
                           background="white",
                           foreground=self.colores['texto_principal'],
                           fieldbackground="white",
                           borderwidth=0,
                           font=('Segoe UI', 10))
            
            style.configure("Tema.Treeview.Heading", 
                           background=self.colores['fondo_terciario'],
                           foreground=self.colores['texto_principal'],
                           relief="flat",
                           borderwidth=0,
                           font=('Segoe UI', 10, 'bold'))
        
        style.map("Tema.Treeview", 
                 background=[('selected', self.colores['acento'])],
                 foreground=[('selected', 'white')])
    
    def crear_interfaz_mejorada(self):
        # Barra superior mejorada con más espacio
        self.frame_superior = tk.Frame(self.ventana, bg=self.colores['fondo_secundario'], height=70)
        self.frame_superior.grid(row=0, column=0, sticky='ew', padx=15, pady=10)
        self.frame_superior.grid_propagate(False)
        self.frame_superior.grid_columnconfigure(9, weight=1)
        
        # Fila 1: Proyecto e Idioma
        tk.Label(self.frame_superior, text="📦 PROYECTO:", bg=self.colores['fondo_secundario'], 
                fg=self.colores['texto_principal'], font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, padx=(0, 5), pady=3)
        
        self.entry_ruta = tk.Entry(self.frame_superior, bg=self.colores['fondo_terciario'], 
                                 fg=self.colores['texto_principal'], font=('Segoe UI', 9), 
                                 width=35, relief='flat', highlightthickness=1,
                                 highlightcolor=self.colores['acento'],
                                 highlightbackground=self.colores['borde'])
        self.entry_ruta.grid(row=0, column=1, padx=(0, 5), pady=3)
        
        btn_buscar = tk.Button(self.frame_superior, text="🔍", bg=self.colores['acento'], 
                              fg='white', font=('Segoe UI', 10), relief='flat', width=3,
                              command=self.buscar_carpeta_mod)
        btn_buscar.grid(row=0, column=2, padx=(0, 15), pady=3)
        
        tk.Label(self.frame_superior, text="🌍 IDIOMA:", bg=self.colores['fondo_secundario'], 
                fg=self.colores['texto_principal'], font=('Segoe UI', 9, 'bold')).grid(row=0, column=3, padx=(0, 5), pady=3)
        
        self.combo_idiomas = ttk.Combobox(self.frame_superior, state="readonly", 
                                         width=18, font=('Segoe UI', 9))
        self.combo_idiomas.grid(row=0, column=4, padx=(0, 5), pady=3)
        self.combo_idiomas.bind('<<ComboboxSelected>>', self.al_seleccionar_idioma)
        
        # Botón de recargar idiomas
        self.btn_recargar_idiomas = tk.Button(self.frame_superior, text="🔄", bg=self.colores['verde'], 
                                        fg='white', font=('Segoe UI', 10), relief='flat', width=3,
                                        command=self.recargar_idiomas)
        self.btn_recargar_idiomas.grid(row=0, column=5, padx=(0, 15), pady=3)
        
        # Fila 2: Archivo con botón Cargar al lado
        tk.Label(self.frame_superior, text="📄 ARCHIVO:", bg=self.colores['fondo_secundario'], 
                fg=self.colores['texto_principal'], font=('Segoe UI', 9, 'bold')).grid(row=1, column=0, padx=(0, 5), pady=3)
        
        self.combo_archivos = ttk.Combobox(self.frame_superior, state="readonly", 
                                          width=25, font=('Segoe UI', 9))
        self.combo_archivos.grid(row=1, column=1, padx=(0, 5), pady=3)
        
        # Botón Cargar al lado del combo de archivos
        self.btn_cargar = tk.Button(self.frame_superior, text="📥 CARGAR", bg=self.colores['acento'], 
                              fg='white', font=('Segoe UI', 9, 'bold'), relief='flat', width=8,
                              command=self.cargar_archivo_seleccionado)
        self.btn_cargar.grid(row=1, column=2, padx=(0, 15), pady=3)
        
        # Búsqueda
        tk.Label(self.frame_superior, text="🔍 BUSCAR:", bg=self.colores['fondo_secundario'], 
                fg=self.colores['texto_principal'], font=('Segoe UI', 9, 'bold')).grid(row=1, column=3, padx=(0, 5), pady=3)
        
        self.entry_buscar = tk.Entry(self.frame_superior, bg=self.colores['fondo_terciario'], 
                                    fg=self.colores['texto_principal'], font=('Segoe UI', 9), 
                                    width=20, relief='flat', highlightthickness=1,
                                    highlightcolor=self.colores['acento'],
                                    highlightbackground=self.colores['borde'])
        self.entry_buscar.grid(row=1, column=4, padx=(0, 15), pady=3)
        self.entry_buscar.bind('<KeyRelease>', self.filtrar_textos)
        
        # Botones de acción principales
        self.btn_traducir = tk.Button(self.frame_superior, text="🤖 TRADUCIR", bg='#9b59b6', 
                                fg='white', font=('Segoe UI', 9, 'bold'), relief='flat', width=10,
                                command=self.traducir_seleccion)
        self.btn_traducir.grid(row=1, column=5, padx=(0, 5), pady=3)
        
        self.btn_corregir = tk.Button(self.frame_superior, text="✏️ CORREGIR", bg='#e74c3c', 
                                fg='white', font=('Segoe UI', 9, 'bold'), relief='flat', width=10,
                                command=self.corregir_ortografia)
        self.btn_corregir.grid(row=1, column=6, padx=(0, 5), pady=3)
        
        self.btn_guardar = tk.Button(self.frame_superior, text="💾 GUARDAR", bg='#27ae60', 
                               fg='white', font=('Segoe UI', 9, 'bold'), relief='flat', width=10,
                               command=self.guardar_xml)
        self.btn_guardar.grid(row=1, column=7, padx=(0, 5), pady=3)
        
        # Nuevo botón para crear idiomas
        self.btn_crear_idioma = tk.Button(self.frame_superior, text="🌐 CREAR IDIOMA", bg='#8e44ad', 
                                fg='white', font=('Segoe UI', 9, 'bold'), relief='flat', width=12,
                                command=self.crear_nuevo_idioma)
        self.btn_crear_idioma.grid(row=1, column=8, padx=(0, 15), pady=3)
        
        # NUEVO: Botón para editar About.xml
        self.btn_editar_about = tk.Button(self.frame_superior, text="📝 EDITAR ABOUT", bg='#f39c12', 
                                fg='white', font=('Segoe UI', 9, 'bold'), relief='flat', width=12,
                                command=self.editar_about)
        self.btn_editar_about.grid(row=1, column=9, padx=(0, 15), pady=3)
        
        # Tema y estadísticas
        self.btn_tema = tk.Button(self.frame_superior, text="🌙" if self.tema_oscuro else "☀️", 
                                 bg=self.colores['gris_boton'], fg='white', font=('Segoe UI', 12),
                                 relief='flat', width=3, command=self.cambiar_tema)
        self.btn_tema.grid(row=1, column=10, padx=(0, 15), pady=3)
        
        self.label_estadisticas = tk.Label(self.frame_superior, text="📊 Total: 0 | Traducidos: 0 | Corregidos: 0", 
                                         bg=self.colores['fondo_secundario'], 
                                         fg=self.colores['texto_secundario'], 
                                         font=('Segoe UI', 9, 'bold'))
        self.label_estadisticas.grid(row=1, column=11, padx=(0, 15), pady=3)
        
        # Área de la tabla con más espacio superior
        frame_tabla = tk.Frame(self.ventana, bg=self.colores['fondo_principal'])
        frame_tabla.grid(row=1, column=0, sticky='nsew', padx=15, pady=(5, 8))
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)
        
        self.actualizar_estilo_tabla()
        
        # Crear Treeview mejorado
        self.tree_textos = ttk.Treeview(frame_tabla, 
                                      columns=('id', 'original', 'traducido', 'estado'), 
                                      show='headings',
                                      style="Tema.Treeview",
                                      selectmode='extended')
        
        # Configurar columnas
        self.tree_textos.heading('id', text='🔑 ID', anchor='w')
        self.tree_textos.heading('original', text='🌍 ORIGINAL', anchor='w')
        self.tree_textos.heading('traducido', text='✏️ TRADUCIDO', anchor='w')
        self.tree_textos.heading('estado', text='📊 ESTADO', anchor='w')
        
        ancho_pantalla = self.ventana.winfo_screenwidth()
        self.tree_textos.column('id', width=int(ancho_pantalla * 0.15), anchor='w', minwidth=100)
        self.tree_textos.column('original', width=int(ancho_pantalla * 0.30), anchor='w', minwidth=150, stretch=True)
        self.tree_textos.column('traducido', width=int(ancho_pantalla * 0.30), anchor='w', minwidth=150, stretch=True)
        self.tree_textos.column('estado', width=int(ancho_pantalla * 0.10), anchor='w', minwidth=80)
        
        # Scrollbars
        scroll_vertical = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree_textos.yview,
                                       style="Tema.Vertical.TScrollbar")
        scroll_horizontal = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.tree_textos.xview,
                                         style="Tema.Horizontal.TScrollbar")
        self.tree_textos.configure(yscrollcommand=scroll_vertical.set, xscrollcommand=scroll_horizontal.set)
        
        self.tree_textos.grid(row=0, column=0, sticky='nsew')
        scroll_vertical.grid(row=0, column=1, sticky='ns')
        scroll_horizontal.grid(row=1, column=0, sticky='ew')
        
        # Barra de estado mejorada
        self.status_bar = tk.Label(self.ventana, 
                                  text="🖱️ Selecciona una carpeta de mod | Ctrl+C: Copiar | Ctrl+V: Pegar | Doble clic: Editar | Ctrl+A: Seleccionar todo | Ctrl+Z: Deshacer | Ctrl+Y: Rehacer", 
                                  bg=self.colores['acento'], fg='white', 
                                  font=('Segoe UI', 9, 'bold'), anchor='w')
        self.status_bar.grid(row=2, column=0, sticky='ew', padx=15, pady=(0, 8))

    # ========== FUNCIONES DE INTERFAZ ORIGINALES ==========

    def configurar_bindings(self):
        """Configura los atajos de teclado y bindings para la tabla"""
        self.tree_textos.bind('<Double-1>', self.al_doble_click_celda)
        self.ventana.bind('<Control-c>', self.copiar_seleccion)
        self.ventana.bind('<Control-v>', self.pegar_seleccion)
        self.ventana.bind('<Control-a>', self.seleccionar_todo)
        self.ventana.bind('<Control-z>', self.deshacer_accion)
        self.ventana.bind('<Control-y>', self.rehacer_accion)
        self.tree_textos.bind('<Return>', self.terminar_edicion)
        self.tree_textos.bind('<Escape>', self.cancelar_edicion)
        self.tree_textos.bind('<<TreeviewSelect>>', self.actualizar_estadisticas)

    def al_doble_click_celda(self, event):
        """Inicia la edición directa en la celda con doble clic"""
        region = self.tree_textos.identify_region(event.x, event.y)
        if region == "cell":
            item = self.tree_textos.identify_row(event.y)
            columna = self.tree_textos.identify_column(event.x)
            
            if item and columna in ('#2', '#3'):
                self.iniciar_edicion(item, columna)

    def iniciar_edicion(self, item, columna):
        """Inicia la edición directa en una celda"""
        valores = self.tree_textos.item(item, 'values')
        indice_columna = int(columna[1]) - 1
        valor_actual = valores[indice_columna] if indice_columna < len(valores) else ""
        
        bbox = self.tree_textos.bbox(item, columna)
        if not bbox:
            return
        
        self.celda_editando = (item, columna)
        self.entry_edicion = tk.Entry(self.tree_textos, 
                                    font=('Segoe UI', 10),
                                    bg='#ffff99' if self.tema_oscuro else '#ffffcc',
                                    fg='black',
                                    relief='solid',
                                    borderwidth=1,
                                    selectbackground='#007acc',
                                    selectforeground='white')
        
        self.entry_edicion.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        self.entry_edicion.insert(0, valor_actual)
        self.entry_edicion.select_range(0, tk.END)
        self.entry_edicion.focus_set()
        
        self.entry_edicion.bind('<Return>', self.guardar_edicion)
        self.entry_edicion.bind('<Escape>', self.cancelar_edicion)
        self.entry_edicion.bind('<FocusOut>', self.guardar_edicion)

    def guardar_edicion(self, event=None):
        """Guarda la edición actual"""
        if not self.celda_editando or not self.entry_edicion:
            return
        
        item, columna = self.celda_editando
        nuevo_valor = self.entry_edicion.get()
        indice_columna = int(columna[1]) - 1
        
        valores = list(self.tree_textos.item(item, 'values'))
        
        if indice_columna < len(valores):
            valores[indice_columna] = nuevo_valor
            if columna == '#3' and nuevo_valor:
                valores[3] = "✏️ Editado"
            self.tree_textos.item(item, values=valores)
            
            if columna == '#3':
                id_texto = valores[0]
                self.traducciones[id_texto] = nuevo_valor
        
        self.terminar_edicion()

    def cancelar_edicion(self, event=None):
        """Cancela la edición actual"""
        self.terminar_edicion()

    def terminar_edicion(self, event=None):
        """Termina la edición y limpia los recursos"""
        if self.entry_edicion:
            self.entry_edicion.destroy()
            self.entry_edicion = None
        self.celda_editando = None
        self.tree_textos.focus_set()

    def copiar_seleccion(self, event=None):
        """Copia el texto seleccionado al portapapeles"""
        seleccionados = self.tree_textos.selection()
        if seleccionados:
            item = seleccionados[0]
            valores = self.tree_textos.item(item, 'values')
            
            columna_focus = self.tree_textos.focus_column()
            if columna_focus:
                indice = int(columna_focus[1]) - 1
                if indice < len(valores):
                    texto = valores[indice]
                    self.ventana.clipboard_clear()
                    self.ventana.clipboard_append(texto)
                    self.actualizar_status("✅ Texto copiado al portapapeles")
            else:
                texto = " | ".join(str(v) for v in valores if v)
                self.ventana.clipboard_clear()
                self.ventana.clipboard_append(texto)
                self.actualizar_status("✅ Fila copiada al portapapeles")

    def pegar_seleccion(self, event=None):
        """Pega texto del portapapeles en la celda seleccionada"""
        try:
            texto = self.ventana.clipboard_get()
            seleccionados = self.tree_textos.selection()
            if seleccionados and texto.strip():
                item = seleccionados[0]
                columna_focus = self.tree_textos.focus_column()
                
                if columna_focus and columna_focus in ('#2', '#3'):
                    self.iniciar_edicion_rapida(item, columna_focus, texto)
        except:
            pass

    def iniciar_edicion_rapida(self, item, columna, texto):
        """Edición rápida con pegado"""
        valores = list(self.tree_textos.item(item, 'values'))
        indice_columna = int(columna[1]) - 1
        
        if indice_columna < len(valores):
            valores[indice_columna] = texto
            if columna == '#3' and texto:
                valores[3] = "📥 Pegado"
            self.tree_textos.item(item, values=valores)
            
            if columna == '#3':
                id_texto = valores[0]
                self.traducciones[id_texto] = texto
            
            self.actualizar_status("✅ Texto pegado")
            self.actualizar_estadisticas()

    def seleccionar_todo(self, event=None):
        """Selecciona todas las filas"""
        items = self.tree_textos.get_children()
        self.tree_textos.selection_set(items)
        return "break"

    def deshacer_accion(self, event=None):
        """Deshace la última acción (para About.xml)"""
        if hasattr(self, 'about_dialogo') and self.about_dialogo.winfo_exists():
            if self.indice_historial_about > 0:
                self.indice_historial_about -= 1
                self._aplicar_estado_about()
                self.actualizar_status("↶ Acción deshecha")
        return "break"

    def rehacer_accion(self, event=None):
        """Rehace la acción deshecha (para About.xml)"""
        if hasattr(self, 'about_dialogo') and self.about_dialogo.winfo_exists():
            if self.indice_historial_about < len(self.historial_about) - 1:
                self.indice_historial_about += 1
                self._aplicar_estado_about()
                self.actualizar_status("↷ Acción rehecha")
        return "break"

    def buscar_carpeta_mod(self):
        """Busca la carpeta del mod y carga automáticamente los idiomas"""
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta del mod")
        if carpeta:
            self.carpeta_mod = carpeta
            self.entry_ruta.delete(0, tk.END)
            self.entry_ruta.insert(0, carpeta)
            self.actualizar_status("🔄 Cargando idiomas...")
            
            threading.Thread(target=self._cargar_idiomas, daemon=True).start()

    def actualizar_status(self, mensaje):
        self.status_bar.config(text=mensaje)

    def recargar_idiomas(self):
        """Recarga la lista de idiomas manualmente"""
        if not self.carpeta_mod:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta de mod")
            return
        
        self.actualizar_status("🔄 Recargando idiomas...")
        threading.Thread(target=self._cargar_idiomas, daemon=True).start()

    def _cargar_idiomas(self):
        """Carga automáticamente los idiomas cuando se selecciona una carpeta"""
        try:
            carpeta_languages = os.path.join(self.carpeta_mod, "Languages")
            if not os.path.exists(carpeta_languages):
                self.actualizar_status("❌ No se encontró la carpeta 'Languages'")
                return
            
            idiomas_encontrados = []
            try:
                for item in os.listdir(carpeta_languages):
                    ruta_completa = os.path.join(carpeta_languages, item)
                    if os.path.isdir(ruta_completa):
                        if self._tiene_archivos_xml(ruta_completa):
                            idiomas_encontrados.append(item)
            except Exception as e:
                self.actualizar_status(f"❌ Error leyendo carpeta: {str(e)}")
                return
            
            self.ventana.after(0, self._actualizar_combobox_idiomas, idiomas_encontrados)
            
        except Exception as e:
            self.actualizar_status(f"❌ Error: {str(e)}")

    def _tiene_archivos_xml(self, carpeta):
        """Verifica si una carpeta tiene archivos XML (incluyendo subcarpetas)"""
        try:
            for root, dirs, files in os.walk(carpeta):
                for file in files:
                    if file.lower().endswith('.xml'):
                        return True
            return False
        except:
            return False

    def _actualizar_combobox_idiomas(self, idiomas_encontrados):
        """Actualiza el combobox de idiomas manteniendo la selección actual si existe"""
        idioma_actual = self.combo_idiomas.get()
        
        if idiomas_encontrados:
            self.combo_idiomas['values'] = idiomas_encontrados
            
            # Mantener la selección actual si todavía existe
            if idioma_actual in idiomas_encontrados:
                self.combo_idiomas.set(idioma_actual)
                self.idioma_cargado = idioma_actual
                self.actualizar_status(f"✅ {len(idiomas_encontrados)} idiomas cargados (se mantuvo {idioma_actual})")
            else:
                # Seleccionar el primero si la selección actual ya no existe
                self.combo_idiomas.set(idiomas_encontrados[0])
                self.idioma_cargado = idiomas_encontrados[0]
                self.actualizar_status(f"✅ {len(idiomas_encontrados)} idiomas cargados")
                
                # Cargar archivos del nuevo idioma seleccionado
                threading.Thread(target=self._cargar_archivos_idioma, daemon=True).start()
        else:
            self.combo_idiomas['values'] = []
            self.combo_idiomas.set('')
            self.actualizar_status("❌ No se encontraron idiomas con archivos XML")

    def al_seleccionar_idioma(self, event):
        """Cuando se selecciona un idioma, carga automáticamente sus archivos"""
        self.idioma_cargado = self.combo_idiomas.get()
        if self.idioma_cargado:
            self.actualizar_status(f"📁 Cargando archivos de {self.idioma_cargado}...")
            threading.Thread(target=self._cargar_archivos_idioma, daemon=True).start()

    def _cargar_archivos_idioma(self):
        """Carga todos los archivos XML del idioma seleccionado (incluyendo subcarpetas)"""
        try:
            if not self.idioma_cargado:
                return
                
            carpeta_idioma = os.path.join(self.carpeta_mod, "Languages", self.idioma_cargado)
            
            if not os.path.exists(carpeta_idioma):
                self.actualizar_status(f"❌ No existe la carpeta {self.idioma_cargado}")
                return
            
            self.archivos_xml = []
            
            for root, dirs, files in os.walk(carpeta_idioma):
                for file in files:
                    if file.lower().endswith('.xml'):
                        ruta_completa = os.path.join(root, file)
                        ruta_relativa = os.path.relpath(ruta_completa, carpeta_idioma)
                        self.archivos_xml.append({
                            'ruta_completa': ruta_completa,
                            'ruta_relativa': ruta_relativa,
                            'nombre_archivo': file
                        })
            
            self.archivos_xml.sort(key=lambda x: x['ruta_relativa'].lower())
            archivos_display = [archivo['ruta_relativa'] for archivo in self.archivos_xml]
            
            self.ventana.after(0, self._actualizar_combobox_archivos, archivos_display)
            
        except Exception as e:
            self.actualizar_status(f"❌ Error cargando archivos: {str(e)}")

    def _actualizar_combobox_archivos(self, archivos_display):
        if archivos_display:
            self.combo_archivos['values'] = archivos_display
            self.combo_archivos.set(archivos_display[0])
            self.actualizar_status(f"📄 {len(archivos_display)} archivos XML encontrados")
        else:
            self.combo_archivos['values'] = []
            self.combo_archivos.set('')
            self.actualizar_status("❌ No se encontraron archivos XML")

    def cargar_archivo_seleccionado(self):
        """Carga el archivo XML seleccionado en la tabla"""
        archivo_relativo = self.combo_archivos.get()
        if not archivo_relativo:
            messagebox.showwarning("Advertencia", "Selecciona un archivo XML")
            return
        
        archivo_encontrado = False
        for archivo_info in self.archivos_xml:
            if archivo_info['ruta_relativa'] == archivo_relativo:
                self.archivo_actual = archivo_info['ruta_completa']
                archivo_encontrado = True
                break
        
        if not archivo_encontrado:
            messagebox.showerror("Error", "No se pudo encontrar el archivo seleccionado")
            return
        
        self.actualizar_status(f"📖 Cargando {os.path.basename(self.archivo_actual)}...")
        threading.Thread(target=self._cargar_textos_archivo, daemon=True).start()

    def _cargar_textos_archivo(self):
        try:
            self.ventana.after(0, self._limpiar_tabla)
            self.textos_actuales = self.extraer_textos_xml(self.archivo_actual)
            self.traducciones = {}
            self.ventana.after(0, self._llenar_tabla)
            
        except Exception as e:
            self.actualizar_status(f"❌ Error cargando archivo: {str(e)}")

    def _limpiar_tabla(self):
        for item in self.tree_textos.get_children():
            self.tree_textos.delete(item)

    def _llenar_tabla(self):
        for texto_info in self.textos_actuales:
            self.tree_textos.insert('', 'end', 
                                  values=(texto_info['id'], texto_info['texto'], "", "⏳ Pendiente"))
        
        self.actualizar_estadisticas()
        self.actualizar_status(f"✅ {len(self.textos_actuales)} textos cargados")
        self.auto_ajustar_columnas()

    def auto_ajustar_columnas(self):
        """Auto-ajusta el ancho de las columnas basado en el contenido"""
        for col in self.tree_textos['columns']:
            max_width = 200
            for item in self.tree_textos.get_children():
                valor = self.tree_textos.set(item, col)
                if valor:
                    ancho_texto = len(str(valor)) * 8
                    max_width = max(max_width, min(ancho_texto, 800))
            
            self.tree_textos.column(col, width=max_width)

    def extraer_textos_xml(self, ruta_archivo):
        textos = []
        try:
            tree = ET.parse(ruta_archivo)
            root = tree.getroot()
            
            if root.tag == "LanguageData":
                for elem in root:
                    if elem.text and elem.text.strip():
                        textos.append({
                            'id': elem.tag,
                            'texto': elem.text.strip(),
                            'elemento': elem,
                            'tipo': 'keyed'
                        })
            else:
                def extraer_recursivo(elemento, ruta_padre=""):
                    id_actual = f"{ruta_padre}/{elemento.tag}" if ruta_padre else elemento.tag
                    
                    if elemento.text and elemento.text.strip():
                        textos.append({
                            'id': id_actual,
                            'texto': elemento.text.strip(),
                            'elemento': elemento,
                            'tipo': 'elemento'
                        })
                    
                    for attr, valor in elemento.attrib.items():
                        if valor and valor.strip() and len(valor.strip()) > 1:
                            textos.append({
                                'id': f"{id_actual}@{attr}",
                                'texto': valor.strip(),
                                'elemento': elemento,
                                'atributo': attr,
                                'tipo': 'atributo'
                            })
                    
                    for hijo in elemento:
                        extraer_recursivo(hijo, id_actual)
                
                extraer_recursivo(root)
                
        except Exception as e:
            self.actualizar_status(f"⚠️ Error en XML: {str(e)}")
        
        return textos

    def traducir_seleccion(self):
        seleccionados = self.tree_textos.selection()
        if not seleccionados:
            messagebox.showwarning("Advertencia", "Selecciona textos para traducir")
            return
        
        threading.Thread(target=self._traducir_seleccion, args=(seleccionados,), daemon=True).start()

    def _traducir_seleccion(self, seleccionados):
        """Traduce los textos seleccionados respetando placeholders"""
        try:
            total = len(seleccionados)
            exitosos = 0
            self.actualizar_status(f"🤖 Traduciendo {total} textos...")
            
            for i, item in enumerate(seleccionados):
                valores = self.tree_textos.item(item, 'values')
                id_texto = valores[0]
                texto_original = valores[1]
                
                if texto_original and len(texto_original.strip()) > 1:
                    try:
                        # Extraer placeholders antes de traducir
                        placeholders = self._extraer_placeholders(texto_original)
                        
                        # Crear texto temporal para traducción (sin placeholders)
                        texto_para_traducir = self._reemplazar_placeholders_para_traduccion(texto_original)
                        
                        if len(texto_para_traducir) > 4900:
                            texto_para_traducir = texto_para_traducir[:4900]
                        
                        texto_traducido_temp = GoogleTranslator(source='auto', target='es').translate(texto_para_traducir)
                        
                        if texto_traducido_temp:
                            # Restaurar placeholders en la traducción
                            texto_traducido = self._restaurar_placeholders(texto_traducido_temp, placeholders)
                            
                            # Mostrar ventana de alternativas si hay múltiples opciones
                            alternativas = [texto_traducido]
                            
                            # Solo generar alternativas si no es un texto con placeholders complejos
                            if len(placeholders) == 0:
                                patron_original = self._analizar_patron_texto(texto_original)
                                alternativas_extra = self._generar_alternativas_respetuosas(texto_original, texto_traducido, patron_original, placeholders)
                                alternativas.extend(alternativas_extra)
                            
                            # Eliminar duplicados
                            alternativas = list(dict.fromkeys(alternativas))
                            
                            # Mostrar ventana de alternativas si hay más de una opción
                            if len(alternativas) > 1:
                                texto_final = self._mostrar_ventana_alternativas_mejorada(alternativas, id_texto, texto_original)
                            else:
                                texto_final = alternativas[0] if alternativas else texto_traducido
                            
                            if texto_final:
                                nuevos_valores = (valores[0], valores[1], texto_final, "✅ Traducido")
                                self.tree_textos.item(item, values=nuevos_valores)
                                self.traducciones[id_texto] = texto_final
                                exitosos += 1
                        
                        time.sleep(0.2)
                        
                    except Exception as e:
                        print(f"Error traduciendo {id_texto}: {str(e)}")
                        continue
            
            self.actualizar_estadisticas()
            self.actualizar_status(f"✅ {exitosos}/{total} textos traducidos")
            
        except Exception as e:
            self.actualizar_status(f"❌ Error en traducción: {str(e)}")

    def _extraer_placeholders(self, texto):
        """Extrae placeholders como {0}, {1}, {name}, etc."""
        placeholders = re.findall(r'\{[^}]+\}', texto)
        return list(set(placeholders))  # Eliminar duplicados

    def _reemplazar_placeholders_para_traduccion(self, texto):
        """Reemplaza placeholders con texto descriptivo para mejor traducción"""
        replacements = {
            r'\{0\}': ' PRIMER_ELEMENTO ',
            r'\{1\}': ' SEGUNDO_ELEMENTO ',
            r'\{2\}': ' TERCER_ELEMENTO ',
            r'\{3\}': ' CUARTO_ELEMENTO ',
            r'\{name\}': ' NOMBRE ',
            r'\{pawn\}': ' PERSONAJE ',
            r'\{item\}': ' OBJETO ',
            r'\{number\}': ' NUMERO ',
            r'\{amount\}': ' CANTIDAD ',
            r'\{gender\}': ' GENERO ',
            r'\{faction\}': ' FACCIÓN ',
            r'\{location\}': ' UBICACIÓN ',
            r'\{time\}': ' TIEMPO ',
            r'\{skill\}': ' HABILIDAD ',
            r'\{bodypart\}': ' PARTE_CUERPO ',
            r'\{animal\}': ' ANIMAL ',
            r'\{weapon\}': ' ARMA ',
            r'\{material\}': ' MATERIAL ',
        }
        
        texto_limpio = texto
        for patron, reemplazo in replacements.items():
            texto_limpio = re.sub(patron, reemplazo, texto_limpio)
        
        # Para placeholders genéricos como {xyz}
        texto_limpio = re.sub(r'\{[^}]+\}', ' ELEMENTO ', texto_limpio)
        
        return texto_limpio

    def _restaurar_placeholders(self, texto_traducido, placeholders):
        """Restaura los placeholders originales en el texto traducido"""
        texto_con_placeholders = texto_traducido
        
        # Reemplazar los marcadores temporales con los placeholders originales
        replacements_inversos = {
            'PRIMER_ELEMENTO': '{0}',
            'SEGUNDO_ELEMENTO': '{1}', 
            'TERCER_ELEMENTO': '{2}',
            'CUARTO_ELEMENTO': '{3}',
            'NOMBRE': '{name}',
            'PERSONAJE': '{pawn}',
            'OBJETO': '{item}',
            'NUMERO': '{number}',
            'CANTIDAD': '{amount}',
            'GENERO': '{gender}',
            'FACCIÓN': '{faction}',
            'UBICACIÓN': '{location}',
            'TIEMPO': '{time}',
            'HABILIDAD': '{skill}',
            'PARTE_CUERPO': '{bodypart}',
            'ANIMAL': '{animal}',
            'ARMA': '{weapon}',
            'MATERIAL': '{material}',
            'ELEMENTO': placeholders[0] if placeholders else '{}'
        }
        
        for temporal, original in replacements_inversos.items():
            texto_con_placeholders = texto_con_placeholders.replace(temporal, original)
        
        return texto_con_placeholders

    def _analizar_patron_texto(self, texto):
        """Analiza el patrón del texto original para mantener la estructura"""
        patron = {
            'tiene_guiones_bajos': '_' in texto,
            'tiene_mayusculas': any(c.isupper() for c in texto[1:]),
            'tiene_espacios': ' ' in texto,
            'es_camel_case': self._es_camel_case(texto),
            'partes': []
        }
        
        # Dividir en partes según el patrón
        if patron['tiene_guiones_bajos']:
            patron['partes'] = texto.split('_')
            patron['separador'] = '_'
        elif patron['es_camel_case']:
            patron['partes'] = self._dividir_camel_case(texto)
            patron['separador'] = ''  # Para CamelCase
        elif patron['tiene_espacios']:
            patron['partes'] = texto.split(' ')
            patron['separador'] = ' '
        else:
            patron['partes'] = [texto]
            patron['separador'] = ''
        
        return patron

    def _es_camel_case(self, texto):
        """Determina si el texto está en formato CamelCase"""
        if not texto or len(texto) < 2:
            return False
        # Debe tener al menos una mayúscula interna y no tener espacios
        return any(c.isupper() for c in texto[1:]) and ' ' not in texto

    def _dividir_camel_case(self, texto):
        """Divide texto CamelCase en palabras"""
        palabras = []
        palabra_actual = texto[0]
        
        for i in range(1, len(texto)):
            char = texto[i]
            if char.isupper():
                if palabra_actual:
                    palabras.append(palabra_actual)
                palabra_actual = char
            else:
                palabra_actual += char
        
        if palabra_actual:
            palabras.append(palabra_actual)
        
        return palabras

    def _generar_alternativas_respetuosas(self, original, traducido, patron, placeholders):
        """Genera alternativas que respetan el patrón original y placeholders"""
        alternativas = []
        
        try:
            # Verificar que todos los placeholders estén presentes
            if not self._verificar_placeholders(traducido, placeholders):
                # Si faltan placeholders, intentar corregir
                traducido = self._corregir_placeholders_faltantes(traducido, placeholders)
            
            # Solo generar alternativas de formato si no es un texto con placeholders complejos
            if len(placeholders) == 0 or patron['tiene_guiones_bajos'] or patron['es_camel_case']:
                # Limpiar y preparar palabras traducidas (sin placeholders para formato)
                texto_sin_placeholders = self._remover_placeholders_para_formato(traducido)
                palabras_traducidas = self._limpiar_y_preparar_palabras(texto_sin_placeholders)
                
                if palabras_traducidas:
                    # Alternativa 2: Respetar guiones bajos originales
                    if patron['tiene_guiones_bajos'] and len(palabras_traducidas) >= len(patron['partes']):
                        partes_traducidas = []
                        for i, parte_original in enumerate(patron['partes']):
                            if i < len(palabras_traducidas):
                                palabra_limpia = self._limpiar_palabra(palabras_traducidas[i])
                                if palabra_limpia:
                                    partes_traducidas.append(palabra_limpia)
                        
                        if len(partes_traducidas) == len(patron['partes']):
                            alternativa_guiones = '_'.join(partes_traducidas)
                            alternativa_guiones = self._restaurar_placeholders(alternativa_guiones, placeholders)
                            if alternativa_guiones not in alternativas:
                                alternativas.append(alternativa_guiones)
                    
                    # Alternativa 3: Formato CamelCase
                    if patron['es_camel_case'] and len(palabras_traducidas) > 1:
                        palabras_camel = [self._limpiar_palabra(p) for p in palabras_traducidas if self._limpiar_palabra(p)]
                        if palabras_camel:
                            alternativa_camel = palabras_camel[0].lower()
                            for palabra in palabras_camel[1:]:
                                alternativa_camel += palabra.capitalize()
                            alternativa_camel = self._restaurar_placeholders(alternativa_camel, placeholders)
                            if alternativa_camel not in alternativas:
                                alternativas.append(alternativa_camel)
            
            # Eliminar duplicados y vacíos
            alternativas = [alt for alt in alternativas if alt and alt.strip()]
            
        except Exception as e:
            print(f"Error generando alternativas: {e}")
        
        return alternativas

    def _verificar_placeholders(self, texto, placeholders):
        """Verifica que todos los placeholders estén presentes en el texto"""
        for placeholder in placeholders:
            if placeholder not in texto:
                return False
        return True

    def _corregir_placeholders_faltantes(self, texto, placeholders):
        """Intenta corregir placeholders faltantes en la traducción"""
        texto_corregido = texto
        for placeholder in placeholders:
            if placeholder not in texto_corregido:
                # Buscar el mejor lugar para insertar el placeholder faltante
                texto_corregido = self._insertar_placeholder_inteligente(texto_corregido, placeholder)
        return texto_corregido

    def _insertar_placeholder_inteligente(self, texto, placeholder):
        """Inserta un placeholder de manera inteligente en el texto"""
        # Por ahora, simplemente agregar al final entre paréntesis
        return f"{texto} ({placeholder})"

    def _remover_placeholders_para_formato(self, texto):
        """Remueve placeholders temporalmente para procesamiento de formato"""
        return re.sub(r'\{[^}]+\}', ' ', texto)

    def _limpiar_y_preparar_palabras(self, texto):
        """Limpia y prepara las palabras para generar alternativas"""
        # Remover puntuación excesiva pero mantener acentos
        texto_limpio = re.sub(r'[^\w\sáéíóúÁÉÍÓÚñÑ]', ' ', texto)
        palabras = texto_limpio.split()
        
        # Limpiar cada palabra
        palabras_limpias = []
        for palabra in palabras:
            palabra_limpia = self._limpiar_palabra(palabra)
            if palabra_limpia and len(palabra_limpia) > 1:
                palabras_limpias.append(palabra_limpia)
        
        return palabras_limpias

    def _limpiar_palabra(self, palabra):
        """Limpia una palabra individual manteniendo acentos"""
        # Remover caracteres no alfabéticos al inicio/final, mantener acentos
        palabra_limpia = re.sub(r'^[^a-zA-ZáéíóúÁÉÍÓÚñÑ]+', '', palabra)
        palabra_limpia = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ]+$', '', palabra_limpia)
        return palabra_limpia

    def _mostrar_ventana_alternativas_mejorada(self, alternativas, id_texto, texto_original):
        """Muestra ventana mejorada para seleccionar alternativa de traducción"""
        resultado = [alternativas[0]]  # Por defecto la primera
        
        def aplicar_traduccion():
            seleccion = lista_alternativas.curselection()
            if seleccion:
                resultado[0] = alternativas[seleccion[0]]
                dialogo.destroy()
            else:
                messagebox.showwarning("Advertencia", "Selecciona una alternativa")
        
        def usar_primera():
            resultado[0] = alternativas[0]
            dialogo.destroy()
        
        dialogo = tk.Toplevel(self.ventana)
        dialogo.title(f"Alternativas de Traducción - {id_texto}")
        dialogo.geometry("600x400")
        dialogo.transient(self.ventana)
        dialogo.grab_set()
        dialogo.configure(bg=self.colores['fondo_principal'])
        
        frame_principal = tk.Frame(dialogo, bg=self.colores['fondo_principal'], padx=20, pady=20)
        frame_principal.pack(fill='both', expand=True)
        
        # Mostrar texto original
        tk.Label(frame_principal, text="Texto original:", 
                bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        tk.Label(frame_principal, text=texto_original, 
                bg=self.colores['fondo_principal'], fg=self.colores['texto_secundario'],
                font=('Segoe UI', 9), wraplength=550, justify='left').pack(anchor='w', pady=(0, 15))
        
        tk.Label(frame_principal, text="Selecciona la traducción preferida:", 
                bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(0, 10))
        
        frame_lista = tk.Frame(frame_principal, bg=self.colores['fondo_principal'])
        frame_lista.pack(fill='both', expand=True, pady=10)
        
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')
        
        lista_alternativas = tk.Listbox(frame_lista, 
                                      bg=self.colores['fondo_terciario'],
                                      fg=self.colores['texto_principal'],
                                      selectbackground=self.colores['acento'],
                                      font=('Segoe UI', 10),
                                      yscrollcommand=scrollbar.set,
                                      height=8)
        lista_alternativas.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=lista_alternativas.yview)
        
        for i, alt in enumerate(alternativas):
            # Mostrar descripción del formato
            formato = self._describir_formato(alt)
            lista_alternativas.insert(i, f"Opción {i+1}: {alt} [{formato}]")
        
        lista_alternativas.selection_set(0)
        
        frame_botones = tk.Frame(frame_principal, bg=self.colores['fondo_principal'])
        frame_botones.pack(fill='x', pady=(10, 0))
        
        btn_aplicar = tk.Button(frame_botones, text="✅ APLICAR SELECCIÓN", 
                              bg=self.colores['exito'], fg='white',
                              font=('Segoe UI', 10, 'bold'), relief='flat',
                              command=aplicar_traduccion)
        btn_aplicar.pack(side='left', padx=(0, 10))
        
        btn_primera = tk.Button(frame_botones, text="🔄 USAR PRIMERA OPCIÓN", 
                               bg=self.colores['advertencia'], fg='white',
                               font=('Segoe UI', 10, 'bold'), relief='flat',
                               command=usar_primera)
        btn_primera.pack(side='left', padx=(0, 10))
        
        btn_cancelar = tk.Button(frame_botones, text="❌ CANCELAR", 
                               bg=self.colores['error'], fg='white',
                               font=('Segoe UI', 10, 'bold'), relief='flat',
                               command=dialogo.destroy)
        btn_cancelar.pack(side='left')
        
        self.ventana.wait_window(dialogo)
        
        return resultado[0]

    def _describir_formato(self, texto):
        """Describe el formato del texto para la interfaz"""
        if '_' in texto:
            return "con guiones"
        elif ' ' in texto:
            return "con espacios"
        elif texto and texto[0].isupper() and any(c.isupper() for c in texto[1:]):
            return "PascalCase"
        elif texto and texto[0].islower() and any(c.isupper() for c in texto[1:]):
            return "camelCase"
        else:
            return "simple"

    # ========== BÚSQUEDA INTELIGENTE ==========

    def filtrar_textos(self, event):
        """Búsqueda inteligente que busca en todas las columnas"""
        texto_buscar = self.entry_buscar.get().lower().strip()
        
        # Mostrar todos los items primero
        for item in self.tree_textos.get_children():
            self.tree_textos.detach(item)
        
        if not texto_buscar:
            # Si no hay texto de búsqueda, mostrar todos
            for item in self.tree_textos.get_children(''):
                self.tree_textos.reattach(item, '', 'end')
        else:
            # Búsqueda inteligente
            for item in self.tree_textos.get_children(''):
                valores = self.tree_textos.item(item, 'values')
                encontrado = False
                
                # Buscar en todas las columnas
                for valor in valores:
                    if valor and texto_buscar in str(valor).lower():
                        encontrado = True
                        break
                
                # Búsqueda parcial en palabras
                if not encontrado:
                    for valor in valores:
                        if valor:
                            palabras = str(valor).lower().split()
                            for palabra in palabras:
                                if texto_buscar in palabra:
                                    encontrado = True
                                    break
                        if encontrado:
                            break
                
                if encontrado:
                    self.tree_textos.attach(item, '', 'end')
        
        self.actualizar_estadisticas()

    # ========== CREAR NUEVOS IDIOMAS MEJORADO ==========

    def crear_nuevo_idioma(self):
        """Crea un nuevo idioma copiando la estructura de carpetas y archivos"""
        if not self.carpeta_mod:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta de mod")
            return
        
        carpeta_languages = os.path.join(self.carpeta_mod, "Languages")
        if not os.path.exists(carpeta_languages):
            messagebox.showwarning("Advertencia", "No se encontró la carpeta 'Languages'")
            return
        
        # Obtener lista de idiomas existentes
        idiomas_existentes = []
        try:
            for item in os.listdir(carpeta_languages):
                if os.path.isdir(os.path.join(carpeta_languages, item)):
                    idiomas_existentes.append(item)
        except:
            pass
        
        # Lista predefinida de idiomas
        idiomas_predefinidos = [
            "English",
            "Catalan (Català)",
            "ChineseSimplified (简体中文)",
            "ChineseTraditional (繁體中文)",
            "Czech (Čeština)",
            "Danish (Dansk)",
            "Dutch (Nederlands)",
            "Estonian (Eesti)",
            "Finnish (Suomi)",
            "French (Français)",
            "German (Deutsch)",
            "Greek (Ελληνικά)",
            "Hungarian (Magyar)",
            "Italian (Italiano)",
            "Japanese (日本語)",
            "Korean (한국어)",
            "Norwegian (Norsk Bokmål)",
            "Polish (Polski)",
            "Portuguese (Português)",
            "PortugueseBrazilian (Português Brasileiro)",
            "Romanian (Română)",
            "Russian (Русский)",
            "Slovak (Slovenčina)",
            "Spanish (Español(Castellano))",
            "SpanishLatin (Español(Latinoamérica))",
            "Swedish (Svenska)",
            "Turkish (Türkçe)",
            "Ukrainian (Українська)",
            "Vietnamese (tiếng Việt)"
        ]
        
        if not idiomas_existentes:
            messagebox.showwarning("Advertencia", "No se encontraron idiomas en la carpeta Languages")
            return
        
        # Crear ventana de diálogo para crear nuevo idioma
        dialogo = tk.Toplevel(self.ventana)
        dialogo.title("🌐 Crear Nuevo Idioma")
        dialogo.geometry("550x400")  # Aumentado el tamaño
        dialogo.transient(self.ventana)
        dialogo.grab_set()
        dialogo.configure(bg=self.colores['fondo_principal'])
        
        frame_principal = tk.Frame(dialogo, bg=self.colores['fondo_principal'], padx=20, pady=20)
        frame_principal.pack(fill='both', expand=True)
        
        # Título
        tk.Label(frame_principal, text="Crear Nuevo Idioma", 
                bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Selección de idioma predefinido
        frame_idioma = tk.Frame(frame_principal, bg=self.colores['fondo_principal'])
        frame_idioma.pack(fill='x', pady=(0, 15))
        
        tk.Label(frame_idioma, text="Selecciona el idioma a crear:", 
                bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        # Variable para almacenar la selección
        self.idioma_seleccionado = tk.StringVar()
        
        # Crear combobox con los idiomas predefinidos
        combo_idiomas = ttk.Combobox(frame_idioma, 
                                    textvariable=self.idioma_seleccionado,
                                    values=idiomas_predefinidos, 
                                    state="readonly",
                                    font=('Segoe UI', 10), 
                                    width=40)
        combo_idiomas.pack(fill='x', pady=(5, 0))
        combo_idiomas.set(idiomas_predefinidos[0])  # Establecer English por defecto
        
        # Frame para mostrar información del idioma seleccionado
        frame_info_idioma = tk.Frame(frame_idioma, bg=self.colores['fondo_secundario'], relief='flat', bd=1)
        frame_info_idioma.pack(fill='x', pady=(10, 0))
        
        self.label_info_idioma = tk.Label(frame_info_idioma, 
                                        text="Carpeta: English",
                                        bg=self.colores['fondo_secundario'], 
                                        fg=self.colores['texto_secundario'],
                                        font=('Segoe UI', 9),
                                        justify='left')
        self.label_info_idioma.pack(padx=10, pady=8)
        
        def actualizar_info_idioma(event=None):
            """Actualiza la información cuando se selecciona un idioma"""
            idioma_completo = self.idioma_seleccionado.get()
            # Extraer el nombre de la carpeta (parte antes del paréntesis)
            if " (" in idioma_completo:
                nombre_carpeta = idioma_completo.split(" (")[0].strip()
            else:
                nombre_carpeta = idioma_completo
            
            self.label_info_idioma.config(text=f"Carpeta: {nombre_carpeta}")
        
        combo_idiomas.bind('<<ComboboxSelected>>', actualizar_info_idioma)
        actualizar_info_idioma()  # Llamar inicialmente
        
        # Idioma base para copiar estructura
        frame_base = tk.Frame(frame_principal, bg=self.colores['fondo_principal'])
        frame_base.pack(fill='x', pady=(0, 15))
        
        tk.Label(frame_base, text="Copiar estructura del idioma existente:", 
                bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        combo_base = ttk.Combobox(frame_base, values=idiomas_existentes, state="readonly",
                                 font=('Segoe UI', 10), width=38)
        combo_base.pack(fill='x', pady=(5, 0))
        if idiomas_existentes:
            combo_base.set(idiomas_existentes[0])
        
        # Información
        frame_info = tk.Frame(frame_principal, bg=self.colores['fondo_secundario'], relief='flat', bd=1)
        frame_info.pack(fill='x', pady=(0, 20))
        
        info_text = "Se creará una nueva carpeta copiando toda la estructura de carpetas, subcarpetas y archivos XML del idioma base seleccionado."
        tk.Label(frame_info, text=info_text, 
                bg=self.colores['fondo_secundario'], fg=self.colores['texto_secundario'],
                font=('Segoe UI', 9), justify='left', wraplength=500).pack(padx=10, pady=10)
        
        # Botones - ahora en un frame separado para mejor organización
        frame_botones = tk.Frame(frame_principal, bg=self.colores['fondo_principal'])
        frame_botones.pack(fill='x', pady=(10, 0))
        
        def crear_idioma():
            idioma_completo = self.idioma_seleccionado.get()
            idioma_base = combo_base.get()
            
            if not idioma_completo:
                messagebox.showwarning("Advertencia", "Selecciona un idioma para crear")
                return
            
            if not idioma_base:
                messagebox.showwarning("Advertencia", "Selecciona un idioma base")
                return
            
            # Extraer nombre de carpeta (parte antes del paréntesis)
            if " (" in idioma_completo:
                nombre_carpeta = idioma_completo.split(" (")[0].strip()
            else:
                nombre_carpeta = idioma_completo
            
            # Verificar si el idioma ya existe
            ruta_nuevo_idioma = os.path.join(carpeta_languages, nombre_carpeta)
            if os.path.exists(ruta_nuevo_idioma):
                respuesta = messagebox.askyesno("Confirmar", 
                    f"El idioma '{nombre_carpeta}' ya existe. ¿Deseas sobrescribirlo?")
                if not respuesta:
                    return
            
            # Crear el nuevo idioma en un hilo separado
            threading.Thread(
                target=self._crear_estructura_idioma,
                args=(ruta_nuevo_idioma, idioma_base, nombre_carpeta),
                daemon=True
            ).start()
            
            dialogo.destroy()
        
        def cancelar():
            dialogo.destroy()
        
        # Botones alineados horizontalmente
        btn_crear = tk.Button(frame_botones, text="✅ CREAR IDIOMA", 
                             bg=self.colores['exito'], fg='white',
                             font=('Segoe UI', 10, 'bold'), relief='flat', width=15,
                             command=crear_idioma)
        btn_crear.pack(side='left', padx=(0, 10))
        
        btn_cancelar = tk.Button(frame_botones, text="❌ CANCELAR", 
                               bg=self.colores['error'], fg='white',
                               font=('Segoe UI', 10, 'bold'), relief='flat', width=15,
                               command=cancelar)
        btn_cancelar.pack(side='left')
        
        # Centrar los botones
        frame_botones.pack_configure(anchor='center')
        
        # Bind Enter para crear
        combo_idiomas.bind('<Return>', lambda e: crear_idioma())
        combo_base.bind('<Return>', lambda e: crear_idioma())

    def _crear_estructura_idioma(self, ruta_nuevo, idioma_base, nombre_idioma):
        """Crea la estructura del nuevo idioma copiando del idioma base"""
        try:
            self.actualizar_status(f"🔄 Creando idioma {nombre_idioma} desde {idioma_base}...")
            
            ruta_base = os.path.join(self.carpeta_mod, "Languages", idioma_base)
            
            # Crear directorio principal si no existe
            os.makedirs(ruta_nuevo, exist_ok=True)
            
            archivos_creados = 0
            carpetas_creadas = 0
            
            # Función recursiva para copiar estructura
            def copiar_estructura_recursiva(ruta_origen, ruta_destino):
                nonlocal archivos_creados, carpetas_creadas
                
                try:
                    for item in os.listdir(ruta_origen):
                        ruta_item_origen = os.path.join(ruta_origen, item)
                        ruta_item_destino = os.path.join(ruta_destino, item)
                        
                        if os.path.isdir(ruta_item_origen):
                            # Es una carpeta - crear y copiar recursivamente
                            os.makedirs(ruta_item_destino, exist_ok=True)
                            carpetas_creadas += 1
                            copiar_estructura_recursiva(ruta_item_origen, ruta_item_destino)
                        else:
                            # Es un archivo - copiar manteniendo estructura
                            shutil.copy2(ruta_item_origen, ruta_item_destino)
                            archivos_creados += 1
                                
                except Exception as e:
                    print(f"Error copiando estructura: {e}")
            
            # Iniciar copia recursiva
            copiar_estructura_recursiva(ruta_base, ruta_nuevo)
            
            # Actualizar interfaz
            self.ventana.after(0, self._actualizar_interfaz_despues_crear, 
                             nombre_idioma, archivos_creados, carpetas_creadas)
            
        except Exception as e:
            self.ventana.after(0, messagebox.showerror, "Error", 
                             f"No se pudo crear el idioma: {str(e)}")

    def _actualizar_interfaz_despues_crear(self, nombre_idioma, archivos_creados, carpetas_creadas):
        """Actualiza la interfaz después de crear un nuevo idioma"""
        messagebox.showinfo("Éxito", 
            f"Idioma '{nombre_idioma}' creado exitosamente!\n\n"
            f"• Archivos creados: {archivos_creados}\n"
            f"• Carpetas creadas: {carpetas_creadas}\n\n"
            f"El nuevo idioma ya está disponible en la lista.")
        
        self.actualizar_status(f"✅ Idioma '{nombre_idioma}' creado con {archivos_creados} archivos")
        
        # Recargar la lista de idiomas y seleccionar automáticamente el nuevo idioma
        def seleccionar_nuevo_idioma():
            # Recargar idiomas
            threading.Thread(target=self._cargar_y_seleccionar_idioma, args=(nombre_idioma,), daemon=True).start()
        
        seleccionar_nuevo_idioma()

    def _cargar_y_seleccionar_idioma(self, nombre_idioma):
        """Recarga los idiomas y selecciona el nuevo idioma creado"""
        try:
            carpeta_languages = os.path.join(self.carpeta_mod, "Languages")
            if not os.path.exists(carpeta_languages):
                return
            
            # Cargar lista actualizada de idiomas
            idiomas_encontrados = []
            for item in os.listdir(carpeta_languages):
                ruta_completa = os.path.join(carpeta_languages, item)
                if os.path.isdir(ruta_completa) and self._tiene_archivos_xml(ruta_completa):
                    idiomas_encontrados.append(item)
            
            # Actualizar combobox en el hilo principal
            self.ventana.after(0, self._seleccionar_nuevo_idioma_en_interfaz, idiomas_encontrados, nombre_idioma)
            
        except Exception as e:
            print(f"Error cargando nuevo idioma: {e}")

    def _seleccionar_nuevo_idioma_en_interfaz(self, idiomas_encontrados, nombre_idioma):
        """Selecciona el nuevo idioma en la interfaz y carga sus archivos"""
        if idiomas_encontrados:
            self.combo_idiomas['values'] = idiomas_encontrados
            
            # Buscar y seleccionar el nuevo idioma
            if nombre_idioma in idiomas_encontrados:
                self.combo_idiomas.set(nombre_idioma)
                self.idioma_cargado = nombre_idioma
                self.actualizar_status(f"🔄 Cargando archivos de {nombre_idioma}...")
                
                # Cargar archivos del nuevo idioma
                threading.Thread(target=self._cargar_archivos_idioma, daemon=True).start()
            else:
                # Si no se encuentra, seleccionar el primero
                self.combo_idiomas.set(idiomas_encontrados[0])
                self.actualizar_status(f"✅ {len(idiomas_encontrados)} idiomas cargados")
        else:
            self.combo_idiomas['values'] = []
            self.combo_idiomas.set('')
            self.actualizar_status("❌ No se encontraron idiomas con archivos XML")

    # ========== FUNCIONES DESHACER/REHACER PARA ABOUT.XML ==========

    def _guardar_estado_about(self, tree, root):
        """Guarda el estado actual en el historial"""
        try:
            # Crear una copia del estado actual
            estado = {
                'nombre': root.find('name').text if root.find('name') is not None else "",
                'autor': root.find('author').text if root.find('author') is not None else "",
                'package_id': root.find('packageId').text if root.find('packageId') is not None else "",
                'descripcion': root.find('description').text if root.find('description') is not None else "",
                'icon_path': root.find('modIconPath').text if root.find('modIconPath') is not None else "",
                'versiones': []
            }
            
            # Guardar versiones soportadas
            supported_versions = root.find('supportedVersions')
            if supported_versions is not None:
                for li in supported_versions.findall('li'):
                    estado['versiones'].append(li.text)
            
            # Limitar el tamaño del historial
            if len(self.historial_about) >= self.max_historial:
                self.historial_about.pop(0)
            
            # Agregar al historial y actualizar índice
            self.historial_about = self.historial_about[:self.indice_historial_about + 1]
            self.historial_about.append(estado)
            self.indice_historial_about = len(self.historial_about) - 1
            
        except Exception as e:
            print(f"Error guardando estado: {e}")

    def _aplicar_estado_about(self):
        """Aplica el estado actual del historial a la interfaz"""
        if not self.historial_about or self.indice_historial_about < 0:
            return
        
        estado = self.historial_about[self.indice_historial_about]
        
        try:
            # Aplicar a los campos de la interfaz
            if hasattr(self, 'entry_nombre_about'):
                self.entry_nombre_about.delete(0, tk.END)
                self.entry_nombre_about.insert(0, estado['nombre'])
            
            if hasattr(self, 'entry_autor_about'):
                self.entry_autor_about.delete(0, tk.END)
                self.entry_autor_about.insert(0, estado['autor'])
            
            if hasattr(self, 'entry_package_id_about'):
                self.entry_package_id_about.delete(0, tk.END)
                self.entry_package_id_about.insert(0, estado['package_id'])
            
            if hasattr(self, 'text_descripcion_about'):
                self.text_descripcion_about.delete('1.0', tk.END)
                self.text_descripcion_about.insert('1.0', estado['descripcion'])
            
            if hasattr(self, 'entry_icon_path_about'):
                self.entry_icon_path_about.delete(0, tk.END)
                self.entry_icon_path_about.insert(0, estado['icon_path'])
                if hasattr(self, 'frame_preview_about'):
                    self.actualizar_preview_icono(estado['icon_path'], self.frame_preview_about)
            
            # Aplicar versiones
            if hasattr(self, 'vars_versiones_about'):
                for version, var in self.vars_versiones_about.items():
                    var.set(version in estado['versiones'])
                    
        except Exception as e:
            print(f"Error aplicando estado: {e}")

    # ========== EDITOR DE ABOUT.XML MEJORADO ==========

    def editar_about(self):
        """Abre el editor para modificar About.xml manteniendo la estructura original"""
        if not self.carpeta_mod:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta de mod")
            return
        
        ruta_about = os.path.join(self.carpeta_mod, "About", "About.xml")
        ruta_published_id = os.path.join(self.carpeta_mod, "About", "PublishedFileId.txt")
        
        if not os.path.exists(ruta_about):
            messagebox.showwarning("Advertencia", "No se encontró el archivo About.xml")
            return
        
        try:
            # Cargar el XML
            tree = ET.parse(ruta_about)
            root = tree.getroot()
            
            # Inicializar historial
            self.historial_about = []
            self.indice_historial_about = -1
            
            # Guardar estado inicial
            self._guardar_estado_about(tree, root)
            
            # Crear ventana de edición
            dialogo = tk.Toplevel(self.ventana)
            dialogo.title("📝 Editor de About.xml")
            dialogo.geometry("900x700")
            dialogo.transient(self.ventana)
            dialogo.grab_set()
            dialogo.configure(bg=self.colores['fondo_principal'])
            self.about_dialogo = dialogo
            
            # Variable para controlar si la ventana está cerrada
            dialogo_cerrada = False
            
            def on_closing():
                nonlocal dialogo_cerrada
                dialogo_cerrada = True
                dialogo.destroy()
            
            dialogo.protocol("WM_DELETE_WINDOW", on_closing)
            
            frame_principal = tk.Frame(dialogo, bg=self.colores['fondo_principal'], padx=20, pady=20)
            frame_principal.pack(fill='both', expand=True)
            
            # Título
            tk.Label(frame_principal, text="Editor de About.xml", 
                    bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                    font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))
            
            # Frame de botones de deshacer/rehacer
            frame_deshacer = tk.Frame(frame_principal, bg=self.colores['fondo_principal'])
            frame_deshacer.pack(fill='x', pady=(0, 10))
            
            btn_deshacer = tk.Button(frame_deshacer, text="↶ Deshacer (Ctrl+Z)", 
                                   bg=self.colores['gris_boton'], fg='white',
                                   font=('Segoe UI', 9, 'bold'), relief='flat', width=15,
                                   command=lambda: self.deshacer_accion())
            btn_deshacer.pack(side='left', padx=(0, 5))
            
            btn_rehacer = tk.Button(frame_deshacer, text="↷ Rehacer (Ctrl+Y)", 
                                  bg=self.colores['gris_boton'], fg='white',
                                  font=('Segoe UI', 9, 'bold'), relief='flat', width=15,
                                  command=lambda: self.rehacer_accion())
            btn_rehacer.pack(side='left', padx=(0, 5))
            
            # Frame principal con scroll
            canvas = tk.Canvas(frame_principal, bg=self.colores['fondo_principal'], highlightthickness=0)
            scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.colores['fondo_principal'])
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Obtener datos actuales
            nombre = root.find('name').text if root.find('name') is not None else ""
            autor = root.find('author').text if root.find('author') is not None else ""
            package_id = root.find('packageId').text if root.find('packageId') is not None else ""
            descripcion = root.find('description').text if root.find('description') is not None else ""
            mod_icon_path = root.find('modIconPath').text if root.find('modIconPath') is not None else ""
            
            # Versiones soportadas
            versiones_soportadas = []
            supported_versions = root.find('supportedVersions')
            if supported_versions is not None:
                for li in supported_versions.findall('li'):
                    versiones_soportadas.append(li.text)
            
            # Leer PublishedFileId si existe
            workshop_id = ""
            if os.path.exists(ruta_published_id):
                try:
                    with open(ruta_published_id, 'r', encoding='utf-8') as f:
                        workshop_id = f.read().strip()
                except:
                    workshop_id = ""
            
            # Frame superior con datos básicos
            frame_superior = tk.Frame(scrollable_frame, bg=self.colores['fondo_principal'])
            frame_superior.pack(fill='x', pady=(0, 20))
            
            # Columna izquierda: Datos básicos
            frame_datos = tk.Frame(frame_superior, bg=self.colores['fondo_principal'])
            frame_datos.pack(side='left', fill='both', expand=True)
            
            # Nombre
            tk.Label(frame_datos, text="Nombre del Mod *", 
                    bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                    font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
            self.entry_nombre_about = tk.Entry(frame_datos, bg=self.colores['fondo_terciario'], 
                                  fg=self.colores['texto_principal'], font=('Segoe UI', 10),
                                  width=50, relief='flat', highlightthickness=1,
                                  highlightcolor=self.colores['acento'],
                                  highlightbackground=self.colores['borde'])
            self.entry_nombre_about.insert(0, nombre)
            self.entry_nombre_about.pack(fill='x', pady=(0, 15))
            self.entry_nombre_about.bind('<KeyRelease>', lambda e: self._guardar_estado_about(tree, root))
            
            # Autor
            tk.Label(frame_datos, text="Autor *", 
                    bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                    font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
            self.entry_autor_about = tk.Entry(frame_datos, bg=self.colores['fondo_terciario'], 
                                 fg=self.colores['texto_principal'], font=('Segoe UI', 10),
                                 width=50, relief='flat', highlightthickness=1,
                                 highlightcolor=self.colores['acento'],
                                 highlightbackground=self.colores['borde'])
            self.entry_autor_about.insert(0, autor)
            self.entry_autor_about.pack(fill='x', pady=(0, 15))
            self.entry_autor_about.bind('<KeyRelease>', lambda e: self._guardar_estado_about(tree, root))
            
            # Package ID
            tk.Label(frame_datos, text="Package ID *", 
                    bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                    font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
            self.entry_package_id_about = tk.Entry(frame_datos, bg=self.colores['fondo_terciario'], 
                                      fg=self.colores['texto_principal'], font=('Segoe UI', 10),
                                      width=50, relief='flat', highlightthickness=1,
                                      highlightcolor=self.colores['acento'],
                                      highlightbackground=self.colores['borde'])
            self.entry_package_id_about.insert(0, package_id)
            self.entry_package_id_about.pack(fill='x', pady=(0, 15))
            self.entry_package_id_about.bind('<KeyRelease>', lambda e: self._guardar_estado_about(tree, root))
            
            # Workshop ID
            tk.Label(frame_datos, text="Workshop ID", 
                    bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                    font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
            frame_workshop = tk.Frame(frame_datos, bg=self.colores['fondo_principal'])
            frame_workshop.pack(fill='x', pady=(0, 15))
            
            entry_workshop_id = tk.Entry(frame_workshop, bg=self.colores['fondo_terciario'], 
                                       fg=self.colores['texto_principal'], font=('Segoe UI', 10),
                                       width=40, relief='flat', highlightthickness=1,
                                       highlightcolor=self.colores['acento'],
                                       highlightbackground=self.colores['borde'])
            entry_workshop_id.insert(0, workshop_id)
            entry_workshop_id.pack(side='left', fill='x', expand=True)
            
            btn_abrir_workshop = tk.Button(frame_workshop, text="🔗 Ver Workshop", 
                                         bg=self.colores['acento'], fg='white',
                                         font=('Segoe UI', 9), relief='flat', width=12,
                                         command=lambda: self.mostrar_workshop(entry_workshop_id.get()))
            btn_abrir_workshop.pack(side='left', padx=(10, 0))
            
            # Mod Icon Path con preview
            tk.Label(frame_datos, text="Ruta del Icono del Mod", 
                    bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                    font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
            
            frame_icono = tk.Frame(frame_datos, bg=self.colores['fondo_principal'])
            frame_icono.pack(fill='x', pady=(0, 15))
            
            # Frame para icono y preview
            frame_icono_preview = tk.Frame(frame_icono, bg=self.colores['fondo_principal'])
            frame_icono_preview.pack(fill='x')
            
            self.entry_icon_path_about = tk.Entry(frame_icono_preview, bg=self.colores['fondo_terciario'], 
                                     fg=self.colores['texto_principal'], font=('Segoe UI', 10),
                                     width=40, relief='flat', highlightthickness=1,
                                     highlightcolor=self.colores['acento'],
                                     highlightbackground=self.colores['borde'])
            self.entry_icon_path_about.insert(0, mod_icon_path)
            self.entry_icon_path_about.pack(side='left', fill='x', expand=True)
            self.entry_icon_path_about.bind('<KeyRelease>', lambda e: self._guardar_estado_about(tree, root))
            
            btn_buscar_icono = tk.Button(frame_icono_preview, text="🔍 Buscar", 
                                       bg=self.colores['verde'], fg='white',
                                       font=('Segoe UI', 9), relief='flat', width=8,
                                       command=lambda: self.buscar_icono_con_preview(self.entry_icon_path_about, self.frame_preview_about))
            btn_buscar_icono.pack(side='left', padx=(10, 0))
            
            # Frame para preview del icono
            self.frame_preview_about = tk.Frame(frame_icono, bg=self.colores['fondo_secundario'], relief='flat', bd=1)
            self.frame_preview_about.pack(fill='x', pady=(10, 0))
            
            # Actualizar preview inicial
            self.actualizar_preview_icono(mod_icon_path, self.frame_preview_about)
            
            # Descripción con botón de traducción
            tk.Label(scrollable_frame, text="Descripción *", 
                    bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                    font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
            
            frame_descripcion = tk.Frame(scrollable_frame, bg=self.colores['fondo_principal'])
            frame_descripcion.pack(fill='x', pady=(0, 10))
            
            self.text_descripcion_about = tk.Text(frame_descripcion, bg=self.colores['fondo_terciario'], 
                                     fg=self.colores['texto_principal'], font=('Segoe UI', 10),
                                     height=6, relief='flat', highlightthickness=1,
                                     highlightcolor=self.colores['acento'],
                                     highlightbackground=self.colores['borde'],
                                     wrap='word')
            self.text_descripcion_about.insert('1.0', descripcion)
            self.text_descripcion_about.pack(side='left', fill='x', expand=True)
            self.text_descripcion_about.bind('<KeyRelease>', lambda e: self._guardar_estado_about(tree, root))
            
            btn_traducir_desc = tk.Button(frame_descripcion, text="🌍\nTraducir", 
                                        bg=self.colores['morado'], fg='white',
                                        font=('Segoe UI', 9, 'bold'), relief='flat', width=6,
                                        command=lambda: self.traducir_descripcion(self.text_descripcion_about))
            btn_traducir_desc.pack(side='left', padx=(10, 0))
            
            # Versiones soportadas
            tk.Label(scrollable_frame, text="Versiones Soportadas *", 
                    bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                    font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 10))
            
            frame_versiones = tk.Frame(scrollable_frame, bg=self.colores['fondo_secundario'], relief='flat', bd=1)
            frame_versiones.pack(fill='x', pady=(0, 20))
            
            # Lista de versiones de RimWorld
            versiones_rimworld = ['1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6']
            self.vars_versiones_about = {}
            
            # Frame para checkboxes en columnas
            frame_checkboxes = tk.Frame(frame_versiones, bg=self.colores['fondo_secundario'])
            frame_checkboxes.pack(fill='x', padx=10, pady=10)
            
            # Crear checkboxes en 2 columnas
            for i, version in enumerate(versiones_rimworld):
                var = tk.BooleanVar(value=(version in versiones_soportadas))
                self.vars_versiones_about[version] = var
                
                # Determinar columna
                columna = i % 2
                fila = i // 2
                
                cb = tk.Checkbutton(frame_checkboxes, text=f"RimWorld {version}", 
                                  variable=var, bg=self.colores['fondo_secundario'],
                                  fg=self.colores['texto_principal'], font=('Segoe UI', 9),
                                  selectcolor=self.colores['fondo_terciario'],
                                  command=lambda: self._guardar_estado_about(tree, root))
                cb.grid(row=fila, column=columna, sticky='w', padx=(0, 20), pady=2)
            
            # Botones
            frame_botones = tk.Frame(scrollable_frame, bg=self.colores['fondo_principal'])
            frame_botones.pack(fill='x', pady=(20, 0))
            
            def guardar_about():
                # Guardar estado actual en historial antes de guardar
                self._guardar_estado_about(tree, root)
                
                # Validar campos obligatorios
                if not self.entry_nombre_about.get().strip():
                    messagebox.showwarning("Advertencia", "El nombre del mod es obligatorio")
                    return
                if not self.entry_autor_about.get().strip():
                    messagebox.showwarning("Advertencia", "El autor es obligatorio")
                    return
                if not self.entry_package_id_about.get().strip():
                    messagebox.showwarning("Advertencia", "El Package ID es obligatorio")
                    return
                if not self.text_descripcion_about.get('1.0', 'end-1c').strip():
                    messagebox.showwarning("Advertencia", "La descripción es obligatoria")
                    return
                
                # Obtener versiones seleccionadas
                versiones_seleccionadas = [v for v, var in self.vars_versiones_about.items() if var.get()]
                if not versiones_seleccionadas:
                    messagebox.showwarning("Advertencia", "Selecciona al menos una versión soportada")
                    return
                
                try:
                    # Actualizar campos existentes sin modificar estructura
                    if root.find('name') is not None:
                        root.find('name').text = self.entry_nombre_about.get().strip()
                    else:
                        ET.SubElement(root, 'name').text = self.entry_nombre_about.get().strip()
                    
                    if root.find('author') is not None:
                        root.find('author').text = self.entry_autor_about.get().strip()
                    else:
                        ET.SubElement(root, 'author').text = self.entry_autor_about.get().strip()
                    
                    if root.find('packageId') is not None:
                        root.find('packageId').text = self.entry_package_id_about.get().strip()
                    else:
                        ET.SubElement(root, 'packageId').text = self.entry_package_id_about.get().strip()
                    
                    if root.find('description') is not None:
                        root.find('description').text = self.text_descripcion_about.get('1.0', 'end-1c').strip()
                    else:
                        ET.SubElement(root, 'description').text = self.text_descripcion_about.get('1.0', 'end-1c').strip()
                    
                    # Mod Icon Path - solo actualizar si hay valor
                    icon_path = self.entry_icon_path_about.get().strip()
                    if icon_path:
                        if root.find('modIconPath') is not None:
                            root.find('modIconPath').text = icon_path
                        else:
                            # Solo crear si no existe y hay valor
                            ET.SubElement(root, 'modIconPath').text = icon_path
                    elif root.find('modIconPath') is not None:
                        # Si existe pero ahora está vacío, eliminarlo
                        root.remove(root.find('modIconPath'))
                    
                    # Versiones soportadas - mantener estructura original
                    supported_versions = root.find('supportedVersions')
                    if supported_versions is not None:
                        # Limpiar versiones existentes
                        for li in supported_versions.findall('li'):
                            supported_versions.remove(li)
                    else:
                        # Crear elemento si no existe
                        supported_versions = ET.SubElement(root, 'supportedVersions')
                    
                    # Agregar versiones seleccionadas
                    for version in versiones_seleccionadas:
                        ET.SubElement(supported_versions, 'li').text = version
                    
                    # Guardar XML manteniendo formato
                    tree.write(ruta_about, encoding='utf-8', xml_declaration=True)
                    
                    # Guardar Workshop ID si se proporcionó
                    workshop_id_text = entry_workshop_id.get().strip()
                    if workshop_id_text:
                        with open(ruta_published_id, 'w', encoding='utf-8') as f:
                            f.write(workshop_id_text)
                    elif os.path.exists(ruta_published_id):
                        # Si existe el archivo pero no hay ID, eliminarlo
                        os.remove(ruta_published_id)
                    
                    messagebox.showinfo("Éxito", "About.xml guardado correctamente")
                    # No cerrar la ventana
                    
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
            
            def cancelar():
                nonlocal dialogo_cerrada
                dialogo_cerrada = True
                dialogo.destroy()
            
            btn_guardar = tk.Button(frame_botones, text="💾 GUARDAR", 
                                  bg=self.colores['exito'], fg='white',
                                  font=('Segoe UI', 11, 'bold'), relief='flat', width=12,
                                  command=guardar_about)
            btn_guardar.pack(side='left', padx=(0, 10))
            
            btn_cancelar = tk.Button(frame_botones, text="❌ CERRAR", 
                                   bg=self.colores['error'], fg='white',
                                   font=('Segoe UI', 11, 'bold'), relief='flat', width=12,
                                   command=cancelar)
            btn_cancelar.pack(side='left')
            
            # Empaquetar canvas y scrollbar
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar About.xml: {str(e)}")

    def actualizar_preview_icono(self, ruta_icono, frame_preview):
        """Actualiza el preview del icono del mod"""
        # Limpiar frame
        for widget in frame_preview.winfo_children():
            widget.destroy()
        
        if not ruta_icono or not self.carpeta_mod:
            tk.Label(frame_preview, text="🖼️ No hay icono seleccionado", 
                    bg=self.colores['fondo_secundario'], fg=self.colores['texto_secundario'],
                    font=('Segoe UI', 9)).pack(pady=20)
            return
        
        ruta_completa = os.path.join(self.carpeta_mod, ruta_icono)
        
        if not os.path.exists(ruta_completa):
            tk.Label(frame_preview, text="❌ Icono no encontrado", 
                    bg=self.colores['fondo_secundario'], fg=self.colores['texto_secundario'],
                    font=('Segoe UI', 9)).pack(pady=20)
            return
        
        if PIL_AVAILABLE:
            try:
                image = Image.open(ruta_completa)
                # Redimensionar manteniendo aspecto
                image.thumbnail((100, 100), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                label_imagen = tk.Label(frame_preview, image=photo, bg=self.colores['fondo_secundario'])
                label_imagen.image = photo  # Mantener referencia
                label_imagen.pack(pady=10)
                
                tk.Label(frame_preview, text="Preview del Icono", 
                        bg=self.colores['fondo_secundario'], fg=self.colores['texto_secundario'],
                        font=('Segoe UI', 8)).pack(pady=(0, 10))
                
            except Exception as e:
                tk.Label(frame_preview, text=f"❌ Error: {str(e)}", 
                        bg=self.colores['fondo_secundario'], fg=self.colores['texto_secundario'],
                        font=('Segoe UI', 8)).pack(pady=20)
        else:
            tk.Label(frame_preview, text="📁 Icono encontrado", 
                    bg=self.colores['fondo_secundario'], fg=self.colores['texto_secundario'],
                    font=('Segoe UI', 9)).pack(pady=20)
            tk.Label(frame_preview, text="(Instala Pillow para ver preview)", 
                    bg=self.colores['fondo_secundario'], fg=self.colores['texto_secundario'],
                    font=('Segoe UI', 7)).pack()

    def buscar_icono_con_preview(self, entry_icon_path, frame_preview):
        """Busca archivos de icono con preview"""
        if not self.carpeta_mod:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta de mod")
            return
        
        # Buscar en Textures y otras carpetas comunes
        carpetas_busqueda = [
            os.path.join(self.carpeta_mod, "Textures"),
            os.path.join(self.carpeta_mod, "Textures", "GUI"),
            os.path.join(self.carpeta_mod, "GUI"),
            os.path.join(self.carpeta_mod, "UI"),
            self.carpeta_mod
        ]
        
        archivos_imagen = []
        
        for carpeta in carpetas_busqueda:
            if os.path.exists(carpeta):
                formatos_imagen = ['*.png', '*.jpg', '*.jpeg', '*.dds']
                for formato in formatos_imagen:
                    for root, dirs, files in os.walk(carpeta):
                        for file in files:
                            if file.lower().endswith(formato[1:]):
                                ruta_relativa = os.path.relpath(os.path.join(root, file), self.carpeta_mod)
                                archivos_imagen.append(ruta_relativa)
        
        if not archivos_imagen:
            messagebox.showinfo("Información", "No se encontraron archivos de imagen")
            return
        
        # Mostrar diálogo de selección
        dialogo_seleccion = tk.Toplevel(self.ventana)
        dialogo_seleccion.title("Seleccionar Icono")
        dialogo_seleccion.geometry("600x500")
        dialogo_seleccion.transient(self.ventana)
        dialogo_seleccion.grab_set()
        dialogo_seleccion.configure(bg=self.colores['fondo_principal'])
        
        tk.Label(dialogo_seleccion, text="Selecciona un archivo de icono:", 
                bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                font=('Segoe UI', 11, 'bold')).pack(pady=10)
        
        # Frame para lista y preview
        frame_contenido = tk.Frame(dialogo_seleccion, bg=self.colores['fondo_principal'])
        frame_contenido.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Lista de archivos
        frame_lista = tk.Frame(frame_contenido, bg=self.colores['fondo_principal'])
        frame_lista.pack(side='left', fill='both', expand=True)
        
        lista_archivos = tk.Listbox(frame_lista, bg=self.colores['fondo_terciario'],
                                  fg=self.colores['texto_principal'], font=('Segoe UI', 10),
                                  selectbackground=self.colores['acento'])
        lista_archivos.pack(fill='both', expand=True)
        
        for archivo in sorted(archivos_imagen):
            lista_archivos.insert(tk.END, archivo)
        
        # Preview
        frame_preview_seleccion = tk.Frame(frame_contenido, bg=self.colores['fondo_secundario'], 
                                         relief='flat', bd=1, width=150)
        frame_preview_seleccion.pack(side='right', fill='both', padx=(10, 0))
        frame_preview_seleccion.pack_propagate(False)
        
        tk.Label(frame_preview_seleccion, text="Preview", 
                bg=self.colores['fondo_secundario'], fg=self.colores['texto_principal'],
                font=('Segoe UI', 9, 'bold')).pack(pady=5)
        
        label_preview = tk.Label(frame_preview_seleccion, bg=self.colores['fondo_secundario'])
        label_preview.pack(pady=10)
        
        def actualizar_preview_seleccion(event):
            seleccion = lista_archivos.curselection()
            if seleccion:
                archivo_seleccionado = archivos_imagen[seleccion[0]]
                ruta_completa = os.path.join(self.carpeta_mod, archivo_seleccionado)
                
                if PIL_AVAILABLE and os.path.exists(ruta_completa):
                    try:
                        image = Image.open(ruta_completa)
                        image.thumbnail((120, 120), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                        label_preview.configure(image=photo)
                        label_preview.image = photo
                    except:
                        label_preview.configure(text="❌", image='')
                else:
                    label_preview.configure(text="📁", image='')
        
        lista_archivos.bind('<<ListboxSelect>>', actualizar_preview_seleccion)
        
        def seleccionar():
            seleccion = lista_archivos.curselection()
            if seleccion:
                archivo_seleccionado = archivos_imagen[seleccion[0]]
                entry_icon_path.delete(0, tk.END)
                entry_icon_path.insert(0, archivo_seleccionado)
                # Actualizar preview en el editor principal
                self.actualizar_preview_icono(archivo_seleccionado, frame_preview)
                dialogo_seleccion.destroy()
            else:
                messagebox.showwarning("Advertencia", "Selecciona un archivo")
        
        frame_botones = tk.Frame(dialogo_seleccion, bg=self.colores['fondo_principal'])
        frame_botones.pack(fill='x', pady=10)
        
        btn_seleccionar = tk.Button(frame_botones, text="✅ SELECCIONAR", 
                                  bg=self.colores['exito'], fg='white',
                                  font=('Segoe UI', 10, 'bold'), relief='flat',
                                  command=seleccionar)
        btn_seleccionar.pack(side='left', padx=(10, 5))
        
        btn_cancelar = tk.Button(frame_botones, text="❌ CANCELAR", 
                               bg=self.colores['error'], fg='white',
                               font=('Segoe UI', 10, 'bold'), relief='flat',
                               command=dialogo_seleccion.destroy)
        btn_cancelar.pack(side='left', padx=(5, 10))

    def traducir_descripcion(self, text_widget):
        """Traduce la descripción usando Google Translate"""
        texto_actual = text_widget.get('1.0', 'end-1c')
        if not texto_actual.strip():
            messagebox.showwarning("Advertencia", "No hay texto para traducir")
            return
        
        try:
            texto_traducido = GoogleTranslator(source='auto', target='es').translate(texto_actual)
            if texto_traducido:
                text_widget.delete('1.0', tk.END)
                text_widget.insert('1.0', texto_traducido)
                messagebox.showinfo("Éxito", "Descripción traducida")
            else:
                messagebox.showerror("Error", "No se pudo traducir la descripción")
        except Exception as e:
            messagebox.showerror("Error", f"Error en traducción: {str(e)}")

    def mostrar_workshop(self, workshop_id):
        """Muestra la página del workshop en una ventana integrada"""
        if not workshop_id.strip():
            messagebox.showwarning("Advertencia", "Ingresa un Workshop ID")
            return
        
        # En una implementación real, aquí integrarías un navegador web embebido
        # Por ahora, mostramos información básica
        dialogo = tk.Toplevel(self.ventana)
        dialogo.title(f"Workshop - ID: {workshop_id}")
        dialogo.geometry("500x300")
        dialogo.transient(self.ventana)
        dialogo.grab_set()
        dialogo.configure(bg=self.colores['fondo_principal'])
        
        frame_principal = tk.Frame(dialogo, bg=self.colores['fondo_principal'], padx=20, pady=20)
        frame_principal.pack(fill='both', expand=True)
        
        tk.Label(frame_principal, text="🔗 Workshop de Steam", 
                bg=self.colores['fondo_principal'], fg=self.colores['texto_principal'],
                font=('Segoe UI', 14, 'bold')).pack(pady=(0, 10))
        
        tk.Label(frame_principal, text=f"ID del Mod: {workshop_id}", 
                bg=self.colores['fondo_principal'], fg=self.colores['texto_secundario'],
                font=('Segoe UI', 11)).pack(pady=(0, 20))
        
        info_text = (
            "En una versión completa, aquí se mostraría la página\n"
            "del workshop de Steam integrada en la aplicación.\n\n"
            f"URL: https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
        )
        
        tk.Label(frame_principal, text=info_text, 
                bg=self.colores['fondo_principal'], fg=self.colores['texto_secundario'],
                font=('Segoe UI', 10), justify='center').pack(pady=(0, 20))
        
        def abrir_navegador():
            webbrowser.open(f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}")
            dialogo.destroy()
        
        def cerrar():
            dialogo.destroy()
        
        frame_botones = tk.Frame(frame_principal, bg=self.colores['fondo_principal'])
        frame_botones.pack(fill='x')
        
        btn_abrir = tk.Button(frame_botones, text="🌐 Abrir en Navegador", 
                            bg=self.colores['acento'], fg='white',
                            font=('Segoe UI', 10, 'bold'), relief='flat', width=15,
                            command=abrir_navegador)
        btn_abrir.pack(side='left', padx=(0, 10))
        
        btn_cerrar = tk.Button(frame_botones, text="❌ Cerrar", 
                             bg=self.colores['error'], fg='white',
                             font=('Segoe UI', 10, 'bold'), relief='flat', width=10,
                             command=cerrar)
        btn_cerrar.pack(side='left')

    # ========== CORRECCIÓN ORTOGRÁFICA ==========

    def corregir_ortografia(self):
        """Corrige la ortografía de los textos seleccionados usando servicio web"""
        seleccionados = self.tree_textos.selection()
        if not seleccionados:
            messagebox.showwarning("Advertencia", "Selecciona textos para corregir")
            return
        
        threading.Thread(target=self._corregir_ortografia, args=(seleccionados,), daemon=True).start()

    def _corregir_ortografia(self, seleccionados):
        """Corrige ortografía usando servicio web gratuito"""
        try:
            total = len(seleccionados)
            corregidos = 0
            self.actualizar_status(f"✏️ Corrigiendo ortografía en {total} textos...")
            
            for i, item in enumerate(seleccionados):
                valores = list(self.tree_textos.item(item, 'values'))
                texto_traducido = valores[2] if len(valores) > 2 else ""
                
                if texto_traducido and texto_traducido.strip():
                    texto_corregido = self._corregir_texto_online(texto_traducido)
                    if texto_corregido and texto_corregido != texto_traducido:
                        valores[2] = texto_corregido
                        valores[3] = "✅ Corregido"
                        self.tree_textos.item(item, values=valores)
                        
                        id_texto = valores[0]
                        self.traducciones[id_texto] = texto_corregido
                        corregidos += 1
                
                # Actualizar progreso
                if i % 5 == 0:
                    self.ventana.after(0, self.actualizar_status, f"✏️ Corrigiendo... {i+1}/{total}")
                    time.sleep(0.5)
            
            self.ventana.after(0, self.actualizar_estadisticas)
            self.ventana.after(0, self.actualizar_status, f"✅ {corregidos} textos corregidos")
            
        except Exception as e:
            self.ventana.after(0, self.actualizar_status, f"❌ Error en corrección: {str(e)}")

    def _corregir_texto_online(self, texto):
        """Usa servicio web gratuito para corrección ortográfica"""
        try:
            # Usar LanguageTool API (gratuito)
            texto_corregido = self._usar_languagetool(texto)
            if texto_corregido:
                return texto_corregido
            
            # Si falla, usar corrección básica
            return self._correccion_basica(texto)
            
        except Exception as e:
            print(f"Error en corrección online: {e}")
            return self._correccion_basica(texto)

    def _usar_languagetool(self, texto):
        """Usa LanguageTool API gratuita"""
        try:
            url = "https://api.languagetool.org/v2/check"
            data = {
                'text': texto,
                'language': 'es',
                'enabledOnly': 'false'
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                corrected_text = texto
                
                # Aplicar correcciones
                matches = result.get('matches', [])
                if matches:
                    matches.sort(key=lambda x: x['offset'], reverse=True)
                    
                    for match in matches:
                        if match['replacements']:
                            replacement = match['replacements'][0]['value']
                            start = match['offset']
                            end = start + match['length']
                            corrected_text = corrected_text[:start] + replacement + corrected_text[end:]
                
                return corrected_text if corrected_text != texto else texto
                
        except Exception as e:
            print(f"Error con LanguageTool: {e}")
        
        return None

    def _correccion_basica(self, texto):
        """Corrección básica local para errores comunes"""
        try:
            correcciones = {
                ' ase ': ' hace ',
                ' aze ': ' hace ',
                ' abia ': ' había ',
                ' anque ': ' aunque ',
                ' estavan ': ' estaban ',
                ' iva ': ' iba ',
                ' enpesar ': ' empezar ',
                ' empesar ': ' empezar ',
                ' desir ': ' decir ',
                ' espesar ': ' empezar ',
            }
            
            texto_corregido = texto.lower()
            for error, correccion in correcciones.items():
                texto_corregido = texto_corregido.replace(error, correccion)
            
            # Capitalizar primera letra
            if texto_corregido and len(texto_corregido) > 0:
                texto_corregido = texto_corregido[0].upper() + texto_corregido[1:]
            
            return texto_corregido if texto_corregido != texto.lower() else texto
            
        except:
            return texto

    def guardar_xml(self):
        if not self.traducciones or not self.archivo_actual:
            messagebox.showwarning("Advertencia", "No hay traducciones para guardar")
            return
        
        try:
            tree = ET.parse(self.archivo_actual)
            root = tree.getroot()
            
            textos_guardados = 0
            
            for texto_info in self.textos_actuales:
                id_texto = texto_info['id']
                if id_texto in self.traducciones and self.traducciones[id_texto]:
                    texto_traducido = self.traducciones[id_texto]
                    
                    if texto_info['tipo'] == 'keyed':
                        for elem in root:
                            if elem.tag == texto_info['id']:
                                elem.text = texto_traducido
                                textos_guardados += 1
                                break
                    elif texto_info['tipo'] == 'elemento':
                        texto_info['elemento'].text = texto_traducido
                        textos_guardados += 1
                    elif texto_info['tipo'] == 'atributo':
                        texto_info['elemento'].set(texto_info['atributo'], texto_traducido)
                        textos_guardados += 1
            
            tree.write(self.archivo_actual, encoding='utf-8', xml_declaration=True)
            self.actualizar_status(f"💾 {textos_guardados} traducciones guardadas")
            messagebox.showinfo("Éxito", f"Guardadas {textos_guardados} traducciones")
            
        except Exception as e:
            self.actualizar_status(f"❌ Error guardando: {str(e)}")
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def actualizar_estadisticas(self, event=None):
        """Actualiza las estadísticas sin causar errores"""
        try:
            total = len(self.tree_textos.get_children())
            traducidos = 0
            corregidos = 0
            
            for item in self.tree_textos.get_children():
                valores = self.tree_textos.item(item, 'values')
                if len(valores) > 2 and valores[2] and valores[2].strip():
                    traducidos += 1
                if len(valores) > 3 and "Corregido" in str(valores[3]):
                    corregidos += 1
            
            # Actualizar el texto de forma segura
            texto_estadisticas = f"📊 Total: {total} | Traducidos: {traducidos} | Corregidos: {corregidos}"
            if hasattr(self, 'label_estadisticas'):
                self.label_estadisticas.config(text=texto_estadisticas)
                
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")

if __name__ == "__main__":
    app = EditorTematico()
    app.ventana.mainloop()