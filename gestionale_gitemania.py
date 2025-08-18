#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestionale Gitemania - Applicazione Desktop (Versione Finale Stabile e Corretta)
"""
import sys, os, tkinter as tk, threading, queue
from tkinter import ttk, messagebox
from typing import Dict, List
from config import config
from woocommerce_api import WooCommerceManager
from database_manager import DatabaseManager
from export_manager import ExportManager
from theme_manager import GiteManiTheme
from modern_components import ModernStatusBar, ModernOrdersView
from modern_dashboard import ModernDashboard
from gui_components import SettingsPanel, AboutDialog, OrderDetailWindow

class GestionaleGitemania:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Gestionale Gitemania - TechExpresso")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        GiteManiTheme.apply_to_root(self.root)
        
        self.queue = queue.Queue()
        self.database_manager = DatabaseManager()
        self.sync_running = False
        
        self._init_application()

    def _init_application(self):
        try:
            self._init_managers()
            self._create_gui()
            self._bind_events()
            self.root.after(100, self._process_queue)
            self._load_initial_data_from_db()
            self._auto_connect()
        except Exception as e:
            messagebox.showerror("Errore Critico", f"Errore inizializzazione:\n{e}")
            sys.exit(1)

    def _process_queue(self):
        try:
            while not self.queue.empty():
                msg_type, data = self.queue.get_nowait()
                
                if msg_type == "update_status":
                    self.status_bar.set_status(data)
                
                elif msg_type == "refresh_all_data":
                    orders, stats = data
                    self.orders_view.update_orders(orders)
                    self.dashboard.update_dashboard(stats)
                    self.status_bar.set_status(f"Visualizzati {len(orders)} ordini.")
                
                elif msg_type == "sync_complete":
                    inserted, updated = data
                    total_changes = inserted + updated
                    msg = f"Sincronizzazione completata. {total_changes} ordini aggiornati." if total_changes > 0 else "Nessun nuovo aggiornamento da registrare."
                    self.status_bar.set_status(msg)
                    self._refresh_orders_view()
                
                elif msg_type == "export_complete":
                    success, result_data = data
                    if success:
                        self.status_bar.set_status(f"Export completato: {result_data['file_name']}")
                        messagebox.showinfo("Export Riuscito", f"Esportati {result_data['total_records']} record.\nFile salvato in: {result_data['file_path']}")
                    else:
                        self.status_bar.set_status("Errore durante l'export.")
                        messagebox.showerror("Export Fallito", f"Errore: {result_data['error_message']}")

                elif msg_type == "error":
                    messagebox.showerror("Errore", data)
                    self.status_bar.set_status(f"Errore: {data}")

        finally:
            self.root.after(200, self._process_queue)

    def _init_managers(self):
        self.woo_manager = WooCommerceManager(on_order_update=self.handle_background_sync)
        self.export_manager = ExportManager(database_manager=self.database_manager, on_export_complete=self._on_export_complete)

    def handle_background_sync(self, orders: List[Dict]):
        if not orders:
            return
        
        def task():
            inserted, updated = self.database_manager.sync_multiple_orders(orders)
            if (inserted + updated) > 0:
                self.queue.put(("sync_complete", (inserted, updated)))
        
        threading.Thread(target=task, daemon=True).start()

    def _create_gui(self):
        if os.path.exists('assets/icon.ico'): self.root.iconbitmap('assets/icon.ico')
        self._create_menu()
        self._create_modern_toolbar()
        self._create_modern_main_area()
        self.status_bar = ModernStatusBar(self.root)
        self.status_bar.pack(side='bottom', fill='x', pady=(5,0), padx=10)

    def _bind_events(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.orders_view.bind("<<ShowOrderDetails>>", self._on_show_order_details)

    def _create_menu(self):
        menubar = tk.Menu(self.root); self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Connetti", command=self._connect_services)
        file_menu.add_command(label="Disconnetti", command=self._disconnect_services)
        file_menu.add_separator(); file_menu.add_command(label="Esporta Ordini", command=self._export_orders)
        file_menu.add_separator(); file_menu.add_command(label="Esci", command=self._on_closing)
        orders_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label="Ordini", menu=orders_menu)
        orders_menu.add_command(label="Sincronizza Recenti", command=self._quick_sync)
        orders_menu.add_command(label="Sincronizza Tutto", command=self._force_sync)

    def _create_modern_toolbar(self):
        toolbar = ttk.Frame(self.root); toolbar.pack(side='top', fill='x', padx=10, pady=10)
        ttk.Button(toolbar, text="🔗 Connetti", style='Primary.TButton', command=self._connect_services).pack(side='left', padx=(0, 5))
        ttk.Button(toolbar, text="🔄 Sync Recenti", command=self._quick_sync).pack(side='left', padx=(0, 5))
        ttk.Button(toolbar, text="🔄 Sync Completo", style='Primary.TButton', command=self._force_sync).pack(side='left', padx=(0, 5))
        ttk.Button(toolbar, text="📄 Esporta", style='Success.TButton', command=self._export_orders).pack(side='left', padx=(5, 0))
        self.connection_info_frame = ttk.Frame(toolbar); self.connection_info_frame.pack(side='left', padx=15)
        self.connection_indicator = ttk.Label(self.connection_info_frame, text="●", foreground=GiteManiTheme.COLORS['danger'], font=('Segoe UI', 12)); self.connection_indicator.pack(side='left')
        self.connection_info = ttk.Label(self.connection_info_frame, text="Disconnesso", font=GiteManiTheme.FONTS['default']); self.connection_info.pack(side='left', padx=5)

    def _create_modern_main_area(self):
        main_container = ttk.Frame(self.root); main_container.pack(fill='both', expand=True, padx=10, pady=0)
        self.notebook = ttk.Notebook(main_container, style='TNotebook'); self.notebook.pack(fill='both', expand=True)
        self.dashboard = ModernDashboard(self.notebook); self.notebook.add(self.dashboard, text="📊 Dashboard")
        self.orders_view = ModernOrdersView(self.notebook, on_filter_apply=self._apply_order_filters); self.notebook.add(self.orders_view, text="📋 Ordini")
        settings_panel = SettingsPanel(self.notebook, current_config=config.config, on_save=self._on_settings_saved, on_test=self._test_connections)
        self.notebook.add(settings_panel, text="⚙️ Impostazioni")

    def _auto_connect(self):
        if config.get('app', 'first_run', True): self.root.after(500, self._show_first_run_wizard)
        elif config.get('woocommerce', 'base_url'): threading.Thread(target=self._connect_services, daemon=True).start()

    def _show_first_run_wizard(self):
        if messagebox.askquestion("Benvenuto!", "Prima configurazione richiesta. Vuoi andare alle impostazioni?"): self.notebook.select(2)
        config.set('app', 'first_run', False); config.save_config()

    def _connect_services(self):
        self.queue.put(("update_status", "Connessione in corso..."))
        woo_url, key, secret = (config.get('woocommerce', 'base_url'), config.get_encrypted('woocommerce', 'consumer_key'), config.get_encrypted('woocommerce', 'consumer_secret'))
        if not all([woo_url, key, secret]):
            self.queue.put(("error", "Configurazione WooCommerce mancante.")); self.notebook.select(2); return
        threading.Thread(target=self._perform_connection, args=(woo_url, key, secret), daemon=True).start()

    def _perform_connection(self, url, key, secret):
        if self.woo_manager.initialize(url, key, secret):
            self.root.after(0, self._update_connection_status, True)
            self._start_sync()
            self._load_initial_data_from_db()
        else:
            self.root.after(0, self._update_connection_status, False)
            self.queue.put(("error", "Connessione a WooCommerce fallita."))

    def _update_connection_status(self, is_connected: bool):
        if is_connected:
            self.status_bar.set_connection_status(True, "WooCommerce"); self.connection_info.config(text="Connesso"); self.connection_indicator.config(foreground=GiteManiTheme.COLORS['success'])
        else:
            self.status_bar.set_connection_status(False, "Errore"); self.connection_info.config(text="Errore"); self.connection_indicator.config(foreground=GiteManiTheme.COLORS['danger'])
        self.queue.put(("update_status", "Pronto"))

    def _load_initial_data_from_db(self):
        self._refresh_orders_view()

    def _refresh_orders_view(self, filters: Dict = None):
        """ Legge dal DB in un thread e mette i dati in coda per l'aggiornamento della GUI. """
        def task():
            orders = self.database_manager.get_orders(filters)
            stats = self.database_manager.get_order_stats()
            self.queue.put(("refresh_all_data", (orders, stats)))
        threading.Thread(target=task, daemon=True).start()

    def _apply_order_filters(self):
        filters = self._get_current_filters()
        self.queue.put(("update_status", "Ricerca in corso..."))
        self._refresh_orders_view(filters or {})
    
    def _get_current_filters(self) -> Dict:
        search_term = self.orders_view.search_var.get().strip()
        status = self.orders_view.status_var.get().strip()
        filters = {};
        if search_term: filters['search_term'] = search_term
        if status: filters['status'] = status
        return filters

    def _force_sync(self):
        def task():
            if not (self.woo_manager and self.woo_manager.api):
                self.queue.put(("error", "Per favore, connettiti prima."))
                return
            self.queue.put(("update_status", "Download di tutti gli ordini in corso..."))
            orders = self.woo_manager.get_orders(paginate_all=True)
            if orders is not None:
                self.queue.put(("update_status", f"Scaricati {len(orders)} ordini. Salvataggio in corso..."))
                inserted, updated = self.database_manager.sync_multiple_orders(orders)
                self.queue.put(("sync_complete", (inserted, updated)))
            else:
                self.queue.put(("error", "Errore durante il download degli ordini."))
        threading.Thread(target=task, daemon=True).start()

    def _quick_sync(self):
        def task():
            if not (self.woo_manager and self.woo_manager.api):
                self.queue.put(("error", "Per favore, connettiti prima."))
                return
            self.queue.put(("update_status", "Sincronizzazione ordini delle ultime 24 ore..."))
            recent_orders = self.woo_manager.fetch_last_day_orders()
            if recent_orders is not None:
                inserted, updated = self.database_manager.sync_multiple_orders(recent_orders)
                self.queue.put(("sync_complete", (inserted, updated)))
            else:
                self.queue.put(("error", "Errore durante la sincronizzazione rapida."))
        threading.Thread(target=task, daemon=True).start()
    
    def _start_sync(self):
        if self.woo_manager and not self.sync_running:
            self.woo_manager.start_sync(); self.sync_running = True; self.status_bar.set_sync_status(True)

    def _disconnect_services(self):
        if self.sync_running:
            self.woo_manager.stop_sync(); self.sync_running = False; self.status_bar.set_sync_status(False)
        self._update_connection_status(False)

    def _on_closing(self):
        if self.sync_running: self.woo_manager.stop_sync()
        self.root.destroy()
        
    def _on_settings_saved(self, new_config: Dict):
        try:
            for section, values in new_config.items():
                for key, value in values.items(): config.set(section, key, value)
            config.save_config(); messagebox.showinfo("Impostazioni", "Configurazione salvata.")
            if messagebox.askyesno("Riconnessione", "Vuoi connetterti con la nuova configurazione?"): self._connect_services()
        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio:\n{e}")

    def _test_connections(self): messagebox.showinfo("Test", "In sviluppo...")
    
    def _on_show_order_details(self, event):
        try:
            order_id = self.orders_view.selected_order_id
            if order_id is None: return
            order_data = next((order for order in self.orders_view.orders_data if order.get('woo_id') == order_id), None)
            if order_data: OrderDetailWindow(self.root, order_data)
            else: messagebox.showwarning("Errore", f"Impossibile trovare i dati per l'ordine ID {order_id}.")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile visualizzare i dettagli dell'ordine.\nDettaglio: {e}")

    def _export_orders(self):
        self.queue.put(("update_status", "Preparazione dell'export in corso..."))
        current_filters = self._get_current_filters()
        threading.Thread(target=self.export_manager.export_orders_csv, args=(current_filters,), daemon=True).start()

    def _on_export_complete(self, result):
        result_data = {
            'file_name': result.file_name,
            'total_records': result.total_records,
            'file_path': result.file_path,
            'error_message': result.error_message
        }
        self.queue.put(("export_complete", (result.success, result_data)))

    def _show_about(self): AboutDialog(self.root)
    def run(self): self.root.mainloop()

if __name__ == "__main__":
    app = GestionaleGitemania()
    app.run()
