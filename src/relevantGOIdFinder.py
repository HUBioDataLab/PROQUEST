import sqlite3
import pandas as pd

def findRelatedGoIds(genesOfInterest, dbPath='asset/protein_index.db'):
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(DISTINCT protein_id) FROM protein_go_mapping")
    distinctProteinCount = cursor.fetchone()[0]

    # fetching go_ids, concatenated protein_ids, and their counts for the proteins in genesOfInterest
    query = """
    SELECT go_id, GROUP_CONCAT(protein_id, ', ') AS protein_ids, COUNT(protein_id) AS count_in_interest
    FROM protein_go_mapping
    WHERE protein_id IN ({})
    GROUP BY go_id
    """.format(','.join('?' for _ in genesOfInterest))  # parameterized query to avoid SQL injection

    cursor.execute(query, genesOfInterest)
    results = cursor.fetchall()

    records = []

    for goId, protein_ids, countInInterest in results:
        cursor.execute("""
        SELECT background_distribution
        FROM background_distribution_count
        WHERE go_id = ?
        """, (goId,))
        background = cursor.fetchone()
        
        if background and background[0] != 0:
            enrichmentScore = round((countInInterest / len(genesOfInterest)) / (background[0] / distinctProteinCount), 3)

            cursor.execute("""
            SELECT go_name, namespace, def, is_a
            FROM go_info
            WHERE go_id = ?
            """, (goId,))
            goInfo = cursor.fetchone()
            if goInfo:
                goName, namespace, goDef, isA = goInfo
            else:
                goName, namespace, goDef, isA = None, None, None, None

            records.append({
                'GO ID': goId,
                'Enrichment Score': enrichmentScore,
                'GO Name': goName,
                'Namespace': namespace,
                'Definition': goDef,
                'is A': isA,
                'Associated Protein IDs': protein_ids
            })

    records.sort(key=lambda r: r['Enrichment Score'], reverse=True)
    df = pd.DataFrame(records)

    conn.close()
    return df