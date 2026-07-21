Attribute VB_Name = "ModCadastroPastas"
'==============================================================================
' MÓDULO VBA - CADASTRO DE PASTAS NO BENNER (PREVI JURÍDICO)
'==============================================================================
' Automatiza cadastro via +Novo > Cadastro rápido de pasta (Categoria: Cível)
' Usa IDs exatos dos campos ASP.NET conforme Mapa de Campos.
'
' URL: https://previ.bennercloud.com.br/JURIDICO/jur/e/PREVI.aspx?i=K9_INICIOPREVI&m=MAIN
'
' PREFIXO COMUM: ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_
'
' REQUISITOS:
' - Microsoft Internet Controls (referência)
' - Microsoft HTML Object Library (referência)
'==============================================================================

Option Explicit

' Constantes do sistema
Private Const URL_BENNER As String = "https://previ.bennercloud.com.br/JURIDICO/jur/e/PREVI.aspx?i=K9_INICIOPREVI&m=MAIN"
Private Const URL_PASTAS As String = "https://previ.bennercloud.com.br/JURIDICO/jur/e/PREVI.aspx?i=K9_INICIOPREVI&m=PASTAS"
Private Const CATEGORIA As String = "Cível"
Private Const TIPO_PASTA As String = "Cobrança"
Private Const CAUSA_PEDIR As String = "Previdencial"
Private Const CAUSA_RAIZ As String = "Produto"
Private Const PROCESSO As String = "Cobrança"
Private Const ANDAMENTO As String = "PEDIDO DE AJUIZAMENTO DE AÇÃO"
Private Const PEDIDO As String = "Dívida Previdenciária"
Private Const RITO As String = "Ordinário"
Private Const TIPO_PROCESSO As String = "Ativo"
Private Const RISCO As String = "Possível"

' === IDs dos campos ASP.NET (Mapa de Campos Benner) ===
' Prefixo: ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_

' Seção Pasta
Private Const ID_FILIAL_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl11_ctl01_select"
Private Const ID_FILIAL_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl11_FILIAL_VALUE"
Private Const ID_GERENCIA_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl22_ctl01_select"
Private Const ID_GERENCIA_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl22_DIVISAO_VALUE"
Private Const ID_CAUSA_PEDIR_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl34_ctl01_select"
Private Const ID_CAUSA_PEDIR_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl34_ASSUNTO_VALUE"
Private Const ID_CAUSA_RAIZ_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl43_ctl01_select"
Private Const ID_CAUSA_RAIZ_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl43_CAUSARAIZ_VALUE"
Private Const ID_TIPO_PROCESSO_ATIVO As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_GroupRadioButton_TIPOPROCESSO_1"
Private Const ID_TIPO_PROCESSO_PASSIVO As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_GroupRadioButton_TIPOPROCESSO_2"

' Seção Processo
Private Const ID_PROCESSO_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl79_ctl01_select"
Private Const ID_PROCESSO_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl79_DESDOBRAMENTO_VALUE"
Private Const ID_RITO_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl87_ctl01_select"
Private Const ID_RITO_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl87_RITO_VALUE"
Private Const ID_ORGAO_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl95_ctl01_select"
Private Const ID_ORGAO_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl95_ORGAO_VALUE"
Private Const ID_UF_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl99_ctl01_select"
Private Const ID_UF_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl99_UF_VALUE"

' Distribuição
Private Const ID_DATA_DISTRIBUICAO As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_DISTRIBUIDO_1_DATADISTRIBUICAO_DATE"
Private Const ID_TIPO_DOC_PROCESSO_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_DISTRIBUIDO_1_ctl10_ctl01_select"
Private Const ID_TIPO_DOC_PROCESSO_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_DISTRIBUIDO_1_ctl10_TIPODOCUMENTO_VALUE"

' Número único
Private Const ID_NUMERO As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_NUMEROUNICO_1_NUMERODISTRIBUICAO"

' Andamentos
Private Const ID_ANDAMENTO_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl122_ctl01_select"
Private Const ID_ANDAMENTO_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl122_EVENTO1_VALUE"
Private Const ID_DATA_ANDAMENTO As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_DATAANDAMENTO1_DATE"

' Participantes
Private Const ID_ADVERSO_NAO As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_POSSUIPESSOAADVERSO_ctl03"
Private Const ID_ADVERSO_SIM As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_POSSUIPESSOAADVERSO_ctl05"
Private Const ID_PARTICIPANTE1_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_POSSUIPESSOAADVERSO_2_ctl04_ctl01_select"
Private Const ID_PARTICIPANTE1_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_POSSUIPESSOAADVERSO_2_ctl04_PARTICIPANTE1_VALUE"
Private Const ID_CONDICAO1_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_POSSUIPESSOAADVERSO_2_ctl13_ctl01_select"
Private Const ID_CONDICAO1_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_POSSUIPESSOAADVERSO_2_ctl13_CONDICAO1_VALUE"
Private Const ID_ADV_INTERNO_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl202_ctl01_select"
Private Const ID_ADV_INTERNO_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl202_ADVOGADOINTERNO_VALUE"
Private Const ID_ADV_EXTERNO_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl206_ctl01_select"
Private Const ID_ADV_EXTERNO_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl206_ADVOGADOEXTERNO_VALUE"

' Pedidos
Private Const ID_PEDIDO_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl213_ctl01_select"
Private Const ID_PEDIDO_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl213_PEDIDO1_VALUE"
Private Const ID_VALOR_PEDIDO As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_VALORPEDIDO1"
Private Const ID_RISCO_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl230_ctl01_select"
Private Const ID_RISCO_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl230_RISCOPEDIDO1_VALUE"

' Documentos (para limpar)
Private Const ID_TIPO_DOC_ARQ_SELECT As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl256_ctl01_select"
Private Const ID_TIPO_DOC_ARQ_VALUE As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_ctl256_TIPODOCUMENTOARQUIVO1_VALUE"
Private Const ID_NOME_ARQUIVO As String = "ctl00_Main_WIDGET_CADASTRO_RAPIDO_PageControl_GERAL_GERAL_NOMEARQUIVO1"

