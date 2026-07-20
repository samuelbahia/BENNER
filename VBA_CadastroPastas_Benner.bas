Attribute VB_Name = "ModCadastroPastas"
'==============================================================================
' MÓDULO VBA - CADASTRO DE PASTAS NO BENNER (PREVI JURÍDICO)
'==============================================================================
' Automatiza:
' 1. Pesquisa prévia no Benner (Pastas > campo "Parte Pasta") para cada
'    participante da planilha, identificando pastas já existentes com o mesmo
'    objeto (DÍVIDA PREVIDENCIÁRIA) e prevenindo duplicidades.
' 2. Cadastro via +Novo > Cadastro rápido de pasta (Categoria: Cível).
' 3. Lançamento do andamento "PEDIDO DE AJUIZAMENTO DE AÇÃO".
'
' URL: https://previ.bennercloud.com.br/JURIDICO/jur/e/PREVI.aspx?i=K9_INICIOPREVI&m=MAIN
'
' REQUISITOS:
' - Microsoft Internet Controls (referência)
' - Microsoft HTML Object Library (referência)
' - Selenium Basic (opcional, para Chrome/Edge - ver flag USE_SELENIUM)
'
' FLUXO:
'   1. AnalisePreviaDuplicidades - análise local na planilha
'   2. VerificarNoBenner - pesquisa online em Pastas > Parte Pasta
'   3. CadastrarPastasBenner - cadastro das pendentes via Cadastro Rápido
'==============================================================================

Option Explicit

' === CONFIGURAÇÃO ===
' Altere para True se usar Selenium (Chrome/Edge) em vez de IE
Private Const USE_SELENIUM As Boolean = False

' Constantes do sistema
Private Const URL_BENNER As String = "https://previ.bennercloud.com.br/JURIDICO/jur/e/PREVI.aspx?i=K9_INICIOPREVI&m=MAIN"
Private Const URL_PASTAS As String = "https://previ.bennercloud.com.br/JURIDICO/jur/e/PREVI.aspx?i=K9_INICIOPREVI&m=PASTAS"
Private Const OBJETO As String = "DÍVIDA PREVIDENCIÁRIA"
Private Const CATEGORIA As String = "Cível"
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

' Colunas da planilha
Private Const COL_PLANO As Integer = 1        ' A - PLANO ATUAL
Private Const COL_NOME As Integer = 4         ' D - NOME
Private Const COL_CONTRATO As Integer = 6     ' F - CONTRATO
Private Const COL_VALOR_DIVIDA As Integer = 15 ' O - VAL DIV ATUAL
Private Const COL_BENNER As Integer = 28       ' AB - Benner (status existente)
Private Const COL_ANALISE As Integer = 29      ' AC - ANÁLISE DUPLICIDADE
Private Const COL_STATUS As Integer = 30       ' AD - STATUS CADASTRO
Private Const COL_CNJ As Integer = 31          ' AE - NÚMERO CNJ
Private Const COL_PLANO_DESC As Integer = 32   ' AF - PLANO DESCRIÇÃO
Private Const COL_PESQUISA_BENNER As Integer = 33 ' AG - RESULTADO PESQUISA BENNER

' Variáveis globais
Private IE As Object
Private driver As Object ' Selenium WebDriver (se USE_SELENIUM=True)

'==============================================================================
' ETAPA 1 - ANÁLISE LOCAL DE DUPLICIDADES NA PLANILHA
'==============================================================================
Public Sub AnalisePreviaDuplicidades()
    Dim wsData As Worksheet
    Set wsData = ThisWorkbook.Sheets("Planilha1")

    Dim lastRow As Long
    lastRow = wsData.Cells(wsData.Rows.Count, COL_NOME).End(xlUp).Row

    ' Limpar colunas de análise
    wsData.Range(wsData.Cells(2, COL_ANALISE), wsData.Cells(lastRow, COL_PESQUISA_BENNER)).ClearContents

    ' Headers
    wsData.Cells(1, COL_ANALISE).Value = "ANÁLISE DUPLICIDADE"
    wsData.Cells(1, COL_STATUS).Value = "STATUS CADASTRO"
    wsData.Cells(1, COL_CNJ).Value = "NÚMERO CNJ"
    wsData.Cells(1, COL_PLANO_DESC).Value = "PLANO DESCRIÇÃO"
    wsData.Cells(1, COL_PESQUISA_BENNER).Value = "PESQUISA BENNER"

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
            Case 1: wsData.Cells(i, COL_PLANO_DESC).Value = "Plano 1"
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
    wsData.Columns(COL_PESQUISA_BENNER).EntireColumn.AutoFit

    MsgBox "Etapa 1 concluída - Análise local." & vbCrLf & vbCrLf & _
           "Total: " & (lastRow - 1) & " operações." & vbCrLf & _
           "Próximo passo: Execute 'VerificarNoBenner' para pesquisar " & _
           "pastas existentes online.", vbInformation, "Análise Prévia"
