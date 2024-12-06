from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from config import MONGO_URI, DB_NAME

app = Flask(__name__)
CORS(app)

# Conexão com MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
produtos_collection = db.produtos

# Função auxiliar para converter ObjectId em string
def serialize_produto(produto):
    produto['_id'] = str(produto['_id'])
    return produto

# Rota para criar produto
@app.route('/produtos', methods=['POST'])
def criar_produto():
    try:
        dados = request.json
        print("Dados recebidos no servidor:", dados)
        
        if not dados:
            return jsonify({'erro': 'Nenhum dado recebido'}), 400
        
        campos_obrigatorios = ['nome', 'preco', 'link_afiliado', 'template']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({'erro': f'Campo obrigatório ausente: {campo}'}), 400
        
        produto = {
            'nome': dados['nome'],
            'preco': float(dados['preco']),
            'link_afiliado': dados['link_afiliado'],
            'template': dados['template'],
            'ativo': True,
            'data_cadastro': datetime.utcnow()
        }
        
        resultado = produtos_collection.insert_one(produto)
        produto['_id'] = str(resultado.inserted_id)
        
        print("Produto cadastrado com sucesso:", produto)
        return jsonify({
            'mensagem': 'Produto cadastrado com sucesso',
            'produto': produto
        }), 201
    except Exception as e:
        print(f"Erro ao cadastrar produto: {e}")
        return jsonify({'erro': str(e)}), 400

# Rota para listar produtos
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    try:
        produtos = list(produtos_collection.find({'ativo': True}))
        return jsonify([serialize_produto(p) for p in produtos])
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# Rota para buscar produto específico
@app.route('/produtos/<id>', methods=['GET'])
def buscar_produto(id):
    try:
        produto = produtos_collection.find_one({'_id': ObjectId(id)})
        if produto:
            return jsonify(serialize_produto(produto))
        return jsonify({'mensagem': 'Produto não encontrado'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# Rota para atualizar produto
@app.route('/produtos/<id>', methods=['PUT'])
def atualizar_produto(id):
    try:
        dados = request.json
        resultado = produtos_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'nome': dados['nome'],
                'preco': float(dados['preco']),
                'link_afiliado': dados['link_afiliado'],
                'template': dados['template'],
                'data_atualizacao': datetime.utcnow()
            }}
        )
        
        if resultado.modified_count:
            return jsonify({'mensagem': 'Produto atualizado com sucesso'})
        return jsonify({'mensagem': 'Produto não encontrado'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

# Rota para deletar produto (soft delete)
@app.route('/produtos/<id>', methods=['DELETE'])
def deletar_produto(id):
    try:
        resultado = produtos_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': {'ativo': False}}
        )
        
        if resultado.modified_count:
            return jsonify({'mensagem': 'Produto removido com sucesso'})
        return jsonify({'mensagem': 'Produto não encontrado'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 400

if __name__ == '__main__':
    try:
        # Teste de conexão
        client.admin.command('ping')
        print("Conexão com MongoDB bem-sucedida!")
    except Exception as e:
        print(f"Erro na conexão com MongoDB: {e}")
    
    # Inicia o servidor Flask
    app.run(debug=True)
