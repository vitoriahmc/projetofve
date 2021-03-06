from flask import Flask, render_template, request, url_for, redirect, send_from_directory
from werkzeug import secure_filename
import os
import random
import firecall

"""
O FireBase é um database que utiliza dicionarios e listas para fazer armazanamentos,
para isso criamos o nosso, chamado PETinder, que salva os dicionarios que queremos 
na url a seguir:https://petinder.firebaseio.com/ 
Usamos metodos do firecall que importamos para fazer esta conexao.
"""
"""
O firecall faz essa ligacao entre o flask e FireBase, os metodos importados para uso sao
arquivos como put, para inserir o dado recebido para o firebase e get para que pegar um
dado no firebase e enviar para o flask, alem disso utilizaAmos o eval que funciona 
como um transformador, ele pega os dados do firebase em binario e transforma em string

"""
PETinder=firecall.Firebase("https://petinder.firebaseio.com/")
USER=[]
NOME=[]
ListadogBR=[]
ListadogDoar=[]

'''As listas acima foram criadas para armazenar todos os dados que necessitariamos
fazer verificacoes se ja existe um nome ou email, utilizado apenas para facilitar 
o uso geral. As funcoes abaixo sao usadas para pegar deletar os caes, nao sao 
partes do objeto porque alem o usuario poder apagar, ao ser adotado ou encontrado
um parceiro por parte de outra pessoa que pode aceitar o cao, assim, o cao nao deve esetar disponivel na lista do outro
'''

def Del_CaesBR(nome):
    dono=eval(PETinder.get_sync(point="/ListadogBR/{0}/nomepessoa".format(nome)))
    PETinder.delete_sync(point="Pessoas/{0}/Caes_BR/{1}".format(dono,nome))
    PETinder.delete_sync(point="ListadogBR/{0}".format(nome))

def Del_CaesDoar(nome):
    dono=eval(PETinder.get_sync(point="/ListadogDoar/{0}/nomepessoa".format(nome)))
    PETinder.delete_sync(point="Pessoas/{0}/CaesDoar/{1}".format(dono,nome))
    PETinder.delete_sync(point="ListadogDoar/{0}".format(nome))
    
'''
Objetos foram criados para facilitar na montagem dos atributos de cada pessoa, 
e cada cao, deixando o codigo mais organizado e facil de arrumar
'''

class Pessoa():
    
    def __init__(self, pessoa, nomepessoa, email, senha):
        self.pessoa=pessoa
        self.nomepessoa = nomepessoa
        self.email = email
        self.senha = senha
        self.dicionario={}
        self.caosex=[]
        self.caodoa=[]
        
    def Salvar_Pessoa(self):
        self.dicionario["pessoa"]=self.pessoa
        self.dicionario["email"]=self.email
        self.dicionario["nomepessoa"]=self.nomepessoa
        self.dicionario["senha"]=self.senha
        self.dicionario["caesBR"]=self.caosex
        self.dicionario["caesDoar"]=self.caodoa
           
        PETinder.put_sync(point="/Pessoas/{0}".format(self.nomepessoa),data=self.dicionario)
        
        

class Caes():
    
    def __init__(self, nome, raca, sexo, idade, cor, saude, cidade,filename):
        self.nome = nome
        self.raca = raca
        self.sexo = sexo
        self.cidade = cidade    
        self.idade = idade
        self.cor = cor
        self.saude = saude
        self.filename=filename
        self.dicionariocaosex={}
        self.dicionariocaodoa={}
        
        
class CaesBR(Caes):
    def __init__(self,nome,raca,sexo,cidade,idade,cor,saude,filename):
        Caes.__init__(self,nome,raca,sexo,cidade,idade,cor,saude,filename)
    
    def Salvar_CaesBR(self,user):
        
        self.dicionariocaosex["nome"]=self.nome
        self.dicionariocaosex["raca"]=self.raca
        self.dicionariocaosex["sexo"]=self.sexo
        self.dicionariocaosex["cidade"]=self.cidade
        self.dicionariocaosex["idade"]=self.idade
        self.dicionariocaosex["cor"]=self.cor        
        self.dicionariocaosex["saude"]=self.saude
        self.dicionariocaosex["filename"]=self.filename
        self.dicionariocaosex["email"]=eval(PETinder.get_sync(point="/Pessoas/{0}/email".format(user)))        
        self.dicionariocaosex["nomepessoa"]=eval(PETinder.get_sync(point="/Pessoas/{0}/nomepessoa".format(user)))
        ListadogBR.append(self.dicionariocaosex)
        PETinder.put_sync(point="/Pessoas/{0}/Caes_BR/{1}".format(user,self.nome),data=self.dicionariocaosex)
        PETinder.put_sync(point="/ListadogBR/{0}".format(self.nome),data=ListadogBR[-1])
        

