jelastic python
===============

Essa semana me foi dado a tarefa de testar o suporte a python no
Jelastic da locaweb. Nada muito sofisticado, apenas criar uma
aplicação web e relatar a experiência. Será bem interessante pois é o
meu primeiro contato com o Jelastic.

Para quem ainda não conhece, o Jelastic é um PaaS (do inglês
*Plataform As A Service*) que permite criar e gerenciar os serviços
necessários para publicar seus projetos Php, Java, Ruby e agora
Python. Além da aplicação em si, também é possível gerenciar bancos
dados, caches e balanceadores de carga. Tudo isso com alguns cliques
de botão. Propaganda a parte, vamos ao projeto.

Minha ideia foi criar uma *API REST* para o famoso e antigo jogo da
velha. É um jogo com regras simples que dispensam comentários, mas
caso alguém tenha esquecido de como funciona o artigo da Wikipedia [1]
é uma boa referência.

Vou começar criando um projeto no github [2]. Não é necessário visto
que existem outros métodos de publicação mas simplifica
consideravelmente todo o processo. Todo o código deste artigo está
publicado neste repositório e pode ser usado como referência:

    $ git clone https://github.com/dgvncsz0f/tic-tac-toe.git

Neste projeto específico vou usar *flask*, que é um *framework* leve
para criar serviços HTTP. Vou deixá-lo no repositório, tornando-o
auto-contido, ou seja, o projeto já contém todas as dependências que
necessita para ser executado:

    $ pip install --target vendor flask
    $ pip install --target vendor redis

Feito isso é hora de criar a aplicação. Agora vamos apenas definir o
esqueleto, sem adicionar nenhuma funcionalidade:

    # -- application.py --
     
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "vendor"))
     
    from flask import Flask
     
    application = Flask(__name__)
     
    @application.route("/")
    def root ():
        return "okie dokie", "text/plain; utf-8"
     
    if __name__ == "__main__":
        application.run()

É importante entender este código antes de seguir adiante. A primeira
parte adiciona o diretório *vendor* e o *HOME* do usuário no *PATH* do
python. Assim, o interpretador será capaz de encontrar o *flask*,
*redis* e o código do jogo da velha que instalamos na raiz do projeto:

    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__))))
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "vendor"))

O resto é código padrão *flask*. A partir daí, somos capazes de testar
e publicar nosso projeto. Basta executar o módulo que um servidor
*HTTP* é iniciado e começa a servir as requisições.

    $ python2 application
    * Running on http://127.0.0.1:5000/

    $ curl http://127.0.0.1:5000/
    okie dokie

Vamos fazer agora uma pequena pausa para publicar este código no
Jelastic. Em primeiro lugar criamos o ambiente seguido pelo projeto. O
ambiente permite o usuário escolher a versão do python que se deseja
usar (neste caso 2.7) bem como os serviços associados (como o Redis) e
o projeto determina como o código é publicado. O Jelastic é capaz de
obter o código a partir do github, instalando eventuais atualizações
automaticamente, o que é bem conveniente. Este foi o motivo pelo qual
escolhemos usar o github no início.

    [[ screenshot ]]

Tudo muito simples e rápido até agora e já temos o ambiente necessário
para publicar o jogo: um container com suporte a especificação *wsgi*
do python e um redis. Feito isso, o seguinte comando não deve retornar
nenhum erro:

    $ curl http://env-9190458.jelasticlw.com.br/
    okie dokie

Retomando ao código, o módulo mais importante é o
`tictactoe.game`. Este módulo contém o estado do jogo e métodos que
permitem modificar ou verificar o estado atual.

O estado do jogo é mantido como um `array` de 9 posições. Ao longo do
tempo, cada item desta estrutura pode assumir três posições: `'x'`,
`'o`' ou `None` que significam respectivamente jogador 1, jogador 2 ou
posição em aberto. Inicialmente todos os valores são `None`:

    # -- tictactoe/game.py --

    def __init__ (self, state=None):
        if state is None:
            state = [None for _ in range(9)]
        self.state = state
    
Com isso em mãos podemos implementar um método que verifica linhas e
colunas e retorna o jogador ganhador, caso haja algum:

    # -- tictactoe/game.py --

    def check_rows_n_cols_ (self):
        for i in range(3):
            j = i * 3
            data = set(self.state[j : j + 3])
            if self.has_winner_(data):
                return data.pop()

            data = set([self.state[i], self.state[3 + i], self.state[6 + i]])
            if self.has_winner_(data):
                return data.pop()

Analogamente, a seguinte função verifica se há algum ganhador em
alguma das duas diagonais:

    # -- tictactoe/game.py --

    def check_diagonals_ (self):
        data = set([self.state[0], self.state[4], self.state[8]])
        if self.has_winner_(data):
            return data.pop()

        data = set([self.state[2], self.state[4], self.state[6]])
        if self.has_winner_(data):
            return data.pop()

Ficou faltando o método auxiliar `has_winner_`, descrito a seguir:

    # -- tictactoe/game.py --

    def has_winner_ (self, s):
        return len(s) == 1 and s != set([None])

