import time
import psutil
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich import box
from sqlalchemy.orm import Session
from database.models import QueueItem, OperationDecision

class TerminalDashboard:
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def generate_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1)
        )
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Header
        layout["header"].update(Panel("[bold cyan]🤖 AI CEO - Operations Dashboard[/bold cyan]", style="bold white"))
        
        # Left: Queue Status
        queue_table = Table(box=box.SIMPLE, expand=True)
        queue_table.add_column("Task ID", style="dim")
        queue_table.add_column("Type", style="bold yellow")
        queue_table.add_column("Status", style="bold green")
        
        items = self.db.query(QueueItem).order_by(QueueItem.created_at.desc()).limit(15).all()
        for item in items:
            queue_table.add_row(item.id[:8], item.task_type, item.status)
            
        layout["left"].update(Panel(queue_table, title="Task Queue", border_style="blue"))
        
        # Right: Resources & CEO
        right_layout = Layout()
        right_layout.split_column(
            Layout(name="resources", size=8),
            Layout(name="ceo")
        )
        
        # Resources
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        res_text = f"CPU Load: {cpu}%\nRAM Usage: {ram}%\nDisk Usage: {psutil.disk_usage('/').percent}%"
        right_layout["resources"].update(Panel(res_text, title="System Health", border_style="red"))
        
        # CEO Decisions
        ceo_table = Table(box=box.SIMPLE, expand=True)
        ceo_table.add_column("Decision", style="bold magenta")
        ceo_table.add_column("Reason")
        
        decs = self.db.query(OperationDecision).order_by(OperationDecision.created_at.desc()).limit(10).all()
        for d in decs:
            ceo_table.add_row(d.decision_type, d.justification)
            
        right_layout["ceo"].update(Panel(ceo_table, title="CEO Decisions", border_style="green"))
        
        layout["right"].update(right_layout)
        return layout

    def start(self):
        with Live(self.generate_layout(), refresh_per_second=1) as live:
            try:
                while True:
                    self.db.commit() # Refresh session
                    live.update(self.generate_layout())
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
