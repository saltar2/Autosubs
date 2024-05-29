from openai import OpenAI
import configparser,srt,os,requests,json,exceptions,tiktoken

config=configparser.ConfigParser()
config.read('.env')
#config.read('backend/.env')
openai_authkey=config.get('API_KEYS','CHATGPT_API')

client = OpenAI(api_key=openai_authkey)
#modelo="gpt-3.5-turbo"
modelo="gpt-4o"
enc = tiktoken.encoding_for_model(modelo)

def comprobacion_tokens(text_sys: str,text_user: str , correction: bool) -> bool:
    enc_prompt_sys=enc.encode(text_sys)
    enc_prompt_user=enc.encode(text_user)

    len_prompt_sys=len(enc_prompt_sys)
    len_prompt_user=len(enc_prompt_user)
    max_tokens=enc.max_token_value
    if correction:
        response_tokens_estimated=len_prompt_user
    else:
        response_tokens_estimated=4000
    return len_prompt_sys+len_prompt_user+response_tokens_estimated<max_tokens#for model gpt3 max tokens are 16K but for gpt4 models suports 128K

def revisar_sub(sub,lan,sub2):
    subtitle1=srt.compose(sub)
    subtitle2=srt.compose(sub2)
    
    
    prompt=f"As an analyst tasked with assessing the two following SRT texts, the first is the deepgram transcription with the model nova-2 and the second is the whisper transcription hosted on deepgram cloud. \
            Your objective is to identify potential issues arising from Automatic Speech Recognition (ASR) errors by comparing the 2 SRT files(try to not compare line by line instead try grouping by timestaps , agregating contiguous subs from start to end but you have to indicate the affected lines). \
            Note that the output lines for the 2 SRT files may be diferent and the errors can be present on several consecutive lines. The provided transcript is the result of transcription without any manual corrections. Your task is to scrutinize the text for three specific types of errors: \
            \
                1. Semantic incoherence: Look for sentences that appear grammatically correct but lack logical sense in the context of the surrounding text or the overall topic. \
                2. Overrepetition: Pay attention to lines that contain nonsensical word combinations, excessive punctuation, or phrase repetition. Also, consider timestamps to search for errors where there is too much text in a short period. \
                3. Possible factual errors: While not the primary focus, be vigilant for lines with information that seems factually incorrect compared to common knowledge. Note any instances where the text contradicts established facts or commonly accepted information. \
            \
            Once you've identified these errors, provide alternative solutions for each error detected with details. Your corrections should aim to ensure that the final text reflects the intended content as accurately as possible. Please note that the source language is {lan} and the text may contain parts of speech in other languages. \
            \
            Finally all errors and suggestions has to be based on transcript file 1, the transcript file 2 is not omnipotent and may be as inacurate as transcript file 1. \
            Take your time to analyze both SRT files. \
            Here is the SRT text to analyze: " 

    text_srt_1=f"Transcript file 1 ->\n {subtitle1}"
    text_srt_2=f"\nTranscript file 2 ->\n {subtitle2}"

    sys_prompt=prompt
    user_prompt=text_srt_1+text_srt_2

    assert comprobacion_tokens(sys_prompt,user_prompt,False)#for model gpt3 max tokens are 16K but for gpt4 models suports 128K
    
    try:
        response = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},]
        )
    except Exception as e:
        raise exceptions.CustomError(str(e))
    
    #print(response)
    if(response.choices[0].message.content):
        text_corrections=response.choices[0].message.content.strip()
        return text_corrections
    else:
        raise exceptions.CustomError('Some error related to openai api response')
    


def correct_subs(sub,text):
    print("Corrigiendo con LLM...")

    subtitle1=srt.compose(sub)

    prompt=f"As an analist you are tasked to perform all the corrections for a given SRT file and a given list of errors with explanation and the alternative solution. \
            You are only able to modify the especify errors on the provided text. \
            When you perform the indicated changes on the SRT file to correct it, please take these considerations into account:\
                1. A subtitle must last a minimum of 1 second and a maximum of 8 seconds. \
                2. The maximum lines that can be shown together on screen are 2 \
            If you need to perform a text separation to fit the above statements, you can use these rules to execute a semantic separation of the phrase: \
                1. After punctuation marks \
                2. Before conjunctions \
                3. Before prepositions \
            To perform the solicited changes on the SRT you are able to modify the timestamps and content of the subtitles but the subtitles cannot be overlaping. \
            Finally you have to return the entire SRT file in the same format as i send you without any further information about the performed changes. \
            Ensure there are no extraneous characters like ``` at the beginning or end of the response, return only the corrected SRT content. \
            Took the time you need to perform with accurancy the task."  
                 
    text_srt_1=f"SRT file ->\n {subtitle1}"
    text_corrections=f"\n File with corrections suggested ->\n {text}"

    sys_prompt=prompt
    user_prompt=text_srt_1+text_corrections

    assert comprobacion_tokens(sys_prompt,user_prompt,True)#for model gpt3 max tokens are 16K but for gpt4 models suports 128K
    try:
        response = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},]
        )
    except Exception as e:
        raise exceptions.CustomError(str(e))
    
    if(response.choices[0].message.content):
        srt_revised=response.choices[0].message.content
        return list(srt.parse(srt_revised))
    else:
        raise exceptions.CustomError('Some error related to openai api response')


'''
file_path='TFG_compartido/How octopuses battle each other _ DIY Neuroscience, a TED series.en.srt'    
file_path2='TFG_compartido/How octopuses battle each other _ DIY Neuroscience, a TED series.es.whisper_deepgram.srt'  
print("Current working directory:", os.getcwd())

try:
    with open(file_path, "r", encoding="utf8") as f, open(file_path2, "r", encoding="utf8") as f2 :
        sub = f.read()
        sub2 = f2.read()
except FileNotFoundError:
    print("File not found at:", file_path)
except UnicodeDecodeError:
    print("Error decoding the file. Check if it's encoded in UTF-8.")
except Exception as e:
    print("An unexpected error occurred:", str(e))
lan='english'
sub=srt.parse(sub)
sub2=srt.parse(sub2)
revisar_sub(sub,lan,sub2)'''



