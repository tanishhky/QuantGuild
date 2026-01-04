import tkinter as tk
from tkinter import ttk,messagebox
import json
import time
import random

DATA_FILE = "equities.json"

def fetch_mock_api(symbol):
    return {
        "price":100
    }

def mock_llm_response(message):
    return f"Mock LLM Response for {message}"

class TradingBotGUI:
    def __init__(self,root):
        self.root = root
        self.root.title("AI Trading Bot")
        self.equities=self.load_equities()
        self.system_running = False
    
        self.form_frame=tk.Frame(root)
        self.form_frame.pack(padx=10,pady=10)
    
        tk.Label(self.form_frame,text="Symbol:").grid(row=0,column=0,padx=5,pady=5)
        self.symbol_entry=tk.Entry(self.form_frame)
        self.symbol_entry.grid(row=0,column=1,padx=5,pady=5)

        tk.Label(self.form_frame,text="Levels:").grid(row=0,column=2,padx=5,pady=5)
        self.levels_entry=tk.Entry(self.form_frame)
        self.levels_entry.grid(row=0,column=3,padx=5,pady=5)

        tk.Label(self.form_frame,text="Drawdown:").grid(row=0,column=4,padx=5,pady=5)
        self.drawdown_entry=tk.Entry(self.form_frame)
        self.drawdown_entry.grid(row=0,column=5,padx=5,pady=5)

        self.add_button=tk.Button(self.form_frame,text="Add Equity",command=self.add_equity)
        self.add_button.grid(row=0,column=6,padx=5,pady=5)

        #Table to track trades
        self.tree=ttk.Treeview(root,columns=("Symbol","Position","Entry Price","Levels","Status"),show="headings")
        for col in ["Symbol","Position","Entry Price","Levels","Status"]:
            self.tree.heading(col,text=col)
            self.tree.column(col,width=120)
        self.tree.pack(fill=tk.BOTH,expand=True)    

        #Buttons to control the bot
        self.toggle_system_button=tk.Button(root,text="Toggle Selected System",command=self.toggle_selected_system)    
        self.toggle_system_button.pack(pady=5)

        self.remove_button=tk.Button(root,text="Remove Selected Equity",command=self.remove_selected_equity)    
        
        #AI Components
        self.chat_frame=tk.Frame(root)
        self.chat_frame.pack(padx=10,pady=10)

        self.chat_input=tk.Entry(self.chat_frame,width=50)
        self.chat_input.grid(row=0,column=0,sticky="ew",padx=5,pady=5)

        self.send_button=tk.Button(self.chat_frame,text="Send",command=self.send_message)
        self.send_button.grid(row=0,column=1,padx=5,pady=5)

        self.chat_output=tk.Text(self.chat_frame,width=60,height=5, state="disabled")
        self.chat_output.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        #Load Saved Data
        self.refresh_table()

        #Auto Refreshing
        #Auto Refreshing
        self.running=True
        self.auto_update()


    def add_equity(self):
        symbol=self.symbol_entry.get()
        levels=self.levels_entry.get()
        drawdown=self.drawdown_entry.get()

        if not symbol or not levels.isdigit() or not drawdown.replace(".","",1).isdigit():
            messagebox.showerror("Error","Invalid input")
            return

        drawdown=float(drawdown)/100
        levels=int(levels)
        entry_price=fetch_mock_api(symbol)["price"]

        level_prices={i+1 : round(entry_price*(1-drawdown*(i+1)), 2) for i in range(levels)}

        self.equities[symbol]={
            "entry_price":entry_price,
            "levels":level_prices,
            "status":"Off",
            "position":0
        }

        self.save_equities()
        self.refresh_table()

    def toggle_selected_system(self):
        selected_items=self.tree.selection()
        if not selected_items:
            messagebox.showerror("Error","Please select an equity")
            return

        for item in selected_items:
            symbol=self.tree.item(item)["values"][0]
            self.equities[symbol]["status"]="On" if self.equities[symbol]["status"]=="Off" else "Off"
        self.save_equities()
        self.refresh_table()

    def remove_selected_equity(self):
        selected_items=self.tree.selection()
        if not selected_items:
            messagebox.showerror("Error","Please select an equity")
            return

        for item in selected_items:
            symbol=self.tree.item(item)["values"][0]
            del self.equities[symbol]
        self.save_equities()
        self.refresh_table()

    def send_message(self):
        message=self.chat_input.get()
        if not message:
            return

        self.chat_input.delete(0,tk.END)
        self.chat_output.config(state="normal")
        self.chat_output.insert(tk.END,f"You: {message}\n")
        self.chat_output.config(state="disabled")
        self.chat_output.yview(tk.END)

        response=mock_llm_response(message)
        self.chat_output.config(state="normal")
        self.chat_output.insert(tk.END,f"Bot: {response}\n")
        self.chat_output.config(state="disabled")
        self.chat_output.yview(tk.END)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for symbol, data in self.equities.items():
            self.tree.insert("","end",values=(symbol,data["position"],data["entry_price"],data["levels"],data["status"]))


    def auto_update(self):
        if self.running:
            self.update_prices()
            self.root.after(3000, self.auto_update)

    def update_prices(self):
        print("Prices updated") # Placeholder for price update logic
    
    def save_equities(self):
        with open(DATA_FILE,"w") as f:
            json.dump(self.equities,f)  
    
    def load_equities(self):
        try:
            with open(DATA_FILE,"r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def on_close(self):
        self.running=False
        self.save_equities()
        self.root.destroy()

    
if __name__=="__main__":
    root=tk.Tk()
    app=TradingBotGUI(root)
    root.protocol("WM_DELETE_WINDOW",app.on_close)
    root.mainloop()
        