import json
from amr_clean.amr import AMR, AMRGraph


class AMRIO:
    def __init__(self):
        pass

    @staticmethod
    def read(file_path):
        with open(file_path, encoding='utf-8') as f:
            amr = AMR()
            graph_lines = []
            misc_lines = []
            for line in f:
                line = line.rstrip()
                if line == '':
                    if len(graph_lines) != 0:
                        amr.graph = AMRGraph.decode(' '.join(graph_lines))
                        amr.graph.set_src_tokens(amr.get_src_tokens())
                        amr.misc = misc_lines
                        yield amr
                        amr = AMR()
                    graph_lines = []
                    misc_lines = []
                elif line.startswith('# ::'):
                    if line.startswith('# ::id '):
                        amr.id = line[len('# ::id '):]
                    elif line.startswith('# ::snt '):
                        amr.sentence = line[len('# ::snt '):]
                    elif line.startswith('# ::token '):
                        amr.tokens = json.loads(line[len('# ::token '):])
                    elif line.startswith('# ::lemma '):
                        amr.lemmas = json.loads(line[len('# ::lemma '):])
                    elif line.startswith('# ::upos '):
                        amr.upos = json.loads(line[len('# ::upos '):])
                    elif line.startswith('# ::xpos '):
                        amr.xpos = json.loads(line[len('# ::xpos '):])
                    elif line.startswith('# ::ner '):
                        amr.ner = json.loads(line[len('# ::ner '):])
                    elif line.startswith('# ::abstract_map '):
                        amr.abstract_map = json.loads(line[len('# ::abstract_map '):])
                    else:
                        misc_lines.append(line)
                else:
                    graph_lines.append(line)

            if len(graph_lines) != 0:
                amr.graph = AMRGraph.decode(' '.join(graph_lines))
                amr.graph.set_src_tokens(amr.get_src_tokens())
                amr.misc = misc_lines
                yield amr

    @staticmethod
    def dump(amr_instances, f):
        for amr in amr_instances:
            f.write(str(amr) + '\n\n')