' Colunas da planilha
Private Const COL_PLANO As Integer = 1         ' A - PLANO ATUAL
Private Const COL_NOME As Integer = 4          ' D - NOME
Private Const COL_CONTRATO As Integer = 6      ' F - CONTRATO
Private Const COL_VALOR_DIVIDA As Integer = 15  ' O - VAL DIV ATUAL
Private Const COL_GERENCIA As Integer = 17      ' Q - GERÊNCIA
Private Const COL_UF As Integer = 20            ' T - UF
Private Const COL_CPF As Integer = 23           ' W - CPF
Private Const COL_BENNER As Integer = 28        ' AB - Benner (status existente)
Private Const COL_ANALISE As Integer = 29       ' AC - ANÁLISE DUPLICIDADE
Private Const COL_STATUS As Integer = 30        ' AD - STATUS CADASTRO
Private Const COL_CNJ As Integer = 31           ' AE - NÚMERO CNJ
Private Const COL_PLANO_DESC As Integer = 32    ' AF - PLANO DESCRIÇÃO
Private Const COL_PESQUISA_BENNER As Integer = 33 ' AG - RESULTADO PESQUISA BENNER
Private Const COL_ID_PASTA As Integer = 34      ' AH - ID PASTA CRIADA
Private Const COL_VALOR_PEDIDO As Integer = 35   ' AI - VALOR PEDIDO (soma quando agrupado)

' Advogados internos (seleção aleatória)
Private Const ADV_INTERNO_1 As String = "EDSON EDUARDO AGUIAR AVELAR"
Private Const ADV_INTERNO_2 As String = "MICHELLE CERQUEIRA NUNEZ"
Private Const ADV_INTERNO_3 As String = "DOMINIQUE DE SOUZA MACHADO"

' Advogados/escritórios externos (seleção aleatória)
Private Const ADV_EXTERNO_1 As String = "Aldrigues Cândido Advocacia"
Private Const ADV_EXTERNO_2 As String = "Bicudo, Matos, e Moraes Sociedade de Advogados"
Private Const ADV_EXTERNO_3 As String = "Dannemann Siemsen Advogados"
Private Const ADV_EXTERNO_4 As String = "Queiroga, Vieira, Queiroz & Ramos Advocacia"
Private Const ADV_EXTERNO_5 As String = "Wambier, Yamasaki, Bevervanço & Lobo Advocacia"

' Variáveis globais
Private IE As Object

'==============================================================================
' ETAPA 1 - ANÁLISE LOCAL DE DUPLICIDADES NA PLANILHA
'==============================================================================
Public Sub AnalisePreviaDuplicidades()
    Dim wsData As Worksheet
    Set wsData = ThisWorkbook.Sheets("Planilha1")

    Dim lastRow As Long
    lastRow = wsData.Cells(wsData.Rows.Count, COL_NOME).End(xlUp).Row

    wsData.Range(wsData.Cells(2, COL_ANALISE), wsData.Cells(lastRow, COL_VALOR_PEDIDO)).ClearContents

    wsData.Cells(1, COL_ANALISE).Value = "ANÁLISE DUPLICIDADE"
    wsData.Cells(1, COL_STATUS).Value = "STATUS CADASTRO"
    wsData.Cells(1, COL_CNJ).Value = "NÚMERO CNJ"
    wsData.Cells(1, COL_PLANO_DESC).Value = "PLANO DESCRIÇÃO"
    wsData.Cells(1, COL_PESQUISA_BENNER).Value = "PESQUISA BENNER"
    wsData.Cells(1, COL_ID_PASTA).Value = "ID PASTA BENNER"
    wsData.Cells(1, COL_VALOR_PEDIDO).Value = "VALOR PEDIDO"

    Dim dictNomes As Object
    Set dictNomes = CreateObject("Scripting.Dictionary")
    Dim i As Long, nome As String
    For i = 2 To lastRow
        nome = UCase(Trim(CStr(wsData.Cells(i, COL_NOME).Value)))
        If Not dictNomes.Exists(nome) Then
            dictNomes.Add nome, 1
        Else
            dictNomes(nome) = dictNomes(nome) + 1
        End If
    Next i

    ' Detectar duplicatas exatas
    Dim dictExatas As Object
    Set dictExatas = CreateObject("Scripting.Dictionary")
    Dim contrato As String, valor As Double, chave As String
    Dim dictDupExata As Object
    Set dictDupExata = CreateObject("Scripting.Dictionary")

    For i = 2 To lastRow
        nome = UCase(Trim(CStr(wsData.Cells(i, COL_NOME).Value)))
        contrato = CStr(wsData.Cells(i, COL_CONTRATO).Value)
        valor = CDbl(wsData.Cells(i, COL_VALOR_DIVIDA).Value)
        chave = nome & "|" & contrato & "|" & CStr(valor)
        If dictExatas.Exists(chave) Then
            dictDupExata(CStr(i)) = True
        End If
        dictExatas(chave) = i
    Next i

    ' Coletar linhas válidas por participante e construir número combinado
    Dim dictLinhas As Object ' nome -> "row1;row2;..."
    Set dictLinhas = CreateObject("Scripting.Dictionary")
    Dim dictContratos As Object ' nome -> "contrato1/contrato2"
    Set dictContratos = CreateObject("Scripting.Dictionary")
    Dim dictValores As Object ' nome -> soma dos valores da dívida
    Set dictValores = CreateObject("Scripting.Dictionary")

    For i = 2 To lastRow
        nome = UCase(Trim(CStr(wsData.Cells(i, COL_NOME).Value)))
        If dictDupExata.Exists(CStr(i)) Then GoTo SkipLinha
        If Len(Trim(CStr(wsData.Cells(i, COL_BENNER).Value))) > 0 Then GoTo SkipLinha

        If Not dictLinhas.Exists(nome) Then
            dictLinhas.Add nome, CStr(i)
        Else
            dictLinhas(nome) = dictLinhas(nome) & ";" & CStr(i)
        End If

        contrato = CStr(wsData.Cells(i, COL_CONTRATO).Value)
        If Not dictContratos.Exists(nome) Then
            dictContratos.Add nome, contrato
        Else
            If InStr(dictContratos(nome), contrato) = 0 Then
                dictContratos(nome) = dictContratos(nome) & "/" & contrato
            End If
        End If

        ' Acumular valor da dívida
        Dim valDiv As Double
        valDiv = CDbl(wsData.Cells(i, COL_VALOR_DIVIDA).Value)
        If Not dictValores.Exists(nome) Then
            dictValores.Add nome, valDiv
        Else
            dictValores(nome) = dictValores(nome) + valDiv
        End If
