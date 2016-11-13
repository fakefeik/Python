import unittest
import poly
import country
import parse
import coloring


class TestClass(unittest.TestCase):
    def test_poly_inside(self):
        self.assertTrue(poly.is_inside([[1, 1], [4, 1], [4, 4], [1, 4]], [[2, 2], [3, 2], [3, 3], [2, 3]]))
        self.assertFalse(poly.is_inside([[1, 1], [4, 1], [4, 4], [1, 4]], [[0, 1], [2, 3], [3, 1]]))

    def test_poly_intersect(self):
        self.assertTrue(poly.are_intersecting([[1, 1], [4, 1], [4, 4], [1, 4]], [[0, 1], [2, 3], [3, 1]]))
        self.assertTrue(poly.are_intersecting([[10, 10], [200, 10], [200, 150], [10, 200]],
                                              [[200, 100], [300, 60], [250, 10], [200, 10]]))
        self.assertFalse(poly.are_intersecting([[10, 10], [10, 100], [100, 100], [100, 10]],
                                               [[200, 200], [300, 300], [250, 250]]))

    def test_country_neigh(self):
        country1 = country.Country([[1, 1], [10, 1], [10, 10], [1, 10]])
        country12 = country.Country([[1, 1], [10, 1], [10, 10], [1, 10]])
        country2 = country.Country([[5, 5], [12, 5], [12, 12], [5, 12]])
        country3 = country.Country([[100, 100], [100, 200], [200, 200], [200, 100]])
        country4 = country.Country([[200, 200], [300, 200], [300, 300], [200, 300]])
        self.assertTrue(country1 in country2)
        self.assertEqual(country1, country12)
        g = country.Graph([country1, country2, country3, country4])
        self.assertEqual(list(g.get_neighbours([country4, None]))[0][0], country3)

    def test_parse(self):
        country1 = country.Country([[1, 1], [10, 1], [10, 10], [1, 10]])
        country2 = country.Country([[5, 5], [12, 5], [12, 12], [5, 12]])
        country3 = country.Country([[100, 100], [100, 200], [200, 200], [200, 100]])
        country4 = country.Country([[200, 200], [300, 200], [300, 300], [200, 300]])
        graph = country.Graph([country1, country2, country3, country4])
        string = parse.save(graph)
        graph2 = parse.load(string.splitlines())
        self.assertEqual(graph, graph2)

    def test_coloring(self):
        countries = """10, 10; 200, 10; 200, 150; 10, 200
        200, 100; 300, 60; 250, 10; 200, 10
        200, 100; 300, 60; 200, 200"""
        graph = parse.load([line.strip() for line in countries.splitlines()])
        colorer = coloring.Colorer(graph)
        colorer.set_colors()
        errors = False
        for item in graph.items:
            for neigh in graph.get_neighbours(item):
                if item[1] == neigh[1]:
                    errors = True
        self.assertFalse(errors)

if __name__ == '__main__':
    unittest.main()