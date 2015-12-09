body = """from py2neo import Graph

graph = Graph()
cypher = graph.cypher


# MIGRATION: {}


def up():
    cypher.execute("")


def down():
    cypher.execute("")
"""
