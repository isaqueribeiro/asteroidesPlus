# ══════════════════════════════════════════════════════════════════════════════
#  config.py — Configurações do jogo ASTEROIDES PLUS 2.0
#  Edite os valores abaixo para ajustar o comportamento do jogo.
# ══════════════════════════════════════════════════════════════════════════════

# ── Tela ──────────────────────────────────────────────────────────────────────
WIDTH  = 800
HEIGHT = 600
FPS    = 60

# ── Cores (R, G, B) ───────────────────────────────────────────────────────────
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GREEN   = (0,   255, 0)
YELLOW  = (255, 220, 0)
CYAN    = (0,   220, 255)
RED     = (255, 60,  60)
ORANGE  = (255, 140, 0)
GRAY    = (140, 140, 140)
DARK_BG = (4,   6,   20)

# ── Jogador ───────────────────────────────────────────────────────────────────
ROT_SPEED   = 4.0    # graus rotacionados por frame
ACCEL       = 0.22   # aceleração por frame (px/frame²)
MAX_SPEED   = 7.0    # velocidade máxima (px/frame)
FRICTION    = 0.974  # multiplicador de velocidade por frame (1.0 = sem atrito)
INVINCIBLE  = 3.0    # segundos de invulnerabilidade após respawn
MAX_LIVES   = 5      # máximo de vidas acumuláveis
START_LIVES = 3      # vidas iniciais

# ── Projétil padrão ───────────────────────────────────────────────────────────
BULLET_SPD  = 10.0   # velocidade (px/frame)
BULLET_LIFE = 65     # duração em frames antes de sumir

# ── Nomes das armas (ordem de exibição no menu) ────────────────────────────────
GAME_NAME = 'ASTEROIDES PLUS 2.0'
WEAPON_NAMES = ['BOMBA', 'TRIPLO', 'LASER', 'ESPALHADO', 'TRASEIRO']
MENU, PLAYING, PAUSED, GAME_OVER = 'menu', 'playing', 'paused', 'gameover'

# ── Asteroides ────────────────────────────────────────────────────────────────
AST_INFO = {
    #          raio  pontos  filho     filhos  vel_min  vel_max
    'large':  dict(radius=42, pts=25,  child='medium', nkids=2, spd_min=0.2, spd_max=0.5),
    'medium': dict(radius=22, pts=50,  child='small',  nkids=2, spd_min=0.5, spd_max=1.5),
    'small':  dict(radius=11, pts=100, child=None,     nkids=0, spd_min=1.0, spd_max=2.0),
}

# ── Dificuldade progressiva ───────────────────────────────────────────────────
# Quantidade de asteroides: 3 + pontuação // DIFF_AST_STEP  (máx DIFF_AST_MAX)
DIFF_AST_STEP = 1000
DIFF_AST_MAX  = 12

# Multiplicador de velocidade: 1.0 + (pontuação // DIFF_SPEED_STEP) * 0.25
# (máx DIFF_SPEED_MAX)
DIFF_SPEED_STEP = 5000
DIFF_SPEED_MAX  = 3.0

# Intervalo de spawn: começa em DIFF_SPAWN_START, reduz a cada
# DIFF_SPAWN_STEP pontos, até o mínimo DIFF_SPAWN_MIN (segundos)
DIFF_SPAWN_START = 3.0
DIFF_SPAWN_STEP  = 3000
DIFF_SPAWN_DEC   = 0.15
DIFF_SPAWN_MIN   = 1.5

# ── Pontuação ─────────────────────────────────────────────────────────────────
STREAK_NEEDED = 5        # mortes consecutivas para bônus de série
STREAK_BONUS  = 500      # pontos do bônus
EXTRA_LIFE_PTS = 10_000  # pontos para ganhar vida extra

# ── Power-ups ─────────────────────────────────────────────────────────────────
WEAPON_DURATION    = 60.0   # segundos de duração após coletar
PU_SPAWN_MIN       = 12.0   # intervalo mínimo entre spawns (s)
PU_SPAWN_MAX       = 22.0   # intervalo máximo entre spawns (s)
PU_MAX_ON_SCREEN   = 2      # máximo de power-ups simultâneos na tela
PU_LIFETIME        = 15.0   # segundos até sumir se não coletado
PU_SPEED           = 1.2    # velocidade de movimento (px/frame, fixa)

# ── Armas — cooldown em frames (0 = sem projéteis / controle externo) ─────────
WEAPON_CD = {
    'NORMAL':    15,
    'BOMBA':     15,
    'TRIPLO':    16,
    'LASER':      0,   # sem projéteis — tratado como feixe contínuo
    'ESPALHADO': 22,
    'TRASEIRO':  15,
}

# ── Armas — limite de projéteis simultâneos ───────────────────────────────────
WEAPON_MAX_BULLETS = {
    'NORMAL':    10,
    'BOMBA':      3,
    'TRIPLO':    14,
    'LASER':      0,
    'ESPALHADO': 18,
    'TRASEIRO':  12,
}

# ── Armas — cores dos projéteis e HUD (R, G, B) ──────────────────────────────
WEAPON_COLOR = {
    'NORMAL':    GREEN,
    'BOMBA':     (255, 140,   0),   # laranja
    'TRIPLO':    (255, 220,   0),   # amarelo
    'LASER':     (220,  30,  30),   # vermelho
    'ESPALHADO': (180,   0, 255),   # roxo
    'TRASEIRO':  ( 60, 180, 255),   # azul céu
}

# ── Armas — descrições exibidas no menu ───────────────────────────────────────
WEAPON_DESC = {
    'BOMBA':     'BOMBA     — explosão em área',
    'TRIPLO':    'TRIPLO    — leque de 3 tiros',
    'LASER':     'LASER     — feixe contínuo',
    'ESPALHADO': 'ESPALHADO — 5 direções',
    'TRASEIRO':  'TRASEIRO  — frente + trás',
}

# ── Bomba ─────────────────────────────────────────────────────────────────────
BOMB_EXPLOSION_RADIUS = 126   # raio de destruição em área (px)

# ── Laser contínuo ────────────────────────────────────────────────────────────
LASER_DAMAGE_CD = 0.22   # segundos entre cada dano aplicado pelo feixe

# ── Caçador (nave inimiga) ────────────────────────────────────────────────────
HUNTER_BASE_SPEED = 1.8    # px/frame no level 1
HUNTER_SPEED_INC  = 0.40   # px/frame adicional por level
HUNTER_TURN_SPEED = 2.8    # graus/frame (steering máximo)
HUNTER_LIFETIME   = 25.0   # segundos até desaparecer sozinho
HUNTER_PTS_BASE   = 500    # pontos por abate (× nível atual)
HUNTER_WARN_DELAY = 3.0    # segundos de aviso antes de aparecer

# ── Som ───────────────────────────────────────────────────────────────────────
VOL_SHOOT    = 0.38
VOL_EXP_SM   = 0.50
VOL_EXP_MD   = 0.62
VOL_EXP_LG   = 0.72
VOL_DEATH    = 0.80
VOL_THRUSTER = 0.28
VOL_POWERUP  = 0.60
VOL_LASER    = 0.35
VOL_BOMB     = 0.90
VOL_MUSIC         = 0.22
VOL_HUNTER_ALERT  = 0.68
