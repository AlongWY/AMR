import json


def main():
    with open('data/check.json', encoding='utf-8') as f:
        data = json.load(f)

    inputs = data['input']
    for node in data['nodes']:
        label = node['label']
        anchors = node['anchors']

        anchors = anchors[0]
        anchor_text = inputs[anchors['from']:anchors['to']]

        print(anchors, label, anchor_text)


if __name__ == '__main__':
    main()
