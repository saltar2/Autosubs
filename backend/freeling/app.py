from flask import Flask, request ,jsonify
import pyfreeling

def Analizador():
# inicilizamos freeling
    DATA = "/usr/local"+"/share/freeling/"
    LANG = "es"
#    DATA = "/usr"+"/share/freeling/"
# Init locales
    pyfreeling.util_init_locale("default")

    op = pyfreeling.analyzer_config()

    # define creation options for morphological analyzer modules
    op.config_opt.Lang = LANG
    op.config_opt.MACO_PunctuationFile = DATA + "common/punct.dat"
    op.config_opt.MACO_DictionaryFile = DATA + LANG + "/dicc.src"
    op.config_opt.MACO_AffixFile = DATA + LANG + "/afixos.dat" 
    op.config_opt.MACO_CompoundFile = DATA + LANG + "/compounds.dat" 
    op.config_opt.MACO_LocutionsFile = DATA + LANG + "/locucions.dat"
    op.config_opt.MACO_NPDataFile = DATA + LANG + "/np.dat"
    op.config_opt.MACO_QuantitiesFile = DATA + LANG + "/quantities.dat"
    op.config_opt.MACO_ProbabilityFile = DATA + LANG + "/probabilitats.dat"

    # chose which modules among those available will be used by default
    # (can be changed at each call if needed)
    op.invoke_opt.MACO_AffixAnalysis = True
    op.invoke_opt.MACO_CompoundAnalysis = True
    op.invoke_opt.MACO_MultiwordsDetection = True
    op.invoke_opt.MACO_NumbersDetection = True
    op.invoke_opt.MACO_PunctuationDetection = True 
    op.invoke_opt.MACO_DatesDetection = True
    op.invoke_opt.MACO_QuantitiesDetection = True
    op.invoke_opt.MACO_DictionarySearch = True
    op.invoke_opt.MACO_ProbabilityAssignment = True
    op.invoke_opt.MACO_NERecognition = True
    op.invoke_opt.MACO_RetokContractions = True

    # create analyzers
    tk=pyfreeling.tokenizer(DATA+LANG+"/tokenizer.dat")
    sp=pyfreeling.splitter(DATA+LANG+"/splitter.dat")

    mf=pyfreeling.maco(op)

    # create tagger, sense anotator, and parsers
    op.config_opt.TAGGER_HMMFile = DATA+LANG+"/tagger.dat"
    op.invoke_opt.TAGGER_Retokenize = True
    op.invoke_opt.TAGGER_ForceSelect = pyfreeling.RETOK
    tg=pyfreeling.hmm_tagger(op)

    sen=pyfreeling.senses(DATA+LANG+"/senses.dat")
    parser= pyfreeling.chart_parser(DATA+LANG+"/chunker/grammar-chunk.dat")
    dep=pyfreeling.dep_txala(DATA+LANG+"/dep_txala/dependences.dat", parser.get_start_symbol());   

 
    return tk,sp,mf,tg,tg,sen,dep

# inicializamos el Analizador Morfológico
tk,sp,mf,tg,tg,sen,dep = Analizador()

# create the Flask app
backend_freeling = Flask(__name__)


def split_text(data):
        sid=sp.open_session()
        l=tk.tokenize(data)
        sentences = sp.split(sid,l,False)
        sp.close_session(sid)
        print(str(sentences))
        return sentences


@backend_freeling.route("/morfo",methods=['POST'])
def morfo_analisis():
    try:
        data = request.json['sentences']

        split_response=split_text(data)
        result = mf.analyze_sentence_list(split_response)
        print(str(result))
        return jsonify(result)
    except Exception as e:
        return jsonify(error=str(e)), 500

# run the app
if __name__ == '__main__':
    backend_freeling.run(host='0.0.0.0',port=5002,threaded=True)