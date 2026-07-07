# PROJETO-GEFIN
GEFIN é um Sistema WEB para gestão financeira desenvolvido pela equipe da HorizonSolutions para a empresa junior Focus Consultoria, em seu processo seletivo de 2026.1. O intuito do sistema é centralizar o controle de transações, fluxo de caixa, dashboards e relatórios financeiros.

A plataforma permite a importação de extratos bancários(CSV) com estruturas diferentes, categorização de movimentações, geração de relatórios e visualização de indicadores financeiros em dashboards interativos.

 ## Tecnologias utilizadas:
 - Python
 - Supabase
 - Dash
 - Flask
 - Pandas
 - E diversas bibliotecas no requirements.txt

## Manual do usuário:
Instalação
1. Clone o repositório:
   git clone https://github.com/mariaffp/projeto-gefin
   cd projeto-gefin
2. Crie e ative o ambiente virtual:
   python3 -m venv venv OU python -m venv venv
   source venv/bin/activate  (para Linux/Mac) OU venv\Scripts\activate  (para Windows)
3. Instale as dependências:
   pip install -r requirements.txt
4. Configure o arquivo .env na raiz do projeto
5. Execute a aplicação python app.py
6. Acesse no navegador: http://localhost:8050
7. Para acesso no Mobile, seguir o mesmo padrão mas com o IP da sua rede(estará no terminal)

 ## Features
 - Gerenciamento de usuários.
 - Níveis entre perfis de acesso.
 - Login com Google.
 - Edição de Perfil.
 - Importação de extratos em .csv.
 - Exportação de Relatórios em .pdf ou .csv.
 - Criação de Transações automáticas com base na importação.
 - Criação de Transações manuais.
 - Verificação de duplicatas.
 - Dashboard Interativo.
 - Verificação de Logs do Sistema.

## Segurança e Controle de Acesso

O sistema possui dois níveis de proteção de rota:

1. **Nível Flask (`before_request` em app.py)**: intercepta toda 
   requisição antes de o Dash processar a página, bloqueando 
   acesso direto via URL a rotas restritas (ex: /admin) para 
   usuários sem permissão. Evita que o conteúdo da página chegue 
   a ser enviado ao navegador de quem não deveria vê-lo.

2. **Nível Dash (callback verificar_autenticacao)**: cuida da 
   navegação interna do site (navbar, redirecionamentos ao clicar 
   em links) e da experiência visual (esconde/mostra componentes 
   conforme o perfil do usuário: NORMAL, FINANCEIRO, ADMIN).

## Perfis e permissões:
- NORMAL: acesso básico
- FINANCEIRO: acesso adicional a /transacoes, /importacao
- ADMIN: acesso adicional a /admin, /admin/cadastro, /admin/usuarios


## Equipe:
 - Victor Iorio (https://github.com/vicode360)
 - Maria Fernanda (https://github.com/mariaffp)
 - João Rocha (https://github.com/Jovigabriel)
 - Leonardo Valladão (https://github.com/Leo-dk574)
 

