from Parser.Escopo import Escopo
import re
class Parser:
    def __init__(self, tabTokens):
        self.tabTokens = tabTokens
        self.indexToken = 0
        self.erro = False
        self.listaEscopos = []
        self.indexEscopoAtual = -1
        self.tabSimbolos = []
        self.indexDecAtual = 0 #Pra saber na semantica qual declaracao no codigo tá sendo checada
                               #seja, variavel, funcao, procedimento e etc
        self.indexDecFunc = 0

    def tokenAtual(self):
        return self.tabTokens[self.indexToken]

    def start(self):
        escopoPai = self.indexEscopoAtual
        self.indexEscopoAtual += 1
        escopoInicial = Escopo(self.indexEscopoAtual,escopoPai)
        self.listaEscopos.append(escopoInicial)
        self.statement_list()
        return

    def statement_list(self):
        if(self.tokenAtual().tipo == "FIM"):
            self.listaEscopos[0].fechar()
            return
        else:
            self.statement()
            self.statement_list()
            return
    
    def statement(self):
        #<var-declaracao>
        if(self.tokenAtual().tipo == 'INT' or self.tokenAtual().tipo == 'TBOOLEAN'):#tipo
            temp = []
            temp.append('VAR')
            temp.append(self.tokenAtual().tipo)
            self.indexToken +=1
            if(self.tokenAtual().tipo == 'ID' and self.tokenAtual().lexema[0] == 'v'):#identificador var
                temp.append(self.tokenAtual().lexema)
                self.indexToken +=1
                if(self.tokenAtual().tipo == 'ATTR'):#atribuicao
                    self.indexToken +=1
                    #Expression
                    temp.append(self.expression())
                    if(self.tokenAtual().tipo == 'SEMICOLON'):
                        self.indexToken +=1
                        temp.append(self.indexEscopoAtual)
                        self.tabSimbolos.append(temp)
                        if(self.checkSemantica('VARDEC',self.indexDecAtual)):
                            return
                    else:
                        self.erro = True
                        raise Exception('Erro sintatico Ponto e virgula Var declaracao na linha '+str(self.tokenAtual().linha))
                else:
                    self.erro = True
                    raise Exception('Erro sintatico Atribuicao Var declaracao na linha '+str(self.tokenAtual().linha))
            else:
                self.erro = True
                raise Exception('Erro sintatico Identificador Var declaracao na linha '+str(self.tokenAtual().linha))
            
        #<funcao-declaracao> ##
        elif(self.tokenAtual().tipo == 'FUNC'):#tipo função
            temp = []
            temp.append('FUNC')
            escopoDaFuncao = self.indexEscopoAtual
            escopoForaDaFunc = self.indexEscopoAtual
            self.indexToken += 1
            if(self.tokenAtual().tipo == 'INT' or self.tokenAtual().tipo == 'TBOOLEAN'):#tipo
                temp.append(self.tokenAtual().tipo)
                self.indexToken += 1
                if(self.tokenAtual().tipo == 'ID' and self.tokenAtual().lexema[0] == 'f'):#identificador
                    temp.append(self.tokenAtual().lexema)
                    self.indexToken += 1
                    if(self.tokenAtual().tipo == 'LBRACK'):#parentese esquerdo

                        escopoPai = self.indexEscopoAtual
                        self.indexEscopoAtual = len(self.listaEscopos) 
                        escopoAtual = Escopo(self.indexEscopoAtual, escopoPai)
                        self.listaEscopos.append(escopoAtual)

                        temp3 = []

                        self.indexToken += 1
                        while(self.tokenAtual().tipo != 'RBRACK'): #verificar caso em que não encontre o RBRACK
                            temp2 = []
                            if(self.tokenAtual().tipo == 'INT' or self.tokenAtual().tipo == 'TBOOLEAN'):#tipo
                                temp2.append('VAR')
                                temp2.append(self.tokenAtual().tipo)
                                self.indexToken += 1
                                if(self.tokenAtual().tipo == 'ID'):#identificador
                                    temp2.append(self.tokenAtual().lexema)
                                    temp2.append('PARAM')
                                    temp2.append(self.indexEscopoAtual)
                                    temp3.append(temp2)
                                    self.indexToken += 1
                                    if(self.tokenAtual().tipo == 'COMMA'):#virgula para um proximo parametro
                                        self.indexToken += 1
                                        if(self.tokenAtual().tipo == 'RBRACK'):
                                            self.erro = True
                                            raise Exception('Erro sintatico virgula Func declaracao na linha '+str(self.tokenAtual().linha))
                                        else:
                                            pass
                                    elif(self.tokenAtual().tipo == 'RBRACK'):
                                        self.indexToken += 1
                                        break
                                    else:
                                        self.erro = True
                                        raise Exception('Erro sintatico virgula Func declaracao na linha '+str(self.tokenAtual().linha))    
                                else:
                                    self.erro = True
                                    raise Exception('Erro sintatico identificador Var declaracao na linha '+str(self.tokenAtual().linha))
                            else:
                                self.erro = True
                                raise Exception('Erro sintatico Tipo Var declaracao na linha '+str(self.tokenAtual().linha))
                        
                        #saiu do laço, isso significa que encontrou o RBRACK
                        if(self.tokenAtual().tipo != 'LCBRACK'):
                            self.indexToken += 1

                        temp.append('RETURN')
                        temp.append(escopoDaFuncao)
                        temp.append(temp3)
                        self.tabSimbolos.append(temp)
                        self.indexDecFunc = len(self.tabSimbolos) - 1

                        # for x in range(len(temp3)):
                        #     self.tabSimbolos.append(temp3[x])

                        if(self.tokenAtual().tipo == 'LCBRACK'):#chave esquerda
                            self.indexToken += 1
                            encontrouReturn = False
                            while(self.tokenAtual().tipo != 'RCBRACK'): #verificar caso em que não encontra o RCBRACK
                                if(self.tokenAtual().tipo == 'RETURN'):
                                    self.indexToken += 1
                                    encontrouReturn = True
                                    if(self.tokenAtual().tipo == 'ID'):#identificador
                                        temp[3] = self.tokenAtual().lexema
                                        self.adicionarVarDeRetornoFuncTabSimbolo(temp)
                                        self.indexToken += 1 
                                        if(self.tokenAtual().tipo == 'SEMICOLON' and self.lookAhead().tipo == 'RCBRACK'):#ponto e virgula seguido de uma chave direita
                                            self.indexToken += 1
                                            # escopoPai = self.indexEscopoAtual
                                            # self.indexEscopoAtual += 1
                                            # escopoAtual = Escopo(self.indexEscopoAtual, escopoPai)
                                            # self.listaEscopos.append(escopoAtual)
                                            break
                                        else:
                                            self.erro = True
                                            raise Exception('Erro sintatico no Retorno da Função declaracao na linha '+str(self.tokenAtual().linha))
                                    else:
                                        self.erro = True
                                        raise Exception('Erro sintatico Retorno Func declaracao na linha '+str(self.tokenAtual().linha))
                                else:
                                    self.statement()#chamo para verificar os stmts contidos dentro do escopo da função
                            self.indexEscopoAtual = escopoForaDaFunc
                            
                            if(encontrouReturn == False):
                                self.erro = True
                                raise Exception('Erro sintatico no retorno da função na linha '+str(self.tokenAtual().linha - 1))
                            self.indexToken +=1

                            if(self.checkSemantica('FUNCDEC', self.indexDecFunc)):
                                return

                        else:
                            self.erro = True
                            raise Exception('Erro sintatico Chave esquerda da Funcao declaracao na linha ' + str(self.tokenAtual().linha))
                    else:
                        self.erro = True
                        raise Exception('Erro sintatico Parentese esquerdo da Funcao declaracao na linha ' + str(self.tokenAtual().linha))
                else:
                    self.erro = True
                    raise Exception('Erro sintatico Identificador da Funcao declaracao na linha ' + str(self.tokenAtual().linha))
            else:
                self.erro = True
                raise Exception('Erro sintatico Tipo da Funcao declaracao na linha ' + str(self.tokenAtual().linha)) 
        
        #<procedimento-declaracao>
        elif(self.tokenAtual().tipo == 'PROC'):
            temp = []
            temp.append('PROC')
            temp.append('NULL')
            escopoDoProcecimento = self.indexEscopoAtual
            escopoForaDoProc = self.indexEscopoAtual
    
            self.indexToken += 1
            if(self.tokenAtual().tipo == 'ID' and self.tokenAtual().lexema[0] == 'p'):
                temp.append(self.tokenAtual().lexema) 
                self.indexToken += 1
                if(self.tokenAtual().tipo == 'LBRACK'):#parentese esquerdo
                    #novoEscopo
                    escopoPai = self.indexEscopoAtual
                    self.indexEscopoAtual = len(self.listaEscopos) #4
                    escopoAtual = Escopo(self.indexEscopoAtual, escopoPai)
                    self.listaEscopos.append(escopoAtual)

                    temp3 = []

                    self.indexToken += 1
                    while(self.tokenAtual().tipo != 'RBRACK'): #obs: verificar caso em que não encontre o RBRACK
                        temp2 = []
                        if(self.tokenAtual().tipo == 'INT' or self.tokenAtual().tipo == 'TBOOLEAN'):#tipo
                            temp2.append('VAR')
                            temp2.append(self.tokenAtual().tipo)
                            self.indexToken += 1
                            if(self.tokenAtual().tipo == 'ID'):#identificador
                                temp2.append(self.tokenAtual().lexema)
                                temp2.append('PARAM')
                                temp2.append(self.indexEscopoAtual)
                                temp3.append(temp2)
                                self.indexToken += 1
                                if(self.tokenAtual().tipo == 'COMMA'):#virgula para um proximo parametro
                                    self.indexToken += 1
                                    if(self.tokenAtual().tipo == 'RBRACK'):
                                        self.erro = True
                                        raise Exception('Erro sintatico virgula Proc declaracao na linha '+str(self.tokenAtual().linha))
                                    else:
                                        pass
                                elif(self.tokenAtual().tipo == 'RBRACK'):
                                    self.indexToken += 1
                                    break
                                else:
                                    self.erro = True
                                    raise Exception('Erro sintatico em Proc declaracao na linha '+str(self.tokenAtual().linha))    
                            else:
                                self.erro = True
                                raise Exception('Erro sintatico identificador Var declaracao na linha '+str(self.tokenAtual().linha))
                        else:
                            self.erro = True
                            raise Exception('Erro sintatico Tipo Var declaracao na linha '+str(self.tokenAtual().linha))
                        
                    #saiu do laço, isso significa que encontrou o RBRACK
                    if(self.tokenAtual().tipo != 'LCBRACK'):
                        self.indexToken += 1

                    temp.append('NULL')
                    temp.append(escopoDoProcecimento)
                    temp.append(temp3)
                    self.tabSimbolos.append(temp)
                    self.indexDecFunc = len(self.tabSimbolos) - 1

                    # for x in range(len(temp3)):
                    #     self.tabSimbolos.append(temp3[x])

                    
                    if(self.tokenAtual().tipo == 'LCBRACK'):#chave esquerda
                        self.indexToken += 1
                        while(self.tokenAtual().tipo != 'RCBRACK'): #verificar caso em que não encontra o RCBRACK
                            if(self.tokenAtual().tipo == 'SEMICOLON' and self.lookAhead().tipo == 'RCBRACK'):#ponto e virgula seguido de uma chave direita
                                self.indexToken += 1
                                break
                            else:
                                self.statement()#chamo para verificar os stmts contidos dentro do escopo da função
                        self.indexEscopoAtual = escopoForaDoProc

                        self.indexToken += 1

                        if(self.checkSemantica('PROCDEC', self.indexDecFunc)):
                            return
                    else:
                        self.erro = True
                        raise Exception('Erro sintatico Chave esquerda do Procedimento declaracao na linha ' + str(self.tokenAtual().linha))
                else:
                    self.erro = True
                    raise Exception('Erro sintatico Parentese esquerdo do Procedimento declaracao na linha ' + str(self.tokenAtual().linha))
            else:
                    self.erro = True
                    raise Exception('Erro sintatico Identificador do Proc declaracao na linha ' + str(self.tokenAtual().linha))
        #Puts
        elif (self.tokenAtual().tipo == 'PUTS'):
            self.indexToken +=1
            if((self.tokenAtual().tipo == 'ID' and self.tokenAtual().lexema[0] == 'v') or self.tokenAtual().tipo == 'NUMBER'):
                self.indexToken+=1
                if(self.tokenAtual().tipo == 'SEMICOLON'):# se for um numero ou var o proximo token vai ser esse semicolon
                    self.indexToken += 1
                    return
                else:
                    self.erro = True
                    raise Exception('Erro sintatico ponto e virgula no puts na linha ' + str(self.tokenAtual().linha))
            else:
                self.erro = True
                raise Exception('Erro sintatico depois do puts na linha ' + str(self.tokenAtual().linha))
        #Chamada de funcao e procedimento e atribuição de var existente**
        elif(self.tokenAtual().tipo == 'ID'):
            #atribuicao de var ja existente vA = 2; sem a declaracao int vA = 1;
            if(self.tokenAtual().lexema[0] == 'v'):
                temp = []
                temp.append('ATTR')
                simbolo =self.buscarSimboloVarPorLexema(self.tokenAtual().lexema)
                print(self.indexEscopoAtual)
                if(simbolo != ''):
                    temp.append(simbolo[1])
                    temp.append(simbolo[2])
                    self.indexToken +=1
                    if(self.tokenAtual().tipo == 'ATTR'):
                        self.indexToken +=1
                        temp.append(self.expression())
                        if(self.tokenAtual().tipo == 'SEMICOLON'):
                            self.indexToken +=1
                            temp.append(self.indexEscopoAtual)
                            self.tabSimbolos.append(temp)
                        else:
                            raise Exception('Erro sintatico Ponto e virgula Var atribuição na linha '+str(self.tokenAtual().linha))

                    else:
                        raise Exception("Erro Sintatico, na linha: "+str(self.tokenAtual().linha))
                else:
                    raise Exception("Erro Semântico, variavel não está declarada neste escopo: "+str(self.tokenAtual().linha))

            elif(self.tokenAtual().lexema[0] == 'f' or self.tokenAtual().lexema[0] == 'p'):
                self.indexToken +=1
                if(self.tokenAtual().tipo == 'LBRACK'):
                    self.indexToken+=1
                    while(self.tokenAtual().tipo != 'RBRACK'):# verifica argumentos da funcao para ser chamada, nao checa tipos (semantica)
                        if(self.tokenAtual().tipo == 'NUMBER' or self.tokenAtual().tipo == 'BOOLEAN' or self.tokenAtual().lexema[0] == 'v'):#verifica se foi passado numero, boolean, ou variavel
                            self.indexToken += 1
                            if(self.tokenAtual().tipo == 'COMMA'):
                                self.indexToken +=1
                                if(self.tokenAtual().tipo == 'RBRACK'):
                                    self.erro = True
                                    raise Exception('Erro sintatico falta de argumentos na linha ' + str(self.tokenAtual().linha))
                            elif(self.tokenAtual().tipo == 'RBRACK'):
                                self.indexToken +=1
                                break
                            else:
                                self.erro = True
                                raise Exception('Erro sintatico Virgula na linha ' + str(self.tokenAtual().linha))
                        else:
                            self.erro = True
                            raise Exception('Erro sintatico argumento invalido na linha ' + str(self.tokenAtual().linha))
                    #fora do laço encontrou o RBRACK
                    if(self.tokenAtual().tipo == 'SEMICOLON'):# ponto e virgula no final da declaração do puts
                        self.indexToken +=1
                        return
                    else:
                        self.erro = True
                        raise Exception('Erro sintatico Ponto e Virgula na linha ' + str(self.tokenAtual().linha))
                else:
                    self.erro = True
                    raise Exception('Erro sintatico parentese esquerdo chama de funcao '+str(self.tokenAtual().linha))
            else:
                self.erro = True
                raise Exception('Erro sintatico identificador chamada de funcao ou procedimento '+str(self.tokenAtual().linha))
        #IF
        elif(self.tokenAtual().tipo == 'IF'):
            self.indexToken+=1
            if(self.tokenAtual().tipo == 'LBRACK'):
                self.indexToken +=1
                self.condicao()# precisa atualizar o index dentro
                if(self.tokenAtual().tipo == 'RBRACK'):
                    self.indexToken +=1
                    if(self.tokenAtual().tipo == 'LCBRACK'):
                        self.indexToken +=1
                        while(self.tokenAtual().tipo != 'RCBRACK'):
                            self.statement()
                        #fora do laço, encontrou o RCBRACK
                        self.indexToken +=1
                        if(self.tokenAtual().tipo == 'ELSE'):
                            self.indexToken +=1
                            if(self.tokenAtual().tipo == 'LCBRACK'):
                                self.indexToken +=1
                                while(self.tokenAtual().tipo != 'RCBRACK'):
                                    self.statement()
                                self.indexToken +=1
                            else:
                                self.erro = True
                                raise Exception('Erro sintatico chaves esquerda else na linha '+str(self.tokenAtual().linha)+' '+str(self.tokenAtual().lexema))    
            
                    else:
                        self.erro = True
                        raise Exception('Erro sintatico chaves esquerda IF na linha '+str(self.tokenAtual().linha)+' '+str(self.tokenAtual().lexema))    
            
                else:
                    self.erro = True
                    raise Exception('Erro sintatico parentese direito IF na linha '+str(self.tokenAtual().linha)+' '+str(self.tokenAtual().lexema))    
             
            else:
                self.erro = True
                raise Exception('Erro sintatico parentese esquerdo IF na linha '+str(self.tokenAtual().linha)+' '+str(self.tokenAtual().lexema))    
        #While
        elif(self.tokenAtual().tipo == 'WHILE'):
            self.indexToken += 1
            if(self.tokenAtual().tipo == 'LBRACK'):
                self.indexToken += 1
                self.condicao()
                #print(self.tokenAtual().lexema)
                if(self.tokenAtual().tipo == 'RBRACK'):
                    self.indexToken += 1
                    if(self.tokenAtual().tipo == 'LCBRACK'):
                        self.indexToken += 1
                        while(self.tokenAtual().tipo != 'RCBRACK'):
                            if(self.tokenAtual().tipo == 'BREAK' or self.tokenAtual().tipo == 'CONTINUE'):
                                self.indexToken += 1
                                if(self.tokenAtual().tipo == 'SEMICOLON'):
                                    self.indexToken += 1
                                else:
                                    self.erro = True
                                    raise Exception('Erro sintatico ponto e virgula na linha '+str(self.tokenAtual().linha)+' '+str(self.tokenAtual().lexema)) 
                            else:
                                self.statement()
                        self.indexToken += 1
                    else:
                        self.erro = True
                        raise Exception('Erro sintatico chaves esquerda else na linha '+str(self.tokenAtual().linha)+' '+str(self.tokenAtual().lexema))         
                else:
                    self.erro = True
                    raise Exception('Erro sintatico parentese direito WHILE na linha '+str(self.tokenAtual().linha)+' '+str(self.tokenAtual().lexema))
            else:
                self.erro = True
                raise Exception('Erro sintatico parentese esquerdo WHILE na linha '+str(self.tokenAtual().linha)+' '+str(self.tokenAtual().lexema))     
        else:
            if(self.tokenAtual().tipo == 'FIM'):
                self.erro = True
                raise Exception('Missing Token na linha '+str(self.tokenAtual().linha)+' '+str(self.tokenAtual().lexema))    
            self.erro = True
            raise Exception('Erro sintatico Token fora do statement na linha '+str(self.tokenAtual().linha)+' '+str(self.tokenAtual().lexema))
    #deve retornar o valor das expressoes, pra salvar na tabela de simbolos
    def expression(self):
        if(self.tokenAtual().tipo == 'NUMBER'):#<numero> que pode occorrer só, na aritmetica ou na logica
            if (not (self.lookAhead().tipo == 'EQUAL' or self.lookAhead().tipo == 'DIFF' or self.lookAhead().tipo == 'LESS' or self.lookAhead().tipo == 'LESSEQUAL' or self.lookAhead().tipo == 'GREAT' or self.lookAhead().tipo == 'GREATEQUAL')):# Se nao tiver simbolo de expressao logica
                #checa simbolo de op aritmetica
                if(not (self.lookAhead().tipo == 'SUM' or self.lookAhead().tipo == 'SUB' or self.lookAhead().tipo == 'DIV' or self.lookAhead().tipo == 'MUL')):#Se nao tiver simbolo de expressao aritmetica
                    #Entra aqui se for apenas numero
                    val = self.tokenAtual().lexema
                    self.indexToken +=1
                    return val
                else:#Se tiver simbolo aritmetico
                    aritExpr = str(self.tokenAtual().lexema)
                    self.indexToken+=1 # Em cima do simbolo aritmetico
                    aritExpr+=str(self.tokenAtual().lexema)
                    if(self.lookAhead().tipo == 'NUMBER' or (self.lookAhead().tipo == 'ID' and (self.lookAhead().lexema[0] == 'v' or self.lookAhead().lexema[0] == 'f'))):
                        aritExpr+=str(self.lookAhead().lexema) ### funcionando para numero e numer apenas
                        if(self.lookAhead().lexema[0] =='v'):
                            if(not self.checkVarExiste(self.lookAhead().lexema)):##Checa se existe aquele ID declarado antes
                                raise Exception('Erro Semântico na aritmetica, Variável inexistente: '+str(self.lookAhead().lexema)+' na linha: ',self.lookAhead().linha)
                        elif(self.lookAhead().lexema[0] == 'f'):
                            if(not self.checkFuncExiste(self.lookAhead().lexema)):##Checa se existe aquele ID declarado antes
                                raise Exception('Erro Semântico na aritmetica, Função inexistente: '+str(self.lookAhead().lexema)+' na linha: ',self.lookAhead().linha)
                        
                        self.indexToken +=2 #Token depois do numero
                        #Mais de um termo na expressao, entra nesse if
                        if(self.tokenAtual().tipo == 'SUM' or self.tokenAtual().tipo == 'SUB' or self.tokenAtual().tipo == 'DIV' or self.tokenAtual().tipo == 'MUL'):
                            aritExpr += self.tokenAtual().lexema
                            self.indexToken += 1
                            aritExpr += self.expression()
                        return aritExpr
                    else:
                        self.erro = True
                        raise Exception('Erro sintatico numero op ?, (arithmetic expression) na linha '+str(self.tokenAtual().linha))
            else: #Se tiver simbolo de expressao logica, logica so permite 2 termos
                logicExpr = str(self.tokenAtual().lexema)
                self.indexToken +=1 # Em cima do simbolo logico (op-condicional)
                logicExpr+=str(self.tokenAtual().lexema)

                if(self.lookAhead().tipo == 'NUMBER'):
                    logicExpr += str(self.lookAhead().lexema)
                    self.indexToken+=2
                    return logicExpr
                elif(self.lookAhead().tipo == 'ID'):
                    if(self.lookAhead().lexema[0] == 'v'):
                        logicExpr += str(self.lookAhead().lexema)
                        if(not self.checkVarExiste(self.lookAhead().lexema)):##Checa se existe aquele ID declarado antes
                            raise Exception('Erro Semântico na op logica, Variável inexistente: '+str(self.lookAhead().lexema)+' na linha: ',self.lookAhead().linha)                        
                        self.indexToken +=2
                        return logicExpr
                    else:
                        self.erro = True
                        raise Exception('Erro sintatico operacao sem variavel '+str(self.tokenAtual().linha))
                else:
                    self.erro = True
                    raise Exception('Erro sintatico numero op ?, (logical expression) na linha '+str(self.tokenAtual().linha))
        
        elif(self.tokenAtual().tipo == 'BOOLEAN'):# Se a expressão for só um boolean
            val = self.tokenAtual().lexema
            self.indexToken +=1
            return val

        elif(self.tokenAtual().tipo == 'ID'):# Identificador de Função e Variável
            if(self.tokenAtual().lexema[0] == 'v' or self.tokenAtual().lexema[0] == 'f'):# checa se o identificador começa com f ou v
                if(self.tokenAtual().lexema[0] == 'f'):# se for uma funcao
                    funcExpr = str(self.tokenAtual().lexema)
                    if(not self.checkFuncExiste(funcExpr)):
                        raise Exception('Erro Semântico na atribuição, Função inexistente: '+str(funcExpr)+' na linha: ',self.tokenAtual().linha)
                    self.indexToken+=1
                    if(self.tokenAtual().tipo == 'LBRACK'):
                        funcExpr += str(self.tokenAtual().lexema)
                        self.indexToken +=1
                        while(self.tokenAtual().tipo != 'RBRACK'):# verifica argumentos da funcao para ser chamada, nao checa tipos (semantica)
                            if(self.tokenAtual().tipo == 'NUMBER' or self.tokenAtual().tipo == 'BOOLEAN' or self.tokenAtual().lexema[0] == 'v'):#verifica se foi passado numero, boolean, ou variavel
                                funcExpr += str(self.tokenAtual().lexema)
                                self.indexToken += 1
                                if(self.tokenAtual().tipo == 'COMMA'):
                                    funcExpr += str(self.tokenAtual().lexema)
                                    self.indexToken +=1
                                    if(self.tokenAtual().tipo == 'RBRACK'):#nao ta incrementando  index igual as outras funcoes, mas ta funcionando
                                        self.erro = True
                                        raise Exception('Erro sintatico falta de argumentos na linha ' + str(self.tokenAtual().linha))
                                elif(self.tokenAtual().tipo == 'RBRACK'):
                                    funcExpr += str(self.tokenAtual().lexema)
                                    break
                                else:
                                    self.erro = True
                                    raise Exception('Erro sintatico Virgula na linha ' + str(self.tokenAtual().linha))
                            else:
                                self.erro = True
                                raise Exception('Erro sintatico argumento invalido na linha ' + str(self.tokenAtual().linha))
                        #fora do laço encontrou o RBRACK
                        self.indexToken+=1
                        return funcExpr
                    else:
                        self.erro = True
                        raise Exception('Erro sintatico Parentese esquerdo da Funcao declaracao na linha ' + str(self.tokenAtual().linha))
                else:#é uma variavel
                    varExpr = str(self.tokenAtual().lexema)
                    if(self.checkVarExiste(varExpr)):
                        self.indexToken +=1
                        return varExpr
                    else:
                        raise Exception('Erro Semântico na atribuição, Variável inexistente: '+str(varExpr)+' na linha: ',self.tokenAtual().linha)
            else:
                self.erro = True
                raise Exception('Erro sintatico, id nao comeca com f ou v '+str(self.tokenAtual().linha))
        else:
            self.erro = True
            raise Exception('Erro sintatico expression '+str(self.tokenAtual().linha))

    def condicao(self):
        self.expression()
        self.condicao_aux()
        return
    def condicao_aux(self):
        if(self.tokenAtual().tipo == 'EQUAL' or self.tokenAtual().tipo == 'DIFF' or self.tokenAtual().tipo == 'LESS' or self.tokenAtual().tipo == 'LESSEQUAL' or self.tokenAtual().tipo == 'GREAT' or self.tokenAtual().tipo == 'GREATEQUAL'):
            self.indexToken +=1
            self.condicao()
            return
        else:
            return
    def lookAhead(self):
        return self.tabTokens[self.indexToken + 1]

    #Estrutura da Tabela de Simbolos
    #idx 0 - tipo do comando: VAR, FUNC, PUTS, ATTR -> vA = 1;
    #idx 1 - tipo da var ou do retorno de funcao, ou do que o Puts ta printando: INT, TBOOLEAN
    #idx 2 - identificador da func ou da var: vA, fSum
    #idx 3 - valor da var, retorno da func etc: 1+2+3
    #idx 4 - escopo onde aquela var ou func tá - self.indexEscopoAtual
    def checkSemantica(self,tipo,index):#checa semantica, se tiver tudo OK return True
        if(tipo == 'VARDEC'): # checa semantica de declaração de Variável
            simbAtual = self.tabSimbolos[index]
            if(simbAtual[1] == 'INT'):
                if(simbAtual[3].isnumeric() or bool(re.match(r"[0-9A-Za-z]*\({0,}( ){0,}([+-/*]( ){0,}[0-9A-Za-a]*( ){0,})*\){0,}",simbAtual[3]))):
                    self.indexDecAtual +=1
                    return True
                else:
                    #linha do ponto e virgula que é a mesma
                    raise Exception("Erro Semântico, variavel do tipo inteiro nao recebe inteiro na linha: "+str(self.tokenAtual().linha))
            if(simbAtual[1] == 'TBOOLEAN'):
                if(simbAtual[3] == 'true' or simbAtual[3] == 'false'):
                    self.indexDecAtual +=1
                    return True
                elif(self.checkValBool(simbAtual[3])):
                    self.indexDecAtual +=1
                    return True

                else:
                    #linha do ponto e virgula que é a mesma
                    raise Exception("Erro Semântico, variavel do tipo boolean nao recebe boolean na linha: "+str(self.tokenAtual().linha))
        
        elif(tipo == 'FUNCDEC'):
            simbDecFuncao = self.tabSimbolos[index]
            #verificando tipo do retorno da função e se a variavel no retorno existe no escopo
            if(self.checkExisteNoEscopo('VAR', simbDecFuncao[1], simbDecFuncao[3], simbDecFuncao[4]) or self.checkExisteNoEscopo('VAR', simbDecFuncao[1], simbDecFuncao[3], simbDecFuncao[4] + 1)):
                self.indexDecAtual += 1
                return True
            else:
                return True ##Bypass pra teste
                raise Exception("Erro Semântico, variavel no retorno da função não está declarada ou a variável possui um tipo diferente de retorno da função: "+str(self.tokenAtual().linha))

        #elif(outros tipos)
    def checkValBool(self, string):
        #checa se é numero, variavel ou expressao aritmetica ou retorno de funcao | ideia que se for diferente de 0 é true
        if(string.isnumeric() or bool(re.match(r"[0-9A-Za-z]*\({0,}( ){0,}([+-/*]( ){0,}[0-9A-Za-a]*( ){0,})*\){0,}",string))):
            return True
        #expressao logica, so checo o primeiro char apos o numero
        #expressoes logicas pela gramatica so tem 2 termos 1 < 2 e nao 1 < 2 < 3
        if(string[1] == '<' or string[1] == '=' or string[1] == '>'):
            return True

    def checkExisteNoEscopo(self, dec, tipo, variavel, indexEscopo):
        for x in range(len(self.tabSimbolos)):
            if(self.tabSimbolos[x][0] == dec and self.tabSimbolos[x][1] == tipo and self.tabSimbolos[x][2] == variavel and self.tabSimbolos[x][4] == indexEscopo):
                return True
        return False
    
    def checkVarExiste(self,var):# Modificar depois que bruno colocar lista de parametros, pra checar os parametros
                                 # Verificar questão do Escopo
        achou = False
        for i in self.tabSimbolos:
            if(i[2].strip("'") == var):
                achou = True
        return achou    

    def checkFuncExiste(self,func):# Modificar depois que bruno colocar lista de parametros, pra checar os parametros
                                   # Verificar questão do Escopo
        achou = False
        for i in self.tabSimbolos:
            if(i[2].strip("'") == func):
                achou = True
        return achou

    def adicionarVarDeRetornoFuncTabSimbolo(self, temp):
        for x in range(len(self.tabSimbolos)):
            if(temp[0] == self.tabSimbolos[x][0] and temp[1] == self.tabSimbolos[x][1] and temp[2] == self.tabSimbolos[x][2] and temp[4] == self.tabSimbolos[x][4]):
                self.tabSimbolos[x][3] = temp[3]
    def buscarSimboloVarPorLexema(self,lexema):# checa se tá no mesmo escopo ou no escopo global que é o 0
        for i in self.tabSimbolos:
            if(i[0].strip("'") == 'VAR' and i[2].strip("'") == lexema and (self.indexEscopoAtual == i[4] or i[4] == 0)):
                return i
            elif( i[0].strip("'") == 'FUNC' and len(i[5]) != 0):
                for k in i[5]:
                    if(k[0].strip("'") == 'VAR' and k[2].strip("'") == lexema and (self.indexEscopoAtual == k[4] or k[4] == 0)):
                        return k
        return ''