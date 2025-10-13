from Grapher import Graph

g = Graph()
g.add_edge('A','B')
g.add_edge('B','C')
g.add_edge('A','C')

g.remove_edge('A','C')

print("node列表",g.tasks())
print("edge列表",g.edges())

print("A的后果：",g.immediate_consequences_of('A'))
print("递归后果",g.recursive_consequences_of(['A'],True))


print("第一次提交")
print(1111)