#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Componenti GUI per Gestionale Gitemania (Versione Finale Stabile con Grafica Migliorata)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Callable, List
import json
from config import config
from theme_manager import GiteManiTheme # <-- Importa il tema

class SettingsPanel(ttk.Frame):
    def __init__(self, parent, *, current_config: Dict, on_save: Callable, on_test: Callable, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_save, self.on_test = on_save, on_test
        self._create_widgets(current_config)

    def _create_widgets(self, current_config: Dict):
        main_container = ttk.Frame(self, padding=20)
        main_container.pack(fill='both', expand=True)
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill='both', expand=True, pady=(0, 20))
        woo_frame = ttk.Frame(notebook, padding=15)
        notebook.add(woo_frame, text="🔌 WooCommerce")
        self._create_woocommerce_tab(woo_frame, current_config)
        buttons_frame = ttk.Frame(main_container)
        buttons_frame.pack(fill='x', side='bottom')
        ttk.Button(buttons_frame, text="✅ Salva Impostazioni", style='Success.TButton', command=self._on_save_click).pack(side='right')
        ttk.Button(buttons_frame, text="🔧 Test Connessioni", style='TButton', command=self.on_test).pack(side='left')

    def _create_woocommerce_tab(self, parent, config_data):
        ttk.Label(parent, text="URL Store:", font=("-weight", "bold")).grid(row=0, column=0, sticky='w')
        self.woo_url_var = tk.StringVar(value=config_data.get('woocommerce', {}).get('base_url', ''))
        ttk.Entry(parent, textvariable=self.woo_url_var).grid(row=1, column=0, sticky='ew', pady=5)
        ttk.Label(parent, text="Consumer Key:", font=("-weight", "bold")).grid(row=2, column=0, sticky='w')
        self.woo_key_var = tk.StringVar(value=config.get_encrypted('woocommerce', 'consumer_key', ''))
        ttk.Entry(parent, textvariable=self.woo_key_var, show='*').grid(row=3, column=0, sticky='ew', pady=5)
        ttk.Label(parent, text="Consumer Secret:", font=("-weight", "bold")).grid(row=4, column=0, sticky='w')
        self.woo_secret_var = tk.StringVar(value=config.get_encrypted('woocommerce', 'consumer_secret', ''))
        ttk.Entry(parent, textvariable=self.woo_secret_var, show='*').grid(row=5, column=0, sticky='ew')
        parent.grid_columnconfigure(0, weight=1)

    def _on_save_click(self):
        new_config = {'woocommerce': {'base_url': self.woo_url_var.get().strip()}}
        if self.woo_key_var.get().strip(): config.set_encrypted('woocommerce', 'consumer_key', self.woo_key_var.get().strip())
        if self.woo_secret_var.get().strip(): config.set_encrypted('woocommerce', 'consumer_secret', self.woo_secret_var.get().strip())
        if self.on_save: self.on_save(new_config)

class AboutDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Info su Gestionale Gitemania"); self.geometry("450x300"); self.resizable(False, False)
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)
        ttk.Label(main_frame, text="Gestionale Gitemania", font=("-size", 16, "-weight", "bold")).pack(pady=5)
        ttk.Label(main_frame, text="Versione 1.0").pack()
        ttk.Button(main_frame, text="Chiudi", command=self.destroy, style='Primary.TButton').pack(pady=20)