End Sub

'==============================================================================
' ETAPA 2 - PESQUISA NO BENNER (Pastas > Parte Pasta)
'==============================================================================
Public Sub VerificarNoBenner()
    '
    ' Para cada participante com STATUS "PENDENTE" ou "VERIFICAR":
    ' 1. Clica em "Pastas" no menu superior do Benner
    ' 2. Cola o nome no campo "Parte Pasta"
    ' 3. Pesquisa e verifica se já existe pasta com mesmo objeto
    ' 4. Registra resultado na coluna AG (PESQUISA BENNER)
    '
    Dim wsData As Worksheet
    Set wsData = ThisWorkbook.Sheets("Planilha1")

    Dim lastRow As Long
    lastRow = wsData.Cells(wsData.Rows.Count, COL_NOME).End(xlUp).Row

    ' Verificar se etapa 1 foi executada
    If wsData.Cells(1, COL_STATUS).Value <> "STATUS CADASTRO" Then
        MsgBox "Execute primeiro a Etapa 1 (AnalisePreviaDuplicidades)!", vbExclamation
        Exit Sub
    End If

    Dim resp As VbMsgBoxResult
    resp = MsgBox("Esta etapa pesquisará cada participante no Benner (Pastas > Parte Pasta) " & _
                  "para verificar pastas já existentes." & vbCrLf & vbCrLf & _
                  "Certifique-se de estar LOGADO no sistema Benner." & vbCrLf & _
                  "O navegador será aberto automaticamente." & vbCrLf & vbCrLf & _
                  "Deseja continuar?", vbYesNo + vbQuestion, "Pesquisa no Benner")
    If resp = vbNo Then Exit Sub

    ' Inicializar navegador
    If Not InicializarNavegador() Then Exit Sub

    ' Navegar para a tela de Pastas
    IE.navigate URL_PASTAS
    Call AguardarCarregamento

    Dim pesquisados As Long, jaExistentes As Long
    pesquisados = 0: jaExistentes = 0

    Dim i As Long
    Dim nome As String
    Dim statusAtual As String

    For i = 2 To lastRow
        statusAtual = UCase(Trim(CStr(wsData.Cells(i, COL_STATUS).Value)))

        ' Pesquisar apenas PENDENTE e VERIFICAR
        If statusAtual = "PENDENTE" Or statusAtual = "VERIFICAR" Then
            nome = Trim(CStr(wsData.Cells(i, COL_NOME).Value))
            If Len(nome) = 0 Then GoTo ProximaLinha

            ' Pesquisar no Benner
            Dim resultadoPesquisa As String
            resultadoPesquisa = PesquisarPartePasta(nome)

            wsData.Cells(i, COL_PESQUISA_BENNER).Value = resultadoPesquisa
            pesquisados = pesquisados + 1

            ' Avaliar resultado
            If InStr(UCase(resultadoPesquisa), "ENCONTRADA") > 0 Then
                ' Pasta já existe - verificar se mesmo objeto
                If InStr(UCase(resultadoPesquisa), OBJETO) > 0 Then
                    wsData.Cells(i, COL_STATUS).Value = "JÁ CADASTRADO NO BENNER"
                    jaExistentes = jaExistentes + 1
                Else
                    ' Existe pasta mas com outro objeto - pode cadastrar
                    wsData.Cells(i, COL_ANALISE).Value = wsData.Cells(i, COL_ANALISE).Value & _
                        " | PASTA EXISTENTE OUTRO OBJETO"
                    ' Mantém PENDENTE
                End If
            ElseIf InStr(UCase(resultadoPesquisa), "NÃO ENCONTRADA") > 0 Then
                ' Nenhuma pasta encontrada - pode cadastrar
                If statusAtual = "VERIFICAR" Then
                    wsData.Cells(i, COL_STATUS).Value = "PENDENTE"
                End If
            End If

            ' Pausa para não sobrecarregar o sistema
            Application.Wait Now + TimeValue("00:00:02")

            ' Atualizar status bar
            Application.StatusBar = "Pesquisando... " & pesquisados & " de " & (lastRow - 1)
        End If
