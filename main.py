import os
import hashlib
import socketserver
from http.server import SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

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
                print("Hhahaahahhahhahahhahahhahaahahahhahaa")

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
        
        elif self.path == '/cadastro_failed':

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastrar_turma.html'), 'r', encoding='utf-8') as login_file:
                content = login_file.read()
               
            print("algo deu errado")
           
            # Envia o conteudo modificado para o cliente
            self.wfile.write(content.encode('utf-8')) 
        
        else:
            super().do_GET()

    def usuario_existente(self, login, senha):
        if login == 'admin' and senha == 'admin@senai':
            return login
        
        return False
    
    def turma_existente(self, nome, professor):
        # Verificando se a turma já existe
        with open('dados_turma.txt', 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    stored_nome, stored_professor = line.strip().split(';')

                    if nome == stored_nome or professor == stored_professor:
                        return True
        return False
    
    def atividade_existente(self, descricao, turma):
        # Verificando se a turma já existe
        with open('dados_atividade.txt', 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    stored_descricao, stored_turma = line.strip().split(';')

                    if descricao == stored_descricao or stored_turma == turma:
                        return True
        return False
                    
                
 
    def adicionar_turma(self, nome, professor):
        with open('dados_turma.txt', 'a', encoding='UTF-8') as file:
            file.write(f'{nome};{professor}\n')

    def adicionar_atividade(self, desc, turma):
        with open('dados_atividade.txt', 'a', encoding='UTF-8') as file:
            file.write(f'{desc};{turma}\n')
    
    def do_POST(self):
        
        if self.path == '/enviar_login':
            content_length = int(self.headers['content-length'])

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
                self.send_response(302)
                self.send_header('Location', '/login_failed')
                self.end_headers()
                return  
            
        elif self.path.startswith('/cadastrar_turma'):
            content_length = int(self.headers['content-length'])

            body = self.rfile.read(content_length).decode('utf-8')

            form_data = parse_qs(body, keep_blank_values = True)

            nome_turma = form_data.get('nome-turma', [''])[0]
            professor = form_data.get('professor', [''])[0]

            if nome_turma.strip() == '' or professor.strip() == '':
                # Se algum campo estiver vazio, redireciona para a página de cadastro falhado
                self.send_response(302)
                self.send_header("Location", "/cadastro_failed")
                self.end_headers()
                return
            
            elif self.turma_existente(nome_turma, professor) == True:
                self.send_response(302)
                self.send_header("Location", "/cadastro_failed")
                self.end_headers()
                return
            else:
                # Se os campos estiverem preenchidos, adiciona a turma
                self.adicionar_turma(nome_turma, professor)

                self.send_response(302)
                self.send_header("Location", "/tela_professor")
                self.end_headers()

        elif self.path.startswith('/cadastrar_atividade'):
            content_length = int(self.headers['content-length'])

            body = self.rfile.read(content_length).decode('utf-8')

            form_data = parse_qs(body, keep_blank_values=True)

            desc_atividade = form_data.get('desc-atividade', [''])[0]
            turma = form_data.get('nome-turma', [''])[0]

            if desc_atividade.strip() == '' or turma.strip() == '':
                self.send_response(302)
                self.send_header("Location", "/cadastro_atividade_failed")
                self.end_headers()
                return
            
            elif self.atividade_existente(desc_atividade, turma) == True:
                self.send_response(302)
                self.send_header("Location", "/cadastro_atividade_failed")
                self.end_headers()
                print("Turma não existente!")
                return
            
            else:

                self.adicionar_atividade(desc_atividade, turma)

                self.send_response(302)
                self.send_header("Location", "/tela_professor")
                self.end_headers()
            
        else:
            super(MyHandler,self).do_POST()

endereco_ip = "0.0.0.0"
porta = 8000
 
# Cria um servidor na porta e IP especificos
with socketserver.TCPServer((endereco_ip, porta), MyHandler) as httpd:
    print(f"Servidor iniciando em {endereco_ip}:{porta}")
    # Mantém o servidor em execução
    httpd.serve_forever()
            