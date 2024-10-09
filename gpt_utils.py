from openai import OpenAI
import json

client = OpenAI(api_key="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")

def filter_with_gpt(json_file):
    # Cargar los datos del archivo JSON
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = []
        with open(json_file, "r") as f:
            for line in f:
                line = line.strip().rstrip(",")
                if not line or line == "[" or line == "]":
                    continue
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error al procesar la línea: {line}. Error: {e}")
                    continue

    if not data:
        raise ValueError(f"No se encontraron datos válidos en el archivo {json_file}.")

    # Prompt para GPT, con la instrucción clara de devolver solo el JSON
    prompt = """
    You will be provided with a JSON list of coffee products. Your task is to:
    1. Remove any products where the 'coffee_name' contains the word "Blend".
    2. Keep only the products whose 'product_origin' is either "El Salvador", "Guatemala", "Etiopia", "Brasil", "Colombia", "Perú", "Burundi", "Sumatra", "México" or "Rwanda".
    3. Return ONLY the cleaned JSON data, without any extra text or explanations.

    Here is the data:
    {}
    """.format(json.dumps(data))

    # Llamada a la API de OpenAI
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a data processing assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,  # Aumentar el número de tokens por si el JSON es grande
        temperature=0
    )

    # Extraer la respuesta de GPT
    raw_response = response.choices[0].message.content.strip()

    # Intentar limpiar la respuesta para convertirla en JSON
    try:
        # Verificar si el contenido ya es un JSON válido
        if raw_response.startswith("{") or raw_response.startswith("["):
            # Intentar cargar el JSON
            filtered_data = json.loads(raw_response)
        else:
            raise ValueError("La respuesta de GPT no es un JSON válido.")
    except json.JSONDecodeError as e:
        # Imprimir la respuesta cruda para analizar errores de formato
        print("Respuesta GPT:", raw_response)
        raise ValueError(f"Error al procesar la respuesta de GPT: {e}")

    # Guardar el archivo JSON limpio
    clean_file = json_file.replace("_output", "_output_clean")
    with open(clean_file, "w") as f:
        json.dump(filtered_data, f, indent=4)

    return clean_file
