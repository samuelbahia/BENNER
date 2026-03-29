"""
Exemplos de uso do SQL Builder Agent
Este arquivo demonstra vários casos de uso do agente SQL
"""

from sql_builder_agent import SQLBuilderAgent, JoinType, Table, Column


def example_1_simple_select():
    """Exemplo 1: Consulta SELECT simples"""
    print("\n" + "="*60)
    print("EXEMPLO 1: Consulta SELECT Simples")
    print("="*60)
    
    agent = SQLBuilderAgent()
    
    # Criar tabela de usuários
    users = Table(name="Z_GRUPOUSUARIOS")
    users.columns = [
        Column(name="HANDLE", table="Z_GRUPOUSUARIOS", data_type="Integer", nullable=False),
        Column(name="NOME", table="Z_GRUPOUSUARIOS", data_type="Varchar(80)", nullable=False),
        Column(name="EMAIL", table="Z_GRUPOUSUARIOS", data_type="Varchar(100)", nullable=True),
    ]
    agent.add_table(users)
    
    # Selecionar colunas
    agent.select_column("Z_GRUPOUSUARIOS", "NOME")
    agent.select_column("Z_GRUPOUSUARIOS", "EMAIL")
    
    # Adicionar condição WHERE
    agent.add_where("Z_GRUPOUSUARIOS.NOME LIKE '%Silva%'")
    
    # Adicionar ORDER BY
    agent.add_order_by("Z_GRUPOUSUARIOS.NOME", ascending=True)
    
    # Gerar SQL
    sql = agent.build_query()
    print(sql)


def example_2_inner_join():
    """Exemplo 2: Consulta com INNER JOIN"""
    print("\n" + "="*60)
    print("EXEMPLO 2: Consulta com INNER JOIN")
    print("="*60)
    
    agent = SQLBuilderAgent()
    
    # Criar tabela de processos
    processes = Table(name="PR_PROCESSOS")
    processes.columns = [
        Column(name="HANDLE", table="PR_PROCESSOS", data_type="Integer", nullable=False),
        Column(name="NUMERO", table="PR_PROCESSOS", data_type="Varchar(40)", nullable=False),
        Column(name="USUARIO", table="PR_PROCESSOS", data_type="Integer", nullable=True),
        Column(name="STATUS", table="PR_PROCESSOS", data_type="Varchar(20)", nullable=False),
    ]
    
    # Criar tabela de usuários
    users = Table(name="Z_GRUPOUSUARIOS")
    users.columns = [
        Column(name="HANDLE", table="Z_GRUPOUSUARIOS", data_type="Integer", nullable=False),
        Column(name="NOME", table="Z_GRUPOUSUARIOS", data_type="Varchar(80)", nullable=False),
    ]
    
    agent.add_table(processes)
    agent.add_table(users)
    
    # Selecionar colunas
    agent.select_column("PR_PROCESSOS", "NUMERO")
    agent.select_column("Z_GRUPOUSUARIOS", "NOME")
    agent.select_column("PR_PROCESSOS", "STATUS")
    
    # Adicionar INNER JOIN
    agent.add_join(
        JoinType.INNER,
        "Z_GRUPOUSUARIOS",
        "PR_PROCESSOS", "USUARIO",
        "Z_GRUPOUSUARIOS", "HANDLE"
    )
    
    # Adicionar condições
    agent.add_where("PR_PROCESSOS.STATUS = 'ATIVO'")
    agent.add_order_by("PR_PROCESSOS.NUMERO", ascending=True)
    
    # Gerar SQL
    sql = agent.build_query()
    print(sql)


def example_3_left_join():
    """Exemplo 3: Consulta com LEFT JOIN"""
    print("\n" + "="*60)
    print("EXEMPLO 3: Consulta com LEFT JOIN")
    print("="*60)
    
    agent = SQLBuilderAgent()
    
    # Criar tabelas
    departments = Table(name="PR_DEPARTAMENTOS")
    departments.columns = [
        Column(name="HANDLE", table="PR_DEPARTAMENTOS", data_type="Integer", nullable=False),
        Column(name="NOME", table="PR_DEPARTAMENTOS", data_type="Varchar(80)", nullable=False),
    ]
    
    processes = Table(name="PR_PROCESSOS")
    processes.columns = [
        Column(name="HANDLE", table="PR_PROCESSOS", data_type="Integer", nullable=False),
        Column(name="NUMERO", table="PR_PROCESSOS", data_type="Varchar(40)", nullable=False),
        Column(name="DEPARTAMENTO", table="PR_PROCESSOS", data_type="Integer", nullable=True),
    ]
    
    agent.add_table(departments)
    agent.add_table(processes)
    
    # Selecionar colunas
    agent.select_column("PR_DEPARTAMENTOS", "NOME")
    agent.select_column("PR_PROCESSOS", "NUMERO")
    
    # Adicionar LEFT JOIN (mostra todos os departamentos, mesmo sem processos)
    agent.add_join(
        JoinType.LEFT,
        "PR_PROCESSOS",
        "PR_DEPARTAMENTOS", "HANDLE",
        "PR_PROCESSOS", "DEPARTAMENTO"
    )
    
    # Adicionar ORDER BY
    agent.add_order_by("PR_DEPARTAMENTOS.NOME", ascending=True)
    
    # Gerar SQL
    sql = agent.build_query()
    print(sql)