SkipLinha:
    Next i

    ' Preencher campos auxiliares
    For i = 2 To lastRow
        nome = UCase(Trim(CStr(wsData.Cells(i, COL_NOME).Value)))
        contrato = CStr(wsData.Cells(i, COL_CONTRATO).Value)

        Select Case wsData.Cells(i, COL_PLANO).Value
            Case 1: wsData.Cells(i, COL_PLANO_DESC).Value = "Plano de Benefícios 1"
            Case 2: wsData.Cells(i, COL_PLANO_DESC).Value = "Plano PREVI Futuro"
        End Select

        If dictDupExata.Exists(CStr(i)) Then
            wsData.Cells(i, COL_ANALISE).Value = "DUPLICATA EXATA - REMOVER"
            wsData.Cells(i, COL_STATUS).Value = "NÃO CADASTRAR"
            wsData.Cells(i, COL_CNJ).Value = "DP" & contrato
        ElseIf Len(Trim(CStr(wsData.Cells(i, COL_BENNER).Value))) > 0 Then
            wsData.Cells(i, COL_ANALISE).Value = "JÁ NO BENNER (" & wsData.Cells(i, COL_BENNER).Value & ")"
            wsData.Cells(i, COL_STATUS).Value = "JÁ CADASTRADO"
            wsData.Cells(i, COL_CNJ).Value = "DP" & contrato
        Else
            Dim numeroCombinado As String
            numeroCombinado = "DP" & dictContratos(nome)
            wsData.Cells(i, COL_CNJ).Value = numeroCombinado

            Dim linhasStr As String
            linhasStr = dictLinhas(nome)
            Dim partes() As String
            partes = Split(linhasStr, ";")

            If UBound(partes) > 0 Then
                ' Múltiplas linhas para este participante
                If CStr(i) = partes(0) Then
                    wsData.Cells(i, COL_ANALISE).Value = "MESMO PARTICIPANTE - " & (UBound(partes) + 1) & " OPERAÇÕES (AGRUPADO)"
                    wsData.Cells(i, COL_STATUS).Value = "PENDENTE"
                    ' Valor somado de todas as linhas do participante
                    wsData.Cells(i, COL_VALOR_PEDIDO).Value = dictValores(nome)
                Else
                    wsData.Cells(i, COL_ANALISE).Value = "AGRUPADO COM LINHA " & partes(0) & " - PASTA ÚNICA"
                    wsData.Cells(i, COL_STATUS).Value = "AGRUPADO"
                End If
            Else
                wsData.Cells(i, COL_ANALISE).Value = "OK"
                wsData.Cells(i, COL_STATUS).Value = "PENDENTE"
                ' Valor individual
                wsData.Cells(i, COL_VALOR_PEDIDO).Value = dictValores(nome)
            End If
        End If
    Next i

    wsData.Columns(COL_ANALISE).EntireColumn.AutoFit
    wsData.Columns(COL_STATUS).EntireColumn.AutoFit

    MsgBox "Etapa 1 concluída - Análise local." & vbCrLf & _
           "Total: " & (lastRow - 1) & " operações." & vbCrLf & _
           "Próximo: Execute 'VerificarNoBenner'.", vbInformation, "Análise Prévia"
End Sub

'==============================================================================
' ETAPA 2 - PESQUISA NO BENNER (Pastas > Parte Pasta)
'==============================================================================
Public Sub VerificarNoBenner()
    Dim wsData As Worksheet
    Set wsData = ThisWorkbook.Sheets("Planilha1")

    Dim lastRow As Long
    lastRow = wsData.Cells(wsData.Rows.Count, COL_NOME).End(xlUp).Row

    If wsData.Cells(1, COL_STATUS).Value <> "STATUS CADASTRO" Then
        MsgBox "Execute primeiro a Etapa 1!", vbExclamation
        Exit Sub
    End If

    If MsgBox("Pesquisará cada participante no Benner (Pastas > Parte Pasta)." & vbCrLf & _
              "Certifique-se de estar LOGADO. Continuar?", vbYesNo + vbQuestion, "Pesquisa") = vbNo Then Exit Sub

    If Not InicializarNavegador() Then Exit Sub
    IE.navigate URL_PASTAS
    Call AguardarCarregamento

    Dim pesquisados As Long, jaExistentes As Long
    pesquisados = 0: jaExistentes = 0
    Dim i As Long, nome As String, statusAtual As String

    For i = 2 To lastRow
        statusAtual = UCase(Trim(CStr(wsData.Cells(i, COL_STATUS).Value)))
        If statusAtual = "PENDENTE" Or statusAtual = "VERIFICAR" Then
            nome = Trim(CStr(wsData.Cells(i, COL_NOME).Value))
            If Len(nome) = 0 Then GoTo ProximaLinha

            Dim resultadoPesquisa As String
            resultadoPesquisa = PesquisarPartePasta(nome)
            wsData.Cells(i, COL_PESQUISA_BENNER).Value = resultadoPesquisa
            pesquisados = pesquisados + 1

            If InStr(UCase(resultadoPesquisa), "ENCONTRADA") > 0 And _
               InStr(UCase(resultadoPesquisa), "NÃO ENCONTRADA") = 0 Then
                ' Extrair ID da pasta se presente (formato: ...| PASTA:123)
                If InStr(UCase(resultadoPesquisa), "PASTA:") > 0 Then
                    Dim posPasta As Long, idExtraido As String
                    posPasta = InStr(resultadoPesquisa, "PASTA:") + 6
                    idExtraido = Mid(resultadoPesquisa, posPasta)
                    ' Limpar caracteres não numéricos
                    Dim ci As Long
                    For ci = 1 To Len(idExtraido)
                        If Not IsNumeric(Mid(idExtraido, ci, 1)) Then
                            idExtraido = Left(idExtraido, ci - 1)
                            Exit For
                        End If
                    Next ci
                    If Len(idExtraido) > 0 Then
                        wsData.Cells(i, COL_ID_PASTA).Value = idExtraido
                    End If
                End If

                If InStr(UCase(resultadoPesquisa), "DÍVIDA PREVIDENCIÁRIA") > 0 Or _
                   InStr(UCase(resultadoPesquisa), "DIVIDA PREVIDENCIARIA") > 0 Then
                    Dim statusText As String
                    statusText = "JÁ CADASTRADO NO BENNER"
                    If Len(idExtraido) > 0 Then
                        statusText = statusText & " (PASTA:" & idExtraido & ")"
                    End If
                    wsData.Cells(i, COL_STATUS).Value = statusText
                    jaExistentes = jaExistentes + 1
                Else
                    wsData.Cells(i, COL_ANALISE).Value = wsData.Cells(i, COL_ANALISE).Value & " | PASTA EXISTENTE OUTRO OBJETO"
                End If
            ElseIf InStr(UCase(resultadoPesquisa), "NÃO ENCONTRADA") > 0 Then
                If statusAtual = "VERIFICAR" Then wsData.Cells(i, COL_STATUS).Value = "PENDENTE"
            End If

            Application.Wait Now + TimeValue("00:00:02")
            Application.StatusBar = "Pesquisando... " & pesquisados & "/" & (lastRow - 1)
        End If
