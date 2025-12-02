"""
Flask Web Application for SQL Builder Agent
Provides a web interface for building SQL queries
"""

from flask import Flask, render_template, request, jsonify
from sql_builder_agent import SQLBuilderAgent, JoinType, Table, Column
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Initialize the SQL Builder Agent
sql_agent = SQLBuilderAgent()

# Load schema from the data dictionary file
def load_schema():
    """Load the database schema from the data dictionary"""
    dict_file = 'Dicionario de Dados.txt'
    if os.path.exists(dict_file):
        try:
            with open(dict_file, 'r', encoding='utf-8', errors='ignore') as f:
                schema_text = f.read()
                sql_agent.load_schema_from_dict(schema_text)
                print(f"Loaded {len(sql_agent.tables)} tables from schema")
        except Exception as e:
            print(f"Error loading schema: {e}")
            # Create a sample schema if loading fails
            create_sample_schema()
    else:
        create_sample_schema()

def create_sample_schema():
    """Create a sample schema for demonstration"""
    # Create sample tables
    users_table = Table(name="Z_GRUPOUSUARIOS", description="Users table")
    users_table.columns = [
        Column(name="HANDLE", table="Z_GRUPOUSUARIOS", data_type="Integer", nullable=False, description="User ID"),
        Column(name="NOME", table="Z_GRUPOUSUARIOS", data_type="Varchar(80)", nullable=False, description="User name"),
        Column(name="EMAIL", table="Z_GRUPOUSUARIOS", data_type="Varchar(100)", nullable=True, description="Email address"),
    ]
    
    processes_table = Table(name="PR_PROCESSOS", description="Processes table")
    processes_table.columns = [
        Column(name="HANDLE", table="PR_PROCESSOS", data_type="Integer", nullable=False, description="Process ID"),
        Column(name="NUMERO", table="PR_PROCESSOS", data_type="Varchar(40)", nullable=False, description="Process number"),
        Column(name="USUARIO", table="PR_PROCESSOS", data_type="Integer", nullable=True, description="User ID"),
    ]
    
    sql_agent.add_table(users_table)
    sql_agent.add_table(processes_table)

# Load schema on startup
load_schema()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/tables', methods=['GET'])
def get_tables():
    """Get list of all tables"""
    tables = sql_agent.get_table_list()
    return jsonify({
        'success': True,
        'tables': tables
    })

@app.route('/api/tables/<table_name>/columns', methods=['GET'])
def get_columns(table_name):
    """Get columns for a specific table"""
    columns = sql_agent.get_columns_for_table(table_name)
    return jsonify({
        'success': True,
        'table': table_name,
        'columns': columns
    })

@app.route('/api/build-query', methods=['POST'])
def build_query():
    """Build SQL query from user selections"""
    try:
        data = request.json
        
        # Reset the agent
        sql_agent.reset()
        
        # Add selected columns
        for col_selection in data.get('columns', []):
            table = col_selection.get('table')
            column = col_selection.get('column')
            if table and column:
                sql_agent.select_column(table, column)
        
        # Add joins
        for join_data in data.get('joins', []):
            join_type_str = join_data.get('type', 'INNER')
            join_type = JoinType[join_type_str]
            
            table = join_data.get('table')
            left_table = join_data.get('leftTable')
            left_column = join_data.get('leftColumn')
            right_table = join_data.get('rightTable')
            right_column = join_data.get('rightColumn')
            
            if all([table, left_table, left_column, right_table, right_column]):
                sql_agent.add_join(
                    join_type,
                    table,
                    left_table, left_column,
                    right_table, right_column
                )
        
        # Add WHERE conditions
        for condition in data.get('where', []):
            if condition:
                sql_agent.add_where(condition)
        
        # Add ORDER BY
        for order in data.get('orderBy', []):
            column = order.get('column')
            ascending = order.get('ascending', True)
            if column:
                sql_agent.add_order_by(column, ascending)
        
        # Add GROUP BY
        for group_col in data.get('groupBy', []):
            if group_col:
                sql_agent.add_group_by(group_col)
        
        # Set LIMIT
        limit = data.get('limit')
        if limit:
            sql_agent.set_limit(int(limit))
        
        # Build the query
        auto_infer = data.get('autoInferJoins', False)
        sql_query = sql_agent.build_query(auto_infer_joins=auto_infer)
        
        return jsonify({
            'success': True,
            'query': sql_query
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/schema/export', methods=['GET'])
def export_schema():
    """Export the entire schema as JSON"""
    schema_json = sql_agent.export_schema_json()
    return jsonify({
        'success': True,
        'schema': schema_json
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
