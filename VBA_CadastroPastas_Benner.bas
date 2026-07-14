Attribute VB_Name = "ModCadastroPastas"
'==============================================================================
' MÓDULO VBA - CADASTRO DE PASTAS NO BENNER (PREVI JURÍDICO)
' ==============================================================================
' Este módulo automatiza o cadastro de pastas no sistema Benner Web
' URL: https://previ.bennercloud.com.br/JURIDICO/jur/e/PREVI.aspx?i=K9_INICIOPREVI&m=MAIN
'
' REQUISITOS:
' - Microsoft Internet Controls (referência)
' - Microsoft HTML Object Library (referência)
' - Planilha "Planilha1" com dados das operações
'
' PARÂMETROS DE CADASTRO:
'   Objeto: DÍVIDA PREVIDENCIÁRIA
'   Chance Êxito: Possível
'   Valor P. Condenação: Valor da dívida (col O)
'   Plano: Conforme planilha (col A: 1=Plano 1, 2=Plano PREVI Futuro)
'   Programa: Previdencial
'   Gerência: GESOP
'   Processo: Não distribuído
'   Número CNJ: DP + número do contrato (col F)
'   Situação: Baixa Provisória
'   Condução: Recuperação de Créditos
'
' ANDAMENTO: PEDIDO DE AJUIZAMENTO DE AÇÃO
'   PROVIDÊNCIA 1: "PREVI AUTORA – DOCUMENTAÇÃO INICIAL" -> GESOP, 10 dias úteis
'   PROVIDÊNCIA 2: "PROVIDENCIAR AJUIZAMENTO" -> Escritório Contratado, 15 dias úteis
'==============================================================================

Option Explicit

' Constantes do sistema
Private Const URL_BENNER As String = "https://previ.bennercloud.com.br/JURIDICO/jur/e/PREVI.aspx?i=K9_INICIOPREVI&m=MAIN"
Private Const OBJETO As String = "DÍVIDA PREVIDENCIÁRIA"
Private Const CHANCE_EXITO As String = "Possível"
Private Const PROGRAMA As String = "Previdencial"
Private Const GERENCIA As String = "GESOP"
Private Const SITUACAO As String = "Baixa Provisória"
Private Const CONDUCAO As String = "Recuperação de Créditos"
Private Const ANDAMENTO As String = "PEDIDO DE AJUIZAMENTO DE AÇÃO"
Private Const PROV1_TITULO As String = "PREVI AUTORA – DOCUMENTAÇÃO INICIAL"
Private Const PROV1_DESTINO As String = "GESOP"
Private Const PROV1_PRAZO As Integer = 10  ' dias úteis
Private Const PROV2_TITULO As String = "PROVIDENCIAR AJUIZAMENTO"
Private Const PROV2_DESTINO As String = "Escritório Contratado"
Private Const PROV2_PRAZO As Integer = 15  ' dias úteis

' Variáveis globais
Private IE As Object ' InternetExplorer
Private ws As Worksheet

