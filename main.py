from flask import Flask, render_template,jsonify,request,session
from flask_cors import CORS
import requests,openai,os
from dotenv.main import load_dotenv
from random import randrange

app = Flask(__name__, static_url_path = '/static')
CORS(app)
app.secret_key ="thisistemporalthingok"
load_dotenv()
API = os.environ.get("OAK")
hist = []
@app.route('/')
def index():


    return render_template('index.html')

@app.route('/ex')
def ex():

    with open('currentchat.txt', 'w+') as f:
        pass
    return render_template('ex.html')

@app.route('/data', methods=['POST'])
def get_data():

    data = request.get_json()
    text=data.get('respuesta')
    pregunta=data.get('pregunta')
    openai.api_key = API
    
    user_input = text
    print(user_input)
    print(pregunta)

  

    guia = []
    with open('guion.txt', encoding="utf-8") as f:
        guia = f.readlines()


    guiaindice = randrange(len(guia))

    print(guiaindice, "d")
    if pregunta > 2:
        print(len(guia))
        print(len(hist))
        x = checkhist(guiaindice,hist,guia)
    moderador_dice = guia[guiaindice]



    moderador = moderador_dice + " " + user_input + " : "
    #print (moderador)

    continuar = []
    with open('continuar.txt', encoding="utf-8") as f:
        continuar = f.readlines()

    x = randrange(len(continuar))

    moderador_continua = continuar[x]

    x = pregunta
    print(x,"ronda")
    roundlen = len(guia) + 3
    print(roundlen)
    if x > roundlen:
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt="Escribe un texto que agradezca al usuario por su participacion y pregunte si quiere expandir alguna idea sobre lo hablado anteriormente",
                temperature=0.7,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )

            model_reply = response['choices'][0]['text']
            # print(response,model_reply)
            mensaje = moderador_continua + model_reply

            return jsonify({"response": True, "message": mensaje})
        except Exception as e:
            print(e)
            error_message = f'Error: {str(e)}'
            return jsonify({"response": False,
                            "message": "Error de conexion de internet con Open IA. Vuelva a intentar la respuesta"})
    elif x > 2:
        try:
            response = openai.Completion.create(
            model="text-davinci-003",
            prompt=moderador,
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        
            model_reply = response['choices'][0]['text']
            #print(response,model_reply)
            mensaje = moderador_continua + model_reply


            return jsonify({"response":True,"message":mensaje})
        except Exception as e:
            print(e)
            error_message = f'Error: {str(e)}'
            return jsonify({"response":False,"message":"Error de conexion de internet con Open IA. Vuelva a intentar la respuesta"})
    else:
        mensaje = "Ok"
        if (x == 0):
            mensaje = "Ok, entendido. Cual es tu edad?"
        if (x == 1):
            mensaje = "Ok, estas en la flor de la vida. Y a que te dedicas o en que trabajas?"       
        if (x == 2):            
            mensaje = "Ahora me gustaria preguntar sobre nuestro tema. Estas preocupado por el cambio climatico?"    
        
        return jsonify({"response":True,"message":mensaje})

import json
@app.route('/chat', methods=['POST'])
def chatbot():
    initialmessage = [
        {"role": "system",
         "content": "Eres modio, un chatbot moderador que se dedica a obtener los pensamientos y opiniones de las personas. Esta recoleccion se hace siguiendo este guion de forma estricta:"
                    "-Presentarse y hacer una pregunta sobre el tema de cambio climatico "
                    "-Hacer una pregunta sobre que entendemos por el cambio climatico "
                    "-Hacer una pregunta sobre los problemas propiciados por el cambio climatico y que son de mayor preocupación para la sociedad "
                    "-Hacer una pregunta sobre el tema de cambio climatico y la responsabilidad que tienen las empresas"
                    "-Hacer una pregunta sobre la responsabilidad que tienen las empresas y sus marcas para apoyar al gobierno en contra del cambio climatico y"
                    "-Hacer una pregunta sobre los beneficios empresariales de adoptar una estrategia enfocada en el cambio climatico"
                    "-Hacer una pregunta sobre las principales iniciativas que las empresas pueden adoptar para combatir el cambio climatico"
                    "-Hacer una pregunta sobre las implicaciones tiene el cambio climatico para el desempeño de las empresas"
                    "-Hacer una pregunta sobre que debe hacer como individuo para ayudar con el problema de cambio climatico"
                    "-Hacer un resumen de las respuestas dadas por el usuario cuando termine de recorrer el guion"
                    "No adiciones informacion a las respuestas"
                    "Comienza la conversacion haciendo una pregunta relacionada al primer item del guion"},
        {"role": "assistant",
         "content": "Hola, soy Modio, un chatbot dedicado a recopilar opiniones sobre el cambio climático. ¿Cómo te afecta el cambio climático en tu día a día y qué medidas crees que se deberían tomar para abordar este problema?"},
    ]
    with open('currentchat.txt', 'r+') as f:
        content = f.read()
        if content:

            initialmessage = []
            f.seek(0,0)
            lines = f.readlines()

            for line in lines:

                linestr = line.replace("\'", "\"")
                msg = json.loads(linestr)

                initialmessage.append(msg)
        else:
            for e in initialmessage:
                f.write(str(e)+"\n")



    data = request.get_json()
    text = data.get('respuesta')
    pregunta = data.get('pregunta')
    openai.api_key = API
    initialmessage.append({"role": "user", "content": text})
    with open('currentchat.txt', 'a+') as f:
        f.write(str({"role": "user", "content": text})+ "\n")


    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages= initialmessage,
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0

        )
    model_reply = response['choices'][0]["message"]["content"]
    with open('currentchat.txt', 'a+') as f:
        f.write(str({"role": "assistant", "content": model_reply})+"\n")
    print(initialmessage)
    return jsonify({"response": True, "message": model_reply})


def checkhist(number,hist,guia):
    try:
        if len(hist) >= len(guia):
            print(len(hist),len(guia))
            return 0
        if number in hist:
            number = randrange(len(hist))
            print(number,hist)
            return checkhist(number,hist,guia)
        else:
            hist.append(number)
            print(number, hist)
            return number
    except Exception as e:
        print(e)
        hist.append(0)
        return 0


if __name__ == '__main__':
    app.run(debug=True)
