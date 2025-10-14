import random
import pygame
import os
import math
import json
import sys

pygame.init()

largura, altura = 400, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Nave vs Meteoros")
clock = pygame.time.Clock()


# == SISTEMA FLEXÍVEL DE CARREGAMENTO DE IMAGENS ==
def encontrar_arquivos_imagem():
    """Encontra arquivos de imagem em vários locais possíveis"""
    locais_possiveis = [
        os.path.dirname(__file__),  # Diretório atual do script
        os.path.join(os.path.dirname(__file__), "imagens"),
        os.path.join(os.path.dirname(__file__), "assets"),
        os.path.join(os.path.dirname(__file__), "sprites"),
        r"C:\Users\aluno\PyCharm\Cotacao-Kivy\corrida",  # Caminho original
    ]

    for local in locais_possiveis:
        if os.path.exists(local):
            arquivos = [f for f in os.listdir(local) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            if arquivos:
                print(f"Imagens encontradas em: {local}")
                return local, arquivos

    print("Nenhuma imagem encontrada. Usando sprites gerados.")
    return None, []


caminho_imagens, arquivos_disponiveis = encontrar_arquivos_imagem()
print("Arquivos encontrados:", arquivos_disponiveis)


# == SISTEMA DE SHADERS E EFEITOS VISUAIS ==
class EfeitosVisuais:
    def __init__(self):
        self.brilho_buffer = pygame.Surface((largura, altura))
        self.brilho_buffer.set_alpha(100)
        self.particulas_brilho = []

    def criar_brilho(self, x, y, cor, raio=50, duracao=1000):
        self.particulas_brilho.append({
            'x': x, 'y': y, 'cor': cor, 'raio': raio,
            'tempo_inicio': pygame.time.get_ticks(),
            'duracao': duracao
        })

    def atualizar_brilhos(self):
        agora = pygame.time.get_ticks()
        self.particulas_brilho = [brilho for brilho in self.particulas_brilho
                                  if agora - brilho['tempo_inicio'] < brilho['duracao']]

    def desenhar_brilhos(self, surface):
        for brilho in self.particulas_brilho:
            progresso = (pygame.time.get_ticks() - brilho['tempo_inicio']) / brilho['duracao']
            alpha = int(255 * (1 - progresso))
            raio_atual = int(brilho['raio'] * (1 - progresso))

            # CORREÇÃO: Garantir que o raio seja pelo menos 1
            raio_atual = max(1, raio_atual)

            surf_brilho = pygame.Surface((raio_atual * 2, raio_atual * 2), pygame.SRCALPHA)
            for i in range(3):
                cor_brilho = (*brilho['cor'], alpha // (i + 1))
                pygame.draw.circle(surf_brilho, cor_brilho,
                                   (raio_atual, raio_atual),
                                   raio_atual - i * 5)
            surface.blit(surf_brilho, (brilho['x'] - raio_atual, brilho['y'] - raio_atual))


efeitos = EfeitosVisuais()


# == SISTEMA DE PARTÍCULAS AVANÇADO ==
class ParticulaAvancada:
    def __init__(self, x, y, cor, velocidade_x=0, velocidade_y=0,
                 vida_util=1000, tamanho=3, tipo="normal", gravidade=0):
        self.x = x
        self.y = y
        self.cor = cor
        self.velocidade_x = velocidade_x
        self.velocidade_y = velocidade_y
        self.vida_util = vida_util
        self.tempo_inicio = pygame.time.get_ticks()
        self.tamanho = tamanho
        self.tamanho_original = tamanho
        self.tipo = tipo
        self.gravidade = gravidade
        self.rotacao = random.uniform(0, 360)
        self.velocidade_rotacao = random.uniform(-5, 5)

    def atualizar(self):
        tempo_atual = pygame.time.get_ticks()
        tempo_decorrido = tempo_atual - self.tempo_inicio

        if tempo_decorrido > self.vida_util:
            return False

        # Movimento com física
        self.x += self.velocidade_x
        self.y += self.velocidade_y
        self.velocidade_y += self.gravidade

        # Rotação para alguns tipos
        if self.tipo in ["estrela", "cristal"]:
            self.rotacao += self.velocidade_rotacao

        # Efeitos especiais por tipo
        progresso = tempo_decorrido / self.vida_util

        if self.tipo == "fumaca":
            self.tamanho = self.tamanho_original * (1 + progresso * 0.5)
        elif self.tipo == "faisca":
            self.tamanho = max(1, self.tamanho_original * (1 - progresso * 2))
        else:
            self.tamanho = max(1, self.tamanho_original * (1 - progresso))

        return True

    def desenhar(self, surface):
        tempo_decorrido = pygame.time.get_ticks() - self.tempo_inicio
        progresso = tempo_decorrido / self.vida_util
        alpha = int(255 * (1 - progresso))

        if alpha <= 0:
            return

        cor_com_alpha = (*self.cor, alpha)

        if self.tipo == "estrela":
            # Partícula em forma de estrela
            # CORREÇÃO: Garantir tamanho mínimo
            tamanho_efetivo = max(1, self.tamanho)
            surf = pygame.Surface((tamanho_efetivo * 3, tamanho_efetivo * 3), pygame.SRCALPHA)
            pontos = []
            for i in range(5):
                angulo = math.radians(self.rotacao + i * 72)
                raio_externo = tamanho_efetivo
                raio_interno = tamanho_efetivo * 0.4

                # Ponta externa
                x_ext = tamanho_efetivo * 1.5 + math.cos(angulo) * raio_externo
                y_ext = tamanho_efetivo * 1.5 + math.sin(angulo) * raio_externo
                pontos.append((x_ext, y_ext))

                # Ponta interna
                x_int = tamanho_efetivo * 1.5 + math.cos(angulo + math.radians(36)) * raio_interno
                y_int = tamanho_efetivo * 1.5 + math.sin(angulo + math.radians(36)) * raio_interno
                pontos.append((x_int, y_int))

            pygame.draw.polygon(surf, cor_com_alpha, pontos)
            surface.blit(surf, (int(self.x - tamanho_efetivo * 1.5), int(self.y - tamanho_efetivo * 1.5)))

        elif self.tipo == "cristal":
            # Partícula em forma de cristal
            # CORREÇÃO: Garantir tamanho mínimo
            tamanho_efetivo = max(1, self.tamanho)
            surf = pygame.Surface((tamanho_efetivo * 2, tamanho_efetivo * 2), pygame.SRCALPHA)
            pontos = [
                (tamanho_efetivo, 0),
                (tamanho_efetivo * 2, tamanho_efetivo),
                (tamanho_efetivo, tamanho_efetivo * 2),
                (0, tamanho_efetivo)
            ]
            # Rotacionar pontos
            pontos_rotacionados = []
            for px, py in pontos:
                px -= tamanho_efetivo
                py -= tamanho_efetivo
                px_rot = px * math.cos(math.radians(self.rotacao)) - py * math.sin(math.radians(self.rotacao))
                py_rot = px * math.sin(math.radians(self.rotacao)) + py * math.cos(math.radians(self.rotacao))
                pontos_rotacionados.append((px_rot + tamanho_efetivo, py_rot + tamanho_efetivo))

            pygame.draw.polygon(surf, cor_com_alpha, pontos_rotacionados)
            surface.blit(surf, (int(self.x - tamanho_efetivo), int(self.y - tamanho_efetivo)))

        else:
            # Partícula circular normal
            # CORREÇÃO: Garantir tamanho mínimo
            tamanho_efetivo = max(1, self.tamanho)
            surf = pygame.Surface((tamanho_efetivo * 2, tamanho_efetivo * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, cor_com_alpha, (tamanho_efetivo, tamanho_efetivo), tamanho_efetivo)
            surface.blit(surf, (int(self.x - tamanho_efetivo), int(self.y - tamanho_efetivo)))


# == FUNÇÕES AVANÇADAS DE PARTÍCULAS ==
particulas = []


def criar_particulas_explosao_avancada(x, y, quantidade=25, cor_base=(255, 165, 0)):
    """Cria uma explosão com partículas variadas"""
    if len(particulas) > 800:
        quantidade = min(quantidade, 10)

    # Brilho central
    efeitos.criar_brilho(x, y, cor_base, 80, 1500)

    for _ in range(quantidade):
        angulo = random.uniform(0, 2 * math.pi)
        velocidade = random.uniform(2, 8)
        vida_util = random.randint(400, 1200)
        tamanho = random.randint(2, 6)

        # Escolher tipo de partícula
        tipo = random.choice(["normal", "fumaca", "faisca", "estrela"])

        # Variação de cor
        variacao = random.randint(-40, 40)
        cor = (
            min(255, max(50, cor_base[0] + variacao)),
            min(255, max(50, cor_base[1] + variacao)),
            min(255, max(50, cor_base[2] + variacao))
        )

        particulas.append(ParticulaAvancada(
            x, y, cor,
            math.cos(angulo) * velocidade,
            math.sin(angulo) * velocidade,
            vida_util, tamanho, tipo,
            gravidade=random.uniform(0.01, 0.05) if tipo == "fumaca" else 0
        ))


def criar_particulas_estrelas_avancadas():
    """Cria estrelas cadentes com efeitos especiais"""
    for _ in range(3):
        if random.random() < 0.2 and len(particulas) < 700:
            x = random.randint(0, largura)
            velocidade = random.uniform(0.8, 3)
            tamanho = random.uniform(1, 3)
            brilho = random.randint(150, 255)

            # Criar rastro
            for i in range(3):
                particulas.append(ParticulaAvancada(
                    x + random.randint(-10, 10),
                    -5 - i * 5,
                    (brilho, brilho, brilho),
                    0, velocidade + i * 0.5,
                    1000, tamanho * (1 - i * 0.3),
                    "estrela"
                ))


def criar_particulas_propulsao_avancada():
    """Partículas de propulsão da nave com efeitos especiais"""
    if not game_over and len(particulas) < 750:
        for i in range(4):
            offset_x = random.randint(-18, 18)
            cor_base = (random.randint(150, 255), random.randint(50, 150), 0)

            # Partículas principais
            particulas.append(ParticulaAvancada(
                jogador.centerx + offset_x,
                jogador.bottom,
                cor_base,
                random.uniform(-1, 1), random.uniform(2, 5),
                600, random.randint(3, 6), "fumaca", 0.02
            ))

            # Faíscas
            if random.random() < 0.3:
                particulas.append(ParticulaAvancada(
                    jogador.centerx + offset_x,
                    jogador.bottom,
                    (255, 255, 200),
                    random.uniform(-2, 2), random.uniform(3, 6),
                    300, random.randint(1, 3), "faisca"
                ))


def criar_particulas_escudo_avancado():
    """Partículas para escudo com efeito energético"""
    if escudo_ativo and len(particulas) < 800:
        for i in range(3):
            angulo = random.uniform(0, 2 * math.pi)
            distancia = 35 + random.uniform(-8, 8)
            x = jogador.centerx + math.cos(angulo) * distancia
            y = jogador.centery + math.sin(angulo) * distancia

            # Partículas energéticas
            particulas.append(ParticulaAvancada(
                x, y, (100, 200, 255),
                random.uniform(-1, 1), random.uniform(-1, 1),
                1000, random.randint(2, 4), "cristal"
            ))


# == SISTEMA DE FUNDO DINÂMICO ==
class FundoEstelar:
    def __init__(self):
        self.estrelas = []
        self.nevoas = []
        self.inicializar_estrelas()
        self.inicializar_nevoas()

    def inicializar_estrelas(self):
        for _ in range(100):
            self.estrelas.append({
                'x': random.randint(0, largura),
                'y': random.randint(0, altura),
                'velocidade': random.uniform(0.1, 0.5),
                'tamanho': random.uniform(0.5, 2),
                'brilho': random.randint(100, 255),
                'piscar_vel': random.uniform(0.01, 0.05)
            })

    def inicializar_nevoas(self):
        for _ in range(5):
            self.nevoas.append({
                'x': random.randint(0, largura),
                'y': random.randint(0, altura),
                'velocidade': random.uniform(0.05, 0.2),
                'tamanho': random.randint(50, 150),
                'alpha': random.randint(10, 30)
            })

    def atualizar(self):
        tempo = pygame.time.get_ticks()

        # Atualizar estrelas
        for estrela in self.estrelas:
            estrela['y'] += estrela['velocidade']
            if estrela['y'] > altura:
                estrela['y'] = 0
                estrela['x'] = random.randint(0, largura)

            # Efeito de piscar
            estrela['brilho'] = 100 + int(155 * abs(math.sin(tempo * estrela['piscar_vel'])))

        # Atualizar névoas
        for nevoa in self.nevoas:
            nevoa['x'] += nevoa['velocidade']
            if nevoa['x'] > largura + nevoa['tamanho']:
                nevoa['x'] = -nevoa['tamanho']
                nevoa['y'] = random.randint(0, altura)

    def desenhar(self, surface):
        # Desenhar névoas
        for nevoa in self.nevoas:
            surf_nevoa = pygame.Surface((nevoa['tamanho'], nevoa['tamanho']), pygame.SRCALPHA)
            pygame.draw.circle(surf_nevoa, (50, 50, 100, nevoa['alpha']),
                               (nevoa['tamanho'] // 2, nevoa['tamanho'] // 2),
                               nevoa['tamanho'] // 2)
            surface.blit(surf_nevoa, (nevoa['x'], nevoa['y']))

        # Desenhar estrelas
        for estrela in self.estrelas:
            cor = (estrela['brilho'], estrela['brilho'], estrela['brilho'])
            pygame.draw.circle(surface, cor, (int(estrela['x']), int(estrela['y'])), estrela['tamanho'])


fundo_estelar = FundoEstelar()


# == CARREGAMENTO DE IMAGENS COM FALLBACK ==
def carregar_imagem_ou_criar(nome_arquivo, escala, cor_fallback=None):
    """Carrega imagem ou cria uma fallback"""
    if caminho_imagens:
        caminho_completo = os.path.join(caminho_imagens, nome_arquivo)
        if os.path.exists(caminho_completo):
            try:
                img = pygame.image.load(caminho_completo)
                return pygame.transform.scale(img, escala)
            except:
                print(f"Erro ao carregar: {nome_arquivo}")

    # Criar fallback
    surf = pygame.Surface(escala)
    if cor_fallback:
        surf.fill(cor_fallback)
    else:
        # Gradiente colorido baseado no nome
        cores = {
            'nave': (100, 150, 255),
            'meteoro': (150, 100, 50),
            'projetil': (255, 255, 100),
            'boss': (255, 50, 50),
            'coracao': (255, 100, 100),
            'portal': (100, 255, 200)
        }

        for chave, cor in cores.items():
            if chave in nome_arquivo.lower():
                surf.fill(cor)
                break
        else:
            surf.fill((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))

    # Adicionar detalhes básicos
    pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 2)
    fonte_fallback = pygame.font.Font(None, 20)
    texto = fonte_fallback.render(nome_arquivo[:3], True, (255, 255, 255))
    surf.blit(texto, (5, 5))

    return surf


# == CARREGAR TODAS AS IMAGENS ==
# Naves
naves_imagens = []
naves_arquivos = ["nave_azulroxo3.gif", "nave_laranja3.gif", "nave_rosa2.gif",
                  "nave_verde3.gif", "nave_vermelho1.gif", "nave_vermelho3.gif"]

for nave_arquivo in naves_arquivos:
    img = carregar_imagem_ou_criar(nave_arquivo, (40, 40), (100, 150, 255))
    naves_imagens.append(img)

# Outros sprites
meteoro_img = carregar_imagem_ou_criar("meteoro.gif", (60, 60), (150, 100, 50))
meteoro_grande_img = carregar_imagem_ou_criar("meteoro.gif", (80, 80), (150, 100, 50))
projetil_img = carregar_imagem_ou_criar("projetil_base.gif", (15, 25), (255, 255, 100))
projetil_boss_img = carregar_imagem_ou_criar("projetil_boss.gif", (15, 25), (255, 100, 100))
boss_img = carregar_imagem_ou_criar("nave_boss.gif", (70, 70), (255, 50, 50))
coracao_img = carregar_imagem_ou_criar("coracao.png", (30, 30), (255, 100, 100))
portal_img = carregar_imagem_ou_criar("portal.gif", (60, 60), (100, 255, 200))

# == SISTEMA DE PROGRESSÃO E DESBLOQUEIO ==
fonte = pygame.font.Font(None, 36)
fonte_pequena = pygame.font.Font(None, 24)
pontuacao = 0
pontuacao_para_proxima_nave = 0
naves_desbloqueadas = [True] + [False] * 5
pontuacao_necessaria_por_nave = [0, 2000, 3000, 4000, 5000, 6000]
nave_selecionada = 0

# == SISTEMA DE TEMPO E NÍVEIS ==
tempo_inicio = pygame.time.get_ticks()
tempo_atual = 0
nivel = 1
velocidade_base = 3
vida_jogador = 3
max_vida = 5

# == SISTEMA DE MUNIÇÃO E RECARGA ==
municao_maxima = 10
municao_atual = municao_maxima
ultimo_recarga = pygame.time.get_ticks()
intervalo_recarga = 10000
recarregando = False
tempo_inicio_recarga = 0

# == SISTEMA DE LAZER/KAMEHAMEHA ==
lazer_ativado = False
lazer_tempo_inicio = 0
lazer_duracao = 2000
lazer_cooldown = 10000
ultimo_lazer = 0
lazer_carregando = False
lazer_carregamento_tempo = 0

# == SISTEMA DE HABILIDADES ESPECIAIS ==
habilidade_cooldown = [0, 0, 0, 0, 0, 0]
habilidade_duracao = [0, 0, 0, 0, 0, 0]
habilidade_ativa = [False, False, False, False, False, False]
meteoros_congelados = []
escudo_ativo = False
escudo_tempo_fim = 0
tiro_triplo_ativo = False
tiro_triplo_contador = 0
velocidade_dupla_ativa = False
velocidade_dupla_tempo_fim = 0

# == SISTEMA DE BOSS MÚLTIPLO ==
bosses = []
boss_ativo = False
ultimo_boss_derrotado = 0

# == SISTEMA DE POWER-UPS ==
powerups = []
powerup_tipos = ['municao', 'velocidade', 'escudo', 'lazer']
ultimo_powerup = pygame.time.get_ticks()
intervalo_powerups = 15000

# == SISTEMA DE SALVAMENTO ==
progresso_salvo = None

# == VARIÁVEIS GLOBAIS DO JOGO ==
jogador = pygame.Rect(180, 500, 40, 40)
velocidade = 5
meteoros = []
projeteis = []
projeteis_boss = []
explosoes = []
coracoes = []
portais = []
ultimo_coracao = pygame.time.get_ticks()
intervalo_coracoes = 15000
ultimo_portal = pygame.time.get_ticks()
intervalo_portais = 30000


# == CLASSE BOSS ==
class Boss:
    def __init__(self, nivel_boss, x, usar_lazer=False):
        self.nivel_boss = nivel_boss
        self.usar_lazer = usar_lazer
        self.vida_maxima = 80 + (nivel_boss // 5) * 40
        self.vida = self.vida_maxima
        self.largura = 70
        self.altura = 70
        self.rect = pygame.Rect(x, 50, self.largura, self.altura)
        self.velocidade = 2 + (nivel_boss // 5) * 0.5
        self.ultimo_tiro = pygame.time.get_ticks()
        self.intervalo_tiros = max(500, 1000 - (nivel_boss // 5) * 100)
        self.tiros_simultaneos = 1 + (nivel_boss // 5)
        self.lazer_ativado = False
        self.lazer_tempo_inicio = 0
        self.lazer_duracao = 1500
        self.ultimo_lazer = 0
        self.lazer_cooldown = 8000

    def atualizar(self, jogador_rect):
        if self.rect.centerx < jogador_rect.centerx:
            self.rect.x += min(self.velocidade, jogador_rect.centerx - self.rect.centerx)
        elif self.rect.centerx > jogador_rect.centerx:
            self.rect.x -= min(self.velocidade, self.rect.centerx - jogador_rect.centerx)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > largura:
            self.rect.right = largura

    def pode_atirar(self):
        agora = pygame.time.get_ticks()
        return agora - self.ultimo_tiro > self.intervalo_tiros

    def pode_usar_lazer(self):
        if not self.usar_lazer:
            return False
        agora = pygame.time.get_ticks()
        return agora - self.ultimo_lazer > self.lazer_cooldown

    def ativar_lazer(self):
        if self.pode_usar_lazer():
            self.lazer_ativado = True
            self.lazer_tempo_inicio = pygame.time.get_ticks()
            self.ultimo_lazer = pygame.time.get_ticks()
            return True
        return False

    def atirar(self, jogador_rect):
        self.ultimo_tiro = pygame.time.get_ticks()
        projeteis = []

        if self.tiros_simultaneos == 1:
            direcao_x = jogador_rect.centerx - self.rect.centerx
            direcao_y = jogador_rect.centery - self.rect.centery
            angulo = math.atan2(direcao_y, direcao_x)

            x = self.rect.centerx - 5
            y = self.rect.bottom
            projeteis.append({
                "rect": pygame.Rect(x, y, 10, 20),
                "velocidade_x": math.cos(angulo) * 5,
                "velocidade_y": math.sin(angulo) * 5
            })
        else:
            for i in range(self.tiros_simultaneos):
                offset = (i - (self.tiros_simultaneos - 1) / 2) * 15

                if self.nivel_boss >= 10:
                    direcao_x = jogador_rect.centerx - (self.rect.centerx + offset)
                    direcao_y = jogador_rect.centery - self.rect.centery
                    angulo = math.atan2(direcao_y, direcao_x)

                    x = self.rect.centerx - 5 + offset
                    y = self.rect.bottom
                    projeteis.append({
                        "rect": pygame.Rect(x, y, 10, 20),
                        "velocidade_x": math.cos(angulo) * 5,
                        "velocidade_y": math.sin(angulo) * 5
                    })
                else:
                    x = self.rect.centerx - 5 + offset
                    y = self.rect.bottom
                    projeteis.append({
                        "rect": pygame.Rect(x, y, 10, 20),
                        "velocidade_x": 0,
                        "velocidade_y": 7
                    })
        return projeteis

    def levar_dano(self, dano):
        self.vida -= dano
        return self.vida <= 0

    def desenhar_barra_vida(self, surface):
        barra_largura = 80
        barra_altura = 8
        x = self.rect.centerx - barra_largura // 2
        y = self.rect.top - 15

        pygame.draw.rect(surface, (255, 0, 0), (x, y, barra_largura, barra_altura))
        vida_largura = int((self.vida / self.vida_maxima) * barra_largura)
        cor_vida = (0, 255, 0) if self.usar_lazer else (255, 255, 0)
        pygame.draw.rect(surface, cor_vida, (x, y, vida_largura, barra_altura))

    def desenhar_lazer(self, surface, jogador_rect):
        if not self.lazer_ativado:
            return False

        agora = pygame.time.get_ticks()
        tempo_decorrido = agora - self.lazer_tempo_inicio

        if tempo_decorrido > self.lazer_duracao:
            self.lazer_ativado = False
            return False

        largura_lazer = 15
        cor_lazer = (255, 0, 0)

        start_pos = (self.rect.centerx, self.rect.bottom)
        end_pos = (jogador_rect.centerx, jogador_rect.top)

        pygame.draw.line(surface, cor_lazer, start_pos, end_pos, largura_lazer)

        for i in range(3):
            cor_brilho = (255, 100 - i * 30, 100 - i * 30)
            pygame.draw.line(surface, cor_brilho, start_pos, end_pos, largura_lazer - i * 3)

        for _ in range(8):
            progresso = random.uniform(0, 1)
            x = start_pos[0] + (end_pos[0] - start_pos[0]) * progresso
            y = start_pos[1] + (end_pos[1] - start_pos[1]) * progresso
            offset_x = random.randint(-5, 5)
            offset_y = random.randint(-5, 5)
            pygame.draw.circle(surface, (255, 255, 200), (int(x) + offset_x, int(y) + offset_y), 2)

        laser_rect = pygame.Rect(
            min(start_pos[0], end_pos[0]) - largura_lazer // 2,
            min(start_pos[1], end_pos[1]) - largura_lazer // 2,
            abs(end_pos[0] - start_pos[0]) + largura_lazer,
            abs(end_pos[1] - start_pos[1]) + largura_lazer
        )

        if laser_rect.colliderect(jogador_rect):
            return True
        return False


# == SISTEMA DE SALVAMENTO ==
def salvar_progresso():
    global pontuacao, nivel, naves_desbloqueadas
    try:
        progresso = {
            'naves_desbloqueadas': naves_desbloqueadas,
            'pontuacao_maxima': pontuacao,
            'nivel_maximo': nivel,
            'ultima_pontuacao': pontuacao
        }
        with open('progresso.json', 'w') as f:
            json.dump(progresso, f)
        print("Progresso salvo!")
    except Exception as e:
        print(f"Erro ao salvar progresso: {e}")


def carregar_progresso():
    global naves_desbloqueadas
    try:
        with open('progresso.json', 'r') as f:
            dados = json.load(f)
            naves_desbloqueadas = dados.get('naves_desbloqueadas', [True] + [False] * 5)
            print("Progresso carregado com sucesso!")
            return dados
    except Exception as e:
        print(f"Erro ao carregar progresso: {e}")
        return None


# == SISTEMA DE POWER-UPS ==
def criar_powerup():
    tipo = random.choice(powerup_tipos)
    x = random.randint(30, largura - 30)
    rect = pygame.Rect(x, -30, 30, 30)

    cores = {
        'municao': (0, 255, 0),
        'velocidade': (255, 255, 0),
        'escudo': (0, 0, 255),
        'lazer': (255, 0, 255)
    }

    return {'rect': rect, 'tipo': tipo, 'cor': cores[tipo], 'ativo': True}


def aplicar_powerup(tipo):
    global municao_atual, velocidade_dupla_ativa, escudo_ativo, escudo_tempo_fim, ultimo_lazer

    efeitos = {
        'municao': {
            'mensagem': 'MUNIÇÃO RECARREGADA!',
            'cor': (0, 255, 0),
            'acao': lambda: setattr(sys.modules[__name__], 'municao_atual', municao_maxima)
        },
        'velocidade': {
            'mensagem': 'VELOCIDADE AUMENTADA!',
            'cor': (255, 255, 0),
            'acao': lambda: (setattr(sys.modules[__name__], 'velocidade_dupla_ativa', True),
                             setattr(sys.modules[__name__], 'velocidade_dupla_tempo_fim',
                                     pygame.time.get_ticks() + 5000))
        },
        'escudo': {
            'mensagem': 'ESCUDO ATIVADO!',
            'cor': (0, 0, 255),
            'acao': lambda: (setattr(sys.modules[__name__], 'escudo_ativo', True),
                             setattr(sys.modules[__name__], 'escudo_tempo_fim', pygame.time.get_ticks() + 5000))
        },
        'lazer': {
            'mensagem': 'LAZER RECARREGADO!',
            'cor': (255, 0, 255),
            'acao': lambda: setattr(sys.modules[__name__], 'ultimo_lazer', 0)
        }
    }

    if tipo in efeitos:
        efeitos[tipo]['acao']()
        criar_particulas_explosao_avancada(jogador.centerx, jogador.centery, 15, efeitos[tipo]['cor'])
        print(efeitos[tipo]['mensagem'])


def desenhar_powerups(surface):
    for powerup in powerups:
        if powerup['ativo']:
            pygame.draw.rect(surface, powerup['cor'], powerup['rect'])
            tempo = pygame.time.get_ticks()
            tamanho = 25 + int(5 * math.sin(tempo / 200))
            rect_pulsante = pygame.Rect(
                powerup['rect'].centerx - tamanho // 2,
                powerup['rect'].centery - tamanho // 2,
                tamanho, tamanho
            )
            pygame.draw.rect(surface, powerup['cor'], rect_pulsante, 2)


# == MENU PRINCIPAL ==
def mostrar_menu_principal():
    menu_ativo = True
    progresso = carregar_progresso()

    while menu_ativo:
        # Desenhar fundo do menu
        tela.fill((0, 0, 40))
        fundo_estelar.desenhar(tela)
        fundo_estelar.atualizar()

        titulo = fonte.render("NAVE vs METEOROS", True, (255, 255, 255))
        iniciar = fonte_pequena.render("Pressione ESPAÇO para iniciar", True, (200, 200, 200))

        if progresso:
            recorde = fonte_pequena.render(f"Recorde: {progresso.get('pontuacao_maxima', 0)} pontos", True,
                                           (255, 255, 0))
            tela.blit(recorde, (largura // 2 - recorde.get_width() // 2, altura // 2 + 50))

        tela.blit(titulo, (largura // 2 - titulo.get_width() // 2, altura // 3))
        tela.blit(iniciar, (largura // 2 - iniciar.get_width() // 2, altura // 2))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    return True
                if evento.key == pygame.K_ESCAPE:
                    return False

    return True


# == SISTEMA DE PROGRESSÃO ==
def verificar_desbloqueio_naves():
    global naves_desbloqueadas, pontuacao_para_proxima_nave, pontuacao

    for i in range(1, len(naves_desbloqueadas)):
        if not naves_desbloqueadas[i] and pontuacao_para_proxima_nave >= pontuacao_necessaria_por_nave[i]:
            naves_desbloqueadas[i] = True
            pontuacao_para_proxima_nave = 0
            print(f"Nave {i + 1} desbloqueada!")
            for _ in range(50):
                criar_particulas_explosao_avancada(largura // 2, altura // 2, 1, (0, 255, 255))
            return True
    return False


def trocar_nave(numero):
    global nave_selecionada
    if 0 <= numero - 1 < len(naves_imagens) and naves_desbloqueadas[numero - 1]:
        nave_selecionada = numero - 1
        print(f"Nave {numero} selecionada!")
    else:
        print(f"Nave {numero} ainda não desbloqueada!")


# == FUNÇÕES DO JOGO ==
def criar_meteoro():
    if nivel >= 5 and random.random() < 0.4:
        tamanho = 80
        velocidade_x = random.uniform(-2, 2)
        velocidade_y = velocidade_base + (nivel * 1.2)
        rotacao_speed = random.uniform(-2, 2)
        x = random.randint(0, largura - tamanho)
        rect = pygame.Rect(x, -tamanho, tamanho, tamanho)
        return {
            "rect": rect,
            "velocidade_y": velocidade_y,
            "velocidade_x": velocidade_x,
            "rotacao": 0,
            "rotacao_speed": rotacao_speed,
            "grande": True,
            "congelado": False,
            "congelado_tempo": 0
        }
    else:
        tamanho = 60
        x = random.randint(0, largura - tamanho)
        rect = pygame.Rect(x, -tamanho, tamanho, tamanho)
        velocidade_y = velocidade_base + (nivel * 1.2)
        rotacao_speed = random.uniform(-2, 2)
        return {
            "rect": rect,
            "velocidade_y": velocidade_y,
            "velocidade_x": 0,
            "rotacao": 0,
            "rotacao_speed": rotacao_speed,
            "grande": False,
            "congelado": False,
            "congelado_tempo": 0
        }


def criar_projetil():
    if municao_atual > 0 and not recarregando:
        x = jogador.centerx - 7
        y = jogador.top
        return {"rect": pygame.Rect(x, y, 15, 25), "rotacao": 0}
    return None


def criar_projeteis_triplo():
    projeteis = []
    if municao_atual > 0 and not recarregando:
        projeteis.append({"rect": pygame.Rect(jogador.centerx - 7, jogador.top, 15, 25), "rotacao": 0})
        projeteis.append({"rect": pygame.Rect(jogador.centerx - 20, jogador.top, 15, 25), "rotacao": -10})
        projeteis.append({"rect": pygame.Rect(jogador.centerx + 6, jogador.top, 15, 25), "rotacao": 10})
    return projeteis


def criar_coracao():
    x = random.randint(30, largura - 30)
    return pygame.Rect(x, -30, 30, 30)


def criar_portal():
    x = random.randint(60, largura - 60)
    return pygame.Rect(x, -60, 60, 60)


def criar_explosao_efeitos(x, y, tamanho=50):
    criar_particulas_explosao_avancada(x, y, 30)
    efeitos.criar_brilho(x, y, (255, 200, 100), tamanho * 2, 800)
    return {"rect": pygame.Rect(x - tamanho // 2, y - tamanho // 2, tamanho, tamanho),
            "tempo_inicio": pygame.time.get_ticks(), "duracao": 500}


def desenhar_explosao(surface, explosao):
    tempo_decorrido = pygame.time.get_ticks() - explosao["tempo_inicio"]
    progresso = min(tempo_decorrido / explosao["duracao"], 1.0)

    raio = int(progresso * explosao["rect"].width // 2)
    for i in range(3):
        cor = (255, 165 - i * 30, 0)
        pygame.draw.circle(surface, cor, explosao["rect"].center, raio - i * 5)

    for i in range(15):
        angulo = random.uniform(0, 6.28)
        distancia = progresso * 40
        x = explosao["rect"].centerx + int(distancia * pygame.math.Vector2(1, 0).rotate(angulo).x)
        y = explosao["rect"].centery + int(distancia * pygame.math.Vector2(1, 0).rotate(angulo).y)
        pygame.draw.circle(surface, (255, 255, 100), (x, y), 3)


def ativar_habilidade():
    global habilidade_cooldown, habilidade_duracao, habilidade_ativa
    global meteoros_congelados, escudo_ativo, escudo_tempo_fim
    global tiro_triplo_ativo, tiro_triplo_contador
    global velocidade_dupla_ativa, velocidade_dupla_tempo_fim
    global vida_jogador

    agora = pygame.time.get_ticks()
    nave_idx = nave_selecionada

    if agora - habilidade_cooldown[nave_idx] < get_cooldown_habilidade(nave_idx):
        return False

    if nave_idx == 0:
        habilidade_ativa[0] = True
        habilidade_duracao[0] = agora + 3000

        for meteoro in meteoros[:]:
            if not meteoro["congelado"]:
                meteoro["congelado"] = True
                meteoro["congelado_tempo"] = agora + 3000
                meteoros_congelados.append(meteoro)

        print("Campo de Congelamento ativado!")

    elif nave_idx == 1:
        escudo_ativo = True
        escudo_tempo_fim = agora + 5000
        habilidade_ativa[1] = True
        habilidade_duracao[1] = agora + 5000
        print("Escudo de Plasma ativado!")

    elif nave_idx == 2:
        nova_x = random.randint(40, largura - 40)
        nova_y = random.randint(300, 500)
        jogador.x = nova_x
        jogador.y = nova_y

        explosoes.append(criar_explosao_efeitos(jogador.centerx, jogador.centery, 60))
        habilidade_ativa[2] = True
        print("Teletransporte Quântico ativado!")

    elif nave_idx == 3:
        if vida_jogador < max_vida:
            vida_jogador += 1
            print("Vida recuperada!")
        else:
            escudo_ativo = True
            escudo_tempo_fim = agora + 3000
            print("Escudo temporário ativado!")

        habilidade_ativa[3] = True
        explosoes.append(criar_explosao_efeitos(jogador.centerx, jogador.centery, 40))

    elif nave_idx == 4:
        tiro_triplo_ativo = True
        tiro_triplo_contador = 10
        habilidade_ativa[4] = True
        print("Rajada Tripla ativada! Próximos 10 tiros serão triplos!")

    elif nave_idx == 5:
        velocidade_dupla_ativa = True
        velocidade_dupla_tempo_fim = agora + 4000
        habilidade_ativa[5] = True
        habilidade_duracao[5] = agora + 4000
        print("Super Velocidade ativada!")

    habilidade_cooldown[nave_idx] = agora
    return True


def get_cooldown_habilidade(nave_idx):
    cooldowns = [15000, 20000, 10000, 30000, 25000, 12000]
    return cooldowns[nave_idx]


def get_nome_habilidade(nave_idx):
    nomes = [
        "Campo de Congelamento (Q)",
        "Escudo de Plasma (W)",
        "Teletransporte (E)",
        "Cura Regenerativa (R)",
        "Rajada Tripla (T)",
        "Super Velocidade (Y)"
    ]
    return nomes[nave_idx]


def atualizar_habilidades():
    global meteoros_congelados, escudo_ativo, tiro_triplo_ativo, tiro_triplo_contador, velocidade_dupla_ativa
    global habilidade_ativa, habilidade_duracao

    agora = pygame.time.get_ticks()

    for i in range(6):
        if habilidade_ativa[i] and agora > habilidade_duracao[i]:
            habilidade_ativa[i] = False

    if habilidade_ativa[0]:
        for meteoro in meteoros_congelados[:]:
            if meteoro not in meteoros:
                meteoros_congelados.remove(meteoro)
            elif agora > meteoro["congelado_tempo"]:
                meteoro["congelado"] = False
                meteoros_congelados.remove(meteoro)
    else:
        for meteoro in meteoros_congelados:
            if meteoro in meteoros:
                meteoro["congelado"] = False
        meteoros_congelados.clear()

    if escudo_ativo and agora > escudo_tempo_fim:
        escudo_ativo = False

    if tiro_triplo_ativo and tiro_triplo_contador <= 0:
        tiro_triplo_ativo = False

    if velocidade_dupla_ativa and agora > velocidade_dupla_tempo_fim:
        velocidade_dupla_ativa = False


def desenhar_escudo(surface):
    if escudo_ativo:
        tempo = pygame.time.get_ticks()
        raio = 30 + int(5 * math.sin(tempo / 200))

        for i in range(3):
            cor_escudo = (255, 165 - i * 20, 0)
            pygame.draw.circle(surface, cor_escudo, jogador.center, raio - i * 5, 2)

        for _ in range(8):
            angulo = random.uniform(0, 6.28)
            distancia = raio - 5
            x = jogador.centerx + int(distancia * math.cos(angulo))
            y = jogador.centery + int(distancia * math.sin(angulo))
            pygame.draw.circle(surface, (255, 255, 100), (x, y), 2)


def desenhar_meteoros_congelados(surface):
    for meteoro in meteoros_congelados:
        if meteoro["congelado"] and meteoro in meteoros:
            rect = meteoro["rect"]
            pygame.draw.circle(surface, (100, 200, 255), rect.center, rect.width // 2 + 5, 2)

            for _ in range(3):
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-10, 10)
                x = rect.centerx + offset_x
                y = rect.centery + offset_y
                pygame.draw.circle(surface, (200, 230, 255), (x, y), 2)


def desenhar_efeito_velocidade(surface):
    if velocidade_dupla_ativa:
        for i in range(3):
            offset = (i + 1) * 8
            cor = (255, 50 + i * 20, 50 + i * 20)
            rect_rastro = pygame.Rect(jogador.x, jogador.y + offset, jogador.width, jogador.height)
            pygame.draw.rect(surface, cor, rect_rastro, 2)


def ativar_lazer():
    global lazer_ativado, lazer_tempo_inicio, ultimo_lazer, lazer_carregando, lazer_carregamento_tempo

    agora = pygame.time.get_ticks()

    if not lazer_ativado and not lazer_carregando and agora - ultimo_lazer > lazer_cooldown:
        lazer_carregando = True
        lazer_carregamento_tempo = agora
        lazer_tempo_inicio = 0


def desenhar_lazer(surface):
    global lazer_ativado, lazer_carregando, bosses, pontuacao, lazer_tempo_inicio, ultimo_lazer

    if not lazer_ativado and not lazer_carregando:
        return

    agora = pygame.time.get_ticks()

    if lazer_carregando:
        tempo_carregamento = agora - lazer_carregamento_tempo
        progresso = min(tempo_carregamento / 1000, 1.0)

        barra_largura = 40
        barra_altura = 5
        x = jogador.centerx - barra_largura // 2
        y = jogador.top - 10

        pygame.draw.rect(surface, (100, 100, 100), (x, y, barra_largura, barra_altura))
        pygame.draw.rect(surface, (0, 255, 255), (x, y, int(barra_largura * progresso), barra_altura))

        if progresso >= 1.0:
            lazer_carregando = False
            lazer_ativado = True
            lazer_tempo_inicio = agora

    if lazer_ativado:
        tempo_decorrido = agora - lazer_tempo_inicio
        progresso = min(tempo_decorrido / lazer_duracao, 1.0)

        largura_lazer = 20 + int(10 * math.sin(tempo_decorrido / 50))

        cor_base = (0, 200, 255)
        cor_brilho = (100, 255, 255)

        rect_lazer = pygame.Rect(
            jogador.centerx - largura_lazer // 2,
            0,
            largura_lazer,
            jogador.top
        )

        for i in range(largura_lazer):
            intensidade = 0.5 + 0.5 * math.sin((tempo_decorrido + i * 10) / 30)
            cor = (
                int(cor_base[0] * intensidade),
                int(cor_base[1] * intensidade),
                int(cor_base[2] * intensidade)
            )
            pygame.draw.line(
                surface,
                cor,
                (rect_lazer.x + i, rect_lazer.y),
                (rect_lazer.x + i, rect_lazer.bottom),
                1
            )

        pygame.draw.rect(surface, cor_brilho, rect_lazer, 2)

        for _ in range(5):
            x = random.randint(rect_lazer.left, rect_lazer.right)
            y = random.randint(rect_lazer.top, rect_lazer.bottom)
            raio = random.randint(2, 5)
            pygame.draw.circle(surface, (255, 255, 200), (x, y), raio)

        for _ in range(10):
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-5, 5)
            x = jogador.centerx + offset_x
            y = jogador.top + offset_y
            raio = random.randint(1, 3)
            pygame.draw.circle(surface, (255, 255, 200), (x, y), raio)

        if lazer_ativado:
            for meteoro in meteoros[:]:
                if (meteoro["rect"].colliderect(rect_lazer) or
                        meteoro["rect"].colliderect(
                            pygame.Rect(rect_lazer.x - 5, rect_lazer.y, rect_lazer.width + 10, rect_lazer.height))):
                    explosoes.append(criar_explosao_efeitos(meteoro["rect"].centerx, meteoro["rect"].centery, 70))
                    meteoros.remove(meteoro)
                    pontuacao += 50

            for projetil in projeteis_boss[:]:
                if projetil["rect"].colliderect(rect_lazer):
                    explosoes.append(criar_explosao_efeitos(projetil["rect"].centerx, projetil["rect"].centery, 30))
                    projeteis_boss.remove(projetil)

            for boss in bosses[:]:
                if boss.rect.colliderect(rect_lazer):
                    explosoes.append(criar_explosao_efeitos(boss.rect.centerx, boss.rect.centery, 40))
                    if boss.levar_dano(5):
                        explosoes.append(criar_explosao_efeitos(boss.rect.centerx, boss.rect.centery, 100))
                        pontuacao += 500
                        bosses.remove(boss)

        if progresso >= 1.0:
            lazer_ativado = False
            ultimo_lazer = agora


def atualizar_municao():
    global municao_atual, recarregando, tempo_inicio_recarga

    agora = pygame.time.get_ticks()

    if municao_atual <= 0 and not recarregando:
        recarregando = True
        tempo_inicio_recarga = agora

    if recarregando:
        tempo_recarga = agora - tempo_inicio_recarga
        if tempo_recarga >= intervalo_recarga:
            municao_atual = municao_maxima
            recarregando = False


def criar_bosses(nivel_boss):
    global bosses, boss_ativo

    bosses.clear()

    if nivel_boss >= 10:
        boss1_x = largura // 3 - 35
        boss2_x = 2 * largura // 3 - 35

        bosses.append(Boss(nivel_boss, boss1_x, usar_lazer=False))
        bosses.append(Boss(nivel_boss, boss2_x, usar_lazer=True))
        print(f"DOIS BOSSES apareceram! Nível {nivel_boss} - Um deles usa LAZER!")
    else:
        boss_x = largura // 2 - 35
        bosses.append(Boss(nivel_boss, boss_x, usar_lazer=False))
        print(f"BOSS apareceu! Nível {nivel_boss}")

    boss_ativo = True


def atualizar_nivel():
    global nivel, boss_ativo, ultimo_boss_derrotado

    novo_nivel = max(1, pontuacao // 300 + 1)

    if novo_nivel > nivel:
        nivel = novo_nivel
        print(f"Subiu para o nível {nivel}!")

    if (nivel % 5 == 0 and
            not boss_ativo and
            len(bosses) == 0 and
            nivel > ultimo_boss_derrotado):
        criar_bosses(nivel)


def atualizar_pontuacao():
    global pontuacao, tempo_atual, pontuacao_para_proxima_nave
    tempo_atual = (pygame.time.get_ticks() - tempo_inicio) // 1000
    pontuacao = tempo_atual * 15
    pontuacao_para_proxima_nave = pontuacao
    atualizar_nivel()

    if verificar_desbloqueio_naves():
        for _ in range(50):
            criar_particulas_explosao_avancada(largura // 2, altura // 2, 1, (0, 255, 255))


def desenhar_vidas():
    for i in range(vida_jogador):
        x = largura - 40 - (i * 35)
        y = 10
        tela.blit(coracao_img, (x, y))


def desenhar_interface():
    texto_pontuacao = fonte.render(f'Pontos: {pontuacao}', True, (255, 255, 255))
    tela.blit(texto_pontuacao, (10, 10))

    minutos = tempo_atual // 60
    segundos = tempo_atual % 60
    texto_tempo = fonte.render(f'Tempo: {minutos:02d}:{segundos:02d}', True, (255, 255, 255))
    tela.blit(texto_tempo, (10, 50))

    texto_nivel = fonte.render(f'Nível: {nivel}', True, (255, 255, 255))
    tela.blit(texto_nivel, (10, 90))

    proxima_nave = None
    for i in range(1, len(naves_desbloqueadas)):
        if not naves_desbloqueadas[i]:
            proxima_nave = i
            break

    if proxima_nave is not None:
        progresso = min(pontuacao_para_proxima_nave / pontuacao_necessaria_por_nave[proxima_nave], 1.0)
        texto_progresso = fonte_pequena.render(f'Próxima nave: {int(progresso * 100)}%', True, (255, 255, 255))
        tela.blit(texto_progresso, (10, 130))

        barra_largura = 150
        barra_altura = 8
        pygame.draw.rect(tela, (100, 100, 100), (10, 150, barra_largura, barra_altura))
        pygame.draw.rect(tela, (0, 255, 0), (10, 150, int(barra_largura * progresso), barra_altura))
    else:
        texto_todas_naves = fonte_pequena.render('Todas as naves desbloqueadas!', True, (0, 255, 0))
        tela.blit(texto_todas_naves, (10, 130))

    if recarregando:
        tempo_restante = max(0, intervalo_recarga - (pygame.time.get_ticks() - tempo_inicio_recarga))
        segundos_restantes = tempo_restante // 1000
        texto_municao = fonte.render(f'Recarregando: {segundos_restantes}s', True, (255, 200, 0))
    else:
        texto_municao = fonte.render(f'Munição: {municao_atual}/{municao_maxima}', True, (255, 255, 255))
    tela.blit(texto_municao, (10, 170))

    agora = pygame.time.get_ticks()
    cooldown_restante = max(0,
                            get_cooldown_habilidade(nave_selecionada) - (agora - habilidade_cooldown[nave_selecionada]))
    segundos_cooldown = cooldown_restante // 1000

    nome_habilidade = get_nome_habilidade(nave_selecionada)

    if nave_selecionada == 4 and tiro_triplo_ativo:
        texto_habilidade = fonte_pequena.render(f'Rajada: {tiro_triplo_contador} tiros', True, (255, 255, 0))
    elif cooldown_restante > 0:
        texto_habilidade = fonte_pequena.render(f'{nome_habilidade}: {segundos_cooldown}s', True, (200, 200, 200))
    else:
        texto_habilidade = fonte_pequena.render(f'{nome_habilidade}: PRONTO', True, (0, 255, 0))

    tela.blit(texto_habilidade, (10, 200))

    desenhar_vidas()

    if boss_ativo:
        texto_boss = fonte.render('BOSS!', True, (255, 0, 0))
        tela.blit(texto_boss, (largura - 100, 10))

        if len(bosses) > 1:
            texto_boss_count = fonte_pequena.render(f'Bosses: {len(bosses)}', True, (255, 255, 255))
            tela.blit(texto_boss_count, (largura - 120, 40))

    cooldown_restante_lazer = max(0, lazer_cooldown - (agora - ultimo_lazer))
    segundos_cooldown_lazer = cooldown_restante_lazer // 1000

    if cooldown_restante_lazer > 0:
        texto_lazer = fonte_pequena.render(f'Lazer: {segundos_cooldown_lazer}s', True, (200, 200, 200))
    else:
        texto_lazer = fonte_pequena.render('Lazer: PRONTO (L)', True, (0, 255, 255))

    tela.blit(texto_lazer, (largura - 150, altura - 60))

    texto_instrucoes = fonte_pequena.render('1-6: Trocar nave | ESPACO: Atirar | L: Lazer', True, (200, 200, 200))
    tela.blit(texto_instrucoes, (10, altura - 90))
    texto_instrucoes2 = fonte_pequena.render('Q/W/E/R/T/Y: Habilidades especiais', True, (200, 200, 200))
    tela.blit(texto_instrucoes2, (10, altura - 60))
    texto_instrucoes3 = fonte_pequena.render('R: Reiniciar', True, (200, 200, 200))
    tela.blit(texto_instrucoes3, (10, altura - 30))


def rotacionar_imagem(imagem, angulo):
    return pygame.transform.rotate(imagem, angulo)


def desenhar_fundo_completo(surface):
    """Desenha o fundo com todos os efeitos"""
    surface.fill((5, 5, 20))
    fundo_estelar.desenhar(surface)
    efeitos.desenhar_brilhos(surface)

    for particula in particulas:
        particula.desenhar(surface)


def atualizar_efeitos_visuais():
    """Atualiza todos os efeitos visuais"""
    fundo_estelar.atualizar()
    efeitos.atualizar_brilhos()

    for particula in particulas[:]:
        if not particula.atualizar():
            particulas.remove(particula)


# == INICIALIZAÇÃO DO JOGO ==
rodando = True
game_over = False
ultimo_salvamento = 0
intervalo_salvamento = 30000

progresso_salvo = carregar_progresso()

# == LOOP PRINCIPAL DO JOGO ==
if __name__ == "__main__":
    if mostrar_menu_principal():
        while rodando:
            # Desenhar fundo avançado
            desenhar_fundo_completo(tela)

            # Atualizar efeitos
            atualizar_efeitos_visuais()

            # Criar partículas de ambiente
            criar_particulas_estrelas_avancadas()
            criar_particulas_propulsao_avancada()
            criar_particulas_escudo_avancado()

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    salvar_progresso()
                    rodando = False

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_1:
                        trocar_nave(1)
                    elif evento.key == pygame.K_2:
                        trocar_nave(2)
                    elif evento.key == pygame.K_3:
                        trocar_nave(3)
                    elif evento.key == pygame.K_4:
                        trocar_nave(4)
                    elif evento.key == pygame.K_5:
                        trocar_nave(5)
                    elif evento.key == pygame.K_6:
                        trocar_nave(6)
                    elif evento.key == pygame.K_SPACE and not game_over:
                        if tiro_triplo_ativo:
                            novos_projeteis = criar_projeteis_triplo()
                            for projetil in novos_projeteis:
                                projeteis.append(projetil)
                            municao_atual -= 1
                            tiro_triplo_contador -= 1
                            if tiro_triplo_contador <= 0:
                                tiro_triplo_ativo = False
                                print("Rajada Tripla acabou!")
                        else:
                            novo_projetil = criar_projetil()
                            if novo_projetil is not None:
                                projeteis.append(novo_projetil)
                                municao_atual -= 1
                    elif evento.key == pygame.K_l and not game_over:
                        ativar_lazer()
                    elif evento.key == pygame.K_q and not game_over:
                        ativar_habilidade()
                    elif evento.key == pygame.K_w and not game_over:
                        ativar_habilidade()
                    elif evento.key == pygame.K_e and not game_over:
                        ativar_habilidade()
                    elif evento.key == pygame.K_r and not game_over:
                        ativar_habilidade()
                    elif evento.key == pygame.K_t and not game_over:
                        ativar_habilidade()
                    elif evento.key == pygame.K_y and not game_over:
                        ativar_habilidade()
                    elif evento.key == pygame.K_r and game_over:
                        salvar_progresso()
                        # Reiniciar jogo
                        jogador = pygame.Rect(180, 500, 40, 40)
                        meteoros = []
                        projeteis = []
                        projeteis_boss = []
                        explosoes = []
                        coracoes = []
                        portais = []
                        powerups = []
                        bosses = []
                        boss_ativo = False
                        pontuacao = 0
                        pontuacao_para_proxima_nave = 0
                        nivel = 1
                        vida_jogador = 3
                        municao_atual = municao_maxima
                        recarregando = False
                        lazer_ativado = False
                        lazer_carregando = False
                        ultimo_lazer = 0
                        habilidade_cooldown = [0, 0, 0, 0, 0, 0]
                        habilidade_duracao = [0, 0, 0, 0, 0, 0]
                        habilidade_ativa = [False, False, False, False, False, False]
                        meteoros_congelados = []
                        escudo_ativo = False
                        tiro_triplo_ativo = False
                        tiro_triplo_contador = 0
                        velocidade_dupla_ativa = False
                        tempo_inicio = pygame.time.get_ticks()
                        ultimo_boss_derrotado = 0
                        naves_desbloqueadas = [True] + [False] * 5
                        nave_selecionada = 0
                        particulas.clear()
                        game_over = False

            # Atualizar bosses
            for boss in bosses[:]:
                boss.atualizar(jogador)

                if boss.pode_atirar():
                    novos_projeteis = boss.atirar(jogador)
                    projeteis_boss.extend(novos_projeteis)

                if boss.usar_lazer and random.random() < 0.02:
                    boss.ativar_lazer()

                if boss.desenhar_lazer(tela, jogador):
                    if not escudo_ativo:
                        explosoes.append(criar_explosao_efeitos(jogador.centerx, jogador.centery, 60))
                        vida_jogador -= 2
                        if vida_jogador <= 0:
                            game_over = True

            agora = pygame.time.get_ticks()

            # Salvar progresso periodicamente
            if agora - ultimo_salvamento > intervalo_salvamento:
                salvar_progresso()
                ultimo_salvamento = agora

            # Gerar power-ups
            if agora - ultimo_powerup > intervalo_powerups and len(powerups) < 2 and not boss_ativo:
                powerups.append(criar_powerup())
                ultimo_powerup = agora

            if agora - ultimo_coracao > intervalo_coracoes and len(coracoes) < 3:
                coracoes.append(criar_coracao())
                ultimo_coracao = agora

            if agora - ultimo_portal > intervalo_portais and len(portais) < 1 and not boss_ativo:
                portais.append(criar_portal())
                ultimo_portal = agora

            # Atualizar sistemas
            atualizar_municao()
            atualizar_habilidades()

            if not game_over:
                velocidade_atual = velocidade * 2 if velocidade_dupla_ativa else velocidade

                teclas = pygame.key.get_pressed()
                if teclas[pygame.K_LEFT] and jogador.left > 0:
                    jogador.x -= velocidade_atual
                if teclas[pygame.K_RIGHT] and jogador.right < largura:
                    jogador.x += velocidade_atual
                if teclas[pygame.K_UP] and jogador.top > 0:
                    jogador.y -= velocidade_atual
                if teclas[pygame.K_DOWN] and jogador.bottom < altura:
                    jogador.y += velocidade_atual

                chance_spawn = max(5, 60 - nivel * 3)
                if boss_ativo:
                    chance_spawn = max(10, 80 - nivel * 3)

                if random.randint(1, chance_spawn) == 1:
                    meteoros.append(criar_meteoro())

                for meteoro in meteoros[:]:
                    if not meteoro["congelado"]:
                        meteoro["rect"].y += meteoro["velocidade_y"]
                        meteoro["rect"].x += meteoro["velocidade_x"]
                        meteoro["rotacao"] += meteoro["rotacao_speed"]

                        if meteoro["rect"].left <= 0 or meteoro["rect"].right >= largura:
                            meteoro["velocidade_x"] *= -1

                    if meteoro["rect"].colliderect(jogador):
                        if not escudo_ativo:
                            explosoes.append(
                                criar_explosao_efeitos(meteoro["rect"].centerx, meteoro["rect"].centery, 70))
                            vida_jogador -= 1
                            if vida_jogador <= 0:
                                game_over = True
                        else:
                            explosoes.append(
                                criar_explosao_efeitos(meteoro["rect"].centerx, meteoro["rect"].centery, 50))
                            pontuacao += 25

                        if meteoro in meteoros:
                            meteoros.remove(meteoro)

                    if meteoro["grande"]:
                        meteoro_img_rotacionada = rotacionar_imagem(meteoro_grande_img, meteoro["rotacao"])
                    else:
                        meteoro_img_rotacionada = rotacionar_imagem(meteoro_img, meteoro["rotacao"])

                    tela.blit(meteoro_img_rotacionada, meteoro["rect"])

                for coracao in coracoes[:]:
                    coracao.y += 3

                    if coracao.colliderect(jogador) and vida_jogador < max_vida:
                        vida_jogador += 1
                        coracoes.remove(coracao)
                        explosoes.append(criar_explosao_efeitos(coracao.centerx, coracao.centery, 30))

                    elif coracao.y < altura:
                        tela.blit(coracao_img, coracao)
                    else:
                        coracoes.remove(coracao)

                for portal in portais[:]:
                    portal.y += 2

                    if portal.colliderect(jogador):
                        nivel += 3
                        pontuacao += 600
                        portais.remove(portal)
                        explosoes.append(criar_explosao_efeitos(portal.centerx, portal.centery, 80))
                        print(f"Portal usado! Avançou para o nível {nivel}")

                    elif portal.y < altura:
                        tela.blit(portal_img, portal)
                    else:
                        portais.remove(portal)

                # Atualizar power-ups
                for powerup in powerups[:]:
                    powerup['rect'].y += 3

                    if powerup['rect'].colliderect(jogador):
                        aplicar_powerup(powerup['tipo'])
                        powerups.remove(powerup)
                        explosoes.append(criar_explosao_efeitos(powerup['rect'].centerx, powerup['rect'].centery, 40))

                    elif powerup['rect'].y < altura:
                        desenhar_powerups(tela)
                    else:
                        powerups.remove(powerup)

                projeteis_a_remover = []

                for projetil in projeteis[:]:
                    velocidade_projetil = 15 if velocidade_dupla_ativa else 10
                    projetil["rect"].y -= velocidade_projetil
                    projetil["rotacao"] += 5

                    for meteoro in meteoros[:]:
                        if projetil["rect"].colliderect(meteoro["rect"]):
                            explosoes.append(
                                criar_explosao_efeitos(meteoro["rect"].centerx, meteoro["rect"].centery, 70))
                            projeteis_a_remover.append(projetil)
                            if meteoro in meteoros:
                                meteoros.remove(meteoro)
                            pontuacao += 50
                            break

                    for boss in bosses[:]:
                        if projetil["rect"].colliderect(boss.rect):
                            explosoes.append(
                                criar_explosao_efeitos(projetil["rect"].centerx, projetil["rect"].centery, 30))
                            projeteis_a_remover.append(projetil)
                            if boss.levar_dano(10):
                                explosoes.append(criar_explosao_efeitos(boss.rect.centerx, boss.rect.centery, 100))
                                pontuacao += 500
                                ultimo_boss_derrotado = boss.nivel_boss
                                bosses.remove(boss)
                                if len(bosses) == 0:
                                    boss_ativo = False
                                    print(f"BOSS nível {ultimo_boss_derrotado} derrotado! Jogo continua normalmente.")
                            break

                    if projetil["rect"].bottom < 0:
                        projeteis_a_remover.append(projetil)
                    else:
                        projetil_img_rotacionada = rotacionar_imagem(projetil_img, projetil["rotacao"])
                        tela.blit(projetil_img_rotacionada, projetil["rect"])

                for projetil in projeteis_a_remover:
                    if projetil in projeteis:
                        projeteis.remove(projetil)

                for projetil in projeteis_boss[:]:
                    projetil["rect"].x += projetil["velocidade_x"]
                    projetil["rect"].y += projetil["velocidade_y"]

                    if projetil["rect"].colliderect(jogador):
                        if not escudo_ativo:
                            explosoes.append(
                                criar_explosao_efeitos(projetil["rect"].centerx, projetil["rect"].centery, 40))
                            projeteis_boss.remove(projetil)
                            vida_jogador -= 1
                            if vida_jogador <= 0:
                                game_over = True
                        else:
                            explosoes.append(
                                criar_explosao_efeitos(projetil["rect"].centerx, projetil["rect"].centery, 20))
                            projeteis_boss.remove(projetil)
                            pontuacao += 10

                    elif (projetil["rect"].top > altura or
                          projetil["rect"].left < 0 or
                          projetil["rect"].right > largura):
                        projeteis_boss.remove(projetil)
                    else:
                        tela.blit(projetil_boss_img, projetil["rect"])

                meteoros = [meteoro for meteoro in meteoros if meteoro["rect"].y < altura]

            # Desenhar efeitos visuais das habilidades
            desenhar_meteoros_congelados(tela)
            desenhar_escudo(tela)
            desenhar_efeito_velocidade(tela)

            # Desenhar e atualizar lazer
            desenhar_lazer(tela)

            # Desenhar bosses
            for boss in bosses:
                tela.blit(boss_img, boss.rect)
                boss.desenhar_barra_vida(tela)

            for explosao in explosoes[:]:
                tempo_decorrido = pygame.time.get_ticks() - explosao["tempo_inicio"]
                if tempo_decorrido > explosao["duracao"]:
                    explosoes.remove(explosao)
                else:
                    desenhar_explosao(tela, explosao)

            atualizar_pontuacao()
            desenhar_interface()

            if not game_over and naves_imagens:
                tela.blit(naves_imagens[nave_selecionada], jogador)
            elif game_over:
                texto_gameover = fonte.render('GAME OVER', True, (255, 0, 0))
                texto_reiniciar = fonte.render('Pressione R para reiniciar', True, (255, 255, 255))
                tela.blit(texto_gameover, (largura // 2 - 80, altura // 2 - 50))
                tela.blit(texto_reiniciar, (largura // 2 - 150, altura // 2))

            pygame.display.flip()
            clock.tick(60)

        salvar_progresso()

pygame.quit()