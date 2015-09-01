import logging

logger = logging.getLogger(__name__)


class Problem(object):

    def __init__(self, search_keys, solution_key, solution_value):
        '''

        :param search_key: text pieces specific to the problem to be found in the ogr output
        :type search_key: list
        :param solution_key: parameter key to be added to the program
        :type solution_key: str
        :param solution_value: parameter value to be added to the program
        :type solution_value: str

        '''
        self.search_keys = search_keys
        self.solution_key = solution_key
        self.solution_value = solution_value

    def find_solution(self, program_output, existing_solution):
        '''

        :param program_output:
        :type program_output: unicode
        :param existing_solution:
        :type existing_solution: Solution
        :return True if a solution was found. False otherwise
        :rtype bool
        '''
        if not self._check_already_exists(existing_solution):
            keys_in_output = [key in program_output for key in self.search_keys]
            found = reduce(lambda x,y: x and y, keys_in_output)
            if found:
                self._add_solution(existing_solution)
            return found

        return False

    def _check_already_exists(self, existing_solution):
        return True

    def _add_solution(self, existing_solution):
        pass


class OgrParamProblem(Problem):
    def _check_already_exists(self, existing_solution):
        '''

        :param existing_solution:
        :type existing_solution: Solution
        :return:
        :rtype: bool
        '''
        return existing_solution.has_ogr_key(self.solution_key)

    def _add_solution(self, existing_solution):
        '''

        :param existing_solution:
        :type existing_solution: Solution
        '''
        existing_solution.add_ogr_key(self.solution_key, self.solution_value)


class EnvParamProblem(Problem):
    def _check_already_exists(self, existing_solution):
        '''
        :param existing_solution:
        :type existing_solution: Solution
        :return:
        :rtype: bool
        '''
        return existing_solution.has_env_key(self.solution_key)

    def _add_solution(self, existing_solution):
        '''
        :param existing_solution:
        :type existing_solution: Solution
        '''
        existing_solution.add_env_key(self.solution_key, self.solution_value)


class MultiPolygonProblem(OgrParamProblem):
    def __init__(self, filepath):
        self.filepath = filepath
        search_keys = ['does not match column type (Polygon)']
        solution_key = '-nlt'
        solution_value = 'MultiPolygon'
        super(MultiPolygonProblem, self).__init__(search_keys, solution_key, solution_value)

    def _add_solution(self, existing_solution):
        super(MultiPolygonProblem, self)._add_solution(existing_solution)
        logger.debug(
            'Geometry type problem. Trying to force MultiPolygon geometry for file {}'.format(self.filepath))


class MultiLineProblem(OgrParamProblem):
    def __init__(self, filepath):
        self.filepath = filepath
        search_keys = ['does not match column type (LineString)']
        solution_key = '-nlt'
        solution_value = 'MultiLineString'
        super(MultiLineProblem, self).__init__(search_keys, solution_key, solution_value)

    def _add_solution(self, existing_solution):
        super(MultiLineProblem, self)._add_solution(existing_solution)
        logger.debug(
            'Geometry type problem. Trying to force MultiLineString geometry for file {}'.format(self.filepath))


class NoSRSProblem(OgrParamProblem):
    def __init__(self, filepath):
        self.filepath = filepath
        search_keys = ['Can\'t transform coordinates, source layer has no']
        solution_key = '-s_srs'
        solution_value = 'EPSG:4326'
        super(NoSRSProblem, self).__init__(search_keys, solution_key, solution_value)

    def _add_solution(self, existing_solution):
        super(NoSRSProblem, self)._add_solution(existing_solution)
        logger.debug(
            'Source SRS missing. Trying again with EPSG:4326 for file {}'.format(self.filepath))


class Latin1EncodingProblem(EnvParamProblem):
    def __init__(self, filepath):
        self.filepath = filepath
        search_keys = ['invalid byte sequence for encoding']
        solution_key = 'PGCLIENTENCODING'
        solution_value = 'latin1'
        super(Latin1EncodingProblem, self).__init__(search_keys, solution_key, solution_value)

    def _add_solution(self, existing_solution):
        super(Latin1EncodingProblem, self)._add_solution(existing_solution)
        logger.debug(
            'Character encoding problem. Trying with PGCLIENTENCODING=latin1 for file {}'.format(self.filepath))
