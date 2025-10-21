import random
import pygame
import os
import math
import json
import sys

pygame.init()

largura, altura = 400, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Nave vs Meteoros - Versão Aprimorada")
clock = pygame.time.Clock()


# == SISTEMA FLEXÍVEL DE CARREGAMENTO DE IMAGENS ==
def encontrar_arquivos_imagem():
    """Encontra arquivos de imagem em vários locais possíveis"""
    locais_possiveis = [
        os.path.dirname(__file__),  # Diretório atual do script
        os.path.join(os.path.dirname(__file__), "imagens"),
        os.path.join(os.path.dirname(__file__), "assets"),
        os.path.join(os.path.dirname(__file__), "sprites"),
        os.path.join(os.path.expanduser("~"), "Pictures"),
        os.path.join(os.path.expanduser("~"), "Downloads"),
        os.path.join(os.path.expanduser("~"), "Documents"),
        r"C:\Users\aluno\PyCharm\Cotacao-Kivy\corrida",
    ]

    for local in locais_possiveis:
        if os.path.exists(local):
            try:
                arquivos = [f for f in os.listdir(local) if
                            f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
                if arquivos:
                    print(f"Imagens encontradas em: {local}")
                    return local, arquivos
            except (PermissionError, OSError) as e:
                print(f"Erro ao acessar {local}: {e}")
                continue

    print("Nenhuma imagem encontrada. Usando sprites gerados.")
    return None, []


caminho_imagens, arquivos_disponiveis = encontrar_arquivos_imagem()
print("Arquivos encontrados:", arquivos_disponiveis)


# == SISTEMA DE SHADERS E EFEITOS VISUAIS SUPER AVANÇADOS ==
class EfeitosVisuais:
    def __init__(self):
        self.brilho_buffer = pygame.Surface((largura, altura), pygame.SRCALPHA)
        self.particulas_brilho = []
        self.luzes_dinamicas = []
        self.scanlines = pygame.Surface((largura, altura), pygame.SRCALPHA)
        self.inicializar_scanlines()
        self.rastros_laser = []

    def inicializar_scanlines(self):
        """Cria efeito de scanlines para dar profundidade"""
        for y in range(0, altura, 4):
            pygame.draw.line(self.scanlines, (0, 0, 0, 15), (0, y), (largura, y))

    def criar_brilho(self, x, y, cor, raio=50, duracao=1000, intensidade=1.0):
        """Cria um efeito de brilho com partículas de luz"""
        if isinstance(cor, tuple) and len(cor) == 3:
            self.particulas_brilho.append({
                'x': x, 'y': y, 'cor': cor, 'raio': raio,
                'tempo_inicio': pygame.time.get_ticks(),
                'duracao': duracao,
                'intensidade': intensidade
            })

    def criar_luz_dinamica(self, x, y, cor, raio=100, duracao=2000, pulsante=False):
        """Cria uma luz dinâmica que pode pulsar"""
        self.luzes_dinamicas.append({
            'x': x, 'y': y, 'cor': cor, 'raio': raio,
            'raio_base': raio,
            'tempo_inicio': pygame.time.get_ticks(),
            'duracao': duracao,
            'pulsante': pulsante,
            'alpha': 255
        })

    def criar_onda_choque(self, x, y, cor=(255, 255, 255), raio_maximo=200, duracao=800):
        """Cria um efeito de onda de choque expansiva"""
        for i in range(3):
            self.particulas_brilho.append({
                'x': x, 'y': y, 'cor': cor,
                'raio': 10 + i * 20,
                'tempo_inicio': pygame.time.get_ticks() + i * 100,
                'duracao': duracao,
                'intensidade': 0.8 - i * 0.2
            })

    def criar_rastro_laser(self, start_pos, end_pos, cor, largura=10, duracao=300):
        """Cria um rastro para lasers - EFEITO MELHORADO"""
        tempo_atual = pygame.time.get_ticks()

        # Adicionar ao sistema de rastros
        self.rastros_laser.append({
            'start_pos': start_pos,
            'end_pos': end_pos,
            'cor': cor,
            'largura': largura,
            'tempo_inicio': tempo_atual,
            'duracao': duracao
        })

        # Criar partículas ao longo do laser
        distancia = math.sqrt((end_pos[0] - start_pos[0]) ** 2 + (end_pos[1] - start_pos[1]) ** 2)
        num_particulas = max(5, int(distancia / 8))

        for i in range(num_particulas):
            progresso = i / num_particulas
            x = start_pos[0] + (end_pos[0] - start_pos[0]) * progresso
            y = start_pos[1] + (end_pos[1] - start_pos[1]) * progresso

            # Adicionar variação aleatória
            variacao_x = random.uniform(-8, 8)
            variacao_y = random.uniform(-8, 8)

            self.particulas_brilho.append({
                'x': x + variacao_x,
                'y': y + variacao_y,
                'cor': cor,
                'raio': random.uniform(4, 10),
                'tempo_inicio': tempo_atual + random.randint(0, 100),
                'duracao': duracao + random.randint(0, 200),
                'intensidade': random.uniform(0.6, 0.9)
            })

    def atualizar_brilhos(self):
        tempo_atual = pygame.time.get_ticks()

        # Atualizar partículas de brilho
        self.particulas_brilho = [brilho for brilho in self.particulas_brilho
                                  if tempo_atual - brilho['tempo_inicio'] < brilho['duracao']]

        # Atualizar luzes dinâmicas
        novas_luzes = []
        for luz in self.luzes_dinamicas:
            tempo_decorrido = tempo_atual - luz['tempo_inicio']
            if tempo_decorrido < luz['duracao']:
                progresso = tempo_decorrido / luz['duracao']
                luz['alpha'] = int(255 * (1 - progresso))

                if luz['pulsante']:
                    pulsacao = 0.5 + 0.5 * math.sin(tempo_atual * 0.01)
                    luz['raio'] = int(luz['raio_base'] * (0.8 + 0.4 * pulsacao))

                novas_luzes.append(luz)
        self.luzes_dinamicas = novas_luzes

        # Atualizar rastros de laser
        self.rastros_laser = [rastro for rastro in self.rastros_laser
                              if tempo_atual - rastro['tempo_inicio'] < rastro['duracao']]

    def desenhar_brilhos(self, surface):
        # Desenhar luzes dinâmicas primeiro (como base)
        for luz in self.luzes_dinamicas:
            surf_luz = pygame.Surface((luz['raio'] * 2, luz['raio'] * 2), pygame.SRCALPHA)

            # Gradiente radial para luz - MELHORADO
            for i in range(4):
                alpha = max(0, luz['alpha'] // (i + 1))
                if alpha > 0:
                    raio_camada = max(1, luz['raio'] - i * 12)
                    cor_luz = luz['cor'] + (alpha,)
                    pygame.draw.circle(surf_luz, cor_luz,
                                       (luz['raio'], luz['raio']), raio_camada)

            surface.blit(surf_luz, (luz['x'] - luz['raio'], luz['y'] - luz['raio']),
                         special_flags=pygame.BLEND_ADD)

        # Desenhar rastros de laser
        for rastro in self.rastros_laser:
            tempo_atual = pygame.time.get_ticks()
            progresso = (tempo_atual - rastro['tempo_inicio']) / rastro['duracao']
            alpha = max(0, int(255 * (1 - progresso)))

            if alpha > 0:
                # Desenhar linha de rastro
                cor_rastro = rastro['cor'] + (alpha // 2,)
                pygame.draw.line(surface, cor_rastro,
                                 rastro['start_pos'], rastro['end_pos'],
                                 max(1, rastro['largura'] // 2))

        # Desenhar partículas de brilho
        for brilho in self.particulas_brilho:
            tempo_atual = pygame.time.get_ticks()
            progresso = (tempo_atual - brilho['tempo_inicio']) / brilho['duracao']
            alpha = max(0, int(255 * (1 - progresso) * brilho['intensidade']))
            raio_atual = int(brilho['raio'] * (1 - progresso))

            if isinstance(brilho['cor'], tuple) and len(brilho['cor']) == 3 and alpha > 0:
                surf_brilho = pygame.Surface((raio_atual * 2, raio_atual * 2), pygame.SRCALPHA)

                # Efeito de brilho com múltiplas camadas - MELHORADO
                for i in range(5):
                    alpha_camada = max(0, alpha // (i + 1))
                    if alpha_camada > 0:
                        cor_brilho = brilho['cor'] + (alpha_camada,)
                        raio_camada = max(1, raio_atual - i * 6)
                        pygame.draw.circle(surf_brilho, cor_brilho,
                                           (raio_atual, raio_atual), raio_camada)

                surface.blit(surf_brilho, (brilho['x'] - raio_atual, brilho['y'] - raio_atual),
                             special_flags=pygame.BLEND_ADD)

        # Aplicar scanlines
        surface.blit(self.scanlines, (0, 0))


efeitos = EfeitosVisuais()


# == SISTEMA DE PARTÍCULAS SUPER AVANÇADO ==
class ParticulaAvancada:
    def __init__(self, x, y, cor, velocidade_x=0, velocidade_y=0,
                 vida_util=1000, tamanho=3, tipo="normal", gravidade=0, rotacao=0):
        self.x = x
        self.y = y
        self.cor = cor if isinstance(cor, tuple) and len(cor) == 3 else (255, 255, 255)
        self.velocidade_x = velocidade_x
        self.velocidade_y = velocidade_y
        self.vida_util = vida_util
        self.tempo_inicio = pygame.time.get_ticks()
        self.tamanho = max(1, tamanho)
        self.tamanho_original = self.tamanho
        self.tipo = tipo
        self.gravidade = gravidade
        self.rotacao = rotacao if rotacao != 0 else random.uniform(0, 360)
        self.velocidade_rotacao = random.uniform(-5, 5)
        self.trail = []  # Para partículas com rastro
        self.max_trail = 5

    def atualizar(self):
        tempo_atual = pygame.time.get_ticks()
        tempo_decorrido_part = tempo_atual - self.tempo_inicio

        if tempo_decorrido_part > self.vida_util:
            return False

        # Atualizar posição
        self.x += self.velocidade_x
        self.y += self.velocidade_y
        self.velocidade_y += self.gravidade

        # Adicionar posição ao rastro
        if self.tipo in ["estrela", "faisca", "laser"]:
            self.trail.append((self.x, self.y))
            if len(self.trail) > self.max_trail:
                self.trail.pop(0)

        if self.tipo in ["estrela", "cristal", "laser"]:
            self.rotacao += self.velocidade_rotacao

        progresso = tempo_decorrido_part / self.vida_util

        # Comportamentos diferentes por tipo
        if self.tipo == "fumaca":
            self.tamanho = self.tamanho_original * (1 + progresso * 0.5)
        elif self.tipo == "faisca":
            self.tamanho = max(1, self.tamanho_original * (1 - progresso * 2))
        elif self.tipo == "estrela":
            self.tamanho = self.tamanho_original * (0.8 + 0.4 * math.sin(progresso * 10))
        elif self.tipo == "laser":
            self.tamanho = self.tamanho_original * (0.9 + 0.2 * math.sin(progresso * 20))
        else:
            self.tamanho = max(1, self.tamanho_original * (1 - progresso))

        return True

    def desenhar(self, surface):
        tempo_decorrido_part = pygame.time.get_ticks() - self.tempo_inicio
        progresso = tempo_decorrido_part / self.vida_util
        alpha = max(0, int(255 * (1 - progresso)))

        if alpha <= 0:
            return

        cor_com_alpha = self.cor + (alpha,)

        # Desenhar rastro primeiro (se houver)
        if self.trail and self.tipo in ["estrela", "faisca", "laser"]:
            for i, (trail_x, trail_y) in enumerate(self.trail):
                trail_alpha = alpha * (i / len(self.trail)) * 0.5
                trail_cor = self.cor + (int(trail_alpha),)
                trail_size = self.tamanho * (i / len(self.trail))

                surf_trail = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf_trail, trail_cor, (trail_size, trail_size), max(1, trail_size))
                surface.blit(surf_trail, (int(trail_x - trail_size), int(trail_y - trail_size)))

        if self.tipo == "estrela":
            surf = pygame.Surface((self.tamanho * 3, self.tamanho * 3), pygame.SRCALPHA)
            pontos = []
            for i in range(5):
                angulo = math.radians(self.rotacao + i * 72)
                raio_externo = self.tamanho
                raio_interno = max(1, self.tamanho * 0.4)

                x_ext = self.tamanho * 1.5 + math.cos(angulo) * raio_externo
                y_ext = self.tamanho * 1.5 + math.sin(angulo) * raio_externo
                pontos.append((x_ext, y_ext))

                x_int = self.tamanho * 1.5 + math.cos(angulo + math.radians(36)) * raio_interno
                y_int = self.tamanho * 1.5 + math.sin(angulo + math.radians(36)) * raio_interno
                pontos.append((x_int, y_int))

            pygame.draw.polygon(surf, cor_com_alpha, pontos)
            surface.blit(surf, (int(self.x - self.tamanho * 1.5), int(self.y - self.tamanho * 1.5)))

        elif self.tipo == "cristal":
            surf = pygame.Surface((self.tamanho * 2, self.tamanho * 2), pygame.SRCALPHA)
            pontos = [
                (self.tamanho, 0),
                (self.tamanho * 2, self.tamanho),
                (self.tamanho, self.tamanho * 2),
                (0, self.tamanho)
            ]
            pontos_rotacionados = []
            for px, py in pontos:
                px -= self.tamanho
                py -= self.tamanho
                px_rot = px * math.cos(math.radians(self.rotacao)) - py * math.sin(math.radians(self.rotacao))
                py_rot = px * math.sin(math.radians(self.rotacao)) + py * math.cos(math.radians(self.rotacao))
                pontos_rotacionados.append((px_rot + self.tamanho, py_rot + self.tamanho))

            pygame.draw.polygon(surf, cor_com_alpha, pontos_rotacionados)
            surface.blit(surf, (int(self.x - self.tamanho), int(self.y - self.tamanho)))

        elif self.tipo == "energia":
            # Partícula de energia com efeito pulsante
            pulsacao = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.02)
            tamanho_pulsante = self.tamanho * (0.8 + 0.4 * pulsacao)

            surf = pygame.Surface((tamanho_pulsante * 2, tamanho_pulsante * 2), pygame.SRCALPHA)

            # Núcleo brilhante
            pygame.draw.circle(surf, cor_com_alpha,
                               (tamanho_pulsante, tamanho_pulsante),
                               max(1, tamanho_pulsante))

            # Aurora externa
            for i in range(2):
                alpha_aurora = max(0, alpha // (i + 2))
                if alpha_aurora > 0:
                    cor_aurora = self.cor + (alpha_aurora,)
                    pygame.draw.circle(surf, cor_aurora,
                                       (tamanho_pulsante, tamanho_pulsante),
                                       max(1, tamanho_pulsante + 2 + i * 3), 2)

            surface.blit(surf, (int(self.x - tamanho_pulsante), int(self.y - tamanho_pulsante)))

        elif self.tipo == "laser":
            # Partícula especial para efeitos de laser
            surf = pygame.Surface((self.tamanho * 2, self.tamanho * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, cor_com_alpha, (self.tamanho, self.tamanho), max(1, self.tamanho))

            # Brilho extra para partículas de laser
            for i in range(2):
                alpha_brilho = max(0, alpha // (i + 3))
                if alpha_brilho > 0:
                    cor_brilho = self.cor + (alpha_brilho,)
                    pygame.draw.circle(surf, cor_brilho, (self.tamanho, self.tamanho),
                                       max(1, self.tamanho + 1 + i * 2))

            surface.blit(surf, (int(self.x - self.tamanho), int(self.y - self.tamanho)))

        else:
            surf = pygame.Surface((self.tamanho * 2, self.tamanho * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, cor_com_alpha, (self.tamanho, self.tamanho), max(1, self.tamanho))
            surface.blit(surf, (int(self.x - self.tamanho), int(self.y - self.tamanho)))


# == FUNÇÕES GLOBAIS DE EFEITOS VISUAIS ==
particulas = []


def criar_particulas_explosao_avancada(x, y, quantidade=25, cor_base=(255, 165, 0), tamanho_base=50):
    """Cria uma explosão avançada com múltiplos tipos de partículas"""
    if len(particulas) > 800:
        quantidade = min(quantidade, 10)

    # Efeitos de brilho
    efeitos.criar_brilho(x, y, cor_base, tamanho_base, 1500, 1.0)
    efeitos.criar_onda_choque(x, y, cor_base, tamanho_base * 2, 800)

    # Luz dinâmica para explosão
    efeitos.criar_luz_dinamica(x, y, cor_base, tamanho_base * 3, 1000, True)

    for _ in range(quantidade):
        angulo = random.uniform(0, 2 * math.pi)
        velocidade = random.uniform(2, 8)
        vida_util = random.randint(400, 1200)
        tamanho = random.randint(2, 6)

        tipo = random.choice(["normal", "fumaca", "faisca", "estrela", "energia"])

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
    """Cria partículas de estrelas para o fundo"""
    for _ in range(3):
        if random.random() < 0.2 and len(particulas) < 700:
            x = random.randint(0, largura)
            velocidade = random.uniform(0.8, 3)
            tamanho = random.uniform(1, 3)
            brilho = random.randint(150, 255)

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
    """Cria partículas de propulsão da nave"""
    global game_over, particulas, jogador
    if not game_over and len(particulas) < 750:
        for i in range(4):
            offset_x = random.randint(-18, 18)
            cor_base = (random.randint(150, 255), random.randint(50, 150), 0)

            particulas.append(ParticulaAvancada(
                jogador.centerx + offset_x,
                jogador.bottom,
                cor_base,
                random.uniform(-1, 1), random.uniform(2, 5),
                600, random.randint(3, 6), "fumaca", 0.02
            ))

            if random.random() < 0.3:
                particulas.append(ParticulaAvancada(
                    jogador.centerx + offset_x,
                    jogador.bottom,
                    (255, 255, 200),
                    random.uniform(-2, 2), random.uniform(3, 6),
                    300, random.randint(1, 3), "faisca"
                ))


def criar_particulas_escudo_avancado(x, y, cor=(100, 200, 255)):
    """Cria partículas para escudo em qualquer posição"""
    if len(particulas) < 800:
        for i in range(3):
            angulo = random.uniform(0, 2 * math.pi)
            distancia = 35 + random.uniform(-8, 8)
            px = x + math.cos(angulo) * distancia
            py = y + math.sin(angulo) * distancia

            particulas.append(ParticulaAvancada(
                px, py, cor,
                random.uniform(-1, 1), random.uniform(-1, 1),
                1000, random.randint(2, 4), "cristal"
            ))


def criar_efeito_congelamento(x, y):
    """Cria efeito de congelamento em qualquer posição"""
    for _ in range(10):
        angulo = random.uniform(0, 2 * math.pi)
        distancia = random.uniform(0, 40)
        px = x + math.cos(angulo) * distancia
        py = y + math.sin(angulo) * distancia

        particulas.append(ParticulaAvancada(
            px, py, (100, 200, 255),
            random.uniform(-1, 1), random.uniform(-1, 1),
            1000, random.uniform(2, 4), "cristal"
        ))

    # Efeito de brilho azul
    efeitos.criar_brilho(x, y, (100, 200, 255), 30, 500, 0.8)


def criar_particulas_portal(x, y):
    """Cria partículas para portal"""
    for _ in range(5):
        angulo = random.uniform(0, 2 * math.pi)
        distancia = random.uniform(20, 40)
        px = x + math.cos(angulo) * distancia
        py = y + math.sin(angulo) * distancia

        particulas.append(ParticulaAvancada(
            px, py, (100, 200, 255),
            (x - px) * 0.1, (y - py) * 0.1,
            1500, random.uniform(2, 5), "estrela"
        ))


def criar_particulas_laser(x, y, cor=(255, 50, 50), quantidade=15):
    """Cria partículas especiais para efeitos de laser"""
    for _ in range(quantidade):
        offset_x = random.uniform(-10, 10)
        offset_y = random.uniform(-5, 5)

        particulas.append(ParticulaAvancada(
            x + offset_x, y + offset_y, cor,
            random.uniform(-2, 2), random.uniform(-1, 1),
            800, random.uniform(2, 4), "laser"
        ))


# == SISTEMA DE FUNDO DINÂMICO SUPER AVANÇADO ==
class FundoEstelar:
    def __init__(self):
        self.estrelas = []
        self.inicializar_estrelas()

    def inicializar_estrelas(self):
        for _ in range(150):
            self.estrelas.append({
                'x': random.randint(0, largura),
                'y': random.randint(0, altura),
                'velocidade': random.uniform(0.1, 0.8),
                'tamanho': random.uniform(0.3, 2.5),
                'brilho': random.randint(100, 255),
                'piscar_vel': random.uniform(0.005, 0.03),
                'cor': (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
            })

    def atualizar(self):
        tempo_atual = pygame.time.get_ticks()

        for estrela in self.estrelas:
            estrela['y'] += estrela['velocidade']
            if estrela['y'] > altura:
                estrela['y'] = 0
                estrela['x'] = random.randint(0, largura)

            estrela['brilho'] = 150 + int(105 * abs(math.sin(tempo_atual * estrela['piscar_vel'])))

    def desenhar(self, surface):
        # Desenhar estrelas
        for estrela in self.estrelas:
            brilho = estrela['brilho']
            cor_estrela = (
                min(255, estrela['cor'][0] * brilho // 255),
                min(255, estrela['cor'][1] * brilho // 255),
                min(255, estrela['cor'][2] * brilho // 255)
            )

            pygame.draw.circle(surface, cor_estrela,
                               (int(estrela['x']), int(estrela['y'])),
                               estrela['tamanho'])


fundo_estelar = FundoEstelar()


# == CARREGAMENTO DE IMAGENS COM FALLBACK ==
def carregar_imagem_ou_criar(nome_arquivo, escala, cor_fallback=None):
    if caminho_imagens:
        caminho_completo = os.path.join(caminho_imagens, nome_arquivo)
        if os.path.exists(caminho_completo):
            try:
                img = pygame.image.load(caminho_completo)
                img = img.convert_alpha()
                return pygame.transform.scale(img, escala)
            except pygame.error as e:
                print(f"Erro ao carregar {nome_arquivo}: {e}")

    surf = pygame.Surface(escala, pygame.SRCALPHA)
    if cor_fallback:
        surf.fill(cor_fallback)
    else:
        cores = {
            'nave': (100, 150, 255),
            'meteoro': (150, 100, 50),
            'projetil': (255, 255, 100),
            'boss': (255, 50, 50),
            'coracao': (255, 100, 100),
            'portal': (100, 255, 200),
            'mega': (200, 50, 150),
            'drone': (150, 50, 50)
        }

        for chave, cor in cores.items():
            if chave in nome_arquivo.lower():
                surf.fill(cor)
                break
        else:
            surf.fill((random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))

    pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 2)
    fonte_fallback = pygame.font.Font(None, 20)
    texto = fonte_fallback.render(nome_arquivo[:3], True, (255, 255, 255))
    surf.blit(texto, (5, 5))

    return surf


# == CARREGAR TODAS AS IMAGENS ==
naves_imagens = []
naves_arquivos = ["nave_azulroxo3.gif", "nave_laranja3.gif", "nave_rosa2.gif",
                  "nave_verde3.gif", "nave_vermelho1.gif", "nave_vermelho3.gif"]

for nave_arquivo in naves_arquivos:
    img = carregar_imagem_ou_criar(nave_arquivo, (40, 40), (100, 150, 255))
    naves_imagens.append(img)

# Adicionar naves de administrador
nave_gabriel_img = carregar_imagem_ou_criar("nave_gabriel.png", (40, 40), (0, 255, 0))
nave_paulo_img = carregar_imagem_ou_criar("nave_paulo.png", (40, 40), (255, 0, 0))
nave_vitor_img = carregar_imagem_ou_criar("nave_vitor.png", (40, 40), (0, 0, 255))

# Adicionar as naves admin à lista de naves
naves_imagens.append(nave_gabriel_img)
naves_imagens.append(nave_paulo_img)
naves_imagens.append(nave_vitor_img)

meteoro_img = carregar_imagem_ou_criar("meteoro.gif", (60, 60), (150, 100, 50))
meteoro_grande_img = carregar_imagem_ou_criar("meteoro.gif", (80, 80), (150, 100, 50))
meteoro_enorme_img = carregar_imagem_ou_criar("meteoro.gif", (100, 100), (120, 80, 40))
projetil_img = carregar_imagem_ou_criar("projetil_base.gif", (15, 25), (255, 255, 100))
projetil_boss_img = carregar_imagem_ou_criar("projetil_boss.gif", (15, 25), (255, 100, 100))
boss_img = carregar_imagem_ou_criar("nave_boss.gif", (70, 70), (255, 50, 50))
boss_menor_img = carregar_imagem_ou_criar("nave_boss.gif", (50, 50), (200, 50, 50))
mega_boss_img = carregar_imagem_ou_criar("mega_boss_img.png", (90, 90), (200, 50, 150))
boss_gabriel_img = carregar_imagem_ou_criar("boss.gabriel.png", (150, 150), (255, 0, 255))
drone_img = carregar_imagem_ou_criar("nave_boss.gif", (30, 30), (150, 50, 50))  # CORRIGIDO: drone.boss.png -> nave_boss.gif
coracao_img = carregar_imagem_ou_criar("coracao.png", (30, 30), (255, 100, 100))
portal_img = carregar_imagem_ou_criar("portal.gif", (60, 60), (100, 255, 200))

# == SISTEMA DE PROGRESSÃO E DESBLOQUEIO ==
fonte = pygame.font.Font(None, 36)
fonte_pequena = pygame.font.Font(None, 24)
pontuacao = 0
pontuacao_para_proxima_nave = 0
naves_desbloqueadas = [True] + [False] * 8  # Agora são 9 naves no total
pontuacao_necessaria_por_nave = [0, 1500, 2000, 2500, 3000, 3500, 0, 0, 0]  # Naves admin não precisam de pontuação
nave_selecionada = 0

# == SISTEMA DE HABILIDADES POR NAVE ==
habilidades_naves = [
    "congelar",  # Nave 1 - Congelamento
    "escudo",  # Nave 2 - Escudo de plasma
    "velocidade",  # Nave 3 - Velocidade dupla
    "tiro_triplo",  # Nave 4 - Tiro triplo
    "lazer",  # Nave 5 - Lazer/Kamehameha
    "teleporte",  # Nave 6 - Teleporte
    "admin",  # Nave 7 - Gabriel (Admin)
    "admin",  # Nave 8 - Paulo (Admin)
    "admin"  # Nave 9 - Vitor (Admin)
]

# == SISTEMA DE TEMPO E NÍVEIS ==
tempo_inicio = pygame.time.get_ticks()
tempo_atual_jogo = 0
nivel = 1
velocidade_base = 3
velocidade_maxima_meteoros = 8  # REDUZIDO: Velocidade máxima dos meteoros (nível 15)
vida_jogador = 3
max_vida = 5
max_vida_admin = 10  # Vida máxima para naves admin

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

# == SISTEMA DE HABILIDADES ESPECIAIS ==
habilidade_ativa = False
habilidade_tempo_fim = 0
habilidade_cooldown = 0

escudo_ativo = False
escudo_tempo_fim = 0
tiro_triplo_ativo = False
tiro_triplo_tempo_fim = 0
velocidade_dupla_ativa = False
velocidade_dupla_tempo_fim = 0
congelar_ativado = False
congelar_tempo_fim = 0
teleporte_ativado = False
teleporte_cooldown = 0

# == VARIÁVEIS PARA NAVES ADMIN ==
habilidades_admin_ativas = False  # Controla se ESCUDO+VELOCIDADE+TIRO TRIPLO estão ativos
municao_infinita_ativa = False  # Controla se munição infinita está ativa

# == SISTEMA DE BOSS MÚLTIPLO ==
bosses = []
drones = []
boss_ativo = False
ultimo_boss_derrotado = 0
boss_spawn_nivel = 0
nivel_maximo_alcancado = 1
bosses_derrotados = []  # Lista para controlar quais bosses já foram derrotados

# == SISTEMA DE SENHA PARA NAVES ADMIN ==
senhas_admin = {
    "gabriel": "Gabriel0312",
    "paulo": "Paulo12",
    "vitor": "Victor12"
}

senha_atual = ""
digitando_senha = False
nave_admin_solicitada = None

# == SISTEMA DE ACELERAÇÃO DE METEOROS ==
fator_aceleracao_meteoros = 0.0005  # REDUZIDO: Quanto os meteoros aceleram por frame
tempo_jogo_inicio = pygame.time.get_ticks()

# == SISTEMA DE SALVAMENTO ==
progresso_salvo = None

# == VARIÁVEIS GLOBAIS DO JOGO ==
jogador = pygame.Rect(180, 500, 40, 40)
velocidade_jogador = 5
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

# == EFEITOS ESPECIAIS ==
portal_rotacao = 0


# == CLASSE DRONE ==
class Drone:
    def __init__(self, x, y, lado):
        self.x = x
        self.y = y
        self.lado = lado  # 'esquerda' ou 'direita'
        self.rect = pygame.Rect(x, y, 30, 30)
        self.vida = 3
        self.velocidade = 1.5
        self.escudo_ativado = False
        self.escudo_tempo_fim = 0
        self.ultimo_escudo = pygame.time.get_ticks()
        self.escudo_cooldown = 8000
        self.congelado = False
        self.congelado_tempo = 0

    def atualizar(self, jogador_rect):
        if self.congelado:
            return

        tempo_atual = pygame.time.get_ticks()
        if not self.escudo_ativado and tempo_atual - self.ultimo_escudo > self.escudo_cooldown:
            self.escudo_ativado = True
            self.escudo_tempo_fim = tempo_atual + 3000

        if self.escudo_ativado and tempo_atual > self.escudo_tempo_fim:
            self.escudo_ativado = False
            self.ultimo_escudo = tempo_atual

        if self.lado == 'esquerda':
            alvo_x = jogador_rect.centerx - 60
            alvo_y = jogador_rect.centery - 40
        else:
            alvo_x = jogador_rect.centerx + 60
            alvo_y = jogador_rect.centery - 40

        dx = alvo_x - self.rect.centerx
        dy = alvo_y - self.rect.centery
        distancia = math.sqrt(dx * dx + dy * dy)

        if distancia > 0:
            self.rect.x += (dx / distancia) * self.velocidade
            self.rect.y += (dy / distancia) * self.velocidade

    def levar_dano(self, dano):
        if self.escudo_ativado:
            return False

        self.vida -= dano
        return self.vida <= 0

    def desenhar_escudo(self, surface):
        if self.escudo_ativado:
            tempo_atual = pygame.time.get_ticks()
            raio = 25 + int(3 * math.sin(tempo_atual * 0.01))

            for i in range(3):
                alpha = 100 - i * 30
                surf_escudo = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
                cor_escudo = (255, 50, 50, alpha)
                pygame.draw.circle(surf_escudo, cor_escudo, (raio, raio), raio - i * 5, 3)
                surface.blit(surf_escudo, (self.rect.centerx - raio, self.rect.centery - raio))

            criar_particulas_escudo_avancado(self.rect.centerx, self.rect.centery, (255, 50, 50))


# == CLASSE BOSS NIVEL 15 ==
class BossNivel15:
    def __init__(self):
        self.vida_maxima = 200  # Vida suficiente para resistir a 4 lasers (50 de dano cada)
        self.vida = self.vida_maxima
        self.largura = 120
        self.altura = 120
        self.rect = pygame.Rect(largura // 2 - self.largura // 2, 50, self.largura, self.altura)
        self.velocidade = 1.5
        self.intervalo_tiros = 1000
        self.tiros_por_cycle = 3
        self.cycles_completos = 0
        self.ultimo_tiro = pygame.time.get_ticks()
        self.ultimo_laser = 0
        self.laser_cooldown = 5000
        self.laser_ativado = False
        self.laser_tempo_inicio = 0
        self.laser_duracao = 2000
        self.escudo_ativado = False
        self.escudo_tempo_fim = 0
        self.escudo_duracao = 3000
        self.bosses_gemeos = []  # Para os bosses do nível 10 que aparecem na metade da vida
        self.gemeos_ativados = False
        self.congelado = False
        self.congelado_tempo = 0

    def atualizar(self, jogador_rect):
        if self.congelado:
            return

        tempo_atual = pygame.time.get_ticks()

        # Movimento
        if self.rect.centerx < jogador_rect.centerx:
            self.rect.x += min(self.velocidade, jogador_rect.centerx - self.rect.centerx)
        elif self.rect.centerx > jogador_rect.centerx:
            self.rect.x -= min(self.velocidade, self.rect.centerx - jogador_rect.centerx)

        # Limites
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > largura:
            self.rect.right = largura

        # Ativar gemeos na metade da vida
        if not self.gemeos_ativados and self.vida <= self.vida_maxima // 2:
            self.ativar_gemeos()

        # Atualizar gemeos
        for gemeo in self.bosses_gemeos[:]:
            gemeo.atualizar(jogador_rect)

        # Sistema de ataques
        if not self.laser_ativado and tempo_atual - self.ultimo_tiro > self.intervalo_tiros:
            if self.cycles_completos < 5:
                # Ciclo de tiros normais
                self.atirar()
                self.cycles_completos += 1
                self.ultimo_tiro = tempo_atual
            else:
                # Após 5 ciclos, ativa laser
                self.laser_ativado = True
                self.laser_tempo_inicio = tempo_atual
                self.cycles_completos = 0

        # Gerenciar laser
        if self.laser_ativado and tempo_atual - self.laser_tempo_inicio > self.laser_duracao:
            self.laser_ativado = False
            self.ultimo_laser = tempo_atual
            # Ativa escudo após laser
            self.escudo_ativado = True
            self.escudo_tempo_fim = tempo_atual + self.escudo_duracao

        # Gerenciar escudo
        if self.escudo_ativado and tempo_atual > self.escudo_tempo_fim:
            self.escudo_ativado = False

    def ativar_gemeos(self):
        """Ativa os bosses gêmeos do nível 10"""
        self.gemeos_ativados = True
        # Boss à esquerda
        boss_esquerda = Boss(10, largura // 4, usar_lazer=False, tipo_boss=2)
        boss_esquerda.rect = pygame.Rect(largura // 4 - 35, 100, 70, 70)
        # Boss à direita
        boss_direita = Boss(10, 3 * largura // 4, usar_lazer=True, tipo_boss=2)
        boss_direita.rect = pygame.Rect(3 * largura // 4 - 35, 100, 70, 70)

        self.bosses_gemeos.append(boss_esquerda)
        self.bosses_gemeos.append(boss_direita)

    def atirar(self):
        """Dispara 3 tiros normais"""
        for i in range(self.tiros_por_cycle):
            offset = (i - 1) * 20  # -20, 0, 20
            x = self.rect.centerx - 5 + offset
            y = self.rect.bottom

            projeteis_boss.append({
                "rect": pygame.Rect(x, y, 10, 20),
                "velocidade_x": 0,
                "velocidade_y": 7
            })

    def levar_dano(self, dano):
        if self.escudo_ativado:
            return False

        self.vida -= dano
        return self.vida <= 0

    def desenhar_barra_vida(self, surface):
        barra_largura = 150
        barra_altura = 12
        x = self.rect.centerx - barra_largura // 2
        y = self.rect.top - 25

        pygame.draw.rect(surface, (255, 0, 0), (x, y, barra_largura, barra_altura))
        vida_largura = int((self.vida / self.vida_maxima) * barra_largura)
        pygame.draw.rect(surface, (255, 255, 0), (x, y, vida_largura, barra_altura))

    def desenhar_laser(self, surface, jogador_rect):
        if not self.laser_ativado:
            return False

        tempo_atual = pygame.time.get_ticks()
        tempo_decorrido_laser = tempo_atual - self.laser_tempo_inicio

        if tempo_decorrido_laser > self.laser_duracao:
            return False

        # Efeito de piscagem no final
        if tempo_decorrido_laser > self.laser_duracao * 0.7:
            if int(tempo_atual / 100) % 2 == 0:
                return False

        # Laser do boss nível 15
        largura_lazer = 30
        start_pos = (self.rect.centerx, self.rect.bottom)
        end_pos = (self.rect.centerx, altura)

        # Núcleo principal
        cor_nucleo = (255, 0, 0)
        pygame.draw.line(surface, cor_nucleo, start_pos, end_pos, largura_lazer)

        # Camadas de brilho
        for i in range(4):
            cor_brilho = (255, 100 - i * 25, 100 - i * 25)
            largura_camada = max(3, largura_lazer - i * 6)
            pygame.draw.line(surface, cor_brilho, start_pos, end_pos, largura_camada)

        # Partículas de energia
        for _ in range(25):
            x = self.rect.centerx + random.randint(-15, 15)
            y = random.randint(self.rect.bottom, altura)
            cor_particula = (255, 255, 200)
            pygame.draw.circle(surface, cor_particula, (x, y), random.randint(1, 4))

        # Efeito de distorção
        for i in range(2):
            surf_borda = pygame.Surface((largura_lazer + 15, altura - self.rect.bottom), pygame.SRCALPHA)
            cor_borda = (255, 150, 150, 100)
            pygame.draw.rect(surf_borda, cor_borda, (0, 0, largura_lazer + 15, altura - self.rect.bottom), 2)
            surface.blit(surf_borda, (self.rect.centerx - (largura_lazer + 15) // 2, self.rect.bottom))

        # Criar rastro visual
        efeitos.criar_rastro_laser(start_pos, end_pos, (255, 100, 100), 20, 500)

        # Criar partículas de laser
        for _ in range(15):
            criar_particulas_laser(self.rect.centerx + random.randint(-12, 12),
                                   self.rect.bottom + random.randint(0, 100))

        # Área de colisão do laser
        lazer_rect = pygame.Rect(
            self.rect.centerx - largura_lazer // 2,
            self.rect.bottom,
            largura_lazer,
            altura - self.rect.bottom
        )

        # Verificar colisão com jogador
        if lazer_rect.colliderect(jogador_rect):
            return True
        return False

    def desenhar_escudo(self, surface):
        if self.escudo_ativado:
            tempo_atual = pygame.time.get_ticks()
            raio = 65
            raio += int(8 * math.sin(tempo_atual * 0.01))

            for i in range(4):
                alpha = 120 - i * 30
                surf_escudo = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
                cor_escudo = (255, 50, 50, alpha)  # Escudo vermelho
                pygame.draw.circle(surf_escudo, cor_escudo, (raio, raio), raio - i * 8, 4)
                surface.blit(surf_escudo, (self.rect.centerx - raio, self.rect.centery - raio))

            # Partículas de escudo vermelho
            for _ in range(5):
                angulo = random.uniform(0, 2 * math.pi)
                distancia = random.uniform(50, 65)
                px = self.rect.centerx + math.cos(angulo) * distancia
                py = self.rect.centery + math.sin(angulo) * distancia
                criar_particulas_escudo_avancado(px, py, (255, 50, 50))


# == CLASSE BOSS GABRIEL (NIVEL 20) ==
class BossGabriel:
    def __init__(self):
        self.vida_maxima = 300
        self.vida = self.vida_maxima
        self.largura = 150
        self.altura = 150
        self.rect = pygame.Rect(largura // 2 - self.largura // 2, 30, self.largura, self.altura)
        self.velocidade = 2
        self.intervalo_tiros = 800
        self.ultimo_tiro = pygame.time.get_ticks()
        self.ultimo_laser = 0
        self.laser_cooldown = 4000
        self.laser_ativado = False
        self.laser_tempo_inicio = 0
        self.laser_duracao = 1500
        self.escudo_ativado = False
        self.escudo_tempo_fim = 0
        self.escudo_duracao = 2500
        self.ataque_especial_ativado = False
        self.ataque_especial_tempo = 0
        self.ataque_especial_duracao = 5000
        self.congelado = False
        self.congelado_tempo = 0
        self.phase = 1
        self.rotacao = 0

    def atualizar(self, jogador_rect):
        if self.congelado:
            return

        tempo_atual = pygame.time.get_ticks()
        self.rotacao += 1

        # Mudança de fase na metade da vida
        if self.vida <= self.vida_maxima // 2 and self.phase == 1:
            self.phase = 2
            self.velocidade = 2.5
            self.intervalo_tiros = 600

        # Movimento mais agressivo
        dx = jogador_rect.centerx - self.rect.centerx
        dy = jogador_rect.centery - self.rect.centery
        distancia = math.sqrt(dx * dx + dy * dy)

        if distancia > 0:
            self.rect.x += (dx / distancia) * self.velocidade
            self.rect.y += (dy / distancia) * self.velocidade * 0.5

        # Limites
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > largura:
            self.rect.right = largura
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > altura // 3:
            self.rect.bottom = altura // 3

        # Sistema de ataques
        if not self.laser_ativado and not self.ataque_especial_ativado:
            if tempo_atual - self.ultimo_tiro > self.intervalo_tiros:
                self.atirar()
                self.ultimo_tiro = tempo_atual

            # Ativar laser periodicamente
            if tempo_atual - self.ultimo_laser > self.laser_cooldown:
                self.laser_ativado = True
                self.laser_tempo_inicio = tempo_atual
                self.ultimo_laser = tempo_atual

        # Ataque especial na fase 2
        if self.phase == 2 and not self.ataque_especial_ativado and random.random() < 0.01:
            self.ataque_especial_ativado = True
            self.ataque_especial_tempo = tempo_atual

        # Gerenciar laser
        if self.laser_ativado and tempo_atual - self.laser_tempo_inicio > self.laser_duracao:
            self.laser_ativado = False
            self.escudo_ativado = True
            self.escudo_tempo_fim = tempo_atual + self.escudo_duracao

        # Gerenciar ataque especial
        if self.ataque_especial_ativado and tempo_atual - self.ataque_especial_tempo > self.ataque_especial_duracao:
            self.ataque_especial_ativado = False

        # Gerenciar escudo
        if self.escudo_ativado and tempo_atual > self.escudo_tempo_fim:
            self.escudo_ativado = False

    def atirar(self):
        """Dispara padrões de tiros complexos"""
        if self.phase == 1:
            # Fase 1: tiros em leque
            for i in range(5):
                angulo = math.radians(-30 + i * 15)
                velocidade_x = math.sin(angulo) * 4
                velocidade_y = math.cos(angulo) * 7

                projeteis_boss.append({
                    "rect": pygame.Rect(self.rect.centerx - 5, self.rect.bottom, 10, 20),
                    "velocidade_x": velocidade_x,
                    "velocidade_y": velocidade_y
                })
        else:
            # Fase 2: tiros espiralados
            for i in range(8):
                angulo = math.radians(self.rotacao + i * 45)
                velocidade_x = math.sin(angulo) * 5
                velocidade_y = math.cos(angulo) * 6

                projeteis_boss.append({
                    "rect": pygame.Rect(self.rect.centerx - 5, self.rect.centery, 10, 20),
                    "velocidade_x": velocidade_x,
                    "velocidade_y": velocidade_y
                })

    def levar_dano(self, dano):
        if self.escudo_ativado:
            return False

        self.vida -= dano
        return self.vida <= 0

    def desenhar_barra_vida(self, surface):
        barra_largura = 180
        barra_altura = 15
        x = self.rect.centerx - barra_largura // 2
        y = self.rect.top - 30

        pygame.draw.rect(surface, (255, 0, 0), (x, y, barra_largura, barra_altura))
        vida_largura = int((self.vida / self.vida_maxima) * barra_largura)
        cor_vida = (0, 255, 0) if self.phase == 1 else (255, 255, 0)
        pygame.draw.rect(surface, cor_vida, (x, y, vida_largura, barra_altura))

    def desenhar_laser(self, surface, jogador_rect):
        if not self.laser_ativado:
            return False

        tempo_atual = pygame.time.get_ticks()
        tempo_decorrido_laser = tempo_atual - self.laser_tempo_inicio

        if tempo_decorrido_laser > self.laser_duracao:
            return False

        # Laser múltiplo do boss Gabriel
        for i in range(3):
            offset = (i - 1) * 40  # -40, 0, 40
            start_pos = (self.rect.centerx + offset, self.rect.bottom)
            end_pos = (self.rect.centerx + offset, altura)

            largura_lazer = 20

            # Núcleo principal
            cor_nucleo = (255, 0, 255) if self.phase == 2 else (0, 255, 255)
            pygame.draw.line(surface, cor_nucleo, start_pos, end_pos, largura_lazer)

            # Camadas de brilho
            for j in range(3):
                cor_brilho = (255, 100, 255, 150) if self.phase == 2 else (100, 255, 255, 150)
                largura_camada = max(3, largura_lazer - j * 5)
                pygame.draw.line(surface, cor_brilho, start_pos, end_pos, largura_camada)

            # Partículas de energia
            for _ in range(10):
                x = self.rect.centerx + offset + random.randint(-10, 10)
                y = random.randint(self.rect.bottom, altura)
                cor_particula = (255, 255, 255)
                pygame.draw.circle(surface, cor_particula, (x, y), random.randint(1, 3))

            # Área de colisão do laser
            lazer_rect = pygame.Rect(
                self.rect.centerx + offset - largura_lazer // 2,
                self.rect.bottom,
                largura_lazer,
                altura - self.rect.bottom
            )

            # Verificar colisão com jogador
            if lazer_rect.colliderect(jogador_rect):
                return True

        return False

    def desenhar_ataque_especial(self, surface, jogador_rect):
        if not self.ataque_especial_ativado:
            return False

        tempo_atual = pygame.time.get_ticks()
        progresso = (tempo_atual - self.ataque_especial_tempo) / self.ataque_especial_duracao

        # Campo de força pulsante
        raio = int(100 + 50 * math.sin(tempo_atual * 0.01))
        for i in range(3):
            alpha = 100 - i * 30
            surf_campo = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
            cor_campo = (255, 0, 255, alpha)
            pygame.draw.circle(surf_campo, cor_campo, (raio, raio), raio - i * 15, 5)
            surface.blit(surf_campo, (self.rect.centerx - raio, self.rect.centery - raio))

        # Raios elétricos
        for _ in range(10):
            start_x = self.rect.centerx + random.randint(-60, 60)
            start_y = self.rect.centery + random.randint(-60, 60)
            end_x = random.randint(0, largura)
            end_y = random.randint(0, altura)

            pygame.draw.line(surface, (200, 100, 255), (start_x, start_y), (end_x, end_y), 2)

        # Verificar colisão com campo de força
        campo_rect = pygame.Rect(self.rect.centerx - raio, self.rect.centery - raio, raio * 2, raio * 2)
        if campo_rect.colliderect(jogador_rect):
            return True

        return False

    def desenhar_escudo(self, surface):
        if self.escudo_ativado:
            tempo_atual = pygame.time.get_ticks()
            raio = 80
            raio += int(10 * math.sin(tempo_atual * 0.01))

            for i in range(5):
                alpha = 150 - i * 30
                surf_escudo = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
                cor_escudo = (0, 255, 255, alpha) if self.phase == 1 else (255, 0, 255, alpha)
                pygame.draw.circle(surf_escudo, cor_escudo, (raio, raio), raio - i * 10, 6)
                surface.blit(surf_escudo, (self.rect.centerx - raio, self.rect.centery - raio))


# == CLASSE BOSS MELHORADA (ORIGINAL) ==
class Boss:
    def __init__(self, nivel_boss, x, usar_lazer=False, tipo_boss=1):
        self.nivel_boss = nivel_boss
        self.usar_lazer = usar_lazer
        self.tipo_boss = tipo_boss
        self.vida_maxima = 80 + (nivel_boss // 5) * 40
        self.vida = self.vida_maxima

        if tipo_boss == 3:
            self.largura = 90
            self.altura = 90
        else:
            self.largura = 70
            self.altura = 70

        self.rect = pygame.Rect(x, 50, self.largura, self.altura)

        if tipo_boss == 1:
            self.velocidade = 2 + (nivel_boss // 5) * 0.5
            self.intervalo_tiros = max(400, 1000 - (nivel_boss // 5) * 120)
            self.tiros_simultaneos = 1 + (nivel_boss // 5)
            self.lazer_duracao = 2000
        elif tipo_boss == 2:
            self.velocidade = 1.5 + (nivel_boss // 5) * 0.3
            self.intervalo_tiros = max(300, 800 - (nivel_boss // 5) * 80)
            self.tiros_simultaneos = 2 + (nivel_boss // 5)
            self.lazer_duracao = 1500
        else:
            self.velocidade = 1 + (nivel_boss // 5) * 0.2
            self.intervalo_tiros = max(400, 900 - (nivel_boss // 5) * 100)
            self.tiros_simultaneos = 2 + (nivel_boss // 5)
            self.lazer_duracao = 2500
            self.ultimo_drone = pygame.time.get_ticks()
            self.intervalo_drones = 15000

        self.ultimo_tiro = pygame.time.get_ticks()
        self.lazer_ativado = False
        self.lazer_tempo_inicio = 0
        self.ultimo_lazer = 0
        self.lazer_cooldown = 8000
        self.congelado = False
        self.congelado_tempo = 0
        self.escudo_ativado = False
        self.escudo_tempo_fim = 0
        self.modo_agressivo = False
        self.ultimo_escudo = pygame.time.get_ticks()
        self.escudo_cooldown = 10000

    def atualizar(self, jogador_rect):
        if self.congelado:
            return

        if self.tipo_boss == 1:
            if self.rect.centerx < jogador_rect.centerx:
                self.rect.x += min(self.velocidade, jogador_rect.centerx - self.rect.centerx)
            elif self.rect.centerx > jogador_rect.centerx:
                self.rect.x -= min(self.velocidade, self.rect.centerx - jogador_rect.centerx)
        elif self.tipo_boss == 2:
            if not self.modo_agressivo:
                if self.rect.centerx < jogador_rect.centerx:
                    self.rect.x += min(self.velocidade, jogador_rect.centerx - self.rect.centerx)
                elif self.rect.centerx > jogador_rect.centerx:
                    self.rect.x -= min(self.velocidade, self.rect.centerx - jogador_rect.centerx)

                if random.random() < 0.01:
                    self.modo_agressivo = True
                    self.escudo_ativado = True
                    self.escudo_tempo_fim = pygame.time.get_ticks() + 3000
            else:
                dx = jogador_rect.centerx - self.rect.centerx
                dy = jogador_rect.centery - self.rect.centery
                distancia = math.sqrt(dx * dx + dy * dy)

                if distancia > 0:
                    self.rect.x += (dx / distancia) * self.velocidade * 0.7
                    self.rect.y += (dy / distancia) * self.velocidade * 0.7

                if pygame.time.get_ticks() > self.escudo_tempo_fim:
                    self.modo_agressivo = False
                    self.escudo_ativado = False
                    self.ultimo_escudo = pygame.time.get_ticks()
        else:
            if self.rect.centerx < jogador_rect.centerx:
                self.rect.x += min(self.velocidade, jogador_rect.centerx - self.rect.centerx)
            elif self.rect.centerx > jogador_rect.centerx:
                self.rect.x -= min(self.velocidade, self.rect.centerx - jogador_rect.centerx)

            tempo_atual = pygame.time.get_ticks()
            if tempo_atual - self.ultimo_drone > self.intervalo_drones and len(drones) < 4:
                drones.append(Drone(self.rect.left - 40, self.rect.centery, 'esquerda'))
                drones.append(Drone(self.rect.right + 10, self.rect.centery, 'direita'))
                self.ultimo_drone = tempo_atual

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > largura:
            self.rect.right = largura
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > altura // 2:
            self.rect.bottom = altura // 2

    def pode_atirar(self):
        if self.congelado:
            return False
        tempo_atual = pygame.time.get_ticks()
        return tempo_atual - self.ultimo_tiro > self.intervalo_tiros

    def pode_usar_lazer(self):
        if not self.usar_lazer or self.congelado:
            return False
        tempo_atual = pygame.time.get_ticks()
        return tempo_atual - self.ultimo_lazer > self.lazer_cooldown

    def ativar_lazer(self):
        if self.pode_usar_lazer():
            self.lazer_ativado = True
            self.lazer_tempo_inicio = pygame.time.get_ticks()
            self.ultimo_lazer = pygame.time.get_ticks()
            return True
        return False

    def atirar(self, jogador_rect):
        self.ultimo_tiro = pygame.time.get_ticks()
        projeteis_boss_local = []

        if self.tiros_simultaneos == 1:
            x = self.rect.centerx - 5
            y = self.rect.bottom
            projeteis_boss_local.append({
                "rect": pygame.Rect(x, y, 10, 20),
                "velocidade_x": 0,
                "velocidade_y": 7
            })
        else:
            for i in range(self.tiros_simultaneos):
                offset = (i - (self.tiros_simultaneos - 1) / 2) * 15
                x = self.rect.centerx - 5 + offset
                y = self.rect.bottom
                projeteis_boss_local.append({
                    "rect": pygame.Rect(x, y, 10, 20),
                    "velocidade_x": 0,
                    "velocidade_y": 7
                })
        return projeteis_boss_local

    def levar_dano(self, dano):
        if self.escudo_ativado:
            return False

        self.vida -= dano
        return self.vida <= 0

    def desenhar_barra_vida(self, surface):
        barra_largura = 100 if self.tipo_boss == 3 else 80
        barra_altura = 10 if self.tipo_boss == 3 else 8
        x = self.rect.centerx - barra_largura // 2
        y = self.rect.top - 20 if self.tipo_boss == 3 else self.rect.top - 15

        pygame.draw.rect(surface, (255, 0, 0), (x, y, barra_largura, barra_altura))
        vida_largura = int((self.vida / self.vida_maxima) * barra_largura)

        if self.tipo_boss == 1:
            cor_vida = (0, 255, 0) if self.usar_lazer else (255, 255, 0)
        elif self.tipo_boss == 2:
            cor_vida = (255, 100, 0)
        else:
            cor_vida = (200, 50, 150)

        pygame.draw.rect(surface, cor_vida, (x, y, vida_largura, barra_altura))

    def desenhar_laser(self, surface, jogador_rect):
        if not self.lazer_ativado:
            return False

        tempo_atual = pygame.time.get_ticks()
        tempo_decorrido_laser = tempo_atual - self.lazer_tempo_inicio

        if tempo_decorrido_laser > self.lazer_duracao:
            self.lazer_ativado = False
            return False

        if tempo_decorrido_laser > self.lazer_duracao * 0.7:
            if int(tempo_atual / 100) % 2 == 0:
                return False

        largura_lazer = 25
        start_pos = (self.rect.centerx, self.rect.bottom)
        end_pos = (self.rect.centerx, altura)

        cor_nucleo = (255, 0, 0)
        pygame.draw.line(surface, cor_nucleo, start_pos, end_pos, largura_lazer)

        for i in range(4):
            cor_brilho = (255, 100 - i * 25, 100 - i * 25)
            largura_camada = max(3, largura_lazer - i * 6)
            pygame.draw.line(surface, cor_brilho, start_pos, end_pos, largura_camada)

        for _ in range(20):
            x = self.rect.centerx + random.randint(-12, 12)
            y = random.randint(self.rect.bottom, altura)
            cor_particula = (255, 255, 200)
            pygame.draw.circle(surface, cor_particula, (x, y), random.randint(1, 3))

        for i in range(2):
            surf_borda = pygame.Surface((largura_lazer + 10, altura - self.rect.bottom), pygame.SRCALPHA)
            cor_borda = (255, 150, 150, 100)
            pygame.draw.rect(surf_borda, cor_borda, (0, 0, largura_lazer + 10, altura - self.rect.bottom), 2)
            surface.blit(surf_borda, (self.rect.centerx - (largura_lazer + 10) // 2, self.rect.bottom))

        efeitos.criar_rastro_laser(start_pos, end_pos, (255, 100, 100), 15, 500)

        for _ in range(10):
            criar_particulas_laser(self.rect.centerx + random.randint(-10, 10),
                                   self.rect.bottom + random.randint(0, 100))

        lazer_rect = pygame.Rect(
            self.rect.centerx - largura_lazer // 2,
            self.rect.bottom,
            largura_lazer,
            altura - self.rect.bottom
        )

        if lazer_rect.colliderect(jogador_rect):
            return True
        return False

    def desenhar_escudo(self, surface):
        if self.escudo_ativado:
            tempo_atual = pygame.time.get_ticks()
            raio = 45 if self.tipo_boss == 3 else 40
            raio += int(5 * math.sin(tempo_atual * 0.01))

            for i in range(3):
                alpha = 100 - i * 30
                surf_escudo = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
                cor_escudo = (0, 100 + i * 50, 255, alpha)
                pygame.draw.circle(surf_escudo, cor_escudo, (raio, raio), raio - i * 5, 3)
                surface.blit(surf_escudo, (self.rect.centerx - raio, self.rect.centery - raio))


# == SISTEMA DE SENHA PARA NAVES ADMIN ==
def mostrar_tela_senha(nave_admin):
    global digitando_senha, senha_atual, nave_admin_solicitada

    digitando_senha = True
    nave_admin_solicitada = nave_admin
    senha_atual = ""

    fonte_senha = pygame.font.Font(None, 32)

    while digitando_senha:
        tela.fill((0, 0, 40))
        fundo_estelar.desenhar(tela)

        # Textos da tela de senha
        texto_titulo = fonte.render(f"NAVE ADMIN {nave_admin.upper()}", True, (255, 255, 255))
        texto_instrucao = fonte_pequena.render("Digite a senha e pressione ENTER:", True, (200, 200, 200))
        texto_senha = fonte_senha.render(senha_atual, True, (255, 255, 255))
        texto_asteriscos = fonte_senha.render("*" * len(senha_atual), True, (255, 255, 255))

        tela.blit(texto_titulo, (largura // 2 - texto_titulo.get_width() // 2, altura // 3 - 50))
        tela.blit(texto_instrucao, (largura // 2 - texto_instrucao.get_width() // 2, altura // 3))
        tela.blit(texto_asteriscos, (largura // 2 - texto_asteriscos.get_width() // 2, altura // 2))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    # Verificar senha
                    if senha_atual == senhas_admin[nave_admin]:
                        # Senha correta - ativar nave admin
                        if nave_admin == "gabriel":
                            trocar_nave(7)
                        elif nave_admin == "paulo":
                            trocar_nave(8)
                            # Se for Paulo ou Vitor, spawnar boss nível 15 imediatamente
                            if not any(isinstance(boss, BossNivel15) for boss in bosses):
                                bosses.append(BossNivel15())
                                boss_ativo = True
                                print("BOSS NÍVEL 15 apareceu instantaneamente!")
                        elif nave_admin == "vitor":
                            trocar_nave(9)
                            # Se for Paulo ou Vitor, spawnar boss nível 15 imediatamente
                            if not any(isinstance(boss, BossNivel15) for boss in bosses):
                                bosses.append(BossNivel15())
                                boss_ativo = True
                                print("BOSS NÍVEL 15 apareceu instantaneamente!")
                        digitando_senha = False
                        return True
                    else:
                        # Senha incorreta
                        senha_atual = ""
                        texto_erro = fonte_pequena.render("Senha incorreta! Tente novamente.", True, (255, 0, 0))
                        tela.blit(texto_erro, (largura // 2 - texto_erro.get_width() // 2, altura // 2 + 50))
                        pygame.display.flip()
                        pygame.time.delay(1000)
                elif evento.key == pygame.K_ESCAPE:
                    digitando_senha = False
                    return False
                elif evento.key == pygame.K_BACKSPACE:
                    senha_atual = senha_atual[:-1]
                else:
                    # Adicionar caractere à senha (apenas letras e números)
                    if evento.unicode.isalnum() or evento.unicode in "!@#$%^&*()_-+=":
                        senha_atual += evento.unicode

    return False


# == SISTEMA DE ACELERAÇÃO DE METEOROS ==
def atualizar_velocidade_meteoros():
    """Atualiza a velocidade dos meteoros baseado no tempo de jogo"""
    global velocidade_base

    tempo_decorrido = (pygame.time.get_ticks() - tempo_jogo_inicio) / 1000  # Tempo em segundos
    nova_velocidade = velocidade_base + tempo_decorrido * fator_aceleracao_meteoros

    # CORREÇÃO: Limitar velocidade máxima (velocidade do nível 15)
    velocidade_base = min(nova_velocidade, velocidade_maxima_meteoros)

    # CORREÇÃO: Garantir que a velocidade não fique negativa
    velocidade_base = max(3, velocidade_base)


# == SISTEMA DE SALVAMENTO ==
def salvar_progresso():
    global pontuacao, nivel, naves_desbloqueadas, progresso_salvo, nivel_maximo_alcancado
    try:
        pontuacao_maxima_anterior = progresso_salvo.get('pontuacao_maxima', 0) if progresso_salvo else 0
        nivel_maximo_anterior = progresso_salvo.get('nivel_maximo', 0) if progresso_salvo else 0

        progresso = {
            'naves_desbloqueadas': naves_desbloqueadas,
            'pontuacao_maxima': max(pontuacao, pontuacao_maxima_anterior),
            'nivel_maximo': max(nivel, nivel_maximo_anterior, nivel_maximo_alcancado),
            'ultima_pontuacao': pontuacao
        }
        with open('progresso.json', 'w') as f:
            json.dump(progresso, f)
        print("Progresso salvo!")
    except (IOError, OSError, TypeError) as e:
        print(f"Erro ao salvar progresso: {e}")


def carregar_progresso():
    global naves_desbloqueadas, nivel_maximo_alcancado
    try:
        with open('progresso.json', 'r') as f:
            dados = json.load(f)
            naves_desbloqueadas = dados.get('naves_desbloqueadas', [True] + [False] * 8)
            nivel_maximo_alcancado = dados.get('nivel_maximo', 1)
            print("Progresso carregado com sucesso!")
            return dados
    except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
        print(f"Erro ao carregar progresso: {e}")
        return {'naves_desbloqueadas': [True] + [False] * 8, 'pontuacao_maxima': 0, 'nivel_maximo': 1}


# == FUNÇÃO CORRIGIDA: RESETAR HABILIDADES AO TROCAR DE NAVE ==
def resetar_habilidades_ao_trocar_nave():
    """Reseta todas as habilidades ao trocar de nave"""
    global escudo_ativo, velocidade_dupla_ativa, tiro_triplo_ativo, congelar_ativado
    global habilidades_admin_ativas, municao_infinita_ativa, vida_jogador, max_vida

    # Resetar todas as habilidades
    escudo_ativo = False
    velocidade_dupla_ativa = False
    tiro_triplo_ativo = False
    congelar_ativado = False
    habilidades_admin_ativas = False
    municao_infinita_ativa = False

    # Resetar vida para o máximo normal
    vida_jogador = max_vida

    # Descongelar todos os inimigos
    for meteoro in meteoros:
        meteoro["congelado"] = False
    for boss in bosses:
        boss.congelado = False
    for drone in drones:
        drone.congelado = False

    print("Habilidades resetadas ao trocar de nave!")


# == SISTEMA DE HABILIDADES POR NAVE ==
def ativar_habilidade():
    global habilidade_ativa, habilidade_tempo_fim, habilidade_cooldown
    global escudo_ativo, escudo_tempo_fim, velocidade_dupla_ativa, velocidade_dupla_tempo_fim
    global tiro_triplo_ativo, tiro_triplo_tempo_fim, congelar_ativado, congelar_tempo_fim
    global lazer_ativado, lazer_tempo_inicio, ultimo_lazer, teleporte_ativado, teleporte_cooldown
    global habilidades_admin_ativas, municao_infinita_ativa, vida_jogador, max_vida_admin

    tempo_atual = pygame.time.get_ticks()

    # Verificar se é uma nave admin
    is_nave_admin = nave_selecionada >= 6  # Naves 7, 8, 9 são admin

    if is_nave_admin:
        # Para naves admin, não há cooldown
        pass
    elif tempo_atual < habilidade_cooldown:
        tempo_restante = (habilidade_cooldown - tempo_atual) // 1000
        print(f"Habilidade em cooldown! Aguarde {tempo_restante} segundos.")
        return False

    habilidade = habilidades_naves[nave_selecionada]

    if is_nave_admin:
        # Lógica especial para naves admin
        if not habilidades_admin_ativas:
            # Primeiro H: Ativa ESCUDO + VELOCIDADE + TIRO TRIPLO + MUNIÇÃO INFINITA permanentemente
            escudo_ativo = True
            velocidade_dupla_ativa = True
            tiro_triplo_ativo = True
            municao_infinita_ativa = True
            habilidades_admin_ativas = True

            # Definir vida máxima para admin
            vida_jogador = max_vida_admin

            print("MODO ADMIN ATIVADO: Escudo, Velocidade, Tiro Triplo e Munição Infinita!")
            return True
        else:
            # Segundo H e subsequentes: Ativa congelar ou teleporte (sem cooldown)
            if random.random() < 0.5:
                # Ativar congelamento
                congelar_ativado = True
                congelar_tempo_fim = tempo_atual + 5000  # 5 segundos

                for meteoro in meteoros:
                    meteoro["congelado"] = True
                    meteoro["congelado_tempo"] = congelar_tempo_fim

                for boss in bosses:
                    boss.congelado = True
                    boss.congelado_tempo = congelar_tempo_fim

                for drone in drones:
                    drone.congelado = True
                    drone.congelado_tempo = congelar_tempo_fim

                print("Campo de congelamento ativado!")
            else:
                # Ativar teleporte
                areas_seguras = []

                for x in range(0, largura - 40, 40):
                    for y in range(100, altura - 100, 40):
                        area_teste = pygame.Rect(x, y, 40, 40)
                        area_segura = True

                        for meteoro in meteoros:
                            if area_teste.colliderect(meteoro["rect"]):
                                area_segura = False
                                break

                        for boss in bosses:
                            if area_teste.colliderect(boss.rect):
                                area_segura = False
                                break

                        for drone in drones:
                            if area_teste.colliderect(drone.rect):
                                area_segura = False
                                break

                        if area_segura:
                            areas_seguras.append((x, y))

                if areas_seguras:
                    melhor_area = None
                    menor_distancia = float('inf')

                    for x, y in areas_seguras:
                        distancia = math.sqrt((jogador.centerx - x) ** 2 + (jogador.centery - y) ** 2)
                        if distancia < menor_distancia:
                            menor_distancia = distancia
                            melhor_area = (x, y)

                    if melhor_area:
                        for _ in range(30):
                            criar_particulas_explosao_avancada(jogador.centerx, jogador.centery, 1, (200, 100, 255))

                        jogador.x, jogador.y = melhor_area

                        for _ in range(30):
                            criar_particulas_explosao_avancada(jogador.centerx, jogador.centery, 1, (100, 200, 255))

                        print("Teleporte realizado para área segura!")
                    else:
                        print("Nenhuma área segura encontrada!")
                else:
                    print("Nenhuma área segura disponível!")
            return True

    # Habilidades normais para naves não-admin
    if habilidade == "congelar":
        congelar_ativado = True
        congelar_tempo_fim = tempo_atual + 3000

        for meteoro in meteoros:
            meteoro["congelado"] = True
            meteoro["congelado_tempo"] = congelar_tempo_fim

        for boss in bosses:
            boss.congelado = True
            boss.congelado_tempo = congelar_tempo_fim

        for drone in drones:
            drone.congelado = True
            drone.congelado_tempo = congelar_tempo_fim

        print("Campo de congelamento ativado!")

    elif habilidade == "escudo":
        escudo_ativo = True
        escudo_tempo_fim = tempo_atual + 5000
        print("Escudo de plasma ativado!")

    elif habilidade == "velocidade":
        velocidade_dupla_ativa = True
        velocidade_dupla_tempo_fim = tempo_atual + 5000
        print("Velocidade dupla ativada!")

    elif habilidade == "tiro_triplo":
        tiro_triplo_ativo = True
        tiro_triplo_tempo_fim = tempo_atual + 10000
        print("Tiro triplo ativado!")

    elif habilidade == "lazer":
        lazer_ativado = True
        lazer_tempo_inicio = tempo_atual
        ultimo_lazer = tempo_atual
        print("Lazer/Kamehameha ativado!")

    elif habilidade == "teleporte":
        areas_seguras = []

        for x in range(0, largura - 40, 40):
            for y in range(100, altura - 100, 40):
                area_teste = pygame.Rect(x, y, 40, 40)
                area_segura = True

                for meteoro in meteoros:
                    if area_teste.colliderect(meteoro["rect"]):
                        area_segura = False
                        break

                for boss in bosses:
                    if area_teste.colliderect(boss.rect):
                        area_segura = False
                        break

                for drone in drones:
                    if area_teste.colliderect(drone.rect):
                        area_segura = False
                        break

                if area_segura:
                    areas_seguras.append((x, y))

        if areas_seguras:
            melhor_area = None
            menor_distancia = float('inf')

            for x, y in areas_seguras:
                distancia = math.sqrt((jogador.centerx - x) ** 2 + (jogador.centery - y) ** 2)
                if distancia < menor_distancia:
                    menor_distancia = distancia
                    melhor_area = (x, y)

            if melhor_area:
                for _ in range(30):
                    criar_particulas_explosao_avancada(jogador.centerx, jogador.centery, 1, (200, 100, 255))

                jogador.x, jogador.y = melhor_area

                for _ in range(30):
                    criar_particulas_explosao_avancada(jogador.centerx, jogador.centery, 1, (100, 200, 255))

                print("Teleporte realizado para área segura!")
            else:
                print("Nenhuma área segura encontrada!")
        else:
            print("Nenhuma área segura disponível!")

    if not is_nave_admin:
        habilidade_ativa = True
        habilidade_tempo_fim = tempo_atual + 5000
        habilidade_cooldown = tempo_atual + 15000

    return True


def ativar_lazer_geral():
    global lazer_ativado, lazer_tempo_inicio, ultimo_lazer

    tempo_atual = pygame.time.get_ticks()
    if tempo_atual - ultimo_lazer >= lazer_cooldown:
        lazer_ativado = True
        lazer_tempo_inicio = tempo_atual
        ultimo_lazer = tempo_atual
        print("LAZER ATIVADO!")
        return True
    else:
        tempo_restante = int((lazer_cooldown - (tempo_atual - ultimo_lazer)) / 1000)
        print(f"Lazer em cooldown! Aguarde {tempo_restante} segundos.")
        return False


def atualizar_habilidades():
    global escudo_ativo, velocidade_dupla_ativa, tiro_triplo_ativo, congelar_ativado
    global lazer_ativado, habilidades_admin_ativas

    tempo_atual = pygame.time.get_ticks()

    # Para naves admin, escudo, velocidade e tiro triplo são permanentes
    if not habilidades_admin_ativas:
        if escudo_ativo and tempo_atual >= escudo_tempo_fim:
            escudo_ativo = False
            print("Escudo desativado!")

        if velocidade_dupla_ativa and tempo_atual >= velocidade_dupla_tempo_fim:
            velocidade_dupla_ativa = False
            print("Velocidade normal restaurada!")

        if tiro_triplo_ativo and tempo_atual >= tiro_triplo_tempo_fim:
            tiro_triplo_ativo = False
            print("Tiro triplo desativado!")

    if congelar_ativado and tempo_atual >= congelar_tempo_fim:
        congelar_ativado = False
        for meteoro in meteoros:
            meteoro["congelado"] = False
        for boss in bosses:
            boss.congelado = False
        for drone in drones:
            drone.congelado = False
        print("Campo de congelamento desativado!")

    if lazer_ativado and tempo_atual - lazer_tempo_inicio > lazer_duracao:
        lazer_ativado = False


# == EFEITOS ESPECIAIS PARA CONGELAMENTO ==
def desenhar_meteoros_congelados(surface):
    tempo_atual = pygame.time.get_ticks()
    for meteoro in meteoros:
        if meteoro["congelado"]:
            pulsacao = 0.5 + 0.5 * math.sin(tempo_atual * 0.01)
            alpha = int(100 + 50 * pulsacao)

            surf_gelo = pygame.Surface((meteoro["rect"].width, meteoro["rect"].height), pygame.SRCALPHA)

            for i in range(5):
                tamanho = random.randint(3, 8)
                x = random.randint(0, meteoro["rect"].width)
                y = random.randint(0, meteoro["rect"].height)
                cor_gelo = (150, 200, 255, alpha)
                pygame.draw.circle(surf_gelo, cor_gelo, (x, y), tamanho)

            surface.blit(surf_gelo, meteoro["rect"])

            if random.random() < 0.3:
                criar_efeito_congelamento(meteoro["rect"].centerx, meteoro["rect"].centery)


def desenhar_bosses_congelados(surface):
    tempo_atual = pygame.time.get_ticks()
    for boss in bosses:
        if boss.congelado:
            pulsacao = 0.5 + 0.5 * math.sin(tempo_atual * 0.01)
            alpha = int(100 + 50 * pulsacao)

            surf_gelo_boss = pygame.Surface((boss.rect.width, boss.rect.height), pygame.SRCALPHA)

            for i in range(8):
                tamanho = random.randint(4, 10)
                x = random.randint(0, boss.rect.width)
                y = random.randint(0, boss.rect.height)
                cor_gelo = (150, 220, 255, alpha)
                pygame.draw.circle(surf_gelo_boss, cor_gelo, (x, y), tamanho)

            surface.blit(surf_gelo_boss, boss.rect)

            if random.random() < 0.4:
                criar_efeito_congelamento(boss.rect.centerx, boss.rect.centery)


def desenhar_drones_congelados(surface):
    tempo_atual = pygame.time.get_ticks()
    for drone in drones:
        if drone.congelado:
            pulsacao = 0.5 + 0.5 * math.sin(tempo_atual * 0.01)
            alpha = int(100 + 50 * pulsacao)

            surf_gelo_drone = pygame.Surface((drone.rect.width, drone.rect.height), pygame.SRCALPHA)

            for i in range(4):
                tamanho = random.randint(2, 6)
                x = random.randint(0, drone.rect.width)
                y = random.randint(0, drone.rect.height)
                cor_gelo = (150, 200, 255, alpha)
                pygame.draw.circle(surf_gelo_drone, cor_gelo, (x, y), tamanho)

            surface.blit(surf_gelo_drone, drone.rect)

            if random.random() < 0.3:
                criar_efeito_congelamento(drone.rect.centerx, drone.rect.centery)


# == EFEITOS ESPECIAIS PARA PORTAL ==
def desenhar_portal(surface, portal_rect):
    global portal_rotacao

    portal_rotacao += 2
    tempo_atual = pygame.time.get_ticks()

    portal_img_rotacionada = pygame.transform.rotate(portal_img, portal_rotacao)
    rect_rotacionado = portal_img_rotacionada.get_rect(center=portal_rect.center)
    surface.blit(portal_img_rotacionada, rect_rotacionado)

    for i in range(3):
        raio = 15 + i * 5
        cor_vortice = (50, 150, 255, 100)
        surf_vortice = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)

        for j in range(5):
            angulo = math.radians(portal_rotacao + j * 72)
            x = raio + math.cos(angulo) * (raio - j * 3)
            y = raio + math.sin(angulo) * (raio - j * 3)
            pygame.draw.circle(surf_vortice, cor_vortice, (int(x), int(y)), 2)

        surface.blit(surf_vortice, (portal_rect.centerx - raio, portal_rect.centery - raio))

    if random.random() < 0.6:
        criar_particulas_portal(portal_rect.centerx, portal_rect.centery)

    pulsacao = 0.5 + 0.5 * math.sin(tempo_atual * 0.005)
    alpha = int(50 + 30 * pulsacao)

    surf_brilho = pygame.Surface((portal_rect.width + 20, portal_rect.height + 20), pygame.SRCALPHA)
    pygame.draw.circle(surf_brilho, (100, 200, 255, alpha),
                       (surf_brilho.get_width() // 2, surf_brilho.get_height() // 2),
                       portal_rect.width // 2)
    surface.blit(surf_brilho, (portal_rect.centerx - surf_brilho.get_width() // 2,
                               portal_rect.centery - surf_brilho.get_height() // 2))


# == SISTEMA DE LAZER DO JOGADOR MELHORADO ==
def desenhar_lazer_jogador(surface):
    """LAZER DO JOGADOR COM EFEITOS VISUAIS MELHORADOS"""
    global lazer_ativado, pontuacao

    if not lazer_ativado:
        return

    tempo_atual = pygame.time.get_ticks()
    tempo_decorrido_lazer = tempo_atual - lazer_tempo_inicio

    if tempo_decorrido_lazer > lazer_duracao:
        lazer_ativado = False
        return

    # Efeito de piscagem no final
    if tempo_decorrido_lazer > lazer_duracao * 0.7:
        if int(tempo_atual / 100) % 2 == 0:
            return

    # Configurações do laser do jogador
    start_pos = (jogador.centerx, jogador.top - 10)
    end_pos = (jogador.centerx, 0)
    progresso = 1.0 - (tempo_decorrido_lazer / lazer_duracao)

    # 1. Núcleo principal super brilhante
    largura_nucleo = int(30 * progresso)
    cor_nucleo = (255, 0, 0)
    pygame.draw.line(surface, cor_nucleo, start_pos, end_pos, largura_nucleo)

    # 2. Múltiplas camadas de brilho
    for i in range(5):
        cor_brilho = (255, 100 - i * 20, 100 - i * 20)
        largura_camada = max(3, largura_nucleo - i * 6)
        pygame.draw.line(surface, cor_brilho, start_pos, end_pos, largura_camada)

    # 3. Partículas de energia intensas
    for _ in range(25):
        x = jogador.centerx + random.randint(-15, 15)
        y = random.randint(0, jogador.top)
        tamanho = random.randint(2, 5)
        cor_particula = (255, 255, 200)
        pygame.draw.circle(surface, cor_particula, (x, y), tamanho)

    # 4. Efeito de aura ao redor do laser
    for i in range(3):
        surf_aura = pygame.Surface((largura_nucleo + 20 + i * 10, altura), pygame.SRCALPHA)
        cor_aura = (255, 150, 150, 50 - i * 15)
        pygame.draw.rect(surf_aura, cor_aura,
                         (0, 0, largura_nucleo + 20 + i * 10, altura),
                         max(1, 3 - i))
        surface.blit(surf_aura, (jogador.centerx - (largura_nucleo + 20 + i * 10) // 2, 0))

    # Criar rastro visual SUPER MELHORADO
    efeitos.criar_rastro_laser(start_pos, end_pos, (255, 100, 100), 20, 600)

    # Criar partículas de laser especiais
    for _ in range(15):
        criar_particulas_laser(jogador.centerx + random.randint(-12, 12),
                               random.randint(0, jogador.top))

    # Área de colisão do laser
    lazer_rect = pygame.Rect(jogador.centerx - largura_nucleo // 2, 0, largura_nucleo, jogador.top)

    # Verificar colisões
    for meteoro_lazer in meteoros[:]:
        if lazer_rect.colliderect(meteoro_lazer["rect"]):
            explosoes.append(
                criar_explosao_efeitos(meteoro_lazer["rect"].centerx, meteoro_lazer["rect"].centery, 70))
            pontuacao += 50
            meteoros.remove(meteoro_lazer)

    for boss_lazer in bosses[:]:
        if lazer_rect.colliderect(boss_lazer.rect):
            if boss_lazer.levar_dano(5):
                explosoes.append(criar_explosao_efeitos(boss_lazer.rect.centerx, boss_lazer.rect.centery, 100))
                pontuacao += 500
                bosses.remove(boss_lazer)
                if len(bosses) == 0:
                    global boss_ativo
                    boss_ativo = False

    for drone_lazer in drones[:]:
        if lazer_rect.colliderect(drone_lazer.rect):
            if drone_lazer.levar_dano(3):
                explosoes.append(criar_explosao_efeitos(drone_lazer.rect.centerx, drone_lazer.rect.centery, 40))
                pontuacao += 100
                drones.remove(drone_lazer)


# == MENU PRINCIPAL ==
def mostrar_menu_principal():
    menu_ativo = True
    progresso = carregar_progresso()

    while menu_ativo:
        tela.fill((0, 0, 40))

        # Desenhar fundo estelar sem causar erros
        fundo_estelar.atualizar()
        fundo_estelar.desenhar(tela)

        titulo = fonte.render("NAVE vs METEOROS", True, (255, 255, 255))
        subtitulo = fonte_pequena.render("VERSÃO APRIMORADA", True, (100, 255, 255))
        iniciar = fonte_pequena.render("Pressione ESPAÇO para iniciar", True, (200, 200, 200))

        if progresso:
            recorde = fonte_pequena.render(f"Recorde: {progresso.get('pontuacao_maxima', 0)} pontos", True,
                                           (255, 255, 0))
            tela.blit(recorde, (largura // 2 - recorde.get_width() // 2, altura // 2 + 50))

        tela.blit(titulo, (largura // 2 - titulo.get_width() // 2, altura // 3 - 30))
        tela.blit(subtitulo, (largura // 2 - subtitulo.get_width() // 2, altura // 3 + 10))
        tela.blit(iniciar, (largura // 2 - iniciar.get_width() // 2, altura // 2))

        pygame.display.flip()

        for evento_menu in pygame.event.get():
            if evento_menu.type == pygame.QUIT:
                return False
            if evento_menu.type == pygame.KEYDOWN:
                if evento_menu.key == pygame.K_SPACE:
                    return True
                if evento_menu.key == pygame.K_ESCAPE:
                    return False

    return True


# == SISTEMA DE PROGRESSÃO ==
def verificar_desbloqueio_naves():
    global naves_desbloqueadas, pontuacao_para_proxima_nave, pontuacao

    for i in range(1, len(naves_desbloqueadas)):
        if not naves_desbloqueadas[i] and pontuacao >= pontuacao_necessaria_por_nave[i]:
            naves_desbloqueadas[i] = True
            pontuacao_para_proxima_nave = 0
            print(f"Nave {i + 1} desbloqueada!")
            for _ in range(50):
                criar_particulas_explosao_avancada(largura // 2, altura // 2, 1, (0, 255, 255))
            return True
    return False


def trocar_nave(numero):
    global nave_selecionada, vida_jogador, max_vida, max_vida_admin

    # Verificar se é uma nave admin (7, 8, 9)
    is_nave_admin = numero >= 7

    if 0 <= numero - 1 < len(naves_imagens):
        # Para naves admin, sempre estão desbloqueadas
        if is_nave_admin or naves_desbloqueadas[numero - 1]:
            # RESETAR HABILIDADES ANTES DE TROCAR DE NAVE
            resetar_habilidades_ao_trocar_nave()

            nave_selecionada = numero - 1

            # Se for nave admin, definir vida máxima como 10
            if is_nave_admin:
                vida_jogador = max_vida_admin
                print(f"Nave Admin {numero} selecionada! (Gabriel, Paulo ou Vitor)")
            else:
                vida_jogador = max_vida
                print(f"Nave {numero} selecionada! Habilidade: {habilidades_naves[nave_selecionada]}")

            return True
        else:
            print(f"Nave {numero} ainda não desbloqueada!")
            return False
    else:
        print(f"Nave {numero} não existe!")
        return False


# == SISTEMA DE METEOROS MELHORADO ==
def criar_meteoro():
    if nivel >= 15 and random.random() < 0.2:
        tamanho = 100
        velocidade_x = random.uniform(-1, 1)
        velocidade_y = velocidade_base + (nivel * 0.8)
        rotacao_speed = random.uniform(-1, 1)
        x = random.randint(0, largura - tamanho)
        rect = pygame.Rect(x, -tamanho, tamanho, tamanho)
        return {
            "rect": rect,
            "velocidade_y": velocidade_y,
            "velocidade_x": velocidade_x,
            "rotacao": 0,
            "rotacao_speed": rotacao_speed,
            "tipo": "enorme",
            "vida": 3,
            "congelado": False,
            "congelado_tempo": 0
        }
    elif nivel >= 10 and random.random() < 0.3:
        tamanho = 80
        velocidade_x = random.uniform(-1.5, 1.5)
        velocidade_y = velocidade_base + (nivel * 1.0)
        rotacao_speed = random.uniform(-1.5, 1.5)
        x = random.randint(0, largura - tamanho)
        rect = pygame.Rect(x, -tamanho, tamanho, tamanho)
        return {
            "rect": rect,
            "velocidade_y": velocidade_y,
            "velocidade_x": velocidade_x,
            "rotacao": 0,
            "rotacao_speed": rotacao_speed,
            "tipo": "grande",
            "vida": 2,
            "congelado": False,
            "congelado_tempo": 0
        }
    elif nivel >= 5 and random.random() < 0.4:
        tamanho = 60
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
            "tipo": "medio",
            "vida": 1,
            "congelado": False,
            "congelado_tempo": 0
        }
    else:
        tamanho = 40
        x = random.randint(0, largura - tamanho)
        rect = pygame.Rect(x, -tamanho, tamanho, tamanho)
        velocidade_y = velocidade_base + (nivel * 1.5)
        rotacao_speed = random.uniform(-2, 2)
        return {
            "rect": rect,
            "velocidade_y": velocidade_y,
            "velocidade_x": 0,
            "rotacao": 0,
            "rotacao_speed": rotacao_speed,
            "tipo": "pequeno",
            "vida": 1,
            "congelado": False,
            "congelado_tempo": 0
        }


def criar_meteoros_filhos(x, y, tipo_pai):
    meteoros_filhos = []

    if tipo_pai == "grande":
        for _ in range(2):
            tamanho = 40
            velocidade_x = random.uniform(-2, 2)
            velocidade_y = velocidade_base + (nivel * 1.5)
            rotacao_speed = random.uniform(-3, 3)

            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)

            rect = pygame.Rect(x + offset_x, y + offset_y, tamanho, tamanho)
            meteoros_filhos.append({
                "rect": rect,
                "velocidade_y": velocidade_y,
                "velocidade_x": velocidade_x,
                "rotacao": 0,
                "rotacao_speed": rotacao_speed,
                "tipo": "pequeno",
                "vida": 1,
                "congelado": False,
                "congelado_tempo": 0
            })

    elif tipo_pai == "enorme":
        for _ in range(3):
            tamanho = 50
            velocidade_x = random.uniform(-2, 2)
            velocidade_y = velocidade_base + (nivel * 1.3)
            rotacao_speed = random.uniform(-2, 2)

            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)

            rect = pygame.Rect(x + offset_x, y + offset_y, tamanho, tamanho)
            meteoros_filhos.append({
                "rect": rect,
                "velocidade_y": velocidade_y,
                "velocidade_x": velocidade_x,
                "rotacao": 0,
                "rotacao_speed": rotacao_speed,
                "tipo": "medio",
                "vida": 1,
                "congelado": False,
                "congelado_tempo": 0
            })

    return meteoros_filhos


def criar_projetil():
    # Para naves admin com munição infinita, sempre pode atirar
    if municao_infinita_ativa or (municao_atual > 0 and not recarregando):
        x = jogador.centerx - 7
        y = jogador.top
        return {"rect": pygame.Rect(x, y, 15, 25), "rotacao": 0}
    return None


def criar_projeteis_triplo():
    projeteis_local = []
    # Para naves admin com munição infinita, sempre pode atirar
    if municao_infinita_ativa or (municao_atual > 0 and not recarregando):
        projeteis_local.append({"rect": pygame.Rect(jogador.centerx - 7, jogador.top, 15, 25), "rotacao": 0})
        projeteis_local.append({"rect": pygame.Rect(jogador.centerx - 20, jogador.top, 15, 25), "rotacao": -10})
        projeteis_local.append({"rect": pygame.Rect(jogador.centerx + 6, jogador.top, 15, 25), "rotacao": 10})
    return projeteis_local


def criar_coracao():
    x = random.randint(30, largura - 30)
    return pygame.Rect(x, -30, 30, 30)


def criar_portal():
    x = random.randint(60, largura - 60)
    return pygame.Rect(x, -60, 60, 60)


def criar_explosao_efeitos(x, y, tamanho=50, tipo="normal"):
    if tipo == "coracao":
        criar_particulas_explosao_avancada(x, y, 15, (255, 100, 100))
        efeitos.criar_brilho(x, y, (255, 100, 100), tamanho, 500, 0.8)
    elif tipo == "portal":
        for _ in range(20):
            angulo = random.uniform(0, 2 * math.pi)
            distancia = random.uniform(0, 40)
            velocidade = random.uniform(2, 6)

            particulas.append(ParticulaAvancada(
                x, y, (100, 150, 255),
                math.cos(angulo) * velocidade,
                math.sin(angulo) * velocidade,
                1200, random.uniform(3, 6), "estrela"
            ))
        efeitos.criar_brilho(x, y, (100, 150, 255), tamanho * 2, 1000, 1.0)
    else:
        criar_particulas_explosao_avancada(x, y, 30)
        efeitos.criar_brilho(x, y, (255, 200, 100), tamanho * 2, 800, 1.0)

    return {"rect": pygame.Rect(x - tamanho // 2, y - tamanho // 2, tamanho, tamanho),
            "tempo_inicio": pygame.time.get_ticks(), "duracao": 500}


def desenhar_explosao(surface, explosao_obj):
    tempo_decorrido_explosao = pygame.time.get_ticks() - explosao_obj["tempo_inicio"]
    progresso = min(tempo_decorrido_explosao / explosao_obj["duracao"], 1.0)

    raio = int(progresso * explosao_obj["rect"].width // 2)
    for i in range(3):
        cor = (255, 165 - i * 30, 0)
        pygame.draw.circle(surface, cor, explosao_obj["rect"].center, raio - i * 5)

    for i in range(15):
        angulo = random.uniform(0, 6.28)
        distancia = progresso * 40
        x = explosao_obj["rect"].centerx + int(distancia * pygame.math.Vector2(1, 0).rotate(angulo).x)
        y = explosao_obj["rect"].centery + int(distancia * pygame.math.Vector2(1, 0).rotate(angulo).y)
        pygame.draw.circle(surface, (255, 255, 100), (x, y), 3)


def atualizar_municao():
    global municao_atual, recarregando, tempo_inicio_recarga, ultimo_recarga

    # Para naves admin com munição infinita, não precisa recarregar
    if municao_infinita_ativa:
        municao_atual = municao_maxima
        recarregando = False
        return

    tempo_atual_municao = pygame.time.get_ticks()

    if municao_atual <= 0 and not recarregando:
        recarregando = True
        tempo_inicio_recarga = tempo_atual_municao
        print("Recarregando munição...")

    if recarregando:
        tempo_decorrido_municao = tempo_atual_municao - tempo_inicio_recarga
        if tempo_decorrido_municao >= intervalo_recarga:
            municao_atual = municao_maxima
            recarregando = False
            print("Munição recarregada!")

    if tempo_atual_municao - ultimo_recarga > 10000 and municao_atual < municao_maxima and not recarregando:
        municao_atual = min(municao_maxima, municao_atual + 1)
        ultimo_recarga = tempo_atual_municao


def desenhar_escudo(surface):
    if escudo_ativo:
        tempo_escudo = pygame.time.get_ticks()
        raio = 35 + int(5 * math.sin(tempo_escudo * 0.01))

        for i in range(3):
            alpha = 100 - i * 30
            surf_escudo = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
            cor_escudo = (0, 100 + i * 50, 255, alpha)
            pygame.draw.circle(surf_escudo, cor_escudo, (raio, raio), raio - i * 5, 3)
            surface.blit(surf_escudo, (jogador.centerx - raio, jogador.centery - raio))

        criar_particulas_escudo_avancado(jogador.centerx, jogador.centery)


def desenhar_efeito_velocidade(surface):
    if velocidade_dupla_ativa:
        tempo_velocidade = pygame.time.get_ticks()
        for i in range(3):
            offset = int(10 * math.sin(tempo_velocidade * 0.01 + i * 2))
            pygame.draw.line(surface, (255, 255, 0),
                             (jogador.left - 5 - offset, jogador.centery),
                             (jogador.left - 15 - offset, jogador.centery), 2)


# == SISTEMA DE BOSS CORRIGIDO ==
def verificar_spawn_boss():
    global boss_ativo, nivel, nivel_maximo_alcancado, bosses_derrotados

    # Se já tem um boss ativo, não spawna outro
    if boss_ativo:
        return

    # CORREÇÃO: Verificar se o jogador alcançou um nível múltiplo de 5
    nivel_boss_atual = (nivel // 5) * 5  # Pega o múltiplo de 5 mais próximo

    # CORREÇÃO: Se o jogador alcançou o nível 20, spawnar Boss Gabriel
    if nivel >= 20 and 20 not in bosses_derrotados:
        spawnar_boss(20)
        print("BOSS GABRIEL (Nível 20) apareceu!")
        return

    # CORREÇÃO: Spawnar bosses nos níveis 5, 10, 15
    if nivel_boss_atual >= 5 and nivel_boss_atual <= 15 and nivel_boss_atual not in bosses_derrotados:
        spawnar_boss(nivel_boss_atual)
        print(f"BOSS nível {nivel_boss_atual} apareceu no nível {nivel}!")


def spawnar_boss(nivel_boss):
    global boss_ativo, bosses

    boss_ativo = True
    bosses.clear()
    drones.clear()

    if nivel_boss == 5:
        bosses.append(Boss(nivel_boss, largura // 2, usar_lazer=True, tipo_boss=1))
        print(f"BOSS nível {nivel_boss} apareceu! (Atirador Rápido)")

    elif nivel_boss == 10:
        bosses.append(Boss(nivel_boss, largura // 3, usar_lazer=False, tipo_boss=2))
        bosses.append(Boss(nivel_boss, 2 * largura // 3, usar_lazer=True, tipo_boss=2))
        bosses[1].largura = 50
        bosses[1].altura = 50
        bosses[1].rect = pygame.Rect(2 * largura // 3, 50, 50, 50)
        print(f"BOSS nível {nivel_boss} apareceu! (Dupla Dinâmica)")

    elif nivel_boss == 15:
        bosses.append(BossNivel15())
        print("BOSS NÍVEL 15 apareceu! (Boss Especial)")

    elif nivel_boss == 20:
        bosses.append(BossGabriel())
        print("BOSS GABRIEL apareceu! (Boss Final)")


def atualizar_pontuacao():
    global pontuacao, nivel, boss_ativo, nivel_maximo_alcancado, bosses_derrotados

    nivel_maximo_alcancado = max(nivel_maximo_alcancado, nivel)

    # Verificar se subiu de nível
    novo_nivel = pontuacao // 500 + 1
    if novo_nivel > nivel:
        nivel = novo_nivel
        print(f"Subiu para o nível {nivel}!")

        # Verificar se precisa spawnar boss
        verificar_spawn_boss()

    verificar_desbloqueio_naves()


def desenhar_interface():
    texto_pontuacao = fonte_pequena.render(f"Pontos: {pontuacao}", True, (255, 255, 255))
    tela.blit(texto_pontuacao, (10, 10))

    texto_nivel = fonte_pequena.render(f"Nível: {nivel}", True, (255, 255, 255))
    tela.blit(texto_nivel, (10, 40))

    for i in range(vida_jogador):
        tela.blit(coracao_img, (10 + i * 35, 70))

    # Mostrar munição de forma diferente para naves admin
    if municao_infinita_ativa:
        texto_municao = fonte_pequena.render(f"Munição: INFINITA", True, (0, 255, 0))
    else:
        texto_municao = fonte_pequena.render(f"Munição: {municao_atual}/{municao_maxima}", True, (255, 255, 255))
    tela.blit(texto_municao, (largura - 150, 10))

    if recarregando and not municao_infinita_ativa:
        tempo_atual_recarga = pygame.time.get_ticks()
        tempo_decorrido_recarga = tempo_atual_recarga - tempo_inicio_recarga
        progresso = min(tempo_decorrido_recarga / intervalo_recarga, 1.0)
        pygame.draw.rect(tela, (255, 0, 0), (largura - 150, 40, 100, 10))
        pygame.draw.rect(tela, (0, 255, 0), (largura - 150, 40, int(100 * progresso), 10))

    tempo_atual_lazer_interface = pygame.time.get_ticks()
    tempo_restante_lazer = max(0, lazer_cooldown - (tempo_atual_lazer_interface - ultimo_lazer))
    if tempo_restante_lazer > 0:
        texto_lazer = fonte_pequena.render(f"Lazer: {int(tempo_restante_lazer / 1000)}s", True, (255, 100, 100))
        tela.blit(texto_lazer, (largura - 150, 60))
    else:
        texto_lazer = fonte_pequena.render("Lazer: PRONTO (L)", True, (100, 255, 100))
        tela.blit(texto_lazer, (largura - 150, 60))

    texto_nave = fonte_pequena.render(f"Nave: {nave_selecionada + 1}", True, (255, 255, 255))
    tela.blit(texto_nave, (largura - 150, 85))

    habilidade_atual = habilidades_naves[nave_selecionada]
    tempo_atual = pygame.time.get_ticks()

    # Para naves admin, mostrar status especial
    if nave_selecionada >= 6:  # Naves admin
        if habilidades_admin_ativas:
            texto_habilidade = fonte_pequena.render("MODO ADMIN ATIVO", True, (0, 255, 0))
        else:
            texto_habilidade = fonte_pequena.render("ADMIN: PRONTO (H)", True, (100, 255, 100))
    elif tempo_atual < habilidade_cooldown:
        tempo_restante = (habilidade_cooldown - tempo_atual) // 1000
        texto_habilidade = fonte_pequena.render(f"{habilidade_atual}: {tempo_restante}s", True, (255, 100, 100))
    else:
        texto_habilidade = fonte_pequena.render(f"{habilidade_atual}: PRONTO (H)", True, (100, 255, 100))

    tela.blit(texto_habilidade, (10, 110))


def desenhar_fundo_completo(surface):
    surface.fill((5, 5, 20))
    fundo_estelar.desenhar(surface)

    # CORREÇÃO: Verificar se há brilhos para desenhar antes de tentar desenhá-los
    try:
        efeitos.desenhar_brilhos(surface)
    except Exception as e:
        print(f"Erro ao desenhar brilhos: {e}")
        # Limpar efeitos problemáticos
        efeitos.particulas_brilho.clear()
        efeitos.luzes_dinamicas.clear()
        efeitos.rastros_laser.clear()

    for particula in particulas:
        particula.desenhar(surface)


def atualizar_efeitos_visuais():
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
nivel_maximo_alcancado = progresso_salvo.get('nivel_maximo', 1)
bosses_derrotados = []

# == LOOP PRINCIPAL DO JOGO ==
if __name__ == "__main__":
    if mostrar_menu_principal():
        while rodando:
            desenhar_fundo_completo(tela)
            atualizar_efeitos_visuais()

            criar_particulas_estrelas_avancadas()
            criar_particulas_propulsao_avancada()

            for evento_jogo in pygame.event.get():
                if evento_jogo.type == pygame.QUIT:
                    salvar_progresso()
                    rodando = False

                if evento_jogo.type == pygame.KEYDOWN:
                    if evento_jogo.key == pygame.K_1:
                        trocar_nave(1)
                    elif evento_jogo.key == pygame.K_2:
                        trocar_nave(2)
                    elif evento_jogo.key == pygame.K_3:
                        trocar_nave(3)
                    elif evento_jogo.key == pygame.K_4:
                        trocar_nave(4)
                    elif evento_jogo.key == pygame.K_5:
                        trocar_nave(5)
                    elif evento_jogo.key == pygame.K_6:
                        trocar_nave(6)
                    elif evento_jogo.key == pygame.K_p:  # Nave Gabriel (Admin)
                        mostrar_tela_senha("gabriel")
                    elif evento_jogo.key == pygame.K_o:  # Nave Paulo (Admin)
                        mostrar_tela_senha("paulo")
                    elif evento_jogo.key == pygame.K_i:  # Nave Vitor (Admin)
                        mostrar_tela_senha("vitor")
                    elif evento_jogo.key == pygame.K_SPACE and not game_over and not digitando_senha:
                        if tiro_triplo_ativo:
                            novos_projeteis = criar_projeteis_triplo()
                            for projetil_novo in novos_projeteis:
                                projeteis.append(projetil_novo)
                            # Para naves normais, reduz munição
                            if not municao_infinita_ativa:
                                municao_atual -= 1
                        else:
                            novo_projetil = criar_projetil()
                            if novo_projetil is not None:
                                projeteis.append(novo_projetil)
                                # Para naves normais, reduz munição
                                if not municao_infinita_ativa:
                                    municao_atual -= 1
                    elif evento_jogo.key == pygame.K_h and not game_over and not digitando_senha:
                        ativar_habilidade()
                    elif evento_jogo.key == pygame.K_l and not game_over and not digitando_senha:
                        ativar_lazer_geral()
                    elif evento_jogo.key == pygame.K_r and game_over:
                        salvar_progresso()
                        jogador = pygame.Rect(180, 500, 40, 40)
                        meteoros = []
                        projeteis = []
                        projeteis_boss = []
                        explosoes = []
                        coracoes = []
                        portais = []
                        bosses = []
                        drones = []
                        boss_ativo = False
                        pontuacao = 0
                        nivel = 1
                        nivel_maximo_alcancado = 1
                        vida_jogador = 3
                        municao_atual = municao_maxima
                        recarregando = False
                        lazer_ativado = False
                        escudo_ativo = False
                        tiro_triplo_ativo = False
                        velocidade_dupla_ativa = False
                        congelar_ativado = False
                        teleporte_ativado = False
                        habilidades_admin_ativas = False
                        municao_infinita_ativa = False
                        tempo_inicio = pygame.time.get_ticks()
                        ultimo_boss_derrotado = 0
                        nave_selecionada = 0
                        bosses_derrotados = []
                        particulas.clear()
                        efeitos.particulas_brilho.clear()
                        efeitos.luzes_dinamicas.clear()
                        efeitos.rastros_laser.clear()
                        game_over = False

            if not game_over and not digitando_senha:
                # Atualizar velocidade dos meteoros
                atualizar_velocidade_meteoros()

                # Atualizar drones
                for drone in drones[:]:
                    drone.atualizar(jogador)

                    if drone.rect.colliderect(jogador) and not escudo_ativo:
                        explosoes.append(criar_explosao_efeitos(drone.rect.centerx, drone.rect.centery, 40))
                        drones.remove(drone)
                        vida_jogador -= 1
                        if vida_jogador <= 0:
                            game_over = True

                for boss_obj in bosses[:]:
                    boss_obj.atualizar(jogador)

                    # Verificar tipo específico de boss para comportamentos especiais
                    if isinstance(boss_obj, BossNivel15):
                        # Boss nível 15 - comportamento específico
                        if pygame.time.get_ticks() - boss_obj.ultimo_tiro > boss_obj.intervalo_tiros:
                            if boss_obj.cycles_completos < 5:
                                boss_obj.atirar()
                                boss_obj.cycles_completos += 1
                                boss_obj.ultimo_tiro = pygame.time.get_ticks()
                            else:
                                boss_obj.laser_ativado = True
                                boss_obj.laser_tempo_inicio = pygame.time.get_ticks()
                                boss_obj.cycles_completos = 0

                        # Laser do boss nível 15 - CORREÇÃO: método correto
                        if boss_obj.desenhar_laser(tela, jogador):
                            # Nave Gabriel é imune ao boss nível 15
                            if nave_selecionada != 6:  # Não é a nave Gabriel
                                if not escudo_ativo:
                                    explosoes.append(criar_explosao_efeitos(jogador.centerx, jogador.centery, 60))
                                    vida_jogador -= 2
                                    if vida_jogador <= 0:
                                        game_over = True

                        # Atualizar bosses gêmeos
                        for gemeo in boss_obj.bosses_gemeos[:]:
                            gemeo.atualizar(jogador)
                            if gemeo.pode_atirar():
                                novos_projeteis_boss_gemeo = gemeo.atirar(jogador)
                                projeteis_boss.extend(novos_projeteis_boss_gemeo)

                            if gemeo.usar_lazer and random.random() < 0.02:
                                gemeo.ativar_lazer()

                            # Laser dos gêmeos - CORREÇÃO: método correto
                            if gemeo.desenhar_laser(tela, jogador):
                                if nave_selecionada != 6 and not escudo_ativo:  # Não é Gabriel e sem escudo
                                    explosoes.append(criar_explosao_efeitos(jogador.centerx, jogador.centery, 60))
                                    vida_jogador -= 2
                                    if vida_jogador <= 0:
                                        game_over = True

                    elif isinstance(boss_obj, BossGabriel):
                        # Boss Gabriel - comportamento específico
                        if pygame.time.get_ticks() - boss_obj.ultimo_tiro > boss_obj.intervalo_tiros:
                            boss_obj.atirar()
                            boss_obj.ultimo_tiro = pygame.time.get_ticks()

                        # Laser do boss Gabriel - CORREÇÃO: método correto
                        if boss_obj.desenhar_laser(tela, jogador):
                            if not escudo_ativo:
                                explosoes.append(criar_explosao_efeitos(jogador.centerx, jogador.centery, 70))
                                vida_jogador -= 3
                                if vida_jogador <= 0:
                                    game_over = True

                        # Ataque especial do boss Gabriel
                        if boss_obj.desenhar_ataque_especial(tela, jogador):
                            if not escudo_ativo:
                                explosoes.append(criar_explosao_efeitos(jogador.centerx, jogador.centery, 80))
                                vida_jogador -= 4
                                if vida_jogador <= 0:
                                    game_over = True

                    else:
                        # Bosses normais
                        if boss_obj.pode_atirar():
                            novos_projeteis_boss = boss_obj.atirar(jogador)
                            projeteis_boss.extend(novos_projeteis_boss)

                        if boss_obj.usar_lazer and random.random() < 0.02:
                            boss_obj.ativar_lazer()

                        # LAZER DO BOSS AGORA CAUSA 2 DE DANO (não mais instantâneo) - CORREÇÃO: método correto
                        if boss_obj.desenhar_laser(tela, jogador):
                            if not escudo_ativo:
                                explosoes.append(criar_explosao_efeitos(jogador.centerx, jogador.centery, 60))
                                vida_jogador -= 2  # Alterado de 0 para 2
                                if vida_jogador <= 0:
                                    game_over = True

                tempo_atual_jogo = pygame.time.get_ticks()

                if tempo_atual_jogo - ultimo_salvamento > intervalo_salvamento:
                    salvar_progresso()
                    ultimo_salvamento = tempo_atual_jogo

                if tempo_atual_jogo - ultimo_coracao > intervalo_coracoes and len(coracoes) < 3:
                    coracoes.append(criar_coracao())
                    ultimo_coracao = tempo_atual_jogo

                # Não spawnar portais durante bosses (exceto boss Gabriel)
                boss_gabriel_ativo = any(isinstance(boss, BossGabriel) for boss in bosses)
                if tempo_atual_jogo - ultimo_portal > intervalo_portais and len(
                        portais) < 1 and not boss_ativo and not boss_gabriel_ativo:
                    portais.append(criar_portal())
                    ultimo_portal = tempo_atual_jogo

                atualizar_municao()
                atualizar_habilidades()

                velocidade_atual = velocidade_jogador * 2 if velocidade_dupla_ativa else velocidade_jogador

                teclas = pygame.key.get_pressed()
                if teclas[pygame.K_LEFT] and jogador.left > 0:
                    jogador.x -= velocidade_atual
                if teclas[pygame.K_RIGHT] and jogador.right < largura:
                    jogador.x += velocidade_atual
                if teclas[pygame.K_UP] and jogador.top > 0:
                    jogador.y -= velocidade_atual
                if teclas[pygame.K_DOWN] and jogador.bottom < altura:
                    jogador.y += velocidade_atual

                # CORREÇÃO: Não spawnar meteoros durante boss (exceto boss Gabriel)
                boss_gabriel_ativo = any(isinstance(boss, BossGabriel) for boss in bosses)
                if not boss_ativo or boss_gabriel_ativo:
                    # Apenas spawnar meteoros se não houver boss ou se for o boss Gabriel
                    chance_spawn = max(5, 60 - nivel * 3)
                    if random.randint(1, chance_spawn) == 1:
                        meteoros.append(criar_meteoro())

                for meteoro_obj in meteoros[:]:
                    if not meteoro_obj["congelado"]:
                        meteoro_obj["rect"].y += meteoro_obj["velocidade_y"]
                        meteoro_obj["rect"].x += meteoro_obj["velocidade_x"]
                        meteoro_obj["rotacao"] += meteoro_obj["rotacao_speed"]

                        if meteoro_obj["rect"].left <= 0 or meteoro_obj["rect"].right >= largura:
                            meteoro_obj["velocidade_x"] *= -1

                    if meteoro_obj["rect"].colliderect(jogador):
                        if not escudo_ativo:
                            explosoes.append(
                                criar_explosao_efeitos(meteoro_obj["rect"].centerx, meteoro_obj["rect"].centery, 70))
                            vida_jogador -= 1
                            if vida_jogador <= 0:
                                game_over = True
                        else:
                            explosoes.append(
                                criar_explosao_efeitos(meteoro_obj["rect"].centerx, meteoro_obj["rect"].centery, 50))
                            pontuacao += 25

                        if meteoro_obj in meteoros:
                            meteoros.remove(meteoro_obj)

                    if meteoro_obj["tipo"] == "enorme":
                        meteoro_img_rotacionada = pygame.transform.rotate(meteoro_enorme_img, meteoro_obj["rotacao"])
                    elif meteoro_obj["tipo"] == "grande":
                        meteoro_img_rotacionada = pygame.transform.rotate(meteoro_grande_img, meteoro_obj["rotacao"])
                    else:
                        meteoro_img_rotacionada = pygame.transform.rotate(meteoro_img, meteoro_obj["rotacao"])

                    tela.blit(meteoro_img_rotacionada, meteoro_obj["rect"])

                for coracao_obj in coracoes[:]:
                    coracao_obj.y += 3

                    if coracao_obj.colliderect(jogador) and vida_jogador < (
                    max_vida_admin if nave_selecionada >= 6 else max_vida):
                        vida_jogador += 1
                        coracoes.remove(coracao_obj)
                        explosoes.append(
                            criar_explosao_efeitos(coracao_obj.centerx, coracao_obj.centery, 30, "coracao"))

                    elif coracao_obj.y < altura:
                        tela.blit(coracao_img, coracao_obj)
                    else:
                        coracoes.remove(coracao_obj)

                for portal_obj in portais[:]:
                    portal_obj.y += 2

                    if portal_obj.colliderect(jogador):
                        nivel_anterior = nivel
                        nivel += 3
                        nivel_maximo_alcancado = max(nivel_maximo_alcancado, nivel)
                        pontuacao += 600
                        portais.remove(portal_obj)
                        explosoes.append(criar_explosao_efeitos(portal_obj.centerx, portal_obj.centery, 80, "portal"))
                        print(f"Portal usado! Avançou do nível {nivel_anterior} para o nível {nivel}")

                        # Verificar se ao passar pelo portal, o jogador alcançou um nível que deveria ter boss
                        verificar_spawn_boss()

                    elif portal_obj.y < altura:
                        desenhar_portal(tela, portal_obj)
                    else:
                        portais.remove(portal_obj)

                projeteis_a_remover = []

                for projetil_obj in projeteis[:]:
                    velocidade_projetil = 15 if velocidade_dupla_ativa else 10
                    projetil_obj["rect"].y -= velocidade_projetil
                    projetil_obj["rotacao"] += 5

                    for meteoro_projetil in meteoros[:]:
                        if projetil_obj["rect"].colliderect(meteoro_projetil["rect"]):
                            if meteoro_projetil["vida"] > 1:
                                meteoro_projetil["vida"] -= 1
                                explosoes.append(criar_explosao_efeitos(meteoro_projetil["rect"].centerx,
                                                                        meteoro_projetil["rect"].centery, 40))
                                pontuacao += 25
                            else:
                                explosoes.append(criar_explosao_efeitos(meteoro_projetil["rect"].centerx,
                                                                        meteoro_projetil["rect"].centery, 70))
                                pontuacao += 50

                                if meteoro_projetil["tipo"] in ["grande", "enorme"]:
                                    novos_meteoros = criar_meteoros_filhos(
                                        meteoro_projetil["rect"].centerx,
                                        meteoro_projetil["rect"].centery,
                                        meteoro_projetil["tipo"]
                                    )
                                    meteoros.extend(novos_meteoros)
                                    print(
                                        f"Meteoro {meteoro_projetil['tipo']} se partiu em {len(novos_meteoros)} pedaços!")

                                meteoros.remove(meteoro_projetil)

                            projeteis_a_remover.append(projetil_obj)
                            break

                    for boss_projetil in bosses[:]:
                        if projetil_obj["rect"].colliderect(boss_projetil.rect):
                            explosoes.append(
                                criar_explosao_efeitos(projetil_obj["rect"].centerx, projetil_obj["rect"].centery, 30))
                            projeteis_a_remover.append(projetil_obj)
                            if boss_projetil.levar_dano(10):
                                explosoes.append(
                                    criar_explosao_efeitos(boss_projetil.rect.centerx, boss_projetil.rect.centery, 100))
                                pontuacao += 500
                                ultimo_boss_derrotado = boss_projetil.nivel_boss if hasattr(boss_projetil,
                                                                                            'nivel_boss') else 15
                                # Adicionar à lista de bosses derrotados
                                if ultimo_boss_derrotado not in bosses_derrotados:
                                    bosses_derrotados.append(ultimo_boss_derrotado)
                                bosses.remove(boss_projetil)
                                # CORREÇÃO: Atualizar boss_ativo quando qualquer boss é derrotado
                                if len(bosses) == 0:
                                    boss_ativo = False
                                    print(f"BOSS nível {ultimo_boss_derrotado} derrotado!")
                            break

                    for drone_projetil in drones[:]:
                        if projetil_obj["rect"].colliderect(drone_projetil.rect):
                            explosoes.append(
                                criar_explosao_efeitos(projetil_obj["rect"].centerx, projetil_obj["rect"].centery, 20))
                            projeteis_a_remover.append(projetil_obj)
                            if drone_projetil.levar_dano(1):
                                explosoes.append(
                                    criar_explosao_efeitos(drone_projetil.rect.centerx, drone_projetil.rect.centery,
                                                           40))
                                pontuacao += 100
                                drones.remove(drone_projetil)
                            break

                    if projetil_obj["rect"].bottom < 0:
                        projeteis_a_remover.append(projetil_obj)
                    else:
                        projetil_img_rotacionada = pygame.transform.rotate(projetil_img, projetil_obj["rotacao"])
                        tela.blit(projetil_img_rotacionada, projetil_obj["rect"])

                for projetil_remover in projeteis_a_remover:
                    if projetil_remover in projeteis:
                        projeteis.remove(projetil_remover)

                for projetil_boss_obj in projeteis_boss[:]:
                    projetil_boss_obj["rect"].x += projetil_boss_obj["velocidade_x"]
                    projetil_boss_obj["rect"].y += projetil_boss_obj["velocidade_y"]

                    if projetil_boss_obj["rect"].colliderect(jogador):
                        if not escudo_ativo:
                            explosoes.append(criar_explosao_efeitos(projetil_boss_obj["rect"].centerx,
                                                                    projetil_boss_obj["rect"].centery, 40))
                            projeteis_boss.remove(projetil_boss_obj)
                            vida_jogador -= 1
                            if vida_jogador <= 0:
                                game_over = True
                        else:
                            explosoes.append(criar_explosao_efeitos(projetil_boss_obj["rect"].centerx,
                                                                    projetil_boss_obj["rect"].centery, 20))
                            projeteis_boss.remove(projetil_boss_obj)
                            pontuacao += 10

                    elif (projetil_boss_obj["rect"].top > altura or
                          projetil_boss_obj["rect"].left < 0 or
                          projetil_boss_obj["rect"].right > largura):
                        projeteis_boss.remove(projetil_boss_obj)
                    else:
                        tela.blit(projetil_boss_img, projetil_boss_obj["rect"])

                meteoros = [meteoro_final for meteoro_final in meteoros if meteoro_final["rect"].y < altura]

                # Desenhar efeitos visuais
                desenhar_meteoros_congelados(tela)
                desenhar_bosses_congelados(tela)
                desenhar_drones_congelados(tela)
                desenhar_escudo(tela)
                desenhar_efeito_velocidade(tela)
                desenhar_lazer_jogador(tela)  # Substituído pela função melhorada

                # Desenhar drones
                for drone in drones:
                    tela.blit(drone_img, drone.rect)
                    drone.desenhar_escudo(tela)

                    barra_largura = 30
                    barra_altura = 4
                    x = drone.rect.centerx - barra_largura // 2
                    y = drone.rect.top - 8
                    pygame.draw.rect(tela, (255, 0, 0), (x, y, barra_largura, barra_altura))
                    vida_largura = int((drone.vida / 3) * barra_largura)
                    pygame.draw.rect(tela, (255, 255, 0), (x, y, vida_largura, barra_altura))

                for boss_desenho in bosses:
                    if isinstance(boss_desenho, BossNivel15):
                        # Desenhar boss nível 15
                        tela.blit(mega_boss_img, boss_desenho.rect)
                        boss_desenho.desenhar_barra_vida(tela)
                        boss_desenho.desenhar_escudo(tela)

                        # Desenhar bosses gêmeos
                        for gemeo in boss_desenho.bosses_gemeos:
                            if gemeo.usar_lazer:
                                tela.blit(boss_menor_img, gemeo.rect)
                            else:
                                tela.blit(boss_img, gemeo.rect)
                            gemeo.desenhar_barra_vida(tela)
                            gemeo.desenhar_escudo(tela)

                    elif isinstance(boss_desenho, BossGabriel):
                        # Desenhar boss Gabriel
                        tela.blit(boss_gabriel_img, boss_desenho.rect)
                        boss_desenho.desenhar_barra_vida(tela)
                        boss_desenho.desenhar_escudo(tela)

                    else:
                        # Bosses normais
                        if boss_desenho.tipo_boss == 3:
                            tela.blit(mega_boss_img, boss_desenho.rect)
                        elif boss_desenho.tipo_boss == 2 and boss_desenho.usar_lazer:
                            tela.blit(boss_menor_img, boss_desenho.rect)
                        else:
                            tela.blit(boss_img, boss_desenho.rect)

                        boss_desenho.desenhar_barra_vida(tela)
                        boss_desenho.desenhar_escudo(tela)

                for explosao_final in explosoes[:]:
                    tempo_decorrido_explosao_final = pygame.time.get_ticks() - explosao_final["tempo_inicio"]
                    if tempo_decorrido_explosao_final > explosao_final["duracao"]:
                        explosoes.remove(explosao_final)
                    else:
                        desenhar_explosao(tela, explosao_final)

                atualizar_pontuacao()

                if naves_imagens:
                    tela.blit(naves_imagens[nave_selecionada], jogador)

            desenhar_interface()

            if game_over:
                texto_gameover = fonte.render('GAME OVER', True, (255, 0, 0))
                texto_reiniciar = fonte.render('Pressione R para reiniciar', True, (255, 255, 255))
                tela.blit(texto_gameover, (largura // 2 - 80, altura // 2 - 50))
                tela.blit(texto_reiniciar, (largura // 2 - 150, altura // 2))

            pygame.display.flip()
            clock.tick(60)

        salvar_progresso()

pygame.quit()