'==============================================================================
' SUB PRINCIPAL - ANÁLISE PRÉVIA
'==============================================================================
Public Sub AnalisePreviaDuplicidades()
    '
    ' Realiza análise prévia para:
    ' 1. Identificar participantes com mais de uma operação
    ' 2. Marcar duplicatas exatas (mesmo contrato e valor)
    ' 3. Identificar pastas já cadastradas (coluna Benner)
    ' 4. Gerar número CNJ (DP + contrato)
    '
    Dim wsData As Worksheet
    Set wsData = ThisWorkbook.Sheets("Planilha1")

    Dim lastRow As Long
    lastRow = wsData.Cells(wsData.Rows.Count, 4).End(xlUp).Row

    ' Limpar colunas de análise
    wsData.Range("AC2:AE" & lastRow).ClearContents

    ' Headers
    wsData.Cells(1, 29).Value = "ANÁLISE DUPLICIDADE"
    wsData.Cells(1, 30).Value = "STATUS CADASTRO"
    wsData.Cells(1, 31).Value = "NÚMERO CNJ"
    wsData.Cells(1, 32).Value = "PLANO DESCRIÇÃO"

    ' Dicionário para contar nomes
    Dim dictNomes As Object
    Set dictNomes = CreateObject("Scripting.Dictionary")

    Dim i As Long
    Dim nome As String
    Dim contrato As String
    Dim valor As Double
    Dim chave As String

    ' Primeira passagem: contar ocorrências por nome
    For i = 2 To lastRow
        nome = Trim(CStr(wsData.Cells(i, 4).Value))
        If Not dictNomes.Exists(nome) Then
            dictNomes.Add nome, 1
        Else
            dictNomes(nome) = dictNomes(nome) + 1
        End If
    Next i

    ' Dicionário para detectar duplicatas exatas
    Dim dictExatas As Object
    Set dictExatas = CreateObject("Scripting.Dictionary")

    ' Segunda passagem: marcar análise
    For i = 2 To lastRow
        nome = Trim(CStr(wsData.Cells(i, 4).Value))
        contrato = CStr(wsData.Cells(i, 6).Value)
        valor = CDbl(wsData.Cells(i, 15).Value)
        chave = nome & "|" & contrato & "|" & CStr(valor)

        ' Gerar número CNJ
        wsData.Cells(i, 31).Value = "DP" & contrato

        ' Mapear plano
        Select Case wsData.Cells(i, 1).Value
            Case 1: wsData.Cells(i, 32).Value = "Plano 1"
            Case 2: wsData.Cells(i, 32).Value = "Plano PREVI Futuro"
        End Select

        ' Verificar duplicata exata
        If dictExatas.Exists(chave) Then
            wsData.Cells(i, 29).Value = "DUPLICATA EXATA - REMOVER"
            wsData.Cells(i, 30).Value = "NÃO CADASTRAR"
        ElseIf dictNomes(nome) > 1 Then
            wsData.Cells(i, 29).Value = "MESMO PARTICIPANTE - " & dictNomes(nome) & " OPERAÇÕES"
            wsData.Cells(i, 30).Value = "VERIFICAR"
        Else
            wsData.Cells(i, 29).Value = "OK"
            wsData.Cells(i, 30).Value = "PENDENTE"
        End If

        dictExatas(chave) = i

        ' Verificar se já tem registro no Benner (coluna AB)
        If Len(Trim(CStr(wsData.Cells(i, 28).Value))) > 0 Then
            wsData.Cells(i, 29).Value = wsData.Cells(i, 29).Value & " | JÁ NO BENNER (" & wsData.Cells(i, 28).Value & ")"
            wsData.Cells(i, 30).Value = "JÁ CADASTRADO"
        End If
    Next i

    ' Formatar
    wsData.Columns("AC:AF").AutoFit

    MsgBox "Análise concluída!" & vbCrLf & vbCrLf & _
           "Total de operações: " & (lastRow - 1) & vbCrLf & _
           "Duplicatas exatas encontradas: verifique coluna AC" & vbCrLf & _
           "Participantes com múltiplas operações: verifique coluna AC" & vbCrLf & vbCrLf & _
           "Revise a coluna 'STATUS CADASTRO' (AD) antes de prosseguir com o cadastro.", _
           vbInformation, "Análise Prévia"
End Sub

'==============================================================================
' SUB PRINCIPAL - CADASTRO AUTOMATIZADO
'==============================================================================
Public Sub CadastrarPastasBenner()
    '
    ' Cadastra as pastas no Benner Web para todas as linhas com STATUS = "PENDENTE"
    ' IMPORTANTE: Executar AnalisePreviaDuplicidades() antes!
    '
    Dim wsData As Worksheet
    Set wsData = ThisWorkbook.Sheets("Planilha1")

    Dim lastRow As Long
    lastRow = wsData.Cells(wsData.Rows.Count, 4).End(xlUp).Row

    ' Verificar se análise foi feita
    If wsData.Cells(1, 30).Value <> "STATUS CADASTRO" Then
        MsgBox "Execute primeiro a Análise Prévia (AnalisePreviaDuplicidades)!", vbExclamation
        Exit Sub
    End If

    ' Confirmar
    Dim resp As VbMsgBoxResult
    resp = MsgBox("Deseja iniciar o cadastro das pastas no Benner?" & vbCrLf & _
                  "Apenas linhas com STATUS 'PENDENTE' serão processadas." & vbCrLf & vbCrLf & _
                  "Certifique-se de estar logado no sistema Benner.", _
                  vbYesNo + vbQuestion, "Cadastro de Pastas")
    If resp = vbNo Then Exit Sub

    ' Inicializar navegador
    On Error Resume Next
    Set IE = CreateObject("InternetExplorer.Application")
    If IE Is Nothing Then
        MsgBox "Erro ao criar instância do Internet Explorer." & vbCrLf & _
               "Este macro requer o Internet Explorer ou compatível.", vbCritical
        Exit Sub
    End If
    On Error GoTo 0

    IE.Visible = True
    IE.navigate URL_BENNER
    Call AguardarCarregamento

    Dim cadastrados As Long
    cadastrados = 0

    Dim i As Long
    For i = 2 To lastRow
        ' Só cadastrar se status = PENDENTE
        If UCase(Trim(CStr(wsData.Cells(i, 30).Value))) = "PENDENTE" Then
            Dim nome As String
            Dim contrato As String
            Dim valorDivida As Double
            Dim plano As String
            Dim numeroCNJ As String

            nome = Trim(CStr(wsData.Cells(i, 4).Value))
            contrato = CStr(wsData.Cells(i, 6).Value)
            valorDivida = CDbl(wsData.Cells(i, 15).Value)
            plano = CStr(wsData.Cells(i, 32).Value)
            numeroCNJ = "DP" & contrato

            ' Cadastrar pasta
            Dim resultado As String
            resultado = CadastrarUmaPasta(nome, contrato, valorDivida, plano, numeroCNJ)

            If resultado = "OK" Then
                wsData.Cells(i, 30).Value = "CADASTRADO"
                cadastrados = cadastrados + 1

                ' Lançar andamento
                Call LancarAndamento(numeroCNJ)
                wsData.Cells(i, 30).Value = "CADASTRADO + ANDAMENTO"
            Else
                wsData.Cells(i, 30).Value = "ERRO: " & resultado
            End If

            ' Pausa entre cadastros para não sobrecarregar
            Application.Wait Now + TimeValue("00:00:02")
        End If
    Next i

    IE.Quit
    Set IE = Nothing

    MsgBox "Cadastro concluído!" & vbCrLf & _
           "Pastas cadastradas: " & cadastrados, vbInformation
