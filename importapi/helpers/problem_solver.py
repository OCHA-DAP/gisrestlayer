from importapi.helpers.problem import MultiLineProblem, MultiPolygonProblem, NoSRSProblem, Latin1EncodingProblem
class ProblemSolver(object):

    problems = [
    ]

    def __init__(self, filepath, solution=None):
        '''
        :param filepath: the path to the geo-file that is being processed
        :type filepath: unicode
        :param solution: A pre-existent solution if there exists one
        :type solution: Solution
        '''
        self.solution = solution if solution else Solution()
        self.problems = [
            MultiLineProblem(filepath),
            MultiPolygonProblem(filepath),
            NoSRSProblem(filepath),
            Latin1EncodingProblem(filepath)
        ]

    def find_solution(self, program_output):
        '''
        :param program_output: output error of ogr2ogr
        :type program_output: unicode
        :return: a solution with all found params
        :rtype: Solution
        '''

        for problem in self.problems:
            found = problem.find_solution(program_output, self.solution)
            if found:
                break
        return self.solution


class Solution(object):
    '''
    This will hold all additional parameters ( all solutions )
    that should be added to either the environment or to ogr2ogr to deal with
    certain errors
    '''
    def __init__(self):
        self._env_dict = {}
        self._ogr_dict = {}

        self.version = 0

    def add_env_key(self, key, value):
        self._env_dict[key] = value
        self.version += 1

    def add_ogr_key(self, key, value):
        self._ogr_dict[key] = value
        self.version += 1

    def has_env_key(self, key):
        return key in self._env_dict

    def has_ogr_key(self, key):
        return key in self._ogr_dict

    def has_env_keys(self,):
        return len(self._env_dict) > 0

    def has_ogr_keys(self):
        return len(self._ogr_dict) > 0

    def get_env_items(self):
        '''
        :return: iterator over the (key,value) env params
        :rtype: iterator
        '''
        return self._env_dict.items()

    def get_ogr_items(self):
        '''
        :return: iterator over the (key,value) ogr params
        :rtype: iterator
        '''
        return self._ogr_dict.items()


