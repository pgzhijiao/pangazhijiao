import requests
import base64
from Crypto.Cipher import AES
import os

# 配置采集地址 (raw 链接)
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/main/BLACK_VLESS_RUS.txt"
]

# 加密配置 (必须与 Rust 终端一致)
CRYPTO_KEY = b"rusthx_secure_key_2026_0504_vpn_" # 32字节
CRYPTO_NONCE = b"unique_nonce"                  # 12字节

def encrypt_data(data):
    cipher = AES.new(CRYPTO_KEY, AES.MODE_GCM, nonce=CRYPTO_NONCE)
    # Rust 侧解密使用的是 aes-gcm 库，不带 tag 的解密需要注意
    # 这里我们只加密内容部分
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    # 注意：Rust 的 aes-gcm 库解密时默认需要 tag 拼接在密文后面
    # 拼接格式: ciphertext + tag
    full_encrypted = ciphertext + tag
    return base64.b64encode(full_encrypted).decode('utf-8')

def collect():
    all_nodes = []
    print(f"开始采集 {len(SOURCES)} 个数据源...")
    
    for url in SOURCES:
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                content = resp.text.strip()
                # 尝试 base64 解码获取原始节点列表
                try:
                    decoded = base64.b64decode(content).decode('utf-8')
                    all_nodes.append(decoded)
                except:
                    all_nodes.append(content)
                print(f"成功采集: {url}")
        except Exception as e:
            print(f"采集失败 {url}: {e}")

    final_content = "\n".join(all_nodes)
    if not final_content.strip():
        print("未采集到有效内容，跳过更新")
        return

    # 加密并保存
    print("正在进行 AES-256-GCM 加密...")
    encrypted_str = encrypt_data(final_content)
    
    with open("jiedian.txt", "w", encoding="utf-8") as f:
        f.write(encrypted_str)
    
    print(f"采集完成，已生成加密后的 jiedian.txt (长度: {len(encrypted_str)})")

if __name__ == "__main__":
    collect()
