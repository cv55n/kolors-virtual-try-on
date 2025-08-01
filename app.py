import os
import cv2
import gradio as gr
import numpy as np
import random
import base64
import requests
import json
import time

def tryon(person_img, garment_img, seed, randomize_seed):
    post_start_time = time.time()

    if person_img is None or garment_img is None:
        gr.Warning("imagem vazia")

        return None, None, "imagem vazia"
    
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)

    encoded_person_img = cv2.imencode('.jpg', cv2.cvtColor(person_img, cv2.COLOR_RGB2BGR))[1].tobytes()
    encoded_person_img = base64.b64encode(encoded_person_img).decode('utf-8')
    
    encoded_garment_img = cv2.imencode('.jpg', cv2.cvtColor(garment_img, cv2.COLOR_RGB2BGR))[1].tobytes()
    encoded_garment_img = base64.b64encode(encoded_garment_img).decode('utf-8')

    url = "http://" + os.environ['tryon_url'] + "enviar"

    token = os.environ['token']
    cookie = os.environ['Cookie']
    referer = os.environ['referer']

    headers = {
        'Content-Type': 'application/json',
        'token': token,
        'Cookie': cookie,
        'referer': referer
        }
    
    data = {
        "clothImage": encoded_garment_img,
        "humanImage": encoded_person_img,
        
        "seed": seed
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=50)

        # print("post response code", response.status_code)

        if response.status_code == 200:
            result = response.json()['result']
            status = result['status']

            if status == "success":
                uuid = result['result']

                # print(uuid)
    except Exception as err:
        print(f"erro de exceção de postagem: {err}")

        raise gr.Error("muitos usuários, por favor tente novamente mais tarde")
    
    post_end_time = time.time()

    print(f"tempo de postagem utilizado: {post_end_time-post_start_time}")

    get_start_time = time.time()

    time.sleep(9)

    Max_Retry = 12
    result_img = None
    info = ""
    err_log = ""

    for i in range(Max_Retry):
        try:
            url = "http://" + os.environ['tryon_url'] + "Query?taskId=" + uuid
            
            response = requests.get(url, headers=headers, timeout=20)

            # print("get response code", response.status_code)

            if response.status_code == 200:
                result = response.json()['result']
                status = result['status']

                if status == "success":
                    result = base64.b64decode(result['result'])
                    result_np = np.frombuffer(result, np.uint8)
                    result_img = cv2.imdecode(result_np, cv2.IMREAD_UNCHANGED)
                    result_img = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR)
                    
                    info = "sucesso"

                    break
                elif status == "error":
                    err_log = f"status é um erro"

                    info = "erro"

                    break
            else:
                # print(response.text)
                err_log = "erro de url, entre em contato com o administrador"
                info = "erro de url, entre em contato com o administrador"
                
                break
        except requests.exceptions.ReadTimeout:
            err_log = "timeout de http"

            info = "timeout de http, tente novamente mais tarde"
        except Exception as err:
            err_log = f"erro de exceção: {err}"

        time.sleep(1)

    get_end_time = time.time()

    print(f"tempo get utilizado: {get_end_time-get_start_time}")
    print(f"todo o tempo utilizado: {get_end_time-get_start_time+post_end_time-post_start_time}")
    
    if info == "":
        err_log = f"nenhuma imagem após {Max_Retry} tentativas"
        info = "muitos usuários, tente novamente mais tarde"

    if info != "Success":
        print(f"log de erro: {err_log}")

        gr.Warning("muitos usuários, tente novamente mais tarde")

    return result_img, seed, info

def start_tryon(person_img, garment_img, seed, randomize_seed):
    start_time = time.time()

    if person_img is None or garment_img is None:
        return None, None, "imagem vazia"
    
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)
    
    encoded_person_img = cv2.imencode('.jpg', cv2.cvtColor(person_img, cv2.COLOR_RGB2BGR))[1].tobytes()
    encoded_person_img = base64.b64encode(encoded_person_img).decode('utf-8')
    encoded_garment_img = cv2.imencode('.jpg', cv2.cvtColor(garment_img, cv2.COLOR_RGB2BGR))[1].tobytes()
    encoded_garment_img = base64.b64encode(encoded_garment_img).decode('utf-8')

    url = "http://" + os.environ['tryon_url']

    token = os.environ['token']
    cookie = os.environ['Cookie']
    referer = os.environ['referer']

    headers = {
        'Content-Type': 'application/json',
        'token': token,
        'Cookie': cookie,
        'referer': referer
    }
    
    data = {
        "clothImage": encoded_garment_img,
        "humanImage": encoded_person_img,
        "seed": seed
    }

    result_img = None

    try:
        session = requests.Session()

        response = session.post(url, headers=headers, data=json.dumps(data), timeout=60)
        
        print("código de resposta", response.status_code)
        
        if response.status_code == 200:
            result = response.json()['result']
            status = result['status']

            if status == "success":
                result = base64.b64decode(result['result'])
                result_np = np.frombuffer(result, np.uint8)
                result_img = cv2.imdecode(result_np, cv2.IMREAD_UNCHANGED)
                result_img = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR)
                
                info = "sucesso"
            else:
                info = "tente novamente mais tarde"
        else:
            print(response.text)

            info = "erro de url, entre em contato com o administrador"
    except requests.exceptions.ReadTimeout:
        print("timeout")

        info = "muitos usuários, tente novamente mais tarde"
        
        raise gr.Error("muitos usuários, tente novamente mais tarde")
    except Exception as err:
        print(f"outros erros: {err}")

        info = "erro, contate o administrador"

    end_time = time.time()

    print(f"tempo utilizado: {end_time-start_time}")

    return result_img, seed, info