class OrderDetailWindow(tk.Toplevel):
    def __init__(self, parent, order: Dict):
        super().__init__(parent)
        self.title(f"Dettaglio Ordine #{order.get('number', '')}")
        self.geometry("800x650") # Leggermente più alta per la nuova grafica
        
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # --- Sezione Generale ---
        general_frame = ttk.LabelFrame(main_frame, text=" ℹ️ Generale", padding=10)
        general_frame.pack(fill='x', pady=(0, 5))
        ttk.Label(general_frame, text=f"Data: {order.get('date_created', 'N/D')} | Stato: {order.get('status', 'N/D')}").pack(anchor='w')
        
        # --- Sezione Fatturazione ---
        billing = order.get('billing_data', {})
        billing_frame = ttk.LabelFrame(main_frame, text=" 🧾 Fatturazione", padding=10)
        billing_frame.pack(fill='x', pady=5)
        billing_address = (f"{billing.get('first_name', '')} {billing.get('last_name', '')}\n"
                           f"Email: {billing.get('email', '')}\nTel: {billing.get('phone', '')}")
        ttk.Label(billing_frame, text=billing_address, justify='left').pack(anchor='w')

        # --- Sezione Dati Viaggiatori (NUOVA GRAFICA) ---
        travelers_container = ttk.LabelFrame(main_frame, text=" ✈️ Dati Viaggiatori", padding=10)
        travelers_container.pack(fill='both', expand=True, pady=5)
        
        # Crea un'area scrollabile
        canvas = tk.Canvas(travelers_container, borderwidth=0, highlightthickness=0, background=GiteManiTheme.COLORS['surface'])
        scrollbar = ttk.Scrollbar(travelers_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='TFrame')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Popola l'area scrollabile con le "card" dei viaggiatori
        self.populate_travelers_cards(scrollable_frame, order)

    def populate_travelers_cards(self, parent_frame, order: Dict):
        travelers_list = self._extract_traveler_data_as_list(order)
        
        if not travelers_list:
            ttk.Label(parent_frame, text="Nessun dato viaggiatore trovato.", padding=20).pack()
            return

        for i, traveler in enumerate(travelers_list, 1):
            # Card principale per ogni viaggiatore
            card = ttk.Frame(parent_frame, style='Card.TFrame', padding=0)
            card.pack(fill='x', expand=True, padx=5, pady=(5, 10))
            
            # --- Header della Card ---
            header_frame = ttk.Frame(card, style='Card.TFrame', padding=(12, 8))
            header_frame.pack(fill='x', expand=True)
            
            title_label = ttk.Label(
                header_frame,
                text=f"Viaggiatore {i}",
                font=GiteManiTheme.FONTS['subheading'],
                foreground=GiteManiTheme.COLORS['primary'], # Colore del brand
                style='Card.TLabel'
            )
            title_label.pack(side='left')
            
            ttk.Separator(card).pack(fill='x', padx=10)

            # --- Corpo della Card ---
            body_frame = ttk.Frame(card, style='Card.TFrame', padding=(15, 10))
            body_frame.pack(fill='both', expand=True)
            body_frame.columnconfigure(1, weight=1) # Permette al valore di espandersi

            row_index = 0
            
            def add_info_row(label, value, icon):
                nonlocal row_index
                if value:
                    # Etichetta (Icona + Testo)
                    label_widget = ttk.Label(
                        body_frame,
                        text=f"{icon} {label}:",
                        style='Card.TLabel',
                        font=GiteManiTheme.FONTS['default'] + ('bold',),
                        foreground=GiteManiTheme.COLORS['text_secondary'] # Colore grigio per etichette
                    )
                    label_widget.grid(row=row_index, column=0, sticky='nw', padx=(0, 15), pady=4)

                    # Valore (Dato)
                    value_widget = ttk.Label(
                        body_frame,
                        text=value,
                        style='Card.TLabel',
                        font=GiteManiTheme.FONTS['default'],
                        foreground=GiteManiTheme.COLORS['text'], # Colore scuro per i dati
                        wraplength=450,
                        justify='left'
                    )
                    value_widget.grid(row=row_index, column=1, sticky='w', pady=4)
                    row_index += 1

            # Aggiungi i dati del viaggiatore alla card
            nome_completo = f"{traveler.get('nome', '')} {traveler.get('cognome', '')}".strip()
            add_info_row("Nome Completo", nome_completo, "👤")
            add_info_row("Email", traveler.get('email'), "📧")
            add_info_row("Telefono", traveler.get('telefono'), "📞")
            add_info_row("Partenza", traveler.get('partenza'), "🚌")
            
            # Gestisce altri campi non standard in modo dinamico
            altri_dati = {k: v for k, v in traveler.items() if k not in ['nome', 'cognome', 'email', 'telefono', 'partenza']}
            if altri_dati:
                 ttk.Separator(body_frame).grid(row=row_index, column=0, columnspan=2, sticky='ew', pady=5)
                 row_index += 1
                 for key, value in altri_dati.items():
                    add_info_row(key.replace("_", " ").title(), str(value), "ℹ️")

    def _extract_traveler_data_as_list(self, order: Dict) -> List[Dict]:
        """
        Estrae i dati dei viaggiatori e li restituisce come una lista di dizionari.
        """
        meta_data = order.get('raw_data', {}).get('meta_data', [])
        possible_keys = ['dati_viaggiatori', '_dati_viaggiatori', 'traveler_data', '_traveler_data']
        
        for item in meta_data:
            key = item.get('key', '').lower()
            if key in possible_keys:
                value = item.get('value')
                if not value:
                    continue

                try:
                    if isinstance(value, str):
                        data = json.loads(value.replace('\\"', '"'))
                    else:
                        data = value
                    
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        return [data]
                        
                except (json.JSONDecodeError, TypeError):
                    return [{'Info': str(value)}]

        return []