End Sub

'==============================================================================
' FUNÇÃO - CADASTRAR UMA PASTA
'==============================================================================
Private Function CadastrarUmaPasta(nome As String, contrato As String, _
                                    valorDivida As Double, plano As String, _
                                    numeroCNJ As String) As String
    On Error GoTo ErrHandler

    ' Navegar para nova pasta
    ' NOTA: Os seletores abaixo devem ser ajustados conforme a estrutura real
    ' da página do Benner. Os IDs e nomes de campos podem variar.

    ' Clicar em "Nova Pasta" ou equivalente
    Call ClicarElemento("btnNovaPasta")
    Call AguardarCarregamento

    ' Preencher campos
    Call PreencherCampo("txtObjeto", OBJETO)
    Call PreencherCampo("txtChanceExito", CHANCE_EXITO)
    Call PreencherCampo("txtValorCondenacao", Format(valorDivida, "#,##0.00"))
    Call PreencherCampo("txtPlano", plano)
    Call PreencherCampo("txtPrograma", PROGRAMA)
    Call PreencherCampo("txtGerencia", GERENCIA)
    Call PreencherCampo("txtNumeroCNJ", numeroCNJ)
    Call PreencherCampo("txtSituacao", SITUACAO)
    Call PreencherCampo("txtConducao", CONDUCAO)

    ' Marcar "Processo não distribuído"
    Call MarcarCheckbox("chkNaoDistribuido")

    ' Salvar
    Call ClicarElemento("btnSalvar")
    Call AguardarCarregamento

    CadastrarUmaPasta = "OK"
    Exit Function

ErrHandler:
    CadastrarUmaPasta = Err.Description
End Function

'==============================================================================
' SUB - LANÇAR ANDAMENTO
'==============================================================================
Private Sub LancarAndamento(numeroCNJ As String)
    On Error Resume Next

    ' Navegar para aba de andamentos
    Call ClicarElemento("tabAndamentos")
    Call AguardarCarregamento

    ' Novo andamento
    Call ClicarElemento("btnNovoAndamento")
    Call AguardarCarregamento

    ' Preencher tipo de andamento
    Call PreencherCampo("txtTipoAndamento", ANDAMENTO)

    ' Salvar andamento (gera providências automaticamente)
    Call ClicarElemento("btnSalvarAndamento")
    Call AguardarCarregamento

    ' As providências são geradas automaticamente pelo sistema:
    ' PROV 1: "PREVI AUTORA – DOCUMENTAÇÃO INICIAL" -> GESOP, 10 dias úteis
    ' PROV 2: "PROVIDENCIAR AJUIZAMENTO" -> Escritório Contratado, 15 dias úteis

    On Error GoTo 0
End Sub

'==============================================================================
' FUNÇÕES AUXILIARES DE AUTOMAÇÃO WEB
'==============================================================================
Private Sub AguardarCarregamento()
    Do While IE.Busy Or IE.readyState <> 4
        DoEvents
        Application.Wait Now + TimeValue("00:00:01")
    Loop
    Application.Wait Now + TimeValue("00:00:02")
