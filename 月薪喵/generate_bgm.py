"""
生成桌面宠物的背景音乐 (8bit风格轻快BGM)
使用numpy生成波形，保存为WAV文件
"""
import numpy as np
import struct
import wave
import os


def generate_bgm(output_path="bgm.wav", duration=16, sample_rate=22050):
    """生成一段轻快的8bit风格循环BGM"""

    # 音符频率 (C大调音阶)
    notes = {
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
        'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25,
        'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
    }

    # 旋律 (音符, 持续时间beat)
    melody = [
        ('E4', 0.5), ('G4', 0.5), ('A4', 0.5), ('B4', 0.5),
        ('C5', 1.0), ('B4', 0.5), ('A4', 0.5),
        ('G4', 1.0), ('E4', 0.5), ('G4', 0.5),
        ('A4', 0.5), ('G4', 0.5), ('E4', 0.5), ('D4', 0.5),
        ('C4', 1.0), ('D4', 0.5), ('E4', 0.5),
        ('G4', 1.0), ('A4', 0.5), ('G4', 0.5),
        ('E4', 0.5), ('D4', 0.5), ('C4', 0.5), ('D4', 0.5),
        ('E4', 1.0), ('G4', 0.5), ('A4', 0.5),
        ('C5', 1.0), ('B4', 0.5), ('A4', 0.5),
        ('G4', 0.5), ('E4', 0.5), ('G4', 0.5), ('A4', 0.5),
        ('G4', 1.5), ('E4', 0.5),
    ]

    # 低音伴奏
    bass_pattern = [
        ('C4', 1.0), ('G3', 1.0), ('A3', 1.0), ('G3', 1.0),
    ]

    bpm = 140
    beat_duration = 60.0 / bpm  # 一个beat的秒数

    total_samples = int(duration * sample_rate)
    audio = np.zeros(total_samples, dtype=np.float64)

    def square_wave(freq, duration_sec, volume=0.15):
        """生成方波（8bit音色）"""
        t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
        wave = np.sign(np.sin(2 * np.pi * freq * t)) * volume
        # 添加简单包络
        attack = int(0.01 * sample_rate)
        release = int(0.05 * sample_rate)
        if len(wave) > attack + release:
            wave[:attack] *= np.linspace(0, 1, attack)
            wave[-release:] *= np.linspace(1, 0, release)
        return wave

    def triangle_wave(freq, duration_sec, volume=0.1):
        """生成三角波（低音音色）"""
        t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
        wave = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
        wave *= volume
        return wave

    # 渲染旋律
    pos = 0  # 当前位置（采样点）
    melody_loop = melody * 4  # 重复足够次数

    for note_name, beats in melody_loop:
        dur = beats * beat_duration
        start = pos
        end = start + int(dur * sample_rate)
        if end >= total_samples:
            end = total_samples
        if start >= total_samples:
            break

        freq = notes.get(note_name, 440)
        segment = square_wave(freq, dur)
        length = min(len(segment), end - start)
        audio[start:start + length] += segment[:length]
        pos = end

    # 渲染低音
    pos = 0
    bass_loop = bass_pattern * 30

    for note_name, beats in bass_loop:
        dur = beats * beat_duration
        start = pos
        end = start + int(dur * sample_rate)
        if end >= total_samples:
            end = total_samples
        if start >= total_samples:
            break

        freq = notes.get(note_name, 196) * 0.5  # 低一个八度
        segment = triangle_wave(freq, dur, volume=0.08)
        length = min(len(segment), end - start)
        audio[start:start + length] += segment[:length]
        pos = end

    # 简单的节拍鼓点 (噪声)
    beat_samples = int(beat_duration * sample_rate)
    for i in range(0, total_samples, beat_samples):
        # 每个beat加一个短噪声
        noise_len = int(0.02 * sample_rate)
        end = min(i + noise_len, total_samples)
        noise = np.random.uniform(-0.03, 0.03, end - i)
        # 快速衰减
        decay = np.exp(-np.linspace(0, 5, len(noise)))
        audio[i:end] += noise * decay

    # 归一化
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.7

    # 转为16位整数
    audio_16bit = (audio * 32767).astype(np.int16)

    # 保存WAV
    with wave.open(output_path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_16bit.tobytes())

    print(f"BGM 生成完成: {output_path} ({duration}秒)")


if __name__ == "__main__":
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bgm.wav")
    generate_bgm(output)