def example_4_multiple_joins():
    """Exemplo 4: Consulta com múltiplos JOINs"""
    print("\n" + "="*60)
    print("EXEMPLO 4: Consulta com Múltiplos JOINs")
    print("="*60)
    
    agent = SQLBuilderAgent()
    
    # Criar tabelas
    processes = Table(name="PR_PROCESSOS")
    processes.columns = [
        Column(name="HANDLE", table="PR_PROCESSOS", data_type="Integer", nullable=False),
        Column(name="NUMERO", table="PR_PROCESSOS", data_type="Varchar(40)", nullable=False),
        Column(name="USUARIO", table="PR_PROCESSOS", data_type="Integer", nullable=True),
        Column(name="DEPARTAMENTO", table="PR_PROCESSOS", data_type="Integer", nullable=True),
    ]
    
    users = Table(name="Z_GRUPOUSUARIOS")
    users.columns = [
        Column(name="HANDLE", table="Z_GRUPOUSUARIOS", data_type="Integer", nullable=False),
        Column(name="NOME", table="Z_GRUPOUSUARIOS", data_type="Varchar(80)", nullable=False),
    ]
    
    departments = Table(name="PR_DEPARTAMENTOS")
    departments.columns = [
        Column(name="HANDLE", table="PR_DEPARTAMENTOS", data_type="Integer", nullable=False),
        Column(name="NOME", table="PR_DEPARTAMENTOS", data_type="Varchar(80)", nullable=False),
    ]
    
    agent.add_table(processes)
    agent.add_table(users)
    agent.add_table(departments)
    
    # Selecionar colunas
    agent.select_column("PR_PROCESSOS", "NUMERO")
    agent.select_column("Z_GRUPOUSUARIOS", "NOME")
    agent.select_column("PR_DEPARTAMENTOS", "NOME")
    
    # Adicionar JOINs
    agent.add_join(
        JoinType.INNER,
        "Z_GRUPOUSUARIOS",
        "PR_PROCESSOS", "USUARIO",
        "Z_GRUPOUSUARIOS", "HANDLE"
    )
    
    agent.add_join(
        JoinType.LEFT,
        "PR_DEPARTAMENTOS",
        "PR_PROCESSOS", "DEPARTAMENTO",
        "PR_DEPARTAMENTOS", "HANDLE"
    )
    
    # Adicionar ORDER BY
    agent.add_order_by("PR_PROCESSOS.NUMERO", ascending=True)
    
    # Gerar SQL
    sql = agent.build_query()
    print(sql)


def example_5_aggregation():
    """Exemplo 5: Consulta com agregação (GROUP BY)"""
    print("\n" + "="*60)
    print("EXEMPLO 5: Consulta com Agregação (GROUP BY)")
    print("="*60)
    
    agent = SQLBuilderAgent()
    
    # Criar tabelas
    departments = Table(name="PR_DEPARTAMENTOS")
    departments.columns = [
        Column(name="HANDLE", table="PR_DEPARTAMENTOS", data_type="Integer", nullable=False),
        Column(name="NOME", table="PR_DEPARTAMENTOS", data_type="Varchar(80)", nullable=False),
    ]
    
    processes = Table(name="PR_PROCESSOS")
    processes.columns = [
        Column(name="HANDLE", table="PR_PROCESSOS", data_type="Integer", nullable=False),
        Column(name="DEPARTAMENTO", table="PR_PROCESSOS", data_type="Integer", nullable=True),
    ]
    
    agent.add_table(departments)
    agent.add_table(processes)
    
    # Selecionar colunas (note que usamos COUNT na consulta real)
    agent.select_column("PR_DEPARTAMENTOS", "NOME")
    
    # Adicionar LEFT JOIN
    agent.add_join(
        JoinType.LEFT,
        "PR_PROCESSOS",
        "PR_DEPARTAMENTOS", "HANDLE",
        "PR_PROCESSOS", "DEPARTAMENTO"
    )
    
    # Adicionar GROUP BY
    agent.add_group_by("PR_DEPARTAMENTOS.NOME")
    
    # Adicionar ORDER BY
    agent.add_order_by("PR_DEPARTAMENTOS.NOME", ascending=True)
    
    # Adicionar LIMIT
    agent.set_limit(10)
    
    # Gerar SQL
    sql = agent.build_query()
    print(sql)
    print("\nNOTA: Para contar processos, adicione 'COUNT(PR_PROCESSOS.HANDLE) as TOTAL' na seleção de colunas")


