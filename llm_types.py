from typing import Dict, List, Union, Optional, Any
from abc import ABC, abstractmethod
import ast

# Define necessary types
ProblemID = str
AIIdentifier = str
Code = str
Feedback = str
Score = int
SubCriteriaScores = Dict[str, Score]
IssueCategory = str
IssueDescription = str
Issue = Dict[IssueCategory, IssueDescription]
Tag = str

class LLMSolution:
	"""
	Represents the solution output from an AI model.
	"""
	def __init__(self,
				 problem_identifier: ProblemID,
				 ai_identifier: AIIdentifier,
				 solution_code: Code,
				 feedback: Optional[Feedback] = None):
		self.problem_identifier = problem_identifier
		self.ai_identifier = ai_identifier
		self.solution_code = solution_code
		self.feedback = feedback

	@classmethod
	def from_json(cls, data: Dict[str, Any]) -> 'LLMSolution':
		"""Create an LLMSolution instance from JSON data."""
		return cls(
			problem_identifier=data.get('problem_identifier', ''),
			ai_identifier=data.get('ai_identifier', ''),
			solution_code=data.get('solution_code', ''),
			feedback=data.get('feedback', None)
		)
		
	def to_json(self) -> Dict[str, Any]:
		"""Convert the LLMSolution instance to a JSON-serializable dictionary."""
		return {
			'problem_identifier': self.problem_identifier,
			'ai_identifier': self.ai_identifier,
			'solution_code': self.solution_code,
			'feedback': self.feedback
		}

	def __str__(self) -> str:
		feedback_str = f", feedback={self.feedback}" if self.feedback else ""
		return (
			f"AIModelSolution("
			f"problem_identifier={self.problem_identifier}, "
			f"ai_identifier={self.ai_identifier}, "
			f"solution_code={self.solution_code}"
			f"{feedback_str}"
			f")"
		)

class Issue:
		def __init__(self,
					 issue_category: str,
					 issue_description: str):
			self.issue_category = issue_category
			self.issue_description = issue_description
		
		@classmethod
		def from_json(cls, data: Dict[str, Any]) -> 'Issue':
			"""Create an Issue instance from JSON data."""
			issue_category = data.get('issue_category', '')
			issue_description = data.get('issue_description', '')
			return cls(issue_category, issue_description)
		
		def to_json(self) -> Dict[str, Any]:
			"""Convert the Issue instance to a JSON-serializable dictionary."""
			return {
				'issue_category': self.issue_category,
				'issue_description': self.issue_description
			}
		
		def __str__(self) -> str:
			return f"Issue({self.issue_category}, {self.issue_description})"

class ProblemGrade:
	"""
	Represents the grade for a single problem.
	"""
	def __init__(self,
				 problem_identifier: ProblemID,
				 score: Score,
				 sub_criteria_scores: Optional[SubCriteriaScores] = None,
				 issues: Optional[List[Issue]] = None):
		self.problem_identifier = problem_identifier
		self.score = score
		self.sub_criteria_scores = sub_criteria_scores
		self.issues = issues
		
	@classmethod
	def from_json(cls, data: Dict[str, Any]) -> 'ProblemGrade':
		"""Create a ProblemGrade instance from JSON data."""
		problem_identifier = data.get('problem_identifier', '')
		score = data.get('score', 0)
		sub_criteria_scores = data.get('sub_criteria_scores', None)
		issues_data = data.get('issues', [])
		issues = [Issue.from_json(issue_data) for issue_data in issues_data]
		return cls(problem_identifier, score, sub_criteria_scores, issues)
	
	def to_json(self) -> Dict[str, Any]:
		"""Convert the ProblemGrade instance to a JSON-serializable dictionary."""
		issues_data = [issue.to_json() for issue in self.issues] if self.issues else []
		return {
			'problem_identifier': self.problem_identifier,
			'score': self.score,
			'sub_criteria_scores': self.sub_criteria_scores,
			'issues': issues_data
	}
	
	def __str__(self) -> str:
		sub_criteria_scores_str = (
			f", sub_criteria_scores={self.sub_criteria_scores}"
			if self.sub_criteria_scores
			else ""
		)
		issues_str = (
			f", issues=[{', '.join(str(issue) for issue in self.issues)}]"
			if self.issues
			else ""
		)
		return (
			f"ProblemGrade("
			f"problem_identifier={self.problem_identifier}, "
			f"score={self.score}"
			f"{sub_criteria_scores_str}"
			f"{issues_str}"
			f")"
		)