ProximaLinha:
    Next i

    Application.StatusBar = False

    MsgBox "Etapa 2 concluída - Pesquisa no Benner." & vbCrLf & vbCrLf & _
           "Pesquisados: " & pesquisados & vbCrLf & _
           "Já existentes (mesmo objeto): " & jaExistentes & vbCrLf & vbCrLf & _
           "Revise a coluna AG (PESQUISA BENNER) e a coluna AD (STATUS)." & vbCrLf & _
           "Próximo passo: Execute 'CadastrarPastasBenner' para registrar as pendentes.", _
           vbInformation, "Pesquisa Concluída"
End Sub

'==============================================================================
' FUNÇÃO - PESQUISAR PARTE PASTA NO BENNER
'==============================================================================
Private Function PesquisarPartePasta(nome As String) As String
    On Error GoTo ErrHandler

    Dim doc As Object
    Set doc = IE.document

    ' --- PASSO 1: Clicar no menu/link "Pastas" no campo superior ---
    ' O link "Pastas" no menu superior abre a lista de pastas com filtros
    Dim menuPastas As Object
    Set menuPastas = BuscarElementoPorTexto(doc, "A", "Pastas")
    If menuPastas Is Nothing Then
        ' Tentar por link direto na barra de navegação
        Set menuPastas = BuscarElementoPorTexto(doc, "SPAN", "Pastas")
    End If
    If Not menuPastas Is Nothing Then
        menuPastas.Click
        Call AguardarCarregamento
    End If

    ' --- PASSO 2: Localizar o campo "Parte Pasta" e preencher com o nome ---
    ' O campo de pesquisa "Parte Pasta" filtra por nome do participante
    Dim campoParte As Object
    Set campoParte = BuscarCampoPorLabel(doc, "Parte Pasta")

    If campoParte Is Nothing Then
        ' Fallback: buscar input por placeholder ou título
        Set campoParte = BuscarInputPorAtributo(doc, "placeholder", "Parte")
        If campoParte Is Nothing Then
            Set campoParte = BuscarInputPorAtributo(doc, "title", "Parte")
        End If
    End If

    If campoParte Is Nothing Then
        PesquisarPartePasta = "ERRO: Campo 'Parte Pasta' não encontrado"
        Exit Function
    End If

    ' Limpar campo e preencher
    campoParte.Value = ""
    campoParte.Focus
    campoParte.Value = nome
    Call FireEvent(campoParte, "change")
    Call FireEvent(campoParte, "input")

    ' --- PASSO 3: Clicar no botão de pesquisa ---
    Dim btnPesquisar As Object
    Set btnPesquisar = BuscarBotaoPesquisa(doc)
    If Not btnPesquisar Is Nothing Then
        btnPesquisar.Click
    Else
        ' Tentar submit com Enter
        Call FireKeyEvent(campoParte, 13) ' Enter
    End If
    Call AguardarCarregamento

    ' --- PASSO 4: Ler resultados ---
    Application.Wait Now + TimeValue("00:00:02")
    Set doc = IE.document

    ' Verificar se há resultados na tabela/grid
    Dim resultados As String
    resultados = LerResultadosPesquisa(doc, nome)

    ' --- PASSO 5: Limpar pesquisa para próxima iteração ---
    If Not campoParte Is Nothing Then
        On Error Resume Next
        Set campoParte = BuscarCampoPorLabel(doc, "Parte Pasta")
        If Not campoParte Is Nothing Then
            campoParte.Value = ""
            Call FireEvent(campoParte, "change")
        End If
        On Error GoTo 0
    End If

    PesquisarPartePasta = resultados
    Exit Function

