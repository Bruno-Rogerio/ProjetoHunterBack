from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from config import MONGO_URI, DB_NAME
import os

# Configurações iniciais
app = Flask(__name__)
CORS(app)

# Conexão com MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
produtos_collection = db.produtos

# Função auxiliar para converter ObjectId em string e categorizar o produto
def serialize_produto(produto):
    produto['_id'] = str(produto['_id'])
    produto['categoria'] = produto.get('categoria', 'Geral')
    return produto

# Rota para criar produto
@app.route('/produtos', methods=['POST'])
def criar_produto():
    dados = request.json
    if not dados:
        return jsonify({'erro': 'Nenhum dado recebido'}), 400
        
    campos_obrigatorios = ['nome', 'preco', 'precoAntigo', 'link_afiliado', 'template', 'categoria']
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({'erro': f'Campo obrigatório ausente: {campo}'}), 400

    produto = {
        'nome': dados['nome'],
        'preco': float(dados['preco']),
        'precoAntigo': float(dados['precoAntigo']),
        'link_afiliado': dados['link_afiliado'],
        'template': dados['template'],
        'categoria': dados.get('categoria', 'Geral'),
        'ativo': True,
        'data_cadastro': datetime.utcnow()
    }
    resultado = produtos_collection.insert_one(produto)
    produto['_id'] = str(resultado.inserted_id)
    return jsonify({'mensagem': 'Produto cadastrado com sucesso', 'produto': produto}), 201

# Rota para listar produtos
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    produtos = list(produtos_collection.find({'ativo': True}))
    produtos_formatados = [
        serialize_produto(produto)
        for produto in produtos
    ]
    return jsonify(produtos_formatados)

# Rota para atualizar produto
@app.route('/produtos/<id>', methods=['PUT'])
def atualizar_produto(id):
    dados = request.json
    resultado = produtos_collection.update_one(
        {'_id': ObjectId(id)},
        {'$set': {
            'nome': dados['nome'],
            'preco': float(dados['preco']),
            'precoAntigo': float(dados['precoAntigo']),
            'link_afiliado': dados['link_afiliado'],
            'template': dados['template'],
            'categoria': dados.get('categoria', 'Geral'),
            'data_atualizacao': datetime.utcnow()
        }}
    )
    if resultado.modified_count:
        return jsonify({'mensagem': 'Produto atualizado com sucesso'})
    return jsonify({'mensagem': 'Produto não encontrado'}), 404

# Rota para deletar produto
@app.route('/produtos/<id>', methods=['DELETE'])
def deletar_produto(id):
    resultado = produtos_collection.delete_one({'_id': ObjectId(id)})
    if resultado.deleted_count > 0:
        return jsonify({'mensagem': 'Produto excluído com sucesso!'})
    return jsonify({'mensagem': 'Produto não encontrado!'}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
