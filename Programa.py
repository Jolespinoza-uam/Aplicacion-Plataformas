# Aplicacion-Plataformas
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime
from typing import List, Dict

class Gasto:
    def __init__(self, descripcion: str, monto: float, categoria: str, fecha: str = None):
        self.descripcion = descripcion
        self.monto = monto
        self.categoria = categoria
        self.fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict:
        return {
            'descripcion': self.descripcion,
            'monto': self.monto,
            'categoria': self.categoria,
            'fecha': self.fecha
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Gasto':
        return cls(
            descripcion=data['descripcion'],
            monto=data['monto'],
            categoria=data['categoria'],
            fecha=data['fecha']
        )

class GestorGastos:
    def __init__(self, archivo_datos: str = "gastos.json"):
        self.archivo_datos = archivo_datos
        self.gastos: List[Gasto] = []
        self.cargar_datos()
    
    def cargar_datos(self):
        """Carga los gastos desde el archivo JSON"""
        if os.path.exists(self.archivo_datos):
            try:
                with open(self.archivo_datos, 'r', encoding='utf-8') as archivo:
                    datos = json.load(archivo)
                    self.gastos = [Gasto.from_dict(gasto) for gasto in datos]
            except (json.JSONDecodeError, KeyError):
                self.gastos = []
    
    def guardar_datos(self):
        """Guarda los gastos en el archivo JSON"""
        with open(self.archivo_datos, 'w', encoding='utf-8') as archivo:
            json.dump([gasto.to_dict() for gasto in self.gastos], 
                     archivo, ensure_ascii=False, indent=2)
    
    def agregar_gasto(self, descripcion: str, monto: float, categoria: str) -> bool:
        """Agrega un nuevo gasto"""
        if monto <= 0:
            return False
        
        gasto = Gasto(descripcion, monto, categoria)
        self.gastos.append(gasto)
        self.guardar_datos()
        return True
    
    def editar_gasto(self, indice: int, descripcion: str, monto: float, categoria: str) -> bool:
        """Edita un gasto existente"""
        if 0 <= indice < len(self.gastos) and monto > 0:
            self.gastos[indice].descripcion = descripcion
            self.gastos[indice].monto = monto
            self.gastos[indice].categoria = categoria
            self.guardar_datos()
            return True
        return False
    
    def eliminar_gasto(self, indice: int) -> bool:
        """Elimina un gasto por su índice"""
        if 0 <= indice < len(self.gastos):
            self.gastos.pop(indice)
            self.guardar_datos()
            return True
        return False
    
    def obtener_gastos_filtrados(self, categoria: str = None, mes: str = None) -> List[Gasto]:
        """Obtiene gastos filtrados por categoría y/o mes"""
        gastos_filtrados = self.gastos
        
        if categoria and categoria != "Todas":
            gastos_filtrados = [g for g in gastos_filtrados if g.categoria == categoria]
        
        if mes and mes != "Todos":
            gastos_filtrados = [g for g in gastos_filtrados if g.fecha.startswith(mes)]
        
        return gastos_filtrados
    
    def obtener_categorias(self) -> List[str]:
        """Obtiene lista de categorías únicas"""
        categorias = list(set(gasto.categoria for gasto in self.gastos))
        categorias.sort()
        return categorias
    
    def obtener_meses(self) -> List[str]:
        """Obtiene lista de meses únicos (YYYY-MM)"""
        meses = list(set(gasto.fecha[:7] for gasto in self.gastos))
        meses.sort(reverse=True)
        return meses
    
    def obtener_total_gastos(self, gastos: List[Gasto] = None) -> float:
        """Calcula el total de gastos"""
        if gastos is None:
            gastos = self.gastos
        return sum(gasto.monto for gasto in gastos)
    
    def obtener_gastos_por_categoria(self, gastos: List[Gasto] = None) -> Dict[str, float]:
        """Obtiene el total de gastos por categoría"""
        if gastos is None:
            gastos = self.gastos
        
        categorias = {}
        for gasto in gastos:
            categorias[gasto.categoria] = categorias.get(gasto.categoria, 0) + gasto.monto
        return categorias

class AplicacionGestorGastos:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Gastos - Control Financiero")
        self.root.geometry("900x600")
        self.root.configure(bg='#f0f0f0')
        
        self.gestor = GestorGastos()
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Cargar datos iniciales
        self.actualizar_lista_gastos()
        self.actualizar_estadisticas()
    
    def configurar_estilo(self):
        """Configura los estilos de la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="💰 Gestor de Gastos Personal", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Notebook (pestañas)
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Agregar Gastos
        self.crear_pestana_agregar(notebook)
        
        # Pestaña 2: Ver Gastos
        self.crear_pestana_ver(notebook)
        
        # Pestaña 3: Estadísticas
        self.crear_pestana_estadisticas(notebook)
    
    def crear_pestana_agregar(self, notebook):
        """Crea la pestaña para agregar gastos"""
        frame = ttk.Frame(notebook, padding="20")
        notebook.add(frame, text="Agregar Gasto")
        
        # Configurar grid
        for i in range(4):
            frame.rowconfigure(i, weight=1)
        frame.columnconfigure(1, weight=1)
        
        # Campos del formulario
        ttk.Label(frame, text="Descripción:", style='Header.TLabel').grid(
            row=0, column=0, sticky=tk.W, pady=10)
        self.descripcion_entry = ttk.Entry(frame, width=30, font=('Arial', 10))
        self.descripcion_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        ttk.Label(frame, text="Monto:", style='Header.TLabel').grid(
            row=1, column=0, sticky=tk.W, pady=10)
        self.monto_entry = ttk.Entry(frame, width=30, font=('Arial', 10))
        self.monto_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        
        ttk.Label(frame, text="Categoría:", style='Header.TLabel').grid(
            row=2, column=0, sticky=tk.W, pady=10)
        self.categoria_combobox = ttk.Combobox(frame, values=self.obtener_categorias_sugeridas(), 
                                              font=('Arial', 10))
        self.categoria_combobox.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10, padx=(10, 0))
        self.categoria_combobox.set('Comida')
        
        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Agregar Gasto", 
                  command=self.agregar_gasto).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar Campos", 
                  command=self.limpiar_campos).pack(side=tk.LEFT, padx=5)
    
    def crear_pestana_ver(self, notebook):
        """Crea la pestaña para ver y gestionar gastos"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="Ver Gastos")
        
        # Configurar grid
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Frame de filtros
        filter_frame = ttk.Frame(frame)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="Categoría:").pack(side=tk.LEFT, padx=(0, 5))
        self.filtro_categoria = ttk.Combobox(filter_frame, values=["Todas"] + self.gestor.obtener_categorias(),
                                            state="readonly", width=15)
        self.filtro_categoria.set("Todas")
        self.filtro_categoria.pack(side=tk.LEFT, padx=(0, 15))
        self.filtro_categoria.bind('<<ComboboxSelected>>', self.aplicar_filtros)
        
        ttk.Label(filter_frame, text="Mes:").pack(side=tk.LEFT, padx=(0, 5))
        self.filtro_mes = ttk.Combobox(filter_frame, values=["Todos"] + self.gestor.obtener_meses(),
                                      state="readonly", width=15)
        self.filtro_mes.set("Todos")
        self.filtro_mes.pack(side=tk.LEFT, padx=(0, 15))
        self.filtro_mes.bind('<<ComboboxSelected>>', self.aplicar_filtros)
        
        ttk.Button(filter_frame, text="Actualizar", 
                  command=self.actualizar_lista_gastos).pack(side=tk.LEFT)
        
        # Treeview para mostrar gastos
        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        columns = ('#1', '#2', '#3', '#4')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        self.tree.heading('#1', text='Descripción')
        self.tree.heading('#2', text='Monto')
        self.tree.heading('#3', text='Categoría')
        self.tree.heading('#4', text='Fecha')
        
        self.tree.column('#1', width=200)
        self.tree.column('#2', width=100)
        self.tree.column('#3', width=150)
        self.tree.column('#4', width=150)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame de botones de acción
        action_frame = ttk.Frame(frame)
        action_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(action_frame, text="Editar Seleccionado", 
                  command=self.editar_gasto_seleccionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Eliminar Seleccionado", 
                  command=self.eliminar_gasto_seleccionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Exportar a TXT", 
                  command=self.exportar_gastos).pack(side=tk.LEFT, padx=5)
    
    def crear_pestana_estadisticas(self, notebook):
        """Crea la pestaña de estadísticas sin gráficos"""
        frame = ttk.Frame(notebook, padding="20")
        notebook.add(frame, text="Estadísticas")
        
        self.stats_text = scrolledtext.ScrolledText(frame, width=80, height=20, font=('Arial', 10))
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        self.stats_text.config(state=tk.DISABLED)
    
    def obtener_categorias_sugeridas(self):
        """Retorna categorías sugeridas para el combobox"""
        return ['Comida', 'Transporte', 'Entretenimiento', 'Salud', 'Educación', 
                'Vivienda', 'Ropa', 'Tecnología', 'Otros']
    
    def agregar_gasto(self):
        """Agrega un nuevo gasto desde la interfaz"""
        descripcion = self.descripcion_entry.get().strip()
        monto_str = self.monto_entry.get().strip()
        categoria = self.categoria_combobox.get().strip()
        
        if not descripcion or not monto_str or not categoria:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            monto = float(monto_str)
            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser mayor a 0")
                return
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")
            return
        
        if self.gestor.agregar_gasto(descripcion, monto, categoria):
            messagebox.showinfo("Éxito", "Gasto agregado correctamente")
            self.limpiar_campos()
            self.actualizar_lista_gastos()
            self.actualizar_estadisticas()
            self.actualizar_filtros()
        else:
            messagebox.showerror("Error", "Error al agregar el gasto")
    
    def limpiar_campos(self):
        """Limpia los campos del formulario"""
        self.descripcion_entry.delete(0, tk.END)
        self.monto_entry.delete(0, tk.END)
        self.categoria_combobox.set('Comida')
        self.descripcion_entry.focus()
    
    def actualizar_lista_gastos(self):
        """Actualiza la lista de gastos en el treeview"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener gastos filtrados
        categoria = self.filtro_categoria.get()
        mes = self.filtro_mes.get()
        gastos = self.gestor.obtener_gastos_filtrados(
            categoria if categoria != "Todas" else None,
            mes if mes != "Todos" else None
        )
        
        # Agregar gastos al treeview
        for gasto in gastos:
            self.tree.insert('', tk.END, values=(
                gasto.descripcion,
                f"${gasto.monto:.2f}",
                gasto.categoria,
                gasto.fecha
            ))
    
    def aplicar_filtros(self, event=None):
        """Aplica los filtros seleccionados"""
        self.actualizar_lista_gastos()
    
    def actualizar_filtros(self):
        """Actualiza las opciones de los filtros"""
        categorias = ["Todas"] + self.gestor.obtener_categorias()
        meses = ["Todos"] + self.gestor.obtener_meses()
        
        self.filtro_categoria['values'] = categorias
        self.filtro_mes['values'] = meses
    
    def editar_gasto_seleccionado(self):
        """Edita el gasto seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un gasto para editar")
            return
        
        item = seleccion[0]
        valores = self.tree.item(item, 'values')
        indice = self.tree.index(item)
        
        # Crear ventana de edición
        self.crear_ventana_edicion(indice, valores)
    
    def crear_ventana_edicion(self, indice, valores):
        """Crea una ventana para editar un gasto"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Editar Gasto")
        ventana.geometry("400x200")
        ventana.resizable(False, False)
        
        frame = ttk.Frame(ventana, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos de edición
        ttk.Label(frame, text="Descripción:").grid(row=0, column=0, sticky=tk.W, pady=5)
        desc_entry = ttk.Entry(frame, width=30)
        desc_entry.insert(0, valores[0])
        desc_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="Monto:").grid(row=1, column=0, sticky=tk.W, pady=5)
        monto_entry = ttk.Entry(frame, width=30)
        monto_entry.insert(0, valores[1].replace('$', ''))
        monto_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="Categoría:").grid(row=2, column=0, sticky=tk.W, pady=5)
        cat_combobox = ttk.Combobox(frame, values=self.obtener_categorias_sugeridas(), width=27)
        cat_combobox.set(valores[2])
        cat_combobox.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Botones
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        def guardar_cambios():
            descripcion = desc_entry.get().strip()
            monto_str = monto_entry.get().strip()
            categoria = cat_combobox.get().strip()
            
            if not descripcion or not monto_str or not categoria:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            try:
                monto = float(monto_str.replace('$', ''))
                if monto <= 0:
                    messagebox.showerror("Error", "El monto debe ser mayor a 0")
                    return
            except ValueError:
                messagebox.showerror("Error", "El monto debe ser un número válido")
                return
            
            if self.gestor.editar_gasto(indice, descripcion, monto, categoria):
                messagebox.showinfo("Éxito", "Gasto editado correctamente")
                ventana.destroy()
                self.actualizar_lista_gastos()
                self.actualizar_estadisticas()
                self.actualizar_filtros()
            else:
                messagebox.showerror("Error", "Error al editar el gasto")
        
        ttk.Button(button_frame, text="Guardar", 
                  command=guardar_cambios).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=ventana.destroy).pack(side=tk.LEFT, padx=5)
        
        frame.columnconfigure(1, weight=1)
    
    def eliminar_gasto_seleccionado(self):
        """Elimina el gasto seleccionado"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un gasto para eliminar")
            return
        
        item = seleccion[0]
        valores = self.tree.item(item, 'values')
        indice = self.tree.index(item)
        
        confirmacion = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar el gasto:\n"
            f"'{valores[0]}' por {valores[1]}?"
        )
        
        if confirmacion:
            if self.gestor.eliminar_gasto(indice):
                messagebox.showinfo("Éxito", "Gasto eliminado correctamente")
                self.actualizar_lista_gastos()
                self.actualizar_estadisticas()
                self.actualizar_filtros()
            else:
                messagebox.showerror("Error", "Error al eliminar el gasto")
    
    def exportar_gastos(self):
        """Exporta los gastos a un archivo de texto"""
        try:
            with open("reporte_gastos.txt", "w", encoding="utf-8") as archivo:
                archivo.write("REPORTE DE GASTOS\n")
                archivo.write("=" * 50 + "\n\n")
                
                total_general = 0
                
                for categoria in self.gestor.obtener_categorias():
                    gastos_categoria = [g for g in self.gestor.gastos if g.categoria == categoria]
                    total_categoria = sum(g.monto for g in gastos_categoria)
                    total_general += total_categoria
                    
                    archivo.write(f"{categoria.upper()} - Total: ${total_categoria:.2f}\n")
                    archivo.write("-" * 30 + "\n")
                    
                    for gasto in gastos_categoria:
                        archivo.write(f"  {gasto.descripcion}: ${gasto.monto:.2f} ({gasto.fecha})\n")
                    
                    archivo.write("\n")
                
                archivo.write(f"\nTOTAL GENERAL: ${total_general:.2f}\n")
            
            messagebox.showinfo("Éxito", "Reporte exportado como 'reporte_gastos.txt'")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte: {str(e)}")
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas en formato texto"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        if not self.gestor.gastos:
            self.stats_text.insert(tk.END, "No hay gastos registrados")
            self.stats_text.config(state=tk.DISABLED)
            return
        
        # Calcular estadísticas
        total_gastos = self.gestor.obtener_total_gastos()
        total_categorias = self.gestor.obtener_gastos_por_categoria()
        gasto_promedio = total_gastos / len(self.gestor.gastos)
        
        # Mostrar estadísticas en texto
        stats_content = "📊 ESTADÍSTICAS DETALLADAS\n"
        stats_content += "=" * 50 + "\n\n"
        
        stats_content += f"💰 RESUMEN GENERAL:\n"
        stats_content += f"• Total de gastos: ${total_gastos:.2f}\n"
        stats_content += f"• Cantidad de gastos: {len(self.gestor.gastos)}\n"
        stats_content += f"• Gasto promedio: ${gasto_promedio:.2f}\n"
        stats_content += f"• Categorías utilizadas: {len(total_categorias)}\n\n"
        
        stats_content += f"📈 DISTRIBUCIÓN POR CATEGORÍA:\n"
        stats_content += "-" * 40 + "\n"
        
        for categoria, monto in sorted(total_categorias.items(), key=lambda x: x[1], reverse=True):
            porcentaje = (monto / total_gastos) * 100
            stats_content += f"• {categoria}: ${monto:.2f} ({porcentaje:.1f}%)\n"
        
        self.stats_text.insert(tk.END, stats_content)
        self.stats_text.config(state=tk.DISABLED)

def main():
    """Función principal para ejecutar la aplicación"""
    try:
        root = tk.Tk()
        app = AplicacionGestorGastos(root)
        root.mainloop()
    except ImportError as e:
        print(f"Error: {e}")
        print("\nSolución:")
        print("1. En Windows: Reinstala Python marcando 'tcl/tk and IDLE'")
        print("2. En Linux: Ejecuta 'sudo apt-get install python3-tk'")
        print("3. En macOS: Ejecuta 'brew install python-tk'")

if __name__ == "__main__":
    main()
