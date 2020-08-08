from argparse import ArgumentParser
from typing import List, Tuple
import penman as pp
from penman import Graph
from amr_parser import amr


def generate_amr_lines(f1, f2):
    """
    Read one AMR line at a time from each file handle
    :param f1: file handle (or any iterable of strings) to read AMR 1 lines from
    :param f2: file handle (or any iterable of strings) to read AMR 2 lines from
    :return: generator of cur_amr1, cur_amr2 pairs: one-line AMR strings
    """
    while True:
        cur_amr1 = amr.AMR.get_amr_line(f1, escape=True)
        cur_amr2 = amr.AMR.get_amr_line(f2)
        if not cur_amr1 and not cur_amr2:
            pass
        else:
            yield cur_amr1, cur_amr2
            continue
        break


def main(args):
    with open(args.input, encoding='utf-8') as f, \
            open(args.extra, encoding='utf-8') as e, \
            open(args.output, mode='w', encoding='utf-8') as out:
        amr_pair: List[Tuple[Graph, Graph]]
        amr_pair = []
        for sent_num, (cur_amr1, cur_amr2) in enumerate(generate_amr_lines(f, e), start=1):
            amr_pair.append(
                (
                    pp.decode(cur_amr1),
                    pp.decode(cur_amr2)
                )
            )

        amrs = []
        for idx, (amr, extra) in enumerate(amr_pair):
            amr.metadata.update(extra.metadata)
            amrs.append(amr)

        out.write(pp.dumps(amrs))


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--extra', '-e', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