ErrHandler:
    PesquisarPartePasta = "ERRO: " & Err.Description
End Function

'==============================================================================
' FUNÇÃO - LER RESULTADOS DA PESQUISA
'==============================================================================
Private Function LerResultadosPesquisa(doc As Object, nomePesquisado As String) As String
    On Error Resume Next

    ' Buscar na tabela de resultados
    Dim tabelas As Object
    Set tabelas = doc.getElementsByTagName("TABLE")

    Dim t As Long, r As Long, c As Long
    Dim encontrou As Boolean
    Dim objetos As String
    encontrou = False
    objetos = ""

    ' Percorrer tabelas buscando resultados
    For t = 0 To tabelas.Length - 1
        Dim tbl As Object
        Set tbl = tabelas(t)
        Dim rows As Object
        Set rows = tbl.getElementsByTagName("TR")

        For r = 0 To rows.Length - 1
            Dim rowText As String
            rowText = UCase(rows(r).innerText)

            ' Verificar se a linha contém o nome pesquisado
            If InStr(rowText, UCase(nomePesquisado)) > 0 Then
                encontrou = True
                ' Verificar se contém o objeto "DÍVIDA PREVIDENCIÁRIA"
                If InStr(rowText, UCase(OBJETO)) > 0 Then
                    objetos = objetos & "DÍVIDA PREVIDENCIÁRIA; "
                Else
                    ' Capturar o objeto da pasta encontrada
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

    ' Montar resultado
    If encontrou Then
        If InStr(UCase(objetos), UCase(OBJETO)) > 0 Then
            LerResultadosPesquisa = "ENCONTRADA - MESMO OBJETO (" & OBJETO & ")"
        ElseIf Len(objetos) > 0 Then
            LerResultadosPesquisa = "ENCONTRADA - OUTRO OBJETO: " & Left(objetos, 100)
        Else
            LerResultadosPesquisa = "ENCONTRADA - objeto não identificado"
        End If
    Else
        ' Verificar mensagem de "nenhum registro"
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
' ETAPA 3 - CADASTRO VIA +NOVO > CADASTRO RÁPIDO DE PASTA
'==============================================================================
Public Sub CadastrarPastasBenner()
    '
    ' Cadastra pastas para linhas com STATUS = "PENDENTE"
    ' Fluxo: +Novo (botão lateral esquerdo) > Cadastro rápido de pasta
    '        Categoria: Cível
    '
    Dim wsData As Worksheet
    Set wsData = ThisWorkbook.Sheets("Planilha1")

    Dim lastRow As Long
    lastRow = wsData.Cells(wsData.Rows.Count, COL_NOME).End(xlUp).Row

    ' Verificar se análise foi feita
    If wsData.Cells(1, COL_STATUS).Value <> "STATUS CADASTRO" Then
        MsgBox "Execute primeiro as Etapas 1 e 2!", vbExclamation
        Exit Sub
    End If

    ' Contar pendentes
    Dim totalPendentes As Long
    Dim i As Long
    For i = 2 To lastRow
        If UCase(Trim(CStr(wsData.Cells(i, COL_STATUS).Value))) = "PENDENTE" Then
            totalPendentes = totalPendentes + 1
        End If
    Next i

    If totalPendentes = 0 Then
        MsgBox "Nenhuma operação com status PENDENTE para cadastrar.", vbInformation
        Exit Sub
    End If

    Dim resp As VbMsgBoxResult
    resp = MsgBox("Serão cadastradas " & totalPendentes & " pastas no Benner." & vbCrLf & _
                  "Fluxo: +Novo > Cadastro rápido de pasta > Categoria Cível" & vbCrLf & vbCrLf & _
                  "Certifique-se de estar LOGADO no sistema." & vbCrLf & _
                  "Deseja continuar?", vbYesNo + vbQuestion, "Cadastro de Pastas")
    If resp = vbNo Then Exit Sub

    ' Inicializar navegador
    If Not InicializarNavegador() Then Exit Sub

    IE.navigate URL_BENNER
    Call AguardarCarregamento

    Dim cadastrados As Long, erros As Long
    cadastrados = 0: erros = 0

    For i = 2 To lastRow
        If UCase(Trim(CStr(wsData.Cells(i, COL_STATUS).Value))) = "PENDENTE" Then
            Dim nome As String
            Dim contrato As String
            Dim valorDivida As Double
            Dim plano As String
            Dim numeroCNJ As String

            nome = Trim(CStr(wsData.Cells(i, COL_NOME).Value))
            contrato = CStr(wsData.Cells(i, COL_CONTRATO).Value)
            valorDivida = CDbl(wsData.Cells(i, COL_VALOR_DIVIDA).Value)
            plano = CStr(wsData.Cells(i, COL_PLANO_DESC).Value)
            numeroCNJ = "DP" & contrato

            ' Cadastrar via Cadastro Rápido
            Dim resultado As String
            resultado = CadastrarViaCadastroRapido(nome, contrato, valorDivida, plano, numeroCNJ)

            If resultado = "OK" Then
                wsData.Cells(i, COL_STATUS).Value = "CADASTRADO"
                cadastrados = cadastrados + 1

                ' Lançar andamento
                Call LancarAndamento(numeroCNJ)
                wsData.Cells(i, COL_STATUS).Value = "CADASTRADO + ANDAMENTO"
            Else
                wsData.Cells(i, COL_STATUS).Value = "ERRO: " & resultado
                erros = erros + 1
            End If

            Application.StatusBar = "Cadastrando... " & cadastrados & "/" & totalPendentes
            Application.Wait Now + TimeValue("00:00:03")
        End If
    Next i

    Application.StatusBar = False

    MsgBox "Cadastro concluído!" & vbCrLf & vbCrLf & _
           "Cadastrados com sucesso: " & cadastrados & vbCrLf & _
           "Erros: " & erros, vbInformation, "Resultado"
