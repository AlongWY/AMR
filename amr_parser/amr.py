#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AMR (Abstract Meaning Representation) structure
For detailed description of AMR, see http://www.isi.edu/natural-language/amr/a.pdf

"""

from __future__ import print_function

import json
from collections import defaultdict
import sys

# change this if needed
ERROR_LOG = sys.stderr

# change this if needed
DEBUG_LOG = sys.stderr


class AMR(object):
    """
    AMR is a rooted, labeled graph to represent semantics.
    This class has the following members:
    nodes: list of node in the graph. Its ith element is the name of the ith node. For example, a node name
           could be "a1", "b", "g2", .etc
    node_values: list of node labels (values) of the graph. Its ith element is the value associated with node i in
                 nodes list. In AMR, such value is usually a semantic concept (e.g. "boy", "want-01")
    root: root node name
    relations: list of edges connecting two nodes in the graph. Each entry is a link between two nodes, i.e. a triple
               <relation name, node1 name, node 2 name>. In AMR, such link denotes the relation between two semantic
               concepts. For example, "arg0" means that one of the concepts is the 0th argument of the other.
    attributes: list of edges connecting a node to an attribute name and its value. For example, if the polarity of
               some node is negative, there should be an edge connecting this node and "-". A triple < attribute name,
               node name, attribute value> is used to represent such attribute. It can also be viewed as a relation.

    """

    def __init__(self, node_list=None, node_value_list=None, relation_list=None, attribute_list=None):
        """
        node_list: names of nodes in AMR graph, e.g. "a11", "n"
        node_value_list: values of nodes in AMR graph, e.g. "group" for a node named "g"
        relation_list: list of relations between two nodes
        attribute_list: list of attributes (links between one node and one constant value)

        """
        # initialize AMR graph nodes using list of nodes name
        # root, by default, is the first in var_list

        if node_list is None:
            self.nodes = []
            self.root = None
        else:
            self.nodes = node_list[:]
            if len(node_list) != 0:
                self.root = node_list[0]
            else:
                self.root = None
        if node_value_list is None:
            self.node_values = []
        else:
            self.node_values = node_value_list[:]
        if relation_list is None:
            self.relations = []
        else:
            self.relations = relation_list[:]
        if attribute_list is None:
            self.attributes = []
        else:
            self.attributes = attribute_list[:]

    def rename_node(self, prefix):
        """
        Rename AMR graph nodes to prefix + node_index to avoid nodes with the same name in two different AMRs.

        """
        node_map_dict = {}
        # map each node to its new name (e.g. "a1")
        for i in range(0, len(self.nodes)):
            node_map_dict[self.nodes[i]] = prefix + str(i)
        # update node name
        for i, v in enumerate(self.nodes):
            self.nodes[i] = node_map_dict[v]
        # update node name in relations
        for node_relations in self.relations:
            for i, l in enumerate(node_relations):
                node_relations[i][1] = node_map_dict[l[1]]

    def get_triples(self):
        """
        Get the triples in three lists.
        instance_triple: a triple representing an instance. E.g. instance(w, want-01)
        attribute triple: relation of attributes, e.g. polarity(w, - )
        and relation triple, e.g. arg0 (w, b)

        """
        instance_triple = []
        relation_triple = []
        attribute_triple = []
        for i in range(len(self.nodes)):
            instance_triple.append(("instance", self.nodes[i], self.node_values[i]))
            # l[0] is relation name
            # l[1] is the other node this node has relation with
            for l in self.relations[i]:
                relation_triple.append((l[0], self.nodes[i], l[1]))
            # l[0] is the attribute name
            # l[1] is the attribute value
            for l in self.attributes[i]:
                attribute_triple.append((l[0], self.nodes[i], l[1]))
        return instance_triple, attribute_triple, relation_triple

    def get_triples2(self):
        """
        Get the triples in two lists:
        instance_triple: a triple representing an instance. E.g. instance(w, want-01)
        relation_triple: a triple representing all relations. E.g arg0 (w, b) or E.g. polarity(w, - )
        Note that we do not differentiate between attribute triple and relation triple. Both are considered as relation
        triples.
        All triples are represented by (triple_type, argument 1 of the triple, argument 2 of the triple)

        """
        instance_triple = []
        relation_triple = []
        for i in range(len(self.nodes)):
            # an instance triple is instance(node name, node value).
            # For example, instance(b, boy).
            instance_triple.append(("instance", self.nodes[i], self.node_values[i]))
            # l[0] is relation name
            # l[1] is the other node this node has relation with
            for l in self.relations[i]:
                relation_triple.append((l[0], self.nodes[i], l[1]))
            # l[0] is the attribute name
            # l[1] is the attribute value
            for l in self.attributes[i]:
                relation_triple.append((l[0], self.nodes[i], l[1]))
        return instance_triple, relation_triple

    def __str__(self):
        """
        Generate AMR string for better readability

        """
        lines = []
        for i in range(len(self.nodes)):
            lines.append("Node " + str(i) + " " + self.nodes[i])
            lines.append("Value: " + self.node_values[i])
            lines.append("Relations:")
            for relation in self.relations[i]:
                lines.append("Node " + relation[1] + " via " + relation[0])
            for attribute in self.attributes[i]:
                lines.append("Attribute: " + attribute[0] + " value " + attribute[1])
        return "\n".join(lines)

    def __repr__(self):
        return self.__str__()

    def output_amr(self):
        """
        Output AMR string

        """
        print(self.__str__(), file=DEBUG_LOG)

    @staticmethod
    def parse_amr(data: dict):
        node_name_list = []
        node_value_list = []
        relation_list = []
        attribute_list = []
        for node in data['nodes']:
            node: dict
            node_name_list.append(node['label'])
            node_value_list.append(node['label'])
            attributes = []
            for attribute, value in zip(node.get('properties', []), node.get('values', [])):
                attributes.append([attribute, value])
            attribute_list.append(attributes)
            relation_list.append([])
        for edge in data.get('edges', []):
            source = edge['source']
            target = edge['target']
            label = edge['label']
            relation_list[source].append([label, node_name_list[target]])
        for top in data['tops']:
            attribute_list[top].append(["TOP", node_value_list[top]])
        result_amr = AMR(node_name_list, node_value_list, relation_list, attribute_list)
        return result_amr


# test AMR parsing
# run by amr.py [file containing AMR]
# a unittest can also be used.
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No file given", file=ERROR_LOG)
        exit(1)
    amr_count = 1
    for line in open(sys.argv[1]):
        cur_line = line.strip()
        line = line.rstrip()
        data = json.loads(line)

        print("AMR", amr_count, file=DEBUG_LOG)
        current = AMR.parse_amr(data)
        current.output_amr()
        amr_count += 1
