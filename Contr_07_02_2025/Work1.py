import sys
import time


def loading_bar(duration, length=10):
    """Функция отображения загрузки с анимацией."""
    for i in range(length + 1):
        progress = "=" * i
        spaces = " " * (length - i)
        percent = int((i / length) * 100)
        print(f"\r[{progress}{spaces}] {percent}%", end="")
        time.sleep(duration / length)
    print()


def distance_decorator(func):
    """Декоратор, который вычисляет пройденное расстояние после ускорения."""

    def wrapper(v0, v1, t):
        try:
            v0 = float(v0)
            v1 = float(v1)
            t = float(t)
        except ValueError:
            print("\n[❌] Ошибка: введите числовые значения!")
            sys.exit(1)

        if t == 0:
            print("\n[⚠️] Ошибка: время не может быть 0!")
            sys.exit(1)

        print("\n⏳ Выполняем расчёт...\n")

        print("📊 Данные приняты, начинаем обработку...")
        loading_bar(2)

        # Вычисляем ускорение
        a = func(v0, v1, t)

        print("\n🔄 Рассчитываем пройденное расстояние...")
        loading_bar(5)

        # Вычисляем расстояние
        s = v0 * t + 0.5 * a * t ** 2

        print("\n📏 Расчёт завершён!")
        loading_bar(3)

        print("════════════════════════════")
        print(f"🚀 Пройденное расстояние: {s:.2f} м")
        print("════════════════════════════")

        return a

    return wrapper


@distance_decorator
def compute_acceleration(v0, v1, t):
    """Вычисляет ускорение по формуле a = (v1 - v0) / t"""
    print("\n🛠 Расчёт ускорения...")
    loading_bar(5)
    a = (v1 - v0) / t
    print("════════════════════════════")
    print(f"⚡ Ускорение: {a:.2f} м/с²")
    print("════════════════════════════")
    return a

v0 = input("🔹 Введите начальную скорость (м/с): ")
v1 = input("🔹 Введите конечную скорость (м/с): ")
t = input("🔹 Введите время (с): ")

compute_acceleration(v0, v1, t)