Outro módulo bem importante é o `tictactoe.db` que persiste os
jogos. Além disso, é um bom exemplo de como definir e usar um arquivo
de configuração no Jelastic. No momento que criamos a instância de
Redis este foi configurado automaticamente. Portanto, precisamos
injetar essas informações no código, isto é, endereço IP, porta e
senha, de alguma maneira. Para tanto, podemos acessar nossa instância
e configurar essas informações ao invés de deixá-las disponíveis no
repositório git:

    $ ssh 10207@gate.jelasticlw.com.br -p 3022
    Please select the required environment available for dgvncsz0f@gmail.com
       0. Quit
       1. Refresh
       2. env-9190458.jelasticlw.com.br                               Running
     
    Enter [0-2]: 2

    Please select the required container provisioned for the 'env-9190458.jelasticlw.com.br' environment.
          Node name                               nodeid    LAN IP
       0. Back
       1. Refresh
       2. Apache-2.2                              31402    10.70.9.150
       3. Redis-2.6                               31424    10.70.11.237
     
    Enter [0-3]: 2

    $ cat ~/etc/tictactoe-config.json 
    {"REDIS_HOST": "redis-env-9190458.jelasticlw.com.br",
     "REDIS_POST": 6379,
     "REDIS_DB": 0,
     "REDIS_PASS": "..."
    }

Você pode configurar esse arquivo de muitas maneiras diferentes. O
mais importante é não deixar essas informação visível no seu
repositório de código. E como podemos ler essa informação? Muito
simples:

    # -- tictactoe/db.py --

    def read_env ():
        try:
            with open(os.path.expanduser("~/etc/tictactoe-config.json"), "r") as fh:
                return json.loads(fh.read(1024))
        except IOError:
            return {}

A função acima tenta ler um arquivo de configuração e caso contrário
retorna um dicionário vazio. Desta forma, podemos usar o mesmo código
no nosso ambiente de desenvolvimento ou nas instâncias do Jelastic:

    # -- tictactoe/db.py --
    
    def instance ():
        env = read_env()
        return redis.Redis(db = env.get("REDIS_DB", 0),
                           host = env.get("REDIS_HOST", "127.0.0.1"),
                           port = env.get("REDIS_POST", 6379),
                           password = env.get("REDIS_PASS"))

É chegada a hora de implementar a *API REST*. Vamos definir 4
recursos, detalhados a seguir:

    * /new: registra um novo jogo;
    
    * /play/<game-id>: executa uma jogada. O próprio servidor seleciona e
      alterna o jogador automáticamente;

    * /show/<game-id>: mostra o estado de um determinado;

    * /show/<game-id>/winner: mostra o ganhador do um determinado jogo;

Não vou incluir todo o código aqui, mas a título de exemplo, veja a
função do recurso */new*:

    # -- application.py --
    
    @application.route("/new", methods=["POST"])
    def new ():
        key = db.create(db.instance())
        return(key, 201, {"content-type": "text/plain; charset=utf8"})

Nenhuma surpresa aqui, apenas código flask. Com tudo pronto e o
projeto publicado, podemos finalmente testar nosso joguinho:

    $ game=$(curl -s -X POST http://env-9190458.jelasticlw.com.br/new); echo $game
    06d640c7-4954-4612-9220-d910ac8e7614

    $ curl -d row=0 -d col=1 http://env-9190458.jelasticlw.com.br/play/$game
       | x |  
    ---+---+---
       |   |  
    ---+---+---
       |   |  

    $ curl -d row=2 -d col=0 http://env-9190458.jelasticlw.com.br/play/$game
       | x |  
    ---+---+---
       |   |  
    ---+---+---
     o |   |  

E isso conclui nossa pequena jornada exploratória do suporte a python
no Jelastic.

Considerações Finais
====================

O objetivo aqui foi mostrar o Jelastic e como ele pode ser usado com
projetos python. Embora eu trabalhe na Locaweb, esta foi minha
primeira experiência com a plataforma e honestamente fiquei bem
satisfeito. É relativamente simples provisionar os recursos
necessários para a maioria das aplicações.

Um aspecto importante que foi negligenciado é a capacidade de
dimensionar o ambiente. Isso significa que você pode começar pequeno,
contratando poucas instâncias e aumentando a capacidade conforme a
necessidade ou um teto de custo estabelecido.

Outro ponto positivo foi a possibilidade de usar python sem
praticamente nenhuma grande modificação: nesta foi apenas necessário
modificar o `sys.path` do python. Isto é muito importante, pois
significa a possibilidade de migrar qualquer projeto python para
dentro ou fora Jelastic de maneira relativamente simples, dando muita
liberdade de escolha.

Claro que houve alguns pequenos problemas, que certamente serão
solucionados rapidamente. Pessoalmente achei que a documentação deixou
um pouco a desejar e não fui capaz de usar python3.3 ou python3.4. Mas
no geral considero o saldo bem positivo!

Por fim, o código encontra-se no meu github, caso haja algum
interesse.