ProximaLinha:
    Next i

    Application.StatusBar = False
    MsgBox "Etapa 2 concluída. Pesquisados: " & pesquisados & _
           ", Já existentes: " & jaExistentes, vbInformation, "Pesquisa Concluída"
End Sub

'==============================================================================
' ETAPA 3 - CADASTRO VIA +NOVO > CADASTRO RÁPIDO DE PASTA (CÍVEL)
'==============================================================================
Public Sub CadastrarPastasBenner()
    Dim wsData As Worksheet
    Set wsData = ThisWorkbook.Sheets("Planilha1")

    Dim lastRow As Long
    lastRow = wsData.Cells(wsData.Rows.Count, COL_NOME).End(xlUp).Row

    If wsData.Cells(1, COL_STATUS).Value <> "STATUS CADASTRO" Then
        MsgBox "Execute primeiro as Etapas 1 e 2!", vbExclamation
        Exit Sub
    End If

    Dim totalPendentes As Long, i As Long
    For i = 2 To lastRow
        If UCase(Trim(CStr(wsData.Cells(i, COL_STATUS).Value))) = "PENDENTE" Then
            totalPendentes = totalPendentes + 1
        End If
    Next i

    If totalPendentes = 0 Then
        MsgBox "Nenhuma operação PENDENTE.", vbInformation
        Exit Sub
    End If

    If MsgBox("Cadastrar " & totalPendentes & " pastas? (+Novo > Cadastro rápido > Cível)" & vbCrLf & _
              "Certifique-se de estar LOGADO.", vbYesNo + vbQuestion, "Cadastro") = vbNo Then Exit Sub

    If Not InicializarNavegador() Then Exit Sub
    IE.navigate URL_BENNER
    Call AguardarCarregamento
    Randomize Timer

    ' Mapa: mesmo participante -> mesmo escritório externo
    Dim dictEscritorio As Object
    Set dictEscritorio = CreateObject("Scripting.Dictionary")

    Dim cadastrados As Long, erros As Long
    cadastrados = 0: erros = 0

    For i = 2 To lastRow
        If UCase(Trim(CStr(wsData.Cells(i, COL_STATUS).Value))) = "PENDENTE" Then
            Dim nome As String, contrato As String, valorPedido As Double
            Dim gerencia As String, uf As String, cpf As String
            Dim filial As String, numeroCNJ As String

            nome = Trim(CStr(wsData.Cells(i, COL_NOME).Value))
            contrato = CStr(wsData.Cells(i, COL_CONTRATO).Value)
            ' Usar valor do COL_VALOR_PEDIDO (já somado na Etapa 1 para agrupados)
            If IsEmpty(wsData.Cells(i, COL_VALOR_PEDIDO).Value) Or wsData.Cells(i, COL_VALOR_PEDIDO).Value = "" Then
                valorPedido = CDbl(wsData.Cells(i, COL_VALOR_DIVIDA).Value)
            Else
                valorPedido = CDbl(wsData.Cells(i, COL_VALOR_PEDIDO).Value)
            End If
            gerencia = Trim(CStr(wsData.Cells(i, COL_GERENCIA).Value))
            uf = Trim(CStr(wsData.Cells(i, COL_UF).Value))
            cpf = FormatarCPF(CStr(wsData.Cells(i, COL_CPF).Value))
            filial = CStr(wsData.Cells(i, COL_PLANO_DESC).Value)
            numeroCNJ = CStr(wsData.Cells(i, COL_CNJ).Value)
            If Len(numeroCNJ) = 0 Then numeroCNJ = "DP" & contrato

            Dim advInterno As String, advExterno As String
            advInterno = SortearAdvogadoInterno()

            ' Mesmo participante sempre com mesmo escritório
            Dim nomeUpper As String
            nomeUpper = UCase(nome)
            If dictEscritorio.Exists(nomeUpper) Then
                advExterno = dictEscritorio(nomeUpper)
            Else
                advExterno = SortearAdvogadoExterno()
                dictEscritorio.Add nomeUpper, advExterno
            End If

            Dim resultado As String
            resultado = CadastrarPastaCivel(nome, contrato, valorPedido, gerencia, _
                                            uf, cpf, filial, numeroCNJ, advInterno, advExterno)

            If Left(resultado, 2) = "OK" Then
                wsData.Cells(i, COL_STATUS).Value = "CADASTRADO + ANDAMENTO"
                Dim idPastaResult As String
                idPastaResult = ""
                If Len(resultado) > 3 Then
                    idPastaResult = Mid(resultado, 4)
                    wsData.Cells(i, COL_ID_PASTA).Value = idPastaResult
                End If
                cadastrados = cadastrados + 1
                ' Marcar linhas AGRUPADO do mesmo participante
                Dim j As Long
                For j = 2 To lastRow
                    If j <> i Then
                        If UCase(Trim(CStr(wsData.Cells(j, COL_STATUS).Value))) = "AGRUPADO" Then
                            If UCase(Trim(CStr(wsData.Cells(j, COL_NOME).Value))) = nomeUpper Then
                                wsData.Cells(j, COL_STATUS).Value = "CADASTRADO (AGRUPADO)"
                                If Len(idPastaResult) > 0 Then
                                    wsData.Cells(j, COL_ID_PASTA).Value = idPastaResult
                                End If
                            End If
                        End If
                    End If
                Next j
            Else
                wsData.Cells(i, COL_STATUS).Value = "ERRO: " & resultado
                erros = erros + 1
            End If

            Application.StatusBar = "Cadastrando... " & cadastrados & "/" & totalPendentes
            Application.Wait Now + TimeValue("00:00:03")
        End If
    Next i

    Application.StatusBar = False
    MsgBox "Concluído! Sucesso: " & cadastrados & ", Erros: " & erros, vbInformation, "Resultado"
End Sub

