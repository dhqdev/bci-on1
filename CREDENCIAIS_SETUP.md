# 🔐 Configuração de Credenciais

## Como Configurar

O arquivo `credentials.json` contém suas credenciais de acesso ao sistema Servopa.

### Opção 1: Via Interface Web (Recomendado)

1. Inicie o sistema:
   ```bash
   ./iniciar.sh
   ```
   
2. Acesse a interface web em: http://localhost:5000

3. Clique em **Credenciais** no menu lateral

4. Preencha seus dados:
   - **Usuário**: Seu email ou CPF de acesso ao Servopa
   - **Senha**: Sua senha do Servopa

5. Clique em **Salvar Credenciais**

### Opção 2: Edição Manual

Edite o arquivo `credentials.json` com suas credenciais:

```json
{
  "servopa": {
    "usuario": "seu.email@exemplo.com",
    "senha": "sua_senha_aqui"
  }
}
```

## ⚠️ Segurança

- **NUNCA** compartilhe o arquivo `credentials.json` com suas credenciais preenchidas
- O arquivo `credentials.json` está no `.gitignore` e **NÃO será enviado ao GitHub**
- Apenas o template vazio (`credentials.json.template`) é versionado no repositório
- Suas credenciais ficam apenas no seu computador local

## 🔄 Atualização do Sistema

Ao atualizar o sistema via `git pull`, suas credenciais serão preservadas pois o arquivo está ignorado pelo Git.

## 📝 Primeiro Uso

No primeiro uso, o sistema criará automaticamente o arquivo `credentials.json` a partir do template vazio. Você precisará preenchê-lo com suas credenciais através da interface web ou editando manualmente.
