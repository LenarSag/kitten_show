from datetime import date, timedelta

from fastapi import status
from httpx import AsyncClient, ASGITransport
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.db.database import get_session
from main import app
from config import API_URL


TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'


test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)

transport = ASGITransport(app=app)


async def override_get_session():
    session = TestSessionLocal()
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
        yield session
    finally:
        await session.close()


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture
def test_user_data():
    return {'username': 'admin', 'password': 'Q123werty!23', 'email': 'test@test.ru'}


@pytest.fixture
def auth_headers(event_loop, test_user_data):
    async def get_headers():
        login_payload = test_user_data
        async with AsyncClient(
            transport=transport,
            base_url='http://test',
        ) as client:
            response = await client.post(
                f'{API_URL}/auth/token',
                json=login_payload,
            )
            assert response.status_code == 200, f'Login failed: {response.json()}'

            login_data = response.json()
            access_token = login_data['access_token']

            return {
                'Authorization': f'Bearer {access_token}',
            }

    return event_loop.run_until_complete(get_headers())


@pytest.fixture
def test_breed_data():
    return {
        'name': 'persian',
    }


@pytest.fixture
def multiple_test_breeds():
    return [
        {
            'name': 'siberian',
        },
        {
            'name': 'british',
        },
        {
            'name': 'scottish',
        },
    ]


@pytest.fixture
def test_kitten_data():
    birth_date = date.today() - timedelta(weeks=5)
    return {
        'name': 'Barsik',
        'birth_date': f'{birth_date}',
        'color': 'white',
        'sex': 'male',
        'description': 'bad boy',
        'breed_id': 1,
    }


@pytest.fixture
def test_edit_kitten_data(test_kitten_data):
    data = test_kitten_data
    data['name'] = 'NewBarsik'
    return data


@pytest.fixture
def multiple_test_kittens():
    birth_date1 = date.today() - timedelta(days=95)
    birth_date2 = date.today() - timedelta(days=65)
    return [
        {
            'name': 'Matros',
            'birth_date': f'{birth_date1}',
            'color': 'white',
            'sex': 'male',
            'description': 'good boy',
            'breed_id': 1,
        },
        {
            'name': 'Lara',
            'birth_date': f'{birth_date2}',
            'color': 'black',
            'sex': 'female',
            'description': 'bad girl',
            'breed_id': 3,
        },
    ]


@pytest.fixture
def test_bad_date_kitten_data():
    future_date = date.today() + timedelta(days=10)
    past_date = date.today() - timedelta(days=365 * 25)
    return [
        {
            'name': 'Matros',
            'birth_date': f'{future_date}',
            'color': 'white',
            'sex': 'male',
            'description': 'good boy',
            'breed_id': 1,
        },
        {
            'name': 'Lara',
            'birth_date': f'{past_date}',
            'color': 'black',
            'sex': 'female',
            'description': 'bad girl',
            'breed_id': 3,
        },
    ]


@pytest.fixture
def test_non_existing_color_kitten_data():
    return {
        'name': 'Kotik',
        'birth_date': '2023-10-12',
        'sex': 'female',
        'color': 'superblack',
        'description': 'bad boy',
        'breed_id': 2,
    }


@pytest.fixture
def test_non_existing_breed_kitten_data():
    return {
        'name': 'Tema',
        'birth_date': '2023-10-12',
        'sex': 'female',
        'color': 'black',
        'description': 'bad boy',
        'breed_id': 99,
    }


@pytest.mark.asyncio
async def test_create_user(test_user_data):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.post(f'{API_URL}/auth/user', json=test_user_data)

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f'Error: {response.json()}'
        response_data = response.json()

        assert (
            test_user_data['username'] == response_data['username']
        ), f"Expected username: {test_user_data['username']}, but got: {response_data['username']}"


@pytest.mark.asyncio
async def test_create_breed(test_breed_data, auth_headers):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.post(
            f'{API_URL}/breeds/', json=test_breed_data, headers=auth_headers
        )

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f'Error: {response.json()}'
        response_data = response.json()

        assert (
            test_breed_data['name'] == response_data['name']
        ), f"Expected name: {test_breed_data['name']}, but got: {response_data['name']}"


@pytest.mark.asyncio
async def test_create_same_breed(test_breed_data, auth_headers):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.post(
            f'{API_URL}/breeds/', json=test_breed_data, headers=auth_headers
        )
        data = response.json()

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), f'Error: {response.json()}'
        expected_error_message = 'Breed already exists'
        assert data['detail'] == expected_error_message


@pytest.mark.asyncio
async def test_create_multiple_breeds(multiple_test_breeds, auth_headers):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        for breed in multiple_test_breeds:
            response = await client.post(
                f'{API_URL}/breeds/', json=breed, headers=auth_headers
            )

            assert (
                response.status_code == status.HTTP_201_CREATED
            ), f'Error: {response.json()}'
            response_data = response.json()

            assert (
                breed['name'] == response_data['name']
            ), f"Expected name: {breed['email']}, but got: {response_data['name']}"


@pytest.mark.asyncio
async def test_create_kitten(test_kitten_data, auth_headers):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.post(
            f'{API_URL}/kittens/', json=test_kitten_data, headers=auth_headers
        )

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f'Error: {response.json()}'
        response_data = response.json()

        assert (
            test_kitten_data['name'] == response_data['name']
        ), f"Expected name: {test_kitten_data['name']}, but got: {response_data['name']}"
        assert (
            test_kitten_data['color'] == response_data['color']
        ), f"Expected color: {test_kitten_data['color']}, but got: {response_data['color']}"
        assert (
            test_kitten_data['sex'] == response_data['sex']
        ), f"Expected sex: {test_kitten_data['sex']}, but got: {response_data['sex']}"
        assert (
            1 == response_data['age_in_months']
        ), f"Expected age_in_months: 1, but got: {response_data['age_in_months']}"