'==============================================================================
' FUNÇÃO PRINCIPAL - CADASTRAR PASTA CÍVEL (IDs exatos)
'==============================================================================
Private Function CadastrarPastaCivel(nome As String, contrato As String, _
                                      valorPedido As Double, gerencia As String, _
                                      uf As String, cpf As String, filial As String, _
                                      numeroCNJ As String, advInterno As String, _
                                      advExterno As String) As String
    On Error GoTo ErrHandler
    Dim doc As Object

    ' === PASSO 1: +Novo > Cadastro rápido de pasta ===
    Set doc = IE.document
    Dim btnNovo As Object
    Set btnNovo = BuscarElementoPorTexto(doc, "A", "+Novo")
    If btnNovo Is Nothing Then Set btnNovo = BuscarElementoPorTexto(doc, "SPAN", "Novo")
    If btnNovo Is Nothing Then Set btnNovo = BuscarElementoPorTexto(doc, "BUTTON", "Novo")

    If Not btnNovo Is Nothing Then
        btnNovo.Click
        Call AguardarCarregamento
    Else
        CadastrarPastaCivel = "Botão +Novo não encontrado"
        Exit Function
    End If

    Set doc = IE.document
    Dim linkCadRapido As Object
    Set linkCadRapido = BuscarElementoPorTexto(doc, "A", "Cadastro rápido de pasta")
    If linkCadRapido Is Nothing Then Set linkCadRapido = BuscarElementoPorTexto(doc, "SPAN", "Cadastro rápido")

    If Not linkCadRapido Is Nothing Then
        linkCadRapido.Click
        Call AguardarCarregamento
    Else
        CadastrarPastaCivel = "Cadastro rápido não encontrado"
        Exit Function
    End If

    ' === PASSO 2: Selecionar Categoria Cível ===
    Set doc = IE.document
    Call PreencherCampoPorLabel(doc, "Categoria", CATEGORIA)
    Call AguardarCarregamento

    ' === PASSO 3: Preencher campos com IDs exatos ===
    Set doc = IE.document

    ' Filial (lookup: select + hidden value)
    Call SelecionarLookup(doc, ID_FILIAL_SELECT, ID_FILIAL_VALUE, filial)

    ' Gerência (lookup)
    Call SelecionarLookup(doc, ID_GERENCIA_SELECT, ID_GERENCIA_VALUE, gerencia)

    ' Causa de Pedir (lookup)
    Call SelecionarLookup(doc, ID_CAUSA_PEDIR_SELECT, ID_CAUSA_PEDIR_VALUE, CAUSA_PEDIR)

    ' Causa Raiz (lookup)
    Call SelecionarLookup(doc, ID_CAUSA_RAIZ_SELECT, ID_CAUSA_RAIZ_VALUE, CAUSA_RAIZ)

    ' Tipo Processo: Ativo (radio button)
    Call ClicarRadio(doc, ID_TIPO_PROCESSO_ATIVO)

    ' Processo (lookup)
    Call SelecionarLookup(doc, ID_PROCESSO_SELECT, ID_PROCESSO_VALUE, PROCESSO)

    ' Rito (lookup)
    Call SelecionarLookup(doc, ID_RITO_SELECT, ID_RITO_VALUE, RITO)

    ' Órgão (lookup) - Tribunal de Justiça
    Call SelecionarLookup(doc, ID_ORGAO_SELECT, ID_ORGAO_VALUE, "Tribunal de Justiça")

    ' UF (lookup)
    Call SelecionarLookup(doc, ID_UF_SELECT, ID_UF_VALUE, uf)

    ' Data distribuição: hoje
    Dim dataHoje As String
    dataHoje = Format(Date, "dd/mm/yyyy")
    Call PreencherTexto(doc, ID_DATA_DISTRIBUICAO, dataHoje)

    ' Número: DP + contrato
    Call PreencherTexto(doc, ID_NUMERO, numeroCNJ)

    ' Andamento (lookup)
    Call SelecionarLookup(doc, ID_ANDAMENTO_SELECT, ID_ANDAMENTO_VALUE, ANDAMENTO)

    ' Data andamento: hoje
    Call PreencherTexto(doc, ID_DATA_ANDAMENTO, dataHoje)

    ' === PASSO 4: Participantes ===
    ' Adverso já cadastrado: Sim (pesquisar)
    Call ClicarRadio(doc, ID_ADVERSO_SIM)
    Application.Wait Now + TimeValue("00:00:01")
    Set doc = IE.document

    ' Participante 1 (adverso/réu)
    Call SelecionarLookup(doc, ID_PARTICIPANTE1_SELECT, ID_PARTICIPANTE1_VALUE, nome)

    ' Condição 1: Réu
    Call SelecionarLookup(doc, ID_CONDICAO1_SELECT, ID_CONDICAO1_VALUE, "Réu")

    ' Advogado interno (aleatório)
    Call SelecionarLookup(doc, ID_ADV_INTERNO_SELECT, ID_ADV_INTERNO_VALUE, advInterno)

    ' Advogado externo (aleatório)
    Call SelecionarLookup(doc, ID_ADV_EXTERNO_SELECT, ID_ADV_EXTERNO_VALUE, advExterno)

    ' === PASSO 5: Pedido ===
    Call SelecionarLookup(doc, ID_PEDIDO_SELECT, ID_PEDIDO_VALUE, PEDIDO)
    ' Valor Pedido
    If valorPedido > 0 Then
        Call PreencherTexto(doc, ID_VALOR_PEDIDO, Replace(Format(valorPedido, "0.00"), ".", ","))
    End If
    ' Risco: Possível
    Call SelecionarLookup(doc, ID_RISCO_SELECT, ID_RISCO_VALUE, RISCO)

    ' === PASSO 6: Documentos - Limpar tipo documento e nome "INICIAL" ===
    Call LimparCampo(doc, ID_TIPO_DOC_ARQ_VALUE)
    Call LimparCampo(doc, ID_NOME_ARQUIVO)
    ' Também limpar o select visível
    Call LimparSelect(doc, ID_TIPO_DOC_ARQ_SELECT)

    ' === PASSO 7: Salvar ===
    Set doc = IE.document
    Dim btnSalvar As Object
    Set btnSalvar = BuscarElementoPorTexto(doc, "A", "Salvar")
    If btnSalvar Is Nothing Then Set btnSalvar = BuscarElementoPorTexto(doc, "BUTTON", "Salvar")
    If btnSalvar Is Nothing Then Set btnSalvar = BuscarElementoPorTexto(doc, "SPAN", "Salvar")

    If Not btnSalvar Is Nothing Then
        btnSalvar.Click
        Call AguardarCarregamento
    Else
        CadastrarPastaCivel = "Botão Salvar não encontrado"
        Exit Function
    End If

    ' === PASSO 8: Capturar ID da pasta ===
    Dim idPasta As String
    idPasta = CapturarIdPasta()

    If Len(idPasta) > 0 Then
        CadastrarPastaCivel = "OK|" & idPasta
    Else
        CadastrarPastaCivel = "OK"
    End If
    Exit Function

