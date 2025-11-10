import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import tkinter as tk
import os
import xml.etree.ElementTree as ET
import threading
from deep_translator import GoogleTranslator
import re
import time
import shutil
import sys
import json
from datetime import datetime

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class EditorTematico:
    def __init__(self):
        # Configurar apariencia de CustomTkinter
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.ventana = ctk.CTk()
        self.ventana.title("Editor Temático Profesional - RimWorld")
        
        # Configurar ventana principal PRIMERO
        self.configurar_ventana_principal()
        
        # Variables de tema
        self.tema_oscuro = True
        self.colores = self.obtener_tema_oscuro()
        
        # Variables de estado
        self.carpeta_mod = ""
        self.idioma_cargado = ""
        self.archivos_xml = []
        self.archivo_actual = ""
        self.textos_actuales = []
        self.traducciones = {}
        
        # Variables para edición
        self.celda_editando = None
        self.entry_edicion = None
        
        # Variables para cache
        self.cache_traducciones = {}
        self.cache_placeholders = {}
        
        # Lista de idiomas actual
        self.lista_idiomas_actual = []
        
        # Lista para imágenes
        self.imagenes_preview = []
        self._cache_busqueda_imagenes = {}
        self._cache_emojis = {}  # Cache para emojis como CTkImage
        
        # Inicializar interfaz PRIMERO
        self.configurar_ventana()
        self.crear_interfaz_mejorada()
        self.configurar_bindings()
        
        # Cargar configuración DESPUÉS de crear la interfaz
        self.cargar_configuracion()
        self.cargar_cache_traducciones()
    
    def configurar_ventana_principal(self):
        """Configura el tamaño y posición de la ventana principal de forma segura"""
        try:
            # Obtener dimensiones de la pantalla de forma segura
            self.ventana.update_idletasks()
            ancho_pantalla = self.ventana.winfo_screenwidth()
            alto_pantalla = self.ventana.winfo_screenheight()
            
            # Usar 95% del monitor para dejar espacio para la barra de tareas
            ancho_ventana = int(ancho_pantalla * 0.95)
            alto_ventana = int(alto_pantalla * 0.95)
            
            # Posición centrada con márgenes
            x = (ancho_pantalla - ancho_ventana) // 2
            y = (alto_pantalla - alto_ventana) // 2
            
            self.ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
            self.ventana.minsize(1400, 800)
            
            # Configurar icono de forma segura
            try:
                if os.path.exists("icon.ico"):
                    self.ventana.iconbitmap(default="icon.ico")
            except:
                pass
                
        except Exception as e:
            # Fallback seguro
            print(f"Error configurando ventana: {e}")
            self.ventana.geometry("1400x800")
            self.ventana.minsize(1400, 800)
    
    def obtener_tema_oscuro(self):
        return {
            'fondo_principal': '#1a1a1a',
            'fondo_secundario': '#2d2d30',
            'fondo_terciario': '#3c3c40',
            'texto_principal': '#ffffff',
            'texto_secundario': '#cccccc',
            'texto_terciario': '#999999',
            'acento': '#0078d7',
            'verde': '#4ec9b0',
            'naranja': '#ce9178',
            'morado': '#c586c0',
            'gris_boton': '#5a5a5a',
            'borde': '#404040',
            'exito': '#4caf50',
            'advertencia': '#ff9800',
            'error': '#f44336',
            'seleccion': '#264f78',
            'header_tabla': '#252526',
            'fila_alterna': '#2a2a2c',
            'hover': '#3a3a3c'
        }
    
    def obtener_tema_claro(self):
        return {
            'fondo_principal': '#f8f9fa',
            'fondo_secundario': '#e9ecef',
            'fondo_terciario': '#ffffff',
            'texto_principal': '#212529',
            'texto_secundario': '#495057',
            'texto_terciario': '#6c757d',
            'acento': '#0078d7',
            'verde': '#28a745',
            'naranja': '#fd7e14',
            'morado': '#6f42c1',
            'gris_boton': '#6c757d',
            'borde': '#dee2e6',
            'exito': '#28a745',
            'advertencia': '#ffc107',
            'error': '#dc3545',
            'seleccion': '#d4e6f1',
            'header_tabla': '#e9ecef',
            'fila_alterna': '#f8f9fa',
            'hover': '#e2e6ea'
        }
    
    def configurar_ventana(self):
        self.ventana.grid_rowconfigure(1, weight=1)
        self.ventana.grid_columnconfigure(0, weight=1)
    
    def crear_emoji_image(self, emoji, size=20):
        """Crear emojis como CTkImage para evitar warnings"""
        cache_key = f"{emoji}_{size}"
        if cache_key in self._cache_emojis:
            return self._cache_emojis[cache_key]
        
        if not PIL_AVAILABLE:
            return None
            
        try:
            # Crear imagen con el emoji
            image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Intentar usar una fuente que soporte emojis
            try:
                font = ImageFont.truetype("seguiemj.ttf", size-4)  # Windows
            except:
                try:
                    font = ImageFont.truetype("Apple Color Emoji.ttf", size-4)  # macOS
                except:
                    try:
                        font = ImageFont.truetype("NotoColorEmoji.ttf", size-4)  # Linux
                    except:
                        # Fallback a fuente básica
                        font = ImageFont.load_default()
            
            # Dibujar emoji centrado
            bbox = draw.textbbox((0, 0), emoji, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            draw.text((x, y), emoji, font=font, fill='white')
            
            ctk_image = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=(size, size)
            )
            
            self._cache_emojis[cache_key] = ctk_image
            return ctk_image
            
        except Exception as e:
            print(f"Error creando emoji {emoji}: {e}")
            return None
    
    def crear_interfaz_mejorada(self):
        # Barra superior
        self.frame_superior = ctk.CTkFrame(self.ventana, height=160)
        self.frame_superior.grid(row=0, column=0, sticky='ew', padx=20, pady=15)
        self.frame_superior.grid_propagate(False)
        
        # Configurar grid con más columnas
        for i in range(12):
            self.frame_superior.grid_columnconfigure(i, weight=1)
        
        # Título principal
        frame_titulo = ctk.CTkFrame(self.frame_superior, fg_color="transparent")
        frame_titulo.grid(row=0, column=0, columnspan=12, sticky='ew', pady=(0, 10))
        
        # Usar label normal para el título (sin emoji como imagen)
        ctk.CTkLabel(frame_titulo, text="Editor Temático RimWorld", 
                    font=('Segoe UI', 16, 'bold')).pack(side='left')
        
        self.btn_tema = ctk.CTkButton(frame_titulo, text="Cambiar Tema", 
                                 command=self.cambiar_tema, width=100)
        self.btn_tema.pack(side='right', padx=(0, 10))
        
        # Fila 1: Proyecto e Idioma
        ctk.CTkLabel(self.frame_superior, text="PROYECTO:", 
                    font=('Segoe UI', 9, 'bold')).grid(row=1, column=0, padx=(0, 5), pady=3, sticky='w')
        
        # CREAR entry_ruta ANTES de usarlo
        self.entry_ruta = ctk.CTkEntry(self.frame_superior, 
                                 font=('Segoe UI', 9), 
                                 width=280,
                                 placeholder_text="Selecciona una carpeta de mod...")
        self.entry_ruta.grid(row=1, column=1, padx=(0, 5), pady=3, sticky='w')
        
        btn_buscar = ctk.CTkButton(self.frame_superior, text="Buscar", 
                              command=self.buscar_carpeta_mod, width=80)
        btn_buscar.grid(row=1, column=2, padx=(0, 15), pady=3)
        
        ctk.CTkLabel(self.frame_superior, text="IDIOMA:", 
                    font=('Segoe UI', 9, 'bold')).grid(row=1, column=3, padx=(0, 5), pady=3, sticky='w')
        
        self.combo_idiomas = ctk.CTkComboBox(self.frame_superior, state="readonly", 
                                         width=180, font=('Segoe UI', 9))
        self.combo_idiomas.grid(row=1, column=4, padx=(0, 5), pady=3, sticky='w')
        self.combo_idiomas.bind('<<ComboboxSelected>>', self.al_seleccionar_idioma)
        
        self.btn_recargar_idiomas = ctk.CTkButton(self.frame_superior, text="Recargar", 
                                        command=self.recargar_idiomas, width=80)
        self.btn_recargar_idiomas.grid(row=1, column=5, padx=(0, 15), pady=3)
        
        # Fila 2: Archivo y búsqueda
        ctk.CTkLabel(self.frame_superior, text="ARCHIVO:", 
                    font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, padx=(0, 5), pady=3, sticky='w')
        
        self.combo_archivos = ctk.CTkComboBox(self.frame_superior, state="readonly", 
                                          width=200, font=('Segoe UI', 9))
        self.combo_archivos.grid(row=2, column=1, padx=(0, 5), pady=3, sticky='w')
        
        self.btn_cargar = ctk.CTkButton(self.frame_superior, text="CARGAR", 
                              command=self.cargar_archivo_seleccionado, width=80)
        self.btn_cargar.grid(row=2, column=2, padx=(0, 15), pady=3)
        
        ctk.CTkLabel(self.frame_superior, text="BUSCAR:", 
                    font=('Segoe UI', 9, 'bold')).grid(row=2, column=3, padx=(0, 5), pady=3, sticky='w')
        
        self.entry_buscar = ctk.CTkEntry(self.frame_superior, 
                                    font=('Segoe UI', 9), 
                                    width=200,
                                    placeholder_text="Buscar textos...")
        self.entry_buscar.grid(row=2, column=4, padx=(0, 15), pady=3, sticky='w')
        self.entry_buscar.bind('<KeyRelease>', self.filtrar_textos)
        
        # Botones de acción
        frame_botones_fila1 = ctk.CTkFrame(self.frame_superior, fg_color="transparent")
        frame_botones_fila1.grid(row=1, column=8, columnspan=4, padx=(20, 0), pady=2, sticky='e')
        
        self.btn_traducir = ctk.CTkButton(frame_botones_fila1, text="TRADUCIR", 
                                command=self.traducir_seleccion, width=120,
                                fg_color='#9b59b6', hover_color='#8e44ad')
        self.btn_traducir.pack(side='left', padx=(0, 5))
        
        self.btn_editar_defs = ctk.CTkButton(frame_botones_fila1, text="EDITAR DEFS", 
                                command=self.editar_defs, width=120,
                                fg_color='#16a085', hover_color='#138a6f')
        self.btn_editar_defs.pack(side='left', padx=(0, 5))
        
        self.btn_guardar = ctk.CTkButton(frame_botones_fila1, text="GUARDAR", 
                               command=self.guardar_xml, width=100,
                               fg_color='#27ae60', hover_color='#219653')
        self.btn_guardar.pack(side='left')
        
        frame_botones_fila2 = ctk.CTkFrame(self.frame_superior, fg_color="transparent")
        frame_botones_fila2.grid(row=2, column=8, columnspan=4, padx=(20, 0), pady=2, sticky='e')
        
        self.btn_crear_idioma = ctk.CTkButton(frame_botones_fila2, text="CREAR IDIOMA", 
                                command=self.crear_nuevo_idioma, width=120,
                                fg_color='#8e44ad', hover_color='#7d3c98')
        self.btn_crear_idioma.pack(side='left', padx=(0, 5))
        
        self.btn_editar_about = ctk.CTkButton(frame_botones_fila2, text="EDITAR ABOUT", 
                                command=self.editar_about, width=120,
                                fg_color='#f39c12', hover_color='#e08e0b')
        self.btn_editar_about.pack(side='left')
        
        # Fila 3: Filtros
        self.crear_filtros_busqueda()
        
        # Área de la tabla
        frame_tabla = ctk.CTkFrame(self.ventana)
        frame_tabla.grid(row=1, column=0, sticky='nsew', padx=20, pady=(0, 10))
        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)
        
        self.actualizar_estilo_tabla()
        
        # Crear Treeview
        self.tree_textos = ttk.Treeview(frame_tabla, 
                                      columns=('id', 'original', 'traducido', 'estado'), 
                                      show='headings',
                                      style="Tema.Treeview",
                                      selectmode='extended')
        
        # Configurar columnas
        self.tree_textos.heading('id', text='ID', anchor='w')
        self.tree_textos.heading('original', text='ORIGINAL', anchor='w')
        self.tree_textos.heading('traducido', text='TRADUCIDO', anchor='w')
        self.tree_textos.heading('estado', text='ESTADO', anchor='w')
        
        ancho_pantalla = self.ventana.winfo_screenwidth()
        self.tree_textos.column('id', width=int(ancho_pantalla * 0.15), anchor='w', minwidth=120)
        self.tree_textos.column('original', width=int(ancho_pantalla * 0.30), anchor='w', minwidth=200)
        self.tree_textos.column('traducido', width=int(ancho_pantalla * 0.30), anchor='w', minwidth=200)
        self.tree_textos.column('estado', width=int(ancho_pantalla * 0.12), anchor='w', minwidth=100)
        
        # Scrollbars
        scroll_vertical = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree_textos.yview,
                                       style="Tema.Vertical.TScrollbar")
        scroll_horizontal = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.tree_textos.xview,
                                         style="Tema.Horizontal.TScrollbar")
        self.tree_textos.configure(yscrollcommand=scroll_vertical.set, xscrollcommand=scroll_horizontal.set)
        
        # Grid
        self.tree_textos.grid(row=0, column=0, sticky='nsew')
        scroll_vertical.grid(row=0, column=1, sticky='ns')
        scroll_horizontal.grid(row=1, column=0, sticky='ew')
        
        # Barra de estado
        self.status_bar = ctk.CTkLabel(self.ventana, 
                                  text="Selecciona una carpeta de mod | Ctrl+C: Copiar | Ctrl+V: Pegar | Doble clic: Editar | Ctrl+A: Seleccionar todo", 
                                  font=('Segoe UI', 9), anchor='w')
        self.status_bar.grid(row=2, column=0, sticky='ew', padx=20, pady=(0, 10))

    def crear_filtros_busqueda(self):
        """Crea la interfaz para filtros de búsqueda avanzada"""
        frame_filtros = ctk.CTkFrame(self.frame_superior, fg_color="transparent")
        frame_filtros.grid(row=3, column=0, columnspan=8, sticky='ew', pady=(8, 0))
        
        # Filtro por estado
        ctk.CTkLabel(frame_filtros, text="FILTRAR POR ESTADO:", 
                    font=('Segoe UI', 9, 'bold')).pack(side='left', padx=(0, 5))
        
        estados = ["Todos", "Pendientes", "Traducidos", "Editados"]
        self.combo_filtro_estado = ctk.CTkComboBox(frame_filtros, values=estados, state="readonly", width=120)
        self.combo_filtro_estado.set("Todos")
        self.combo_filtro_estado.pack(side='left', padx=(0, 15))
        self.combo_filtro_estado.bind('<<ComboboxSelected>>', self.aplicar_filtros)
        
        # Filtro por tipo de texto
        ctk.CTkLabel(frame_filtros, text="FILTRAR POR TIPO:", 
                    font=('Segoe UI', 9, 'bold')).pack(side='left', padx=(0, 5))
        
        tipos = ["Todos", "Con Placeholders", "Sin Placeholders"]
        self.combo_filtro_tipo = ctk.CTkComboBox(frame_filtros, values=tipos, state="readonly", width=150)
        self.combo_filtro_tipo.set("Todos")
        self.combo_filtro_tipo.pack(side='left', padx=(0, 15))
        self.combo_filtro_tipo.bind('<<ComboboxSelected>>', self.aplicar_filtros)
        
        # Botones de acción para filtros
        btn_limpiar_filtros = ctk.CTkButton(frame_filtros, text="LIMPIAR FILTROS", 
                                      command=self.limpiar_filtros, width=150,
                                      fg_color='#f44336', hover_color='#d32f2f')
        btn_limpiar_filtros.pack(side='left', padx=(0, 10))

    def cambiar_tema(self):
        self.tema_oscuro = not self.tema_oscuro
        if self.tema_oscuro:
            ctk.set_appearance_mode("Dark")
            self.colores = self.obtener_tema_oscuro()
            self.btn_tema.configure(text="Modo Claro")
        else:
            ctk.set_appearance_mode("Light")
            self.colores = self.obtener_tema_claro()
            self.btn_tema.configure(text="Modo Oscuro")
        self.actualizar_tema()
        self.guardar_configuracion()
    
    def actualizar_tema(self):
        """Actualiza todos los elementos de la interfaz al cambiar el tema"""
        self.actualizar_estilo_tabla()
    
    def actualizar_estilo_tabla(self):
        """Configura el estilo de la tabla según el tema actual"""
        style = ttk.Style()
        
        if self.tema_oscuro:
            style.theme_use('clam')
            style.configure("Tema.Treeview",
                background=self.colores['fondo_terciario'],
                foreground=self.colores['texto_principal'],
                fieldbackground=self.colores['fondo_terciario'],
                borderwidth=0,
                font=('Segoe UI', 10),
                rowheight=25
            )
            style.configure("Tema.Treeview.Heading",
                background=self.colores['header_tabla'],
                foreground=self.colores['texto_principal'],
                relief="flat",
                borderwidth=1,
                font=('Segoe UI', 10, 'bold'),
                padding=(5, 5)
            )
            style.map("Tema.Treeview",
                background=[('selected', self.colores['seleccion'])],
                foreground=[('selected', self.colores['texto_principal'])]
            )
        else:
            style.theme_use('clam')
            style.configure("Tema.Treeview",
                background=self.colores['fondo_terciario'],
                foreground=self.colores['texto_principal'],
                fieldbackground=self.colores['fondo_terciario'],
                borderwidth=0,
                font=('Segoe UI', 10),
                rowheight=25
            )
            style.configure("Tema.Treeview.Heading",
                background=self.colores['header_tabla'],
                foreground=self.colores['texto_principal'],
                relief="flat",
                borderwidth=1,
                font=('Segoe UI', 10, 'bold'),
                padding=(5, 5)
            )
            style.map("Tema.Treeview",
                background=[('selected', self.colores['seleccion'])],
                foreground=[('selected', self.colores['texto_principal'])]
            )
        
        style.configure("Tema.Vertical.TScrollbar",
            background=self.colores['fondo_secundario'],
            troughcolor=self.colores['fondo_principal'],
            borderwidth=0,
            relief='flat',
            arrowsize=12
        )
        
        style.configure("Tema.Horizontal.TScrollbar",
            background=self.colores['fondo_secundario'],
            troughcolor=self.colores['fondo_principal'],
            borderwidth=0,
            relief='flat',
            arrowsize=12
        )

    def guardar_cache_traducciones(self):
        """Guarda el cache de traducciones en un archivo"""
        try:
            cache_dir = os.path.join(os.path.expanduser("~"), ".rimworld_editor")
            os.makedirs(cache_dir, exist_ok=True)
            
            cache_file = os.path.join(cache_dir, "cache_traducciones.json")
            
            # Limpiar cache viejo (más de 1000 entradas)
            if len(self.cache_traducciones) > 1000:
                items = list(self.cache_traducciones.items())[-800:]
                self.cache_traducciones = dict(items)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'traducciones': self.cache_traducciones,
                    'placeholders': self.cache_placeholders,
                    'timestamp': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando cache: {e}")

    def cargar_cache_traducciones(self):
        """Carga el cache de traducciones desde archivo"""
        try:
            cache_file = os.path.join(os.path.expanduser("~"), ".rimworld_editor", "cache_traducciones.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.cache_traducciones = cache_data.get('traducciones', {})
                    self.cache_placeholders = cache_data.get('placeholders', {})
        except Exception as e:
            print(f"Error cargando cache: {e}")

    def guardar_configuracion(self):
        """Guarda la configuración de la aplicación"""
        try:
            config_dir = os.path.join(os.path.expanduser("~"), ".rimworld_editor")
            os.makedirs(config_dir, exist_ok=True)
            
            config_file = os.path.join(config_dir, "config.json")
            config = {
                'tema_oscuro': self.tema_oscuro,
                'carpeta_mod_reciente': self.carpeta_mod if self.carpeta_mod else "",
                'timestamp': datetime.now().isoformat()
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error guardando configuración: {e}")

    def cargar_configuracion(self):
        """Carga la configuración de la aplicación"""
        try:
            config_file = os.path.join(os.path.expanduser("~"), ".rimworld_editor", "config.json")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.tema_oscuro = config.get('tema_oscuro', True)
                    carpeta_reciente = config.get('carpeta_mod_reciente', "")
                    
                    if carpeta_reciente and os.path.exists(carpeta_reciente):
                        self.carpeta_mod = carpeta_reciente
                        if hasattr(self, 'entry_ruta'):  # ✅ VERIFICAR QUE EXISTE
                            self.entry_ruta.insert(0, carpeta_reciente)
                            threading.Thread(target=self._cargar_idiomas, daemon=True).start()
                        
        except Exception as e:
            print(f"Error cargando configuración: {e}")

    def buscar_carpeta_mod(self):
        """Busca la carpeta del mod y carga automáticamente los idiomas"""
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta del mod")
        if carpeta:
            self.limpiar_datos_anteriores()
            self.carpeta_mod = carpeta
            self.entry_ruta.delete(0, ctk.END)
            self.entry_ruta.insert(0, carpeta)
            self.actualizar_status("Cargando idiomas...")
            self.guardar_configuracion()
            threading.Thread(target=self._cargar_idiomas, daemon=True).start()

    def limpiar_datos_anteriores(self):
        """Limpia todos los datos del mod anterior"""
        self.idioma_cargado = ""
        self.archivos_xml = []
        self.archivo_actual = ""
        self.textos_actuales = []
        self.traducciones = {}
        self.lista_idiomas_actual = []
        
        # Limpiar comboboxes
        if hasattr(self, 'combo_idiomas'):
            self.combo_idiomas.set('')
            self.combo_idiomas.configure(values=[])
        if hasattr(self, 'combo_archivos'):
            self.combo_archivos.set('')
            self.combo_archivos.configure(values=[])
        
        # Limpiar tabla
        self._limpiar_tabla()

    def actualizar_status(self, mensaje):
        """Actualiza la barra de estado"""
        self.status_bar.configure(text=mensaje)

    def recargar_idiomas(self):
        """Recarga la lista de idiomas manualmente"""
        if not self.carpeta_mod:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta de mod")
            return
        
        self.actualizar_status("Recargando idiomas...")
        threading.Thread(target=self._cargar_idiomas, daemon=True).start()

    def _cargar_idiomas(self):
        """Carga automáticamente los idiomas de forma más inteligente"""
        try:
            if not self.carpeta_mod:
                return

            # Buscar carpeta Languages
            carpeta_languages = self._encontrar_carpeta_languages()
            
            if not carpeta_languages:
                self.ventana.after(0, lambda: self.actualizar_status("No se encontró carpeta 'Languages'"))
                return

            # Buscar idiomas
            idiomas_encontrados = []
            try:
                for item in os.listdir(carpeta_languages):
                    ruta_item = os.path.join(carpeta_languages, item)
                    if os.path.isdir(ruta_item) and self._tiene_archivos_xml(ruta_item):
                        nombre_legible = self._obtener_nombre_legible_idioma(item)
                        idiomas_encontrados.append({
                            'carpeta': item,
                            'ruta': ruta_item,
                            'nombre_legible': nombre_legible
                        })
            except Exception as e:
                self.ventana.after(0, lambda: self.actualizar_status(f"Error escaneando idiomas: {str(e)}"))
                return
            
            self.ventana.after(0, self._actualizar_combobox_idiomas, idiomas_encontrados)
            
        except Exception as e:
            self.ventana.after(0, lambda: self.actualizar_status(f"Error cargando idiomas: {str(e)}"))

    def _encontrar_carpeta_languages(self):
        """Encuentra la carpeta Languages"""
        if not self.carpeta_mod:
            return None
            
        posibles_rutas = [
            os.path.join(self.carpeta_mod, "Languages"),
            os.path.join(self.carpeta_mod, "1.4", "Languages"),
            os.path.join(self.carpeta_mod, "1.3", "Languages"),
            os.path.join(self.carpeta_mod, "Common", "Languages"),
        ]
        
        for ruta in posibles_rutas:
            if os.path.exists(ruta):
                return ruta
        
        # Búsqueda recursiva como fallback
        for root, dirs, files in os.walk(self.carpeta_mod):
            if 'Languages' in dirs:
                return os.path.join(root, 'Languages')
        return None

    def _tiene_archivos_xml(self, carpeta):
        """Verifica si una carpeta tiene archivos XML"""
        try:
            for root, dirs, files in os.walk(carpeta):
                for file in files:
                    if file.lower().endswith('.xml'):
                        return True
            return False
        except:
            return False

    def _obtener_nombre_legible_idioma(self, nombre_carpeta):
        """Convierte el nombre de carpeta a un nombre legible"""
        mapeo_idiomas = {
            'english': 'English',
            'spanish': 'Spanish (Español)',
            'french': 'French (Français)', 
            'german': 'German (Deutsch)',
            'italian': 'Italian (Italiano)',
            'portuguese': 'Portuguese (Português)',
            'russian': 'Russian (Русский)',
            'chinesesimplified': 'Chinese Simplified (简体中文)',
            'chinesetraditional': 'Chinese Traditional (繁體中文)',
            'japanese': 'Japanese (日本語)',
            'korean': 'Korean (한국어)',
        }
        
        nombre_limpio = nombre_carpeta.lower().replace('_', '').replace('-', '')
        return mapeo_idiomas.get(nombre_limpio, nombre_carpeta.title())

    def _actualizar_combobox_idiomas(self, idiomas_encontrados):
        """Actualiza el combobox de idiomas"""
        self.lista_idiomas_actual = idiomas_encontrados
        
        if idiomas_encontrados:
            display_values = [f"{idioma['nombre_legible']} ({idioma['carpeta']})" for idioma in idiomas_encontrados]
            self.combo_idiomas.configure(values=display_values)
            self.combo_idiomas.set(display_values[0])
            self.idioma_cargado = idiomas_encontrados[0]
            self.actualizar_status(f"{len(idiomas_encontrados)} idiomas cargados")
            
            # Cargar archivos del idioma seleccionado
            threading.Thread(target=self._cargar_archivos_idioma, daemon=True).start()
        else:
            self.combo_idiomas.configure(values=[])
            self.combo_idiomas.set('')
            self.actualizar_status("No se encontraron idiomas con archivos XML")

    def al_seleccionar_idioma(self, event):
        """Cuando se selecciona un idioma, carga automáticamente sus archivos"""
        seleccion_display = self.combo_idiomas.get()
        if seleccion_display:
            for idioma_info in self.lista_idiomas_actual:
                display_text = f"{idioma_info['nombre_legible']} ({idioma_info['carpeta']})"
                if display_text == seleccion_display:
                    self.idioma_cargado = idioma_info
                    break
            
            self.actualizar_status(f"Cargando archivos de {self.idioma_cargado['nombre_legible']}...")
            threading.Thread(target=self._cargar_archivos_idioma, daemon=True).start()

    def _cargar_archivos_idioma(self):
        """Carga todos los archivos XML del idioma seleccionado"""
        try:
            if not self.idioma_cargado:
                return
                
            carpeta_idioma = self.idioma_cargado['ruta']
            
            if not os.path.exists(carpeta_idioma):
                self.ventana.after(0, lambda: self.actualizar_status(f"No existe la carpeta {self.idioma_cargado['carpeta']}"))
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
                            'nombre_archivo': file,
                            'carpeta': os.path.basename(os.path.dirname(ruta_completa))
                        })
            
            self.archivos_xml.sort(key=lambda x: x['ruta_relativa'].lower())
            archivos_display = [f"{archivo['carpeta']}/{archivo['ruta_relativa']}" if archivo['carpeta'] != self.idioma_cargado['carpeta'] else archivo['ruta_relativa'] for archivo in self.archivos_xml]
            
            self.ventana.after(0, self._actualizar_combobox_archivos, archivos_display)
            
        except Exception as e:
            self.ventana.after(0, lambda: self.actualizar_status(f"Error cargando archivos: {str(e)}"))

    def _actualizar_combobox_archivos(self, archivos_display):
        if archivos_display:
            self.combo_archivos.configure(values=archivos_display)
            self.combo_archivos.set(archivos_display[0])
            self.actualizar_status(f"{len(archivos_display)} archivos XML encontrados")
        else:
            self.combo_archivos.configure(values=[])
            self.combo_archivos.set('')
            self.actualizar_status("No se encontraron archivos XML")

    def cargar_archivo_seleccionado(self):
        """Carga el archivo XML seleccionado en la tabla con mejor manejo de errores"""
        try:
            archivo_relativo = self.combo_archivos.get()
            if not archivo_relativo:
                messagebox.showwarning("Advertencia", "Selecciona un archivo XML")
                return
            
            archivo_encontrado = None
            for archivo_info in self.archivos_xml:
                display_text = f"{archivo_info['carpeta']}/{archivo_info['ruta_relativa']}" if archivo_info['carpeta'] != self.idioma_cargado['carpeta'] else archivo_info['ruta_relativa']
                if display_text == archivo_relativo:
                    archivo_encontrado = archivo_info
                    break
            
            if not archivo_encontrado:
                messagebox.showerror("Error", "No se pudo encontrar el archivo seleccionado")
                return
            
            # Verificar permisos de lectura
            if not os.access(archivo_encontrado['ruta_completa'], os.R_OK):
                messagebox.showerror("Error", f"No se puede leer el archivo: {archivo_encontrado['ruta_completa']}")
                return
                
            self.archivo_actual = archivo_encontrado['ruta_completa']
            self.actualizar_status(f"Cargando {os.path.basename(self.archivo_actual)}...")
            threading.Thread(target=self._cargar_textos_archivo, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}")

    def _cargar_textos_archivo(self):
        try:
            self.ventana.after(0, self._limpiar_tabla)
            self.textos_actuales = self.extraer_textos_xml(self.archivo_actual)
            self.traducciones = {}
            self.ventana.after(0, self._llenar_tabla)
            
        except Exception as e:
            self.ventana.after(0, lambda: self.actualizar_status(f"Error cargando archivo: {str(e)}"))

    def _limpiar_tabla(self):
        for item in self.tree_textos.get_children():
            self.tree_textos.delete(item)

    def _llenar_tabla(self):
        for i, texto_info in enumerate(self.textos_actuales):
            tags = ('even',) if i % 2 == 0 else ('odd',)
            self.tree_textos.insert('', 'end', 
                                  values=(texto_info['id'], texto_info['texto'], "", "Pendiente"),
                                  tags=tags)
        
        # Configurar colores alternos
        self.tree_textos.tag_configure('even', background=self.colores['fondo_terciario'])
        self.tree_textos.tag_configure('odd', background=self.colores['fila_alterna'])
        
        self.actualizar_status(f"{len(self.textos_actuales)} textos cargados")
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
            self.actualizar_status(f"Error en XML: {str(e)}")
        
        return textos

    def traducir_seleccion(self):
        seleccionados = self.tree_textos.selection()
        if not seleccionados:
            messagebox.showwarning("Advertencia", "Selecciona textos para traducir")
            return
        
        threading.Thread(target=self._traducir_seleccion, args=(seleccionados,), daemon=True).start()

    def _traducir_seleccion(self, seleccionados):
        """Traduce los textos seleccionados usando cache"""
        try:
            total = len(seleccionados)
            exitosos = 0
            fallidos = 0
            self.ventana.after(0, lambda: self.actualizar_status(f"Traduciendo {total} textos..."))
            
            for i, item in enumerate(seleccionados):
                try:
                    valores = self.tree_textos.item(item, 'values')
                    id_texto = valores[0]
                    texto_original = valores[1]
                    
                    if texto_original and len(texto_original.strip()) > 1:
                        # Verificar cache primero
                        cache_key = texto_original.strip().lower()
                        if cache_key in self.cache_traducciones:
                            texto_traducido = self.cache_traducciones[cache_key]
                            nuevos_valores = (valores[0], valores[1], texto_traducido, "Traducido (Cache)")
                            self.tree_textos.item(item, values=nuevos_valores)
                            self.traducciones[id_texto] = texto_traducido
                            exitosos += 1
                            continue
                        
                        # Extraer placeholders (usar cache si existe)
                        if cache_key in self.cache_placeholders:
                            placeholders = self.cache_placeholders[cache_key]
                        else:
                            placeholders = self._extraer_placeholders(texto_original)
                            self.cache_placeholders[cache_key] = placeholders
                        
                        # Crear texto temporal para traducción
                        texto_para_traducir = self._reemplazar_placeholders_para_traduccion(texto_original)
                        
                        if len(texto_para_traducir) > 4900:
                            texto_para_traducir = texto_para_traducir[:4900]
                        
                        texto_traducido_temp = GoogleTranslator(source='auto', target='es').translate(texto_para_traducir)
                        
                        if texto_traducido_temp:
                            # Restaurar placeholders en la traducción
                            texto_traducido = self._restaurar_placeholders(texto_traducido_temp, placeholders)
                            
                            # Guardar en cache
                            self.cache_traducciones[cache_key] = texto_traducido
                            
                            nuevos_valores = (valores[0], valores[1], texto_traducido, "Traducido")
                            self.tree_textos.item(item, values=nuevos_valores)
                            self.traducciones[id_texto] = texto_traducido
                            exitosos += 1
                        
                        time.sleep(0.2)  # Rate limiting
                    else:
                        fallidos += 1
                        
                except Exception as e:
                    print(f"Error traduciendo {id_texto}: {str(e)}")
                    fallidos += 1
                    continue
            
            mensaje_final = f"{exitosos}/{total} textos traducidos"
            if fallidos > 0:
                mensaje_final += f" ({fallidos} fallos)"
            self.ventana.after(0, lambda: self.actualizar_status(mensaje_final))
            
            # Guardar cache
            self.guardar_cache_traducciones()
            
        except Exception as e:
            self.ventana.after(0, lambda: self.actualizar_status(f"Error en traducción: {str(e)}"))

    def _extraer_placeholders(self, texto):
        """Extrae placeholders como {0}, {1}, {name}, etc."""
        placeholders = re.findall(r'\{[^}]+\}', texto)
        return list(set(placeholders))

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
        }
        
        texto_limpio = texto
        for patron, reemplazo in replacements.items():
            texto_limpio = re.sub(patron, reemplazo, texto_limpio)
        
        texto_limpio = re.sub(r'\{[^}]+\}', ' ELEMENTO ', texto_limpio)
        return texto_limpio

    def _restaurar_placeholders(self, texto_traducido, placeholders):
        """Restaura los placeholders originales en el texto traducido"""
        texto_con_placeholders = texto_traducido
        
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
            'ELEMENTO': placeholders[0] if placeholders else '{}'
        }
        
        for temporal, original in replacements_inversos.items():
            texto_con_placeholders = texto_con_placeholders.replace(temporal, original)
        
        return texto_con_placeholders

    def aplicar_filtros(self, event=None):
        """Aplica todos los filtros de búsqueda combinados"""
        self.filtrar_textos()

    def limpiar_filtros(self):
        """Limpia todos los filtros y muestra todos los textos"""
        self.combo_filtro_estado.set("Todos")
        self.combo_filtro_tipo.set("Todos")
        self.entry_buscar.delete(0, ctk.END)
        self.filtrar_textos()

    def filtrar_textos(self, event=None):
        """Búsqueda inteligente con filtros combinados"""
        texto_buscar = self.entry_buscar.get().lower().strip()
        filtro_estado = self.combo_filtro_estado.get()
        filtro_tipo = self.combo_filtro_tipo.get()
        
        # Ocultar todos los items primero
        for item in self.tree_textos.get_children():
            self.tree_textos.detach(item)
        
        # Aplicar filtros
        items_filtrados = 0
        for item in self.tree_textos.get_children(''):
            valores = self.tree_textos.item(item, 'values')
            
            # Aplicar filtro de estado
            if not self._cumple_filtro_estado(valores, filtro_estado):
                continue
                
            # Aplicar filtro de tipo
            if not self._cumple_filtro_tipo(valores, filtro_tipo):
                continue
                
            # Aplicar filtro de búsqueda de texto
            if not self._cumple_busqueda_texto(valores, texto_buscar):
                continue
            
            # Si pasa todos los filtros, mostrar el item
            self.tree_textos.attach(item, '', 'end')
            items_filtrados += 1
        
        self.actualizar_status(f"Mostrando {items_filtrados} textos filtrados")

    def _cumple_filtro_estado(self, valores, filtro_estado):
        """Verifica si el texto cumple con el filtro de estado"""
        if filtro_estado == "Todos":
            return True
            
        estado = valores[3] if len(valores) > 3 else ""
        
        if filtro_estado == "Pendientes":
            return "Pendiente" in estado or estado == ""
        elif filtro_estado == "Traducidos":
            return "Traducido" in estado
        elif filtro_estado == "Editados":
            return "Editado" in estado or "Pegado" in estado
            
        return True

    def _cumple_filtro_tipo(self, valores, filtro_tipo):
        """Verifica si el texto cumple con el filtro de tipo"""
        if filtro_tipo == "Todos":
            return True
            
        texto_original = valores[1] if len(valores) > 1 else ""
        
        if filtro_tipo == "Con Placeholders":
            return bool(re.search(r'\{[^}]+\}', texto_original))
        elif filtro_tipo == "Sin Placeholders":
            return not bool(re.search(r'\{[^}]+\}', texto_original))
            
        return True

    def _cumple_busqueda_texto(self, valores, texto_buscar):
        """Verifica si el texto cumple con la búsqueda de texto"""
        if not texto_buscar:
            return True
            
        # Buscar en todas las columnas
        for valor in valores:
            if valor and texto_buscar in str(valor).lower():
                return True
                
        # Búsqueda parcial en palabras
        for valor in valores:
            if valor:
                palabras = str(valor).lower().split()
                for palabra in palabras:
                    if texto_buscar in palabra:
                        return True
        return False

    def crear_nuevo_idioma(self):
        """Crea un nuevo idioma basado en uno existente"""
        if not self.carpeta_mod:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta de mod")
            return
        
        carpeta_languages = self._encontrar_carpeta_languages()
        if not carpeta_languages:
            messagebox.showwarning("Advertencia", "No se encontró la carpeta 'Languages'")
            return
        
        # LISTA DE IDIOMAS DISPONIBLES PARA CREAR
        idiomas_disponibles = [
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
            "Vietnamese (tiếng Việt)",
            "English (English)"
        ]
        
        dialogo = ctk.CTkToplevel(self.ventana)
        dialogo.title("Crear Nuevo Idioma")
        dialogo.geometry("500x350")
        dialogo.transient(self.ventana)
        dialogo.grab_set()
        
        # Centrar el diálogo
        dialogo.update_idletasks()
        x = (self.ventana.winfo_x() + (self.ventana.winfo_width() // 2)) - (500 // 2)
        y = (self.ventana.winfo_y() + (self.ventana.winfo_height() // 2)) - (350 // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        # Frame principal con padding
        frame_principal = ctk.CTkFrame(dialogo)
        frame_principal.pack(fill='both', expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame_principal, text="Crear Nuevo Idioma", 
                    font=('Segoe UI', 14, 'bold')).pack(pady=(0, 20))
        
        # Selección de idioma a crear (LISTA DESPLEGABLE)
        ctk.CTkLabel(frame_principal, text="Selecciona el idioma a crear:", 
                    font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        combo_idiomas_crear = ctk.CTkComboBox(frame_principal, values=idiomas_disponibles, 
                                         state="readonly", font=('Segoe UI', 10), width=300)
        combo_idiomas_crear.pack(fill='x', pady=(0, 15))
        combo_idiomas_crear.set("Spanish")  # Valor por defecto
        
        # Selección de idioma base para copiar
        ctk.CTkLabel(frame_principal, text="Copiar estructura del idioma existente:", 
                    font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        idiomas_base = self._obtener_idiomas_base(carpeta_languages)
        combo_base = ctk.CTkComboBox(frame_principal, values=idiomas_base, state="readonly", 
                                font=('Segoe UI', 10), width=300)
        combo_base.pack(fill='x', pady=(0, 20))
        if idiomas_base:
            combo_base.set(idiomas_base[0])
        
        def crear_idioma():
            nombre_nuevo = combo_idiomas_crear.get().strip()
            idioma_base = combo_base.get()
            
            if not nombre_nuevo:
                messagebox.showwarning("Advertencia", "Selecciona un idioma para crear")
                return
            
            if not idioma_base:
                messagebox.showwarning("Advertencia", "Selecciona un idioma base")
                return
            
            dialogo.destroy()
            threading.Thread(target=self._crear_idioma_completo, 
                           args=(carpeta_languages, nombre_nuevo, idioma_base), 
                           daemon=True).start()
        
        # Botones
        frame_botones = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_botones.pack(fill='x', pady=20)
        
        btn_crear = ctk.CTkButton(frame_botones, text="CREAR IDIOMA", 
                            command=crear_idioma, width=150,
                            fg_color='#4caf50', hover_color='#45a049')
        btn_crear.pack(side='left', padx=(0, 10))
        
        btn_cancelar = ctk.CTkButton(frame_botones, text="CANCELAR", 
                               command=dialogo.destroy, width=150,
                               fg_color='#f44336', hover_color='#d32f2f')
        btn_cancelar.pack(side='left')

    def _obtener_idiomas_base(self, carpeta_languages):
        """Obtiene idiomas existentes"""
        idiomas = []
        try:
            for item in os.listdir(carpeta_languages):
                ruta_item = os.path.join(carpeta_languages, item)
                if os.path.isdir(ruta_item) and self._tiene_archivos_xml(ruta_item):
                    idiomas.append(item)
        except:
            pass
        return idiomas

    def _crear_idioma_completo(self, carpeta_languages, nombre_idioma, idioma_base):
        """Crea un nuevo idioma copiando la estructura completa"""
        try:
            ruta_nuevo = os.path.join(carpeta_languages, nombre_idioma)
            ruta_base = os.path.join(carpeta_languages, idioma_base)
            
            if os.path.exists(ruta_nuevo):
                self.ventana.after(0, lambda: messagebox.showerror("Error", f"El idioma '{nombre_idioma}' ya existe"))
                return
            
            os.makedirs(ruta_nuevo, exist_ok=True)
            
            # Copiar estructura recursivamente
            archivos_copiados = 0
            for root, dirs, files in os.walk(ruta_base):
                # Calcular ruta relativa para crear estructura paralela
                ruta_relativa = os.path.relpath(root, ruta_base)
                ruta_destino = os.path.join(ruta_nuevo, ruta_relativa)
                
                # Crear carpetas
                if not os.path.exists(ruta_destino):
                    os.makedirs(ruta_destino, exist_ok=True)
                
                # Copiar archivos XML
                for file in files:
                    if file.lower().endswith('.xml'):
                        archivo_origen = os.path.join(root, file)
                        archivo_destino = os.path.join(ruta_destino, file)
                        shutil.copy2(archivo_origen, archivo_destino)
                        archivos_copiados += 1
            
            self.ventana.after(0, lambda: messagebox.showinfo(
                "Éxito", 
                f"Idioma '{nombre_idioma}' creado exitosamente!\n\n"
                f"• Copiado de: {idioma_base}\n"
                f"• Archivos copiados: {archivos_copiados}"
            ))
            
            # Recargar idiomas
            self.recargar_idiomas()
            
        except Exception as e:
            self.ventana.after(0, lambda: messagebox.showerror("Error", f"No se pudo crear: {str(e)}"))

    def editar_defs(self):
        """Abre el editor para modificar Defs.xml con interfaz mejorada"""
        if not self.carpeta_mod:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta de mod")
            return
        
        carpeta_defs = os.path.join(self.carpeta_mod, "Defs")
        if not os.path.exists(carpeta_defs):
            messagebox.showwarning("Advertencia", "No se encontró la carpeta 'Defs'")
            return
        
        archivos_defs = []
        for root, dirs, files in os.walk(carpeta_defs):
            for file in files:
                if file.lower().endswith('.xml'):
                    ruta_completa = os.path.join(root, file)
                    ruta_relativa = os.path.relpath(ruta_completa, carpeta_defs)
                    archivos_defs.append({
                        'ruta_completa': ruta_completa,
                        'ruta_relativa': ruta_relativa,
                        'nombre_archivo': file,
                        'carpeta': os.path.dirname(ruta_relativa)
                    })
        
        if not archivos_defs:
            messagebox.showwarning("Advertencia", "No se encontraron archivos XML en la carpeta Defs")
            return
        
        self._mostrar_selector_defs_mejorado(archivos_defs)

    def _mostrar_selector_defs_mejorado(self, archivos_defs):
        """Muestra un selector de Defs moderno con CTkScrollableFrame"""
        dialogo = ctk.CTkToplevel(self.ventana)
        dialogo.title("Seleccionar Archivo Defs")
        
        # Configurar tamaño seguro
        ancho_pantalla = self.ventana.winfo_screenwidth()
        alto_pantalla = self.ventana.winfo_screenheight()
        ancho_dialogo = int(ancho_pantalla * 0.7)
        alto_dialogo = int(alto_pantalla * 0.8)
        x = (ancho_pantalla - ancho_dialogo) // 2
        y = (alto_pantalla - alto_dialogo) // 2
        dialogo.geometry(f"{ancho_dialogo}x{alto_dialogo}+{x}+{y}")
        
        dialogo.transient(self.ventana)
        dialogo.grab_set()
        
        # Frame principal
        frame_principal = ctk.CTkFrame(dialogo)
        frame_principal.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(frame_principal, text="Selecciona un archivo Defs para editar:", 
                    font=('Segoe UI', 16, 'bold')).pack(pady=(0, 20))
        
        # Búsqueda
        frame_busqueda = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_busqueda.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(frame_busqueda, text="Buscar:", 
                    font=('Segoe UI', 12, 'bold')).pack(side='left')
        
        entry_busqueda = ctk.CTkEntry(frame_busqueda,
                                    font=('Segoe UI', 11),
                                    width=300,
                                    placeholder_text="Buscar por nombre de archivo...")
        entry_busqueda.pack(side='left', padx=10)
        entry_busqueda.focus_set()
        
        # Contador
        label_contador = ctk.CTkLabel(frame_busqueda, text=f"Archivos: {len(archivos_defs)}",
                                    font=('Segoe UI', 10))
        label_contador.pack(side='right')
        
        # Área de lista con CTkScrollableFrame
        frame_lista = ctk.CTkFrame(frame_principal)
        frame_lista.pack(fill='both', expand=True, pady=(0, 15))
        
        # Usar CTkScrollableFrame nativo
        scrollable_frame = ctk.CTkScrollableFrame(
            frame_lista, 
            fg_color=self.colores['fondo_secundario']
        )
        scrollable_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Organizar archivos por carpeta
        archivos_por_carpeta = {}
        for archivo in archivos_defs:
            carpeta = archivo['carpeta'] if archivo['carpeta'] != '.' else 'Raíz'
            if carpeta not in archivos_por_carpeta:
                archivos_por_carpeta[carpeta] = []
            archivos_por_carpeta[carpeta].append(archivo)
        
        # Variables para selección
        self.archivo_seleccionado_defs = None
        tarjetas_archivos = []
        
        def crear_tarjeta_archivo(parent, archivo, es_carpeta=False):
            """Crea una tarjeta visual para archivo o carpeta"""
            if es_carpeta:
                # Tarjeta de carpeta
                frame = ctk.CTkFrame(parent, 
                                   fg_color=self.colores['fondo_terciario'],
                                   corner_radius=8,
                                   border_width=1,
                                   border_color=self.colores['borde'])
                frame.pack(fill='x', pady=(0, 5))
                
                # Contenido de carpeta
                ctk.CTkLabel(frame, text="📁", 
                           font=('Segoe UI', 14)).pack(side='left', padx=10)
                
                ctk.CTkLabel(frame, text=archivo, 
                           font=('Segoe UI', 12, 'bold')).pack(side='left', padx=5)
                
                return frame
            else:
                # Tarjeta de archivo
                frame = ctk.CTkFrame(parent, 
                                   fg_color=self.colores['fondo_terciario'],
                                   corner_radius=8,
                                   border_width=1,
                                   border_color=self.colores['borde'])
                frame.pack(fill='x', pady=2, padx=5)
                
                # Variable para estado de selección
                seleccionado = False
                
                def on_enter(e):
                    if not seleccionado:
                        frame.configure(fg_color=self.colores['hover'])
                
                def on_leave(e):
                    if not seleccionado:
                        frame.configure(fg_color=self.colores['fondo_terciario'])
                
                def on_click(e):
                    nonlocal seleccionado
                    # Deseleccionar todos
                    for tarjeta in tarjetas_archivos:
                        if tarjeta['frame'] != frame:
                            tarjeta['frame'].configure(fg_color=self.colores['fondo_terciario'])
                            tarjeta['seleccionado'] = False
                    
                    # Seleccionar actual
                    seleccionado = True
                    frame.configure(fg_color=self.colores['seleccion'])
                    self.archivo_seleccionado_defs = archivo
                
                frame.bind("<Enter>", on_enter)
                frame.bind("<Leave>", on_leave)
                frame.bind("<Button-1>", on_click)
                
                # Contenido del archivo
                frame_contenido = ctk.CTkFrame(frame, fg_color="transparent")
                frame_contenido.pack(fill='x', padx=15, pady=10)
                
                # Icono y nombre
                ctk.CTkLabel(frame_contenido, text="📄", 
                           font=('Segoe UI', 12)).grid(row=0, column=0, rowspan=2, padx=(0, 10))
                
                # Nombre del archivo
                ctk.CTkLabel(frame_contenido, text=archivo['nombre_archivo'], 
                           font=('Segoe UI', 11, 'bold')).grid(row=0, column=1, sticky='w')
                
                # Ruta
                ctk.CTkLabel(frame_contenido, text=archivo['ruta_relativa'], 
                           font=('Segoe UI', 9),
                           text_color=self.colores['texto_secundario']).grid(row=1, column=1, sticky='w')
                
                tarjeta_info = {
                    'frame': frame,
                    'archivo': archivo,
                    'seleccionado': seleccionado
                }
                tarjetas_archivos.append(tarjeta_info)
                
                return frame
        
        # Llenar la lista
        for carpeta, archivos in sorted(archivos_por_carpeta.items()):
            # Agregar carpeta
            crear_tarjeta_archivo(scrollable_frame, carpeta, es_carpeta=True)
            
            # Agregar archivos de la carpeta
            for archivo in sorted(archivos, key=lambda x: x['nombre_archivo']):
                crear_tarjeta_archivo(scrollable_frame, archivo, es_carpeta=False)
        
        # Función de filtrado
        def filtrar_archivos(event=None):
            texto = entry_busqueda.get().lower().strip()
            archivos_visibles = 0
            
            for tarjeta in tarjetas_archivos:
                archivo = tarjeta['archivo']
                nombre = archivo['nombre_archivo'].lower()
                ruta = archivo['ruta_relativa'].lower()
                
                if texto in nombre or texto in ruta:
                    tarjeta['frame'].pack(fill='x', pady=2, padx=5)
                    archivos_visibles += 1
                else:
                    tarjeta['frame'].pack_forget()
            
            label_contador.configure(text=f"Archivos: {archivos_visibles}/{len(archivos_defs)}")
        
        entry_busqueda.bind('<KeyRelease>', filtrar_archivos)
        
        # Botones
        frame_botones = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_botones.pack(fill='x', pady=10)
        
        def abrir_editor():
            if self.archivo_seleccionado_defs:
                dialogo.destroy()
                self._abrir_editor_defs_mejorado(self.archivo_seleccionado_defs)
            else:
                messagebox.showwarning("Advertencia", "Selecciona un archivo")
        
        btn_abrir = ctk.CTkButton(frame_botones, text="ABRIR EDITOR", 
                            command=abrir_editor, width=150,
                            fg_color='#4caf50', hover_color='#45a049')
        btn_abrir.pack(side='left', padx=(0, 10))
        
        btn_cancelar = ctk.CTkButton(frame_botones, text="CANCELAR", 
                               command=dialogo.destroy, width=150,
                               fg_color='#f44336', hover_color='#d32f2f')
        btn_cancelar.pack(side='left')

    def _abrir_editor_defs_mejorado(self, archivo_info):
        """Abre el editor mejorado para Defs.xml con scroll nativo"""
        try:
            tree = ET.parse(archivo_info['ruta_completa'])
            root = tree.getroot()
            
            thingdefs = root.findall('.//ThingDef')
            statdefs = root.findall('.//StatDef')
            
            if not thingdefs and not statdefs:
                messagebox.showinfo("Información", "No se encontraron ThingDefs ni StatDefs en este archivo")
                return
            
            thingdefs_con_nombre = []
            for thingdef in thingdefs:
                defname_elem = thingdef.find('defName')
                if defname_elem is not None and defname_elem.text and defname_elem.text.strip():
                    thingdefs_con_nombre.append({
                        'element': thingdef,
                        'defName': defname_elem.text.strip(),
                        'tipo': 'ThingDef'
                    })
            
            statdefs_con_nombre = []
            for statdef in statdefs:
                defname_elem = statdef.find('defName')
                if defname_elem is not None and defname_elem.text and defname_elem.text.strip():
                    statdefs_con_nombre.append({
                        'element': statdef,
                        'defName': defname_elem.text.strip(),
                        'tipo': 'StatDef'
                    })
            
            todos_los_defs = thingdefs_con_nombre + statdefs_con_nombre
            
            if not todos_los_defs:
                messagebox.showinfo("Información", "No se encontraron Defs con nombres válidos")
                return
            
            dialogo = ctk.CTkToplevel(self.ventana)
            dialogo.title(f"Editor de Defs - {archivo_info['ruta_relativa']}")
            
            # Configurar tamaño seguro
            ancho_pantalla = self.ventana.winfo_screenwidth()
            alto_pantalla = self.ventana.winfo_screenheight()
            ancho_dialogo = int(ancho_pantalla * 0.85)
            alto_dialogo = int(alto_pantalla * 0.85)
            x = (ancho_pantalla - ancho_dialogo) // 2
            y = (alto_pantalla - alto_dialogo) // 2
            dialogo.geometry(f"{ancho_dialogo}x{alto_dialogo}+{x}+{y}")
            
            dialogo.transient(self.ventana)
            dialogo.grab_set()
            
            # Frame principal
            frame_principal = ctk.CTkFrame(dialogo)
            frame_principal.pack(fill='both', expand=True, padx=15, pady=15)
            
            # Dividir en dos partes
            frame_superior = ctk.CTkFrame(frame_principal, fg_color="transparent")
            frame_superior.pack(fill='x', pady=(0, 10))
            
            frame_inferior = ctk.CTkFrame(frame_principal)
            frame_inferior.pack(fill='both', expand=True)
            
            # Título y controles
            ctk.CTkLabel(frame_superior, text=f"Editando: {archivo_info['ruta_relativa']}", 
                        font=('Segoe UI', 14, 'bold')).pack(anchor='w')
            
            frame_botones_superior = ctk.CTkFrame(frame_superior, fg_color="transparent")
            frame_botones_superior.pack(fill='x', pady=10)
            
            def abrir_selector_defs():
                dialogo.destroy()
                self.editar_defs()
            
            btn_otro_def = ctk.CTkButton(frame_botones_superior, text="ELEGIR OTRO DEF", 
                                   command=abrir_selector_defs, width=180,
                                   fg_color='#3498db', hover_color='#2980b9')
            btn_otro_def.pack(side='left', padx=5)
            
            btn_guardar_todos = ctk.CTkButton(frame_botones_superior, text="GUARDAR TODOS", 
                                       command=lambda: self._guardar_todos_los_defs(tree, archivo_info), 
                                       width=150,
                                       fg_color='#4caf50', hover_color='#45a049')
            btn_guardar_todos.pack(side='left', padx=5)
            
            btn_cerrar = ctk.CTkButton(frame_botones_superior, text="CERRAR EDITOR", 
                                 command=dialogo.destroy, width=150,
                                 fg_color='#f44336', hover_color='#d32f2f')
            btn_cerrar.pack(side='left', padx=5)
            
            # Lista de Defs a la izquierda con CTkScrollableFrame
            frame_lista = ctk.CTkFrame(frame_inferior, width=300)
            frame_lista.pack(side='left', fill='y', padx=(0, 10))
            frame_lista.pack_propagate(False)
            
            ctk.CTkLabel(frame_lista, text="Defs:", 
                        font=('Segoe UI', 12, 'bold')).pack(pady=(10, 5))
            
            # Usar CTkScrollableFrame nativo
            scrollable_lista = ctk.CTkScrollableFrame(frame_lista)
            scrollable_lista.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Área de edición a la derecha con CTkScrollableFrame
            frame_edicion = ctk.CTkFrame(frame_inferior)
            frame_edicion.pack(side='right', fill='both', expand=True)
            
            # Usar CTkScrollableFrame nativo para el área de edición
            scrollable_edicion = ctk.CTkScrollableFrame(frame_edicion)
            scrollable_edicion.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Llenar lista con Defs
            def_data = {}
            tarjetas_defs = []
            
            for def_info in todos_los_defs:
                nombre = f"{def_info['defName']} ({def_info['tipo']})"
                
                # Crear tarjeta para cada Def
                frame_tarjeta = ctk.CTkFrame(scrollable_lista,
                                           fg_color=self.colores['fondo_terciario'],
                                           corner_radius=6,
                                           border_width=1,
                                           border_color=self.colores['borde'])
                frame_tarjeta.pack(fill='x', pady=2, padx=2)
                
                seleccionado = False
                
                def crear_callback(def_nombre, frame):
                    def callback(e):
                        nonlocal seleccionado
                        # Deseleccionar todos
                        for tarjeta in tarjetas_defs:
                            if tarjeta['frame'] != frame:
                                tarjeta['frame'].configure(fg_color=self.colores['fondo_terciario'])
                                tarjeta['seleccionado'] = False
                        
                        # Seleccionar actual
                        seleccionado = True
                        frame.configure(fg_color=self.colores['seleccion'])
                        
                        # Mostrar Def en área de edición
                        self._mostrar_def_para_edicion_mejorado(def_nombre, scrollable_edicion, def_data)
                    
                    return callback
                
                frame_tarjeta.bind("<Button-1>", crear_callback(nombre, frame_tarjeta))
                
                # Contenido de la tarjeta
                ctk.CTkLabel(frame_tarjeta, text="⚙️", 
                           font=('Segoe UI', 12)).pack(side='left', padx=10, pady=5)
                
                ctk.CTkLabel(frame_tarjeta, text=def_info['defName'], 
                           font=('Segoe UI', 10, 'bold'),
                           wraplength=200).pack(side='left', padx=5, pady=5)
                
                ctk.CTkLabel(frame_tarjeta, text=def_info['tipo'], 
                           font=('Segoe UI', 8),
                           text_color=self.colores['texto_secundario']).pack(side='right', padx=10, pady=5)
                
                tarjeta_info = {
                    'frame': frame_tarjeta,
                    'def_info': def_info,
                    'seleccionado': seleccionado
                }
                tarjetas_defs.append(tarjeta_info)
                
                def_data[nombre] = {
                    'element': def_info['element'],
                    'widgets': {},
                    'tree': tree,
                    'valores_actuales': {},
                    'archivo_ruta': archivo_info['ruta_completa'],
                    'tipo': def_info['tipo']
                }
            
            # Mostrar el primer Def por defecto
            if todos_los_defs:
                primera_tarjeta = tarjetas_defs[0]
                primera_tarjeta['frame'].configure(fg_color=self.colores['seleccion'])
                primera_tarjeta['seleccionado'] = True
                primer_nombre = f"{todos_los_defs[0]['defName']} ({todos_los_defs[0]['tipo']})"
                self._mostrar_def_para_edicion_mejorado(primer_nombre, scrollable_edicion, def_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo Defs: {str(e)}")

    def _mostrar_def_para_edicion_mejorado(self, nombre_def, scrollable_frame, def_data):
        """Muestra la interfaz para editar un Def específico usando CTkScrollableFrame"""
        try:
            # Limpiar área de edición de forma segura
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            data = def_data[nombre_def]
            elemento_def = data['element']
            tipo_def = data['tipo']
            
            # Título
            frame_titulo = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            frame_titulo.pack(fill='x', pady=(0, 20))
            
            ctk.CTkLabel(frame_titulo, text=f"Editando: {nombre_def}", 
                        font=('Segoe UI', 16, 'bold')).pack(side='left')
            
            btn_guardar_individual = ctk.CTkButton(frame_titulo, text="GUARDAR ESTE", 
                                             command=lambda: self._guardar_def_individual(nombre_def, def_data), 
                                             width=120,
                                             fg_color='#4caf50', hover_color='#45a049')
            btn_guardar_individual.pack(side='right', padx=10)
            
            # Inicializar widgets
            data['widgets'] = {}
            
            # Campos editables según el tipo de Def
            if tipo_def == 'ThingDef':
                campos_def = [
                    ('label', 'Label (Nombre)', 'text'),
                    ('description', 'Description (Descripción)', 'text'),
                    ('graphicData/texPath', 'Texture Path', 'icon'),
                    ('uiIconPath', 'UI Icon Path', 'icon')
                ]
            elif tipo_def == 'StatDef':
                campos_def = [
                    ('label', 'Label (Nombre)', 'text'),
                    ('description', 'Description (Descripción)', 'text')
                ]
            else:
                campos_def = [
                    ('label', 'Label (Nombre)', 'text'),
                    ('description', 'Description (Descripción)', 'text')
                ]
            
            for campo, etiqueta, tipo in campos_def:
                frame_campo = ctk.CTkFrame(scrollable_frame, corner_radius=8)
                frame_campo.pack(fill='x', pady=(0, 15), padx=5)
                
                # Buscar el elemento
                if '/' in campo:
                    partes = campo.split('/')
                    elemento_actual = elemento_def
                    for parte in partes:
                        elemento_actual = elemento_actual.find(parte)
                        if elemento_actual is None:
                            break
                    elemento = elemento_actual
                else:
                    elemento = elemento_def.find(campo)
                
                valor_actual = elemento.text if elemento is not None and elemento.text else ""
                data['valores_actuales'][campo] = valor_actual
                
                if tipo == 'text':
                    ctk.CTkLabel(frame_campo, text=etiqueta, 
                               font=('Segoe UI', 12, 'bold')).pack(anchor='w', padx=15, pady=(10, 5))
                    
                    if campo in ['label', 'description']:
                        text_widget = ctk.CTkTextbox(frame_campo, 
                                                   font=('Segoe UI', 10),
                                                   height=100)
                        text_widget.pack(fill='x', padx=15, pady=(0, 10))
                        text_widget.insert('1.0', valor_actual)
                        
                        frame_botones_campo = ctk.CTkFrame(frame_campo, fg_color="transparent")
                        frame_botones_campo.pack(fill='x', padx=15, pady=(0, 10))
                        
                        btn_traducir = ctk.CTkButton(frame_botones_campo, text="Traducir", 
                                           command=lambda tw=text_widget: self._traducir_campo_defs(tw),
                                           width=120,
                                           fg_color='#9b59b6', hover_color='#8e44ad')
                        btn_traducir.pack(side='left')
                        
                        data['widgets'][campo] = {
                            'type': 'text',
                            'widget': text_widget,
                            'element': elemento
                        }
                    else:
                        entry = ctk.CTkEntry(frame_campo, font=('Segoe UI', 10))
                        entry.insert(0, valor_actual)
                        entry.pack(fill='x', padx=15, pady=(0, 10))
                        
                        data['widgets'][campo] = {
                            'type': 'entry', 
                            'widget': entry,
                            'element': elemento
                        }
                
                elif tipo == 'icon':
                    ctk.CTkLabel(frame_campo, text=etiqueta, 
                               font=('Segoe UI', 12, 'bold')).pack(anchor='w', padx=15, pady=(10, 5))
                    
                    frame_icono = ctk.CTkFrame(frame_campo, fg_color="transparent")
                    frame_icono.pack(fill='x', padx=15, pady=(0, 10))
                    
                    entry_icono = ctk.CTkEntry(frame_icono, font=('Segoe UI', 10))
                    entry_icono.insert(0, valor_actual)
                    entry_icono.pack(side='left', fill='x', expand=True, padx=(0, 10))
                    
                    btn_buscar_icono = ctk.CTkButton(frame_icono, text="Buscar", 
                                           command=lambda e=entry_icono, n=nombre_def, c=campo, d=data: self._buscar_icono_defs(e, n, c, d),
                                           width=100,
                                           fg_color='#4caf50', hover_color='#45a049')
                    btn_buscar_icono.pack(side='left', padx=(0, 5))
                    
                    btn_limpiar = ctk.CTkButton(frame_icono, text="Limpiar", 
                                      command=lambda e=entry_icono, n=nombre_def, c=campo, d=data: self._limpiar_icono_defs(e, n, c, d),
                                      width=80,
                                      fg_color='#f44336', hover_color='#d32f2f')
                    btn_limpiar.pack(side='left')
                    
                    # Preview del icono
                    frame_preview = ctk.CTkFrame(frame_campo, width=100, height=100, corner_radius=8)
                    frame_preview.pack(pady=(0, 10), padx=15)
                    frame_preview.pack_propagate(False)
                    
                    label_preview = ctk.CTkLabel(frame_preview, text="Preview", 
                                               font=('Segoe UI', 8), 
                                               justify='center')
                    label_preview.pack(expand=True, fill='both', padx=5, pady=5)
                    
                    # Actualizar preview inicial
                    self._actualizar_preview_icono_defs_mejorado(valor_actual, label_preview)
                    
                    data['widgets'][campo] = {
                        'type': 'icon',
                        'widget': entry_icono,
                        'preview': label_preview,
                        'element': elemento
                    }
                    
                    # Bind para actualizar preview
                    entry_icono.bind('<KeyRelease>', 
                                   lambda e, n=nombre_def, c=campo, d=data: self._actualizar_preview_desde_entry_mejorado(n, c, d))
                    
        except Exception as e:
            print(f"Error mostrando Def {nombre_def}: {e}")

    def _actualizar_preview_icono_defs_mejorado(self, ruta_icono, label_preview):
        """Actualiza el preview de un icono con búsqueda mejorada"""
        # Limpiar el label primero
        label_preview.configure(image='', text='Preview')
        
        if not ruta_icono or not self.carpeta_mod:
            label_preview.configure(text="No icon")
            return
        
        # Búsqueda mejorada de la imagen
        ruta_encontrada = self._buscar_imagen_mejorado(ruta_icono)
        
        # Mostrar resultado
        if ruta_encontrada:
            self._mostrar_imagen_preview_ctk(ruta_encontrada, label_preview, 90)
        else:
            # Mostrar información de búsqueda
            nombre_archivo = os.path.basename(ruta_icono)
            if not nombre_archivo.lower().endswith('.png'):
                nombre_archivo += '.png'
            label_preview.configure(
                text=f"No encontrado\n{nombre_archivo}"
            )

    def _actualizar_preview_desde_entry_mejorado(self, nombre_def, campo, def_data):
        """Actualiza el preview cuando cambia el texto del entry con búsqueda mejorada"""
        data = def_data['widgets'][campo]
        ruta_icono = data['widget'].get()
        self._actualizar_preview_icono_defs_mejorado(ruta_icono, data['preview'])

    def _buscar_imagen_mejorado(self, ruta_icono):
        """Búsqueda mejorada de imágenes con cache"""
        if not self.carpeta_mod or not ruta_icono:
            return None
        
        # Usar cache para búsquedas frecuentes
        cache_key = f"{self.carpeta_mod}:{ruta_icono}"
        if cache_key in self._cache_busqueda_imagenes:
            return self._cache_busqueda_imagenes[cache_key]
        
        nombre_archivo = os.path.basename(ruta_icono)
        if not nombre_archivo.lower().endswith('.png'):
            nombre_archivo += '.png'
        
        # Estrategias de búsqueda mejoradas
        estrategias = [
            # 1. Ruta exacta desde carpeta mod
            lambda: os.path.join(self.carpeta_mod, ruta_icono),
            
            # 2. En Textures/ con la ruta completa
            lambda: os.path.join(self.carpeta_mod, "Textures", ruta_icono),
            
            # 3. En Textures/ solo con el nombre del archivo
            lambda: os.path.join(self.carpeta_mod, "Textures", nombre_archivo),
            
            # 4. Búsqueda recursiva en Textures/
            lambda: self._buscar_en_textures_recursivo(nombre_archivo),
            
            # 5. Búsqueda recursiva en todo el mod (excluyendo algunas carpetas)
            lambda: self._buscar_archivo_recursivo_png(nombre_archivo),
            
            # 6. Intentar con diferentes estructuras comunes
            lambda: os.path.join(self.carpeta_mod, "Textures", "Things", nombre_archivo),
            lambda: os.path.join(self.carpeta_mod, "Textures", "Buildings", nombre_archivo),
            lambda: os.path.join(self.carpeta_mod, "Textures", "Items", nombre_archivo),
            lambda: os.path.join(self.carpeta_mod, "Textures", "UI", nombre_archivo),
            lambda: os.path.join(self.carpeta_mod, "Textures", "Icons", nombre_archivo),
            
            # 7. Buscar en la ruta relativa desde Textures
            lambda: os.path.join(self.carpeta_mod, "Textures", os.path.basename(ruta_icono)),
        ]
        
        for estrategia in estrategias:
            try:
                ruta = estrategia()
                if ruta and os.path.exists(ruta):
                    # Guardar en cache
                    self._cache_busqueda_imagenes[cache_key] = ruta
                    return ruta
            except:
                continue
        
        return None

    def _buscar_en_textures_recursivo(self, nombre_archivo):
        """Búsqueda recursiva específica en Textures/"""
        carpeta_textures = os.path.join(self.carpeta_mod, "Textures")
        if not os.path.exists(carpeta_textures):
            return None
        
        for root, dirs, files in os.walk(carpeta_textures):
            for file in files:
                if file.lower() == nombre_archivo.lower():
                    return os.path.join(root, file)
        return None

    def _buscar_archivo_recursivo_png(self, nombre_archivo):
        """Busca un archivo PNG recursivamente en todo el mod"""
        if not self.carpeta_mod:
            return None
        
        # Buscar en todo el directorio del mod
        for root, dirs, files in os.walk(self.carpeta_mod):
            # Excluir algunas carpetas que no suelen tener texturas
            dirs[:] = [d for d in dirs if d not in ['Languages', 'Defs', 'About', 'Source', 'Assemblies']]
            
            for file in files:
                if file.lower() == nombre_archivo.lower():
                    return os.path.join(root, file)
        
        return None

    def _mostrar_imagen_preview_ctk(self, ruta_imagen, label_preview, max_size=250):
        """Muestra imagen en el preview usando CTkImage (MEJORADO)"""
        # Limpiar primero
        label_preview.configure(image='', text='Cargando...')
        
        if not os.path.exists(ruta_imagen):
            label_preview.configure(text="No encontrada")
            return
        
        if not PIL_AVAILABLE:
            nombre = os.path.basename(ruta_imagen)
            label_preview.configure(text=f"{nombre}")
            return
        
        try:
            with Image.open(ruta_imagen) as img:
                # Convertir si es necesario
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGBA')
                else:
                    img = img.convert('RGB')
                
                # Redimensionar manteniendo proporción
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Crear CTkImage
                ctk_image = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=img.size
                )
                
                # Configurar la imagen en el label
                label_preview.configure(image=ctk_image, text='')
                
                # Guardar referencia para evitar garbage collection
                if not hasattr(label_preview, '_ctk_image'):
                    label_preview._ctk_image = None
                
                # Liberar imagen anterior
                if label_preview._ctk_image:
                    try:
                        del label_preview._ctk_image
                    except:
                        pass
                
                label_preview._ctk_image = ctk_image
                
        except Exception as e:
            print(f"Error cargando preview {ruta_imagen}: {e}")
            nombre = os.path.basename(ruta_imagen)
            label_preview.configure(text=f"Error")

    def _guardar_def_individual(self, nombre_def, def_data):
        """Guarda un Def individual con validación"""
        try:
            if nombre_def not in def_data:
                messagebox.showerror("Error", f"Datos no encontrados para '{nombre_def}'")
                return
                
            data = def_data[nombre_def]
            
            if self._aplicar_cambios_def(nombre_def, data):
                # Guardar el archivo
                data['tree'].write(data['archivo_ruta'], encoding='utf-8', xml_declaration=True)
                
                # Actualizar valores actuales después de guardar
                for campo, widget_data in data.get('widgets', {}).items():
                    if widget_data['type'] == 'text':
                        nuevo_valor = widget_data['widget'].get('1.0', 'end-1c').strip()
                    else:
                        nuevo_valor = widget_data['widget'].get().strip()
                    data['valores_actuales'][campo] = nuevo_valor
                    
                messagebox.showinfo("Éxito", f"Def '{nombre_def}' guardado correctamente")
            else:
                messagebox.showinfo("Información", f"No hay cambios en '{nombre_def}' para guardar")
                
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar '{nombre_def}': {str(e)}")

    def _aplicar_cambios_def(self, nombre_def, def_data):
        """Aplica los cambios de forma segura con validación de widgets"""
        try:
            cambios_aplicados = False
            
            for campo, data in def_data.get('widgets', {}).items():
                try:
                    elemento = data['element']
                    
                    if data['type'] == 'text':
                        nuevo_valor = data['widget'].get('1.0', 'end-1c').strip()
                    else:
                        nuevo_valor = data['widget'].get().strip()
                    
                    # Solo aplicar cambios si el valor es diferente
                    valor_anterior = def_data['valores_actuales'].get(campo, '')
                    if nuevo_valor != valor_anterior:
                        if nuevo_valor:
                            if elemento is None:
                                # Crear elemento si no existe
                                if '/' in campo:
                                    partes = campo.split('/')
                                    elemento_padre = def_data['element']
                                    for parte in partes[:-1]:
                                        sub_elemento = elemento_padre.find(parte)
                                        if sub_elemento is None:
                                            sub_elemento = ET.SubElement(elemento_padre, parte)
                                        elemento_padre = sub_elemento
                                    elemento = ET.SubElement(elemento_padre, partes[-1])
                                else:
                                    elemento = ET.SubElement(def_data['element'], campo)
                            elemento.text = nuevo_valor
                            cambios_aplicados = True
                        elif elemento is not None:
                            # Eliminar elemento si está vacío
                            padre = elemento.getparent()
                            if padre is not None:
                                padre.remove(elemento)
                                cambios_aplicados = True
                            
                except Exception as e:
                    print(f"Error procesando campo {campo}: {e}")
                    continue
                    
            return cambios_aplicados
            
        except Exception as e:
            print(f"Error aplicando cambios para {nombre_def}: {e}")
            return False

    def _traducir_campo_defs(self, text_widget):
        """Traduce el contenido de un campo de texto"""
        texto_actual = text_widget.get('1.0', 'end-1c')
        if not texto_actual.strip():
            messagebox.showwarning("Advertencia", "No hay texto para traducir")
            return
        
        try:
            texto_traducido = GoogleTranslator(source='auto', target='es').translate(texto_actual)
            if texto_traducido:
                text_widget.delete('1.0', ctk.END)
                text_widget.insert('1.0', texto_traducido)
            else:
                messagebox.showerror("Error", "No se pudo traducir el texto")
        except Exception as e:
            messagebox.showerror("Error", f"Error en traducción: {str(e)}")

    def _buscar_icono_defs(self, entry_widget, nombre_def, campo, def_data):
        """Busca iconos PNG en todo el mod"""
        if not self.carpeta_mod:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta de mod")
            return
        
        # Buscar TODAS las imágenes PNG recursivamente
        archivos_imagen = self._buscar_todas_las_imagenes_png()
        
        if not archivos_imagen:
            messagebox.showinfo("Información", "No se encontraron archivos PNG en el mod")
            return
        
        self._mostrar_dialogo_seleccion_icono_simple(archivos_imagen, entry_widget, nombre_def, campo, def_data)

    def _limpiar_icono_defs(self, entry_widget, nombre_def, campo, def_data):
        """Limpia el icono seleccionado"""
        entry_widget.delete(0, ctk.END)
        data = def_data['widgets'][campo]
        self._actualizar_preview_icono_defs_mejorado("", data['preview'])

    def _buscar_todas_las_imagenes_png(self):
        """Busca TODAS las imágenes PNG en el mod recursivamente"""
        archivos_imagen = []
        
        if not self.carpeta_mod:
            return archivos_imagen
        
        # Buscar en todo el directorio del mod
        try:
            for root, dirs, files in os.walk(self.carpeta_mod):
                # Excluir algunas carpetas que no suelen tener texturas
                dirs[:] = [d for d in dirs if d not in ['Languages', 'Defs', 'About', 'Source', 'Assemblies']]
                
                for file in files:
                    if file.lower().endswith('.png'):
                        ruta_completa = os.path.join(root, file)
                        ruta_relativa = os.path.relpath(ruta_completa, self.carpeta_mod)
                        archivos_imagen.append({
                            'ruta_completa': ruta_completa,
                            'ruta_relativa': ruta_relativa,
                            'nombre_archivo': file,
                            'carpeta_padre': os.path.basename(root)
                        })
        except Exception as e:
            print(f"Error buscando imágenes PNG: {e}")
        
        return archivos_imagen

    def _mostrar_dialogo_seleccion_icono_simple(self, archivos_imagen, entry_widget, nombre_def, campo, def_data):
        """Diálogo de selección simplificado"""
        dialogo_seleccion = ctk.CTkToplevel(self.ventana)
        dialogo_seleccion.title("Seleccionar Textura PNG")
        dialogo_seleccion.geometry("900x650")
        dialogo_seleccion.transient(self.ventana)
        dialogo_seleccion.grab_set()
        
        # Centrar el diálogo
        dialogo_seleccion.update_idletasks()
        x = (self.ventana.winfo_x() + (self.ventana.winfo_width() // 2)) - (900 // 2)
        y = (self.ventana.winfo_y() + (self.ventana.winfo_height() // 2)) - (650 // 2)
        dialogo_seleccion.geometry(f"+{x}+{y}")
        
        frame_principal = ctk.CTkFrame(dialogo_seleccion)
        frame_principal.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(frame_principal, text="Seleccionar Textura PNG", 
                    font=('Segoe UI', 16, 'bold')).pack(pady=(0, 15))
        
        # Búsqueda
        frame_busqueda = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_busqueda.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(frame_busqueda, text="Buscar:", 
                    font=('Segoe UI', 11, 'bold')).pack(side='left')
        
        entry_busqueda = ctk.CTkEntry(frame_busqueda,
                                    font=('Segoe UI', 10),
                                    width=400,
                                    placeholder_text="Buscar por nombre...")
        entry_busqueda.pack(side='left', padx=10)
        entry_busqueda.focus_set()
        
        # Contenido dividido
        frame_contenido = ctk.CTkFrame(frame_principal)
        frame_contenido.pack(fill='both', expand=True)
        
        # Lista a la izquierda
        frame_lista = ctk.CTkFrame(frame_contenido)
        frame_lista.pack(side='left', fill='both', expand=True, padx=(0, 20))
        
        ctk.CTkLabel(frame_lista, text="Archivos PNG encontrados:", 
                    font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        
        frame_lista_scroll = ctk.CTkFrame(frame_lista)
        frame_lista_scroll.pack(fill='both', expand=True, pady=(5, 0))
        
        # Usar tk.Listbox ya que CTk no tiene un widget de lista equivalente
        lista_archivos = tk.Listbox(frame_lista_scroll, bg='#2b2b2b', fg='white', font=('Segoe UI', 10))
        scrollbar_lista = ctk.CTkScrollbar(frame_lista_scroll, command=lista_archivos.yview)
        lista_archivos.configure(yscrollcommand=scrollbar_lista.set)
        
        lista_archivos.pack(side='left', fill='both', expand=True)
        scrollbar_lista.pack(side='right', fill='y')
        
        # Preview a la derecha
        frame_preview = ctk.CTkFrame(frame_contenido, width=350)
        frame_preview.pack(side='right', fill='y')
        frame_preview.pack_propagate(False)
        
        ctk.CTkLabel(frame_preview, text="Vista previa:", 
                    font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        
        frame_marco_preview = ctk.CTkFrame(frame_preview, width=320, height=320)
        frame_marco_preview.pack(pady=(5, 15))
        frame_marco_preview.pack_propagate(False)
        
        label_preview = ctk.CTkLabel(frame_marco_preview, text="Preview", 
                                   font=('Segoe UI', 12), 
                                   justify='center')
        label_preview.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Información de la ruta
        label_ruta = ctk.CTkLabel(frame_preview, text="Ruta: -", 
                                font=('Segoe UI', 9), 
                                justify='left', 
                                wraplength=300)
        label_ruta.pack(fill='x', pady=(0, 10))
        
        # Variables para filtros
        archivos_imagen_completos = archivos_imagen
        texto_busqueda_actual = ""
        
        def actualizar_lista_archivos():
            lista_archivos.delete(0, tk.END)
            
            archivos_filtrados = []
            for archivo in archivos_imagen_completos:
                # Filtrar por texto
                if texto_busqueda_actual:
                    texto_busqueda = texto_busqueda_actual.lower()
                    nombre_archivo = archivo['nombre_archivo'].lower()
                    ruta_relativa = archivo['ruta_relativa'].lower()
                    
                    if (texto_busqueda not in nombre_archivo and 
                        texto_busqueda not in ruta_relativa):
                        continue
                
                archivos_filtrados.append(archivo)
                # Mostrar con ruta para mejor identificación
                display_text = f"{archivo['nombre_archivo']} - {archivo['ruta_relativa']}"
                lista_archivos.insert(tk.END, display_text)
            
            if lista_archivos.size() > 0:
                lista_archivos.selection_set(0)
                lista_archivos.see(0)
                actualizar_preview_seleccion()
            
            # Actualizar contador
            label_contador.configure(text=f"Encontradas: {len(archivos_filtrados)}/{len(archivos_imagen_completos)}")
        
        def actualizar_preview_seleccion(event=None):
            seleccion = lista_archivos.curselection()
            if seleccion:
                indice = seleccion[0]
                archivos_filtrados = []
                
                # Reconstruir lista de archivos filtrados
                for archivo in archivos_imagen_completos:
                    if texto_busqueda_actual:
                        texto_busqueda = texto_busqueda_actual.lower()
                        nombre_archivo = archivo['nombre_archivo'].lower()
                        ruta_relativa = archivo['ruta_relativa'].lower()
                        
                        if (texto_busqueda not in nombre_archivo and 
                            texto_busqueda not in ruta_relativa):
                            continue
                    archivos_filtrados.append(archivo)
                
                if indice < len(archivos_filtrados):
                    archivo_seleccionado = archivos_filtrados[indice]
                    
                    # Actualizar preview
                    self._mostrar_imagen_preview_ctk(archivo_seleccionado['ruta_completa'], label_preview, 300)
                    
                    # Actualizar información de ruta
                    label_ruta.configure(text=f"Ruta: {archivo_seleccionado['ruta_relativa']}")
        
        def filtrar_por_texto(event=None):
            nonlocal texto_busqueda_actual
            texto_busqueda_actual = entry_busqueda.get().lower()
            actualizar_lista_archivos()
        
        # Configurar binds
        entry_busqueda.bind('<KeyRelease>', filtrar_por_texto)
        lista_archivos.bind('<<ListboxSelect>>', actualizar_preview_seleccion)
        
        # Inicializar lista
        actualizar_lista_archivos()
        
        # Contador
        label_contador = ctk.CTkLabel(frame_principal, text=f"Encontradas: {len(archivos_imagen)}",
                                    font=('Segoe UI', 9))
        label_contador.pack(pady=(5, 0))
        
        def seleccionar():
            seleccion = lista_archivos.curselection()
            if seleccion:
                indice = seleccion[0]
                archivos_filtrados = []
                
                # Reconstruir lista de archivos filtrados
                for archivo in archivos_imagen_completos:
                    if texto_busqueda_actual:
                        texto_busqueda = texto_busqueda_actual.lower()
                        nombre_archivo = archivo['nombre_archivo'].lower()
                        ruta_relativa = archivo['ruta_relativa'].lower()
                        
                        if (texto_busqueda not in nombre_archivo and 
                            texto_busqueda not in ruta_relativa):
                            continue
                    archivos_filtrados.append(archivo)
                
                if indice < len(archivos_filtrados):
                    archivo_seleccionado = archivos_filtrados[indice]
                    
                    # Usar la ruta relativa desde la carpeta del mod
                    entry_widget.delete(0, ctk.END)
                    entry_widget.insert(0, archivo_seleccionado['ruta_relativa'])
                    
                    # Actualizar preview en la interfaz principal
                    data = def_data['widgets'][campo]
                    self._actualizar_preview_icono_defs_mejorado(
                        archivo_seleccionado['ruta_relativa'], 
                        data['preview']
                    )
                    
                    dialogo_seleccion.destroy()
                else:
                    messagebox.showwarning("Advertencia", "No se pudo encontrar el archivo seleccionado")
            else:
                messagebox.showwarning("Advertencia", "Selecciona un archivo")
        
        # Botones
        frame_botones = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_botones.pack(fill='x', pady=15)
        
        btn_seleccionar = ctk.CTkButton(frame_botones, text="SELECCIONAR", 
                                  command=seleccionar, width=200,
                                  fg_color='#4caf50', hover_color='#45a049')
        btn_seleccionar.pack(side='left', padx=(0, 10))
        
        btn_cancelar = ctk.CTkButton(frame_botones, text="CANCELAR", 
                               command=dialogo_seleccion.destroy, width=150,
                               fg_color='#f44336', hover_color='#d32f2f')
        btn_cancelar.pack(side='left')

    def _traducir_todos_los_defs(self, dialogo, todos_los_defs, tree, archivo_info):
        """Traduce todos los Defs automáticamente"""
        try:
            total = len(todos_los_defs)
            exitosos = 0
            
            for def_info in todos_los_defs:
                if self._traducir_def_automatico(def_info):
                    exitosos += 1
            
            messagebox.showinfo("Traducción completada", 
                              f"Se tradujeron {exitosos} de {total} Defs")
            
            # Guardar cambios
            tree.write(archivo_info['ruta_completa'], encoding='utf-8', xml_declaration=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en traducción automática: {str(e)}")

    def _traducir_def_automatico(self, def_info):
        """Traduce automáticamente los campos de un Def"""
        try:
            elemento = def_info['element']
            cambios = False
            
            # Campos a traducir para ThingDef
            if def_info['tipo'] == 'ThingDef':
                campos_a_traducir = ['label', 'description']
                for campo in campos_a_traducir:
                    campo_elem = elemento.find(campo)
                    if campo_elem is not None and campo_elem.text and campo_elem.text.strip():
                        texto_original = campo_elem.text.strip()
                        if len(texto_original) > 1:
                            try:
                                texto_traducido = GoogleTranslator(source='auto', target='es').translate(texto_original)
                                if texto_traducido and texto_traducido != texto_original:
                                    campo_elem.text = texto_traducido
                                    cambios = True
                                time.sleep(0.1)  # Rate limiting
                            except:
                                continue
            
            # Campos a traducir para StatDef
            elif def_info['tipo'] == 'StatDef':
                campos_a_traducir = ['label', 'description']
                for campo in campos_a_traducir:
                    campo_elem = elemento.find(campo)
                    if campo_elem is not None and campo_elem.text and campo_elem.text.strip():
                        texto_original = campo_elem.text.strip()
                        if len(texto_original) > 1:
                            try:
                                texto_traducido = GoogleTranslator(source='auto', target='es').translate(texto_original)
                                if texto_traducido and texto_traducido != texto_original:
                                    campo_elem.text = texto_traducido
                                    cambios = True
                                time.sleep(0.1)  # Rate limiting
                            except:
                                continue
            
            return cambios
            
        except Exception as e:
            print(f"Error traduciendo {def_info['defName']}: {e}")
            return False

    def _guardar_todos_los_defs(self, tree, archivo_info):
        """Guarda todos los Defs"""
        try:
            tree.write(archivo_info['ruta_completa'], encoding='utf-8', xml_declaration=True)
            messagebox.showinfo("Éxito", "Todos los Defs guardados correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def editar_about(self):
        """Abre el editor para modificar About.xml con preview de icono"""
        if not self.carpeta_mod:
            messagebox.showwarning("Advertencia", "Primero selecciona una carpeta de mod")
            return
        
        ruta_about = os.path.join(self.carpeta_mod, "About", "About.xml")
        
        if not os.path.exists(ruta_about):
            messagebox.showwarning("Advertencia", "No se encontró el archivo About.xml")
            return
        
        try:
            tree = ET.parse(ruta_about)
            root = tree.getroot()
            
            dialogo = ctk.CTkToplevel(self.ventana)
            dialogo.title("Editor de About.xml")
            
            # Configurar tamaño y posición
            ancho_pantalla = self.ventana.winfo_screenwidth()
            alto_pantalla = self.ventana.winfo_screenheight()
            ancho_dialogo = int(ancho_pantalla * 0.8)
            alto_dialogo = int(alto_pantalla * 0.8)
            x = (ancho_pantalla - ancho_dialogo) // 2
            y = (alto_pantalla - alto_dialogo) // 2
            dialogo.geometry(f"{ancho_dialogo}x{alto_dialogo}+{x}+{y}")
            
            dialogo.transient(self.ventana)
            dialogo.grab_set()
            
            # Frame principal con scroll
            frame_principal = ctk.CTkFrame(dialogo)
            frame_principal.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Canvas y scrollbar MEJORADO
            canvas = tk.Canvas(frame_principal, bg='#2b2b2b', highlightthickness=0)
            scrollbar = ctk.CTkScrollbar(frame_principal, orientation="vertical", command=canvas.yview)
            scrollable_frame = ctk.CTkFrame(canvas)
            
            # Configurar scroll suave
            def configurar_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            scrollable_frame.bind("<Configure>", configurar_scroll_region)
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Actualizar ancho del frame cuando cambie el canvas
            def configurar_ancho_frame(event):
                canvas.itemconfig(1, width=event.width)
            
            canvas.bind("<Configure>", configurar_ancho_frame)
            
            # Dividir en two columnas dentro del frame scrollable
            frame_contenido = ctk.CTkFrame(scrollable_frame)
            frame_contenido.pack(fill='both', expand=True, padx=10, pady=10)
            
            frame_izquierda = ctk.CTkFrame(frame_contenido)
            frame_izquierda.pack(side='left', fill='both', expand=True, padx=(0, 20))
            
            frame_derecha = ctk.CTkFrame(frame_contenido, width=300)
            frame_derecha.pack(side='right', fill='y')
            frame_derecha.pack_propagate(False)
            
            # Extraer datos
            datos_about = self._extraer_datos_about(root)
            
            # Columna izquierda - Campos editables
            campos_about = [
                ('name', 'Nombre del Mod'),
                ('author', 'Autor'),
                ('packageId', 'Package ID'),
                ('description', 'Descripción'),
            ]
            
            for campo, etiqueta in campos_about:
                ctk.CTkLabel(frame_izquierda, text=etiqueta, 
                            font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(10, 5))
                
                if campo == 'description':
                    text_widget = ctk.CTkTextbox(frame_izquierda, 
                                               font=('Segoe UI', 10),
                                               height=150)
                    text_widget.pack(fill='x', pady=(0, 10))
                    text_widget.insert('1.0', datos_about.get(campo, ''))
                    
                    # Botón de traducción
                    btn_traducir_desc = ctk.CTkButton(frame_izquierda, text="Traducir Descripción", 
                                            command=lambda tw=text_widget: self._traducir_campo_about(tw),
                                            width=200,
                                            fg_color='#9b59b6', hover_color='#8e44ad')
                    btn_traducir_desc.pack(pady=(0, 15))
                    
                    setattr(self, f'text_{campo}_about', text_widget)
                else:
                    frame_campo = ctk.CTkFrame(frame_izquierda, fg_color="transparent")
                    frame_campo.pack(fill='x', pady=(0, 10))
                    
                    entry = ctk.CTkEntry(frame_campo,
                                       font=('Segoe UI', 10))
                    entry.insert(0, datos_about.get(campo, ''))
                    entry.pack(side='left', fill='x', expand=True)
                    
                    # Botón de traducción para nombre del mod
                    if campo == 'name':
                        btn_traducir_nombre = ctk.CTkButton(frame_campo, text="Traducir", 
                                                  command=lambda e=entry: self._traducir_entry_about(e),
                                                  width=100,
                                                  fg_color='#9b59b6', hover_color='#8e44ad')
                        btn_traducir_nombre.pack(side='left', padx=(10, 0))
                    
                    setattr(self, f'entry_{campo}_about', entry)
            
            # Columna derecha - Preview del icono
            frame_icono = ctk.CTkFrame(frame_derecha)
            frame_icono.pack(fill='both', pady=(0, 15))
            
            ctk.CTkLabel(frame_icono, text="Icono del Mod", 
                        font=('Segoe UI', 12, 'bold')).pack(pady=10)
            
            # Buscar icono del mod en About/Preview con diferentes extensiones
            icono_mod_path = self._buscar_icono_mod()
            if icono_mod_path:
                frame_marco_icono = ctk.CTkFrame(frame_icono, width=200, height=200)
                frame_marco_icono.pack(pady=10)
                frame_marco_icono.pack_propagate(False)
                
                label_icono_mod = ctk.CTkLabel(frame_marco_icono, text="Cargando...", 
                                             font=('Segoe UI', 12), 
                                             justify='center')
                label_icono_mod.pack(expand=True, fill='both', padx=5, pady=5)
                
                # Mostrar preview del icono usando CTkImage
                self._mostrar_imagen_preview_ctk(icono_mod_path, label_icono_mod, 200)
            else:
                ctk.CTkLabel(frame_icono, text="No se encontró icono del mod", 
                            font=('Segoe UI', 10)).pack(pady=20)
            
            # Versiones soportadas
            frame_versiones = ctk.CTkFrame(frame_derecha)
            frame_versiones.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(frame_versiones, text="Versiones Soportadas", 
                        font=('Segoe UI', 12, 'bold')).pack(pady=10)
            
            versiones_rimworld = ['1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '1.6']
            self.vars_versiones = {}
            
            # Obtener versiones actuales
            supported_versions = root.find('supportedVersions')
            versiones_actuales = []
            if supported_versions is not None:
                for li in supported_versions.findall('li'):
                    if li.text:
                        versiones_actuales.append(li.text)
            
            for version in versiones_rimworld:
                var = ctk.BooleanVar(value=(version in versiones_actuales))
                self.vars_versiones[version] = var
                cb = ctk.CTkCheckBox(frame_versiones, text=f"RimWorld {version}", 
                                   variable=var)
                cb.pack(anchor='w', padx=10, pady=2)
            
            # Botones en la parte inferior
            frame_botones = ctk.CTkFrame(frame_izquierda, fg_color="transparent")
            frame_botones.pack(fill='x', pady=20)
            
            def guardar_about():
                try:
                    # Aplicar cambios a campos básicos
                    for campo, _ in campos_about:
                        if campo == 'description':
                            valor = getattr(self, f'text_{campo}_about').get('1.0', 'end-1c').strip()
                        else:
                            valor = getattr(self, f'entry_{campo}_about').get().strip()
                        
                        elemento = root.find(campo)
                        if valor:
                            if elemento is None:
                                elemento = ET.SubElement(root, campo)
                            elemento.text = valor
                        elif elemento is not None:
                            root.remove(elemento)
                    
                    # Aplicar versiones soportadas
                    versiones_seleccionadas = [v for v, var in self.vars_versiones.items() if var.get()]
                    
                    supported_versions = root.find('supportedVersions')
                    if versiones_seleccionadas:
                        if supported_versions is None:
                            supported_versions = ET.SubElement(root, 'supportedVersions')
                        else:
                            # Limpiar lista existente
                            for li in supported_versions.findall('li'):
                                supported_versions.remove(li)
                        # Agregar nuevas versiones
                        for version in sorted(versiones_seleccionadas):
                            li = ET.SubElement(supported_versions, 'li')
                            li.text = version
                    elif supported_versions is not None:
                        # Eliminar elemento si no hay versiones seleccionadas
                        root.remove(supported_versions)
                    
                    # Guardar archivo
                    tree.write(ruta_about, encoding='utf-8', xml_declaration=True)
                    messagebox.showinfo("Éxito", "About.xml guardado correctamente")
                    dialogo.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")
            
            btn_guardar = ctk.CTkButton(frame_botones, text="GUARDAR", 
                                  command=guardar_about, width=150,
                                  fg_color='#4caf50', hover_color='#45a049')
            btn_guardar.pack(side='left', padx=10)
            
            btn_cancelar = ctk.CTkButton(frame_botones, text="CERRAR", 
                                   command=dialogo.destroy, width=150,
                                   fg_color='#f44336', hover_color='#d32f2f')
            btn_cancelar.pack(side='left', padx=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar About.xml: {str(e)}")

    def _traducir_campo_about(self, text_widget):
        """Traduce el contenido de un campo de texto en About"""
        texto_actual = text_widget.get('1.0', 'end-1c')
        if not texto_actual.strip():
            messagebox.showwarning("Advertencia", "No hay texto para traducir")
            return
        
        try:
            texto_traducido = GoogleTranslator(source='auto', target='es').translate(texto_actual)
            if texto_traducido:
                text_widget.delete('1.0', ctk.END)
                text_widget.insert('1.0', texto_traducido)
            else:
                messagebox.showerror("Error", "No se pudo traducir el texto")
        except Exception as e:
            messagebox.showerror("Error", f"Error en traducción: {str(e)}")

    def _traducir_entry_about(self, entry_widget):
        """Traduce el contenido de un campo Entry en About"""
        texto_actual = entry_widget.get()
        if not texto_actual.strip():
            messagebox.showwarning("Advertencia", "No hay texto para traducir")
            return
        
        try:
            texto_traducido = GoogleTranslator(source='auto', target='es').translate(texto_actual)
            if texto_traducido:
                entry_widget.delete(0, ctk.END)
                entry_widget.insert(0, texto_traducido)
            else:
                messagebox.showerror("Error", "No se pudo traducir el texto")
        except Exception as e:
            messagebox.showerror("Error", f"Error en traducción: {str(e)}")

    def _buscar_icono_mod(self):
        """Busca el icono del mod en About/Preview con diferentes extensiones"""
        if not self.carpeta_mod:
            return None
        
        carpeta_about = os.path.join(self.carpeta_mod, "About")
        if not os.path.exists(carpeta_about):
            return None
        
        # Extensiones posibles para el icono
        extensiones = ['.png', '.jpg', '.jpeg', '.dds']
        nombre_base = 'Preview'
        
        for ext in extensiones:
            ruta_icono = os.path.join(carpeta_about, nombre_base + ext)
            if os.path.exists(ruta_icono):
                return ruta_icono
        
        # Buscar cualquier archivo que empiece con 'Preview'
        try:
            for file in os.listdir(carpeta_about):
                if file.lower().startswith('preview'):
                    ruta_icono = os.path.join(carpeta_about, file)
                    if os.path.isfile(ruta_icono):
                        return ruta_icono
        except:
            pass
        
        return None

    def _extraer_datos_about(self, root):
        """Extrae datos de About.xml"""
        datos = {}
        elementos = ['name', 'author', 'packageId', 'description']
        for elem in elementos:
            elemento = root.find(elem)
            if elemento is not None and elemento.text:
                datos[elem] = elemento.text
        return datos

    def guardar_xml(self):
        """Guarda las traducciones al archivo XML"""
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
            self.actualizar_status(f"{textos_guardados} traducciones guardadas")
            messagebox.showinfo("Éxito", f"Guardadas {textos_guardados} traducciones")
            
        except Exception as e:
            self.actualizar_status(f"Error guardando: {str(e)}")
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")

    def configurar_bindings(self):
        """Configura atajos de teclado"""
        self.tree_textos.bind('<Double-1>', self.al_doble_click_celda)
        self.ventana.bind('<Control-c>', self.copiar_seleccion)
        self.ventana.bind('<Control-v>', self.pegar_seleccion)
        self.ventana.bind('<Control-a>', self.seleccionar_todo)
        self.tree_textos.bind('<Return>', self.terminar_edicion)
        self.tree_textos.bind('<Escape>', self.cancelar_edicion)
        self.ventana.bind('<Control-s>', lambda e: self.guardar_xml())
        self.ventana.bind('<Control-f>', lambda e: self.entry_buscar.focus())

    def al_doble_click_celda(self, event):
        """Inicia edición con doble clic"""
        region = self.tree_textos.identify_region(event.x, event.y)
        if region == "cell":
            item = self.tree_textos.identify_row(event.y)
            columna = self.tree_textos.identify_column(event.x)
            
            if item and columna in ('#2', '#3'):
                self.iniciar_edicion(item, columna)

    def iniciar_edicion(self, item, columna):
        """Inicia edición directa"""
        valores = self.tree_textos.item(item, 'values')
        indice_columna = int(columna[1]) - 1
        valor_actual = valores[indice_columna] if indice_columna < len(valores) else ""
        
        bbox = self.tree_textos.bbox(item, columna)
        if not bbox:
            return
        
        self.celda_editando = (item, columna)
        self.entry_edicion = ctk.CTkEntry(self.tree_textos, 
                                        font=('Segoe UI', 10))
        
        self.entry_edicion.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        self.entry_edicion.insert(0, valor_actual)
        self.entry_edicion.select_range(0, ctk.END)
        self.entry_edicion.focus_set()
        
        self.entry_edicion.bind('<Return>', self.guardar_edicion)
        self.entry_edicion.bind('<Escape>', self.cancelar_edicion)

    def guardar_edicion(self, event=None):
        """Guarda la edición"""
        if not self.celda_editando or not self.entry_edicion:
            return
        
        item, columna = self.celda_editando
        nuevo_valor = self.entry_edicion.get()
        indice_columna = int(columna[1]) - 1
        
        valores = list(self.tree_textos.item(item, 'values'))
        
        if indice_columna < len(valores):
            valores[indice_columna] = nuevo_valor
            if columna == '#3' and nuevo_valor:
                valores[3] = "Editado"
            self.tree_textos.item(item, values=valores)
            
            if columna == '#3':
                id_texto = valores[0]
                self.traducciones[id_texto] = nuevo_valor
        
        self.terminar_edicion()

    def cancelar_edicion(self, event=None):
        """Cancela la edición"""
        self.terminar_edicion()

    def terminar_edicion(self, event=None):
        """Termina la edición"""
        if self.entry_edicion:
            self.entry_edicion.destroy()
            self.entry_edicion = None
        self.celda_editando = None

    def copiar_seleccion(self, event=None):
        """Copia texto seleccionado"""
        seleccionados = self.tree_textos.selection()
        if seleccionados:
            item = seleccionados[0]
            valores = self.tree_textos.item(item, 'values')
            texto = " | ".join(str(v) for v in valores if v)
            self.ventana.clipboard_clear()
            self.ventana.clipboard_append(texto)
            self.actualizar_status("Texto copiado")

    def pegar_seleccion(self, event=None):
        """Pega texto en celda seleccionada"""
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
                valores[3] = "Pegado"
            self.tree_textos.item(item, values=valores)
            
            if columna == '#3':
                id_texto = valores[0]
                self.traducciones[id_texto] = texto
            
            self.actualizar_status("Texto pegado")

    def seleccionar_todo(self, event=None):
        """Selecciona todas las filas"""
        items = self.tree_textos.get_children()
        self.tree_textos.selection_set(items)
        return "break"

    def limpiar_imagenes(self):
        """Limpia todas las referencias a imágenes para evitar memory leaks"""
        # Limpiar cache de búsqueda de imágenes
        self._cache_busqueda_imagenes.clear()
        self._cache_emojis.clear()
        
        # Limpiar imágenes de preview
        if hasattr(self, 'imagenes_preview'):
            for imagen in self.imagenes_preview:
                try:
                    if hasattr(imagen, '_ctk_image'):
                        imagen._ctk_image = None
                    del imagen
                except:
                    pass
            self.imagenes_preview.clear()

    def cerrar_aplicacion(self):
        """Cierra la aplicación limpiando recursos"""
        self.limpiar_imagenes()
        self.guardar_configuracion()
        self.guardar_cache_traducciones()
        self.ventana.quit()
        self.ventana.destroy()

# Manejo de excepciones no capturadas
def excepthook(exc_type, exc_value, exc_traceback):
    error_msg = f"Error no capturado: {exc_value}"
    print(error_msg)
    try:
        messagebox.showerror("Error Fatal", error_msg)
    except:
        pass

sys.excepthook = excepthook

if __name__ == "__main__":
    try:
        app = EditorTematico()
        app.ventana.protocol("WM_DELETE_WINDOW", app.cerrar_aplicacion)
        app.ventana.mainloop()
    except KeyboardInterrupt:
        print("\n¡Hasta luego!")
    except Exception as e:
        error_msg = f"Error: {e}"
        print(error_msg)
        messagebox.showerror("Error", error_msg)