import requests
from bs4 import BeautifulSoup
import json
import re

backend_url_cervantes = "https://data.cervantesvirtual.com/analizador"
'''
def parse_html(text):
    result = {'words': []}  # Diccionario para almacenar la información de las palabras
    
    # Realizar la solicitud al backend de Cervantes con el texto proporcionado
    response = requests.post(backend_url_cervantes, data={'texto': text})
    
    # Comprobar si la solicitud fue exitosa
    if response.status_code == 200:
        result['status'] = 'success'
        # Analizar el HTML de la respuesta
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar la estructura <h2>Resultado análisis morfológico</h2>
        h2_tag = soup.find('h2', text='Resultado análisis morfológico')
        if h2_tag:
            # Buscar el siguiente elemento <table> después del h2_tag
            table_tag = h2_tag.find_next_sibling('table', class_='analisis')
            if table_tag:
                # Procesar las filas de la tabla
                rows = table_tag.find_all('tr')
                for row in rows[1:]:  # Saltar la primera fila (encabezados de columna)
                    cells = row.find_all('td')
                    if cells:
                        # Obtener el texto dentro de las celdas
                        palabra = cells[0].strong.get_text(strip=True)
                        categoria = cells[1].span.span.get_text(strip=True)
                        descripcion = cells[2].span.get_text(strip=True).split('Ejemplo')[0]
                        
                        
                        word_info = {
                            'palabra': palabra,
                            'categoria_gramatical': categoria,
                            'descripcion': descripcion
                        }
                        
                        
                        result['words'].append(word_info)
        else:
            result['status'] = 'error'
            result['message'] = 'No se encontró la estructura <h2>Resultado análisis morfológico</h2>'
    else:
        result['status'] = 'error'
        result['message'] = 'Error al realizar la solicitud al backend de Cervantes'
    
    return json.dumps(result, ensure_ascii=False,indent=4)'''

def find_positions(json_data):
    positions = []
    # Cargar el JSON
    data = json_data
    # Verificar si el JSON contiene la clave 'words'
    if 'words' in data:
        aux = 0
        left_puntuation_marks = ['¿', '¡','-']
        right_puntuation_marks = ['.', ',', ';', ':', '?', '!']       
        for word_info in data['words']:
            # Verificar si la palabra tiene una categoría gramatical de 'es', 'sp000', o es un signo de puntuación
            if word_info['categoria_gramatical'] in ['cs', 'sp000'] or word_info['palabra'] in left_puntuation_marks:
                # Obtener la palabra y encontrar su posición en la oración
                start = aux
                # Si se encuentra la palabra en la oración, agregar su posición a la lista
                if start != -1:
                    positions.append(start)
            
            elif word_info['palabra'] in right_puntuation_marks:
                # Verificar si es el primer signo de puntuación de una secuencia
                if aux > 0 and data['words'][aux - 1]['palabra'] in right_puntuation_marks:
                    # Si es parte de una secuencia, omitirlo
                    pass
                else:
                    start = aux + 1
                    if start != -1:
                        positions.append(start)
            aux += 1
            
    return positions

def debug_print(text):
    words = re.findall(r"[\w']+|[.,!?;¿¡:-]", text)
        
    # Insertar números entre palabras y signos de puntuación
    text_with_numbers = ''.join(f"{i} {word} " if word != '' else f"{i} " for i, word in enumerate(words))
    text_with_numbers += f"{len(words)} "
    return text_with_numbers


'''def process_text(text):
    return find_positions(parse_html(text))'''

def process_text_v2(text_list):
    string_text=''.join(text_list)
        #string_text+= [t for t in text_list]
    result=parse_html_v2(string_text)
    list_positions=[]
    for res in result:
        list_positions.append(find_positions(res))
    return list_positions

def parse_html_v2(text):
    result = []  # Lista para almacenar la información de los subtítulos
    
    # Realizar la solicitud al backend de Cervantes con el texto proporcionado
    response = requests.post(backend_url_cervantes, data={'texto': text})
    
    # Comprobar si la solicitud fue exitosa
    if response.status_code == 200:
        # Analizar el HTML de la respuesta
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar la estructura <h2>Resultado análisis morfológico</h2>
        h2_tag = soup.find('h2', text='Resultado análisis morfológico')
        if h2_tag:
            # Buscar el siguiente elemento <table> después del h2_tag
            table_tag = h2_tag.find_next_sibling('table', class_='analisis')
            if table_tag:
                # Procesar las filas de la tabla
                rows = table_tag.find_all('tr')
                subtitle_info = None
                for row in rows[1:]:  # Saltar la primera fila (encabezados de columna)
                    cells = row.find_all('td')
                    if cells:
                        # Obtener el texto dentro de las celdas
                        palabra = cells[0].strong.get_text(strip=True)
                        categoria = cells[1].span.span.get_text(strip=True)
                        descripcion = cells[2].span.get_text(strip=True).split('Ejemplo')[0]
                        
                        
                        word_info = {
                            'palabra': palabra,
                            'categoria_gramatical': categoria,
                            'descripcion': descripcion
                        }
                        
                        
                        if palabra == '@':
                            # Si se encuentra el carácter "@" indica el final de un subtítulo
                            if subtitle_info:
                                result.append(subtitle_info)
                            subtitle_info = None
                        else:
                            # Si no es el carácter "@" se trata de información de palabra
                            if not subtitle_info:
                                subtitle_info = {'words': []}
                            subtitle_info['words'].append(word_info)
                
                # Añadir el último subtítulo a la lista
                if subtitle_info:
                    result.append(subtitle_info)
        else:
            # Si no se encuentra la estructura <h2>Resultado análisis morfológico</h2>
            result.append({
                'status': 'error',
                'message': 'No se encontró la estructura <h2>Resultado análisis morfológico</h2>'
            })
    else:
        # Si hay un error al realizar la solicitud al backend de Cervantes
        result.append({
            'status': 'error',
            'message': 'Error al realizar la solicitud al backend de Cervantes'
        })
    
    return result 

# Llamar a la función con el texto proporcionado
'''text="Cuando estoy flotando como una medusa en una ciudad vacía, no me importa quién me vea."
json_result = parse_html(text)
#print(json_result)
list_positions=find_positions(json_result)
print(list_positions)
print(debug_print(text))'''

'''string_aux="Me gusta pasear por Shibuya de noche. @ Las medusas son criaturas que no saben nadar solas. @ Me gusta flotar como una medusa en la ciudad, donde nadie me conoce, @ porque puedo ser yo mismo sin preocuparme de lo que piensen los demás."
process_text_v2(string_aux)'''