class CaesDoar(Caes):
    def __init__(self,nome,raca,sexo,cidade,idade,cor,saude,filename):
        Caes.__init__(self,nome,raca,sexo,cidade,idade,cor,saude,filename)

    def Salvar_CaesDoar(self,user):
        
        self.dicionariocaodoa["nome"]=self.nome
        self.dicionariocaodoa["raca"]=self.raca
        self.dicionariocaodoa["sexo"]=self.sexo
        self.dicionariocaodoa["cidade"]=self.cidade
        self.dicionariocaodoa["idade"]=self.idade
        self.dicionariocaodoa["cor"]=self.cor        
        self.dicionariocaodoa["saude"]=self.saude
        self.dicionariocaodoa["filename"]=self.filename
        self.dicionariocaodoa["email"]=eval(PETinder.get_sync(point="/Pessoas/{0}/email".format(user)))        
        self.dicionariocaodoa["nomepessoa"]=eval(PETinder.get_sync(point="/Pessoas/{0}/nomepessoa".format(user)))
        ListadogDoar.append(self.dicionariocaodoa)
        PETinder.put_sync(point="/Pessoas/{0}/CaesDoar/{1}".format(user,self.nome),data=self.dicionariocaodoa)
        PETinder.put_sync(point="/ListadogDoar/{0}".format(self.nome),data=ListadogDoar[-1])
"""
Aqui seria todos os metodos que utilizamos para controlar melhor o que colocamos no FireBase,
ao longo do codigo ha outros metodos para fazer pesquisas no FireBase, porem nao criamos funcoes
porque seria algo que teria uso pequeno, em condicoes especiais
"""
"""
O código abaixo se refere ao Flask e tem como principal objetivo fazer o meio campo entre os
arquivos HTML e o FireBase, ou seja, é responsável por enviar as informações coletadas pelo HTML 
para o FireBase e enviá-las de volta para o HTML quando requisitadas.
"""
app = Flask(__name__, static_url_path='')

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
    
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
                             
@app.route('/', methods=['POST','GET'])
#A def firstpage é responsável por tudo o que irá ocorrer no end point '/'. 
#No caso, ela receberá os dados de login e validará esses dados a partir das informações
#armazenadas no FireBase.

def firstpage():
    #LOGIN
    if request.method == 'POST': 
        nomepessoa = request.form['nomepessoa'] 
        senha = request.form['senha'] 
        L = eval(PETinder.get_sync(point="/ListaUSER")) 
        #Validação do login:
        if nomepessoa in L:
            listasenha=[]
            s= eval(PETinder.get_sync(point="/Pessoas/{0}/senha".format(nomepessoa)))
            listasenha.append(s)
            if senha in listasenha:
                return render_template('home.html', nomepessoa=nomepessoa)
            else: 
                e = 'Senha incorreta'
                
                return render_template('mainerro.html', nomepessoa=nomepessoa, dic = PETinder.get_sync(point="/Pessoas/{0}".format(nomepessoa)), erro = e) 
        else:
            e = 'Usuário inválido'
            return render_template('mainerro.html', nomepessoa=nomepessoa, dic = PETinder.get_sync(point="/Pessoas/{0}".format(nomepessoa)), erro = e)

    return render_template('main.html', pessoa = Pessoa('','','',''))        

    
@app.route('/login', methods=['POST','GET'])
#A def conta é responsável por tudo o que irá ocorrer no end point 'login'.
#Essa def recebe os dados inseridos pelo usuário, passa eles pelas condições de cadastro
#e, caso esteja tudo correto, envia os dados para o FireBase. Caso não passe em algumas das 
#condições, a def retorna uma mensagem de erro que será exibida para o usuário pelo HTML.