End Sub

'==============================================================================
' FUNÇÃO - CADASTRAR VIA CADASTRO RÁPIDO DE PASTA
'==============================================================================
Private Function CadastrarViaCadastroRapido(nome As String, contrato As String, _
                                             valorDivida As Double, plano As String, _
                                             numeroCNJ As String) As String
    On Error GoTo ErrHandler
    Dim doc As Object

    ' --- PASSO 1: Clicar em "+Novo" (botão lateral esquerdo) ---
    Set doc = IE.document
    Dim btnNovo As Object
    Set btnNovo = BuscarElementoPorTexto(doc, "A", "+Novo")
    If btnNovo Is Nothing Then
        Set btnNovo = BuscarElementoPorTexto(doc, "SPAN", "Novo")
    End If
    If btnNovo Is Nothing Then
        Set btnNovo = BuscarElementoPorTexto(doc, "BUTTON", "Novo")
    End If
    If btnNovo Is Nothing Then
        ' Tentar por classe ou ícone
        Set btnNovo = BuscarElementoPorClasse(doc, "btn-novo")
    End If

    If Not btnNovo Is Nothing Then
        btnNovo.Click
        Call AguardarCarregamento
    Else
        CadastrarViaCadastroRapido = "Botão +Novo não encontrado"
        Exit Function
    End If

    ' --- PASSO 2: Selecionar "Cadastro rápido de pasta" ---
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
        CadastrarViaCadastroRapido = "Opção 'Cadastro rápido de pasta' não encontrada"
        Exit Function
    End If

    ' --- PASSO 3: Preencher formulário (Pastas > Novo Registro) ---
    Set doc = IE.document

    ' Categoria: Cível
    Call PreencherCampoPorLabel(doc, "Categoria", CATEGORIA)

    ' Objeto: DÍVIDA PREVIDENCIÁRIA
    Call PreencherCampoPorLabel(doc, "Objeto", OBJETO)

    ' Chance Êxito: Possível
    Call PreencherCampoPorLabel(doc, "Chance", CHANCE_EXITO)

    ' Valor da P. Condenação
    Call PreencherCampoPorLabel(doc, "Valor", Format(valorDivida, "#,##0.00"))

    ' Plano
    Call PreencherCampoPorLabel(doc, "Plano", plano)

    ' Programa: Previdencial
    Call PreencherCampoPorLabel(doc, "Programa", PROGRAMA)

    ' Gerência: GESOP
    Call PreencherCampoPorLabel(doc, "Gerência", GERENCIA)
    Call PreencherCampoPorLabel(doc, "Ger" & Chr(234) & "ncia", GERENCIA)

    ' Processo - não distribuído (checkbox ou campo)
    Call PreencherCampoPorLabel(doc, "Processo", "Não distribuído")

    ' Número CNJ: DP + contrato
    Call PreencherCampoPorLabel(doc, "CNJ", numeroCNJ)
    Call PreencherCampoPorLabel(doc, "Número", numeroCNJ)

    ' Situação: Baixa Provisória
    Call PreencherCampoPorLabel(doc, "Situação", SITUACAO)
    Call PreencherCampoPorLabel(doc, "Situa", SITUACAO)

    ' Condução: Recuperação de Créditos
    Call PreencherCampoPorLabel(doc, "Condução", CONDUCAO)
    Call PreencherCampoPorLabel(doc, "Condu", CONDUCAO)

    ' --- PASSO 4: Salvar ---
    Dim btnSalvar As Object
    Set btnSalvar = BuscarElementoPorTexto(doc, "A", "Salvar")
    If btnSalvar Is Nothing Then
        Set btnSalvar = BuscarElementoPorTexto(doc, "BUTTON", "Salvar")
    End If
    If btnSalvar Is Nothing Then
        Set btnSalvar = BuscarElementoPorTexto(doc, "SPAN", "Salvar")
    End If

    If Not btnSalvar Is Nothing Then
        btnSalvar.Click
        Call AguardarCarregamento
    Else
        CadastrarViaCadastroRapido = "Botão Salvar não encontrado"
        Exit Function
    End If

    CadastrarViaCadastroRapido = "OK"
    Exit Function

