from flask import Flask, request ,jsonify
import pyfreeling

def Analizador():
# inicilizamos freeling
    DATA = "/usr/local"+"/share/freeling/"
#    DATA = "/usr"+"/share/freeling/"
# Init locales
    pyfreeling.util_init_locale("default")

# create options set for maco analyzer. Default values are Ok, except for data files.
    LANG="es"
    op= pyfreeling.maco_options(LANG)
    op.set_data_files( "", 
                   DATA + "common/punct.dat",
                   DATA + LANG + "/dicc.src",
                   DATA + LANG + "/afixos.dat",
                   "",
                   DATA + LANG + "/locucions.dat", 
                   DATA + LANG + "/np.dat",
                   DATA + LANG + "/quantities.dat",
                   DATA + LANG + "/probabilitats.dat")

# create analyzers
    tk=pyfreeling.tokenizer(DATA+LANG+"/tokenizer.dat")
    sp=pyfreeling.splitter(DATA+LANG+"/splitter.dat")#separador
    mf=pyfreeling.maco(op)#morfo analisis
# create tagger
    tagger = pyfreeling.hmm_tagger(DATA + LANG +"/tagger.dat",True,2)

# activate morpho modules to be used in next call

    mf.set_active_options (False,  # UserMap 
                          True,  # NumbersDetection,  
                          True,  # PunctuationDetection,   
                          True,  # DatesDetection,    
                          True,  # DictionarySearch,  
                          True,  # AffixAnalysis,  
                          False, # CompoundAnalysis, 
                          True,  # RetokContractions,
                          True,  # MultiwordsDetection,  
                          True,  # NERecognition,     
                          False, # QuantitiesDetection,  
                          True); # ProbabilityAssignment     

 
    return tk,sp,mf,tagger

# inicializamos el Analizador Morfológico
tk,sp,mf,tagger = Analizador()

# create the Flask app
backend_freeling = Flask(__name__)

@backend_freeling.route("/spl",methods=['POST'])
def split_text():
    try:
        data = request.json['sentences']
        sid=sp.open_session()
        l=tk.tokenize(data)
        sentences = sp.split(sid,l,False)
        sp.close_session(sid)
        print(str(sentences))
        return jsonify(sentences)
    except Exception as e:
        return jsonify(error=str(e)), 500

@backend_freeling.route("/morfo",methods=['POST'])
def morfo_analisis():
    try:
        data = request.json['sentences']

        with backend_freeling.test_request_context("/spl",method='POST',json={'sentences': data}):
            split_response=backend_freeling.dispatch_request()
        print(str(split_response))
        result = mf.analyze(split_response)
        return jsonify(result)
    except Exception as e:
        return jsonify(error=str(e)), 500

# run the app
if __name__ == '__main__':
    backend_freeling.run(host='0.0.0.0',port=5002,threaded=True)