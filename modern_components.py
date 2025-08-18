#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Componenti GUI Moderni per Gestionale Gitemania (Versione Finale Stabile con Filtri)
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Dict, List, Callable
from theme_manager import GiteManiTheme, ModernUIHelper

class ModernStatusBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style='TFrame')
        self.status_var = tk.StringVar(value="🚀 Gestionale pronto")
        self.connection_var = tk.StringVar(value="Disconnesso")
        self._create_widgets()
    def _create_widgets(self):
        self.status_label = ttk.Label(self, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=(10, 20))
        ttk.Separator(self, orient='vertical').pack(side=tk.LEFT, fill='y', padx=5)
        self.conn_frame = ttk.Frame(self)
        self.conn_frame.pack(side=tk.LEFT, padx=5)
        self.conn_indicator = ttk.Label(self.conn_frame, text="●", foreground=GiteManiTheme.COLORS['danger'], font=('Segoe UI', 12))
        self.conn_indicator.pack(side='left')
        self.conn_label = ttk.Label(self, textvariable=self.connection_var)
        self.conn_label.pack(side=tk.LEFT, padx=(5, 0))
        self.sync_indicator = ttk.Label(self, text="⏸️", font=('Segoe UI', 12))
        self.sync_indicator.pack(side=tk.RIGHT, padx=5)
    def set_status(self, message: str): self.status_var.set(message)
    def set_connection_status(self, connected: bool, service: str = ""):
        color = GiteManiTheme.COLORS['success'] if connected else GiteManiTheme.COLORS['danger']
        text = f"{service} Connesso" if connected else f"{service} Disconnesso"
        self.connection_var.set(text)
        self.conn_indicator.configure(foreground=color)
    def set_sync_status(self, syncing: bool):
        self.sync_indicator.configure(text="🔄" if syncing else "⏸️")

class ModernOrdersView(ttk.Frame):
    def __init__(self, parent, on_filter_apply: Callable, **kwargs):
        super().__init__(parent, **kwargs)
        self.orders_data = []
        self.on_filter_apply = on_filter_apply
        self._create_widgets()

    def _create_widgets(self):
        header = ModernUIHelper.create_header_frame(self, "📊 Gestione Ordini")
        header.pack(fill='x', padx=10, pady=(10,5))
        
        # --- NUOVA BARRA FILTRI ---
        self._create_filter_bar()

        table_container = ttk.Frame(self, style='Card.TFrame', padding=10)
        table_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('id', 'customer', 'status', 'total', 'date', 'payment')
        self.tree = ttk.Treeview(table_container, columns=columns, show='headings')
        headings = {'id': 'ID Ordine', 'customer': 'Cliente', 'status': 'Stato', 'total': 'Totale', 'date': 'Data', 'payment': 'Pagamento'}
        widths = {'id': 100, 'customer': 250, 'status': 150, 'total': 120, 'date': 160, 'payment': 200}
        for col, text in headings.items(): self.tree.heading(col, text=text)
        for col, width in widths.items(): self.tree.column(col, width=width, anchor='w' if col != 'total' else 'e')
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind("<Double-1>", self._on_double_click)

    def _create_filter_bar(self):
        filter_frame = ttk.Frame(self, padding=(10, 5))
        filter_frame.pack(fill='x')

        # --- Campo di ricerca per testo ---
        ttk.Label(filter_frame, text="Cerca:").pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(0, 15))
        search_entry.bind("<Return>", lambda event: self.on_filter_apply())

        # --- Filtro per stato ---
        ttk.Label(filter_frame, text="Stato:").pack(side='left', padx=(0, 5))
        self.status_var = tk.StringVar()
        status_options = ["", "completed", "processing", "pending", "on-hold", "cancelled", "refunded", "failed"]
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var, values=status_options, state="readonly", width=15)
        status_combo.pack(side='left', padx=(0, 15))

        # --- Pulsanti ---
        apply_button = ttk.Button(filter_frame, text="Applica Filtri", command=self.on_filter_apply, style="Primary.TButton")
        apply_button.pack(side='left', padx=5)

        clear_button = ttk.Button(filter_frame, text="Pulisci", command=self._clear_filters)
        clear_button.pack(side='left', padx=5)

    def _clear_filters(self):
        self.search_var.set("")
        self.status_var.set("")
        self.on_filter_apply()
        
    def update_orders(self, orders: List[Dict]):
        self.orders_data = orders
        self.tree.delete(*self.tree.get_children())
        if orders:
            for order in orders: self._add_order_to_tree(order)
            
    def _on_double_click(self, event):
        if not self.tree.selection(): return
        item_id_text = self.tree.item(self.tree.selection()[0])['values'][0]
        order_id_str = item_id_text.replace('#', '').strip()
        if order_id_str.isdigit():
            self.selected_order_id = int(order_id_str)
            self.event_generate("<<ShowOrderDetails>>")
        else:
            self.selected_order_id = None

    def _add_order_to_tree(self, order: Dict):
        try:
            order_id = f"#{order.get('woo_id', 'N/D')}"
            billing = order.get('billing_data', {}) or {}
            customer_name = f"{billing.get('first_name', '')} {billing.get('last_name', '')}".strip() or billing.get('email', 'N/D')
            status_raw = order.get('status', 'n/d').lower()
            status_text = f"{GiteManiTheme.get_status_icon(status_raw)} {status_raw.capitalize()}"
            total_text = f"€ {float(order.get('total', 0.0)):,.2f}"
            date_created_raw = order.get('date_created', '')
            date_text = datetime.fromisoformat(date_created_raw.replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M') if date_created_raw else "N/D"
            payment_text = order.get('payment_method_title', 'N/D')
            values = (order_id, customer_name, status_text, total_text, date_text, payment_text)
            self.tree.insert('', 'end', values=values)
        except Exception as e:
            print(f"ERRORE: Impossibile aggiungere l'ordine #{order.get('woo_id')} alla tabella: {e}")