ErrHandler:
    CadastrarViaCadastroRapido = Err.Description
End Function

'==============================================================================
' SUB - LANÇAR ANDAMENTO
'==============================================================================
Private Sub LancarAndamento(numeroCNJ As String)
    On Error Resume Next
    Dim doc As Object
    Set doc = IE.document

    ' Navegar para aba de andamentos da pasta recém-criada
    Dim tabAndamento As Object
    Set tabAndamento = BuscarElementoPorTexto(doc, "A", "Andamento")
    If tabAndamento Is Nothing Then
        Set tabAndamento = BuscarElementoPorTexto(doc, "SPAN", "Andamento")
    End If
    If Not tabAndamento Is Nothing Then
        tabAndamento.Click
        Call AguardarCarregamento
    End If

    ' Novo andamento
    Set doc = IE.document
    Dim btnNovoAnd As Object
    Set btnNovoAnd = BuscarElementoPorTexto(doc, "A", "Novo")
    If Not btnNovoAnd Is Nothing Then
        btnNovoAnd.Click
        Call AguardarCarregamento
    End If

    ' Preencher tipo de andamento
    Set doc = IE.document
    Call PreencherCampoPorLabel(doc, "Tipo", ANDAMENTO)
    Call PreencherCampoPorLabel(doc, "Andamento", ANDAMENTO)

    ' Salvar
    Dim btnSalvar As Object
    Set btnSalvar = BuscarElementoPorTexto(doc, "A", "Salvar")
    If btnSalvar Is Nothing Then
        Set btnSalvar = BuscarElementoPorTexto(doc, "BUTTON", "Salvar")
    End If
    If Not btnSalvar Is Nothing Then
        btnSalvar.Click
        Call AguardarCarregamento
    End If

    ' As providências são geradas automaticamente pelo sistema Benner:
    ' PROV 1: "PREVI AUTORA – DOCUMENTAÇÃO INICIAL" -> GESOP, 10 dias úteis
    ' PROV 2: "PROVIDENCIAR AJUIZAMENTO" -> Escritório Contratado, 15 dias úteis
    On Error GoTo 0