def conta():
    #CADASTRO DO USUÁRIO
    if request.method == 'POST':
        nome = request.form['pessoa'] 
        nomepessoa = request.form['nomepessoa'] 
        email = request.form['email'] 
        senha = request.form['senha'] 
        use= eval(PETinder.get_sync(point="/ListaUSER")) 
        mail=[]        
        for p in use:        
            usemail=eval(PETinder.get_sync(point="/Pessoas/{0}/email".format(p)))
            mail.append(usemail)
            
        #Condições de cadastro do usuário:
        if nomepessoa in use:
            e = 'Usuário já cadastrado'
            return render_template('loginrepetido.html', dic = PETinder.get_sync(point="/Pessoas/{0}".format(nomepessoa)), erro = e)
        elif email == "":
            e = 'O campo Email está vazio'
            return render_template('loginemail.html', dic = PETinder.get_sync(point="/Pessoas/{0}".format(nomepessoa)), erro = e)
        elif email in mail:
            e = 'Email já cadastrado'
            return render_template('loginemailrep.html', dic = PETinder.get_sync(point="/Pessoas/{0}".format(nomepessoa)), erro = e)
        elif senha == "":
            e = 'O campo Senha está vazio'
            return render_template('loginsenha.html', dic = PETinder.get_sync(point="/Pessoas/{0}".format(nomepessoa)), erro = e)        
        elif nomepessoa == "":
            e = 'O campo Usuário está vazio'
            return render_template('loginusuario.html', dic = PETinder.get_sync(point="/Pessoas/{0}".format(nomepessoa)), erro = e)        
        elif nome == "":
            e = 'O campo Nome está vazio'
            return render_template('loginnome.html', dic = PETinder.get_sync(point="/Pessoas/{0}".format(nomepessoa)), erro = e)
        else:
            #Cadastro o novo usuário e manda as informações para o firebase
            USER.append(nomepessoa)
            USER[-1] = Pessoa(nome , nomepessoa, email, senha)
            USER[-1].Salvar_Pessoa() 
            PETinder.put_sync(point="/ListaUSER/{0}".format(nomepessoa),data=nomepessoa)                
            return render_template('home.html', dic = USER[-1].nomepessoa, nomepessoa = nomepessoa)

    return render_template('login.html', erro = '')
    
@app.route('/cadastro', methods=['POST','GET'])
#A def cadastro é responsável por tudo que ocorre no end point '/cadastro'.
#Ela receberá os dados de cadastro de um cão para encontrar parceiro e, após passar pelas
#condições de cadastro, irá armazenar o cão no usuário logado no momento. Se os dados não 
#passarem pelas condições ela retornará, também, uma mensagem de erro.

def cadastro():
    #CADASTRO DE CÃES PARA ENCONTRAR PARCEIRO
    user=request.args['user'] #Chama o usuário que está logado  
    if request.method=='POST':

        nome = request.form['nome'] 
        raca = request.form['raca'] 
        sexo = request.form['sexo'] 
        cidade = request.form['cidade']
        idade = request.form['idade'] 
        cor = request.form['cor'] 
        saude = request.form['saude']
        use=eval(PETinder.get_sync(point="/ListadogBR")) 
        file = request.files['filename']
        
        #Condições de cadastro do cão:   
                   
        if nome in use:
            e = 'Cão já cadastrado'
            return render_template('cadastrorepetido.html', dic = PETinder.get_sync(point="/ListadogBR/{0}".format(nome)),nomepessoa = user, erro = e)
        elif nome == "":
            e = 'O campo Nome está vazio'
            return render_template('cadastronome.html', dic = PETinder.get_sync(point="/ListadogBR/{0}".format(nome)),nomepessoa = user, erro = e)
        elif raca == "":
            e = 'O campo Raça está vazio'
            return render_template('cadastroraca.html', dic = PETinder.get_sync(point="/ListadogBR/{0}".format(nome)),nomepessoa = user, erro = e)       
        elif sexo == "0":
            e = 'O campo Sexo deve ser selecionado'
            return render_template('cadastrosexo.html', dic = PETinder.get_sync(point="/ListadogBR/{0}".format(nome)),nomepessoa = user, erro = e)        
        elif cidade == "":
            e = 'O campo Cidade está vazio'
            return render_template('cadastrocidade.html', dic = PETinder.get_sync(point="/ListadogBR/{0}".format(nome)),nomepessoa = user, erro = e)
        elif idade == "":
            e = 'O campo Idade está vazio'
            return render_template('cadastroidade.html', dic = PETinder.get_sync(point="/ListadogBR/{0}".format(nome)),nomepessoa = user, erro = e)
        elif cor == "":
            e = 'O campo Cor está vazio'
            return render_template('cadastrocor.html', dic = PETinder.get_sync(point="/ListadogBR/{0}".format(nome)),nomepessoa = user, erro = e)
        else:
            #Cadastra o novo cão do usuário logado e manda as informações para o firebase
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            NOME.append(nome)
            NOME[-1] = CaesBR(nome, raca, sexo, idade, cor, saude, cidade,filename)
            NOME[-1].Salvar_CaesBR(user)
            return redirect(url_for('perfil', user=user, file=file))

    return render_template('cadastro.html',nomepessoa = user, erro = '')
    
    
    