class GradingOutput:
	"""
	Represents the grading output for a set of problems.
	"""
	def __init__(self,
				 overall_score: Score,
				 problem_grades: List[ProblemGrade]):
		self.overall_score = overall_score
		self.problem_grades = problem_grades

	@classmethod
	def from_json(cls, data: Dict[str, Any]) -> 'GradingOutput':
		"""Create a GradingOutput instance from JSON data."""
		overall_score = data.get('overall_score', 0)
		problem_grades_data = data.get('problem_grades', [])
		problem_grades = [ProblemGrade.from_json(grade_data) for grade_data in problem_grades_data]
		return cls(overall_score, problem_grades)
	
	def to_json(self) -> Dict[str, Any]:
		"""Convert the GradingOutput instance to a JSON-serializable dictionary."""
		problem_grades_data = [problem_grade.to_json() for problem_grade in self.problem_grades]
		return {
			'overall_score': self.overall_score,
			'problem_grades': problem_grades_data
		}
		
	def __str__(self) -> str:
		return f"GradingOutput({self.overall_score}, {[str(x) for x in self.problem_grades]})"

class FunctionPrototype:
	def __init__(self, data):
		self.function_name = data["function_name"]
		self.parameters = [Parameter(p) for p in data["parameters"]]
		self.return_values = [ReturnValue(r) for r in data["return_values"]]

	@classmethod
	def from_json(cls, data: Dict[str, Any]) -> 'FunctionPrototype':
		return cls(data)
	
	def to_json(self) -> Dict[str, Any]:
		return {
			"function_name": self.function_name,
			"parameters": [param.to_json() for param in self.parameters],
			"return_values": [rv.to_json() for rv in self.return_values]
		}

	def __str__(self):
		params_str = ", ".join([str(p) for p in self.parameters])
		return_values_str = ", ".join([str(r) for r in self.return_values])
		return f"{self.function_name}({params_str}) -> {return_values_str}"
		
	def genericize(self):
		generic_data = {
			"function_name": "function",
			"parameters": [{"name": chr(97 + i), "type": param.type} for i, param in enumerate(self.parameters)],
			"return_values": [{"type": rv.type} for rv in self.return_values]
		}
		return FunctionPrototype(generic_data)
	
	def get_python_type(self, param_type, input):
		# Based on the type, convert the string representation to the appropriate Python object
		if param_type == "int":
			return int(input)
		elif param_type == "float":
			return float(input)
		elif param_type == "str":
			return ast.literal_eval(input)
		elif param_type == "bool":
			return input.lower() == "true"
		elif '[' in param_type:
			# Using ast.literal_eval to safely evaluate the string representation
			return ast.literal_eval(input)
		
	def get_parameter_values(self, test_case: Dict[str, str]) -> Dict[str, Any]:
		converted_params = {}
		
		for param in self.parameters:
			converted_params[param.name] = self.get_python_type(param.type, test_case["parameters"][param.name])
		return converted_params
		
	def get_ordered_parameter_values(self, test_case) -> List[str]:
		ordered_parameters = []
		
		parameter_values = self.get_parameter_values(test_case)
		
		for p in self.parameters:
			ordered_parameters.append(parameter_values[p.name])
		return ordered_parameters
		
	def get_return_values(self, test_case: Dict[str, str]) -> Dict[str, Any]:
		converted_retvals = []
		
		expectedOutput = test_case["expected_output"]
		
		for retval, expected in zip(self.return_values, expectedOutput):
			# Extract the type of the parameter
			converted_retvals.append(self.get_python_type(retval.type, expected))
			
		if len(converted_retvals) == 1:
			return converted_retvals[0]
		elif len(converted_retvals) > 1:
			return tuple(converted_retvals)

class Parameter:
	def __init__(self, data):
		self.name = data["name"]
		self.type = data["type"]

	@classmethod
	def from_json(cls, data: Dict[str, Any]) -> 'Parameter':
		return cls(data)
	
	def to_json(self) -> Dict[str, Any]:
		return {
			"name": self.name,
			"type": self.type
		}

	def __str__(self):
		return f"{self.name}: {self.type}"

class ReturnValue:
	def __init__(self, data):
		self.type = data["type"]

	@classmethod
	def from_json(cls, data: Dict[str, Any]) -> 'ReturnValue':
		return cls(data)
	
	def to_json(self) -> Dict[str, Any]:
		return {
			"type": self.type
		}

	def __str__(self):
		return self.type

