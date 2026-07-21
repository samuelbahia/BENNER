Attribute VB_Name = "ModCadastroPastas"
'==============================================================================
' MÓDULO VBA - CADASTRO DE PASTAS NO BENNER (PREVI JURÍDICO)
'==============================================================================
' Automatiza:
' 1. Pesquisa prévia no Benner (Pastas > campo "Parte Pasta") para cada
'    participante da planilha, identificando pastas já existentes.
' 2. Cadastro via +Novo > Cadastro rápido de pasta (Categoria: Cível).
' 3. Lançamento do andamento "PEDIDO DE AJUIZAMENTO DE AÇÃO".
'
' URL: https://previ.bennercloud.com.br/JURIDICO/jur/e/PREVI.aspx?i=K9_INICIOPREVI&m=MAIN
'
' CAMPOS DO CADASTRO RÁPIDO (após selecionar Cível):
'   Filial: Plano de Benefícios 1 (col A planilha)
'   Gerência: conforme col Q da planilha
'   Tipo: Cobrança
'   Causa de Pedir: Previdencial
'   Causa Raiz: Produto
'   Processo: Cobrança
'   Órgão: Tribunal de Justiça conforme UF (col T)
'   UF: conforme col T
'   Já distribuído judicialmente: Não
'   Data: hoje
'   Tipo de documento: (excluir/limpar)
'   Número: DP + contrato (col F)
'   Andamento: PEDIDO DE AJUIZAMENTO DE AÇÃO
'   Data andamento: hoje
'   Participante adverso: Nome (col D) + CPF (col W), condição Réu
'   Participante PREVI: condição Autor
'   Advogado interno: aleatório
'   Advogado externo: aleatório
'   Pedido: Dívida Previdenciária
'   Grid documentos: excluir linha com "inicial"
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

    ' Limpar colunas de análise
    wsData.Range(wsData.Cells(2, COL_ANALISE), wsData.Cells(lastRow, COL_ID_PASTA)).ClearContents

    ' Headers
    wsData.Cells(1, COL_ANALISE).Value = "ANÁLISE DUPLICIDADE"
    wsData.Cells(1, COL_STATUS).Value = "STATUS CADASTRO"
    wsData.Cells(1, COL_CNJ).Value = "NÚMERO CNJ"
    wsData.Cells(1, COL_PLANO_DESC).Value = "PLANO DESCRIÇÃO"
    wsData.Cells(1, COL_PESQUISA_BENNER).Value = "PESQUISA BENNER"
    wsData.Cells(1, COL_ID_PASTA).Value = "ID PASTA BENNER"

    ' Contar nomes
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

    ' Detectar duplicatas exatas e marcar
    Dim dictExatas As Object
    Set dictExatas = CreateObject("Scripting.Dictionary")
    Dim contrato As String, valor As Double, chave As String

    For i = 2 To lastRow
        nome = UCase(Trim(CStr(wsData.Cells(i, COL_NOME).Value)))
        contrato = CStr(wsData.Cells(i, COL_CONTRATO).Value)
        valor = CDbl(wsData.Cells(i, COL_VALOR_DIVIDA).Value)
        chave = nome & "|" & contrato & "|" & CStr(valor)

        ' Gerar número CNJ
        wsData.Cells(i, COL_CNJ).Value = "DP" & contrato

        ' Mapear plano
        Select Case wsData.Cells(i, COL_PLANO).Value
            Case 1: wsData.Cells(i, COL_PLANO_DESC).Value = "Plano de Benefícios 1"
            Case 2: wsData.Cells(i, COL_PLANO_DESC).Value = "Plano PREVI Futuro"
        End Select

        ' Classificar
        If dictExatas.Exists(chave) Then
            wsData.Cells(i, COL_ANALISE).Value = "DUPLICATA EXATA - REMOVER"
            wsData.Cells(i, COL_STATUS).Value = "NÃO CADASTRAR"
        ElseIf dictNomes(nome) > 1 Then
            wsData.Cells(i, COL_ANALISE).Value = "MESMO PARTICIPANTE - " & dictNomes(nome) & " OPERAÇÕES"
            wsData.Cells(i, COL_STATUS).Value = "VERIFICAR"
        Else
            wsData.Cells(i, COL_ANALISE).Value = "OK"
            wsData.Cells(i, COL_STATUS).Value = "PENDENTE"
        End If
        dictExatas(chave) = i

        ' Verificar coluna Benner existente
        If Len(Trim(CStr(wsData.Cells(i, COL_BENNER).Value))) > 0 Then
            wsData.Cells(i, COL_ANALISE).Value = wsData.Cells(i, COL_ANALISE).Value & _
                " | JÁ NO BENNER (" & wsData.Cells(i, COL_BENNER).Value & ")"
            wsData.Cells(i, COL_STATUS).Value = "JÁ CADASTRADO"
        End If
    Next i

    wsData.Columns(COL_ANALISE).EntireColumn.AutoFit
    wsData.Columns(COL_STATUS).EntireColumn.AutoFit
    wsData.Columns(COL_ID_PASTA).EntireColumn.AutoFit

    MsgBox "Etapa 1 concluída - Análise local." & vbCrLf & vbCrLf & _
           "Total: " & (lastRow - 1) & " operações." & vbCrLf & _
           "Próximo passo: Execute 'VerificarNoBenner' para pesquisar " & _
           "pastas existentes online.", vbInformation, "Análise Prévia"
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
        MsgBox "Execute primeiro a Etapa 1 (AnalisePreviaDuplicidades)!", vbExclamation
        Exit Sub
    End If

    Dim resp As VbMsgBoxResult
    resp = MsgBox("Pesquisará cada participante no Benner (Pastas > Parte Pasta)." & vbCrLf & _
                  "Certifique-se de estar LOGADO no sistema." & vbCrLf & _
                  "Deseja continuar?", vbYesNo + vbQuestion, "Pesquisa no Benner")
    If resp = vbNo Then Exit Sub

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

            If InStr(UCase(resultadoPesquisa), "ENCONTRADA") > 0 Then
                If InStr(UCase(resultadoPesquisa), "DÍVIDA PREVIDENCIÁRIA") > 0 Or _
                   InStr(UCase(resultadoPesquisa), "DIVIDA PREVIDENCIARIA") > 0 Then
                    wsData.Cells(i, COL_STATUS).Value = "JÁ CADASTRADO NO BENNER"
                    jaExistentes = jaExistentes + 1
                Else
                    wsData.Cells(i, COL_ANALISE).Value = wsData.Cells(i, COL_ANALISE).Value & _
                        " | PASTA EXISTENTE OUTRO OBJETO"
                End If
            ElseIf InStr(UCase(resultadoPesquisa), "NÃO ENCONTRADA") > 0 Then
                If statusAtual = "VERIFICAR" Then
                    wsData.Cells(i, COL_STATUS).Value = "PENDENTE"
                End If
            End If

            Application.Wait Now + TimeValue("00:00:02")
            Application.StatusBar = "Pesquisando... " & pesquisados & "/" & (lastRow - 1)
        End If