@app.route('/caddoar', methods=['POST','GET'])
#A def caddoar é responsável por tudo que ocorre no end point '/caddoar'.
#Ela receberá os dados de cadastro de um cão para doar e, após passar pelas
#condições de cadastro, irá armazenar o cão no usuário logado no momento. Novamente,
#se os dados não passarem pelas condições ela retornará uma mensagem de erro.

def caddoar():
    #CADASTRO DE CÃES PARA DOAR
    user=request.args['user']
    if request.method == 'POST':     
        nome = request.form['nome']
        raca = request.form['raca']
        sexo = request.form['sexo']
        cidade = request.form['cidade']
        idade = request.form['idade']
        cor = request.form['cor']
        saude = request.form['saude']
        use=eval(PETinder.get_sync(point="/ListadogDoar"))
        file = request.files['filename']
        #Condições de cadastro do cão para doar:   
        if nome in use:
            e = 'Usuário já cadastrado'
            return render_template('caddoarrepetido.html', dic = PETinder.get_sync(point="/Listadogoar/{0}".format(nome)),nomepessoa = user, erro = e)
        elif nome == "":
            e = 'O campo Nome está vazio'
            return render_template('caddoarnome.html', dic = PETinder.get_sync(point="/Listadogoar/{0}".format(nome)),nomepessoa = user, erro = e)
        elif raca == "":
            e = 'O campo raca está vazio'
            return render_template('caddoarraca.html', dic = PETinder.get_sync(point="/Listadogoar/{0}".format(nome)),nomepessoa = user, erro = e)       
        elif sexo == "0":
            e = 'O campo sexo deve ser selecionado'
            return render_template('caddoarsexo.html', dic = PETinder.get_sync(point="/Listadogoar/{0}".format(nome)),nomepessoa = user, erro = e)        
        elif cidade == "":
            e = 'O campo cidade está vazio'
            return render_template('caddoarcidade.html', dic = PETinder.get_sync(point="/Listadogoar/{0}".format(nome)),nomepessoa = user, erro = e)
        elif idade == "":
            e = 'O campo idade está vazio'
            return render_template('caddoaridade.html', dic = PETinder.get_sync(point="/Listadogoar/{0}".format(nome)),nomepessoa = user, erro = e)
        elif cor == "":
            e = 'O campo cor está vazio'
            return render_template('caddoarcor.html', dic = PETinder.get_sync(point="/Listadogoar/{0}".format(nome)),nomepessoa = user, erro = e)
        else:
            #Cadastra o novo cão do usuário logado e manda as informações para o firebase
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            NOME.append(nome)
            NOME[-1] = CaesDoar(nome, raca, sexo, idade, cor, saude, cidade, filename)
            NOME[-1].Salvar_CaesDoar(user)
            return redirect(url_for('doar', user=user, filename=filename))
        
   
    return render_template('caddoar.html', nomepessoa = user, erro = '')
        
@app.route('/home', methods=['POST', 'GET'])
#A def home é responsável por tudo o que irá ocorrer no end point '/home'.
#A def irá identificar qual dos três botões criados pelo HTML foi selecionado pelo usuário
#e o redicionará para a próxima página, que é referente ao botão escolhido. Além disso, ela
#retornará todas as informações necessárias para as páginas seguintes.

