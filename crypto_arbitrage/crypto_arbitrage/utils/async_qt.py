from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import asyncio


class AsyncQtBridge(QObject):
    update_signal = pyqtSignal(str)
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()
        self.timer = QTimer()
        self.timer.timeout.connect(self._process_events)
        self.timer.start(100)  # 100ms interval

    def _process_events(self):
        """Обработка asyncio событий в Qt event loop"""
        self.loop.call_soon(self.loop.stop)
        self.loop.run_forever()

    def start_arbitrage(self, engine, **params):
        """Запуск арбитража в фоновом режиме"""

        async def _run():
            try:
                self.update_signal.emit("Starting arbitrage search...")
                opportunities = await engine.find_arbitrage_opportunities(**params)
                self.finished.emit(opportunities)
            except Exception as e:
                self.update_signal.emit(f"Error: {str(e)}")
                self.finished.emit([])

        self.loop.create_task(_run())

    def close(self):
        """Корректное завершение"""
        self.timer.stop()
        self.loop.close()