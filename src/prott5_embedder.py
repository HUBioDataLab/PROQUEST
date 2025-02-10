import argparse
import time
from pathlib import Path
import torch
import numpy as np
import h5py
from transformers import T5EncoderModel, T5Tokenizer

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print("Using device: {}".format(device))

def get_T5_model(model_dir, transformer_link="Rostlab/prot_t5_xl_half_uniref50-enc"):
    print("Loading: {}".format(transformer_link))
    if model_dir is not None:
        print("##########################")
        print("Loading cached model from: {}".format(model_dir))
        print("##########################")
    model = T5EncoderModel.from_pretrained(transformer_link, cache_dir=model_dir)
    # only cast to full-precision if no GPU is available
    if device == torch.device("cpu"):
        print("Casting model to full precision for running on CPU ...")
        model.to(torch.float32)

    model = model.to(device)
    model = model.eval()
    vocab = T5Tokenizer.from_pretrained(transformer_link, do_lower_case=False)
    return model, vocab

def read_fasta(fasta_path):
    '''
        Reads in fasta file containing multiple sequences.
        Returns dictionary of holding multiple sequences or only single 
        sequence, depending on input file.
    '''
    sequences = dict()
    with open(fasta_path, 'r') as fasta_f:
        x=0
        for line in fasta_f:
            if line.startswith('>'):
                uniprot_id = line.split("|")[1]
                sequences[uniprot_id] = ''
                if (x < 3):
                    x +=1
            else:
                sequences[uniprot_id] += ' '.join(''.join(line.split()).upper().replace("-", ""))  # drop gaps, cast to upper-case, and add spaces between characters
                if (x >= 3):
                    break
    print (sequences)
    return sequences

def get_embeddings(seq_path, emb_path, model_dir, per_protein, max_residues=4000, max_seq_len=1000, max_batch=100):
    seq_dict = read_fasta(seq_path)
    model, vocab = get_T5_model(model_dir)

    avg_length = sum([len(seq) for _, seq in seq_dict.items()]) / len(seq_dict)
    n_long = sum([1 for _, seq in seq_dict.items() if len(seq) > max_seq_len])
    seq_dict = sorted(seq_dict.items(), key=lambda kv: len(seq_dict[kv[0]]), reverse=True)

    print("Average sequence length: {}".format(avg_length))
    print("Number of sequences >{}: {}".format(max_seq_len, n_long))

    start = time.time()
    batch = list()
    emb_dict = dict()

    for seq_idx, (pdb_id, seq) in enumerate(seq_dict, 1):
        #seq = seq.replace('U', 'X').replace('Z', 'X').replace('O', 'X')
        seq_len = len(seq)
        seq = ' '.join(list(seq))
        batch.append((pdb_id, seq, seq_len))

        # count residues in current batch and add the last sequence length to
        # avoid that batches with (n_res_batch > max_residues) get processed 
        n_res_batch = sum([s_len for _, _, s_len in batch]) + seq_len 
        if len(batch) >= max_batch or n_res_batch >= max_residues or seq_idx == len(seq_dict) or seq_len > max_seq_len:
            pdb_ids, seqs, seq_lens = zip(*batch)
            batch = list()

            token_encoding = vocab.batch_encode_plus(seqs, add_special_tokens=True, padding="longest")
            input_ids = torch.tensor(token_encoding['input_ids']).to(device)
            attention_mask = torch.tensor(token_encoding['attention_mask']).to(device)

            try:
                with torch.no_grad():
                    embedding_repr = model(input_ids, attention_mask=attention_mask)
            except RuntimeError as e:
                print(f"RuntimeError during embedding for {pdb_id} (L={seq_len}). Error: {e}")
                continue

            for batch_idx, identifier in enumerate(pdb_ids):
                s_len = seq_lens[batch_idx]
                emb = embedding_repr.last_hidden_state[batch_idx, :s_len]

                if per_protein:
                    emb = emb.mean(dim=0)

                if len(emb_dict) == 0:
                    print("Embedded protein {} with length {} to emb. of shape: {}".format(
                        identifier, s_len, emb.shape))

                emb_dict[identifier] = emb.detach().cpu().numpy().squeeze()
                print(emb_dict)

    end = time.time()

    for sequence_id, embedding in emb_dict.items():
        print("buraaaaa")
        print(sequence_id)
        print(embedding)
        #hf.create_dataset(sequence_id, data=embedding)
        np.savetxt("emb.txt", embedding,) 
        break

    print('\n############# STATS #############')
    print('Total number of embeddings: {}'.format(len(emb_dict)))
    print('Total time: {:.2f}[s]; time/prot: {:.4f}[s]; avg. len= {:.2f}'.format(
        end - start, (end - start) / len(emb_dict), avg_length))
    return True

def create_arg_parser():
    """"Creates and returns the ArgumentParser object."""
    parser = argparse.ArgumentParser(description=(
        't5_embedder.py creates T5 embeddings for a given text ' +
        ' file containing sequence(s) in FASTA-format.'))
    parser.add_argument('-i', '--input', required=True, type=str,
                        help='A path to a fasta-formatted text file containing protein sequence(s).')
    parser.add_argument('-o', '--output', required=True, type=str,
                        help='A path for saving the created embeddings as NumPy npz file.')
    parser.add_argument('--model', required=False, type=str,
                        default=None,
                        help='A path to a directory holding the checkpoint for a pre-trained model')
    return parser

def main():
    parser = create_arg_parser()
    args = parser.parse_args()

    seq_path = Path(args.input)
    emb_path = Path(args.output)
    model_dir = Path(args.model) if args.model is not None else None

    get_embeddings(seq_path, emb_path, model_dir, per_protein=True)

if __name__ == '__main__':
    main()