def home():
  
    button=request.form['button']
    user=request.args['user']
    
    
    if request.method == 'POST':
        
        if button == "parceiro":
            try:
                listausers= eval(PETinder.get_sync(point="/Pessoas/{0}/Caes_BR".format(user)))
                for y in listausers:
                    return redirect(url_for('perfil', user=user))
            except:
                return render_template('perfil.html', nomepessoa=user)
        
        elif button == "doar":
            try:
                listauser=eval(PETinder.get_sync(point="/Pessoas/{0}/CaesDoar".format(user)))
                for x in listauser:                
                    return redirect(url_for('doar', user = user ))
            except:
                return render_template('doar.html', nomepessoa = user)
        
        elif button == "adotar":
            cachorros=eval(PETinder.get_sync(point="/ListadogDoar"))
            sorte=random.choice(list(cachorros.keys()))    
            while (eval(PETinder.get_sync(point="/ListadogDoar/{0}/nomepessoa".format(sorte)))) == user:
                sorte=random.choice(list(cachorros.keys()))                
            return redirect(url_for('adotar', user=user, cao=sorte ))
            
    return render_template('home.html', nomepessoa = user)
        
@app.route('/perfil', methods=['POST', 'GET'])
#A def perfil é responsável por tudo o que irá ocorrer no end point '/perfil'.
#Ela irá pegar os dados do FireBase referentes aos cachorros cadastrado para encontrar 
#um parceiro do usuário logado e retornará os nomes desses cães para o HTML.

def perfil():
    user=request.args['user']
    try:
        caesb= eval(PETinder.get_sync(point="/Pessoas/{0}/Caes_BR".format(user)))
        listacaes=[]
        for j in caesb:
            caes=eval(PETinder.get_sync(point="/Pessoas/{0}/Caes_BR/{1}/nome".format(user, j)))
            listacaes.append(caes)
 
            return render_template('perfil.html', nomepessoa=user, caesb=caesb)
    
    except:
        return render_template('perfil.html', nomepessoa=user)
    
@app.route('/doar', methods=['POST', 'GET'])
#A def doar é responsável por tudo o que irá ocorrer no end point '/doar'.
#Ela irá pegar os dados do FireBase referentes aos cachorros cadastrado para doar 
#do usuário logado e retornará os nomes desses cães para o HTML.

def doar():
    user=request.args['user']
    try:
        caesdoar= eval(PETinder.get_sync(point="/Pessoas/{0}/CaesDoar".format(user)))
        listacaesd=[]
        for i in caesdoar:
            caesd=eval(PETinder.get_sync(point="/Pessoas/{0}/CaesDoar/{1}/nome".format(user, i)))
            listacaesd.append(caesd)

            return render_template('doar.html', nomepessoa=user, caesdoar=caesdoar)
    except:
        return render_template('doar.html', nomepessoa = user)
        
@app.route('/opt', methods=['POST', 'GET'])
#A def opt é responsável por tudo o que irá ocorrer no end point '/opt'.
#Essa def irá receber do FireBase os dados de todos os cães cadastrados para encontrar um 
#parceiro (com exceção do cão do usuário logado) e retornará alguns dados de cada ção para 
#o HTML. 

def opt():
    user=request.args['user']
    cachorros=(eval(PETinder.get_sync(point = "/ListadogBR")))
    sorte=random.choice(list(cachorros.keys()))
    while (eval(PETinder.get_sync(point="/ListadogBR/{0}/nomepessoa".format(sorte)))) == user:
                sorte=random.choice(list(cachorros.keys()))            
    
    caninos=(eval(PETinder.get_sync(point = "/ListadogBR/{0}".format(sorte))))
    file=eval(PETinder.get_sync(point="/ListadogBR/{0}/filename".format(sorte)))     
    return render_template('opt.html', cao = sorte, filename=file, caninos = caninos, nomepessoa = user)
                
    
    
@app.route('/user', methods=['POST', 'GET'])
#A def usuario é responsável por tudo o que irá ocorrer no end point '/user'.
#Ela irá receber do FireBase todas as informções do cão escolhido pelo usuário no
#end point '/opt' e os retornará para o HTML.