ErrHandler:
    CadastrarPastaCivel = Err.Description
End Function

'==============================================================================
' FUNÇÕES DE PREENCHIMENTO POR ID EXATO
'==============================================================================
Private Sub SelecionarLookup(doc As Object, idSelect As String, idValue As String, texto As String)
    ' Campos lookup do Benner têm um select visível e um hidden _VALUE.
    ' Preenche o select buscando a opção pelo texto, e seta o _VALUE.
    On Error Resume Next

    Dim selectElem As Object
    Set selectElem = doc.getElementById(idSelect)

    If Not selectElem Is Nothing Then
        ' Buscar opção pelo texto
        Dim opts As Object
        Set opts = selectElem.getElementsByTagName("OPTION")
        Dim j As Long
        For j = 0 To opts.Length - 1
            If InStr(1, opts(j).innerText, texto, vbTextCompare) > 0 Then
                selectElem.selectedIndex = j
                Call FireEvent(selectElem, "change")

                ' Setar o hidden value
                Dim hiddenElem As Object
                Set hiddenElem = doc.getElementById(idValue)
                If Not hiddenElem Is Nothing Then
                    hiddenElem.Value = opts(j).Value
                End If
                Exit For
            End If
        Next j
    End If
    On Error GoTo 0
End Sub

Private Sub PreencherTexto(doc As Object, idCampo As String, valor As String)
    On Error Resume Next
    Dim elem As Object
    Set elem = doc.getElementById(idCampo)
    If Not elem Is Nothing Then
        elem.Value = valor
        elem.Focus
        Call FireEvent(elem, "change")
        Call FireEvent(elem, "input")
        Call FireEvent(elem, "blur")
    End If
    On Error GoTo 0
End Sub

Private Sub ClicarRadio(doc As Object, idRadio As String)
    On Error Resume Next
    Dim elem As Object
    Set elem = doc.getElementById(idRadio)
    If Not elem Is Nothing Then
        elem.Click
        Call FireEvent(elem, "change")
    End If
    On Error GoTo 0
End Sub

Private Sub LimparCampo(doc As Object, idCampo As String)
    On Error Resume Next
    Dim elem As Object
    Set elem = doc.getElementById(idCampo)
    If Not elem Is Nothing Then
        elem.Value = ""
        Call FireEvent(elem, "change")
    End If
    On Error GoTo 0
End Sub

Private Sub LimparSelect(doc As Object, idSelect As String)
    On Error Resume Next
    Dim elem As Object
    Set elem = doc.getElementById(idSelect)
    If Not elem Is Nothing Then
        elem.selectedIndex = 0
        Call FireEvent(elem, "change")
    End If
    On Error GoTo 0
End Sub

'==============================================================================
' FUNÇÃO - CAPTURAR ID DA PASTA CRIADA
'==============================================================================
Private Function CapturarIdPasta() As String
    On Error Resume Next
    Dim doc As Object
    Set doc = IE.document

    ' Tentar da URL
    Dim currentUrl As String
    currentUrl = IE.LocationURL
    If InStr(currentUrl, "id=") > 0 Then
        Dim posId As Long, endPos As Long
        posId = InStr(currentUrl, "id=") + 3
        endPos = InStr(posId, currentUrl, "&")
        If endPos = 0 Then endPos = Len(currentUrl) + 1
        CapturarIdPasta = Mid(currentUrl, posId, endPos - posId)
        Exit Function
    End If

    ' Tentar campo Código na página
    Dim campoCodigo As Object
    Set campoCodigo = BuscarCampoPorLabel(doc, "Código")
    If Not campoCodigo Is Nothing Then
        CapturarIdPasta = campoCodigo.Value
        Exit Function
    End If

    CapturarIdPasta = ""
    On Error GoTo 0
End Function

'==============================================================================
' FUNÇÕES - ADVOGADOS ALEATÓRIOS
'==============================================================================
Private Function SortearAdvogadoInterno() As String
    Select Case Int(Rnd() * 3) + 1
        Case 1: SortearAdvogadoInterno = ADV_INTERNO_1
        Case 2: SortearAdvogadoInterno = ADV_INTERNO_2
        Case 3: SortearAdvogadoInterno = ADV_INTERNO_3
    End Select
End Function

Private Function SortearAdvogadoExterno() As String
    Select Case Int(Rnd() * 5) + 1
        Case 1: SortearAdvogadoExterno = ADV_EXTERNO_1
        Case 2: SortearAdvogadoExterno = ADV_EXTERNO_2
        Case 3: SortearAdvogadoExterno = ADV_EXTERNO_3
        Case 4: SortearAdvogadoExterno = ADV_EXTERNO_4
        Case 5: SortearAdvogadoExterno = ADV_EXTERNO_5
    End Select
End Function

'==============================================================================
' FUNÇÃO - FORMATAR CPF
'==============================================================================
Private Function FormatarCPF(cpfRaw As String) As String
    Dim cpf As String
    cpf = Trim(cpfRaw)
    cpf = Replace(cpf, ".", "")
    cpf = Replace(cpf, "-", "")
    cpf = Replace(cpf, " ", "")
    Do While Len(cpf) < 11
        cpf = "0" & cpf
    Loop
    FormatarCPF = Left(cpf, 3) & "." & Mid(cpf, 4, 3) & "." & Mid(cpf, 7, 3) & "-" & Right(cpf, 2)
End Function

