import csv
import json
import os
import argparse

parser = argparse.ArgumentParser(description='CSV Reader', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
	'-f', '--file-name',
	required=False,
	type=str,
	help=''
)
parser.add_argument(
	'-a', '--accounts-detail-file',
	required=False,
	type=str,
	help=''
)
args = vars(parser.parse_args())


class CSVReader:
	def __init__(self, file_name: str = '', accounts_detail_path: str = ''):
		if args['file_name']:
			self._file_name = args['file_name']
		else:
			self._file_name = file_name
		if args['accounts_detail_file']:
			self._accounts_detail_path = args['accounts_detail_file']
		else:
			self._accounts_detail_path = accounts_detail_path

	def __str__(self):
		return "CSV Reader Class"

	@property
	def file_name(self) -> str:
		"""The CSV file name"""
		if self._file_name:
			return self._file_name
		else:
			print("The CSV file name was not provided")
			return ""

	@file_name.setter
	def file_name(self, set_file_name: str):
		if set_file_name is None:
			raise Exception("A file name is required")
		self._file_name = set_file_name

	@property
	def accounts_detail_path(self):
		return self._accounts_detail_path

	@accounts_detail_path.setter
	def accounts_detail_path(self, set_detail_path):
		self._accounts_detail_path = set_detail_path

	def get_account_data(self):
		try:
			path = fr"{os.getcwd()}\{self.accounts_detail_path}"
			with open(file=path, mode='r') as fd:
				json_data = fd.read()
		except Exception as error:
			raise error
		else:
			account_detail = json.loads(json_data)
			return account_detail

	def csv_to_dict(
			self,
			output_file_name: str = '',
	):
		"""Extract detail from csv file into a dictionary

		Parameters
		----------
		output_file_name : str, optional
			If provide the function wil automatically create a JSON file of the return object.
		"""

		try:
			path = fr"{os.getcwd()}\{self.file_name}"
			with open(file=path, newline='') as csv_file:
				csv_reader = csv.reader(csv_file)
				lines = list(csv_reader)
		except Exception as error:
			raise error
		# Getting index of each column in line
		account_number_index: int = 0
		accounts_detail: dict = dict()
		if self.accounts_detail_path:
			accounts_detail = self.get_account_data()
			account_number_index = lines[0].index('accountId')
		resource_type_index: int = lines[0].index('resourceType')
		arn_index: int = lines[0].index('arn')
		region_index: int = lines[0].index('region')

		account_name = 'Account Name'

		account_names = list()
		filter_dict = dict()
		for item in lines:
			if item[resource_type_index] == 'resourceType':
				# Skip first line which is the column name
				continue
			if accounts_detail:
				account_number = item[account_number_index]
				try:
					# Mapping account name with account number
					account_name = accounts_detail[account_number]['Account Name']
				except ValueError:
					raise ValueError('Missing detail of AWS Component')
			if account_name not in account_names:
				account_names.append(account_name)
			if account_name not in filter_dict.keys():
				filter_dict[account_name] = dict()
				filter_dict[account_name]['Total Resources'] = 0
			resource_type = item[resource_type_index]
			filter_dict[account_name][resource_type] = dict()

		for account_name in filter_dict.keys():
			for resource_type in filter_dict[account_name].keys():
				if "AWS::" in resource_type:
					filter_dict[account_name][resource_type]["Total"] = 0
					filter_dict[account_name][resource_type]["serviceName"] = resource_type.rsplit("::")[1]
					filter_dict[account_name][resource_type]["resourceDetail"] = list()

		for item in lines:
			if item[arn_index] == "arn" and item[region_index] == "region":
				# Skip first line which is the column name
				continue
			arn = item[arn_index]
			region = item[region_index]
			resource_type = item[resource_type_index]
			resource_detail = {
				"arn": arn,
				"region": region
			}
			if accounts_detail:
				account_number = item[account_number_index]
				account_name = accounts_detail[account_number]["Account Name"]
			filter_dict[account_name][resource_type]["resourceDetail"].append(resource_detail)
			filter_dict[account_name][resource_type]["Total"] += 1
			filter_dict[account_name]["Total Resources"] += 1

		if output_file_name:
			# Getting current script directory and combine with the file name as full path of output file name
			full_output_file_name = fr"{os.getcwd()}\{output_file_name}"
			# Get the directory name of the output file name
			dir_name = os.path.dirname(full_output_file_name)
			if not os.path.exists(dir_name):
				# If the directory not exist then create one
				os.makedirs(name=dir_name, exist_ok=True)
			with open(file=full_output_file_name, mode="w") as output:
				# Write the detail into the output file name, mode "w" will truncate first
				output.write(json.dumps(filter_dict, indent=4))

		return filter_dict

	def get_role_from_arn(self) -> list[str]:
		"""Read CSV file and return a list of AWS resources"""
		role_list = []
		path = fr"{os.getcwd()}\{self.file_name}"
		try:
			with open(file=path, newline='') as csv_file:
				csv_reader = csv.reader(csv_file)
				iam_roles = list(csv_reader)
		except Exception as error:
			raise error
		arn_index = iam_roles[0].index('arn')
		for line in iam_roles:
			if line[arn_index] == 'arn':
				continue
			role = line[arn_index].split(":")[-1].split("/")[-1]
			role_list.append(role)
		return role_list


if __name__ == '__main__':
	print('Hello from Thai')
	reader = CSVReader()