def example_6_complex_filters():
    """Exemplo 6: Consulta com filtros complexos"""
    print("\n" + "="*60)
    print("EXEMPLO 6: Consulta com Filtros Complexos")
    print("="*60)
    
    agent = SQLBuilderAgent()
    
    # Criar tabela
    processes = Table(name="PR_PROCESSOS")
    processes.columns = [
        Column(name="HANDLE", table="PR_PROCESSOS", data_type="Integer", nullable=False),
        Column(name="NUMERO", table="PR_PROCESSOS", data_type="Varchar(40)", nullable=False),
        Column(name="STATUS", table="PR_PROCESSOS", data_type="Varchar(20)", nullable=False),
        Column(name="VALOR", table="PR_PROCESSOS", data_type="Number", nullable=True),
        Column(name="DATA", table="PR_PROCESSOS", data_type="Data", nullable=True),
    ]
    
    agent.add_table(processes)
    
    # Selecionar colunas
    agent.select_column("PR_PROCESSOS", "NUMERO")
    agent.select_column("PR_PROCESSOS", "STATUS")
    agent.select_column("PR_PROCESSOS", "VALOR")
    agent.select_column("PR_PROCESSOS", "DATA")
    
    # Adicionar múltiplas condições WHERE
    agent.add_where("PR_PROCESSOS.STATUS IN ('ATIVO', 'PENDENTE')")
    agent.add_where("PR_PROCESSOS.VALOR > 1000")
    agent.add_where("PR_PROCESSOS.DATA >= '2024-01-01'")
    
    # Adicionar ORDER BY com múltiplas colunas
    agent.add_order_by("PR_PROCESSOS.DATA", ascending=False)
    agent.add_order_by("PR_PROCESSOS.VALOR", ascending=False)
    
    # Adicionar LIMIT
    agent.set_limit(50)
    
    # Gerar SQL
    sql = agent.build_query()
    print(sql)


def example_7_export_schema():
    """Exemplo 7: Exportar schema como JSON"""
    print("\n" + "="*60)
    print("EXEMPLO 7: Exportar Schema como JSON")
    print("="*60)
    
    agent = SQLBuilderAgent()
    
    # Criar algumas tabelas
    users = Table(name="Z_GRUPOUSUARIOS", description="Tabela de usuários do sistema")
    users.columns = [
        Column(name="HANDLE", table="Z_GRUPOUSUARIOS", data_type="Integer", 
               nullable=False, description="ID único do usuário"),
        Column(name="NOME", table="Z_GRUPOUSUARIOS", data_type="Varchar(80)", 
               nullable=False, description="Nome completo do usuário"),
        Column(name="EMAIL", table="Z_GRUPOUSUARIOS", data_type="Varchar(100)", 
               nullable=True, description="Endereço de email"),
    ]
    
    processes = Table(name="PR_PROCESSOS", description="Tabela de processos")
    processes.columns = [
        Column(name="HANDLE", table="PR_PROCESSOS", data_type="Integer", 
               nullable=False, description="ID único do processo"),
        Column(name="NUMERO", table="PR_PROCESSOS", data_type="Varchar(40)", 
               nullable=False, description="Número do processo"),
    ]
    
    agent.add_table(users)
    agent.add_table(processes)
    
    # Exportar schema
    schema_json = agent.export_schema_json()
    print(schema_json)


def main():
    """Executar todos os exemplos"""
    print("\n" + "="*60)
    print("SQL BUILDER AGENT - EXEMPLOS DE USO")
    print("="*60)
    
    example_1_simple_select()
    example_2_inner_join()
    example_3_left_join()
    example_4_multiple_joins()
    example_5_aggregation()
    example_6_complex_filters()
    example_7_export_schema()
    
    print("\n" + "="*60)
    print("TODOS OS EXEMPLOS FORAM EXECUTADOS!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
