import boto3
import json
from csv_reader import CSVReader


class AWSTagging:
	def __init__(self, service: str = ""):
		self._service = service

	def tagging_iam_role(self, root_path: str, aws_accounts: dict) -> dict:
		"""Tagging VRS IAM Role"""
		# Define a dictionary variable that contains the key as an account name
		# and the value as a list of tagged roles for a return value.
		tagged_role = dict(map(lambda x: (x, list()), aws_accounts.keys()))
		# Loop through AWS component dictionary contains key as account name
		# and value as the value of the tag key, which is unique with each account.
		for account, tag_component in aws_accounts.items():
			# The CSV file name must be named as the account name.
			file_name = f"{account}.csv"
			# Getting all roles that need to tag from the CSV file.
			csv_reader = CSVReader(root_path)
			iam_roles = csv_reader.get_role_from_arn(file_name)
			# Getting AWS credential session by a profile that name as pattern: {account name} PROD
			aws_session = boto3.Session(profile_name=f"{account} PROD")
			iam_client = aws_session.client('iam')
			print(f"Starting work with {account} account...")
			for role in iam_roles:
				response = iam_client.tag_role(
					RoleName=role,
					Tags=[
						{
							'Key': tag_component['key'],
							'Value': tag_component['value']
						},
					]
				)
				if response:
					tagged_role[account].append(role)
					print(f"Tagged role {role}.")
				else:
					Exception(f"An error occur, can not tag resource {role}")
			print(f"Finished tag {tagged_role[account].__len__()} resources of {account} account.")
		return tagged_role


if __name__ == "__main__":
	print("Hello from Thai")
