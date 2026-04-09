from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import decode_ieee, word_list_to_long

print("=== INICIANDO TESTE MODBUS ===")
cliente = ModbusClient(host="127.0.0.1", port=10502)
# FORÇA A CONEXÃO AGORA ANTES DE PERGUNTAR SE ESTÁ ABERTO
cliente.open()

if not cliente.is_open:
    print("❌ ERRO: Não conectou. Verifique se o servidor está rodando.")
else:
    print("✅ CONEXÃO ESTABELECIDA!")
    # Lê 2 registradores a partir do endereço 10 (Tensão Va)
    regs = cliente.read_holding_registers(10, 2)
    
    if regs:
        val_32bit = word_list_to_long(regs)[0]
        tensao = decode_ieee(val_32bit)
        print(f"✅ Tensão Va lida da memória Modbus: {tensao:.2f} V")
    else:
        print("⚠️ Conectou, mas não conseguiu ler o endereço 10.")