'==============================================================================
' FUNÇÕES AUXILIARES - PESQUISA
'==============================================================================
Private Function PesquisarPartePasta(nome As String) As String
    On Error GoTo ErrHandler
    Dim doc As Object
    Set doc = IE.document

    Dim menuPastas As Object
    Set menuPastas = BuscarElementoPorTexto(doc, "A", "Pastas")
    If menuPastas Is Nothing Then Set menuPastas = BuscarElementoPorTexto(doc, "SPAN", "Pastas")
    If Not menuPastas Is Nothing Then
        menuPastas.Click
        Call AguardarCarregamento
    End If

    Set doc = IE.document
    Dim campoParte As Object
    Set campoParte = BuscarCampoPorLabel(doc, "Parte Pasta")
    If campoParte Is Nothing Then Set campoParte = BuscarInputPorAtributo(doc, "placeholder", "Parte")
    If campoParte Is Nothing Then Set campoParte = BuscarInputPorAtributo(doc, "title", "Parte")

    If campoParte Is Nothing Then
        PesquisarPartePasta = "ERRO: Campo não encontrado"
        Exit Function
    End If

    campoParte.Value = ""
    campoParte.Focus
    campoParte.Value = nome
    Call FireEvent(campoParte, "change")
    Call FireEvent(campoParte, "input")

    Dim btnPesquisar As Object
    Set btnPesquisar = BuscarBotaoPesquisa(doc)
    If Not btnPesquisar Is Nothing Then
        btnPesquisar.Click
    Else
        campoParte.Focus
        Application.SendKeys "{ENTER}", True
    End If
    Call AguardarCarregamento
    Application.Wait Now + TimeValue("00:00:02")

    Set doc = IE.document
    PesquisarPartePasta = LerResultadosPesquisa(doc, nome)

    On Error Resume Next
    Set campoParte = BuscarCampoPorLabel(doc, "Parte Pasta")
    If Not campoParte Is Nothing Then
        campoParte.Value = ""
        Call FireEvent(campoParte, "change")
    End If
    On Error GoTo 0
    Exit Function

ErrHandler:
    PesquisarPartePasta = "ERRO: " & Err.Description
End Function

Private Function LerResultadosPesquisa(doc As Object, nomePesquisado As String) As String
    On Error Resume Next
    Dim tabelas As Object
    Set tabelas = doc.getElementsByTagName("TABLE")
    Dim t As Long, r As Long
    Dim encontrou As Boolean, objetos As String, idPastaEncontrada As String, nomePasta As String
    encontrou = False: objetos = "": idPastaEncontrada = "": nomePasta = ""

    For t = 0 To tabelas.Length - 1
        Dim rows As Object
        Set rows = tabelas(t).getElementsByTagName("TR")
        For r = 0 To rows.Length - 1
            Dim rowText As String
            rowText = UCase(rows(r).innerText)
            If InStr(rowText, UCase(nomePesquisado)) > 0 Then
                encontrou = True
                ' Capturar valor do campo Pasta (primeiro link ou primeira célula)
                If Len(nomePasta) = 0 Then
                    Dim cells As Object
                    Set cells = rows(r).getElementsByTagName("TD")
                    If cells.Length > 0 Then
                        nomePasta = Trim(cells(0).innerText)
                    End If
                End If
                ' Tentar capturar ID da pasta via link
                If Len(idPastaEncontrada) = 0 Then
                    Dim links As Object
                    Set links = rows(r).getElementsByTagName("A")
                    Dim lk As Long
                    For lk = 0 To links.Length - 1
                        Dim href As String
                        href = CStr(links(lk).getAttribute("href"))
                        Dim posId As Long
                        posId = InStr(href, "id=")
                        If posId > 0 Then
                            Dim idStr As String
                            idStr = Mid(href, posId + 3)
                            Dim posAmp As Long
                            posAmp = InStr(idStr, "&")
                            If posAmp > 0 Then idStr = Left(idStr, posAmp - 1)
                            If Len(idStr) > 0 And IsNumeric(idStr) Then
                                idPastaEncontrada = idStr
                                Exit For
                            End If
                        End If
                    Next lk
                End If
                ' Verificar coluna Pedido (segunda célula) especificamente
                Dim cellsObj As Object
                Set cellsObj = rows(r).getElementsByTagName("TD")
                Dim pedidoText As String
                pedidoText = ""
                If cellsObj.Length > 1 Then pedidoText = UCase(Trim(cellsObj(1).innerText))
                If InStr(pedidoText, "DÍVIDA PREVIDENCIÁRIA") > 0 Or InStr(pedidoText, "DIVIDA PREVIDENCIARIA") > 0 Then
                    objetos = objetos & "DÍVIDA PREVIDENCIÁRIA; "
                ElseIf cellsObj.Length > 1 Then
                    objetos = objetos & Left(cellsObj(1).innerText, 50) & "; "
                End If
            End If
        Next r
    Next t
    On Error GoTo 0

    Dim sufixoId As String
    If Len(idPastaEncontrada) > 0 Then
        sufixoId = " | PASTA:" & idPastaEncontrada
    Else
        sufixoId = ""
    End If

    Dim prefixoPasta As String
    If Len(nomePasta) > 0 Then
        prefixoPasta = "[" & nomePasta & "] "
    Else
        prefixoPasta = ""
    End If

    If encontrou Then
        If InStr(UCase(objetos), "DÍVIDA PREVIDENCIÁRIA") > 0 Or InStr(UCase(objetos), "DIVIDA PREVIDENCIARIA") > 0 Then
            LerResultadosPesquisa = prefixoPasta & "ENCONTRADA - MESMO OBJETO (DÍVIDA PREVIDENCIÁRIA)" & sufixoId
        ElseIf Len(objetos) > 0 Then
            LerResultadosPesquisa = prefixoPasta & "ENCONTRADA - OUTRO OBJETO: " & Left(objetos, 100) & sufixoId
        Else
            LerResultadosPesquisa = prefixoPasta & "ENCONTRADA - objeto não identificado" & sufixoId
        End If
    Else
        Dim bodyText As String
        bodyText = UCase(doc.body.innerText)
        If InStr(bodyText, "NENHUM REGISTRO") > 0 Or InStr(bodyText, "NÃO ENCONTR") > 0 Then
            LerResultadosPesquisa = "NÃO ENCONTRADA - OK para cadastrar"
        Else
            LerResultadosPesquisa = "NÃO ENCONTRADA - verificar manualmente"
        End If
    End If
End Function

'==============================================================================
' FUNÇÕES AUXILIARES - NAVEGAÇÃO E ELEMENTOS
'==============================================================================
Private Function InicializarNavegador() As Boolean
    On Error Resume Next
    If Not IE Is Nothing Then
        If IE.readyState >= 0 Then
            InicializarNavegador = True
            Exit Function
        End If
    End If
    Set IE = CreateObject("InternetExplorer.Application")
    If IE Is Nothing Then
        MsgBox "Erro ao criar navegador.", vbCritical
        InicializarNavegador = False
        Exit Function
    End If
    IE.Visible = True
    InicializarNavegador = True
    On Error GoTo 0
End Function

