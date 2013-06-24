from graph4py import ObjectsGraph


class Example(ObjectsGraph):

    def create_article(self, title):
        with self.transaction():
            vertex = self.create_vertex()
            vertex['title'] = title
        return vertex.id()
