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

    def adicionar_turma(self, descricao):
        cursor = conexao.cursor()

        cursor.execute("INSERT INTO turmas (descricao) VALUES (%s)", (descricao,))

        conexao.commit()

        cursor.close()

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

        elif self.path.startswith('/tela_professor'):
            print("entrou tela professor")
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'tela_professor.html'), 'r', encoding='utf-8') as file:
                content = file.read()

            self.wfile.write(content.encode('utf-8'))
            
            return
        
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
                self.send_response(302)
                self.send_header('Location', '/tela_professor')
                self.end_headers()

                return
            
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
            self.send_header("Location", "/tela_professor")
            self.end_headers()
            return

            
        elif self.path.startswith('/cadastrar_turma'):
            content_length = int(self.headers['content-length'])

            body = self.rfile.read(content_length).decode('utf-8')

            form_data = parse_qs(body, keep_blank_values = True)

            descricao = form_data.get('descricao', [''])[0]

            print(descricao)

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
                self.adicionar_turma(descricao)

                self.send_response(302)
                self.send_header("Location", "/tela_professor")
                self.end_headers()

                return

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
                self.send_header("Location", "/tela_professor")
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
            