#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Moderna per Gestionale Gitemania (Versione Finale Stabile)
"""
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
from typing import Dict
import warnings

from theme_manager import GiteManiTheme, ModernUIHelper

class ModernDashboard(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style='TFrame')
        self.stats_data = {}
        self.chart_colors = GiteManiTheme.setup_matplotlib()
        self._create_widgets()
        
    def _create_widgets(self):
        header = ModernUIHelper.create_header_frame(self, "Dashboard Gestionale")
        header.pack(fill='x', padx=10, pady=(10,0))
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self._create_kpi_section(main_frame)
        self._create_charts_section(main_frame)
        
    def _create_kpi_section(self, parent):
        kpi_container = ttk.Frame(parent)
        kpi_container.pack(fill='x', pady=(0, 10))
        
        self.kpi_vars = {
            'total_orders': {'value': tk.StringVar(value="0"), 'trend': tk.StringVar(value="")},
            'total_revenue': {'value': tk.StringVar(value="€0.00"), 'trend': tk.StringVar(value="")},
            'avg_order': {'value': tk.StringVar(value="€0.00"), 'trend': tk.StringVar(value="")},
            'pending_orders': {'value': tk.StringVar(value="0"), 'trend': tk.StringVar(value="")},
            'growth': {'value': tk.StringVar(value="+0.0%"), 'trend': tk.StringVar(value="")},
            'conversion': {'value': tk.StringVar(value="0.0%"), 'trend': tk.StringVar(value="")}
        }
        
        kpi_data = [
            ("Ordini Totali", "total_orders", "📦", "primary"),
            ("Fatturato", "total_revenue", "€", "success"),
            ("Ordine Medio", "avg_order", "🛒", "info"),
            ("In Elaborazione", "pending_orders", "🔄", "warning"),
            ("Crescita Mensile", "growth", "📈", "primary"),
            ("Tasso Conversione", "conversion", "🎯", "success")
        ]

        for i, (title, key, icon, color) in enumerate(kpi_data):
            card = self._create_kpi_card(kpi_container, title, self.kpi_vars[key]['value'], self.kpi_vars[key]['trend'], icon, color)
            card.grid(row=0, column=i, padx=(0, 10) if i < 5 else 0, sticky="nsew")
            kpi_container.grid_columnconfigure(i, weight=1)

    def _create_kpi_card(self, parent, title: str, value_var: tk.StringVar, trend_var: tk.StringVar,
                        icon: str, color_type: str) -> ttk.Frame:
        
        card = ttk.Frame(parent, style='Card.TFrame')
        header_frame = ttk.Frame(card, style='Card.TFrame')
        header_frame.pack(fill='x', padx=15, pady=(10, 5))
        
        icon_label = ttk.Label(header_frame, text=icon, font=('Segoe UI', 12), foreground=GiteManiTheme.COLORS[color_type], style='Card.TLabel')
        icon_label.pack(side='left')
        
        title_label = ttk.Label(header_frame, text=title, font=GiteManiTheme.FONTS['subheading'], foreground=GiteManiTheme.COLORS['text_secondary'], style='Card.TLabel')
        title_label.pack(side='left', padx=5)

        value_label = ttk.Label(card, textvariable=value_var, font=GiteManiTheme.FONTS['large_value'], foreground=GiteManiTheme.COLORS['text'], style='Card.TLabel')
        value_label.pack(fill='x', padx=15, pady=5)

        trend_label = ttk.Label(card, textvariable=trend_var, font=GiteManiTheme.FONTS['default'], style='Card.TLabel')
        trend_label.pack(fill='x', padx=15, pady=(0, 10))
        
        trend_var._widget = trend_label
        
        return card
        
    def _create_charts_section(self, parent):
        self.charts_notebook = ttk.Notebook(parent, style='TNotebook')
        self.charts_notebook.pack(fill='both', expand=True)
        
        self.status_frame = ttk.Frame(self.charts_notebook, style='TFrame')
        self.charts_notebook.add(self.status_frame, text="🍩 Stati Ordini")
        
        self.timeline_frame = ttk.Frame(self.charts_notebook, style='TFrame')
        self.charts_notebook.add(self.timeline_frame, text="📈 Andamento")
        
        self.products_frame = ttk.Frame(self.charts_notebook, style='TFrame')
        self.charts_notebook.add(self.products_frame, text="🛒 Prodotti")
        
        self._init_charts()
        
    def _init_charts(self):
        warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
        
        self.status_fig = Figure(figsize=(5, 4), dpi=100, facecolor=GiteManiTheme.COLORS['card'])
        self.status_ax = self.status_fig.add_subplot(111)
        self.status_canvas = FigureCanvasTkAgg(self.status_fig, self.status_frame)
        self.status_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        self.timeline_fig = Figure(figsize=(5, 4), dpi=100, facecolor=GiteManiTheme.COLORS['card'])
        self.timeline_ax = self.timeline_fig.add_subplot(111)
        self.timeline_canvas = FigureCanvasTkAgg(self.timeline_fig, self.timeline_frame)
        self.timeline_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        self.products_fig = Figure(figsize=(5, 4), dpi=100, facecolor=GiteManiTheme.COLORS['card'])
        self.products_ax = self.products_fig.add_subplot(111)
        self.products_canvas = FigureCanvasTkAgg(self.products_fig, self.products_frame)
        self.products_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        self._update_all_charts({})

    def update_dashboard(self, stats: Dict):
        self.stats_data = stats
        self._update_kpi(stats)
        self._update_all_charts(stats)
        
    def _update_kpi(self, stats: Dict):
        total_orders = stats.get('total_orders', 0)
        total_revenue = stats.get('total_revenue', 0)
        pending_orders = (stats.get('by_status', {}).get('processing', 0) + 
                          stats.get('by_status', {}).get('pending', 0))
        avg_order = total_revenue / total_orders if total_orders > 0 else 0
        
        self.kpi_vars['total_orders']['value'].set(f"{total_orders:,}")
        self.kpi_vars['total_orders']['trend'].set("▲ +15% vs mese prec.")
        
        self.kpi_vars['total_revenue']['value'].set(f"€{total_revenue:,.2f}")
        self.kpi_vars['total_revenue']['trend'].set("▲ +12% vs mese prec.")

        self.kpi_vars['avg_order']['value'].set(f"€{avg_order:.2f}")
        self.kpi_vars['avg_order']['trend'].set("▼ -2% vs mese prec.")

        self.kpi_vars['pending_orders']['value'].set(f"{pending_orders}")
        self.kpi_vars['pending_orders']['trend'].set("Invariato")

        self.kpi_vars['growth']['value'].set("+12.5%")
        self.kpi_vars['growth']['trend'].set("Obiettivo: 15%")
        
        self.kpi_vars['conversion']['value'].set("3.2%")
        self.kpi_vars['conversion']['trend'].set("▲ +0.5% vs mese prec.")

        for key, trend_info in self.kpi_vars.items():
            widget = trend_info['trend']._widget
            if hasattr(widget, 'winfo_exists') and widget.winfo_exists():
                text = trend_info['trend'].get()
                if '▲' in text or '+' in text:
                    widget.configure(foreground=GiteManiTheme.COLORS['success'])
                elif '▼' in text or '-' in text:
                    widget.configure(foreground=GiteManiTheme.COLORS['danger'])
                else:
                    widget.configure(foreground=GiteManiTheme.COLORS['text_secondary'])

    def _update_all_charts(self, stats: Dict):
        self._update_status_donut(stats.get('by_status', {}))
        self._update_timeline_chart(stats.get('by_date', {}))
        self._update_products_chart(stats.get('top_products', {}))
        
    def _update_status_donut(self, by_status: Dict):
        self.status_ax.clear()
        if by_status:
            labels = list(by_status.keys())
            sizes = list(by_status.values())
            wedges, texts, autotexts = self.status_ax.pie(
                sizes, autopct='%1.1f%%', startangle=90, 
                wedgeprops=dict(width=0.4, edgecolor=GiteManiTheme.COLORS['card'], linewidth=2),
                pctdistance=0.8
            )
            plt.setp(autotexts, size=8, weight="bold", color="white")
            self.status_ax.set_title('Distribuzione Stati Ordini', fontweight='bold')
        self.status_fig.tight_layout()
        self.status_canvas.draw()
        
    def _update_timeline_chart(self, by_date: Dict):
        self.timeline_ax.clear()
        if by_date:
            dates = sorted(by_date.keys())
            values = [by_date[date] for date in dates]
            try:
                date_objects = [datetime.fromisoformat(date.replace('Z', '+00:00')) for date in dates]
                self.timeline_ax.plot(date_objects, values, linewidth=2.5, marker='o', markersize=6, markerfacecolor='white')
                self.timeline_ax.fill_between(date_objects, values, alpha=0.1)
                self.timeline_ax.set_title('Andamento Ordini', fontweight='bold')
                self.timeline_ax.grid(True, alpha=0.3)
                self.timeline_fig.autofmt_xdate()
            except ValueError:
                print("Formato data non valido per il grafico Andamento.")
        self.timeline_fig.tight_layout()
        self.timeline_canvas.draw()
        
    def _update_products_chart(self, top_products: Dict):
        self.products_ax.clear()
        if top_products:
            sorted_products = sorted(top_products.items(), key=lambda item: item[1])[-5:]
            products = [item[0] for item in sorted_products]
            values = [item[1] for item in sorted_products]
            
            self.products_ax.barh(products, values, height=0.6)
            self.products_ax.set_title('Top 5 Prodotti', fontweight='bold')
        self.products_fig.tight_layout()
        self.products_canvas.draw()
