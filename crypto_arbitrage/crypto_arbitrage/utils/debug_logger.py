import sys
from datetime import datetime
from PyQt6.QtWidgets import QTextEdit


class DebugLogger:
    def __init__(self, output_widget: QTextEdit = None):
        self.output_widget = output_widget
        self.log_buffer = []

    def log(self, message: str):
        """Логирование сообщения с временной меткой"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        full_message = f"[{timestamp}] {message}"

        # Вывод в консоль
        print(full_message)

        # Вывод в GUI
        if self.output_widget:
            self.output_widget.append(full_message)
            self.output_widget.verticalScrollBar().setValue(
                self.output_widget.verticalScrollBar().maximum()
            )

        # Сохранение в буфер
        self.log_buffer.append(full_message)

    def get_logs(self) -> str:
        """Получить все логи"""
        return "\n".join(self.log_buffer)


# Глобальный экземпляр логгера
logger = DebugLogger()