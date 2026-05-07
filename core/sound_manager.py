import pygame
import array as _array
import math
import random

from typing import List, Optional, Tuple
from config import *


class SoundManager:
    RATE = 44100

    def __init__(self):
        self.enabled = bool(pygame.mixer.get_init())
        if not self.enabled:
            return
        _, _, self._ch = pygame.mixer.get_init()
        try:
            self.snd_shoot        = self._make_shoot()
            self.snd_exp_sm       = self._make_explosion(0.20, 350)
            self.snd_exp_md       = self._make_explosion(0.35, 160)
            self.snd_exp_lg       = self._make_explosion(0.52,  75)
            self.snd_death        = self._make_death()
            self.snd_thruster     = self._make_thruster()
            self.snd_powerup      = self._make_powerup()
            self.snd_laser_hum    = self._make_laser_hum()
            self.snd_bomb         = self._make_bomb()
            self.snd_hunter_alert = self._make_hunter_alert()
            self.snd_music        = self._make_music()

            self.snd_shoot       .set_volume(VOL_SHOOT)
            self.snd_exp_sm      .set_volume(VOL_EXP_SM)
            self.snd_exp_md      .set_volume(VOL_EXP_MD)
            self.snd_exp_lg      .set_volume(VOL_EXP_LG)
            self.snd_death       .set_volume(VOL_DEATH)
            self.snd_thruster    .set_volume(VOL_THRUSTER)
            self.snd_powerup     .set_volume(VOL_POWERUP)
            self.snd_laser_hum   .set_volume(VOL_LASER)
            self.snd_bomb        .set_volume(VOL_BOMB)
            self.snd_hunter_alert.set_volume(VOL_HUNTER_ALERT)
            self.snd_music       .set_volume(VOL_MUSIC)

            # Canais fixos: 0=música, 1=propulsor, 2=laser, 3=alerta caçador
            self._music_ch  = pygame.mixer.Channel(0)
            self._thrust_ch = pygame.mixer.Channel(1)
            self._laser_ch  = pygame.mixer.Channel(2)
            self._alert_ch  = pygame.mixer.Channel(3)
        except Exception as exc:
            print(f"[SoundManager] falha ao gerar sons: {exc}")
            self.enabled = False

    # ── conversão ─────────────────────────────────────────────────────────────
    def _buf(self, mono: List[float]) -> pygame.mixer.Sound:
        clamp = lambda v: max(-32767, min(32767, int(v * 32767)))
        if self._ch == 2:
            data: List[int] = []
            for s in mono:
                v = clamp(s); data.append(v); data.append(v)
        else:
            data = [clamp(s) for s in mono]
        return pygame.mixer.Sound(buffer=_array.array('h', data))

    # ── sons ──────────────────────────────────────────────────────────────────
    def _make_shoot(self):
        R, dur = self.RATE, 0.13
        n = int(R * dur)
        out = []
        for i in range(n):
            t = i / R; frq = 1100 - 520*(i/n); env = (1 - i/n)**1.8
            out.append(math.sin(2*math.pi*frq*t) * env * 0.70)
        return self._buf(out)

    def _make_explosion(self, dur: float, low_hz: float):
        R = self.RATE; n = int(R*dur)
        rng = random.Random(int(low_hz*13)); out = []
        for i in range(n):
            t = i/R; env = (1-t/dur)**2
            noise = rng.uniform(-1,1); tone = math.sin(2*math.pi*low_hz*t)
            out.append((noise*0.74 + tone*0.26)*env*0.88)
        return self._buf(out)

    def _make_death(self):
        R, dur = self.RATE, 1.5; n = int(R*dur)
        rng = random.Random(42); out = []
        for i in range(n):
            t = i/R; env = (1-t/dur)**1.05
            noise = rng.uniform(-1,1); frq = 190*(1-0.60*t/dur)
            tone = math.sin(2*math.pi*frq*t); harm = math.sin(2*math.pi*frq*1.5*t)*0.38
            out.append((noise*0.38 + tone*0.44 + harm*0.18)*env*0.90)
        return self._buf(out)

    def _make_thruster(self):
        R, dur = self.RATE, 0.4; n = int(R*dur)
        rng = random.Random(77); out = []
        for i in range(n):
            t = i/R; noise = rng.uniform(-1,1)
            tone1 = math.sin(2*math.pi*95 *t)*0.42
            tone2 = math.sin(2*math.pi*190*t)*0.18
            tone3 = math.sin(2*math.pi*285*t)*0.08
            mod = 1.0 + 0.12*math.sin(2*math.pi*18*t)
            out.append((noise*0.32 + tone1 + tone2 + tone3)*mod*0.52)
        fade = int(R*0.04)
        for i in range(fade):
            t = i/fade; out[i] *= t; out[-(i+1)] *= t
        return self._buf(out)

    def _make_powerup(self):
        R, dur = self.RATE, 0.28; n = int(R*dur); out = []
        for i in range(n):
            t = i/R; env = (1-t/dur)**1.4
            s  = math.sin(2*math.pi*660 *t)*0.55
            s += math.sin(2*math.pi*990 *t)*0.30
            s += math.sin(2*math.pi*1320*t)*0.15
            out.append(s*env*0.75)
        return self._buf(out)

    def _make_laser_hum(self):
        """Zumbido elétrico para o feixe contínuo — loop de 0.5 s."""
        R, dur = self.RATE, 0.5; n = int(R*dur)
        rng = random.Random(55); out = []
        for i in range(n):
            t = i/R
            s  = math.sin(2*math.pi*440 *t)*0.35
            s += math.sin(2*math.pi*880 *t)*0.20
            s += math.sin(2*math.pi*1760*t)*0.10
            s *= 1.0 + 0.10*math.sin(2*math.pi*30*t)  # shimmer
            s += rng.uniform(-1,1)*0.04            # textura
            out.append(s*0.42)
        fade = int(R*0.04)
        for i in range(fade):
            t = i/fade; out[i] *= t; out[-(i+1)] *= t
        return self._buf(out)

    def _make_bomb(self):
        """Explosão grave e pesada para a bomba em área."""
        R, dur = self.RATE, 0.9; n = int(R*dur)
        rng = random.Random(33); out = []
        for i in range(n):
            t = i/R; env = (1-t/dur)**1.3
            noise = rng.uniform(-1,1)
            tone1 = math.sin(2*math.pi*40*t)
            tone2 = math.sin(2*math.pi*80*t)*0.50
            # pitch descendo para realismo
            tone3 = math.sin(2*math.pi*(38*(1-0.4*t/dur))*t)*0.30
            out.append((noise*0.45 + tone1*0.30 + tone2*0.15 + tone3*0.10)*env*0.95)
        return self._buf(out)

    def _make_hunter_alert(self):
        """Dois beeps ascendentes em loop — aviso de caçador se aproximando."""
        R, dur = self.RATE, 0.7; n = int(R * dur); out = []
        for i in range(n):
            t = i / R; phase = t / dur
            if phase < 0.35:
                env = math.sin(math.pi * phase / 0.35)
                s   = math.sin(2 * math.pi * 740 * t) * env
            elif phase < 0.70:
                env = math.sin(math.pi * (phase - 0.35) / 0.35)
                s   = math.sin(2 * math.pi * 1040 * t) * env
            else:
                s = 0.0
            out.append(s * 0.55)
        fade = int(R * 0.02)
        for i in range(fade):
            out[i] *= i / fade; out[-(i+1)] *= i / fade
        return self._buf(out)

    def _make_music(self):
        R, dur = self.RATE, 8.0; n = int(R*dur); out = []
        for i in range(n):
            t = i/R
            s  = math.sin(2*math.pi*55.0 *t)*0.33
            s += math.sin(2*math.pi*82.5 *t)*0.17
            s += math.sin(2*math.pi*110.0*t)*0.11
            s += math.sin(2*math.pi*165.0*t)*0.06
            f1 = 220 + 28*math.sin(2*math.pi*(1.0/dur)*t)
            s += math.sin(2*math.pi*f1*t)*0.07
            f2 = 330 + 18*math.sin(2*math.pi*(2.0/dur)*t)
            s += math.sin(2*math.pi*f2*t)*0.04
            lfo = 0.52 + 0.48*math.sin(2*math.pi*(1.0/dur)*t)
            out.append(s*lfo*0.46)
        fade = int(R*0.12)
        for i in range(fade):
            t = i/fade; out[i] *= t; out[-(i+1)] *= t
        return self._buf(out)

    # ── API pública ───────────────────────────────────────────────────────────
    def play_shoot(self):
        if self.enabled: self.snd_shoot.play()

    def play_explosion(self, size: str):
        if not self.enabled: return
        {'large': self.snd_exp_lg,
         'medium': self.snd_exp_md,
         'small': self.snd_exp_sm}[size].play()

    def play_death(self):
        if self.enabled: self.snd_death.play()

    def play_thruster(self):
        if self.enabled and not self._thrust_ch.get_busy():
            self._thrust_ch.play(self.snd_thruster, -1)

    def stop_thruster(self):
        if self.enabled: self._thrust_ch.stop()

    def play_powerup(self):
        if self.enabled: self.snd_powerup.play()

    def play_laser_hum(self):
        if self.enabled and not self._laser_ch.get_busy():
            self._laser_ch.play(self.snd_laser_hum, -1)

    def stop_laser_hum(self):
        if self.enabled: self._laser_ch.stop()

    def play_bomb(self):
        if self.enabled: self.snd_bomb.play()

    def play_hunter_alert(self):
        if self.enabled and not self._alert_ch.get_busy():
            self._alert_ch.play(self.snd_hunter_alert, -1)

    def stop_hunter_alert(self):
        if self.enabled: self._alert_ch.stop()

    def start_music(self):
        if self.enabled: self._music_ch.play(self.snd_music, -1)

    def stop_music(self):
        if self.enabled: self._music_ch.stop()