Private Sub AguardarCarregamento()
    Dim timeout As Date
    timeout = Now + TimeValue("00:00:30")
    Do While (IE.Busy Or IE.readyState <> 4) And Now < timeout
        DoEvents
        Application.Wait Now + TimeValue("00:00:01")
    Loop
    Application.Wait Now + TimeValue("00:00:02")
End Sub

Private Function BuscarElementoPorTexto(doc As Object, tag As String, texto As String) As Object
    On Error Resume Next
    Dim elementos As Object
    Set elementos = doc.getElementsByTagName(tag)
    Dim i As Long
    For i = 0 To elementos.Length - 1
        If InStr(1, elementos(i).innerText, texto, vbTextCompare) > 0 Then
            Set BuscarElementoPorTexto = elementos(i)
            Exit Function
        End If
    Next i
    Set BuscarElementoPorTexto = Nothing
    On Error GoTo 0
End Function

Private Function BuscarCampoPorLabel(doc As Object, labelText As String) As Object
    On Error Resume Next
    Dim labels As Object
    Set labels = doc.getElementsByTagName("LABEL")
    Dim i As Long
    For i = 0 To labels.Length - 1
        If InStr(1, labels(i).innerText, labelText, vbTextCompare) > 0 Then
            Dim forId As String
            forId = labels(i).getAttribute("for")
            If Len(forId) > 0 Then
                Set BuscarCampoPorLabel = doc.getElementById(forId)
                If Not BuscarCampoPorLabel Is Nothing Then Exit Function
            End If
            Dim inputs As Object
            Set inputs = labels(i).parentElement.getElementsByTagName("INPUT")
            If inputs.Length > 0 Then
                Set BuscarCampoPorLabel = inputs(0)
                Exit Function
            End If
            Set inputs = labels(i).parentElement.getElementsByTagName("SELECT")
            If inputs.Length > 0 Then
                Set BuscarCampoPorLabel = inputs(0)
                Exit Function
            End If
        End If
    Next i
    Set BuscarCampoPorLabel = Nothing
    On Error GoTo 0
End Function

Private Function BuscarInputPorAtributo(doc As Object, atributo As String, valor As String) As Object
    On Error Resume Next
    Dim inputs As Object
    Set inputs = doc.getElementsByTagName("INPUT")
    Dim i As Long
    For i = 0 To inputs.Length - 1
        If InStr(1, CStr(inputs(i).getAttribute(atributo)), valor, vbTextCompare) > 0 Then
            Set BuscarInputPorAtributo = inputs(i)
            Exit Function
        End If
    Next i
    Set BuscarInputPorAtributo = Nothing
    On Error GoTo 0
End Function

Private Function BuscarBotaoPesquisa(doc As Object) As Object
    On Error Resume Next
    Set BuscarBotaoPesquisa = BuscarElementoPorTexto(doc, "BUTTON", "Pesquisar")
    If Not BuscarBotaoPesquisa Is Nothing Then Exit Function
    Set BuscarBotaoPesquisa = BuscarElementoPorTexto(doc, "A", "Pesquisar")
    If Not BuscarBotaoPesquisa Is Nothing Then Exit Function
    Dim elem As Object
    Set elem = doc.getElementsByClassName("fa-search")
    If elem.Length > 0 Then
        Set BuscarBotaoPesquisa = elem(0).parentElement
        Exit Function
    End If
    Set BuscarBotaoPesquisa = Nothing
    On Error GoTo 0
End Function

Private Sub PreencherCampoPorLabel(doc As Object, labelText As String, valor As String)
    Dim campo As Object
    Set campo = BuscarCampoPorLabel(doc, labelText)
    If Not campo Is Nothing Then
        If UCase(campo.tagName) = "SELECT" Then
            Dim opts As Object
            Set opts = campo.getElementsByTagName("OPTION")
            Dim j As Long
            For j = 0 To opts.Length - 1
                If InStr(1, opts(j).innerText, valor, vbTextCompare) > 0 Then
                    campo.selectedIndex = j
                    Call FireEvent(campo, "change")
                    Exit For
                End If
            Next j
        Else
            campo.Value = valor
            campo.Focus
            Call FireEvent(campo, "change")
            Call FireEvent(campo, "input")
            Call FireEvent(campo, "blur")
        End If
    End If
End Sub

Private Sub FireEvent(elem As Object, eventName As String)
    On Error Resume Next
    Dim evt As Object
    Set evt = IE.document.createEvent("HTMLEvents")
    evt.initEvent eventName, True, True
    elem.dispatchEvent evt
    On Error GoTo 0
End Sub

'==============================================================================
' UTILITÁRIOS
'==============================================================================
Public Sub FecharNavegador()
    On Error Resume Next
    If Not IE Is Nothing Then
        IE.Quit
        Set IE = Nothing
    End If
    On Error GoTo 0
End Sub

Public Sub GerarRelatorioStatus()
    Dim wsData As Worksheet
    Set wsData = ThisWorkbook.Sheets("Planilha1")
    Dim lastRow As Long
    lastRow = wsData.Cells(wsData.Rows.Count, COL_NOME).End(xlUp).Row

    Dim pendentes As Long, cadastrados As Long, erros As Long
    Dim duplicatas As Long, jaCadastrados As Long, verificar As Long
    Dim i As Long
    For i = 2 To lastRow
        Dim st As String
        st = UCase(Trim(CStr(wsData.Cells(i, COL_STATUS).Value)))
        Select Case st
            Case "PENDENTE": pendentes = pendentes + 1
            Case "CADASTRADO", "CADASTRADO + ANDAMENTO": cadastrados = cadastrados + 1
            Case "NÃO CADASTRAR": duplicatas = duplicatas + 1
            Case "VERIFICAR": verificar = verificar + 1
            Case Else
                If InStr(st, "JÁ CADASTRADO") > 0 Then
                    jaCadastrados = jaCadastrados + 1
                ElseIf InStr(st, "ERRO") > 0 Then
                    erros = erros + 1
                End If
        End Select
    Next i

    MsgBox "Total: " & (lastRow - 1) & vbCrLf & _
           "Pendentes: " & pendentes & vbCrLf & _
           "Cadastradas: " & cadastrados & vbCrLf & _
           "Duplicatas: " & duplicatas & vbCrLf & _
           "Já no Benner: " & jaCadastrados & vbCrLf & _
           "Verificar: " & verificar & vbCrLf & _
           "Erros: " & erros, vbInformation, "Relatório"
End Sub