ProximaLinha:
    Next i

    Application.StatusBar = False
    MsgBox "Etapa 2 concluída." & vbCrLf & _
           "Pesquisados: " & pesquisados & vbCrLf & _
           "Já existentes: " & jaExistentes & vbCrLf & vbCrLf & _
           "Próximo: Execute 'CadastrarPastasBenner'.", vbInformation, "Pesquisa Concluída"
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

    ' Contar pendentes
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

    Dim resp As VbMsgBoxResult
    resp = MsgBox("Serão cadastradas " & totalPendentes & " pastas." & vbCrLf & _
                  "+Novo > Cadastro rápido > Cível" & vbCrLf & _
                  "Certifique-se de estar LOGADO." & vbCrLf & _
                  "Continuar?", vbYesNo + vbQuestion, "Cadastro de Pastas")
    If resp = vbNo Then Exit Sub

    If Not InicializarNavegador() Then Exit Sub
    IE.navigate URL_BENNER
    Call AguardarCarregamento

    ' Inicializar randomização
    Randomize Timer

    Dim cadastrados As Long, erros As Long
    cadastrados = 0: erros = 0

    For i = 2 To lastRow
        If UCase(Trim(CStr(wsData.Cells(i, COL_STATUS).Value))) = "PENDENTE" Then
            Dim nome As String, contrato As String, valorDivida As Double
            Dim gerencia As String, uf As String, cpf As String
            Dim filial As String, numeroCNJ As String

            nome = Trim(CStr(wsData.Cells(i, COL_NOME).Value))
            contrato = CStr(wsData.Cells(i, COL_CONTRATO).Value)
            valorDivida = CDbl(wsData.Cells(i, COL_VALOR_DIVIDA).Value)
            gerencia = Trim(CStr(wsData.Cells(i, COL_GERENCIA).Value))
            uf = Trim(CStr(wsData.Cells(i, COL_UF).Value))
            cpf = FormatarCPF(CStr(wsData.Cells(i, COL_CPF).Value))
            filial = CStr(wsData.Cells(i, COL_PLANO_DESC).Value)
            numeroCNJ = "DP" & contrato

            ' Selecionar advogados aleatórios
            Dim advInterno As String, advExterno As String
            advInterno = SortearAdvogadoInterno()
            advExterno = SortearAdvogadoExterno()

            ' Cadastrar
            Dim resultado As String
            resultado = CadastrarPastaCivel(nome, contrato, valorDivida, gerencia, _
                                            uf, cpf, filial, numeroCNJ, advInterno, advExterno)

            If Left(resultado, 2) = "OK" Then
                wsData.Cells(i, COL_STATUS).Value = "CADASTRADO + ANDAMENTO"
                ' Extrair ID da pasta se retornado
                If Len(resultado) > 3 Then
                    wsData.Cells(i, COL_ID_PASTA).Value = Mid(resultado, 4)
                End If
                cadastrados = cadastrados + 1
            Else
                wsData.Cells(i, COL_STATUS).Value = "ERRO: " & resultado
                erros = erros + 1
            End If

            Application.StatusBar = "Cadastrando... " & cadastrados & "/" & totalPendentes
            Application.Wait Now + TimeValue("00:00:03")
        End If
    Next i

    Application.StatusBar = False
    MsgBox "Cadastro concluído!" & vbCrLf & _
           "Sucesso: " & cadastrados & vbCrLf & _
           "Erros: " & erros, vbInformation, "Resultado"