End Sub

Private Sub PreencherCampo(idCampo As String, valor As String)
    ' Tenta encontrar o elemento por ID ou Name
    Dim doc As Object
    Set doc = IE.document

    Dim elem As Object
    Set elem = Nothing

    ' Tentar por ID
    On Error Resume Next
    Set elem = doc.getElementById(idCampo)
    On Error GoTo 0

    If Not elem Is Nothing Then
        elem.Value = valor
        elem.Focus
        Call FireEvent(elem, "change")
    End If
End Sub

Private Sub ClicarElemento(idElemento As String)
    Dim doc As Object
    Set doc = IE.document

    Dim elem As Object
    On Error Resume Next
    Set elem = doc.getElementById(idElemento)
    On Error GoTo 0

    If Not elem Is Nothing Then
        elem.Click
    End If
End Sub

Private Sub MarcarCheckbox(idCheck As String)
    Dim doc As Object
    Set doc = IE.document

    Dim elem As Object
    On Error Resume Next
    Set elem = doc.getElementById(idCheck)
    On Error GoTo 0

    If Not elem Is Nothing Then
        If Not elem.Checked Then elem.Click
    End If
End Sub

Private Sub FireEvent(elem As Object, eventName As String)
    Dim evt As Object
    Set evt = IE.document.createEvent("HTMLEvents")
    evt.initEvent eventName, True, True
    elem.dispatchEvent evt
End Sub

'==============================================================================
' SUB - PESQUISAR PASTA EXISTENTE (para verificação manual)
'==============================================================================
Public Sub PesquisarPastaExistente()
    '
    ' Pesquisa no Benner se já existe pasta cadastrada para o participante
    ' selecionado na planilha (célula ativa na coluna D - NOME)
    '
    Dim wsData As Worksheet
    Set wsData = ThisWorkbook.Sheets("Planilha1")

    Dim nome As String
    nome = wsData.Cells(ActiveCell.Row, 4).Value

    If Len(nome) = 0 Then
        MsgBox "Selecione uma linha com dados.", vbExclamation
        Exit Sub
    End If

    ' Abrir navegador e pesquisar
    Set IE = CreateObject("InternetExplorer.Application")
    IE.Visible = True
    IE.navigate URL_BENNER
    Call AguardarCarregamento

    ' Pesquisar por nome
    ' NOTA: Ajustar seletor conforme estrutura real da página
    Call PreencherCampo("txtPesquisa", nome)
    Call ClicarElemento("btnPesquisar")
    Call AguardarCarregamento

    MsgBox "Verifique o resultado da pesquisa no navegador para: " & nome, vbInformation
End Sub

'==============================================================================
' SUB - RELATÓRIO DE STATUS
'==============================================================================
Public Sub GerarRelatorioStatus()
    '
    ' Gera um resumo do status atual do cadastramento
    '
    Dim wsData As Worksheet
    Set wsData = ThisWorkbook.Sheets("Planilha1")

    Dim lastRow As Long
    lastRow = wsData.Cells(wsData.Rows.Count, 4).End(xlUp).Row

    Dim pendentes As Long, cadastrados As Long, erros As Long
    Dim duplicatas As Long, jaCadastrados As Long

    Dim i As Long
    For i = 2 To lastRow
        Select Case UCase(Trim(CStr(wsData.Cells(i, 30).Value)))
            Case "PENDENTE": pendentes = pendentes + 1
            Case "CADASTRADO", "CADASTRADO + ANDAMENTO": cadastrados = cadastrados + 1
            Case "NÃO CADASTRAR": duplicatas = duplicatas + 1
            Case "JÁ CADASTRADO": jaCadastrados = jaCadastrados + 1
            Case Else
                If InStr(UCase(CStr(wsData.Cells(i, 30).Value)), "ERRO") > 0 Then
                    erros = erros + 1
                End If
        End Select
    Next i

    MsgBox "=== RELATÓRIO DE STATUS ===" & vbCrLf & vbCrLf & _
           "Total de operações: " & (lastRow - 1) & vbCrLf & _
           "Pendentes: " & pendentes & vbCrLf & _
           "Cadastrados com sucesso: " & cadastrados & vbCrLf & _
           "Duplicatas (não cadastrar): " & duplicatas & vbCrLf & _
           "Já cadastrados no Benner: " & jaCadastrados & vbCrLf & _
           "Erros: " & erros, vbInformation, "Relatório"
End Sub
