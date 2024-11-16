import customtkinter as ctk
import requests
import unicodedata
import random
import re
from PIL import Image, ImageTk
from io import BytesIO

class Chatbot:
    def __init__(self, master):
        self.master = master
        master.title("Kilua")
        master.geometry("600x600")

        # Configuração da janela
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)

        ctk.set_appearance_mode("dark")  # "light" ou "dark"
        ctk.set_default_color_theme("dark-blue")  # Temas disponíveis: "blue", "green", "dark-blue"

        # Área de texto
        self.text_area = ctk.CTkTextbox(master, width=500, height=300, wrap="word")
        self.text_area.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.text_area.insert(ctk.END, "Olá, sou Kilua, sua assistente virtual sobre climas. Como posso te ajudar hoje?\n")
        self.text_area.configure(state="normal")

        # Campo de entrada
        self.entry = ctk.CTkEntry(master, width=400, placeholder_text="Digite sua pergunta aqui...")
        self.entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.entry.bind("<Return>", self.process_input)

        # Botão de envio
        self.send_button = ctk.CTkButton(master, text="Enviar", fg_color="blue", command=self.process_input)
        self.send_button.grid(row=2, column=0, padx=20, pady=10)

        # Label para exibir o ícone do clima
        self.weather_icon_label = ctk.CTkLabel(master)
        self.weather_icon_label.grid(row=3, column=0, padx=20, pady=10)

        # Lista de cidades para comparação
        self.city_list = ["São Paulo", "Nova York", "Tóquio", "Paris", "Londres", "Sydney"]

    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        normalized_input = self.normalize_text(user_input)
        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Você: " + user_input + "\n")
        self.text_area.configure(state="disabled")
        self.entry.delete(0, ctk.END)

        response = self.get_weather_response(normalized_input)
        
        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, f"Kilua: {response}\n")
        self.text_area.configure(state="disabled")

        self.master.update_idletasks()

    def normalize_text(self, text):
        text = text.strip().lower()
        text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
        return text

    def get_weather_response(self, text):
        if re.search(r"(tempo|clima|previsao).*(em|de|na|em um local)", text):
            city = self.extract_city_from_input(text)
            if city:
                return self.get_weather(city)
            else:
                return "Desculpe, não consegui identificar a cidade. Você pode tentar novamente?"
        
        elif "qual lugar mais quente hoje" in text:
            return self.get_hottest_city()
        elif "qual lugar mais frio hoje" in text:
            return self.get_coldest_city()
        elif "qual lugar mais umido hoje" in text or "qual lugar com mais umidade" in text:
            return self.get_most_humid_city()
        elif "qual cidade esta com mais ventos" in text or "qual lugar mais ventoso" in text:
            return self.get_most_windy_city()
        else:
            return "Desculpe, não entendi sua pergunta. Você pode perguntar sobre o clima em uma cidade?"

    def extract_city_from_input(self, text):
        match = re.search(r"(em|de|na|para)\s+([\w\s]+)", text)
        if match:
            city = match.group(2).strip()
            if len(city) > 2:
                return city
        return None

    def get_weather(self, city):
        try:
            api_key = "f191cf42850e76128abd8a8f5ff8c4b0"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=pt_br&units=metric"

            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                weather = data["weather"][0]["description"]
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                icon_code = data["weather"][0]["icon"]
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"

                icon_response = requests.get(icon_url)
                img_data = icon_response.content
                img = Image.open(BytesIO(img_data))
                img = img.resize((50, 50))
                icon_image = ImageTk.PhotoImage(img)

                self.weather_icon_label.configure(image=icon_image)
                self.weather_icon_label.image = icon_image

                return f"Atualmente, o clima em {city} é {weather} com temperatura de {temp}°C.\nUmidade: {humidity}% | Vento: {wind_speed} m/s"
            elif response.status_code == 404:
                return f"Não consegui encontrar informações sobre o clima em {city}. Verifique o nome da cidade."
            else:
                return f"Erro ao buscar informações. Código: {response.status_code}."
        except Exception as e:
            print("Erro capturado:", e)
            return "Houve um erro ao buscar o clima. Tente novamente mais tarde."

    def get_hottest_city(self):
        return self.compare_cities("max", "quente", "temp")

    def get_coldest_city(self):
        return self.compare_cities("min", "fria", "temp")

    def get_most_humid_city(self):
        return self.compare_cities("max", "úmida", "humidity")

    def get_most_windy_city(self):
        return self.compare_cities("max", "ventosa", "wind_speed")

    def compare_cities(self, comparison, adjective, key):
        city_data = {}
        for city in self.city_list:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=f191cf42850e76128abd8a8f5ff8c4b0&lang=pt_br&units=metric"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                if key == "temp":
                    value = data["main"]["temp"]
                elif key == "humidity":
                    value = data["main"]["humidity"]
                elif key == "wind_speed":
                    value = data["wind"]["speed"]
                city_data[city] = value
        
        if city_data:
            selected_city = (
                min(city_data, key=city_data.get)
                if comparison == "min"
                else max(city_data, key=city_data.get)
            )
            selected_value = city_data[selected_city]
            return f"A cidade mais {adjective} hoje é {selected_city} com {selected_value}."
        else:
            return f"Não foi possível determinar a cidade mais {adjective} no momento."

if __name__ == "__main__":
    root = ctk.CTk()
    chatbot = Chatbot(root)
    root.mainloop()
