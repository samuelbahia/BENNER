#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de HTML Interativo para o Dicionário de Dados BENNER
Cria um arquivo HTML único (self-contained) com dashboard e visualizações
"""

import json
import os
from datetime import datetime
from parser_dicionario import parse_data_dictionary, build_statistics, MODULE_PREFIXES

def generate_html(tables: dict, stats: dict, output_path: str):
    """Gera arquivo HTML interativo self-contained"""
    
    # Converter para JSON para embedding no HTML
    tables_json = json.dumps(tables, ensure_ascii=False)
    stats_json = json.dumps(stats, ensure_ascii=False)
    modules_json = json.dumps(MODULE_PREFIXES, ensure_ascii=False)
    
    html_template = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dicionário de Dados BENNER - Visualizador Interativo</title>
    <style>
        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary: #64748b;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg-main: #f8fafc;
            --bg-card: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border: #e2e8f0;
            --shadow: 0 1px 3px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: var(--bg-main);
            color: var(--text-primary);
            line-height: 1.5;
        }
        
        /* Header */
        header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            color: white;
            padding: 1.5rem 2rem;
            box-shadow: var(--shadow-lg);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        header h1 {
            font-size: 1.75rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }
        
        header p {
            opacity: 0.9;
            font-size: 0.9rem;
        }
        
        /* Layout */
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 1.5rem;
        }
        
        .main-layout {
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 1.5rem;
            min-height: calc(100vh - 120px);
        }
        
        /* Sidebar */
        .sidebar {
            background: var(--bg-card);
            border-radius: 12px;
            box-shadow: var(--shadow);
            padding: 1rem;
            height: fit-content;
            position: sticky;
            top: 100px;
            max-height: calc(100vh - 120px);
            overflow-y: auto;
        }
        
        .search-box {
            position: relative;
            margin-bottom: 1rem;
        }
        
        .search-box input {
            width: 100%;
            padding: 0.75rem 1rem 0.75rem 2.5rem;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 0.9rem;
            transition: all 0.2s;
        }
        
        .search-box input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        
        .search-box::before {
            content: "🔍";
            position: absolute;
            left: 0.75rem;
            top: 50%;
            transform: translateY(-50%);
        }
        
        /* Module Filter */
        .module-filter {
            margin-bottom: 1rem;
        }
        
        .module-filter select {
            width: 100%;
            padding: 0.5rem;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 0.9rem;
            background: white;
            cursor: pointer;
        }
        
        /* Table List */
        .table-list {
            max-height: 500px;
            overflow-y: auto;
        }
        
        .table-item {
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.15s;
            font-size: 0.85rem;
        }
        
        .table-item:hover {
            background: var(--bg-main);
        }
        
        .table-item.active {
            background: var(--primary);
            color: white;
        }
        
        .table-item .module-badge {
            font-size: 0.65rem;
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            background: var(--border);
            color: var(--text-secondary);
            font-weight: 600;
        }
        
        .table-item.active .module-badge {
            background: rgba(255,255,255,0.2);
            color: white;
        }
        
        /* Main Content */
        .main-content {
            background: var(--bg-card);
            border-radius: 12px;
            box-shadow: var(--shadow);
            padding: 1.5rem;
        }
        
        /* Dashboard */
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: linear-gradient(135deg, var(--bg-main) 0%, white 100%);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 1.25rem;
            text-align: center;
        }
        
        .stat-card .value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
        }
        
        .stat-card .label {
            color: var(--text-secondary);
            font-size: 0.85rem;
            margin-top: 0.25rem;
        }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 0.5rem;
            border-bottom: 2px solid var(--border);
            margin-bottom: 1.5rem;
        }
        
        .tab {
            padding: 0.75rem 1.25rem;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--text-secondary);
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            transition: all 0.2s;
        }
        
        .tab:hover {
            color: var(--primary);
        }
        
        .tab.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Table Detail */
        .table-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid var(--border);
        }
        
        .table-header h2 {
            font-size: 1.5rem;
            color: var(--text-primary);
        }
        
        .table-header .badge {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .badge-module {
            background: var(--primary);
            color: white;
        }
        
        .badge-count {
            background: var(--success);
            color: white;
        }
        
        /* Fields Table */
        .fields-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .fields-table th,
        .fields-table td {
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        
        .fields-table th {
            background: var(--bg-main);
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            color: var(--text-secondary);
        }
        
        .fields-table tr:hover {
            background: var(--bg-main);
        }
        
        .type-badge {
            display: inline-block;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .type-Integer { background: #dbeafe; color: #1d4ed8; }
        .type-Varchar { background: #dcfce7; color: #15803d; }
        .type-Char { background: #fef3c7; color: #b45309; }
        .type-Number { background: #fce7f3; color: #be185d; }
        .type-Blob { background: #f3e8ff; color: #7c3aed; }
        .type-Date { background: #ffedd5; color: #c2410c; }
        .type-Unknown { background: #f1f5f9; color: #64748b; }
        
        .fk-link {
            color: var(--primary);
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
        }
        
        .fk-link:hover {
            text-decoration: underline;
        }
        
        /* Relationships */
        .relationship-card {
            background: var(--bg-main);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .relationship-card .arrow {
            font-size: 1.5rem;
            color: var(--primary);
        }
        
        /* ER Diagram */
        .er-diagram {
            background: var(--bg-main);
            border-radius: 8px;
            padding: 1rem;
            min-height: 400px;
            position: relative;
            overflow: auto;
        }
        
        .er-diagram svg {
            width: 100%;
            height: 100%;
        }
        
        .er-table {
            fill: white;
            stroke: var(--border);
            stroke-width: 2;
        }
        
        .er-table-header {
            fill: var(--primary);
        }
        
        .er-text {
            font-family: inherit;
            font-size: 12px;
        }
        
        .er-text-header {
            fill: white;
            font-weight: bold;
        }
        
        .er-line {
            stroke: var(--secondary);
            stroke-width: 1.5;
            fill: none;
        }
        
        /* Charts */
        .chart-container {
            background: var(--bg-main);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        
        .chart-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--text-primary);
        }
        
        .bar-chart {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .bar-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .bar-label {
            min-width: 100px;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }
        
        .bar-track {
            flex: 1;
            height: 24px;
            background: var(--border);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .bar-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary), var(--primary-dark));
            border-radius: 4px;
            display: flex;
            align-items: center;
            padding-left: 0.5rem;
            color: white;
            font-size: 0.75rem;
            font-weight: 600;
            min-width: 30px;
        }
        
        /* Breadcrumb */
        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
            font-size: 0.85rem;
            color: var(--text-secondary);
        }
        
        .breadcrumb a {
            color: var(--primary);
            text-decoration: none;
        }
        
        .breadcrumb a:hover {
            text-decoration: underline;
        }
        
        /* Export Buttons */
        .export-buttons {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 6px;
            font-size: 0.85rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: var(--primary);
            color: white;
        }
        
        .btn-primary:hover {
            background: var(--primary-dark);
        }
        
        .btn-secondary {
            background: var(--bg-main);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }
        
        .btn-secondary:hover {
            background: var(--border);
        }
        
        /* Lineage View */
        .lineage-container {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .lineage-section {
            background: var(--bg-main);
            border-radius: 8px;
            padding: 1rem;
        }
        
        .lineage-section h4 {
            color: var(--text-secondary);
            font-size: 0.85rem;
            margin-bottom: 0.75rem;
            text-transform: uppercase;
        }
        
        .lineage-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .lineage-item {
            background: white;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            border: 1px solid var(--border);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .lineage-item:hover {
            border-color: var(--primary);
            color: var(--primary);
        }
        
        /* Welcome */
        .welcome {
            text-align: center;
            padding: 4rem 2rem;
        }
        
        .welcome h2 {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: var(--text-primary);
        }
        
        .welcome p {
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto 2rem;
        }

        /* Query Builder */
        .qb-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .qb-header p {
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }

        .qb-layout {
            display: grid;
            grid-template-columns: minmax(280px, 340px) 1fr;
            gap: 1.5rem;
        }

        .qb-sidebar,
        .qb-content {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .qb-panel {
            background: var(--bg-main);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 1rem;
        }

        .qb-panel h3,
        .qb-panel h4 {
            margin-bottom: 0.75rem;
        }

        .qb-search-input,
        .qb-join-select,
        .qb-limit-input {
            width: 100%;
            padding: 0.65rem 0.75rem;
            border: 2px solid var(--border);
            border-radius: 8px;
            font-size: 0.9rem;
            background: white;
        }

        .qb-search-input:focus,
        .qb-join-select:focus,
        .qb-limit-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .qb-table-list {
            max-height: 520px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .qb-table-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.65rem 0.75rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: white;
        }

        .qb-table-item input,
        .qb-field-item input,
        .qb-relationship-item input,
        .qb-limit-option input {
            width: 16px;
            height: 16px;
            accent-color: var(--primary);
            flex-shrink: 0;
        }

        .qb-table-item label,
        .qb-field-item label,
        .qb-relationship-item label {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
            width: 100%;
        }

        .qb-table-item-main {
            display: flex;
            flex-direction: column;
            min-width: 0;
        }

        .qb-table-item strong,
        .qb-field-item strong {
            word-break: break-word;
        }

        .qb-table-meta,
        .qb-help-text,
        .qb-relationship-meta,
        .qb-diagram-note {
            color: var(--text-secondary);
            font-size: 0.8rem;
        }

        .qb-selected-tables,
        .qb-relationships-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .qb-table-card {
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 1rem;
            background: white;
        }

        .qb-card-header,
        .qb-card-actions,
        .qb-actions-row,
        .qb-option-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            flex-wrap: wrap;
        }

        .qb-card-header {
            margin-bottom: 0.75rem;
        }

        .qb-card-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .qb-fields-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.5rem 1rem;
            margin-top: 0.75rem;
        }

        .qb-field-item {
            padding: 0.4rem 0;
            border-bottom: 1px dashed var(--border);
        }

        .qb-field-type {
            color: var(--text-secondary);
            font-size: 0.75rem;
        }

        .qb-relationship-item {
            background: white;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.85rem 0.9rem;
        }

        .qb-sql-output {
            background: #0f172a;
            color: #e2e8f0;
            border-radius: 10px;
            padding: 1rem;
            min-height: 220px;
            overflow: auto;
        }

        .qb-sql-output pre {
            margin: 0;
            white-space: pre-wrap;
            word-break: break-word;
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 0.88rem;
        }

        .qb-warning,
        .qb-info-box {
            border-radius: 8px;
            padding: 0.85rem 1rem;
            font-size: 0.85rem;
        }

        .qb-warning {
            background: #fff7ed;
            color: #9a3412;
            border: 1px solid #fdba74;
        }

        .qb-info-box {
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
        }

        .qb-diagram {
            background: var(--bg-main);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 1rem;
            min-height: 320px;
            overflow: auto;
        }

        .qb-diagram svg {
            width: 100%;
            height: auto;
        }

        .qb-diagram-meta {
            margin-top: 0.75rem;
        }

        .qb-empty-small {
            color: var(--text-secondary);
            font-size: 0.85rem;
            padding: 0.5rem 0;
        }
        
        /* Responsive */
        @media (max-width: 1024px) {
            .main-layout {
                grid-template-columns: 1fr;
            }
            
            .sidebar {
                position: static;
                max-height: none;
            }

            .qb-layout {
                grid-template-columns: 1fr;
            }
        }
        
        /* Print styles */
        @media print {
            header { position: static; }
            .sidebar { display: none; }
            .main-layout { grid-template-columns: 1fr; }
            .btn { display: none; }
        }
        
        /* Empty state */
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: var(--text-secondary);
        }
        
        .empty-state svg {
            width: 80px;
            height: 80px;
            margin-bottom: 1rem;
            opacity: 0.5;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-main);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--secondary);
        }
        
        /* Tooltip */
        [data-tooltip] {
            position: relative;
        }
        
        [data-tooltip]:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            padding: 0.5rem;
            background: var(--text-primary);
            color: white;
            font-size: 0.75rem;
            border-radius: 4px;
            white-space: nowrap;
            z-index: 100;
        }
        
        /* Null indicator */
        .nullable {
            color: var(--warning);
            font-size: 0.75rem;
        }
        
        .not-nullable {
            color: var(--success);
            font-size: 0.75rem;
        }
    </style>
</head>
<body>
    <header>
        <h1>📊 Dicionário de Dados BENNER</h1>
        <p>Visualizador Interativo de Estrutura de Banco de Dados</p>
    </header>
    
    <div class="container">
        <div class="main-layout">
            <!-- Sidebar -->
            <aside class="sidebar">
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Buscar tabelas, campos..." autocomplete="off">
                </div>
                
                <div class="module-filter">
                    <select id="moduleFilter">
                        <option value="">Todos os Módulos</option>
                    </select>
                </div>
                
                <div class="table-list" id="tableList">
                    <!-- Lista de tabelas será preenchida via JS -->
                </div>
            </aside>
            
            <!-- Main Content -->
            <main class="main-content" id="mainContent">
                <!-- Dashboard inicial -->
                <div id="dashboard">
                    <h2 style="margin-bottom: 1.5rem;">📈 Dashboard</h2>
                    
                    <div class="export-buttons" style="margin-bottom: 1.5rem;">
                        <button class="btn btn-primary" onclick="qbShowBuilder()">🛠️ Construtor de Query SQL</button>
                        <button class="btn btn-primary" onclick="exportAllExcel()">📊 Exportar Excel Completo</button>
                        <button class="btn btn-secondary" onclick="exportModulesExcel()">📋 Índice de Tabelas</button>
                        <button class="btn btn-secondary" onclick="exportRelationshipsExcel()">🔗 Relacionamentos</button>
                        <button class="btn btn-secondary" onclick="exportAllJSON()">📄 Exportar JSON</button>
                    </div>
                    
                    <div class="dashboard" id="statsCards">
                        <!-- Stats serão preenchidos via JS -->
                    </div>
                    
                    <div class="chart-container">
                        <h3 class="chart-title">📦 Tabelas por Módulo</h3>
                        <div class="bar-chart" id="moduleChart"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h3 class="chart-title">🔢 Tipos de Campos</h3>
                        <div class="bar-chart" id="typesChart"></div>
                    </div>
                    
                    <div class="chart-container">
                        <h3 class="chart-title">🔗 Tabelas Mais Referenciadas</h3>
                        <div class="bar-chart" id="referencedChart"></div>
                    </div>
                </div>

                <!-- Query Builder -->
                <div id="queryBuilderView" style="display: none;">
                    <div class="breadcrumb">
                        <a href="#" onclick="showDashboard(); return false;">Dashboard</a>
                        <span>›</span>
                        <span>Construtor de Query SQL</span>
                    </div>

                    <div class="qb-header">
                        <div>
                            <h2>🛠️ Construtor de Query SQL</h2>
                            <p>Selecione tabelas, campos e relacionamentos existentes no dicionário para montar um SQL Oracle com aliases, JOINs automáticos e diagrama ER offline.</p>
                        </div>
                        <div class="qb-actions-row">
                            <button class="btn btn-secondary" onclick="showDashboard()">← Voltar ao Dashboard</button>
                            <button class="btn btn-secondary" onclick="qbClearAll()">🧹 Limpar tudo</button>
                        </div>
                    </div>

                    <div class="qb-layout">
                        <section class="qb-sidebar">
                            <div class="qb-panel">
                                <div class="qb-card-actions" style="margin-bottom: 0.75rem;">
                                    <h3>📚 Tabelas</h3>
                                    <span class="qb-help-text" id="qbSelectedCount">0 selecionadas</span>
                                </div>
                                <input type="text" id="qbTableFilter" class="qb-search-input" placeholder="Buscar por tabela, módulo ou descrição..." autocomplete="off">
                                <p class="qb-help-text" style="margin: 0.75rem 0 0.5rem;">As tabelas aparecem em ordem alfabética. Ao marcar uma tabela, todos os campos são selecionados por padrão.</p>
                                <div class="qb-table-list" id="qbTableList"></div>
                            </div>
                        </section>

                        <section class="qb-content">
                            <div class="qb-panel">
                                <div class="qb-option-row">
                                    <div>
                                        <h3>⚙️ Opções</h3>
                                        <p class="qb-help-text">Se nenhum campo permanecer marcado em uma tabela, o SQL usa o alias com <code>*</code> para essa tabela.</p>
                                    </div>
                                    <div style="min-width: 220px;">
                                        <label for="qbJoinType" class="qb-help-text" style="display: block; margin-bottom: 0.35rem;">Tipo padrão de JOIN</label>
                                        <select id="qbJoinType" class="qb-join-select">
                                            <option value="INNER JOIN">INNER JOIN</option>
                                            <option value="LEFT JOIN">LEFT JOIN</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div class="qb-panel">
                                <h3>🧩 Campos selecionados por tabela</h3>
                                <div id="qbSelectedTables" class="qb-selected-tables"></div>
                            </div>

                            <div class="qb-panel">
                                <div class="qb-card-header">
                                    <div>
                                        <h3>🔗 Relacionamentos detectados</h3>
                                        <p class="qb-help-text">Somente relacionamentos existentes em <code>fields.fk_table</code> / <code>relationships</code> são considerados. Tabelas sem conexão entram como <code>CROSS JOIN</code>.</p>
                                    </div>
                                </div>
                                <div id="qbRelationshipWarning" style="display: none;"></div>
                                <div id="qbRelationshipsList" class="qb-relationships-list"></div>
                            </div>

                            <div class="qb-panel">
                                <div class="qb-card-header">
                                    <div>
                                        <h3>🧾 SQL Oracle gerado</h3>
                                        <p class="qb-help-text">Aliases são atribuídos como <code>T1</code>, <code>T2</code>... sem usar <code>AS</code>.</p>
                                    </div>
                                    <div class="qb-actions-row">
                                        <button class="btn btn-secondary" onclick="qbCopySQL()">📋 Copiar SQL</button>
                                        <button class="btn btn-secondary" onclick="qbDownloadSQL()">💾 Baixar .sql</button>
                                    </div>
                                </div>
                                <div class="qb-sql-output">
                                    <pre id="qbSqlOutput">-- Selecione pelo menos uma tabela para gerar o SQL.</pre>
                                </div>
                            </div>

                            <div class="qb-panel">
                                <div class="qb-card-header">
                                    <div>
                                        <h3>🎨 Diagrama ER dos relacionamentos selecionados</h3>
                                        <p class="qb-diagram-note">O diagrama mostra apenas um subconjunto de campos (PK, FKs selecionadas e alguns campos adicionais) para manter a leitura leve.</p>
                                    </div>
                                </div>
                                <div id="qbDiagram" class="qb-diagram"></div>
                                <div id="qbDiagramMeta" class="qb-diagram-meta qb-help-text"></div>
                            </div>
                        </section>
                    </div>
                </div>
                
                <!-- Table Detail (hidden initially) -->
                <div id="tableDetail" style="display: none;">
                    <div class="breadcrumb">
                        <a href="#" onclick="showDashboard()">Dashboard</a>
                        <span>›</span>
                        <span id="breadcrumbModule"></span>
                        <span>›</span>
                        <span id="breadcrumbTable"></span>
                    </div>
                    
                    <div class="table-header">
                        <h2 id="tableName"></h2>
                        <span class="badge badge-module" id="tableModule"></span>
                        <span class="badge badge-count" id="tableFieldCount"></span>
                    </div>
                    
                    <p id="tableDescription" style="margin-bottom: 1rem; color: var(--text-secondary);"></p>
                    
                    <div class="export-buttons">
                        <button class="btn btn-primary" onclick="exportTableExcel()">📊 Exportar Excel</button>
                        <button class="btn btn-secondary" onclick="exportTableJSON()">📄 Exportar JSON</button>
                        <button class="btn btn-secondary" onclick="exportTableDBML()">📐 Exportar DBML</button>
                        <button class="btn btn-secondary" onclick="window.print()">🖨️ Imprimir</button>
                    </div>
                    
                    <div class="tabs">
                        <button class="tab active" data-tab="fields">📋 Campos</button>
                        <button class="tab" data-tab="relationships">🔗 Relacionamentos</button>
                        <button class="tab" data-tab="lineage">📊 Lineage</button>
                        <button class="tab" data-tab="diagram">🎨 Diagrama</button>
                    </div>
                    
                    <!-- Fields Tab -->
                    <div class="tab-content active" id="tab-fields">
                        <table class="fields-table">
                            <thead>
                                <tr>
                                    <th>Campo</th>
                                    <th>Tipo</th>
                                    <th>Null</th>
                                    <th>Descrição</th>
                                    <th>FK</th>
                                </tr>
                            </thead>
                            <tbody id="fieldsBody">
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Relationships Tab -->
                    <div class="tab-content" id="tab-relationships">
                        <div id="relationshipsContainer"></div>
                    </div>
                    
                    <!-- Lineage Tab -->
                    <div class="tab-content" id="tab-lineage">
                        <div class="lineage-container">
                            <div class="lineage-section">
                                <h4>⬆️ Depende de (referencia)</h4>
                                <div class="lineage-list" id="dependsOn"></div>
                            </div>
                            <div class="lineage-section">
                                <h4>⬇️ Dependentes (referenciada por)</h4>
                                <div class="lineage-list" id="dependents"></div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Diagram Tab -->
                    <div class="tab-content" id="tab-diagram">
                        <div class="er-diagram" id="erDiagram"></div>
                    </div>
                </div>
            </main>
        </div>
    </div>
    
    <script>
        // Dados incorporados
        const TABLES = ''' + tables_json + ''';
        const STATS = ''' + stats_json + ''';
        const MODULES = ''' + modules_json + ''';
        
        // Estado da aplicação
        let currentTable = null;
        let filteredTables = Object.keys(TABLES).sort();
        const qbState = {
            visible: false,
            tableFilter: '',
            selectedTables: [],
            selectedFields: {},
            availableJoins: [],
            joinSelection: {},
            joinType: 'INNER JOIN',
            generatedSQL: ''
        };
        
        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {
            initModuleFilter();
            renderTableList();
            renderDashboard();
            qbInit();
            setupEventListeners();
        });
        
        function initModuleFilter() {
            const select = document.getElementById('moduleFilter');
            const moduleGroups = {};
            
            Object.values(TABLES).forEach(table => {
                const module = table.module;
                if (!moduleGroups[module]) {
                    moduleGroups[module] = 0;
                }
                moduleGroups[module]++;
            });
            
            const sortedModules = Object.entries(moduleGroups)
                .sort((a, b) => b[1] - a[1]);
            
            sortedModules.forEach(([module, count]) => {
                const option = document.createElement('option');
                option.value = module;
                option.textContent = `${module} - ${MODULES[module] || module} (${count})`;
                select.appendChild(option);
            });
        }
        
        function renderTableList() {
            const container = document.getElementById('tableList');
            container.innerHTML = '';
            
            filteredTables.forEach(tableName => {
                const table = TABLES[tableName];
                const item = document.createElement('div');
                item.className = 'table-item' + (currentTable === tableName ? ' active' : '');
                item.innerHTML = `
                    <span class="module-badge">${table.module}</span>
                    <span>${tableName}</span>
                `;
                item.onclick = () => selectTable(tableName);
                container.appendChild(item);
            });
        }
        
        function renderDashboard() {
            // Stats cards
            const statsHtml = `
                <div class="stat-card">
                    <div class="value">${STATS.total_tables.toLocaleString()}</div>
                    <div class="label">Tabelas</div>
                </div>
                <div class="stat-card">
                    <div class="value">${STATS.total_fields.toLocaleString()}</div>
                    <div class="label">Campos</div>
                </div>
                <div class="stat-card">
                    <div class="value">${STATS.total_relationships.toLocaleString()}</div>
                    <div class="label">Relacionamentos</div>
                </div>
                <div class="stat-card">
                    <div class="value">${Object.keys(STATS.tables_by_module).length}</div>
                    <div class="label">Módulos</div>
                </div>
            `;
            document.getElementById('statsCards').innerHTML = statsHtml;
            
            // Module chart
            const moduleChart = document.getElementById('moduleChart');
            const maxModuleCount = Math.max(...Object.values(STATS.tables_by_module));
            moduleChart.innerHTML = Object.entries(STATS.tables_by_module)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 15)
                .map(([module, count]) => `
                    <div class="bar-item">
                        <span class="bar-label">${module}</span>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: ${(count / maxModuleCount) * 100}%">${count}</div>
                        </div>
                    </div>
                `).join('');
            
            // Types chart
            const typesChart = document.getElementById('typesChart');
            const maxTypeCount = Math.max(...Object.values(STATS.fields_by_type));
            typesChart.innerHTML = Object.entries(STATS.fields_by_type)
                .sort((a, b) => b[1] - a[1])
                .map(([type, count]) => `
                    <div class="bar-item">
                        <span class="bar-label">${type}</span>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: ${(count / maxTypeCount) * 100}%">${count.toLocaleString()}</div>
                        </div>
                    </div>
                `).join('');
            
            // Referenced tables chart
            const referencedChart = document.getElementById('referencedChart');
            const maxRefCount = Math.max(...Object.values(STATS.most_referenced_tables));
            referencedChart.innerHTML = Object.entries(STATS.most_referenced_tables)
                .map(([table, count]) => `
                    <div class="bar-item">
                        <span class="bar-label" style="min-width: 200px; cursor: pointer;" onclick="selectTable('${table}')">${table}</span>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: ${(count / maxRefCount) * 100}%">${count}</div>
                        </div>
                    </div>
                `).join('');
        }

        function qbInit() {
            const joinTypeSelect = document.getElementById('qbJoinType');
            const filterInput = document.getElementById('qbTableFilter');

            if (joinTypeSelect) {
                joinTypeSelect.value = qbState.joinType;
                joinTypeSelect.addEventListener('change', function() {
                    qbState.joinType = this.value;
                    qbRefreshOutputs();
                });
            }

            if (filterInput) {
                filterInput.addEventListener('input', function() {
                    qbState.tableFilter = this.value || '';
                    qbRenderTableList();
                });
            }

            qbRenderTableList();
            qbRenderSelectedTables();
            qbRenderRelationships();
            qbRefreshOutputs();
        }

        function qbShowBuilder() {
            qbState.visible = true;
            document.getElementById('dashboard').style.display = 'none';
            document.getElementById('tableDetail').style.display = 'none';
            document.getElementById('queryBuilderView').style.display = 'block';
            qbRenderTableList();
            qbRenderSelectedTables();
            qbRenderRelationships();
            qbRefreshOutputs();
        }

        function qbGetSelectedTableSet() {
            return new Set(qbState.selectedTables);
        }

        function qbEscapeHTML(value) {
            return String(value ?? '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        function qbGetFilteredTables() {
            const query = qbState.tableFilter.trim().toLowerCase();
            return Object.keys(TABLES).sort().filter(tableName => {
                if (!query) return true;
                const table = TABLES[tableName];
                return [
                    tableName,
                    table.module || '',
                    table.module_name || '',
                    table.description || ''
                ].some(value => String(value).toLowerCase().includes(query));
            });
        }

        function qbRenderTableList() {
            const container = document.getElementById('qbTableList');
            const counter = document.getElementById('qbSelectedCount');
            const selectedSet = qbGetSelectedTableSet();
            const tableNames = qbGetFilteredTables();

            counter.textContent = `${qbState.selectedTables.length} selecionada(s)`;

            if (!tableNames.length) {
                container.innerHTML = '<div class="empty-state">Nenhuma tabela encontrada para o filtro informado.</div>';
                return;
            }

            container.innerHTML = tableNames.map(tableName => {
                const table = TABLES[tableName];
                return `
                    <div class="qb-table-item">
                        <label>
                            <input type="checkbox" data-qb-table="${qbEscapeHTML(tableName)}" ${selectedSet.has(tableName) ? 'checked' : ''}>
                            <span class="module-badge">${qbEscapeHTML(table.module || '-')}</span>
                            <span class="qb-table-item-main">
                                <strong>${qbEscapeHTML(tableName)}</strong>
                                <span class="qb-table-meta">${qbEscapeHTML(table.module_name || table.description || '')}</span>
                            </span>
                        </label>
                    </div>
                `;
            }).join('');

            container.querySelectorAll('input[data-qb-table]').forEach(input => {
                input.addEventListener('change', function() {
                    qbToggleTable(this.dataset.qbTable, this.checked);
                });
            });
        }

        function qbToggleTable(tableName, shouldSelect) {
            if (!TABLES[tableName]) return;

            const alreadySelected = qbState.selectedTables.includes(tableName);
            if (shouldSelect && !alreadySelected) {
                qbState.selectedTables.push(tableName);
                qbState.selectedFields[tableName] = new Set(TABLES[tableName].fields.map(field => field.name));
            } else if (!shouldSelect && alreadySelected) {
                qbState.selectedTables = qbState.selectedTables.filter(name => name !== tableName);
                delete qbState.selectedFields[tableName];
            }

            qbRefreshSelection();
        }

        function qbSetAllFields(tableName, shouldSelectAll) {
            if (!TABLES[tableName]) return;
            qbState.selectedFields[tableName] = shouldSelectAll
                ? new Set(TABLES[tableName].fields.map(field => field.name))
                : new Set();
            qbRenderSelectedTables();
            qbRefreshOutputs();
        }

        function qbToggleField(tableName, fieldName, shouldSelect) {
            if (!TABLES[tableName]) return;
            if (!qbState.selectedFields[tableName]) {
                qbState.selectedFields[tableName] = new Set();
            }

            if (shouldSelect) {
                qbState.selectedFields[tableName].add(fieldName);
            } else {
                qbState.selectedFields[tableName].delete(fieldName);
            }

            qbRenderSelectedTables();
            qbRefreshOutputs();
        }

        function qbRefreshSelection() {
            qbDetectJoins();
            qbRenderTableList();
            qbRenderSelectedTables();
            qbRenderRelationships();
            qbRefreshOutputs();
        }

        function qbDetectJoins() {
            const selectedSet = qbGetSelectedTableSet();
            const joinsMap = new Map();

            qbState.selectedTables.forEach(tableName => {
                const table = TABLES[tableName];
                if (!table) return;

                table.fields.forEach(field => {
                    if (field.fk_table && selectedSet.has(field.fk_table) && TABLES[field.fk_table]) {
                        const joinId = `${tableName}|${field.name}|${field.fk_table}`;
                        joinsMap.set(joinId, {
                            id: joinId,
                            source_table: tableName,
                            target_table: field.fk_table,
                            field: field.name,
                            references_field: 'HANDLE'
                        });
                    }
                });

                (table.relationships || []).forEach(rel => {
                    if (!rel.references_table || !selectedSet.has(rel.references_table) || !TABLES[rel.references_table]) {
                        return;
                    }

                    const joinId = `${tableName}|${rel.field}|${rel.references_table}`;
                    if (!joinsMap.has(joinId)) {
                        joinsMap.set(joinId, {
                            id: joinId,
                            source_table: tableName,
                            target_table: rel.references_table,
                            field: rel.field,
                            references_field: rel.references_field || 'HANDLE'
                        });
                    }
                });
            });

            qbState.availableJoins = Array.from(joinsMap.values()).sort((a, b) => {
                const tableCompare = a.source_table.localeCompare(b.source_table);
                if (tableCompare !== 0) return tableCompare;
                const targetCompare = a.target_table.localeCompare(b.target_table);
                if (targetCompare !== 0) return targetCompare;
                return a.field.localeCompare(b.field);
            });

            const availableIds = new Set(qbState.availableJoins.map(join => join.id));
            Object.keys(qbState.joinSelection).forEach(joinId => {
                if (!availableIds.has(joinId)) {
                    delete qbState.joinSelection[joinId];
                }
            });

            qbState.availableJoins.forEach(join => {
                if (!(join.id in qbState.joinSelection)) {
                    qbState.joinSelection[join.id] = true;
                }
            });
        }

        function qbRenderSelectedTables() {
            const container = document.getElementById('qbSelectedTables');

            if (!qbState.selectedTables.length) {
                container.innerHTML = '<div class="empty-state">Selecione uma ou mais tabelas para escolher os campos que entrarão no <strong>SELECT</strong>.</div>';
                return;
            }

            container.innerHTML = qbState.selectedTables.map(tableName => {
                const table = TABLES[tableName];
                const selectedFields = qbState.selectedFields[tableName] || new Set();
                const totalFields = table.fields.length;
                const selectedCount = selectedFields.size;

                const fieldsHtml = table.fields.map(field => `
                    <div class="qb-field-item">
                        <label>
                            <input type="checkbox"
                                   data-qb-field-table="${qbEscapeHTML(tableName)}"
                                   data-qb-field-name="${qbEscapeHTML(field.name)}"
                                   ${selectedFields.has(field.name) ? 'checked' : ''}>
                            <span>
                                <strong>${qbEscapeHTML(field.name)}</strong>
                                <span class="qb-field-type"> • ${qbEscapeHTML(field.type || 'Unknown')}${field.size ? `(${qbEscapeHTML(field.size)})` : ''}${field.fk_table ? ` • FK → ${qbEscapeHTML(field.fk_table)}` : ''}</span>
                            </span>
                        </label>
                    </div>
                `).join('');

                return `
                    <div class="qb-table-card">
                        <div class="qb-card-header">
                            <div class="qb-card-title">
                                <strong>${qbEscapeHTML(tableName)}</strong>
                                <span class="module-badge">${qbEscapeHTML(table.module || '-')}</span>
                                <span class="qb-help-text">${selectedCount}/${totalFields} campo(s) marcado(s)</span>
                            </div>
                            <div class="qb-card-actions">
                                <button class="btn btn-secondary" data-qb-select-all="${qbEscapeHTML(tableName)}">Selecionar todos</button>
                                <button class="btn btn-secondary" data-qb-clear-fields="${qbEscapeHTML(tableName)}">Limpar campos</button>
                            </div>
                        </div>
                        <div class="qb-fields-grid">${fieldsHtml}</div>
                    </div>
                `;
            }).join('');

            container.querySelectorAll('[data-qb-select-all]').forEach(button => {
                button.addEventListener('click', function() {
                    qbSetAllFields(this.dataset.qbSelectAll, true);
                });
            });

            container.querySelectorAll('[data-qb-clear-fields]').forEach(button => {
                button.addEventListener('click', function() {
                    qbSetAllFields(this.dataset.qbClearFields, false);
                });
            });

            container.querySelectorAll('input[data-qb-field-table]').forEach(input => {
                input.addEventListener('change', function() {
                    qbToggleField(this.dataset.qbFieldTable, this.dataset.qbFieldName, this.checked);
                });
            });
        }

        function qbRenderRelationships() {
            const container = document.getElementById('qbRelationshipsList');

            if (!qbState.selectedTables.length) {
                container.innerHTML = '<div class="qb-empty-small">Selecione tabelas para detectar relacionamentos automaticamente.</div>';
                return;
            }

            if (!qbState.availableJoins.length) {
                container.innerHTML = '<div class="empty-state">Nenhum relacionamento detectado entre as tabelas selecionadas.</div>';
                return;
            }

            container.innerHTML = qbState.availableJoins.map(join => `
                <div class="qb-relationship-item">
                    <label>
                        <input type="checkbox" data-qb-join="${qbEscapeHTML(join.id)}" ${qbState.joinSelection[join.id] !== false ? 'checked' : ''}>
                        <span>
                            <strong>${qbEscapeHTML(join.source_table)}.${qbEscapeHTML(join.field)}</strong>
                            <span>→</span>
                            <strong>${qbEscapeHTML(join.target_table)}.${qbEscapeHTML(join.references_field)}</strong>
                            <div class="qb-relationship-meta">${qbEscapeHTML(join.source_table)} referencia ${qbEscapeHTML(join.target_table)} pelo campo ${qbEscapeHTML(join.field)}.</div>
                        </span>
                    </label>
                </div>
            `).join('');

            container.querySelectorAll('input[data-qb-join]').forEach(input => {
                input.addEventListener('change', function() {
                    qbState.joinSelection[this.dataset.qbJoin] = this.checked;
                    qbRefreshOutputs();
                });
            });
        }

        function qbGetSelectedJoins() {
            return qbState.availableJoins.filter(join => qbState.joinSelection[join.id] !== false);
        }

        function qbBuildQueryPlan() {
            const selectedTables = qbState.selectedTables.slice();
            const selectedJoins = qbGetSelectedJoins();

            if (!selectedTables.length) {
                return {
                    aliasMap: {},
                    fromLines: [],
                    islands: [],
                    selectedJoins
                };
            }

            const aliasMap = {};
            const fromLines = [];
            const included = new Set();
            const remaining = new Set(selectedTables);
            const baseTable = selectedTables[0];
            let aliasCounter = 1;

            aliasMap[baseTable] = `T${aliasCounter++}`;
            included.add(baseTable);
            remaining.delete(baseTable);
            fromLines.push(`FROM ${baseTable} ${aliasMap[baseTable]}`);

            let hasProgress = true;
            while (remaining.size && hasProgress) {
                hasProgress = false;

                selectedJoins.forEach(join => {
                    const sourceIncluded = included.has(join.source_table);
                    const targetIncluded = included.has(join.target_table);

                    if (sourceIncluded && remaining.has(join.target_table)) {
                        aliasMap[join.target_table] = `T${aliasCounter++}`;
                        fromLines.push(`${qbState.joinType} ${join.target_table} ${aliasMap[join.target_table]} ON ${aliasMap[join.source_table]}.${join.field} = ${aliasMap[join.target_table]}.${join.references_field}`);
                        included.add(join.target_table);
                        remaining.delete(join.target_table);
                        hasProgress = true;
                    } else if (targetIncluded && remaining.has(join.source_table)) {
                        aliasMap[join.source_table] = `T${aliasCounter++}`;
                        fromLines.push(`${qbState.joinType} ${join.source_table} ${aliasMap[join.source_table]} ON ${aliasMap[join.source_table]}.${join.field} = ${aliasMap[join.target_table]}.${join.references_field}`);
                        included.add(join.source_table);
                        remaining.delete(join.source_table);
                        hasProgress = true;
                    }
                });
            }

            const islands = selectedTables.filter(tableName => remaining.has(tableName));
            islands.forEach(tableName => {
                aliasMap[tableName] = `T${aliasCounter++}`;
                fromLines.push(`CROSS JOIN ${tableName} ${aliasMap[tableName]}`);
                included.add(tableName);
                remaining.delete(tableName);
            });

            return {
                aliasMap,
                fromLines,
                islands,
                selectedJoins
            };
        }

        function qbBuildSQL() {
            if (!qbState.selectedTables.length) {
                qbState.generatedSQL = '';
                return '';
            }

            const queryPlan = qbBuildQueryPlan();
            const selectParts = [];

            qbState.selectedTables.forEach(tableName => {
                const table = TABLES[tableName];
                const alias = queryPlan.aliasMap[tableName];
                const selectedFields = qbState.selectedFields[tableName] || new Set();
                const chosenFields = table.fields.filter(field => selectedFields.has(field.name));

                if (!chosenFields.length) {
                    selectParts.push(`${alias}.*`);
                    return;
                }

                chosenFields.forEach(field => {
                    selectParts.push(`${alias}.${field.name}`);
                });
            });

            const sql = [
                'SELECT',
                `    ${selectParts.join(',\\n    ')}`,
                ...queryPlan.fromLines,
                ';'
            ].join('\\n');

            qbState.generatedSQL = sql;
            return sql;
        }

        function qbRefreshOutputs() {
            const sqlOutput = document.getElementById('qbSqlOutput');
            const warningContainer = document.getElementById('qbRelationshipWarning');
            const sql = qbBuildSQL();
            const queryPlan = qbBuildQueryPlan();

            sqlOutput.textContent = sql || '-- Selecione pelo menos uma tabela para gerar o SQL.';

            if (queryPlan.islands.length) {
                warningContainer.style.display = 'block';
                warningContainer.className = 'qb-warning';
                warningContainer.textContent = `${queryPlan.islands.length} tabela(s) sem relacionamento com as demais serão adicionadas com CROSS JOIN: ${queryPlan.islands.join(', ')}.`;
            } else if (qbState.selectedTables.length > 1 && !queryPlan.selectedJoins.length) {
                warningContainer.style.display = 'block';
                warningContainer.className = 'qb-info-box';
                warningContainer.textContent = 'Há mais de uma tabela selecionada, mas nenhum JOIN marcado. O SQL usará apenas CROSS JOIN entre as tabelas desconectadas.';
            } else {
                warningContainer.style.display = 'none';
                warningContainer.textContent = '';
                warningContainer.className = '';
            }

            qbRenderDiagram(queryPlan);
        }

        function qbCopySQL() {
            if (!qbState.generatedSQL) {
                alert('Nenhum SQL gerado para copiar.');
                return;
            }

            const fallbackCopy = () => {
                const tempTextarea = document.createElement('textarea');
                tempTextarea.value = qbState.generatedSQL;
                document.body.appendChild(tempTextarea);
                tempTextarea.select();
                document.execCommand('copy');
                document.body.removeChild(tempTextarea);
                alert('SQL copiado para a área de transferência.');
            };

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(qbState.generatedSQL)
                    .then(() => alert('SQL copiado para a área de transferência.'))
                    .catch(() => fallbackCopy());
            } else {
                fallbackCopy();
            }
        }

        function qbDownloadSQL() {
            if (!qbState.generatedSQL) {
                alert('Nenhum SQL gerado para baixar.');
                return;
            }

            const blob = new Blob([qbState.generatedSQL + '\\n'], {type: 'text/sql;charset=utf-8'});
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'query_benner.sql';
            link.click();
            setTimeout(() => URL.revokeObjectURL(url), 1000);
        }

        function qbClearAll() {
            if (!confirm('Deseja limpar toda a seleção do construtor de query?')) {
                return;
            }

            qbState.tableFilter = '';
            qbState.selectedTables = [];
            qbState.selectedFields = {};
            qbState.availableJoins = [];
            qbState.joinSelection = {};
            qbState.generatedSQL = '';
            qbState.joinType = 'INNER JOIN';

            document.getElementById('qbTableFilter').value = '';
            document.getElementById('qbJoinType').value = qbState.joinType;

            qbRefreshSelection();
        }

        function qbMermaidSafeName(value) {
            return String(value || '').replace(/[^A-Za-z0-9_]/g, '_');
        }

        function qbGetDiagramFields(tableName, joins) {
            const table = TABLES[tableName];
            if (!table) return [];

            const highlightFields = new Set(['HANDLE']);
            joins.forEach(join => {
                if (join.source_table === tableName) {
                    highlightFields.add(join.field);
                }
            });

            const pickedFields = [];
            const extras = [];
            table.fields.forEach(field => {
                if (highlightFields.has(field.name)) {
                    pickedFields.push(field);
                } else if (extras.length < 3) {
                    extras.push(field);
                }
            });

            return [...pickedFields, ...extras].slice(0, 6);
        }

        function qbBuildMermaidDefinition(joins) {
            const lines = ['erDiagram'];

            joins.forEach(join => {
                lines.push(`    ${qbMermaidSafeName(join.source_table)} }o--|| ${qbMermaidSafeName(join.target_table)} : "${join.field}"`);
            });

            qbState.selectedTables.forEach(tableName => {
                lines.push(`    ${qbMermaidSafeName(tableName)} {`);
                qbGetDiagramFields(tableName, joins).forEach(field => {
                    lines.push(`        ${qbMermaidSafeName(field.type || 'Unknown')} ${qbMermaidSafeName(field.name)}`);
                });
                lines.push('    }');
            });

            return lines.join('\\n');
        }

        function qbRenderDiagram(queryPlan) {
            const container = document.getElementById('qbDiagram');
            const meta = document.getElementById('qbDiagramMeta');
            const joins = queryPlan ? queryPlan.selectedJoins : qbGetSelectedJoins();

            if (!qbState.selectedTables.length) {
                container.innerHTML = '<div class="empty-state">Selecione tabelas para visualizar o diagrama ER correspondente.</div>';
                meta.textContent = '';
                return;
            }

            const mermaidDefinition = qbBuildMermaidDefinition(joins);
            meta.textContent = 'Renderização offline nativa em SVG. Se `window.mermaid` estiver disponível no navegador, o mesmo diagrama pode ser renderizado a partir da definição Mermaid equivalente.';

            if (window.mermaid && typeof window.mermaid.render === 'function') {
                try {
                    const renderId = 'qb-mermaid-' + Date.now();
                    const renderResult = window.mermaid.render(renderId, mermaidDefinition);

                    if (renderResult && typeof renderResult.then === 'function') {
                        renderResult.then(result => {
                            container.innerHTML = result.svg || '';
                        }).catch(() => {
                            qbRenderFallbackDiagram(container, joins);
                        });
                        return;
                    }

                    if (renderResult && renderResult.svg) {
                        container.innerHTML = renderResult.svg;
                        return;
                    }
                } catch (error) {
                    // Fallback below
                }
            }

            qbRenderFallbackDiagram(container, joins);
        }

        function qbRenderFallbackDiagram(container, joins) {
            const tables = qbState.selectedTables.slice();
            const positions = {};
            const tableWidth = 260;
            const padding = 40;
            const cols = Math.max(1, Math.ceil(Math.sqrt(tables.length)));
            let currentRowHeights = [];

            tables.forEach((tableName, index) => {
                const col = index % cols;
                const row = Math.floor(index / cols);
                const fields = qbGetDiagramFields(tableName, joins);
                const tableHeight = 56 + (fields.length * 18) + 20;

                if (!currentRowHeights[row]) {
                    currentRowHeights[row] = tableHeight;
                } else {
                    currentRowHeights[row] = Math.max(currentRowHeights[row], tableHeight);
                }

                positions[tableName] = {
                    x: padding + col * (tableWidth + padding),
                    row,
                    height: tableHeight
                };
            });

            let accumulatedY = padding;
            Object.keys(positions).sort((a, b) => positions[a].row - positions[b].row).forEach(tableName => {
                const position = positions[tableName];
                let rowY = padding;
                for (let rowIndex = 0; rowIndex < position.row; rowIndex++) {
                    rowY += (currentRowHeights[rowIndex] || 0) + padding;
                }
                position.y = rowY;
            });

            const rows = Math.ceil(tables.length / cols);
            const svgWidth = Math.max(420, (cols * (tableWidth + padding)) + padding);
            const svgHeight = Math.max(260, currentRowHeights.slice(0, rows).reduce((sum, value) => sum + value, 0) + ((rows + 1) * padding));

            const escapeSvg = qbEscapeHTML;
            let svg = `<svg viewBox="0 0 ${svgWidth} ${svgHeight}" xmlns="http://www.w3.org/2000/svg">`;
            svg += `
                <defs>
                    <marker id="qbArrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"></path>
                    </marker>
                </defs>
            `;

            joins.forEach(join => {
                const source = positions[join.source_table];
                const target = positions[join.target_table];
                if (!source || !target) return;

                const startX = source.x + tableWidth;
                const startY = source.y + (source.height / 2);
                const endX = target.x;
                const endY = target.y + (target.height / 2);
                const controlX = (startX + endX) / 2;
                const labelX = controlX;
                const labelY = ((startY + endY) / 2) - 6;

                svg += `<path d="M ${startX} ${startY} C ${controlX} ${startY}, ${controlX} ${endY}, ${endX} ${endY}" stroke="#64748b" stroke-width="2" fill="none" marker-end="url(#qbArrow)"></path>`;
                svg += `<text x="${labelX}" y="${labelY}" font-size="11" fill="#475569" text-anchor="middle">${escapeSvg(join.field)}</text>`;
            });

            tables.forEach(tableName => {
                const table = TABLES[tableName];
                const position = positions[tableName];
                const fields = qbGetDiagramFields(tableName, joins);
                const tableHeight = position.height;
                let textY = position.y + 48;

                svg += `
                    <g>
                        <rect x="${position.x}" y="${position.y}" width="${tableWidth}" height="${tableHeight}" rx="10" fill="#ffffff" stroke="#cbd5e1" stroke-width="2"></rect>
                        <rect x="${position.x}" y="${position.y}" width="${tableWidth}" height="34" rx="10" fill="#2563eb"></rect>
                        <rect x="${position.x}" y="${position.y + 20}" width="${tableWidth}" height="14" fill="#2563eb"></rect>
                        <text x="${position.x + 14}" y="${position.y + 22}" font-size="13" font-weight="700" fill="#ffffff">${escapeSvg(tableName)}</text>
                        <text x="${position.x + 14}" y="${position.y + 40}" font-size="11" fill="#475569">${escapeSvg((table.module || '-') + ' • ' + fields.length + ' campo(s)')}</text>
                `;

                fields.forEach(field => {
                    const prefix = field.name === 'HANDLE' ? 'PK ' : (field.fk_table ? 'FK ' : '');
                    svg += `<text x="${position.x + 14}" y="${textY}" font-size="11" fill="#0f172a">${escapeSvg(prefix + field.name + ' : ' + (field.type || 'Unknown'))}</text>`;
                    textY += 18;
                });

                svg += '</g>';
            });

            svg += '</svg>';
            container.innerHTML = svg;
        }
        
        function selectTable(tableName) {
            if (!TABLES[tableName]) {
                alert('Tabela não encontrada: ' + tableName);
                return;
            }
            
            qbState.visible = false;
            currentTable = tableName;
            const table = TABLES[tableName];
            
            // Update breadcrumb
            document.getElementById('breadcrumbModule').textContent = table.module;
            document.getElementById('breadcrumbTable').textContent = tableName;
            
            // Update header
            document.getElementById('tableName').textContent = tableName;
            document.getElementById('tableModule').textContent = table.module_name;
            document.getElementById('tableFieldCount').textContent = `${table.fields.length} campos`;
            document.getElementById('tableDescription').textContent = table.description || '';
            
            // Update fields table
            const fieldsBody = document.getElementById('fieldsBody');
            fieldsBody.innerHTML = table.fields.map(field => `
                <tr>
                    <td><strong>${field.name}</strong>${field.name === 'HANDLE' ? ' 🔑' : ''}</td>
                    <td>
                        <span class="type-badge type-${field.type}">${field.type}</span>
                        ${field.size ? `(${field.size})` : ''}
                    </td>
                    <td>
                        ${field.nullable === true ? '<span class="nullable">✓ Null</span>' : 
                          field.nullable === false ? '<span class="not-nullable">✗ Not Null</span>' : ''}
                    </td>
                    <td>${field.description || '-'}</td>
                    <td>
                        ${field.fk_table ? 
                            `<a class="fk-link" onclick="selectTable('${field.fk_table}')">🔗 ${field.fk_table}</a>` : 
                            '-'}
                    </td>
                </tr>
            `).join('');
            
            // Update relationships
            const relContainer = document.getElementById('relationshipsContainer');
            if (table.relationships.length > 0) {
                relContainer.innerHTML = table.relationships.map(rel => `
                    <div class="relationship-card">
                        <div>
                            <strong>${rel.field}</strong>
                            <div style="font-size: 0.8rem; color: var(--text-secondary);">Campo local</div>
                        </div>
                        <div class="arrow">→</div>
                        <div>
                            <a class="fk-link" onclick="selectTable('${rel.references_table}')">
                                <strong>${rel.references_table}</strong>
                            </a>
                            <div style="font-size: 0.8rem; color: var(--text-secondary);">${rel.references_field}</div>
                        </div>
                    </div>
                `).join('');
            } else {
                relContainer.innerHTML = '<div class="empty-state">Esta tabela não possui relacionamentos definidos.</div>';
            }
            
            // Update lineage
            updateLineage(tableName);
            
            // Update ER diagram
            renderERDiagram(tableName);
            
            // Show table detail
            document.getElementById('dashboard').style.display = 'none';
            document.getElementById('tableDetail').style.display = 'block';
            document.getElementById('queryBuilderView').style.display = 'none';
            
            // Update table list
            renderTableList();
            
            // Reset to first tab
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.querySelector('.tab[data-tab="fields"]').classList.add('active');
            document.getElementById('tab-fields').classList.add('active');
        }
        
        function updateLineage(tableName) {
            const table = TABLES[tableName];
            
            // Tabelas que esta tabela referencia
            const dependsOn = new Set();
            table.fields.forEach(f => {
                if (f.fk_table && TABLES[f.fk_table]) {
                    dependsOn.add(f.fk_table);
                }
            });
            
            const dependsOnContainer = document.getElementById('dependsOn');
            if (dependsOn.size > 0) {
                dependsOnContainer.innerHTML = Array.from(dependsOn).map(t => 
                    `<div class="lineage-item" onclick="selectTable('${t}')">${t}</div>`
                ).join('');
            } else {
                dependsOnContainer.innerHTML = '<span style="color: var(--text-secondary)">Nenhuma dependência</span>';
            }
            
            // Tabelas que referenciam esta tabela
            const dependents = [];
            Object.entries(TABLES).forEach(([name, t]) => {
                if (name !== tableName) {
                    t.fields.forEach(f => {
                        if (f.fk_table === tableName) {
                            dependents.push(name);
                        }
                    });
                }
            });
            
            const dependentsContainer = document.getElementById('dependents');
            if (dependents.length > 0) {
                dependentsContainer.innerHTML = [...new Set(dependents)].slice(0, 50).map(t => 
                    `<div class="lineage-item" onclick="selectTable('${t}')">${t}</div>`
                ).join('');
                if (dependents.length > 50) {
                    dependentsContainer.innerHTML += `<span style="color: var(--text-secondary)">... e mais ${dependents.length - 50}</span>`;
                }
            } else {
                dependentsContainer.innerHTML = '<span style="color: var(--text-secondary)">Nenhuma tabela dependente</span>';
            }
        }
        
        function renderERDiagram(tableName) {
            const container = document.getElementById('erDiagram');
            const table = TABLES[tableName];
            
            // Coletar tabelas relacionadas
            const relatedTables = new Set([tableName]);
            table.fields.forEach(f => {
                if (f.fk_table && TABLES[f.fk_table]) {
                    relatedTables.add(f.fk_table);
                }
            });
            
            // Adicionar tabelas que referenciam esta
            Object.entries(TABLES).forEach(([name, t]) => {
                if (relatedTables.size < 8) { // Limitar para não ficar muito grande
                    t.fields.forEach(f => {
                        if (f.fk_table === tableName) {
                            relatedTables.add(name);
                        }
                    });
                }
            });
            
            // Calcular dimensões
            const tableCount = relatedTables.size;
            const tableWidth = 200;
            const tableHeight = 120;
            const padding = 50;
            const cols = Math.ceil(Math.sqrt(tableCount));
            const rows = Math.ceil(tableCount / cols);
            const svgWidth = cols * (tableWidth + padding) + padding;
            const svgHeight = rows * (tableHeight + padding) + padding;
            
            // Posições das tabelas
            const positions = {};
            let i = 0;
            relatedTables.forEach(t => {
                const col = i % cols;
                const row = Math.floor(i / cols);
                positions[t] = {
                    x: padding + col * (tableWidth + padding),
                    y: padding + row * (tableHeight + padding)
                };
                i++;
            });
            
            // Gerar SVG
            let svg = `<svg viewBox="0 0 ${svgWidth} ${svgHeight}" xmlns="http://www.w3.org/2000/svg">`;
            
            // Linhas de relacionamento
            relatedTables.forEach(t => {
                const tbl = TABLES[t];
                if (tbl) {
                    tbl.fields.forEach(f => {
                        if (f.fk_table && relatedTables.has(f.fk_table)) {
                            const from = positions[t];
                            const to = positions[f.fk_table];
                            if (from && to) {
                                svg += `<path class="er-line" d="M${from.x + tableWidth} ${from.y + tableHeight/2} Q${(from.x + to.x)/2 + tableWidth} ${(from.y + to.y)/2} ${to.x} ${to.y + tableHeight/2}" marker-end="url(#arrow)"/>`;
                            }
                        }
                    });
                }
            });
            
            // Definição do marcador de seta
            svg += `<defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--secondary)"/>
                </marker>
            </defs>`;
            
            // Tabelas
            relatedTables.forEach(t => {
                const pos = positions[t];
                const isMain = t === tableName;
                const headerColor = isMain ? '#2563eb' : '#64748b';
                
                svg += `
                    <g transform="translate(${pos.x}, ${pos.y})" style="cursor: pointer" onclick="selectTable('${t}')">
                        <rect class="er-table" width="${tableWidth}" height="${tableHeight}" rx="8"/>
                        <rect class="er-table-header" width="${tableWidth}" height="30" rx="8" ry="8" style="fill: ${headerColor}"/>
                        <rect width="${tableWidth}" height="15" y="15" style="fill: ${headerColor}"/>
                        <text class="er-text er-text-header" x="10" y="20">${t.length > 20 ? t.substring(0, 20) + '...' : t}</text>
                        <text class="er-text" x="10" y="50" style="fill: var(--text-secondary); font-size: 10px;">
                            ${TABLES[t] ? TABLES[t].fields.length : 0} campos
                        </text>
                        <text class="er-text" x="10" y="65" style="fill: var(--text-secondary); font-size: 10px;">
                            ${TABLES[t] ? TABLES[t].relationships.length : 0} relacionamentos
                        </text>
                        <text class="er-text" x="10" y="95" style="fill: var(--primary); font-size: 10px;">
                            ${TABLES[t] ? TABLES[t].module : ''}
                        </text>
                    </g>
                `;
            });
            
            svg += '</svg>';
            container.innerHTML = svg;
        }
        
        function showDashboard() {
            qbState.visible = false;
            currentTable = null;
            document.getElementById('dashboard').style.display = 'block';
            document.getElementById('tableDetail').style.display = 'none';
            document.getElementById('queryBuilderView').style.display = 'none';
            renderTableList();
        }
        
        function setupEventListeners() {
            // Search
            const searchInput = document.getElementById('searchInput');
            searchInput.addEventListener('input', function() {
                const query = this.value.toLowerCase();
                const moduleFilter = document.getElementById('moduleFilter').value;
                
                filteredTables = Object.keys(TABLES).filter(tableName => {
                    const table = TABLES[tableName];
                    const matchesModule = !moduleFilter || table.module === moduleFilter;
                    
                    if (!query) return matchesModule;
                    
                    // Buscar em nome da tabela
                    if (tableName.toLowerCase().includes(query)) return matchesModule;
                    
                    // Buscar em descrição
                    if (table.description && table.description.toLowerCase().includes(query)) return matchesModule;
                    
                    // Buscar em campos
                    const fieldMatch = table.fields.some(f => 
                        f.name.toLowerCase().includes(query) ||
                        (f.description && f.description.toLowerCase().includes(query))
                    );
                    if (fieldMatch) return matchesModule;
                    
                    return false;
                }).sort();
                
                renderTableList();
            });
            
            // Module filter
            document.getElementById('moduleFilter').addEventListener('change', function() {
                document.getElementById('searchInput').dispatchEvent(new Event('input'));
            });
            
            // Tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    const tabId = this.dataset.tab;
                    
                    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                    
                    this.classList.add('active');
                    document.getElementById('tab-' + tabId).classList.add('active');
                });
            });
        }
        
        function exportTableJSON() {
            if (!currentTable) return;
            const table = TABLES[currentTable];
            const blob = new Blob([JSON.stringify(table, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = currentTable + '.json';
            a.click();
        }
        
        function exportTableDBML() {
            if (!currentTable) return;
            const table = TABLES[currentTable];
            
            let dbml = `Table ${currentTable} {\\n`;
            table.fields.forEach(f => {
                let type = f.type.toLowerCase();
                if (f.size) type = `varchar(${f.size})`;
                
                const constraints = [];
                if (f.name === 'HANDLE') constraints.push('pk');
                if (f.nullable === false) constraints.push('not null');
                if (f.fk_table) constraints.push(`ref: > ${f.fk_table}.HANDLE`);
                
                const constraintStr = constraints.length ? ` [${constraints.join(', ')}]` : '';
                const desc = f.description ? ` // ${f.description}` : '';
                
                dbml += `  ${f.name} ${type}${constraintStr}${desc}\\n`;
            });
            dbml += '}';
            
            const blob = new Blob([dbml], {type: 'text/plain'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = currentTable + '.dbml';
            a.click();
        }
        
        // Export all data
        function exportAllJSON() {
            const blob = new Blob([JSON.stringify({tables: TABLES, statistics: STATS}, null, 2)], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'dicionario_dados_completo.json';
            a.click();
        }
        
        // Excel Export Functions
        function escapeCSV(str) {
            if (str == null) return '';
            str = String(str);
            if (str.includes(',') || str.includes('"') || str.includes('\\n')) {
                return '"' + str.replace(/"/g, '""') + '"';
            }
            return str;
        }
        
        function exportTableExcel() {
            if (!currentTable) return;
            const table = TABLES[currentTable];
            
            let csv = '\\uFEFF'; // BOM for Excel UTF-8
            csv += 'Campo,Tipo,Tamanho,Nulo,Descrição,FK Tabela\\n';
            
            table.fields.forEach(f => {
                csv += [
                    escapeCSV(f.name),
                    escapeCSV(f.type),
                    escapeCSV(f.size || ''),
                    escapeCSV(f.nullable === true ? 'Sim' : (f.nullable === false ? 'Não' : '')),
                    escapeCSV(f.description || ''),
                    escapeCSV(f.fk_table || '')
                ].join(',') + '\\n';
            });
            
            const blob = new Blob([csv], {type: 'text/csv;charset=utf-8'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = currentTable + '.csv';
            a.click();
        }
        
        function exportAllExcel() {
            // Export complete data dictionary to Excel-compatible format
            let csv = '\\uFEFF'; // BOM for Excel UTF-8
            csv += 'Tabela,Módulo,Campo,Tipo,Tamanho,Nulo,Descrição,FK Tabela\\n';
            
            Object.entries(TABLES).sort((a, b) => a[0].localeCompare(b[0])).forEach(([tableName, table]) => {
                table.fields.forEach(f => {
                    csv += [
                        escapeCSV(tableName),
                        escapeCSV(table.module),
                        escapeCSV(f.name),
                        escapeCSV(f.type),
                        escapeCSV(f.size || ''),
                        escapeCSV(f.nullable === true ? 'Sim' : (f.nullable === false ? 'Não' : '')),
                        escapeCSV(f.description || ''),
                        escapeCSV(f.fk_table || '')
                    ].join(',') + '\\n';
                });
            });
            
            const blob = new Blob([csv], {type: 'text/csv;charset=utf-8'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'dicionario_dados_completo.csv';
            a.click();
        }
        
        function exportRelationshipsExcel() {
            // Export all relationships to Excel-compatible format
            let csv = '\\uFEFF'; // BOM for Excel UTF-8
            csv += 'Tabela Origem,Campo,Tabela Destino,Campo Destino\\n';
            
            Object.entries(TABLES).sort((a, b) => a[0].localeCompare(b[0])).forEach(([tableName, table]) => {
                table.relationships.forEach(rel => {
                    csv += [
                        escapeCSV(tableName),
                        escapeCSV(rel.field),
                        escapeCSV(rel.references_table),
                        escapeCSV(rel.references_field)
                    ].join(',') + '\\n';
                });
            });
            
            const blob = new Blob([csv], {type: 'text/csv;charset=utf-8'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'relacionamentos.csv';
            a.click();
        }
        
        function exportModulesExcel() {
            // Export tables index by module
            let csv = '\\uFEFF'; // BOM for Excel UTF-8
            csv += 'Módulo,Nome do Módulo,Tabela,Qtd Campos,Qtd Relacionamentos\\n';
            
            Object.entries(TABLES).sort((a, b) => {
                if (a[1].module !== b[1].module) return a[1].module.localeCompare(b[1].module);
                return a[0].localeCompare(b[0]);
            }).forEach(([tableName, table]) => {
                csv += [
                    escapeCSV(table.module),
                    escapeCSV(table.module_name),
                    escapeCSV(tableName),
                    escapeCSV(table.fields.length),
                    escapeCSV(table.relationships.length)
                ].join(',') + '\\n';
            });
            
            const blob = new Blob([csv], {type: 'text/csv;charset=utf-8'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'indice_tabelas.csv';
            a.click();
        }
    </script>
</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"HTML gerado: {output_path}")

def main():
    """Função principal"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'Dicionario de Dados.txt')
    html_output = os.path.join(script_dir, 'dicionario_dados.html')
    
    print(f"Processando: {input_file}")
    
    # Parse data
    tables = parse_data_dictionary(input_file)
    print(f"Tabelas encontradas: {len(tables)}")
    
    # Build statistics
    stats = build_statistics(tables)
    
    # Generate HTML
    generate_html(tables, stats, html_output)
    
    print(f"\\nArquivos gerados:")
    print(f"  - {html_output}")
    print(f"\\nAbra o arquivo HTML em um navegador para visualizar o dicionário de dados.")

if __name__ == '__main__':
    main()
