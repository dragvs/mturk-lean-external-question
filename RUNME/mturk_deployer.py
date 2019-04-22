import boto3

import config


def deploy():
    # Before connecting to MTurk, set up your AWS account and IAM settings as
    # described here:
    # https://blog.mturk.com/how-to-use-iam-to-control-api-access-to-your-mturk-account-76fe2c2e66e2
    #
    # Follow AWS best practices for setting up credentials here:
    # http://boto3.readthedocs.io/en/latest/guide/configuration.html

    # Use the Amazon Mechanical Turk Sandbox to publish test Human Intelligence
    # Tasks (HITs) without paying any money.  Sign up for a Sandbox account at
    # https://requestersandbox.mturk.com/ with the same credentials as your main
    # MTurk account.

    # By default, HITs are created in the free-to-use Sandbox
    use_sandbox = True

    environments = {
        "live": {
            "endpoint": "https://mturk-requester.us-east-1.amazonaws.com",
            "preview": "https://www.mturk.com/mturk/preview",
            "manage": "https://requester.mturk.com/mturk/manageHITs",
            "reward": "0.00"
        },
        "sandbox": {
            "endpoint": "https://mturk-requester-sandbox.us-east-1.amazonaws.com",
            "preview": "https://workersandbox.mturk.com/mturk/preview",
            "manage": "https://requestersandbox.mturk.com/mturk/manageHITs",
            "reward": "0.11"
        },
    }
    mturk_environment = environments["sandbox"] if use_sandbox else environments["live"]

    # use profile if one was passed as an arg, otherwise
    # profile_name = sys.argv[1] if len(sys.argv) >= 2 else None
    session = boto3.Session(
        # profile_name=profile_name
        # aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        # aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        # aws_session_token=SESSION_TOKEN,
    )
    client = session.client(
        service_name='mturk',
        region_name='us-east-1',
        endpoint_url=mturk_environment['endpoint'],
    )

    # Test that you can connect to the API by checking your account balance
    user_balance = client.get_account_balance()

    # In Sandbox this always returns $10,000. In live, it will be your actual balance.
    print("Your account balance is {}".format(user_balance['AvailableBalance']))

    # The question we ask the workers is contained in this file.
    question = open('./question.xml', mode='r').read()

    # Example of using qualification to restrict responses to Workers who have had
    # at least 80% of their assignments approved. See:
    # http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationRequirementDataStructureArticle.html#ApiReference_QualificationType-IDs
    worker_requirements = [{
        'QualificationTypeId': '000000000000000000L0',
        'Comparator': 'GreaterThanOrEqualTo',
        'IntegerValues': [80],
        'RequiredToPreview': True,
    }]

    # Create the HIT
    response = client.create_hit(
        MaxAssignments=3,
        LifetimeInSeconds=600,
        AssignmentDurationInSeconds=600,
        Reward=mturk_environment['reward'],
        Title='Answer a simple question',
        Keywords='question, answer, research',
        Description='Answer a simple question. Created from mturk-code-samples.',
        Question=question,
        QualificationRequirements=worker_requirements,
    )

    # The response included several fields that will be helpful later
    hit_type_id = response['HIT']['HITTypeId']
    hit_id = response['HIT']['HITId']
    print("\nCreated HIT: {}".format(hit_id))

    print("\nYou can work the HIT here:")
    print(mturk_environment['preview'] + "?groupId={}".format(hit_type_id))

    print("\nAnd see results here:")
    print(mturk_environment['manage'])


deploy()
