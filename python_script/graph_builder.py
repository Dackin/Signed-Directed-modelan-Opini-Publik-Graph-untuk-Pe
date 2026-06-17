import pandas as pd
import networkx as nx
import json
import os

# Kamus Peran (Role Dictionary)
# Kamu bisa menambahkan username lain ke dalam kategori yang sesuai di sini kapan saja
ROLE_MAPPING = {
    'Pemerintah': ['@prabowo', '@kemkomdigi', '@DPR_RI', '@DivHumas_Polri', '@kemkominfo', '@ListyoSigitP', '@KemenkeuRI', '@jokowi'],
    'Media': ['@kumparan', '@tempodotco', '@geloraco', '@txtdrimedia', '@KompasTV', '@hariankompas', '@Harian_Jogja'],
    'Influencer': ['@safenetvoice', '@kurawa', '@idwiki'],
    'Komunitas': ['@tanyarlfes', '@tanyakanrl']
}

def get_role(username):
    for role, users in ROLE_MAPPING.items():
        # Pengecekan case-insensitive (huruf besar/kecil tidak masalah)
        if username.lower() in [u.lower() for u in users]:
            return role
    return 'Masyarakat' # Default (Sapu Jagat)

def build_and_export_graph(csv_path, output_json):
    if not os.path.exists(csv_path):
        print(f"File tidak ditemukan: {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    G = nx.DiGraph()
    
    # 1. Kumpulkan sentimen per user
    user_sentiments = {}
    for index, row in df.iterrows():
        author = row['Author_Username']
        if pd.isna(author): continue
        author = str(author).strip()
        if not author.startswith('@'): author = '@' + author
        
        sent = row.get('Sentimen', None)
        if pd.notna(sent):
            user_sentiments[author] = sent
            
    # 2. Iterasi untuk membuat Nodes dan Edges
    for index, row in df.iterrows():
        author = row['Author_Username']
        if pd.isna(author): continue
        
        author = str(author).strip()
        if not author.startswith('@'): author = '@' + author
        
        if not G.has_node(author):
            G.add_node(author)
        
        # Fungsi pembantu untuk membuat edge interaksi
        def add_interaction_edges(interaction_string, interaction_type):
            if pd.notna(interaction_string):
                users = [u.strip() for u in str(interaction_string).split(',')]
                for u in users:
                    if u:
                        if not u.startswith('@'): u = '@' + u
                        if not G.has_node(u):
                            G.add_node(u)
                        G.add_edge(author, u, type=interaction_type)

        add_interaction_edges(row.get('Mentions'), 'mention')
        add_interaction_edges(row.get('Reply_To'), 'reply')
        add_interaction_edges(row.get('Quote_Tweet_Of'), 'quote')

    # 3. Hitung In-Degree (seberapa populer/sering disebut)
    in_degrees = dict(G.in_degree())
    
    # 4. Terapkan atribut (Role, Sentimen, Size) ke semua Node
    for node in G.nodes():
        G.nodes[node]['role'] = get_role(node)
        
        # -1 berarti akun tersebut tidak menulis tweet, hanya di-mention orang lain
        # jadi sentimen aslinya tidak diketahui (Netral)
        G.nodes[node]['sentimen'] = int(user_sentiments.get(node, -1)) 
        
        # Tambahkan 1 agar akun yang tidak pernah di-mention (size=0) tetap punya ukuran minimal
        G.nodes[node]['size'] = in_degrees.get(node, 0) + 1 

    # 5. Export ke format JSON Standar Web (Node-Link Data)
    data = nx.node_link_data(G)
    
    with open(output_json, 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"Berhasil mengekspor {G.number_of_nodes()} Nodes & {G.number_of_edges()} Edges ke {output_json}")

if __name__ == "__main__":
    print("Mulai mengekstrak data dan membuat Graf...")
    build_and_export_graph("Data/NLI/pro_pemerintah_nli.csv", "graf_pro.json")
    build_and_export_graph("Data/NLI/kontra_pemerintah_nli.csv", "graf_kontra.json")
    build_and_export_graph("Data/NLI/skenario3_polarisasi_IKN_nli.csv", "graf_ikn.json")
    print("Selesai! JSON siap dihubungkan ke Frontend Web.")
