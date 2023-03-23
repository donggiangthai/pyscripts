from csv_reader import CSVReader
import boto3
import json


def verify_tagged(root_path: str, aws_accounts: dict) -> None:
	"""Verify that every resource are tagged"""
	result = dict(map(lambda x: (x, dict()), aws_accounts.keys()))
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
		result[account]["Total tagged"] = 0
		result[account]["Roles"] = list()
		for role in iam_roles:
			role_result = dict()
			response = iam_client.list_role_tags(
				RoleName=role
			)
			filtered_tag = next(filter(lambda tags: (tags['Key'] == tag_component['Key']), response['Tags']), None)
			if filtered_tag:
				print(f"\tRole {role} tagged.")
				role_result[role] = filtered_tag
				result[account]["Roles"].append(role_result)
				result[account]["Total tagged"] += 1
	with open(file='verified.json', mode="w") as output:
		output.write(json.dumps(result, indent=4))
	return


if __name__ == "__main__":
	print("Hello from Thai")
