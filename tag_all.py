from csv_reader import *
import json
import botocore.exceptions
from boto3.session import Session


class AWSTagger:
	_accounts_data: dict = dict()
	_detail_data: dict = dict()
	_aws_session: Session = None
	_csv_reader: CSVReader = CSVReader()
	_key_tag: str = ''
	_value_tag: str = ''
	_tagged: dict = dict()
	_output_detail_file_name: str = ''
	_result_file_name: str = ''

	def __init__(
			self,
			output_detail_file_name: str = '',
			result_file_name: str = ''
	):
		self.set_up()
		self._output_detail_file_name = output_detail_file_name
		self._result_file_name = result_file_name

	@property
	def key_tag(self) -> str:
		return self._key_tag

	@key_tag.setter
	def key_tag(self, set_key_tag: str) -> None:
		self._key_tag = set_key_tag

	@property
	def value_tag(self) -> str:
		return self._value_tag

	@value_tag.setter
	def value_tag(self, set_value_tag: str) -> None:
		self._value_tag = set_value_tag

	@property
	def output_detail_file_name(self) -> str:
		return self._output_detail_file_name

	@output_detail_file_name.setter
	def output_detail_file_name(self, set_output_detail_file_name: str) -> None:
		self._output_detail_file_name = set_output_detail_file_name

	@property
	def result_file_name(self) -> str:
		return self._result_file_name

	@result_file_name.setter
	def result_file_name(self, set_result_file_name: str) -> None:
		self._result_file_name = set_result_file_name

	@property
	def csv_reader(self):
		return self._csv_reader

	@property
	def aws_session(self):
		return self._aws_session

	@aws_session.setter
	def aws_session(self, profile_name: str = '') -> None:
		# Getting AWS credential session by a profile that name as pattern: {account name} PROD
		aws_session = Session(profile_name=profile_name)
		self._aws_session = aws_session

	def set_up(self) -> None:
		self._accounts_data = self._csv_reader.get_account_data()
		self._detail_data = self._csv_reader.csv_to_dict(output_file_name=self.output_detail_file_name)

	def service_tag_function(
			self,
			service_name: str,
			service_type: str,
			region: str,
			arn: str,
			existing_tags: dict
	):
		if not service_name:
			raise ValueError("Missing service name")
		service_name = service_name.lower()
		service_type = service_type.lower()
		if service_name == 'ElasticLoadBalancingV2'.lower():
			service_name = 'elbv2'
		if service_name == 'ElasticLoadBalancing'.lower():
			service_name = 'elb'
		client = self._aws_session.client(service_name=service_name, region_name=region)  # type: ignore
		resource_id: str = arn.rsplit(":")[-1].rsplit("/")[-1]
		tags: list = list()
		for key, value in existing_tags.items():
			if "aws:" in key:
				continue
			existing_tag = {
				'Key': key,
				'Value': value
			}
			tags.append(existing_tag)
		tags.append({
			'Key': self._key_tag,
			'Value': self._value_tag,
		})

		tags_return = dict()
		for item in tags:
			tags_return[item['Key']] = item['Value']

		if service_name == 'athena':
			client.tag_resource(
				ResourceARN=arn,
				Tags=tags,
			)
			return tags_return
		if service_name == 'iam':
			if service_type == 'role':
				role = resource_id
				client.tag_role(
					RoleName=role,
					Tags=tags
				)
				return tags_return
			if service_type == 'user':
				user_name = resource_id
				client.tag_user(
					UserName=user_name,
					Tags=tags
				)
				return tags_return
		if service_name == 'acm':
			client.add_tags_to_certificate(
				CertificateArn=arn,
				Tags=tags,
			)
			return tags_return
		if service_name == 'apigateway':
			api_gateway_tags: dict = dict()
			for key, value in existing_tags.items():
				api_gateway_tags[key] = value
			api_gateway_tags[self._key_tag] = self._value_tag
			client.tag_resource(
				resourceArn=arn,
				tags=api_gateway_tags
			)
			return api_gateway_tags
		if service_name == 'autoscaling':
			auto_scaling_tags = list()
			for key, value in existing_tags.items():
				if "aws:" in key:
					continue
				tag = {
					'ResourceId': resource_id,
					'ResourceType': 'auto-scaling-group',
					'Key': key,
					'Value': value,
					'PropagateAtLaunch': True
				}
				auto_scaling_tags.append(tag)
			auto_scaling_tags.append({
				'ResourceId': resource_id,
				'ResourceType': 'auto-scaling-group',
				'Key': self._key_tag,
				'Value': self._value_tag,
				'PropagateAtLaunch': True
			})
			auto_scaling_tags_return: dict = dict()
			for item in auto_scaling_tags:
				auto_scaling_tags_return[item['Key']] = item['Value']
			client.create_or_update_tags(
				Tags=auto_scaling_tags
			)
			return auto_scaling_tags_return
		if service_name == 'ec2':
			client.create_tags(
				DryRun=False,
				Resources=[
					resource_id,
				],
				Tags=tags
			)
			return tags_return
		if service_name == 'ecr':
			client.tag_resource(
				resourceArn=arn,
				tags=tags
			)
			return tags_return
		if service_name == 'elbv2':
			client.add_tags(
				ResourceArns=[
					arn,
				],
				Tags=tags
			)
			return tags_return
		if service_name == 'elb':
			client.add_tags(
				LoadBalancerNames=[
					resource_id,
				],
				Tags=tags
			)
			return tags_return
		if service_name == 'kms':
			kms_tags = list()
			for key, value in existing_tags.items():
				tag = {
					'TagKey': key,
					'TagValue': value,
				}
				kms_tags.append(tag)
			kms_tags.append({
				'TagKey': self._key_tag,
				'TagValue': self._value_tag,
			})
			kms_tags_return: dict = dict()
			for item in kms_tags:
				kms_tags_return[item['TagKey']] = item['TagValue']
			client.tag_resource(
				KeyId=resource_id,
				Tags=kms_tags
			)
			return kms_tags_return
		if service_name == 'lambda':
			lambda_tags: dict = dict()
			for key, value in existing_tags.items():
				if "aws:" in key:
					continue
				lambda_tags[key] = value
			lambda_tags[self._key_tag] = self._value_tag
			client.tag_resource(
				Resource=arn,
				Tags=lambda_tags
			)
			return lambda_tags
		if service_name == 'rds':
			client.add_tags_to_resource(
				ResourceName=arn,
				Tags=tags
			)
			return tags_return
		if service_name == 's3':
			client.put_bucket_tagging(
				Bucket=resource_id,
				Tagging={
					'TagSet': tags
				},
			)
			return tags_return
		if service_name == 'ses':
			client = self._aws_session.client('sesv2', region_name=region)
			client.tag_resource(
				ResourceArn=arn,
				Tags=tags
			)
			return tags_return
		if service_name == 'sns':
			client.tag_resource(
				ResourceArn=arn,
				Tags=tags
			)
			return tags_return
		if service_name == 'sqs':
			sqs_tags: dict = dict()
			for key, value in existing_tags.items():
				sqs_tags[key] = value
			sqs_tags[self._key_tag] = self._value_tag
			account_id = arn.rsplit(":")[4]
			queue_url = fr"https://sqs.{region}.amazonaws.com/{account_id}/{resource_id}"
			client.tag_queue(
				QueueUrl=queue_url,
				Tags=sqs_tags
			)
			return sqs_tags
		if service_name == 'codebuild':
			cb_tags = list()
			for key, value in existing_tags.items():
				cb_tags.append({
					'key': key,
					'value': value
				})
			cb_tags.append({
				'key': self._key_tag,
				'value': self._value_tag
			})
			cb_tags_return: dict = dict()
			for item in cb_tags:
				cb_tags_return[item['key']] = item['value']
			client.update_project(
				name=resource_id,
				tags=cb_tags
			)
			return cb_tags_return
		if service_name == 'dynamodb':
			client.tag_resource(
				ResourceArn=arn,
				Tags=tags
			)
			return tags_return
		if service_name == 'cloudfront':
			client.tag_resource(
				Resource=arn,
				Tags={
					'Items': tags
				}
			)
			return tags_return
		if service_name == 'cloudtrail':
			client.add_tags(
				ResourceId=arn,
				TagsList=tags
			)
			return tags_return
		if service_name == 'ecs':
			ecs_tags = list()
			for key, value in existing_tags.items():
				ecs_tags.append({
					'key': key,
					'value': value
				})
			ecs_tags.append({
				'key': self._key_tag,
				'value': self._value_tag
			})
			ecs_tags_return: dict = dict()
			for item in ecs_tags:
				ecs_tags_return[item['key']] = item['value']
			client.tag_resource(
				resourceArn=arn,
				tags=ecs_tags
			)
			return ecs_tags_return
		if service_name == 'events':
			client.tag_resource(
				ResourceARN=arn,
				Tags=tags
			)
			return tags_return
		if service_name == 'glue':
			glue_tags: dict = dict()
			for key, value in existing_tags.items():
				glue_tags[key] = value
			glue_tags[self._key_tag] = self._value_tag
			client.tag_resource(
				ResourceArn=arn,
				TagsToAdd=glue_tags
			)
			return glue_tags

		raise NameError("Service was not defined")

	def tag_resources(self, tagged_cache: dict = None):
		for account_name, account_detail in self._detail_data.items():
			print(f"Working with {account_name}")
			self.aws_session = account_name
			self._tagged[account_name] = dict()
			self._tagged[account_name]["Total tagged"] = 0
			account_number: str = str(account_detail['Account Number'])
			self._key_tag = self._accounts_data[account_number]['Key Tag']
			self._value_tag = self._accounts_data[account_number]['Value Tag']
			for resource_type in account_detail.keys():
				if "AWS::" not in resource_type:
					continue
				print(f"Tagging service {resource_type}")
				# Define return schema
				tagged_resources = dict()
				tagged_resources['Total Tagged'] = int(0)
				tagged_resources["Success"] = dict()
				tagged_resources["Success"]["Resources"] = list()
				tagged_resources["Failure"] = dict()
				tagged_resources["Failure"]["Error"] = dict()
				for resource_detail in account_detail[resource_type]["resourceDetail"]:
					if tagged_cache:
						if resource_detail['arn'] in tagged_cache[account_name][resource_type]:
							print(f"\tResource {resource_detail['arn']} already tagged.")
							continue
					try:
						print(f"\tTry to tag resource: {resource_detail['arn']}")
						tagged = self.service_tag_function(
							service_name=resource_type.rsplit("::")[1],
							service_type=resource_type.rsplit("::")[2],
							arn=resource_detail['arn'],
							region=resource_detail['region'],
							existing_tags=resource_detail['tags']
						)
					except NameError:
						if 'NotDefined' not in tagged_resources["Failure"]["Error"]:
							tagged_resources["Failure"]["Error"]['NotDefined'] = dict()
							tagged_resources["Failure"]["Error"]['NotDefined']['Resources'] = list()
						resource_detail['Message'] = "Service was not defined"
						tagged_resources["Failure"]["Error"]['NotDefined']['Resources'].append(resource_detail)
					except botocore.exceptions.ClientError as error:
						error_code = error.response['Error']['Code']
						error_message = error.response['Error']['Message']
						if error_code not in tagged_resources["Failure"]["Error"]:
							tagged_resources["Failure"]["Error"][error_code] = dict()
							tagged_resources["Failure"]["Error"][error_code]["Resources"] = list()
						resource_detail["Message"] = error_message
						tagged_resources["Failure"]["Error"][error_code]["Resources"].append(resource_detail)
						print(f"\tTag fail: {error_message}")
					else:
						resource_detail['tags'] = tagged
						tagged_resources["Success"]["Resources"].append(resource_detail)
						tagged_resources["Total Tagged"] += 1
						print("\tTagged.")
				self._tagged[account_name]["Total tagged"] += tagged_resources["Total Tagged"]
				self._tagged[account_name][resource_type] = tagged_resources
		return self._tagged

	def tag_cache(self) -> dict:
		tagged = None
		if self.result_file_name:
			path = fr"{os.getcwd()}\{self.result_file_name}"
			with open(file=path, mode="r") as fd:
				json_data = fd.read()
			if json_data:
				tagged = json.loads(json_data)
		tagged_cache = None
		tagged_cache_path = './tagged_cache.json'
		if os.path.isfile(tagged_cache_path):
			with open(file=tagged_cache_path, mode='r') as fd:
				json_cache = fd.read()
			if json_cache:
				tagged_cache = json.loads(json_cache)
			if tagged:
				for account_name in tagged.keys():
					if account_name not in tagged_cache.keys():
						tagged_cache[account_name] = dict()
					for resource_type in tagged[account_name].keys():
						if "AWS::" not in resource_type:
							continue
						if resource_type not in tagged_cache[account_name].keys():
							tagged_cache[account_name][resource_type] = list()
						success_resources = tagged[account_name][resource_type]["Success"]["Resources"]
						for item in success_resources:
							if item['arn'] not in tagged_cache[account_name][resource_type]:
								tagged_cache[account_name][resource_type].append(item['arn'])
				with open(file="tagged_cache.json", mode='w') as fd:
					fd.write(json.dumps(tagged_cache, indent=4, default=str))
		return tagged_cache

	def tag_all(self, result_file_name: str = '') -> None:
		if result_file_name:
			self.result_file_name = result_file_name
		if not self.result_file_name:
			self.result_file_name = 'tagged-result.json'
		path = fr"{os.getcwd()}\{self.result_file_name}"
		with open(file=path, mode="w") as result:
			result.write(json.dumps(self.tag_resources(tagged_cache=self.tag_cache()), indent=4))
		# Cache all tagged.
		self.tag_cache()


if __name__ == "__main__":
	print("Hello from Thai")
	tagger = AWSTagger()
	tagger.tag_all()