def usuario():
    user=request.args['user']
    cao = request.args['cao']
    name=eval(PETinder.get_sync(point="/ListadogBR/{0}".format(cao)))
    file=eval(PETinder.get_sync(point="/ListadogBR/{0}/filename".format(cao)))
    return render_template('user.html', user=user,filename=file, cao=cao, name=name)
    
    
@app.route('/adotar', methods=['POST', 'GET'])
#A def adotar é responsável por tudo o que irá ocorrer no end point '/adotar'.
#Essa def irá receber do FireBase os dados de todos os cães cadastrados para doação
#(com exceção dos cães do usuário logado) e retornará alguns dados de cada ção para 
#o HTML. 

def adotar():
    user=request.args['user']
    cachorros=eval(PETinder.get_sync(point="/ListadogDoar"))
    sorte=random.choice(list(cachorros.keys()))
    while (eval(PETinder.get_sync(point="/ListadogDoar/{0}/nomepessoa".format(sorte)))) == user:
        sorte=random.choice(list(cachorros.keys()))           
    caesdoar= eval(PETinder.get_sync(point="/ListadogDoar/{0}".format(sorte)))
    file=eval(PETinder.get_sync(point="/ListadogDoar/{0}/filename".format(sorte)))
 
    return render_template('adotar.html', filename = file, cao=sorte, caesdoar=caesdoar, user=user)
    
@app.route('/adote', methods=['POST', 'GET'])
#A def adote é responsável por tudo o que irá ocorrer no end point '/adote'.
#Ela irá receber do FireBase todas as informções do cão escolhido pelo usuário no
#end point '/adotar' e os retornará para o HTML.

def adote():
    user=request.args['user']
    cao = request.args['cao']
    name=eval(PETinder.get_sync(point="/ListadogDoar/{0}".format(cao)))
    file=eval(PETinder.get_sync(point="/ListadogDoar/{0}/filename".format(cao)))
    return render_template('adote.html', user=user, filename=file, cao=cao, name=name)

@app.route('/del', methods=['POST', 'GET']) 
#A def delete1 é responsável pelo o que irá ocorrer no end point '/del'.
#Ao ser acionada, ela irá chamar a função do FireBase que irá deletar o cão que o usuário 
#desejar no end point '/doar'.

def delete1():
    user=request.args['user']
    nome=request.args['nome']
    Del_CaesDoar(nome)
    
    return redirect(url_for('doar', user=user))   
    
@app.route('/deld', methods=['POST', 'GET']) 
#A def delete2 é responsável pelo o que irá ocorrer no end point '/deld'.
#Ao ser acionada, ela irá chamar a função do FireBase que irá deletar o cão que o usuário 
#desejar no end point '/perfil'.

def delete2():
    user=request.args['user']
    nome=request.args['nome']
    Del_CaesBR(nome)
    
    return redirect(url_for('perfil', user=user))  

@app.route('/delfinal', methods=['POST', 'GET']) 
#A def delete3 é responsável pelo o que irá ocorrer no end point '/delfinal'.
#Ao ser acionada, ela irá chamar a função do FireBase que irá deletar o cão que o usuário 
#escolheu para adotar da lista de cães disponíveis. Depois, ela fará o usuário voltar para 
#o end point '/home'

def delete3():
    user=request.args['user']
    cao=request.args['cao']
    Del_CaesDoar(cao)
    
    return render_template('home.html', nomepessoa=user) 
        
        
@app.route('/deldfinal', methods=['POST', 'GET'])
#A def delete4 é responsável pelo o que irá ocorrer no end point '/deldfinal'.
#Ao ser acionada, ela irá chamar a função do FireBase que irá deletar o cão que o usuário 
#escolheu para formar um parceiro com o seu da lista de cães disponíveis. Depois, ela fará 
#o usuário voltar para o end point '/home'
 
def delete4():
    user=request.args['user']
    cao=request.args['cao']
    Del_CaesBR(cao)
    
    return render_template('home.html', nomepessoa=user) 
    
@app.route('/voltar', methods=['POST', 'GET']) 
#A def voltar é responsável pelo o que irá ocorrer no end point '/voltar'.
#Ela tem como único objetivo voltar para home.html com o usuário logado.

def voltar():
    user=request.args['user']

    return render_template('home.html', nomepessoa=user) 
    
if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=5000) #Começa o programa 