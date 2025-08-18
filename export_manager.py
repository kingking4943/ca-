#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export Manager per Gestionale Gitemania PORTABLE
Gestisce export automatici CSV/DOCX con dettagli viaggiatori
Sviluppato da TechExpresso
"""

import os, csv, json, schedule, threading, time
from datetime import datetime
from typing import Dict, List
from config import config

class ExportResult:
    def __init__(self, success: bool, file_name: str = "", file_path: str = "", total_records: int = 0, error_message: str = ""):
        self.success = success
        self.file_name = file_name
        self.file_path = file_path
        self.total_records = total_records
        self.error_message = error_message

class ExportManager:
    def __init__(self, database_manager, on_export_complete=None):
        self.database_manager = database_manager
        self.on_export_complete = on_export_complete
        self.exports_dir = config.exports_dir
        os.makedirs(self.exports_dir, exist_ok=True)
        self.scheduler_running = False
        self.scheduler_thread = None

    @staticmethod
    def _extract_traveler_data(order: Dict) -> List[Dict]:
        meta_data = order.get('raw_data', {}).get('meta_data', [])
        possible_keys = ['dati_viaggiatori', '_dati_viaggiatori', 'traveler_data', '_traveler_data']
        for item in meta_data:
            key = item.get('key', '').lower()
            if key in possible_keys:
                value = item.get('value')
                if not value: continue
                try:
                    data = json.loads(value.replace('\\"', '"')) if isinstance(value, str) else value
                    if isinstance(data, list): return data
                    if isinstance(data, dict): return [data]
                except (json.JSONDecodeError, TypeError):
                    return [{'Info': str(value)}]
        return []

    def start_scheduler(self):
        # ... (codice invariato)
        pass

    def stop_scheduler(self):
        # ... (codice invariato)
        pass

    def _run_scheduler(self):
        # ... (codice invariato)
        pass

    def _daily_export(self):
        self.export_orders_csv()

    def export_orders_csv(self, filters: Dict = None):
        """ Esporta ordini in CSV. Se non ci sono filtri, esporta TUTTI gli ordini. """
        try:
            # Se i filtri sono presenti e non vuoti, usali. Altrimenti, None (per prendere tutto).
            final_filters = filters if filters else None
            
            print("\n--- AVVIO EXPORT ---")
            print("DEBUG: Export richiesto con i seguenti filtri:", final_filters)
            
            orders = self.database_manager.get_orders(final_filters)
            
            print(f"DEBUG: Il database ha restituito {len(orders)} ordini per l'export.")
            
            if not orders:
                result = ExportResult(success=False, error_message="Nessun ordine trovato con i filtri specificati.")
                if self.on_export_complete: self.on_export_complete(result)
                return

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"export_dettaglio_viaggiatori_{timestamp}.csv"
            file_path = os.path.join(self.exports_dir, filename)

            fieldnames = ['ID Ordine', 'Numero Ordine', 'Data Ordine', 'Cliente Principale', 'Email Cliente', 'Stato Ordine', 'Totale Ordine', 'Nome Viaggiatore', 'Cognome Viaggiatore', 'Email Viaggiatore', 'Telefono Viaggiatore', 'Partenza Viaggiatore', 'Prodotti', 'Metodo Pagamento']
            
            rows_to_write = []
            for order in orders:
                common_info = {'ID Ordine': order.get('woo_id', ''), 'Numero Ordine': order.get('order_number', ''), 'Data Ordine': order.get('date_created', ''), 'Cliente Principale': order.get('customer_name', ''), 'Email Cliente': order.get('customer_email', ''), 'Stato Ordine': order.get('status', ''), 'Totale Ordine': order.get('total', 0), 'Metodo Pagamento': order.get('payment_method_title', '')}
                line_items = json.loads(order['line_items']) if isinstance(order.get('line_items'), str) else order.get('line_items', [])
                common_info['Prodotti'] = '; '.join([f"{item.get('name', 'N/A')} (x{item.get('quantity', 0)})" for item in line_items])
                travelers = self._extract_traveler_data(order)

                if travelers:
                    for traveler in travelers:
                        row = common_info.copy()
                        row.update({'Nome Viaggiatore': traveler.get('nome', ''), 'Cognome Viaggiatore': traveler.get('cognome', ''), 'Email Viaggiatore': traveler.get('email', ''), 'Telefono Viaggiatore': traveler.get('telefono', ''), 'Partenza Viaggiatore': traveler.get('partenza', '')})
                        rows_to_write.append(row)
                else:
                    row = common_info.copy()
                    row.update({'Nome Viaggiatore': '', 'Cognome Viaggiatore': '', 'Email Viaggiatore': '', 'Telefono Viaggiatore': '', 'Partenza Viaggiatore': ''})
                    rows_to_write.append(row)
            
            print(f"DEBUG: Sto per scrivere {len(rows_to_write)} righe nel file CSV...")
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames); writer.writeheader(); writer.writerows(rows_to_write)
                
            result = ExportResult(success=True, file_name=filename, file_path=file_path, total_records=len(rows_to_write))
            if self.on_export_complete: self.on_export_complete(result)
            print("--- EXPORT COMPLETATO ---")

        except Exception as e:
            error_msg = f"Errore durante l'export CSV: {e}"
            result = ExportResult(success=False, error_message=error_msg)
            if self.on_export_complete: self.on_export_complete(result)