@pytest.mark.asyncio
async def test_create_multiple_kittens(multiple_test_kittens, auth_headers):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        for kitten in multiple_test_kittens:
            response = await client.post(
                f'{API_URL}/kittens/',
                json=kitten,
                headers=auth_headers,
            )
            assert (
                response.status_code == status.HTTP_201_CREATED
            ), f'Error: {response.json()}'


@pytest.mark.asyncio
async def test_get_kittens():
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.get(f'{API_URL}/kittens/')

        assert response.status_code == status.HTTP_200_OK, f'Error: {response.json()}'
        data = response.json()
        expected_response = {
            'items': [
                {
                    'id': 1,
                    'name': 'Barsik',
                    'color': 'white',
                    'sex': 'male',
                    'age_in_months': 1,
                    'description': 'bad boy',
                    'breed': {'name': 'persian', 'id': 1},
                },
                {
                    'id': 3,
                    'name': 'Lara',
                    'color': 'black',
                    'sex': 'female',
                    'age_in_months': 2,
                    'description': 'bad girl',
                    'breed': {'name': 'british', 'id': 3},
                },
                {
                    'id': 2,
                    'name': 'Matros',
                    'color': 'white',
                    'sex': 'male',
                    'age_in_months': 3,
                    'description': 'good boy',
                    'breed': {'name': 'persian', 'id': 1},
                },
            ],
            'total': 3,
            'page': 1,
            'size': 50,
            'pages': 1,
        }

        assert data == expected_response, f'Unexpected response: {data}'


@pytest.mark.asyncio
async def test_filter_kittens_by_breed():
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.get(f'{API_URL}/kittens/?breed__name=persian')

    assert response.status_code == status.HTTP_200_OK, f'Error: {response.json()}'
    response_data = response.json()

    assert (
        len(response_data['items']) == 2
    ), f"Expected 2 kitten, got {len(response_data['items'])}"
    assert response_data['items'][0]['breed']['name'] == 'persian'


@pytest.mark.asyncio
async def test_filter_kittens_by_age_in_months_gt():
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.get(f'{API_URL}/kittens/?age_in_months__gt=10')

    assert response.status_code == status.HTTP_200_OK, f'Error: {response.json()}'
    response_data = response.json()

    assert (
        len(response_data['items']) == 0
    ), f"Expected 0 kitten, got {len(response_data['items'])}"


@pytest.mark.asyncio
async def test_filter_kittens_by_age_in_months_lt():
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.get(f'{API_URL}/kittens/?age_in_months__lt=3')

    assert response.status_code == status.HTTP_200_OK, f'Error: {response.json()}'
    response_data = response.json()

    assert (
        len(response_data['items']) == 2
    ), f"Expected 2 kitten, got {len(response_data['items'])}"


@pytest.mark.asyncio
async def test_edit_kitten(test_edit_kitten_data, auth_headers):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.get(f'{API_URL}/kittens/1')

    assert response.status_code == status.HTTP_200_OK, f'Error: {response.json()}'
    response_data = response.json()
    assert response_data['name'] == 'Barsik'

    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.patch(
            f'{API_URL}/kittens/1', json=test_edit_kitten_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK, f'Error: {response.json()}'
        response_edit_data = response.json()
        assert response_edit_data['name'] == test_edit_kitten_data['name']
        assert response_edit_data['name'] != response_data['name']


@pytest.mark.asyncio
async def test_delete_kitten(auth_headers):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.get(f'{API_URL}/kittens/1')

    assert response.status_code == status.HTTP_200_OK, f'Error: {response.json()}'

    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.delete(f'{API_URL}/kittens/1', headers=auth_headers)
        assert (
            response.status_code == status.HTTP_204_NO_CONTENT
        ), f'Error: {response.json()}'

    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.get(f'{API_URL}/kittens/1')

    assert (
        response.status_code == status.HTTP_404_NOT_FOUND
    ), f'Error: {response.json()}'


@pytest.mark.asyncio
async def test_create_kitten_with_non_existing_breed(
    test_non_existing_breed_kitten_data, auth_headers
):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.post(
            f'{API_URL}/kittens/',
            json=test_non_existing_breed_kitten_data,
            headers=auth_headers,
        )
        data = response.json()

        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), f'Error: {response.json()}'
        expected_error_message = 'Breed not found'
        assert data['detail'] == expected_error_message


@pytest.mark.asyncio
async def test_create_kitten_with_non_existing_color(
    test_non_existing_color_kitten_data, auth_headers
):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        response = await client.post(
            f'{API_URL}/kittens/',
            json=test_non_existing_color_kitten_data,
            headers=auth_headers,
        )
        data = response.json()

        assert (
            response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        ), f'Error: {response.json()}'
        expected_error_message = [
            {
                'type': 'enum',
                'loc': ['body', 'color'],
                'msg': "Input should be 'white', 'black', 'grey' or 'ginger'",
                'input': 'superblack',
                'ctx': {'expected': "'white', 'black', 'grey' or 'ginger'"},
            }
        ]
        assert (
            data['detail'] == expected_error_message
        ), f'Expected: {expected_error_message}, but got: {data["detail"]}'


@pytest.mark.asyncio
async def test_create_kitten_with_bad_birth_data(
    test_bad_date_kitten_data, auth_headers
):
    async with AsyncClient(
        transport=transport,
        base_url='http://test',
    ) as client:
        for kitten in test_bad_date_kitten_data:
            response = await client.post(
                f'{API_URL}/kittens/',
                json=kitten,
                headers=auth_headers,
            )
            assert (
                response.status_code == status.HTTP_400_BAD_REQUEST
            ), f'Error: {response.json()}'