End Sub

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
        MsgBox "Erro ao criar instância do navegador." & vbCrLf & _
               "Verifique se o Internet Explorer está disponível.", vbCritical
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
    ' Pausa adicional para renderização JavaScript
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
    ' Busca um campo de input associado a um label que contém o texto
    On Error Resume Next
    Dim labels As Object
    Set labels = doc.getElementsByTagName("LABEL")

    Dim i As Long
    For i = 0 To labels.Length - 1
        If InStr(1, labels(i).innerText, labelText, vbTextCompare) > 0 Then
            ' Tentar pelo atributo "for"
            Dim forId As String
            forId = labels(i).getAttribute("for")
            If Len(forId) > 0 Then
                Set BuscarCampoPorLabel = doc.getElementById(forId)
                If Not BuscarCampoPorLabel Is Nothing Then Exit Function
            End If

            ' Tentar input dentro ou após o label
            Dim inputs As Object
            Set inputs = labels(i).parentElement.getElementsByTagName("INPUT")
            If inputs.Length > 0 Then
                Set BuscarCampoPorLabel = inputs(0)
                Exit Function
            End If

            ' Tentar select
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
    ' Tentar botão com texto "Pesquisar"
    Set BuscarBotaoPesquisa = BuscarElementoPorTexto(doc, "BUTTON", "Pesquisar")
    If Not BuscarBotaoPesquisa Is Nothing Then Exit Function

    Set BuscarBotaoPesquisa = BuscarElementoPorTexto(doc, "A", "Pesquisar")
    If Not BuscarBotaoPesquisa Is Nothing Then Exit Function

    ' Tentar ícone de lupa (classe comum)
    Set BuscarBotaoPesquisa = BuscarElementoPorClasse(doc, "btn-search")
    If Not BuscarBotaoPesquisa Is Nothing Then Exit Function

    Set BuscarBotaoPesquisa = BuscarElementoPorClasse(doc, "fa-search")
    If Not BuscarBotaoPesquisa Is Nothing Then
        Set BuscarBotaoPesquisa = BuscarBotaoPesquisa.parentElement
        Exit Function
    End If

    ' Tentar input type=submit
    Dim inputs As Object
    Set inputs = doc.getElementsByTagName("INPUT")
    Dim i As Long
    For i = 0 To inputs.Length - 1
        If LCase(inputs(i).getAttribute("type")) = "submit" Then
            If InStr(1, inputs(i).Value, "Pesquis", vbTextCompare) > 0 Or _
               InStr(1, inputs(i).Value, "Buscar", vbTextCompare) > 0 Then
                Set BuscarBotaoPesquisa = inputs(i)
                Exit Function
            End If
        End If
    Next i

    Set BuscarBotaoPesquisa = Nothing
    On Error GoTo 0
End Function

Private Sub PreencherCampoPorLabel(doc As Object, labelText As String, valor As String)
    Dim campo As Object
    Set campo = BuscarCampoPorLabel(doc, labelText)

    If Not campo Is Nothing Then
        Dim tagName As String
        tagName = UCase(campo.tagName)

        If tagName = "SELECT" Then
            ' Selecionar opção pelo texto
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
            ' Input text
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
    Dim evt As Object
    Set evt = IE.document.createEvent("KeyboardEvent")
    evt.initEvent "keydown", True, True
    elem.dispatchEvent evt
    ' Simular Enter via SendKeys como fallback
    elem.Focus
    Application.SendKeys "{ENTER}", True
    On Error GoTo 0
End Sub

'==============================================================================
' UTILITÁRIO - FECHAR NAVEGADOR
'==============================================================================
Public Sub FecharNavegador()
    On Error Resume Next
    If Not IE Is Nothing Then
        IE.Quit
        Set IE = Nothing
    End If
    On Error GoTo 0
End Sub

'==============================================================================
' UTILITÁRIO - RELATÓRIO DE STATUS
'==============================================================================
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

    MsgBox "=== RELATÓRIO DE STATUS ===" & vbCrLf & vbCrLf & _
           "Total de operações: " & (lastRow - 1) & vbCrLf & _
           "Pendentes (prontas p/ cadastro): " & pendentes & vbCrLf & _
           "Cadastradas com sucesso: " & cadastrados & vbCrLf & _
           "Duplicatas (não cadastrar): " & duplicatas & vbCrLf & _
           "Já cadastradas no Benner: " & jaCadastrados & vbCrLf & _
           "A verificar manualmente: " & verificar & vbCrLf & _
           "Erros: " & erros, vbInformation, "Relatório de Status"
End Sub
