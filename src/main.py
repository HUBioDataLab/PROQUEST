import h5py
import numpy as np
from annoy import AnnoyIndex
import sqlite3

filePath = 'asset/per-protein.h5'
indexFile = 'protein_embeddings.ann'
databaseFile = 'protein_index.db'

def isValidEmbedding(embedding):
    return not np.any(np.isnan(embedding) | np.isinf(embedding))

def buildAnnoyDb(embeddings, num_trees=10):
    dimension = embeddings[0].shape[0]  # assume all embeddings have the same dimension
    index = AnnoyIndex(dimension, 'euclidean')  # could be 'angular', 'manhattan', or 'hamming'

    for i, embedding in enumerate(embeddings):
        index.add_item(i, embedding)

    index.build(num_trees)
    index.save(indexFile)
    print(f"Annoy index built and saved to {indexFile}")
    return index

def storeIdMap(ids):
    conn = sqlite3.connect(databaseFile)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS id_map (index_id INTEGER PRIMARY KEY, protein_id TEXT)''')
    
    for i, protein_id in enumerate(ids):
        c.execute('INSERT INTO id_map (index_id, protein_id) VALUES (?, ?)', (i, protein_id))
    
    conn.commit()
    conn.close()
    print(f"ID map stored in SQLite database at {databaseFile}")