import pytest

from cord.orm.dataset import ReEncodeVideoTask


@pytest.fixture
def client():
    from cord.client import CordClient
    client = CordClient.initialise(
        'a985bb78-b0ed-4304-ab56-2ebb1c428096',  # Dataset ID
        'VZnih0Zw8kcuoKt8RbpgVVgToVnFa4MW9uMpNyXpCMU'  # API key
    )

    return client


def test_reencode_video(client):
    # Get and print dataset info (videos, image groups)
    dataset = client.get_dataset()

    assert dataset is not None

    data_hash = dataset['data_rows'][0]['data_hash']
    task_id = client.re_encode_data([data_hash])
    task: ReEncodeVideoTask = client.re_encode_data_status(task_id)

    assert task.status == 'SUBMITTED'

    while task.status == 'SUBMITTED':
        task: ReEncodeVideoTask = client.re_encode_data_status(task_id)

    assert task.status == 'DONE'
