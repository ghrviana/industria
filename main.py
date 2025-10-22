import pandas as pd
import streamlit as st
from streamlit_ketcher import st_ketcher
from datetime import datetime
from rdkit import Chem
from rdkit.Chem import Descriptors
import requests

#Função para buscar informações no PubChem
def get_pubchem_info(smiles: str) -> dict:
    """
    Busca informações no PubChem a partir de um SMILES.
    Retorna IUPAC Name, CID, Sinônimos e CAS Number.
    
    Parâmetros:
        smiles (str): SMILES da molécula.
        
    Retorna:
        dict: {'iupac_name', 'cid', 'synonyms', 'cas_number'}
    """
    # Dicionário de retorno inicial com valores None
    result = {
        "iupac_name": None,
        "cid": None,
        "synonyms": None,
        "cas_number": None
    }

    try:
        # 1. Busca o CID a partir do SMILES
        url_cid = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{smiles}/cids/JSON"
        cid_response = requests.get(url_cid)
        if cid_response.status_code != 200:
            return result

        cid_data = cid_response.json()
        cid_list = cid_data.get("IdentifierList", {}).get("CID", [])
        if not cid_list:
            return result

        cid = cid_list[0]
        result["cid"] = cid

        # 2. Busca propriedades, incluindo o IUPAC Name
        url_props = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/IUPACName/JSON"
        props_response = requests.get(url_props)
        if props_response.status_code == 200:
            try:
                props = props_response.json()["PropertyTable"]["Properties"][0]
                result["iupac_name"] = props.get("IUPACName")
            except:
                result["iupac_name"] = None

        # 3. Busca os sinônimos
        url_synonyms = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
        syn_response = requests.get(url_synonyms)
        if syn_response.status_code == 200:
            try:
                synonyms = syn_response.json()["InformationList"]["Information"][0]["Synonym"]
                result["synonyms"] = synonyms[:10] if synonyms else None

                # 4. Procura um CAS Number entre os sinônimos
                for syn in synonyms:
                    if syn.replace("-", "").isdigit() and syn.count("-") == 2:
                        result["cas_number"] = syn
                        break
            except:
                result["synonyms"] = None
                result["cas_number"] = None

    except Exception as e:
        print(f"Erro na busca: {e}")

    return result


colunas = ["medicamento","etapa_sintetica","rota_sintetica","formula_molecular","iupac_name","cid","synonyms","cas_number","SMILES", "InChI", "InChIKey", "MolWt", "Referência"]

# Verifica se o DataFrame está no estado da sessão, caso contrário, inicializa-o
if "df_dados" not in st.session_state:    
    st.session_state.df_dados = pd.DataFrame(columns=colunas)

smiles = st_ketcher(height=400)

# Busca informações no PubChem
dic_pubchem = get_pubchem_info(smiles)
iupac_name = dic_pubchem.get("iupac_name")
cid = dic_pubchem.get("cid")
synonyms = dic_pubchem.get("synonyms")
cas_number = dic_pubchem.get("cas_number")

# cálculo massa molecular para conversão de unidade
mol = Chem.MolFromSmiles(smiles) 
massa_molecular = Descriptors.MolWt(mol)

formula_molecular = Chem.rdMolDescriptors.CalcMolFormula(mol)
inchi = Chem.MolToInchi(mol)
inchikey = Chem.InchiToInchiKey(inchi)

