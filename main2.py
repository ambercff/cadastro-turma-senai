import os
import hashlib
import socketserver
from http.server import SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from db import conectar

conexao = conectar()

# Classe HTTP
class MyHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            # Abre o arquivo index.html
            f = open(os.path.join(path, 'index.html'), 'r')

            # Código de resposta para o cliente
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f.read().encode('utf-8'))

            f.close()

            return None
        
        except FileNotFoundError:
            print("hahahha")

        return super().list_directory(path)
    
    def usuario_existente(self, login, senha):
        cursor = conexao.cursor()
        cursor.execute("SELECT senha FROM dados_login WHERE login = %s", (login,))
        resultado = cursor.fetchone()
        cursor.close()

        if resultado:
            senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
            return senha_hash == resultado[0]
        
        return False
    
    def turma_existente(self, descricao):
        cursor = conexao.cursor()
        cursor.execute("SELECT descricao FROM turmas WHERE descricao = %s", (descricao,))
        resultado = cursor.fetchone()
        cursor.close()

        if resultado:
            return True
        
        return False
    
    def atividade_existente(self, descricao):
        cursor = conexao.cursor()
        cursor.execute("SELECT descricao FROM atividades WHERE descricao = %s", (descricao,))
        resultado = cursor.fetchone()
        cursor.close()

        if resultado:
            return True
        
        return False
    
    def adicionar_usuario(self, login, senha, nome):
        cursor = conexao.cursor()

        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        cursor.execute("INSERT INTO dados_login (login, senha, nome) VALUES (%s, %s, %s)", (login, senha_hash, nome))

        conexao.commit()

        cursor.close()

    def adicionar_turma(self, descricao, id_professor):
        cursor = conexao.cursor()

        cursor.execute("INSERT INTO turmas (descricao) VALUES (%s)", (descricao,))
        cursor.execute("SELECT id_turma FROM turmas WHERE descricao = %s", (descricao,))

        resultado = cursor.fetchone()

        cursor.execute("INSERT INTO turmas_professor (id_turma, id_professor) VALUES (%s, %s)", (resultado[0], id_professor))

        conexao.commit()

        cursor.close()

    def carrega_turmas_professor(self, login):
        # Carrega turmas do professor

        cursor = conexao.cursor()

        cursor.execute("SELECT id_professor, nome FROM dados_login WHERE login = %s", (login,))

        resultado = cursor.fetchone()

        cursor.close()

        # Resultaod[0] traz id_professor e resultado[1] trás o nome do professor
        id_professor = resultado[0]

        cursor = conexao.cursor()
        cursor.execute(
            "SELECT turmas.id_turma, turmas.descricao FROM turmas_professor INNER JOIN turmas ON turmas_professor.id_turma = turmas.id_turma WHERE turmas_professor.id_professor = %s", (id_professor,)
        )

        turmas = cursor.fetchall()
        cursor.close()

        # Construindo as linhas de tabela com o resultado
        linhas_tabela = ""
        for turma in turmas:
            id_turmas = turma[0]
            descricao_turma = turma[1]
            link_atividade = "<a href='tela_atividade'><button style='width: 180px; padding: 8px;border-radius: 10px;background-color: black;border: none;color: white;cursor: pointer;'> Cadastrar atividade <i class='fa-solid fa-plus'></i></button></a>"
            linha = "<tr><td style='text-align:center; border: 1px solid black; padding: 15px;'>{}</td><td style='text-align:center; border: 1px solid black; padding: 15px;'>{}</td></tr>".format(descricao_turma, link_atividade)
            linhas_tabela += linha

        with open(os.path.join(os.getcwd(), 'cadastrar_turma.html'), 'r', encoding='utf-8') as cad_turma_file:
            content = cad_turma_file.read()

            content = content.replace('{nome_professor}', resultado[1])
            content = content.replace('{id_professor}', str(id_professor))
            content = content.replace('{login}', str(login))

        content = content.replace('<!-- Tabela com linhas zebradas -->', linhas_tabela)

        self.send_response(200)
        self.send_header("Content-type", "text/html;charset=utf8")
        self.end_headers()

        self.wfile.write(content.encode('utf-8'))

    def adicionar_atividade(self, descricao):
        cursor = conexao.cursor()

        cursor.execute("INSERT INTO atividades (descricao) VALUES (%s)", (descricao,))

        conexao.commit()

        cursor.close()

   
    def do_GET(self):

        # Rota login
        if self.path == '/login':
            try:
                with open(os.path.join(os.getcwd(), 'login.html'), 'r') as login_file:
                    content = login_file.read()

                self.send_response(200)
                self.send_header("content-type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))

            except FileNotFoundError:
                self.send_error(404, "File not found")

        elif self.path == '/login_failed':

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'login.html'), 'r', encoding='utf-8') as login_file:
                content = login_file.read()
               
            # adiciona a mensagem de erro no conteudo da pagina
            mensagem = "Login e/ou senha incorreta. Tente novamente"
            content = content.replace('<!-- Mensagem de erro será inserida aqui -->',
                                      f'<div class="error-message">{mensagem}</div>')
           
            # Envia o conteudo modificado para o cliente
            self.wfile.write(content.encode('utf-8')) 

        # elif self.path.startswith('/tela_professor'):
        #     print("entrou tela professor")
        #     self.send_response(200)
        #     self.send_header("Content-type", "text/html; charset=utf-8")
        #     self.end_headers()

        #     with open(os.path.join(os.getcwd(), 'tela_professor.html'), 'r', encoding='utf-8') as file:
        #         content = file.read()

        #     self.wfile.write(content.encode('utf-8'))
            
        #     return
        
        elif self.path.startswith('/tela_turma'):
            self.send_response(200)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastrar_turma.html'), 'r', encoding='utf-8') as file:
                content = file.read()

            self.wfile.write(content.encode('utf-8'))
            
            return
        
        elif self.path.startswith('/tela_atividade'):
            self.send_response(200)
            self.send_header("content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastrar_atividade.html'), 'r', encoding='utf-8') as file:
                content = file.read()

            self.wfile.write(content.encode('utf-8'))
            
            return
        
        elif self.path == '/cadastro_atividade_failed':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastrar_atividade.html'), 'r', encoding='utf-8') as login_file:
                content = login_file.read()
               
            print("algo deu errado")
           
            # Envia o conteudo modificado para o cliente
            self.wfile.write(content.encode('utf-8')) 

            return
        
        elif self.path == '/cadastro_failed':

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastrar_turma.html'), 'r', encoding='utf-8') as login_file:
                content = login_file.read()
               
            print("algo deu errado")
           
            # Envia o conteudo modificado para o cliente
            self.wfile.write(content.encode('utf-8')) 

            return

        elif self.path.startswith('/cadastro'):
            query_params = parse_qs(urlparse(self.path).query)
            login = query_params.get('login', [''])[0]
            senha = query_params.get('senha', [''])[0]
            welcome_message = f"Olá {login}, seja bem-vindo! Percebemos que você é novo por aqui. Complete o seu cadastro."
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            # Lê o conteúdo da página cadastro.html
            with open(os.path.join(os.getcwd(), 'cadastro.html'), 'r', encoding='utf-8') as cadastro_file:
                content = cadastro_file.read()
            # Substitui os marcadores de posição pelos valores correspondentes
            content = content.replace('{login}', login)
            content = content.replace('{senha}', senha)
            content = content.replace('{welcome_message}', welcome_message)
            # Envia o conteúdo modificado para o cliente
            self.wfile.write(content.encode('utf-8'))
            return  # Adicionando um return para evitar a execução do restante do código
        
        else:
            super().do_GET()

    
    def do_POST(self):
        
        if self.path == '/enviar_login':
            content_length = int(self.headers['Content-Length'])

            body = self.rfile.read(content_length).decode('utf-8')

            form_data = parse_qs(body, keep_blank_values=True)

            login = form_data.get('email', [''])[0]
            senha = form_data.get('senha', [''])[0]

            # Dados do formulario

            print("DADOS DO FORMULÁRIO")
            print("E-mail:", login)
            print("Senha:", senha)

            # Verificando se o usuário já existe

            if self.usuario_existente(login, senha):
                self.carrega_turmas_professor(login)
                # return
            
            else:
                # Verifica se o usuário já está cadastrado. Caso não esteja foi caso de login errado
                cursor = conexao.cursor()
                cursor.execute("SELECT login FROM dados_login WHERE login = %s", (login,))
                resultado = cursor.fetchone()
                
                if resultado:
                    self.send_response(302)
                    self.send_header('Location', '/login_failed')
                    self.end_headers()
                    cursor.close()
                    return
                else:
                    self.send_response(302)
                    self.send_header('Location', f'/cadastro?login={login}&senha={senha}')
                    self.end_headers()
                    cursor.close()
                    return
                
        elif self.path.startswith('/confirmar_cadastro'):
            content_length = int(self.headers['Content-Length'])

            body = self.rfile.read(content_length).decode('utf-8')

            form_data = parse_qs(body, keep_blank_values=True)

            login = form_data.get("login", [''])[0]
            senha = form_data.get("senha", [''])[0]
            nome = form_data.get("nome", [''])[0]

            self.adicionar_usuario(login, senha, nome)

            self.send_response(302)
            self.send_header("Location", "/tela_turma")
            self.end_headers()
            return

            
        elif self.path.startswith('/cadastrar_turma'):
            content_length = int(self.headers['content-length'])

            body = self.rfile.read(content_length).decode('utf-8')

            form_data = parse_qs(body, keep_blank_values = True)

            descricao = form_data.get('descricao', [''])[0]
            id_professor = form_data.get('id_professor', [''])[0]
            login = form_data.get('login', [''])[0]

            print(f"Cad_turma, dados: {descricao}, {id_professor}")

            if descricao.strip() == '':
                # Se algum campo estiver vazio, redireciona para a página de cadastro falhado
                self.send_response(302)
                self.send_header("Location", "/cadastro_failed")
                self.end_headers()
                return
            elif self.turma_existente(descricao):
                self.send_response(302)
                self.send_header("Location", "/cadastro_failed")
                self.end_headers()
                return
            else:
                # Se os campos estiverem preenchidos, adiciona a turma
                self.adicionar_turma(descricao, id_professor)
                self.carrega_turmas_professor(login)

                # self.send_response(302)
                # self.send_header("Location", "/tela_turma")
                # self.end_headers()

                # return

        elif self.path.startswith('/cadastrar_atividade'):
            content_length = int(self.headers['content-length'])

            body = self.rfile.read(content_length).decode('utf-8')

            form_data = parse_qs(body, keep_blank_values = True)

            descricao = form_data.get('descricao', [''])[0]

            print(descricao)

            if descricao.strip() == '':
                # Se algum campo estiver vazio, redireciona para a página de cadastro falhado
                self.send_response(302)
                self.send_header("Location", "/cadastro_atividade_failed")
                self.end_headers()
                return
            elif self.atividade_existente(descricao):
                self.send_response(302)
                self.send_header("Location", "/cadastro_atividade_failed")
                self.end_headers()
                return
            else:
                # Se os campos estiverem preenchidos, adiciona a turma
                self.adicionar_atividade(descricao)

                self.send_response(302)
                self.send_header("Location", "/tela_turma")
                self.end_headers()

                return
            
        else:
            super(MyHandler,self).do_POST()

endereco_ip = "0.0.0.0" 
porta = 8000
 
# Cria um servidor na porta e IP especificos
with socketserver.TCPServer((endereco_ip, porta), MyHandler) as httpd:
    print(f"Servidor iniciando em {endereco_ip}:{porta}")
    # Mantém o servidor em execução
    httpd.serve_forever()
            