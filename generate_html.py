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
        
        /* Responsive */
        @media (max-width: 1024px) {
            .main-layout {
                grid-template-columns: 1fr;
            }
            
            .sidebar {
                position: static;
                max-height: none;
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
        
        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {
            initModuleFilter();
            renderTableList();
            renderDashboard();
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
        
        function selectTable(tableName) {
            if (!TABLES[tableName]) {
                alert('Tabela não encontrada: ' + tableName);
                return;
            }
            
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
            currentTable = null;
            document.getElementById('dashboard').style.display = 'block';
            document.getElementById('tableDetail').style.display = 'none';
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
            
            const blob = new Blob([dbml.replace(/\\n/g, '\\n')], {type: 'text/plain'});
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