class Prompt:
	def __init__(self, data: Dict[str, any]):
		self.prompt = data["prompt"]
		self.genericize = data["genericize"]
		self.sample_inputs_outputs = [
			{k: {
				"input": v["input"],
				"expected_output": v["expected_output"]
			 } for k, v in data.get("sample_inputs_outputs", {}).items()}
		]
		self.input_code = data.get("input_code", None)

	def __str__(self):
		genericize_str = "Genericize" if self.genericize else "Do not genericize"
		return f'Prompt: "{self.prompt}", {genericize_str}, Sample Inputs/Outputs: {self.sample_inputs_outputs}, Input Code: {self.input_code}'

	@classmethod
	def from_json(cls, data: Dict[str, any]) -> 'Prompt':
		return cls(data)

	def to_json(self) -> Dict[str, any]:
		return {
			"prompt": self.prompt,
			"genericize": self.genericize,
			"sample_inputs_outputs": self.sample_inputs_outputs,
			"input_code": self.input_code
		}

class ProblemDefinition:
	def __init__(self,
				 identifier: str,
				 description: str,
				 prompts: Dict[str, Prompt],
				 function_prototype: FunctionPrototype,
				 correctness_test_suite: Optional[Dict[str, Any]] = None,
				 optimal_solution: Optional[str] = None,
				 additional_instructions: Optional[str] = None,
				 tags: Optional[List[str]] = None):
		self.identifier = identifier
		self.description = description
		self.prompts = prompts
		self.function_prototype = function_prototype
		self.correctness_test_suite = correctness_test_suite
		self.optimal_solution = optimal_solution
		self.additional_instructions = additional_instructions
		self.tags = tags

	@classmethod
	def from_json(cls, data: Dict[str, Any]) -> 'ProblemDefinition':
		function_prototype = FunctionPrototype.from_json(data.get('function_prototype', {}))
		prompts = {key: Prompt.from_json(value) for key, value in data.get("prompts", {}).items()}
		return cls(
			identifier=data.get('identifier', ''),
			description=data.get('description', ''),
			prompts=prompts,
			function_prototype=function_prototype,
			correctness_test_suite=data.get('correctness_test_suite', None),
			optimal_solution=data.get('optimal_solution', None),
			additional_instructions=data.get('additional_instructions', None),
			tags=data.get('tags', None)
		)

	def to_json(self) -> Dict[str, Any]:
		return {
			'identifier': self.identifier,
			'description': self.description,
			'prompts': {key: value.to_json() for key, value in self.prompts.items()},
			'function_prototype': self.function_prototype.to_json(),
			'correctness_test_suite': self.correctness_test_suite,
			'optimal_solution': self.optimal_solution,
			'additional_instructions': self.additional_instructions,
			'tags': self.tags
		}

	def __str__(self) -> str:
		prompts_str = '\n'.join([f'{key}: {str(value)}' for key, value in self.prompts.items()])
		return (
			f"ProblemDefinition("
			f"identifier={self.identifier}, "
			f"description={self.description}, "
			f"prompts=\n{prompts_str}\n"
			f"function_prototype={str(self.function_prototype)}, "
			f"correctness_test_suite={self.correctness_test_suite}, "
			f"optimal_solution={self.optimal_solution}, "
			f"additional_instructions={self.additional_instructions}, "
			f"tags={self.tags}"
			f")"
		)

class AIModel(ABC):
	"""
	Abstract base class for AI models.
	"""
	
	@abstractmethod
	def generate_solution(self, problem_definition: ProblemDefinition) -> 'LLMSolution':
		"""
		Generates a solution for the given problem definition.
		
		Subclasses should override this method to provide the logic for
		generating solutions.
		
		:param problem_definition: The problem definition for which to generate a solution.
		:return: An LLMSolution object containing the generated solution.
		"""
		pass
		
	def __str__(self) -> str:
		return f"{self.__class__.__name__}()"

class Grader(ABC):
	"""
	Abstract base class for graders.
	"""
	
	@abstractmethod
	def grade(self, problems: List[ProblemDefinition], solutions: List[LLMSolution]) -> GradingOutput:
		"""
		Grades the provided solutions against the problem definitions.
		"""
		pass
		
	def __str__(self) -> str:
		return f"{self.__class__.__name__}()"
		