medicamentos = [
    "dipirona",
    "cloridrato de metformina",
    "ibuprofeno",
    "losartana potássica",
    "levotiroxina sódica",
    "rosuvastatina cálcica",
    "amoxicilina",
    "colecalciferol",
    "oxalato de escitalopram",
    "cetoprofeno",
    "cloridrato de sertralina",
    "azitromicina",
    "levonorgestrel",
    "paracetamol",
    "pantoprazol sódico",
    "sinvastatina",
    "gliclazida",
    "sulfato de salbutamol",
    "succinato de metoprolol",
    "besilato de anlodipino",
    "tadalafila",
    "hemifumarato de quetiapina",
    "pregabalina",
    "cloridrato de ondansetrona di-hidratado",
    "cefalexina",
    "nimesulida",
    "cloridrato de nafazolina",
    "hemitartarato de zolpidem",
    "cloridrato de venlafaxina",
    "clonazepam",
    "succinato de desvenlafaxina monoidratado",
    "cloridrato de fexofenadina",
    "acetilcisteína",
    "maleato de enalapril",
    "maleato de dexclorfeniramina",
    "budesonida",
    "dapagliflozina",
    "cloridrato de duloxetina",
    "atorvastatina cálcica",
    "cloridrato de fluoxetina",
    "loratadina",
    "dolutegravir sódico",
    "fosfato sódico de prednisolona",
    "furoato de mometasona",
    "citrato de sildenafila",
    "hemifumarato de bisoprolol",
    "nitazoxanida",
    "cloridrato de tramadol",
    "omeprazol",
    "valsartana",
    "apixabana",
    "bromazepam",
    "cloridrato de metilfenidato",
    "risperidona",
    "prednisolona",
    "dipropionato de beclometasona"
]

col1, col2, col3 = st.columns(3)
with col1:
    nome_medicamento = st.selectbox("Selecione o nome do medicamento:",
                                    medicamentos,
                                    index=None                                    
                                )
with col2:
    etapa_sintetica = st.number_input("Informe a etapa sintética:",                                      
                                      step=1)
with col3:
    rota_sintetica = st.selectbox(
                                    "Informe a rota sintética a, b, c, etc:",
                                    ["a","b","c","d","e","f"],
                                    index=None,                                    
                                )
ref = st.number_input("Informe a página do pdf referente a rota sintética:",
                                      value=None,
                                      step=1)

gravar_dados = st.button("Registrar Dados na Tabela")
if gravar_dados:
    # Adiciona os novos dados a um DataFrame temporário
    novos_dados = pd.DataFrame([[nome_medicamento, etapa_sintetica, rota_sintetica, formula_molecular, iupac_name, cid, synonyms, cas_number, smiles, inchi, inchikey, massa_molecular, ref]], columns=colunas)
    
    # Concatena o DataFrame temporário com o DataFrame no estado da sessão
    st.session_state.df_dados = pd.concat([st.session_state.df_dados, novos_dados], ignore_index=True)

on = st.toggle("Apagar linha")
if on:    
    index_linha = st.number_input("Informe o índice da linha para ser removida", step=1)
    apagar_linha = st.button("Apagar Linha", type="primary")
    if apagar_linha:
        try:
            st.session_state.df_dados = st.session_state.df_dados.drop(index_linha)        
            st.session_state.df_dados = st.session_state.df_dados.reset_index(drop=True)
        except:
            pass

# Exibe o DataFrame atualizado
st.write(st.session_state.df_dados)

if st.session_state.df_dados.shape[0] > 0:
    #data e hora do registro
    agora = datetime.now()
    data = agora.strftime('%d_%b_%Y')
    hora = agora.strftime('%Hh%Mm%Sseg')
    # Cria uma lista de medicamentos únicos
    medicamentos_unicos = st.session_state.df_dados['medicamento'].unique().tolist()
    # Substitui espaços por underscores em cada item e junta com underscores
    medicamentos_registrados = '_'.join(item.replace(' ', '_') for item in medicamentos_unicos)
    # Nome do arquivo com data, hora e medicamentos
    nome_arquivo = f'{medicamentos_registrados}_{data}_{hora}.parquet'
    # Converter DataFrame para bytes
    parquet_bytes = st.session_state.df_dados.to_parquet(index=False)
    # Botão de download
    gravar_parquet = st.download_button(
        label="Salvar Arquivo e Fazer Download",
        data=parquet_bytes,
        file_name=nome_arquivo,
        mime='application/octet-stream',
        type = "primary"
    )