End Sub

'==============================================================================
' FUNÇÃO - CADASTRAR PASTA CÍVEL (FORMULÁRIO COMPLETO)
'==============================================================================
Private Function CadastrarPastaCivel(nome As String, contrato As String, _
                                      valorDivida As Double, gerencia As String, _
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
    If btnNovo Is Nothing Then Set btnNovo = BuscarElementoPorClasse(doc, "btn-novo")

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
    If linkCadRapido Is Nothing Then
        Set linkCadRapido = BuscarElementoPorTexto(doc, "SPAN", "Cadastro rápido")
    End If

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
    Call AguardarCarregamento ' aguarda tela recarregar após seleção

    ' === PASSO 3: Preencher campos do formulário Cível ===
    Set doc = IE.document

    ' Filial: Plano de Benefícios 1
    Call PreencherCampoPorLabel(doc, "Filial", filial)

    ' Gerência: conforme planilha
    Call PreencherCampoPorLabel(doc, "Gerência", gerencia)
    Call PreencherCampoPorLabel(doc, "Ger" & Chr(234) & "ncia", gerencia)

    ' Tipo: Cobrança
    Call PreencherCampoPorLabel(doc, "Tipo", TIPO_PASTA)

    ' Causa de Pedir: Previdencial
    Call PreencherCampoPorLabel(doc, "Causa de Pedir", CAUSA_PEDIR)
    Call PreencherCampoPorLabel(doc, "Causa Pedir", CAUSA_PEDIR)

    ' Causa Raiz: Produto
    Call PreencherCampoPorLabel(doc, "Causa Raiz", CAUSA_RAIZ)

    ' Processo: Cobrança
    Call PreencherCampoPorLabel(doc, "Processo", PROCESSO)

    ' Órgão: Tribunal de Justiça (conforme UF)
    Dim orgao As String
    orgao = "Tribunal de Justiça"
    Call PreencherCampoPorLabel(doc, "Órgão", orgao)
    Call PreencherCampoPorLabel(doc, "Orgão", orgao)

    ' UF
    Call PreencherCampoPorLabel(doc, "UF", uf)

    ' Já distribuído judicialmente: Não
    Call PreencherCampoPorLabel(doc, "distribuído", "Não")
    Call PreencherCampoPorLabel(doc, "distribu", "Não")

    ' Data: hoje
    Dim dataHoje As String
    dataHoje = Format(Date, "dd/mm/yyyy")
    Call PreencherCampoPorLabel(doc, "Data", dataHoje)

    ' Número: DP + contrato
    Call PreencherCampoPorLabel(doc, "Número", numeroCNJ)
    Call PreencherCampoPorLabel(doc, "Numero", numeroCNJ)

    ' Andamento: PEDIDO DE AJUIZAMENTO DE AÇÃO
    Call PreencherCampoPorLabel(doc, "Andamento", ANDAMENTO)

    ' Data andamento: hoje
    Call PreencherCampoPorLabel(doc, "Data andamento", dataHoje)
    Call PreencherCampoPorLabel(doc, "Data Andamento", dataHoje)

    ' === PASSO 4: Participante adverso (réu) ===
    ' Pesquisar se já cadastrado, senão cadastrar com Nome + CPF
    Call CadastrarParticipante(doc, nome, cpf, "Réu")

    ' === PASSO 5: Participante PREVI (autor) ===
    Call AdicionarParticipantePrevi(doc, "Autor")

    ' === PASSO 6: Advogado interno (aleatório) ===
    Call PreencherCampoPorLabel(doc, "Advogado Interno", advInterno)
    Call PreencherCampoPorLabel(doc, "Advogado interno", advInterno)

    ' === PASSO 7: Advogado externo (aleatório) ===
    Call PreencherCampoPorLabel(doc, "Advogado Externo", advExterno)
    Call PreencherCampoPorLabel(doc, "Advogado externo", advExterno)
    Call PreencherCampoPorLabel(doc, "Escritório", advExterno)

    ' === PASSO 8: Pedido ===
    Call PreencherCampoPorLabel(doc, "Pedido", PEDIDO)

    ' === PASSO 9: Limpar grid documentos (excluir tipo documento e "inicial") ===
    Call ExcluirDocumentoInicial(doc)

    ' === PASSO 10: Salvar ===
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

    ' === PASSO 11: Capturar ID da pasta criada ===
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
' SUB - CADASTRAR PARTICIPANTE (ADVERSO/RÉU)
'==============================================================================
Private Sub CadastrarParticipante(doc As Object, nome As String, cpf As String, condicao As String)
    On Error Resume Next

    ' Tentar pesquisar participante existente
    Dim campoParticipante As Object
    Set campoParticipante = BuscarCampoPorLabel(doc, "Participante")
    If campoParticipante Is Nothing Then
        Set campoParticipante = BuscarCampoPorLabel(doc, "Parte")
    End If

    If Not campoParticipante Is Nothing Then
        ' Preencher com nome para busca
        campoParticipante.Value = nome
        campoParticipante.Focus
        Call FireEvent(campoParticipante, "change")
        Call FireEvent(campoParticipante, "input")
        Application.Wait Now + TimeValue("00:00:02")

        ' Verificar se apareceu sugestão/autocomplete
        Set doc = IE.document
        Dim sugestao As Object
        Set sugestao = BuscarElementoPorTexto(doc, "LI", nome)
        If sugestao Is Nothing Then
            Set sugestao = BuscarElementoPorTexto(doc, "DIV", nome)
        End If

        If Not sugestao Is Nothing Then
            ' Participante já cadastrado - selecionar
            sugestao.Click
            Call AguardarCarregamento
        Else
            ' Participante não cadastrado - preencher dados
            Call PreencherCampoPorLabel(doc, "Nome", nome)
            Call PreencherCampoPorLabel(doc, "CPF", cpf)
        End If
    End If

    ' Condição: Réu
    Call PreencherCampoPorLabel(doc, "Condição", condicao)
    Call PreencherCampoPorLabel(doc, "Condi", condicao)

    On Error GoTo 0
End Sub

'==============================================================================
' SUB - ADICIONAR PREVI COMO PARTICIPANTE AUTOR
'==============================================================================
Private Sub AdicionarParticipantePrevi(doc As Object, condicao As String)
    On Error Resume Next

    ' Buscar campo para adicionar segundo participante (PREVI)
    ' Pesquisar PREVI no campo participante
    Dim campoParte As Object
    Set campoParte = BuscarCampoPorLabel(doc, "Participante")
    If campoParte Is Nothing Then
        Set campoParte = BuscarCampoPorLabel(doc, "Autor")
    End If

    If Not campoParte Is Nothing Then
        campoParte.Value = "PREVI"
        campoParte.Focus
        Call FireEvent(campoParte, "change")
        Call FireEvent(campoParte, "input")
        Application.Wait Now + TimeValue("00:00:02")

        ' Selecionar PREVI na sugestão
        Set doc = IE.document
        Dim sugestao As Object
        Set sugestao = BuscarElementoPorTexto(doc, "LI", "PREVI")
        If sugestao Is Nothing Then
            Set sugestao = BuscarElementoPorTexto(doc, "DIV", "PREVI")
        End If

        If Not sugestao Is Nothing Then
            sugestao.Click
            Call AguardarCarregamento
        End If
    End If

    ' Condição: Autor
    Call PreencherCampoPorLabel(doc, "Condição", condicao)
    Call PreencherCampoPorLabel(doc, "Condi", condicao)

    On Error GoTo 0
End Sub

'==============================================================================
' SUB - EXCLUIR DOCUMENTO "INICIAL" DA GRID
'==============================================================================
Private Sub ExcluirDocumentoInicial(doc As Object)
    On Error Resume Next

    ' Localizar grid de documentos e excluir a linha com "inicial"
    Dim tabelas As Object
    Set tabelas = doc.getElementsByTagName("TABLE")

    Dim t As Long, r As Long
    For t = 0 To tabelas.Length - 1
        Dim rows As Object
        Set rows = tabelas(t).getElementsByTagName("TR")
        For r = 0 To rows.Length - 1
            Dim rowText As String
            rowText = LCase(rows(r).innerText)
            If InStr(rowText, "inicial") > 0 And InStr(rowText, "documento") > 0 Then
                ' Encontrou linha com "inicial" - buscar botão excluir
                Dim btns As Object
                Set btns = rows(r).getElementsByTagName("A")
                Dim b As Long
                For b = 0 To btns.Length - 1
                    If InStr(1, btns(b).innerText, "Exclu", vbTextCompare) > 0 Or _
                       InStr(1, btns(b).getAttribute("title"), "Exclu", vbTextCompare) > 0 Or _
                       InStr(1, btns(b).getAttribute("class"), "delete", vbTextCompare) > 0 Then
                        btns(b).Click
                        Application.Wait Now + TimeValue("00:00:01")
                        Exit For
                    End If
                Next b

                ' Tentar ícone de delete
                Set btns = rows(r).getElementsByTagName("BUTTON")
                For b = 0 To btns.Length - 1
                    If InStr(1, btns(b).getAttribute("title"), "Exclu", vbTextCompare) > 0 Or _
                       InStr(1, btns(b).getAttribute("class"), "delete", vbTextCompare) > 0 Then
                        btns(b).Click
                        Application.Wait Now + TimeValue("00:00:01")
                        Exit For
                    End If
                Next b
                Exit For
            End If
        Next r
    Next t

    ' Limpar campo "Tipo Documento" e "Nome" se existirem como inputs
    Dim campoTipoDoc As Object
    Set campoTipoDoc = BuscarCampoPorLabel(doc, "Tipo Documento")
    If Not campoTipoDoc Is Nothing Then
        campoTipoDoc.Value = ""
        Call FireEvent(campoTipoDoc, "change")
    End If

    Dim campoNomeDoc As Object
    Set campoNomeDoc = BuscarCampoPorLabel(doc, "Nome")
    ' Cuidado: não limpar o nome do participante
    ' Só limpar se estiver na seção de documentos

    On Error GoTo 0
End Sub

'==============================================================================
' FUNÇÃO - CAPTURAR ID DA PASTA CRIADA
'==============================================================================
Private Function CapturarIdPasta() As String
    On Error Resume Next

    Dim doc As Object
    Set doc = IE.document

    ' Tentar capturar da URL (muitos sistemas colocam o ID na URL após salvar)
    Dim currentUrl As String
    currentUrl = IE.LocationURL

    ' Buscar padrão de ID na URL (ex: ?id=12345 ou /pasta/12345)
    If InStr(currentUrl, "id=") > 0 Then
        Dim posId As Long
        posId = InStr(currentUrl, "id=") + 3
        Dim endPos As Long
        endPos = InStr(posId, currentUrl, "&")
        If endPos = 0 Then endPos = Len(currentUrl) + 1
        CapturarIdPasta = Mid(currentUrl, posId, endPos - posId)
        Exit Function
    End If

    ' Tentar capturar do breadcrumb ou título da página
    Dim titulo As String
    titulo = doc.Title
    If InStr(titulo, "Pasta") > 0 Then
        ' Extrair número do título se presente
        Dim partes() As String
        partes = Split(titulo, " ")
        Dim p As Long
        For p = 0 To UBound(partes)
            If IsNumeric(partes(p)) Then
                CapturarIdPasta = partes(p)
                Exit Function
            End If
        Next p
    End If

    ' Tentar buscar campo "Código" ou "Nº Pasta" na página
    Dim campoCodigo As Object
    Set campoCodigo = BuscarCampoPorLabel(doc, "Código")
    If campoCodigo Is Nothing Then
        Set campoCodigo = BuscarCampoPorLabel(doc, "Pasta")
    End If
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
    Dim n As Integer
    n = Int(Rnd() * 3) + 1
    Select Case n
        Case 1: SortearAdvogadoInterno = ADV_INTERNO_1
        Case 2: SortearAdvogadoInterno = ADV_INTERNO_2
        Case 3: SortearAdvogadoInterno = ADV_INTERNO_3
    End Select
End Function

Private Function SortearAdvogadoExterno() As String
    Dim n As Integer
    n = Int(Rnd() * 5) + 1
    Select Case n
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
    ' Remover formatação existente
    cpf = Replace(cpf, ".", "")
    cpf = Replace(cpf, "-", "")
    cpf = Replace(cpf, " ", "")
    ' Preencher com zeros à esquerda se necessário
    Do While Len(cpf) < 11
        cpf = "0" & cpf
    Loop
    ' Formatar: 000.000.000-00
    FormatarCPF = Left(cpf, 3) & "." & Mid(cpf, 4, 3) & "." & Mid(cpf, 7, 3) & "-" & Right(cpf, 2)
End Function

'==============================================================================
' FUNÇÕES AUXILIARES - PESQUISA NO BENNER
'==============================================================================
Private Function PesquisarPartePasta(nome As String) As String
    On Error GoTo ErrHandler
    Dim doc As Object
    Set doc = IE.document

    ' Clicar em "Pastas" no menu superior
    Dim menuPastas As Object
    Set menuPastas = BuscarElementoPorTexto(doc, "A", "Pastas")
    If menuPastas Is Nothing Then Set menuPastas = BuscarElementoPorTexto(doc, "SPAN", "Pastas")
    If Not menuPastas Is Nothing Then
        menuPastas.Click
        Call AguardarCarregamento
    End If

    ' Localizar campo "Parte Pasta"
    Set doc = IE.document
    Dim campoParte As Object
    Set campoParte = BuscarCampoPorLabel(doc, "Parte Pasta")
    If campoParte Is Nothing Then
        Set campoParte = BuscarInputPorAtributo(doc, "placeholder", "Parte")
    End If
    If campoParte Is Nothing Then
        Set campoParte = BuscarInputPorAtributo(doc, "title", "Parte")
    End If

    If campoParte Is Nothing Then
        PesquisarPartePasta = "ERRO: Campo 'Parte Pasta' não encontrado"
        Exit Function
    End If

    ' Preencher e pesquisar
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
        Call FireKeyEvent(campoParte, 13)
    End If
    Call AguardarCarregamento
    Application.Wait Now + TimeValue("00:00:02")

    ' Ler resultados
    Set doc = IE.document
    PesquisarPartePasta = LerResultadosPesquisa(doc, nome)

    ' Limpar
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
    Dim encontrou As Boolean, objetos As String
    encontrou = False: objetos = ""

    For t = 0 To tabelas.Length - 1
        Dim rows As Object
        Set rows = tabelas(t).getElementsByTagName("TR")
        For r = 0 To rows.Length - 1
            Dim rowText As String
            rowText = UCase(rows(r).innerText)
            If InStr(rowText, UCase(nomePesquisado)) > 0 Then
                encontrou = True
                If InStr(rowText, "DÍVIDA PREVIDENCIÁRIA") > 0 Or _
                   InStr(rowText, "DIVIDA PREVIDENCIARIA") > 0 Then
                    objetos = objetos & "DÍVIDA PREVIDENCIÁRIA; "
                Else
                    Dim cells As Object
                    Set cells = rows(r).getElementsByTagName("TD")
                    If cells.Length > 1 Then
                        objetos = objetos & Left(cells(1).innerText, 50) & "; "
                    End If
                End If
            End If
        Next r
    Next t
    On Error GoTo 0

    If encontrou Then
        If InStr(UCase(objetos), "DÍVIDA PREVIDENCIÁRIA") > 0 Or _
           InStr(UCase(objetos), "DIVIDA PREVIDENCIARIA") > 0 Then
            LerResultadosPesquisa = "ENCONTRADA - MESMO OBJETO (DÍVIDA PREVIDENCIÁRIA)"
        ElseIf Len(objetos) > 0 Then
            LerResultadosPesquisa = "ENCONTRADA - OUTRO OBJETO: " & Left(objetos, 100)
        Else
            LerResultadosPesquisa = "ENCONTRADA - objeto não identificado"
        End If
    Else
        Dim bodyText As String
        bodyText = UCase(doc.body.innerText)
        If InStr(bodyText, "NENHUM REGISTRO") > 0 Or _
           InStr(bodyText, "NÃO ENCONTR") > 0 Or _
           InStr(bodyText, "SEM RESULTADO") > 0 Then
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

Private Function BuscarElementoPorClasse(doc As Object, classe As String) As Object
    On Error Resume Next
    Dim elementos As Object
    Set elementos = doc.getElementsByClassName(classe)
    If elementos.Length > 0 Then
        Set BuscarElementoPorClasse = elementos(0)
    Else
        Set BuscarElementoPorClasse = Nothing
    End If
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
        Dim attrVal As String
        attrVal = inputs(i).getAttribute(atributo)
        If InStr(1, attrVal, valor, vbTextCompare) > 0 Then
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
    Set BuscarBotaoPesquisa = BuscarElementoPorClasse(doc, "btn-search")
    If Not BuscarBotaoPesquisa Is Nothing Then Exit Function
    Set BuscarBotaoPesquisa = BuscarElementoPorClasse(doc, "fa-search")
    If Not BuscarBotaoPesquisa Is Nothing Then
        Set BuscarBotaoPesquisa = BuscarBotaoPesquisa.parentElement
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

Private Sub FireKeyEvent(elem As Object, keyCode As Integer)
    On Error Resume Next
    elem.Focus
    Application.SendKeys "{ENTER}", True
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
            Case "JÁ CADASTRADO", "JÁ CADASTRADO NO BENNER": jaCadastrados = jaCadastrados + 1
            Case "VERIFICAR": verificar = verificar + 1
            Case Else
                If InStr(st, "ERRO") > 0 Then erros = erros + 1
        End Select
    Next i

    MsgBox "=== RELATÓRIO ===" & vbCrLf & _
           "Total: " & (lastRow - 1) & vbCrLf & _
           "Pendentes: " & pendentes & vbCrLf & _
           "Cadastradas: " & cadastrados & vbCrLf & _
           "Duplicatas: " & duplicatas & vbCrLf & _
           "Já no Benner: " & jaCadastrados & vbCrLf & _
           "Verificar: " & verificar & vbCrLf & _
           "Erros: " & erros, vbInformation, "Status"
End Sub
