import customtkinter as ctk
import requests
import unicodedata
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

        ctk.set_appearance_mode("dark")  
        ctk.set_default_color_theme("dark-blue")  

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
        self.send_button = ctk.CTkButton(master, text="Consultar", fg_color="blue", command=self.process_input)
        self.send_button.grid(row=2, column=0, padx=20, pady=10)

        # Botão de limpar histórico
        self.clear_button = ctk.CTkButton(master, text="Limpar Histórico", fg_color="red", command=self.clear_history)
        self.clear_button.grid(row=3, column=0, padx=20, pady=10)

        # Label para exibir o ícone do clima
        self.weather_icon_label = ctk.CTkLabel(master)
        self.weather_icon_label.grid(row=4, column=0, padx=20, pady=10)

        # Label de carregamento
        self.loading_label = ctk.CTkLabel(master, text="Carregando...", fg_color="gray", text_color="white")
        self.loading_label.grid(row=5, column=0, padx=20, pady=10)
        self.loading_label.grid_forget()  # Inicialmente invisível

        # Lista de cidades para comparação
        self.city_list = ["paulista", "São Paulo", "Recife", "Olinda", "Nova York", "Tóquio", "Paris", "Londres", "Sydney", 
    "Rio de Janeiro", "Belo Horizonte", "Brasília", "Fortaleza", "Salvador", "Curitiba", "Manaus", "Porto Alegre", 
    "São Luís", "Vitória", "Natal", "Florianópolis", "Maceió", "João Pessoa", "Campo Grande", "Cuiabá", 
    "Buenos Aires", "Madrid", "Berlim", "Roma", "Lima", "Los Angeles", "Chicago", "Cidade do Cabo", "Pequim", 
    "Dubai", "Istambul", "Bangkok", "Moscovo", "Cairo", "Seul", "Toronto", "Vancouver", "Los Angeles", "Melbourne"]

    def process_input(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        normalized_input = self.normalize_text(user_input)
        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, "Você: " + user_input + "\n")
        self.text_area.configure(state="disabled")
        self.entry.delete(0, ctk.END)

        # Mostrar "Carregando..."
        self.loading_label.grid(row=5, column=0, padx=20, pady=10)

        # Processar a resposta
        response = self.get_weather_response(normalized_input)

        # Esconder "Carregando..." após resposta
        self.loading_label.grid_forget()

        self.text_area.configure(state="normal")
        self.text_area.insert(ctk.END, f"Kilua: {response}\n")
        self.text_area.configure(state="disabled")

        self.master.update_idletasks()

    def normalize_text(self, text):
        text = text.strip().lower()
        text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
        return text

    def get_weather_response(self, text):
        # Detecção de variações de perguntas sobre clima nos próximos dias ou clima atual
        if re.search(r"(previsao|clima|tempo).*(próximos dias|dias seguintes|proximos dias em|como estará o clima|qual será o clima)", text):
            city = self.extract_city_from_input(text)
            if city:
                return self.get_weather_forecast(city)
            else:
                return "Desculpe, não consegui identificar a cidade. Você pode tentar novamente?"
        
        elif re.search(r"(clima|tempo|previsao).*(agora|hoje|atualmente|hoje mesmo)", text):
            city = self.extract_city_from_input(text)
            if city:
                return self.get_weather(city)
            else:
                return "Desculpe, não consegui identificar a cidade. Você pode tentar novamente?"
        
        elif re.search(r"(umidade|vento|temperatura|quente|frio)", text):
            city = self.extract_city_from_input(text)
            if city:
                return self.get_weather_conditions(city, text)
            else:
                return "Desculpe, não consegui identificar a cidade. Você pode tentar novamente?"
        
        elif re.search(r"(cidade mais quente|cidade mais fria|cidade mais ventosa)", text):
            return self.get_extreme_weather_conditions()

        else:
            return "Desculpe, não entendi sua pergunta. Você pode perguntar sobre o clima em uma cidade?"

    def extract_city_from_input(self, text):
        # para tentar extrair a cidade do texto de entrada
        for city in self.city_list:
            if city.lower() in text:
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

    def get_weather_conditions(self, city, text):
        try:
            api_key = "f191cf42850e76128abd8a8f5ff8c4b0"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=pt_br&units=metric"

            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]

                if "quente" in text:
                    return f"A temperatura em {city} é de {temp}°C."
                elif "frio" in text:
                    return f"A temperatura em {city} é de {temp}°C."
                elif "umidade" in text:
                    return f"A umidade em {city} é de {humidity}%. "
                elif "vento" in text:
                    return f"A velocidade do vento em {city} é de {wind_speed} m/s."
                else:
                    return f"Em {city}, a temperatura é de {temp}°C, umidade: {humidity}%, vento: {wind_speed} m/s."
            elif response.status_code == 404:
                return f"Não consegui encontrar informações sobre o clima em {city}. Verifique o nome da cidade."
            else:
                return f"Erro ao buscar informações. Código: {response.status_code}."
        except Exception as e:
            print("Erro capturado:", e)
            return "Houve um erro ao buscar as condições climáticas. Tente novamente mais tarde."

    def get_extreme_weather_conditions(self):
        # Aqui, ainda estarei implementando uma lógica para determinar qual cidade está mais quente, mais fria ou mais ventosa.
        return "Essa funcionalidade ainda precisa ser implementada."

    def get_weather_forecast(self, city):
        try:
            api_key = "f191cf42850e76128abd8a8f5ff8c4b0"
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&lang=pt_br&units=metric"

            response = requests.get(url)
            data = response.json()

            if response.status_code == 200:
                forecast = data["list"]
                forecast_response = f"Previsão do clima nos próximos dias em {city}:\n"

                for day in forecast[:5]:  # Limitando para 5 dias
                    date = day["dt_txt"]
                    weather = day["weather"][0]["description"]
                    temp = day["main"]["temp"]
                    humidity = day["main"]["humidity"]
                    wind_speed = day["wind"]["speed"]
                    forecast_response += f"\n{date}: {weather} | Temp: {temp}°C | Umidade: {humidity}% | Vento: {wind_speed} m/s"

                return forecast_response
            elif response.status_code == 404:
                return f"Não consegui encontrar informações sobre a previsão do clima em {city}. Verifique o nome da cidade."
            else:
                return f"Erro ao buscar previsão do clima. Código: {response.status_code}."
        except Exception as e:
            print("Erro capturado:", e)
            return "Houve um erro ao buscar a previsão do clima. Tente novamente mais tarde."

    def clear_history(self):
        # Limpa o conteúdo da text_area
        self.text_area.configure(state="normal")
        self.text_area.delete(1.0, ctk.END)
        self.text_area.insert(ctk.END, "Olá, sou Kilua, sua assistente virtual sobre climas. Como posso te ajudar hoje?\n")
        self.text_area.configure(state="disabled")

if __name__ == "__main__":
    root = ctk.CTk()
    chatbot = Chatbot(root)
    root.mainloop()