MAX_SEED = 999999

example_path = os.path.join(os.path.dirname(__file__), 'assets')

garm_list = os.listdir(os.path.join(example_path,"cloth"))
garm_list_path = [os.path.join(example_path,"cloth",garm) for garm in garm_list]

human_list = os.listdir(os.path.join(example_path,"human"))
human_list_path = [os.path.join(example_path,"human",human) for human in human_list]

css="""
#col-left {
    margin: 0 auto;
    max-width: 430px;
}

#col-mid {
    margin: 0 auto;
    max-width: 430px;
}

#col-right {
    margin: 0 auto;
    max-width: 430px;
}

#col-showcase {
    margin: 0 auto;
    max-width: 1100px;
}

#button {
    color: blue;
}
"""

def load_description(fp):
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    return content

def change_imgs(image1, image2):
    return image1, image2

with gr.Blocks(css=css) as Tryon:
    gr.HTML(load_description("assets/title.md"))

    with gr.Row():
        with gr.Column(elem_id = "col-left"):
            gr.HTML("""
            <div style="display: flex; justify-content: center; align-items: center; text-align: center; font-size: 20px;">
                <div>
                passo 1. carregue uma imagem de pessoa ⬇️
                </div>
            </div>
            """)

        with gr.Column(elem_id = "col-mid"):
            gr.HTML("""
            <div style="display: flex; justify-content: center; align-items: center; text-align: center; font-size: 20px;">
                <div>
                passo 2. carregue uma imagem de roupa ⬇️
                </div>
            </div>
            """)

        with gr.Column(elem_id = "col-right"):
            gr.HTML("""
            <div style="display: flex; justify-content: center; align-items: center; text-align: center; font-size: 20px;">
                <div>
                passo 3. pressione “rodar” para obter os resultados do teste
                </div>
            </div>
            """)

    with gr.Row():
        with gr.Column(elem_id = "col-left"):
            imgs = gr.Image(label="imagem da pessoa", sources='upload', type="numpy")

            # category = gr.Dropdown(label="Garment category", choices=['upper_body', 'lower_body', 'dresses'],  value="upper_body")

            example = gr.Examples(
                inputs=imgs,
                examples_per_page=12,
                examples=human_list_path
            )

        with gr.Column(elem_id = "col-mid"):
            garm_img = gr.Image(label="imagem da roupa", sources='upload', type="numpy")

            example = gr.Examples(
                inputs=garm_img,
                examples_per_page=12,
                examples=garm_list_path
            )

        with gr.Column(elem_id = "col-right"):
            image_out = gr.Image(label="resultado", show_share_button=False)

            with gr.Row():
                seed = gr.Slider(
                    label="Seed",
                    minimum=0,
                    maximum=MAX_SEED,
                    step=1,
                    value=0
                )

                randomize_seed = gr.Checkbox(label="seed aleatória", value=True)
            with gr.Row():
                seed_used = gr.Number(label="seed utilizada")
                result_info = gr.Text(label="resposta")

            # try_button = gr.Button(value="rodar", elem_id="button")
            test_button = gr.Button(value="rodar", elem_id="button")


    # try_button.click(fn=start_tryon, inputs=[imgs, garm_img, seed, randomize_seed], outputs=[image_out, seed_used, result_info], api_name='tryon',concurrency_limit=10)
    test_button.click(fn=tryon, inputs=[imgs, garm_img, seed, randomize_seed], outputs=[image_out, seed_used, result_info], api_name=False, concurrency_limit=45)

    with gr.Column(elem_id = "col-showcase"):
        gr.HTML("""
        <div style="display: flex; justify-content: center; align-items: center; text-align: center; font-size: 20px;">
            <div> </div>
            <br>
            <div>
            exemplos de try-on virtuais em pares de imagens de pessoas e roupas
            </div>
        </div>
        """)

        show_case = gr.Examples(
            examples=[
                ["assets/examples/model2.png", "assets/examples/garment2.png", "assets/examples/result2.png"],
                ["assets/examples/model3.png", "assets/examples/garment3.png", "assets/examples/result3.png"],
                ["assets/examples/model1.png", "assets/examples/garment1.png", "assets/examples/result1.png"]
            ],

            inputs=[imgs, garm_img, image_out],
            label=None
        )

Tryon.queue(api_open=False).launch(show_api=False)